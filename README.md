# Overview for Front View of smart contract platform
This project aims to provide different analysis tools for smart contracts on chainmaker [link](https://chainmaker.org.cn).

# Docker container for Development and Production

All dependencies are installed to the docker container, there is no need to manually configure python3, mysql, redis, etc.

Its better to config china mirror for docker hub, which could always changed.

```
  "registry-mirrors": [
    "https://docker.1panel.dev",
    "https://docker.anyhub.us.kg",
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
```

Linux 

```

```

Windows

```

```


## Development

```

```


## Production

Windows
```
.\script\start-sc-platform-docker-container.cmd
```

Linux

```

```

=======

## How to install on your server

* You can download the zip or clone the project with git.

    `https://github.com/bit-smartcontract-analysis/changan-SC-platform.git`

* Install `equirements.txt` via terminal: 

    `pip install -r /path/to/requirements.txt`

* Install MySQL：

    mYSQL is available at [link](https://dev.mysql.com/downloads/mysql/).


## Quick start

* To enable all development features (including debug mode) you can export the FLASK_ENV environment variable and set it to development before running the server:

    `export FLASK_ENV=development`

* To run the application you can use the **flask** command or python’s -m switch with Flask. Before you can do that you need to tell your terminal the application to work with by exporting the **FLASK_APP** environment variable:

    `export FLASK_APP=app.py`

* To test the web app, execute

    ``` Shell
    $ flask run
        * Running on http://127.0.0.1:5000/
    ```

* Alternatively you can use python -m flask:
    ``` Shell
    $ python -m flask run
        * Running on http://127.0.0.1:5000/
    ```
## How to use

* 如果是第一次使用，请在MySQL建立相应的database，并安装config.py进行配置（你也可以根据你的需要修改配置）

* 删除文件migrations，并建立自己的db数据库通过一下指令：
    ``` Shell
   $ flask db init
   $ flask db migrate
   $ flask db upgrade
    ```

* 如果你想快速得到一些示例，可以运行以下指令
    ``` Shell
    $ Flask init_boards (init_roles, bind_roles, create_test_posts)
    ```

* 在注册用户的时候，由于本项目使用了celery机制异步发送，需要开启celery通过(注意，不同的系统celery安装方法不同，下面仅介绍windows)
    ``` Shell
    $ celery -A app.mycelery worker --loglevel=info -P gevent
    ```

* 在第一次使用的时，可以通过flask指令初始化一些配置,例如添加测试用户，添加测试post
    ``` Shell
    $ flask create_test_users 
    $ flask create_test_posts
    ``` 
 
## 脚本指令
  如果非开发人员，可以直接使用脚本指令，前提需要保证您的系统是windows，同时安装python3.8
* 配置环境
  ```
  点击install_app.bat
  ```
* 运行程序
  ```
  点击run_app.bat, 以及run_celery_mail.bat
  ```

## Requirements

* Python 3.8+
* Flask
