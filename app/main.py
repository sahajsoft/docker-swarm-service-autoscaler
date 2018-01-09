#!/usr/bin/python

import argparse
import yaml
import logging
from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler

from .dockerclients.cli_client import DockerCLIBasedClient
from .metricstores import MetricStoreFactory
from .autoscaler import Autoscaler

DEFAULT_LOG_LEVEL='info'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Autoscale services in docker swarm based on rules')
    parser.add_argument('config_file', help='Path of the config file')
    parser.add_argument('--log-level', help='Log level', default = DEFAULT_LOG_LEVEL)
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(args.log_level.upper()))
    with open(args.config_file) as config_file:
        config = yaml.load(config_file)
        logging.debug("Config %s", config)
        metric_store_factory = MetricStoreFactory()
        docker_client = DockerCLIBasedClient()
        scheduler = BlockingScheduler(timezone=utc)
        autoscaler = Autoscaler(config, docker_client, metric_store_factory, scheduler)
    autoscaler.start()
