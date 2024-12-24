#!/bin/bash

pull_image() {
    full_image_name=$1

    # Extract image name and tag/digest
    image_name=$(echo "$full_image_name" | cut -d':' -f1)
    image_tag=$(echo "$full_image_name" | cut -d':' -f2)

    # Check if the image with this tag or digest exists in the local registry
    result=$(curl -s "http://localhost:5001/v2/$image_name/tags/list" | jq -r ".tags[]" | grep "^$image_tag$")

    if [ "$result" != "" ]; then
        echo "Image $full_image_name found in localhost:5001. Pulling from local registry..."
        docker pull localhost:5001/$full_image_name
        docker tag localhost:5001/$full_image_name $full_image_name
    else
        echo "Image $full_image_name not found in localhost:5001. Pulling from Docker Hub..."
        docker pull $full_image_name
        docker tag $full_image_name localhost:5001/$full_image_name
        docker push localhost:5001/$full_image_name
    fi
}

wait_for_docker() {
    echo "Waiting for Docker to start..."
    while ! docker info >/dev/null 2>&1; do
        echo "Docker is not yet available. Waiting..."
        sleep 2
    done
    echo "Docker has started successfully."
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
wait_for_docker
pull_image eddiechen1008/smartbugs-slither-snapshot:1e2685153d1b &
pull_image weiboot/wana:v1.0 &

# Initialize MySQL data directory if it doesn't exist
service mysql stop
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
