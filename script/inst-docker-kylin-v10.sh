#!/bin/bash

# 银河麒麟安装正确版本的 docker 和 docker-compse 

sudo yum install -y docker

# Install Docker Compose from a China mirror
DOCKER_COMPOSE_VERSION="1.20.0" # Change this to the desired version
sudo curl -L "https://mirrors.aliyun.com/docker-toolbox/linux/compose/$DOCKER_COMPOSE_VERSION/docker-compose-Linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version

echo '#######################################################################'
echo '# cat /etc/docker/daemon.json'
echo -e '{\n   "registry-mirrors": ["https://docker.1panel.dev", "https://docker.anyhub.us.kg", "https://docker.m.daocloud.io", "https://dockerproxy.com", "https://docker.mirrors.ustc.edu.cn"],\n    "dns": ["114.114.114.114"] \n}' | sudo tee /etc/docker/daemon.json

sudo chmod 666 /var/run/docker.sock
sudo usermod -aG docker $USER
sudo systemctl daemon-reload
sudo service docker restart