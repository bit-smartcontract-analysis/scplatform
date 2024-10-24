#!/bin/bash

SCRIPT_PWD="$(pwd)"

echo '#######################################################################'
docker compose -f docker-compose.yaml up -d --build sc-platform-docker-image-registry
docker compose -f docker-compose.yaml up -d --build sc-platform

echo '#######################################################################'
echo '# Go back to home'
cd $SCRIPT_PWD
