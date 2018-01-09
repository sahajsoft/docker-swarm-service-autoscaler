from mock import Mock, call, patch
from app.metricstores.prometheus import PrometheusMetricStore


class TestPrometheusMetricStore(object):
    def setup(self):
        self.config = {
            "url": "http://localhost:9090"
        }
        self.metric_store = PrometheusMetricStore(self.config)

    @patch('requests.get')
    def test_get_metric_value_calls_prometheus_quey_api_for_given_metric_query(self, requests_get):
        metric_query = "scalar(avg(http_requests_total))"

        self.metric_store.get_metric_value(metric_query)

        requests_get.assert_called_once_with('http://localhost:9090/api/v1/query', params={'query': 'scalar(avg(http_requests_total))'})

    @patch('requests.get')
    def test_get_metric_value_returns_metric_value_from_metic_query_response(self, requests_get):
        metric_query = "scalar(avg(http_requests_total))"
        response = Mock()
        requests_get.return_value  = response
        response.json.return_value = {
            "status": "success",
            "data": {
                "resultType": "scalar",
                "result": [
                    1515494365.202,
                    "0.06666666666666667"
                ]
            }
        }

        metric_value = self.metric_store.get_metric_value(metric_query)

        assert metric_value == 0.06666666666666667
