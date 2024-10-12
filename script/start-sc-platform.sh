#!/bin/bash

SCRIPT_PWD="$(pwd)"

docker compose down
docker image rm scplatform-sc-platform -f 

echo '#######################################################################'
echo '# Build and start sc-platform docker compose'
docker compose up -d
# docker build --tag sc-platform:v0.0.1 \
#   --file $SCRIPT_PWD/dockerfile \
#   --progress=plain \
#   --ulimit nofile=1024:4096 \
#   $SCRIPT_PWD

# docker run -d --name sc-platform sc-platform:v0.0.1 

echo '#######################################################################'
echo '# Go back to home'
cd $SCRIPT_PWD