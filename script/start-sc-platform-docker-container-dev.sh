#!/bin/bash

mkdir -p ./media/docker-image-registry

docker compose -f docker-compose-dev.yaml up -d --build sc-platform
