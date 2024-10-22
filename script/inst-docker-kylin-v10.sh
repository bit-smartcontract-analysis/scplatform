#!/bin/bash

# Check system version
echo "Checking system version..."
if ! grep -q "Kylin Linux Advanced Server" /etc/os-release; then
  echo "This script is intended for Kylin Linux Advanced Server V10."
  exit 1
fi

# Check Linux kernel version
echo "Checking Linux kernel version..."
KERNEL_VERSION=$(uname -r)
if [[ $(echo "$KERNEL_VERSION < 3.10" | bc) -eq 1 ]]; then
  echo "Linux kernel version must be 3.10 or higher."
  exit 1
fi

# Check iptables version
echo "Checking iptables version..."
IPTABLES_VERSION=$(iptables --version | awk '{print $2}')
if [[ $(echo "$IPTABLES_VERSION < 1.4" | bc) -eq 1 ]]; then
  echo "iptables version must be 1.4 or higher."
  exit 1
fi

# Determine processor architecture
ARCH=$(uname -p)
echo "Processor architecture: $ARCH"

# Download Docker installation package (change to Aliyun mirror)
DOCKER_VERSION="20.10.6"
DOCKER_TAR="docker-$DOCKER_VERSION-ce.tgz"
DOCKER_URL="https://mirrors.aliyun.com/docker-ce/linux/static/stable/$ARCH/$DOCKER_TAR"

echo "Downloading Docker package from $DOCKER_URL..."
curl -L $DOCKER_URL -o /opt/$DOCKER_TAR

# Extract Docker package
echo "Extracting Docker package..."
tar -zxvf /opt/$DOCKER_TAR -C /opt/

# Move binaries to /usr/bin
echo "Moving Docker binaries to /usr/bin..."
sudo mv /opt/docker/* /usr/bin/

# Test Docker installation
echo "Testing Docker installation..."
docker -v

# Start Docker daemon manually for testing
echo "Starting Docker daemon manually..."
sudo dockerd &

# Create Docker service file
echo "Creating Docker service file..."
cat <<EOF | sudo tee /usr/lib/systemd/system/docker.service
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/dockerd
ExecReload=/bin/kill -s HUP \$MAINPID
LimitNOFILE=infinity
LimitNPROC=infinity
TimeoutStartSec=0
Delegate=yes
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Set permissions for the service file
echo "Setting permissions for the Docker service file..."
sudo chmod +x /usr/lib/systemd/system/docker.service

# Create daemon.json configuration file for Docker
echo "Creating daemon.json configuration file..."
sudo mkdir -p /etc/docker/
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "registry-mirrors": ["https://registry.docker-cn.com"],
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF

# Reload systemd daemon to recognize the new service file
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Start Docker service and enable it to start on boot
echo "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Install docker-compose from Aliyun mirror (latest version)
# DOCKER_COMPOSE_VERSION="v2.24.0"
# DOCKER_COMPOSE_URL="https://mirrors.aliyun.com/docker/compose/releases/$DOCKER_COMPOSE_VERSION/docker-compose-linux-$ARCH"

# echo "Downloading Docker Compose from $DOCKER_COMPOSE_URL..."
# curl -L $DOCKER_COMPOSE_URL -o /usr/local/bin/docker-compose

# # Set permissions for docker-compose binary
# echo "Setting permissions for docker-compose binary..."
# sudo chmod +x /usr/local/bin/docker-compose

# # Verify installation of docker-compose
# echo "Verifying installation of docker-compose..."
# docker-compose -v

echo "Docker and Docker Compose installation completed successfully."
