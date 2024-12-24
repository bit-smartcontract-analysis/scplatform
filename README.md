# Overview for Front View of smart contract platform

This project aims to provide different analysis tools for smart contracts on chainmaker [link](https://chainmaker.org.cn).

# Docker container for Development and Production

All dependencies are installed to the docker container, there is no need to manually configure python3, mysql, redis, etc.

**Note: Only Ubuntu 20.04+ tested**

## Install docker

Start server backend:

```
./script/install-docker-ubuntu.sh
```
## Development

All changes for files in the source folder will take effect via docker volume. 

```
./script/start-sc-platform-docker-container-platform.sh
```

Now static page worked at http://localhost:5000/cms#/scAnalyze and also work for local network.

Then start server frontend optionally, if you want to debug frontend project at the same time, in [changan-SC-vue](https://github.com/bit-smartcontract-analysis/changan-SC-vue) run:

```
npm run serve
```

Now vue dev server worked at http://localhost:8081/cms#/scAnalyze and also work for local network.


## Production 


All changes for files in the source folder will not take effect, must stop and start docker container to modify any file.

```
./script/start-sc-platform-docker-container-prod.sh
```

## Stop all 
Work both for Development and Production 

```
./script/stop-sc-platform-docker-container-all.sh
```

# Troubleshooting

## Dockerhub register cn mirror not working

Its better to config [dockerhub mirror](https://docs.docker.com/docker-hub/image-library/mirror/) with latest mirrors. For example:

```
  "registry-mirrors": [
    "https://docker.1panel.dev",
    "https://docker.anyhub.us.kg",
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
```
