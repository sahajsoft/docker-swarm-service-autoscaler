import requests

class PrometheusMetricStore(object):
  def __init__(self, config):
    self.config = config

  def get_metric_value(self, metric_query):
    prometheus_url = self.config['url']
    prometheus_query_url = "{}/api/v1/query".format(prometheus_url)
    resposnse = requests.get(prometheus_query_url, params=dict(query=metric_query))
    resposnse_json = resposnse.json()
    return float(resposnse_json['data']['result'][1])
