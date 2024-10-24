#!/bin/bash

# SCRIPT_PWD="$(pwd)"
SCRIPT_PWD=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
SCRIPT_PWD=$(echo "$SCRIPT_PWD" | sed 's|/common/script$||')
SCRIPT_PWD=$(echo "$SCRIPT_PWD" | sed 's|/$||')
echo $SCRIPT_PWD
export GOENV_ROOT="$SCRIPT_PWD/.goenv"
export GO_BUILD_CACHE_PATH="$GOENV_ROOT/cache"
GO_VERSION=1.18.10

# Check if the folder exists
if [ -d "$GOENV_ROOT" ]; then
  echo "The folder $GOENV_ROOT exists."
  export PATH="$GOENV_ROOT/bin:$PATH"
  eval "$(goenv init -)"
  export PATH="$GOROOT/bin:$PATH"
  export PATH="$PATH:$GOPATH/bin"
else
  echo "The folder $GOENV_ROOT not exists, build."
  git clone -b 2.0.6 https://gitee.com/azhao-1981/goenv.git $GOENV_ROOT
  ARCH=$(uname -m)
  echo $ARCH
  URL_ARCH=""
  if [ "$ARCH" = "aarch64" ]; then
    echo "ARM64 architecture"
    URL_ARCH="arm64"
  elif [ "$ARCH" = "x86_64" ]; then
    echo "AMD64 architecture"
    URL_ARCH="amd64"
  else
    echo "Unknown architecture: $ARCH"
  fi

  mkdir -p $GOENV_ROOT/cache/
  cp $SCRIPT_PWD/common/patch/goenv/go-build $GOENV_ROOT/plugins/go-build/bin/
  # wget https://mirrors.aliyun.com/golang/go$GO_VERSION.linux-$URL_ARCH.tar.gz -P $GOENV_ROOT/cache/ 

  export PATH="$GOENV_ROOT/bin:$PATH"
  eval "$(goenv init -)"
  export GO_BUILD_CACHE_PATH="$GOENV_ROOT/cache"
  export PATH="$GOROOT/bin:$PATH"
  export PATH="$PATH:$GOPATH/bin"
  # goenv install --list

  env GO_BUILD_CACHE_PATH="$GOENV_ROOT/cache" goenv install $GO_VERSION
  goenv global $GO_VERSION
  go version
fi

goenv --version
go version
rm -rf ~/.config/go
go env -w GOPROXY=https://goproxy.cn,direct

# cd $SCRIPT_PWD
