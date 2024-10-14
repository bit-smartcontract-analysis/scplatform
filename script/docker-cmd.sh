#!/bin/bash

service docker start
service ssh start

# Initialize MySQL data directory if it doesn't exist
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo 'Initializing database...'
    mysqld --initialize-insecure --user=mysql
    echo 'Database initialized.'
fi

# 暴露 3306
sudo sed -i.bak 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i.bak 's/^mysqlx-bind-address.*/mysqlx-bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf

echo 'Starting MySQL server...'
mysqld_safe 
# service mysql restart

# Wait for MySQL to start
echo 'Waiting for MySQL to start...'
until mysqladmin ping --silent; do
    sleep 1
done

# Set root password and create database if not already done
echo 'Setting root password and creating database...'
mysql -u root <<-EOSQL
    ALTER USER 'root'@'localhost' IDENTIFIED BY '000000';
    CREATE DATABASE IF NOT EXISTS sc_platform;
    FLUSH PRIVILEGES;
EOSQL
touch /var/lib/mysql/.mysql_initialized


rm -rf migrations
python3 -m flask db init >> /tmp/flask-db.log 
python3 -m flask db migrate >> /tmp/flask-db.log 
python3 -m flask db upgrade >> /tmp/flask-db.log 

# nohup bash -c 'npm run start >> /tmp/node.log 2>&1' >& /tmp/node.log &
nohup bash -c 'redis-server >> /tmp/redis.log 2>&1' >& /tmp/redis.log &
nohup bash -c 'python3 app.py >> /tmp/flask.log 2>&1' >& /tmp/flask.log &
# nohup bash -c 'python3 -m flask run >> /tmp/flask.log 2>&1' >& /tmp/flask.log &
# nohup bash -c 'gunicorn -b :80 app >> /tmp/gunicorn.log' >& /tmp/gunicorn.log &
nohup bash -c 'celery -A app.mycelery worker --loglevel=info -P gevent >> /tmp/celery.log 2>&1' >& /tmp/celery.log &
nohup bash -c 'cnpm run serve >> /tmp/cnpm.log 2>&1' >& /tmp/cnpm.log &

sleep infinity
