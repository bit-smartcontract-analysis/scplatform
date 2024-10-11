#!/bin/bash

SCRIPT_PWD="$(pwd)"

docker stop sc-platform
docker remove sc-platform

echo '#######################################################################'
echo '# Build sc-platform'
docker build --tag sc-platform:v0.0.1 \
  --file $SCRIPT_PWD/dockerfile \
  --progress=plain \
  --ulimit nofile=1024:4096 \
  $SCRIPT_PWD

docker run --name sc-platform sc-platform:v0.0.1

echo '#######################################################################'
echo '# Go back to home'
cd $SCRIPT_PWD