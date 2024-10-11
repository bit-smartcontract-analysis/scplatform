FROM ubuntu:focal

RUN sed -i "s@http://.*archive.ubuntu.com@http://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list
RUN sed -i "s@http://.*security.ubuntu.com@http://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade --yes && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes \
      psmisc \
      software-properties-common \
      git \
      vim \
      curl \
      make \
      wget \
      build-essential \
      checkinstall \
      libreadline-gplv2-dev \
      libncursesw5-dev \
      libssl-dev \
      python3-pip \
      libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev \
      net-tools \
      iputils-ping \
      moreutils \
      cmake \
  && rm -rf /var/lib/apt/lists/*

