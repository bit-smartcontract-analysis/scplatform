#!/bin/bash

mkdir -p ./media/docker-image-registry

docker compose -f docker-compose-prod.yaml up -d --build sc-platform
