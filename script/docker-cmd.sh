#!/bin/bash

# Initialize MySQL data directory if it doesn't exist
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo 'Initializing database...'
    mysqld --initialize-insecure --user=mysql
    echo 'Database initialized.'
fi

echo 'Starting MySQL server...'
mysqld_safe &

# Wait for MySQL to start
echo 'Waiting for MySQL to start...'
until mysqladmin ping --silent; do
    sleep 1
done

# Set root password and create database if not already done
if [ ! -f /var/lib/mysql/.mysql_initialized ]; then
    echo 'Setting root password and creating database...'
    mysql -u root <<-EOSQL
        ALTER USER 'root'@'localhost' IDENTIFIED BY '000000';
        CREATE DATABASE IF NOT EXISTS sc_platform;
        FLUSH PRIVILEGES;
EOSQL
    touch /var/lib/mysql/.mysql_initialized
fi


rm -rf migrations
python3 -m flask db init >> /tmp/flask-db.log 
python3 -m flask db migrate >> /tmp/flask-db.log 
python3 -m flask db upgrade >> /tmp/flask-db.log 

# nohup bash -c 'npm run start >> /tmp/node.log 2>&1' >& /tmp/node.log &
nohup bash -c 'redis-server >> /tmp/redis.log 2>&1' >& /tmp/redis.log &
sleep 5
nohup bash -c 'python3 app.py >> /tmp/flask.log 2>&1' >& /tmp/flask.log &
# nohup bash -c 'python3 -m flask run >> /tmp/flask.log 2>&1' >& /tmp/flask.log &
# nohup bash -c 'gunicorn -b :80 app >> /tmp/gunicorn.log' >& /tmp/gunicorn.log &
# nohup bash -c ' >> /tmp/gunicorn.log' >& /tmp/gunicorn.log &
sleep 5
nohup bash -c 'celery -A app.mycelery worker --loglevel=info -P gevent >> /tmp/celery.log 2>&1' >& /tmp/celery.log &

sleep infinity
