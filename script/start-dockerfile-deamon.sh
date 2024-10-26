#!/bin/bash

pull_image() {
    image_name=$1

    # Check if the image exists in the local registry
    result=$(curl -s http://localhost:5001/v2/_catalog | jq -r ".repositories[]" | grep "^$image_name$")

    if [ "$result" != "" ]; then
        echo "Pulling image $image_name from localhost:5001..."
        docker tag localhost:5001/$image_name $image_name 
    else
        echo "Image $image_name not found in localhost:5001. Pulling from Docker Hub..."
        docker pull $image_name
        docker tag $image_name localhost:5001/$image_name
        docker push localhost:5001/$image_name 
    fi
}

# run main services
nohup bash -c 'redis-server >> /tmp/redis.log 2>&1' >& /tmp/redis.log &
nohup bash -c 'python3 app.py >> /tmp/flask.log 2>&1' >& /tmp/flask.log &
nohup bash -c 'celery -A app.mycelery worker --loglevel=info -P gevent >> /tmp/celery.log 2>&1' >& /tmp/celery.log &

# start docker registry
mkdir -p /etc/docker/registry
tee /etc/docker/registry/config.yml > /dev/null <<EOF
version: 0.1
log:
  fields:
    service: registry
storage:
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: :5001
EOF
env REGISTRY_PORT=5001 docker-registry serve /etc/docker/registry/config.yml &

# Pull docker image for detection 
service docker start
pull_image smartbugs/slither:latest &
pull_image weiboot/wana:v1.0 &

# Initialize MySQL data directory if it doesn't exist
service mysql stopkk
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo 'Initializing database...'
    mysqld --initialize-insecure --user=mysql
    echo 'Database initialized.'
fi

# 暴露 3306
sudo sed -i.bak 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i.bak 's/^mysqlx-bind-address.*/mysqlx-bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf

echo 'Starting MySQL server...'
mysqld_safe --skip-grant-tables --skip-networking &
# service mysql restart

# Wait for MySQL to start
echo 'Waiting for MySQL to start...'
until mysqladmin ping --silent; do
    sleep 1
done

# Set root password and create database if not already done
echo 'Setting root password and creating database...'
mysql -u root <<-EOSQL
    FLUSH PRIVILEGES;
    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '000000';
    CREATE DATABASE IF NOT EXISTS sc_platform;
EOSQL
touch /var/lib/mysql/.mysql_initialized
service mysql restart

rm -rf migrations
python3 -m flask db init >> /tmp/flask-db.log 
python3 -m flask db migrate >> /tmp/flask-db.log 
python3 -m flask db upgrade >> /tmp/flask-db.log 

tail -f /tmp/*.log

# sleep infinity
