import subprocess


class DockerCLIBasedClient(object):
  def get_service_replica_count(self, service_name):
    service_name_filter = "name={}".format(service_name)
    service_replicas_line = subprocess.check_output(['docker', 'service', 'ls', '--filter', service_name_filter, '--format', '{{.Replicas}}']).strip()
    service_replica_count = int(service_replicas_line.split("/")[0])
    return service_replica_count

  def scale_service(self, service_name, replica_count):
    subprocess.check_output(['docker', 'service', 'scale', "{}={}".format(service_name, replica_count)])
