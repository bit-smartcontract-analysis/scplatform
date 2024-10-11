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
    ca-certificates

# Set the Python version as a build argument
ARG PYTHON_VERSION=3.11.0

# Download and compile Python from the Chinese mirror
RUN cd /usr/src \
    && wget https://npmmirror.com/mirrors/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
    && tar xzf Python-$PYTHON_VERSION.tgz \
    && cd Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make install \
    && rm -rf /usr/src/Python-$PYTHON_VERSION*

# Install pip for the specified Python version from the Chinese mirror
# RUN curl -fsSL https://npmmirror.com/mirrors/pip/get-pip.py -o get-pip.py \
#     && python${PYTHON_VERSION%.*} get-pip.py \
#     && rm get-pip.py
RUN python3 -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip

# Configure pip to use Aliyun mirror
RUN pip${PYTHON_VERSION%.*} config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# Specify the Node.js version as a build argument
ARG NODE_VERSION=20.18.0

# Download and install Node.js from the Chinese npm mirror
RUN curl -fsSL https://npmmirror.com/mirrors/node/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz -o node.tar.xz \
    && tar -xJf node.tar.xz -C /usr/local --strip-components=1 \
    && rm node.tar.xz

# Set npm to use the Chinese npm registry mirror
RUN npm config set registry https://registry.npmmirror.com

# Verify installations
RUN node -v
RUN npm -v 
RUN python3 --version
RUN pip3 --version
