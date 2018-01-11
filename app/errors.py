class ServiceNotFoundException(Exception):
    def __init__(self, service_name):
        super(ServiceNotFoundException, self).__init__("Service by name '{}' not found".format(service_name))


class UknownMetricStoreTypeException(Exception):
    def __init__(self, metric_store_type):
        super(UknownMetricStoreTypeException, self).__init__("Unknown metric store type '{}'".format(metric_store_type))
