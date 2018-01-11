class ServiceNotFoundException(Exception):
    def __init__(self, service_name):
        super(ServiceNotFoundException, self).__init__("Service by name '{}' not found".format(service_name))
