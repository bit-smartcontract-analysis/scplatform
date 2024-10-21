# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Set non-interactive mode for apt to avoid prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# Replace default apt sources with Aliyun mirrors for faster downloads in China
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list \
    && sed -i 's|http://security.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list

# Update package lists
RUN apt-get update

# Install necessary packages for building Python
RUN apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libnss3-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    libbz2-dev \
    wget \
    curl \
    ca-certificates \
    net-tools \
    sudo

# Install python
ARG PYTHON_VERSION=3.11.0
RUN cd /usr/src \
    && wget https://npmmirror.com/mirrors/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
    && tar xzf Python-$PYTHON_VERSION.tgz \
    && cd Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make install \
    && rm -rf /usr/src/Python-$PYTHON_VERSION*
RUN python3 -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
RUN pip${PYTHON_VERSION%.*} config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# Install node lst 
ARG NODE_VERSION=20.18.0
RUN curl -fsSL https://npmmirror.com/mirrors/node/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz -o node.tar.xz \
    && tar -xJf node.tar.xz -C /usr/local --strip-components=1 \
    && rm node.tar.xz
RUN npm config set registry https://registry.npmmirror.com

# Install cnpm and yarn
RUN npm install cnpm -g --registry=https://registry.npmmirror.com
RUN npm install yarn -g --registry=https://registry.npmmirror.com

# Install MySQL Server
RUN apt-get install -y mysql-server

# Install Redis 
RUN apt install -y redis-server

# Install Golang
ENV GO_VERSION=1.21.1
ENV GOPATH=/go
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:$GOROOT/bin:$GOPATH/bin
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://mirrors.ustc.edu.cn/golang/go$GO_VERSION.linux-amd64.tar.gz -o go$GO_VERSION.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go$GO_VERSION.linux-amd64.tar.gz \
    && rm go$GO_VERSION.linux-amd64.tar.gz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p $GOPATH/src $GOPATH/bin
WORKDIR /go/src
ENV GOPROXY=https://goproxy.cn,direct

# Verify installations
RUN node -v
RUN npm -v 
RUN yarn -v 
RUN python3 --version
RUN pip3 --version
RUN mysqld --version

# Install python deps
WORKDIR /root/sc-platform
COPY requirements.txt ./requirements.txt 
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# Install node deps
COPY package.json ./package.json 
RUN cnpm i   

# Install https://github.com/hyperledger-labs/chaincode-analyzer with mirror
RUN mkdir -p /srv/chaincode/chaincode-analyzer
RUN git clone https://gitee.com/esenle/chaincode-analyzer.git /srv/chaincode/chaincode-analyzer/
WORKDIR /srv/chaincode/chaincode-analyzer
RUN ls -al
RUN go build ccanalyzer.go
WORKDIR /root/sc-platform

# Install Docker inside a docker
RUN mkdir -p ./script
COPY ./script/inst-docker-ubuntu.sh ./script/inst-docker-ubuntu.sh 
RUN bash ./script/inst-docker-ubuntu.sh 

# Other source file
COPY . ./ 

EXPOSE 5000 
EXPOSE 8080 
EXPOSE 3306 

# cmd
CMD ["/bin/bash", "/root/sc-platform/script/docker-cmd.sh"]
