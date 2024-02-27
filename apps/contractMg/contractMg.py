from flask import (
    Blueprint,
    jsonify
)
import docker
import os


bp = Blueprint("contractMg", __name__, url_prefix="/contractMg")
# client = docker.from_env()

container = None

project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


@bp.get("/startRemix")
def start_Docker():
    global container
    client = docker.from_env()
    try:
        host_path = project_root_path
        image_name = "remixproject/remix-ide:latest"
        image = None
        message = ''

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        ports = {'80/tcp': 3000}

        container = client.containers.run(image_name, detach=True, ports=ports, volumes=volumes)
        container.start()

        return jsonify({"message": "successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/stopRemoveRemix")
def stop_remove_docker():
    client = docker.from_env()
    try:
        image_name = "remixproject/remix-ide:latest"
        containers_stopped = 0

        # Iterate through all running containers
        for container in client.containers.list():
            # Check if the container is running the specified image
            if container.image.tags[0] == image_name:
                container.stop()  # Stop the container
                container.remove()  # Remove the container
                containers_stopped += 1

        if containers_stopped > 0:
            message = f'successfully.'
        else:
            message = 'No container running the specified image was found.'

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/checkRemixRunning")
def check_docker():
    client = docker.from_env()
    try:
        image_name = "remixproject/remix-ide:latest"
        is_running = False

        # Iterate through all running containers
        for container in client.containers.list():
            # Check if the container is running the specified image
            if container.image.tags[0] == image_name:
                is_running = True
                break  # No need to check other containers once we find a match

        message = 'Running' if is_running else 'Not running'

        return jsonify({"status": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500