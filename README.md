# Docker swarm service autoscaler [![Build Status](https://travis-ci.org/sahajsoft/docker-swarm-service-autoscaler.svg?branch=master)](https://travis-ci.org/sahajsoft/docker-swarm-service-autoscaler?branch=master) [![codecov](https://codecov.io/gh/sahajsoft/docker-swarm-service-autoscaler/branch/master/graph/badge.svg)](https://codecov.io/gh/sahajsoft/docker-swarm-service-autoscaler)

Scales the number of docker containers for service based on threshold(s) for metrics

## Configuration

```yml
poll_interval_seconds: 60
metric_stores:
  - name: monitoring
    type: prometheus
    prometheus:
      url: http://localhost:9090
autoscale_rules:
  - service_name: example_web
    scale_min: 1
    scale_max: 3
    scale_step: 1
    metric_store: monitoring
    metric_query: scalar(avg(rate(http_requests_total{job="web"}[5m])))
    scale_up_threshold: 300
    scale_down_threshold: 200
```

## Running

> This service must be run on a docker swarm manager node if the connection to docker daemon needs to be established via `/var/run/docker.sock`

> You can alternatively pass docker host url via `DOCKER_HOST` environment variable. You can pass environment variable `DOCKER_TLS_VERIFY` to verify the host against a CA certificate and `DOCKER_CERT_PATH` for specifying
path to a directory containing TLS certificates to use when connecting to the Docker host.

#### Using code (local)

```
# Ensure python 2.x and pip installed
pip install -r app/requirements.txt
python -m app.main example/autoscaler.yml --log-level debug
```

#### Using docker

```
# Change example/autoscaler.yml as per your need
docker run -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/example/autoscaler.yml:/etc/docker-swarm-service-autoscaler/autoscaler.yml sahajsoft/docker-swarm-service-autoscaler /etc/docker-swarm-service-autoscaler/autoscaler.yml --log-level=DEBUG
```

### Running in docker swarm

```
services:
  autoscaler:
    image: sahajsoft/docker-swarm-service-autoscaler
    command: "/etc/docker-swarm-service-autoscaler/autoscaler.yml --log-leve=DEBUG"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    configs:
      - source: autoscaler.yml
        target: /etc/docker-swarm-service-autoscaler/autoscaler.yml
    deploy:
      placement:
        constraints:
          - node.role == manager
```

## Example

Please checkout the [examples here](example/README.md)

## Running tests

```sh
# Run tests
py.test
# Run tests and print coverage
py.test --cov=app
# Run tests and create html covergae report
py.test --cov=app --cov-report html
# Run tests automatically on any file change
ptw
```

## Demo

[![Demo: Docker swarm service autoscaler](https://img.youtube.com/vi/P1KTjvranYI/0.jpg)](https://www.youtube.com/watch?v=P1KTjvranYI)

## Metric stores

* Prometheus (Supported)
* InfluxDB (Pending): [#4](issues/4)

## Contributing

Please raise an [issue](issues) for feature requests & bugs. Please submit a [pull request](pulls) to contribute code