# spies

Simplest Proxy I've Ever Seen

<details>
  <summary>How to run it</summary>

You can install it in Python virtual environment

... or...

You can run it via a Docker container

... or...

You can run it on minikube (by installing it via Helm or an Operator and a CRD)

</details>

<details>
  <summary>How to Configure It</summary>

The `proxy.yaml` is the configuration file. You have to restart the application in order for the configuration to take effect. Also, for Docker/minikube, you have to rebuild the Docker image and redeploy the helm chart in order for the configuation to take effect.

### The `listen` Section

This is where you'd specify the interface and TCP port to listen on. You could use `127.0.0.1` as address, but that's complicated to be exposed from Docker containers

### The `services` Section

This is a list with the following items

- `name`: give your service a name
- `domain`: set a domain name for your service. When proxying, spies will identify the service by mapping the `Host` header value to this `domain`. If the `Host` header is not found in this list, the proxy will return `404, 'please use one of the domains in the config file'`
- `lb-strategy`: this is an optional field. The default value is `random`, but `round-robin` can also be set as a load balacing strategy between the `hosts`
- `hosts`: list of hosts/origins to balance between and proxy to. For each host, specify an `address` and a TCP `port`. No SSL verification is done while proxying to SSL

</details>

<details>
  <summary>Running the Python Application</summary>

Requirements / Tested on

- python 3.8

#### Preparing the Environment

```sh
mkdir venv
python3 -m venv venv/
. venv/bin/activate
pip install -r spies/requirements.txt
```

#### Starting the Application

```sh
cd spies
python ./proxy.py
```

Press Ctrl + C to stop the process once you're done

</details>

<details>
  <summary>Running the Docker Container</summary>

Requirements / Tested on

- docker 19

#### Building the Docker Image

```sh
export IMG_TAG=`grep tag spies-helm-chart/values.yaml | awk '{print $2}'`
docker build -t spies:$IMG_TAG .
```

#### Starting the Docker Container

```sh
docker run -it --rm --name spies -p 127.0.0.1:8080:8080 spies:$IMG_TAG
```

Press Ctrl + C to stop the process once you're done

</details>

<details>
  <summary>Running it on Minikube as a Helm Chart</summary>

Requirements / Tested on

- minikube 1.17
- kubectl 1.20
- kubernetes 1.20
- helm 3.5

#### Preparing the Helm Chart

```sh
helm dependency update ./spies-helm-chart && helm package --version `grep version spies-helm-chart/Chart.yaml | awk '{print $2}'` ./spies-helm-chart
```

#### Running it on Minikube as a Helm Chart

```sh
minikube start
eval $(minikube docker-env)
docker build -t spies:$IMG_TAG .
helm upgrade --install spies spies-helm-chart-`grep version spies-helm-chart/Chart.yaml | awk '{print $2}'`.tgz
minikube service spies
kubectl get all
```

You may note that the Docker image must be rebuilt with the docker binary provided by minikube, so that minikube can fetch the image

</details>

<details>
  <summary>Running it on Minikube as an Operator</summary>

Requirements / Tested on

- minikube 1.17
- kubectl 1.20
- kubernetes 1.20
- helm 3.5
- operator-sdk 1.4

#### Building the Docker Image

```sh
eval $(minikube docker-env)
export IMG_TAG=`grep tag spies-helm-chart/values.yaml | awk '{print $2}'`
docker build -t spies:$IMG_TAG .
```

You may note that the Docker image must be rebuilt with the docker binary provided by minikube, so that minikube can fetch the image

#### Deploying the Operator

```sh
cd spies-operator
export OPERATOR_IMG=spies-operator:$IMG_TAG
make docker-build IMG=$OPERATOR_IMG
make deploy IMG=$OPERATOR_IMG
kubectl get all
```

#### Deploy the Proxy CRD

```sh
cd spies-operator
kubectl apply -f config/samples/charts_v1alpha1_spies.yaml
kubectl get all
minikube service spies
```

</details>

<details>
  <summary>Sample Requests</summary>

In the below examples, you may want to replace "127.0.0.1:8080" with the specific IP:Port on which the proxy is exposed (for example, what `minikube service spies` returns)

```sh
curl -H "Host:wikipedia.org" http://127.0.0.1:8080/wiki/Tesla_Model_X
curl -H "Host:robots.txt" http://127.0.0.1:8080/robots.txt
curl -H "Host:this-must-fail.com" http://127.0.0.1:8080/bla
curl -H "Host:the.one" http://127.0.0.1:8080/robots.txt
```

</details>

<details>
  <summary>Known Issues and Limitations</summary>

- The biggest limitation is that... this proxy is not nginx... nor envoy, or HAproxy or Apache HTTPD... This is just for fun and/or academic purposes

- You have to restart the application if you've changed the configuration file; In case of Docker, you need to rebuild the image and restart the container if you've changed the configuration file; In case of Kubernetes, you also have to repackage the Helm chart and re-deploy it in case you've changed the configuration file
</details>
