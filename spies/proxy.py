#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import os
import random
import sys
import requests
import yaml
import time


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        # we'll use start to store the time when we entered this routine, to calculate latency
        start = time.time()
        sent = False
        try:
            host_header = self.headers.get('Host')
            print('Host header: {}'.format(host_header))
            service_found = False
            for service in args['proxy']['services']:
                # default load balancing strategy is "random"
                lb_strategy = 'random'
                # if there's another load balancing strategy defined for this service, we'll use it
                if 'lb-strategy' in service:
                    lb_strategy = service['lb-strategy']
                # let's find where to proxy (to which downstream service)
                if host_header == service['domain']:
                    service_found = True
                    if lb_strategy == 'random':
                        no_of_hosts = len(service['hosts'])
                        index_of_host = random.randint(0, no_of_hosts-1)
                    elif lb_strategy == 'round-robin':
                        if 'active_host' in service:
                            service['active_host'] += 1
                            if service['active_host'] >= len(service['hosts']):
                                service['active_host'] = 0
                        else:
                            service['active_host'] = 0
                        index_of_host = service['active_host']
                    url = 'http://{}:{}{}'.format(
                        service['hosts'][index_of_host]['address'], service['hosts'][index_of_host]['port'], self.path)
                    print('Proxying to "{}" via strategy "{}"'.format(
                        url, lb_strategy))
                    resp = requests.get(url, verify=False)
                    sent = True

                    self.send_response(resp.status_code)
                    self.send_header("Content-Type", self.error_content_type)
                    self.send_header('Content-Length', len(resp.content))
                    self.end_headers()
                    if body:
                        self.wfile.write(resp.content)
                    # once I've sent the request and returned the response, I can safely exit the for loop
                    break
            if not service_found:
                self.send_error(
                    404, 'please use one of the domains in the config file')
        finally:
            # we'll use finish to store the time when we exited this routine, to calculate latency
            finish = time.time()
            sli_latency['last_request'] = finish - start
            if sli_latency['average'] == -1:
                # this is the first request ever
                sli_latency['average'] = sli_latency['last_request']
            else:
                # this is not the first request, so let's recalculate the average latency
                sli_latency['average'] = (
                    sli_latency['average'] + sli_latency['last_request'])/2
            print('Latency statistics (in seconds with 18 decimals)\nlast request / average: {} / {}'.format(
                sli_latency['last_request'], sli_latency['average']))
            if not sent:
                self.send_error(404, 'error trying to proxy')


def parse_config(config_file):
    with open(config_file, 'r') as stream:
        args = yaml.safe_load(stream)
    return args


def main(argv=sys.argv[1:]):
    global args
    args = parse_config("proxy.yaml")
    print('http server is starting on {}:{}...'.format(
        args['proxy']['listen']['address'], args['proxy']['listen']['port']))
    server_address = (args['proxy']['listen']['address'],
                      args['proxy']['listen']['port'])
    # we'll use sli_latency to calculate and store the latency
    # sli = service level indicator
    # sli_latency is a dictionary holding
    #   the latency of the last request and
    #   the average latency of all requests since the server was started
    global sli_latency
    sli_latency = {'last_request': -1, 'average': -1}
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()


if __name__ == '__main__':
    main()
