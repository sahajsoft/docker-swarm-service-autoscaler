from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Autoscaler(object):
    def __init__(self, config, docker_client, metric_store_factory, scheduler, datetime_module=None):
        self.config = config
        self.docker_client = docker_client
        self.metric_store_factory = metric_store_factory
        self.scheduler = scheduler
        self.metric_stores_map = {}
        self.datetime_module = datetime_module or datetime
        metric_store_configs = self.config['metric_stores']
        for metric_store_config in metric_store_configs:
            metric_store_name = metric_store_config['name']
            metric_store = self.metric_store_factory.get_metric_store(metric_store_config)
            self.metric_stores_map[metric_store_name] = metric_store

    def start(self):
        job = self.scheduler.add_job(self.run, 'interval', seconds=self.config['poll_interval_seconds'])
        job.modify(next_run_time=self.datetime_module.now(self.scheduler.timezone))
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

            current_replica_count = self.docker_client.get_service_replica_count(service_name=service_name)
            logger.debug("Replica count for {}: {}".format(service_name, current_replica_count))
            metric_value = metric_store.get_metric_value(metric_query)
            logger.debug("Metric value for {}: {}".format(service_name, metric_value))
            if metric_value > scale_up_threshold and (current_replica_count + scale_step) <= scale_max:
                logger.info("Scaling up {} from {} to {} as metric value is {}".format(service_name, current_replica_count, current_replica_count + scale_step, metric_value))
                self.docker_client.scale_service(service_name=service_name, replica_count=current_replica_count + scale_step)
            if metric_value < scale_down_threshold and (current_replica_count - scale_step) >= scale_min:
                logger.info("Scaling down {} from {} to {} as metric value is {}".format(service_name, current_replica_count, current_replica_count - scale_step, metric_value))
                self.docker_client.scale_service(service_name=service_name, replica_count=current_replica_count - scale_step)

