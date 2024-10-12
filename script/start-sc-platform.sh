#!/bin/bash

SCRIPT_PWD="$(pwd)"

docker compose down
docker image rm scplatform-sc-platform -f 

echo '#######################################################################'
echo '# Build and start sc-platform docker compose'
if grep -q "Kylin" /etc/os-release; then
    echo "This is Kylin OS."
    docker build -t sc-platform . && docker run --name sc-platform --privileged -p 5000:5000 -e FLASK_ENV=development -e FLASK_APP=app.py --ulimit nofile=65536:65536 sc-platform
else
    echo "This is not Kylin OS."
    docker compose up -d
fi

echo '#######################################################################'
echo '# Go back to home'
cd $SCRIPT_PWD