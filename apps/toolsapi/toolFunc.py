# 使用脚本执行工作的代码放在toolExecute.py文件中
from .process import process_slither_data, process_log_slither, save_to_csv, process_log_evulhunter, process_log_rust, process_log_ccanalyzer

from flask import (
    Blueprint,
    render_template,
    session,
    g,
    request,
    current_app,
    jsonify
)
import docker
import os
from .forms import UploadContractForm
from utils import restful
import time
import subprocess


bp = Blueprint("toolFunc", __name__, url_prefix="/toolFunc")
# client = docker.from_env()

container = None


@bp.get("/")
def index():
    return render_template("sc/scAnalysis.html")


@bp.post("/contracts/upload")
def upload_contracts_file():
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename
        contract_path = os.path.join(current_app.config['CONTRACT_IMAGE_SAVE_PATH'], filename)
        file.save(contract_path)
        return restful.ok(data={"contract_url": filename})
    else:
        message = form.messages[0]
        print(message)
        return restful.params_error(message=message)


@bp.get("/contracts/list")
def list_contracts():
    contract_path = current_app.config.get('CONTRACT_IMAGE_SAVE_PATH', None)
    if contract_path is None:
        return jsonify({"error": "Path not configured"}), 500

    if not os.path.exists(contract_path):
        return jsonify({"error": "Directory not found"}), 404

    try:
        files = os.listdir(contract_path)
        file_data = []

        for file in files:
            file_path = os.path.join(contract_path, file)
            file_size = os.path.getsize(file_path)
            file_data.append({"name": file, "size": file_size})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"files": file_data})


@bp.get("/logs/list")
def list_logs():
    logs_path = current_app.config.get('CONTRACT_LOGS_SAVE_PATH', None)
    if logs_path is None:
        return jsonify({"error": "Path not configured"}), 500

    if not os.path.exists(logs_path):
        return jsonify({"error": "Directory not found"}), 404

    try:
        files = os.listdir(logs_path)
        file_data = []

        for file in files:
            file_path = os.path.join(logs_path, file)
            file_size = os.path.getsize(file_path)
            file_data.append({"name": file, "size": file_size})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"files": file_data})


@bp.post("/contracts/delete")
def delete_contract():
    file_name = request.form.get("contract")
    print('contract: ', file_name)
    if not file_name:
        return jsonify({"error": "No file name provided"}), 400

    contract_path = current_app.config.get('CONTRACT_IMAGE_SAVE_PATH', None)
    if contract_path is None:
        return jsonify({"error": "Path not configured"}), 500

    file_path = os.path.join(contract_path, file_name)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        os.remove(file_path)
        return jsonify({"message": f"{file_name} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/startDocker")
def start_Docker():
    global container
    client = docker.from_env()
    try:
        image_name = "smartbugs/oyente:480e725"
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
            message = "Docker image-" + image_name + " now is pulled and "

        # Run a container using the image
        container = client.containers.run(image_name, detach=True)
        message += 'Docker image-' + image_name + " started successfully"

        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/stopDocker", methods=['GET', 'POST'])
def stop_Docker():
    global container
    try:
        if container:
            container.stop()
            return jsonify({"message": "Docker stopped successfully"}), 200
        else:
            return jsonify({"message": "No active Docker container to stop"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


# 成功生成结果，并能产生输出
@bp.route("/run/mythril", methods=['POST', 'GET'])
def run_myth_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    # print("contract: ", contract)
    # print("start")
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
        image_name = "smartbugs/mythril:0.23.15"
        image = None

        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break
        if image is None:
            client.images.pull(image_name)

        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}
        command = f"analyze -o json {contract_path}"
        container = client.containers.create(image_name, command=command, volumes=volumes)
        start_time = time.time()  # Record start time
        container.start()
        result = container.wait()
        logs = container.logs().decode('utf-8')
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        bugs = "Reentrancy"
        print(logs)
        save_to_csv(contract, bugs, logs)
        return jsonify({"message": "Analysis completed", "exit_code": result['StatusCode'], "logs": logs, "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/oyente", methods=['POST', 'GET'])
def run_oyente_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
        image_name = "smartbugs/oyente:480e725"
        image = None

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

        # Define the command
        command = f"-s {contract_path}"

        # Create and run the container
        container = client.containers.create(image_name, command=command, volumes=volumes)
        start_time = time.time()
        container.start()

        # Wait for the container to finish
        result = container.wait()

        # Retrieve the logs
        logs = container.logs().decode('utf-8')

        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)
        return jsonify({"message": "Analysis completed", "exit_code": result['StatusCode'], "logs": logs, "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/slither", methods=['POST', 'GET'])
def run_slither_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
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

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Define the command
        command = f"slither {contract_path} --json /output.json"

        # Create and run the container
        container = client.containers.create(image_name, command=command, volumes=volumes)
        start_time = time.time()
        container.start()

        # Wait for the container to finish
        result = container.wait()

        # Retrieve the logs
        logs = container.logs().decode('utf-8')

        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)
        return jsonify({"message": "Analysis completed", "exit_code": result['StatusCode'], "logs": logs, "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/conkas",  methods=['POST', 'GET'])
def run_conkas_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
        image_name = "smartbugs/conkas:4e0f256"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                print(image_name + ' is already here')
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
            print("pulling " + image_name)

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Create the container without starting it
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python3 conkas.py -s {contract_path}")
        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        execution_time = end_time - start_time
        container.remove()

        print(output.decode('utf-8'))

        return jsonify({"message": "Analysis completed", "exit_code": exit_code, "logs": output.decode('utf-8'), "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/run/solhint")
def run_solhint_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/sample/{contract}"
        image_name = "smartbugs/solhint:3.3.8"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        if image is None:
            client.images.pull(image_name)

        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        container = client.containers.create(image_name, volumes=volumes, tty=True)
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"solhint -f unix {contract_path}")

        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        print(output.decode('utf-8'))
        return jsonify({"message": "Analysis completed", "exit_code": exit_code, "logs": output.decode('utf-8'), "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/run/confuzzius")
def run_confuzzius_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/sample/{contract}"
        image_name = "smartbugs/confuzzius:4315fb7"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        if image is None:
            client.images.pull(image_name)

        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        container = client.containers.create(image_name, volumes=volumes, tty=True)
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python3 fuzzer/main.py -s {contract_path} --evm byzantium --results results.json --seed 1427655")

        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        print(output.decode('utf-8'))
        return jsonify({"message": "Analysis completed", "exit_code": exit_code, "logs": output.decode('utf-8'), "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/osiris", methods=['POST', 'GET'])
def run_osiris_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/sample/{contract}"
        image_name = "smartbugs/osiris:d1ecc37"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        if image is None:
            client.images.pull(image_name)

        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        container = client.containers.create(image_name, volumes=volumes, tty=True)
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python osiris/osiris.py -s {contract_path}")
        # output = container.logs()
        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        print(output.decode('utf-8'))
        return jsonify({"message": "Analysis completed", "exit_code": exit_code, "logs": output.decode('utf-8'), "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/honeybadger", methods=['POST', 'GET'])
def run_honeybadger_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/sample/{contract}"
        image_name = "smartbugs/honeybadger:ff30c9a"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        if image is None:
            client.images.pull(image_name)

        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        container = client.containers.create(image_name, volumes=volumes, tty=True)
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python honeybadger/honeybadger.py -s {contract_path}")
        # output = container.logs()
        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        print(output.decode('utf-8'))
        return jsonify({"message": "Analysis completed", "exit_code": exit_code, "logs": output.decode('utf-8'), "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/wana_rust", methods=['POST', 'GET'])
def run_wana_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
        image_name = "weiboot/wana:v1.0"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
            print("pulling " + image_name)

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Create the container without starting it
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python3 wana.py -r -e {contract_path}")
        logs = output.decode('utf-8')
        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        execution_time = end_time - start_time
        container.remove()

        print(logs)
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)

        return jsonify(
            {"message": "Analysis completed", "exit_code": exit_code, "logs": logs, "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/run/evulhunter", methods=['POST', 'GET'])
def run_evulhunter_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
        image_name = "weiboot/evulhunter:v0.1"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
            print("pulling " + image_name)

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Create the container without starting it
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python3 EOSVulDetector.py -i \"{contract_path}\"  -t 2 -o \"test.txt\"")
        # Optionally, stop and remove the container
        logs = container.logs().decode('utf-8')

        container.stop()
        end_time = time.time()
        execution_time = end_time - start_time
        container.remove()

        print(logs)

        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)
        return jsonify({"message": "Analysis completed", "exit_code": exit_code, "logs": logs, "time": execution_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.post('/selection')
def tool_selection():
    tools = [
        {'name': 'mythril', 'url': '/run/mythril'},
        {'name': 'oyente', 'url': '/run/oyente'},
        {'name': 'slither', 'url': '/run/slither'},
        # {'name': 'conkas', 'url': '/run/conkas'},
        {'name': 'solhint', 'url': '/run/solhint'},
        {'name': 'confuzzius', 'url': '/run/confuzzius',},
        # {'name': 'security',   'url': '/run/security', },
        # {'name': 'sfuzz',      'url': '/run/sfuzz', },
        # {'name': 'smartcheck', 'url': '/run/smartcheck', },
        {'name': 'osiris', 'url': '/run/osiris',},
        {'name': 'honeybadger', 'url': '/run/honeybadger',},
        # {'name': 'maian', 'url': '/run/maian',},
    ]
    return jsonify(tools)


@bp.post("/contractsAnalyze/slither")
def analyzeContracts_slither():
    # Upload contracts
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename
        contract_path = os.path.join(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], filename)

        # remove previous the same name of contacts
        try:
            os.remove(contract_path)
        except OSError as e:
            # Handle the error (e.g., log it, notify someone, etc.)
            print(f"Error: None previous contracts")
        # Upload new contracts
        file.save(contract_path)
        # return restful.ok(data={"contract_url": filename})
    else:
        message = form.messages[0]

    # analyze contracts
    client = docker.from_env()
    contract = filename
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/tmpContracts/{contract}"
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

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Define the command
        command = f"slither {contract_path} --json /output.json"

        # Create and run the container
        container = client.containers.create(image_name, command=command, volumes=volumes)
        start_time = time.time()
        container.start()

        # Wait for the container to finish
        result = container.wait()

        # Retrieve the logs
        logs = container.logs().decode('utf-8')

        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)
        # vuln_list = process_slither_data(logs)
        processData = process_log_slither(logs)
        return jsonify(processData), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.post("/contractsAnalyze/evulhunter")
def analyzeContracts_evulhunter():
    # Upload contracts
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename
        contract_path = os.path.join(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], filename)
        # remove previous the same name of contacts
        try:
            os.remove(contract_path)
        except OSError as e:
            # Handle the error (e.g., log it, notify someone, etc.)
            print(f"Error: None previous contracts")
        file.save(contract_path)
        # return restful.ok(data={"contract_url": filename})
    else:
        message = form.messages[0]

    # analyze contracts
    client = docker.from_env()
    contract = filename
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/tmpContracts/{contract}"
        image_name = "weiboot/evulhunter:v0.1"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
            print("pulling " + image_name)

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Create the container without starting it
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python3 EOSVulDetector.py -i \"{contract_path}\"  -t 2 -o \"test.txt\"")
        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        execution_time = end_time - start_time
        container.remove()

        results = process_log_evulhunter(output.decode('utf-8'))

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.post("/contractsAnalyze/wana_rust")
def analyzeContracts_wana_analysis():
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename
        contract_path = os.path.join(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], filename)
        # remove previous the same name of contacts
        try:
            os.remove(contract_path)
        except OSError as e:
            # Handle the error (e.g., log it, notify someone, etc.)
            print(f"None previous contracts")
        file.save(contract_path)
        # return restful.ok(data={"contract_url": filename})
    else:
        message = form.messages[0]

    # analyze contracts
    client = docker.from_env()
    contract = filename
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/tmpContracts/{contract}"
        image_name = "weiboot/wana:v1.0"
        image = None

        # Check if the image exists
        for img in client.images.list():
            if image_name in img.tags:
                image = img
                break

        # If not, pull the image
        if image is None:
            client.images.pull(image_name)
            print("pulling " + image_name)

        # Define the volume mapping
        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}

        # Create the container without starting it
        container = client.containers.create(image_name, volumes=volumes, tty=True)

        # Start the container
        start_time = time.time()
        container.start()

        # Execute the Python command inside the container
        exit_code, output = container.exec_run(f"python3 wana.py -r -e {contract_path}")
        logs = output.decode('utf-8')
        # Optionally, stop and remove the container
        container.stop()
        end_time = time.time()
        execution_time = end_time - start_time
        container.remove()

        # print(logs)
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)

        return jsonify(process_log_rust(logs)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/contractsAnalyze/ccanalyzer", methods=["POST"])
def analyzeContracts_ccanalyzer():
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename
        contract_path = os.path.join(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], filename)
        # remove previous the same name of contacts
        try:
            os.remove(contract_path)
        except OSError as e:
            # Handle the error (e.g., log it, notify someone, etc.)
            print(f"None previous contracts")
        file.save(contract_path)
        # return restful.ok(data={"contract_url": filename})
    else:
        message = form.messages[0]

    command = ["/srv/chaincode/chaincode-analyzer/ccanalyzer", contract_path]

    try:
        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # If the command was successful, return the output
        # return jsonify({"message": "Analysis completed", "output": result.stdout, "error": result.stderr}), 200
        return jsonify(process_log_ccanalyzer(result)), 200
    except subprocess.CalledProcessError as e:
        # If an error occurred while executing the command, return the error
        return jsonify({"msg": "错误结果", "code": "9999", "data": None}), 500

