@bp.get("/execute/conkas")
def execute_conkas_analysis():
    try:
        host_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        host_script_path = os.path.join(host_data_path, 'tools/conkas/scripts')
        container_script_path = "/data/tools/conkas/scripts/run_analysis.sh"
        image_name = "smartbugs/conkas:4e0f256"
        image = None
        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)

        # Define the volume mapping for both the script and the data
        volumes = {
            host_script_path: {'bind': '/data/tools/conkas/scripts', 'mode': 'ro'},
            host_data_path: {'bind': '/data', 'mode': 'rw'}
        }

        # Create the container with the volume mappings
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        container.start()

        # Execute the script inside the container
        exit_code, output = container.exec_run(container_script_path)

        # Optionally, stop and remove the container
        container.stop()
        container.remove()

        if exit_code != 0:
            return jsonify({"error": "Command returned non-zero exit status", "logs": output.decode('utf-8')}), 500

        return jsonify({"message": "Analysis completed successfully", "logs": output.decode('utf-8')}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/execute/slither")
def execute_slither_analysis():
    try:
        host_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        host_script_path = os.path.join(host_data_path, 'tools/slither/scripts')
        container_script_path = "/data/tools/slither/scripts/run_analysis.sh"
        image_name = "smartbugs/slither:latest"
        image = None
        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
        # Define the volume mapping for both the script and the data
        volumes = {
            host_script_path: {'bind': '/scripts', 'mode': 'ro'},
            host_data_path: {'bind': '/data', 'mode': 'rw'}
        }

        # Create the container with the volume mappings
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        container.start()

        # Execute the script inside the container
        exit_code, output = container.exec_run(container_script_path)

        # Optionally, stop and remove the container
        container.stop()
        container.remove()

        if exit_code != 0:
            return jsonify({"error": "Command returned non-zero exit status", "output": output.decode('utf-8')}), 500

        return jsonify({"message": "Analysis completed successfully", "output": output.decode('utf-8')}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@bp.get("/execute/solhint")
def execute_oyente_analysis():
    try:
        host_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        host_script_path = os.path.join(host_data_path, 'tools/solhint/scripts')
        container_script_path = "/data/tools/solhint/scripts/run_analysis.sh"
        image_name = "smartbugs/solhint:3.3.8"
        image = None
        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
        # Define the volume mapping for both the script and the data
        volumes = {
            host_script_path: {'bind': '/scripts', 'mode': 'ro'},
            host_data_path: {'bind': '/data', 'mode': 'rw'}
        }

        # Create the container with the volume mappings
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        container.start()
        # Execute the script inside the container
        exit_code, output = container.exec_run(container_script_path)

        # Optionally, stop and remove the container
        container.stop()
        container.remove()

        if exit_code != 0:
            return jsonify({"error": "Command returned non-zero exit status", "output": output.decode('utf-8')}), 500

        return jsonify({"message": "Analysis completed successfully", "output": output.decode('utf-8')}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500