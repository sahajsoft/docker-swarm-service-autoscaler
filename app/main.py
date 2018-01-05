#!/usr/bin/python

from pytz import utc
from datetime import datetime
import subprocess
import docker
import requests
import argparse
import yaml
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

DEFAULT_LOG_LEVEL='info'


class DockerCLIBasedClient(object):
  def get_service_replica_count(self, service_name):
    service_name_filter = "name={}".format(service_name)
    service_replicas_line = subprocess.check_output(['docker', 'service', 'ls', '--filter', service_name_filter, '--format', '{{.Replicas}}']).strip()
    service_replica_count = int(service_replicas_line.split("/")[0])
    return service_replica_count

  def scale_service(self, service_name, replica_count):
    subprocess.check_output(['docker', 'service', 'scale', "{}={}".format(service_name, replica_count)])


class MetricStoreFactory(object):
  def get_metric_store(self, metric_store_config):
      metric_store_type = metric_store_config['type']
      if metric_store_type == 'prometheus':
        return PrometheusMetricStore(metric_store_config[metric_store_type])


class PrometheusMetricStore(object):
  def __init__(self, config):
    self.config = config

  def get_metric_value(self, metric_query):
    prometheus_url = self.config['url']
    prometheus_query_url = "{}/api/v1/query".format(prometheus_url)
    resposnse = requests.get(prometheus_query_url, params=dict(query=metric_query))
    resposnse_json = resposnse.json()
    return float(resposnse_json['data']['result'][1])


class Autoscaler(object):
  def __init__(self, config):
    self.config = config
    self.scheduler = BlockingScheduler(timezone=utc)
    self.docker_client = DockerCLIBasedClient()
    self.metric_stores_map = {}
    self.metric_store_factory = MetricStoreFactory()
    metric_store_configs = self.config['metric_stores']
    for metric_store_config in metric_store_configs:
      metric_store_name = metric_store_config['name']
      metric_store = self.metric_store_factory.get_metric_store(metric_store_config)
      self.metric_stores_map[metric_store_name] = metric_store

  def start(self):
    job = self.scheduler.add_job(self.run, 'interval', seconds=self.config['poll_interval_seconds'])
    job.modify(next_run_time=datetime.now(utc))
    self.scheduler.start()

  def run(self):
    autoscale_rules = self.config['autoscale_rules']
    for autoscale_rule in autoscale_rules:
      service_name = autoscale_rule['service_name']
      scale_min = autoscale_rule['scale_min']
      scale_max = autoscale_rule['scale_max']
      scale_step = autoscale_rule['scale_step']
      metric_store_name = autoscale_rule['metric_store']
      metric_query = autoscale_rule['metric_query']
      scale_up_threshold = autoscale_rule['scale_up_threshold']
      scale_down_threshold = autoscale_rule['scale_down_threshold']
      metric_store = self.metric_stores_map[metric_store_name]

      current_replica_count = self.docker_client.get_service_replica_count(service_name)
      logging.debug("Replica count for {}: {}".format(service_name, current_replica_count))
      metric_value = metric_store.get_metric_value(metric_query)
      logging.debug("Metric value for {}: {}".format(service_name, metric_value))
      if metric_value > scale_up_threshold and (current_replica_count + scale_step) <= scale_max:
        logging.info("Scaling up {} from {} to {} as metric value is {}".format(service_name, current_replica_count, current_replica_count + scale_step, metric_value))
        self.docker_client.scale_service(service_name, current_replica_count + scale_step)
      if metric_value < scale_down_threshold and (current_replica_count - scale_step) >= scale_min:
        logging.info("Scaling down {} from {} to {} as metric value is {}".format(service_name, current_replica_count, current_replica_count - scale_step, metric_value))
        self.docker_client.scale_service(service_name, current_replica_count - scale_step)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Autoscale services in docker swarm based on rules')
  parser.add_argument('config_file', help='Path of the config file')
  parser.add_argument('--log-level', help='Log level', default = DEFAULT_LOG_LEVEL)
  args = parser.parse_args()
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(args.log_level.upper()))
  with open(args.config_file) as config_file:
    config = yaml.load(config_file)
    logging.debug("Config %s", config)
    autoscaler = Autoscaler(config)
  autoscaler.start()
