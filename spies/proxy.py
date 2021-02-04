#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import os
import random
import sys
import requests
import yaml


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    # TODO: your server must then include an accurate Content-Length header (using send_header()) in all of its responses to clients
    protocol_version = 'HTTP/1.1'

    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
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
                if host_header == service['domain']:
                    service_found = True
                    if lb_strategy == 'random':
                        no_of_hosts = len(service['hosts'])
                        index_of_host = random.randint(0, no_of_hosts-1)
                        url = 'http://{}:{}{}'.format(
                            service['hosts'][index_of_host]['address'], service['hosts'][index_of_host]['port'], self.path)
                    elif lb_strategy == 'round-robin':
                        print('now this is something different')
                    print('Proxying to "{}" via strategy "{}"'.format(
                        url, lb_strategy))
                    resp = requests.get(url, verify=False)
                    sent = True

                    self.send_response(resp.status_code)
                    # self.send_resp_headers(resp)
                    self.send_header("Content-Type", self.error_content_type)
                    self.send_header('Content-Length', len(resp.content))
                    # self.send_header('Connection', 'close')
                    self.end_headers()
                    if body:
                        self.wfile.write(resp.content)
                        self.wfile.close()
                    return
            if not service_found:
                self.send_error(
                    404, 'please use one of the domains in the config file')
        finally:
            self.finish()
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
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()


if __name__ == '__main__':
    main()