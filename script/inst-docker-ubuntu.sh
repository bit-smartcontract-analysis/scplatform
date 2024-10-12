#!/bin/bash

echo '#######################################################################'
echo '# sudo apt-get remove docker docker-engine docker.io containerd runc docker-compose'
sudo apt-get remove docker docker-engine docker.io containerd runc docker compose -y
sudo snap remove docker

echo '#######################################################################'
echo '# sudo apt-get update'
sudo apt-get update -y
sudo apt-get install ca-certificates curl gnupg lsb-release -y
sudo mkdir -p /etc/apt/keyrings
sudo rm -rf /etc/apt/keyrings/docker.gpg
sudo curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] http://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu  \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo '#######################################################################'
echo '# sudo apt-get update 2'
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
# sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

echo '#######################################################################'
echo '# cat /etc/docker/daemon.json'
echo -e '{\n   "registry-mirrors": ["https://docker.1panel.dev", "https://docker.anyhub.us.kg", "https://docker.m.daocloud.io", "https://dockerproxy.com", "https://docker.mirrors.ustc.edu.cn"],\n    "dns": ["114.114.114.114"] \n}' | sudo tee /etc/docker/daemon.json

sudo chmod 666 /var/run/docker.sock
sudo usermod -aG docker $USER
sudo systemctl daemon-reload
sudo service docker restart
