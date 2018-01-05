docker stack rm example
sleep 10 # Wait for stack remove to complete
docker stack deploy example -c docker-compose.yml
