from mock import Mock, call, patch
from docker.models.services import Service
from docker.types import ServiceMode
import pytest

from app.docker.api_client import DockerAPIBasedClient
from app.errors import ServiceNotFoundException


class TestDockerAPIBasedClient(object):

    def setup(self):
        self.native_docker_client = Mock()
        self.docker_client = DockerAPIBasedClient(self.native_docker_client)

    def test_get_replica_count_returns_replica_count_from_service_spec_for_replicas(self):
        service = Mock(attrs={
                "Spec": {
                    "Mode": {
                        "Replicated": {
                            "Replicas": 2
                        }
                    }
                }
        })
        self.native_docker_client.services.list.return_value = [service]

        service_replica_count = self.docker_client.get_service_replica_count("web")


        self.native_docker_client.services.list.assert_called_once_with(filters=dict(name="web"))
        assert service_replica_count == 2

    def test_get_replica_count_raises_service_not_found_exception_when_service_does_not_exist(self):
        self.native_docker_client.services.list.return_value = []

        with pytest.raises(ServiceNotFoundException, message="Service by name 'foo' not found"):
            service_replica_count = self.docker_client.get_service_replica_count("foo")

        self.native_docker_client.services.list.assert_called_once_with(filters=dict(name="foo"))

    def test_scale_service_updates_the_service_replicas_to_given_replication_count(self):
        service = Mock()
        self.native_docker_client.services.list.return_value = [service]

        self.docker_client.scale_service("web", 3)

        self.native_docker_client.services.list.assert_called_once_with(filters=dict(name="web"))
        service.update.assert_called_once_with(mode=ServiceMode("replicated", replicas=3))

    def test_scale_service_count_raises_service_not_found_exception_when_service_does_not_exist(self):
        self.native_docker_client.services.list.return_value = []

        with pytest.raises(ServiceNotFoundException, message="Service by name 'foo' not found"):
            self.docker_client.scale_service("foo", 3)

        self.native_docker_client.services.list.assert_called_once_with(filters=dict(name="foo"))

