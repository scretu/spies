# spies

Simplest Proxy I've Ever Seen

## How to run it?

You can install it in Python virtual environment

... or...

You can run it via a Docker container

... or...

You can run it on minikube

### Running the Python application

Requirements / Tested on

- python 3.8

#### Preparing the environment

```sh
mkdir venv
python3 -m venv venv/
. venv/bin/activate
pip install -r spies/requirements.txt
```

#### Starting the application

```sh
cd spies
python ./proxy.py
```

Press Ctrl + C to stop the process once you're done

### Running the Docker container

Requirements / Tested on

- docker 19

#### Preparing the container

```sh
docker build -t spies:latest .
```

#### Starting the application

```sh
docker run -it --rm --name spies -p 127.0.0.1:8080:8080 spies:latest
```

Press Ctrl + C to stop the process once you're done

### Running it in minikube

Requirements / Tested on

- minikube 1.17
- kubectl 1.20
- kubernetes 1.20

#### Preparing the Helm chart

```sh
helm dependency update ./spies-helm-chart && helm package --version `grep version spies-helm-chart/Chart.yaml | awk '{print $2}'` ./spies-helm-chart
```

#### Running it on minikube

```sh
minikube start
eval $(minikube docker-env)
docker build -t spies:`grep tag spies-helm-chart/values.yaml | awk '{print $2}'` .
helm upgrade --install spies spies-helm-chart-`grep version spies-helm-chart/Chart.yaml | awk '{print $2}'`.tgz
minikube service spies
```

## Sample requests

In the below examples, you may want to replace "127.0.0.1:8080" with the specific IP:Port on which the proxy is exposed (for example, what `minikube service spies` returns)

```sh
curl -H "Host:wikipedia.org" http://127.0.0.1:8080/wiki/Tesla_Model_X
curl -H "Host:robots.txt" http://127.0.0.1:8080/robots.txt
curl -H "Host:this-must-fail.com" http://127.0.0.1:8080/bla
```
