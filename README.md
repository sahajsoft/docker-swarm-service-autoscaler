# Docker swarm service autoscaler [![Build Status](https://travis-ci.org/sahajsoft/docker-swarm-service-autoscaler.svg?branch=master)](https://travis-ci.org/sahajsoft/docker-swarm-service-autoscaler?branch=master)

> Currently in Pre-Aplha stage

Scales the number of docker containers for service based on threshold(s) for metrics

## Configuration

```yml
poll_interval_seconds: 10
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

### Run

#### Using code (local)

```
# Ensure python 2.x and pip installed
pip install -r app/requirements.txt
python -m app.main example/autoscaler.yml --log-level debug
```

#### Using docker

> This must be run on a docker swarm master node

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
```

## Example

Please checkout the [examples here](example/README.md)

## TODO

- [x] Docker image for this service
- [x] Runnable example setup for testing the autoscaler
- [x] Docker hub automated build
- [x] Tests and CI setup
- [x] Use docker HTTP API(instead of docker CLI) to get replica_count and for scaling
- [ ] Cool off period for scaling
- [ ] Defaults for missing configuration which can have defaults
- [ ] Helpful error for missing configuration
- [ ] Support for InfluxDB as metric store
- [ ] Demo video
- [ ] Can there be a reverse case where scale up should happen when metric value is below threshold? Or Validation for scale_up_threshold > scale_down_threshold
- [ ] HA mode for autoscaler
