from mock import Mock, call, patch
from pytz import utc
from app.autoscaler import Autoscaler
from datetime import datetime

class TestAutoscaler(object):

    def setup(self):
        self.config = {
            "poll_interval_seconds": 60,
            "metric_stores": [
                {
                    "name": "monitoring",
                    "type": "prometheus",
                    "prometheus": {
                        "url": "http://localhost:9090"
                    }
                }
            ],
            "autoscale_rules": [
                {
                    "service_name": "web",
                    "scale_min": 1,
                    "scale_max": 3,
                    "metric_store": "monitoring",
                    "metric_query": "scalar(avg(http_requests_total))",
                    "scale_up_threshold": 300,
                    "scale_down_threshold": 250,
                    "scale_step": 1
                }
            ]
        }
        self.docker_client = Mock()
        self.metric_store_factory = Mock()
        self.monitoring_metric_store = Mock()
        self.scheduler = Mock()
        self.mock_datetime = Mock()
        self.metric_store_factory.get_metric_store.return_value = self.monitoring_metric_store
        self.autoscaler = Autoscaler(self.config, self.docker_client, self.metric_store_factory, self.scheduler, self.mock_datetime)

    def test_run_gets_replica_count_of_the_service_from_docker_client(self):
        self.docker_client.get_service_replica_count.return_value = 1
        self.monitoring_metric_store.get_metric_value.return_value = 100

        self.autoscaler.run()

        self.docker_client.get_service_replica_count.assert_called_once_with(service_name="web")

    def test_run_gets_metric_value_from_metric_strore_for_configured_metric_query(self):
        self.docker_client.get_service_replica_count.return_value = 1
        self.monitoring_metric_store.get_metric_value.return_value = 100

        self.autoscaler.run()

        self.monitoring_metric_store.get_metric_value.assert_called_once_with("scalar(avg(http_requests_total))")

    def test_run_scales_up_service_replicas_when_metric_value_is_above_scale_up_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 1
        self.monitoring_metric_store.get_metric_value.return_value = 301

        self.autoscaler.run()

        self.docker_client.scale_service.assert_called_once_with(service_name = "web", replica_count = 2)

    def test_run_scales_up_service_replicas_when_metric_value_is_above_scale_up_threshold_and_current_replica_count_is_close_to_scale_max(self):
        self.docker_client.get_service_replica_count.return_value = 2
        self.monitoring_metric_store.get_metric_value.return_value = 301

        self.autoscaler.run()

        self.docker_client.scale_service.assert_called_once_with(service_name = "web", replica_count = 3)

    def test_run_scales_down_service_replicas_when_metric_value_is_below_scale_down_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 3
        self.monitoring_metric_store.get_metric_value.return_value = 249

        self.autoscaler.run()

        self.docker_client.scale_service.assert_called_once_with(service_name = "web", replica_count = 2)

    def test_run_scales_down_service_replicas_when_metric_value_is_below_scale_down_threshold_and_current_replica_count_close_to_scale_down_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 2
        self.monitoring_metric_store.get_metric_value.return_value = 249

        self.autoscaler.run()

        self.docker_client.scale_service.assert_called_once_with(service_name = "web", replica_count = 1)

    def test_run_does_not_scale_up_service_replicas_when_current_replica_count_equals_scale_max(self):
        self.docker_client.get_service_replica_count.return_value = 3
        self.monitoring_metric_store.get_metric_value.return_value = 301

        self.autoscaler.run()

        self.docker_client.scale_service.assert_not_called()

    def test_run_does_not_scale_up_service_replicas_when_metric_value_equals_scale_up_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 1
        self.monitoring_metric_store.get_metric_value.return_value = 300

        self.autoscaler.run()

        self.docker_client.scale_service.assert_not_called()

    def test_run_does_not_scale_up_service_replicas_when_metric_value_is_below_scale_up_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 1
        self.monitoring_metric_store.get_metric_value.return_value = 299

        self.autoscaler.run()

        self.docker_client.scale_service.assert_not_called()

    def test_run_does_not_scale_down_service_replicas_when_current_replica_count_equals_scale_min(self):
        self.docker_client.get_service_replica_count.return_value = 1
        self.monitoring_metric_store.get_metric_value.return_value = 249

        self.autoscaler.run()

        self.docker_client.scale_service.assert_not_called()

    def test_run_does_not_scale_down_service_replicas_when_metric_value_equals_scale_down_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 2
        self.monitoring_metric_store.get_metric_value.return_value = 250

        self.autoscaler.run()

        self.docker_client.scale_service.assert_not_called()

    def test_run_does_not_scale_down_service_replicas_when_metric_value_is_above_scale_down_threshold(self):
        self.docker_client.get_service_replica_count.return_value = 2
        self.monitoring_metric_store.get_metric_value.return_value = 251

        self.autoscaler.run()

        self.docker_client.scale_service.assert_not_called()

    def test_start_starts_the_scheduler(self):
        self.scheduler.timezone = utc

        self.autoscaler.start()

        self.scheduler.start.assert_called_once()

    def test_start_schedules_the_job_to_run_autoscaler_for_each_poll_interval_seconds(self):
        self.scheduler.timezone = utc

        self.autoscaler.start()

        self.scheduler.add_job.assert_called_once_with(self.autoscaler.run, 'interval', seconds=60)

    def test_start_runs_the_job_to_run_autoscaler_immediately(self):
        job = Mock()
        current_time = datetime.now()
        self.scheduler.timezone = utc
        self.mock_datetime.now.return_value = current_time
        self.scheduler.add_job.return_value = job

        self.autoscaler.start()

        self.mock_datetime.now.assert_called_once_with(utc)
        job.modify.assert_called_once_with(next_run_time=current_time)
