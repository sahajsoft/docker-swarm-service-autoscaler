## Example

* Prerequisites
    * docker 17.09.1-ce
    * apache-workbench(ab)

* Open a shell(1) and run
```
cd example/prometheus
./run.sh
docker service ls
```
These commands deploy the services in docker swarm and lists the services running in swarm.

* Open another shell(2) and run
```
docker service logs example_autoscaler -f
```
This shows information logs of autoscaler service.

* Open another shell(3) and run
```
watch docker service ls
```

* In shell(1), run
```
./generate-load.sh
```
This will generate load on `example_web` service using apache workbench
In shell(2), you can find logs from autoscaler showing scale up of `example_web` service based on load
In shell(3), you can find the replica count of `example_web` increasing from 1 to 3 as configured in `example/prometheus/autoscaler.yml`

* In shell(1), terminate the `./generate-load.sh` process by pressing `ctrl+c`

This will stop load on `example_web` service.

* Check the output of shell(2) and shell(3) to find scale down of `example_web` from 3 to 1
