import docker
from docker.types import ServiceMode

from ..errors import ServiceNotFoundException


class DockerAPIBasedClient(object):
    def __init__(self, native_docker_client=None):
        self.native_docker_client = native_docker_client or docker.from_env()

    def _get_service(self, service_name):
        services = self.native_docker_client.services.list(filters=dict(name=service_name))
        if(not services):
            raise ServiceNotFoundException(service_name)
        return services[0]

    def get_service_replica_count(self, service_name):
        service = self._get_service(service_name)
        return service.attrs['Spec']['Mode']['Replicated']['Replicas']

    def scale_service(self, service_name, replica_count):
        service = self._get_service(service_name)
        service.update(mode=ServiceMode("replicated", replicas=replica_count))