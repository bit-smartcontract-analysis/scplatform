#!/bin/bash

# 银河麒麟安装正确版本的 docker 和 docker-compse 

# sudo yum install -y docker
# 卸载旧版本的 Docker（如果存在）
sudo dnf remove -y docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine

# Install Docker Compose from a China mirror
DOCKER_VERSION="20.10.21"
DOCKER_COMPOSE_VERSION="2.12.2"
CONTAINERD_VERSION="1.6.21"
rm -rf /tmp/docker-rpm-for-kylin
mkdir -p /tmp/docker-rpm-for-kylin
cd /tmp/docker-rpm-for-kylin
# wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/containerd.io-${CONTAINERD_VERSION}-3.1.el8.x86_64.rpm
# wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-${DOCKER_VERSION}-3.el8.x86_64.rpm
wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-${DOCKER_VERSION}-3.el8.x86_64.rpm
wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-compose-plugin-${DOCKER_COMPOSE_VERSION}-3.el8.x86_64.rpm
sudo dnf install -y ./*.rpm
docker compose version
cd -

echo '#######################################################################'
echo '# cat /etc/docker/daemon.json'
echo -e '{\n   "registry-mirrors": ["https://docker.1panel.dev", "https://docker.anyhub.us.kg", "https://docker.m.daocloud.io", "https://dockerproxy.com", "https://docker.mirrors.ustc.edu.cn"],\n    "dns": ["114.114.114.114"] \n}' | sudo tee /etc/docker/daemon.json

sudo chmod 666 /var/run/docker.sock
sudo usermod -aG docker $USER
sudo systemctl daemon-reload
sudo service docker restart