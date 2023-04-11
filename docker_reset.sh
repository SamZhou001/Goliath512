docker rm -f $(docker ps -aq)
docker image prune -a
