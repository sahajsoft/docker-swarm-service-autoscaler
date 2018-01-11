from mock import Mock, call, patch
import pytest
from app.metricstores import MetricStoreFactory
from app.metricstores.prometheus import PrometheusMetricStore
from app.errors import UknownMetricStoreTypeException


class TestMetricStoreFactory(object):
    def setup(self):
        self.metric_store_factory = MetricStoreFactory()

    def test_get_metric_store_creates_prometheus_metric_store_when_type_is_prometheus(self):
        metric_store_config = {
            "type": "prometheus",
            "prometheus": {
                "url": "http://localhost:9090"
            }
        }

        metric_store = self.metric_store_factory.get_metric_store(metric_store_config)

        assert type(metric_store) == PrometheusMetricStore
        assert metric_store.config == metric_store_config['prometheus']

    def test_get_metric_store_raises_uknown_metric_store_exception_when_type_is_unknown(self):
        metric_store_config = {
            "type": "foo",
            "foo": {
                "url": "http://localhost:9090"
            }
        }

        with pytest.raises(UknownMetricStoreTypeException, message="Unknown metric store type 'foo'"):
            self.metric_store_factory.get_metric_store(metric_store_config)
