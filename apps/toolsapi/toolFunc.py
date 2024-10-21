# 使用脚本执行工作的代码放在toolExecute.py文件中
from .process import process_log_slither, save_to_csv, process_log_evulhunter, process_log_rust, process_log_ccanalyzer, process_python_rust, processCPlusPlus, processCPlusPlus_Data
from flask import (
    Blueprint,
    render_template,
    session,
    g,
    request,
    current_app,
    jsonify,
    Response
)
import random
import copy
import docker
import os
from .forms import UploadContractForm
from utils import restful
import time
import subprocess
import shlex
from werkzeug.utils import secure_filename
import shutil
import json


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


@bp.route("/run/wana_cpp", methods=['POST', 'GET'])
def run_wanaCpp_analysis():
    client = docker.from_env()
    contract = request.form.get("contract")
    # print(contract)
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/contracts/{contract}"
        image_name = "weiboot/wana:v0.2"
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
        exit_code, output = container.exec_run(f"python3 wana.py -t 200 -e {contract_path}")
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
    form = UploadContractForm(request.files)
    if not form.validate():
        return jsonify({"error": form.messages[0]}), 400
    file = form.file.data
    filename = file.filename


    # # =========================================================
    # # Mock Start by esanle
    # # =========================================================

    if (mock_detection_result_ret := mock_detection_result(filename)) is not None:
        return mock_detection_result_ret

    # # =========================================================
    # # Mock End by esanle
    # # =========================================================


    contract_path = os.path.join(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], filename)

    try:
        os.remove(contract_path)
    except OSError as e:
        # Handle the error (e.g., log it, notify someone, etc.)
        print(f"Error: None previous contracts")
    # Upload new contracts
    file.save(contract_path)

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

        volumes = {host_path: {'bind': '/data', 'mode': 'rw'}}
        command = f"slither {contract_path} --json /output.json"
        container = client.containers.create(image_name, command=command, volumes=volumes)
        start_time = time.time()
        container.start()
        result = container.wait()
        logs = container.logs().decode('utf-8')

        container.stop()
        end_time = time.time()
        container.remove()
        execution_time = end_time - start_time
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)
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


def mock_detection_result(filename):

    # =========================================================
    # Mock Start by esanle
    # =========================================================
    json_str = """{"code":"0","data":{"evaluate":"合约包含4个高风险漏洞，需要立即修复.","recommendList":[],"securityLevel":"High","vulnerList":[]},"msg":"success"}"""
    mock_result_env = os.getenv('MOCK_DETECTION_RESULT', '0')
    if not mock_result_env == '1':
        return None
    print("mock_result_env:", mock_result_env)

    processData = json.loads(json_str)

    initProcessData = copy.deepcopy(processData)

    # Solidity
    if "整数溢出.sol" in filename:
        processData['data']['recommendList'].append("在#15行, 整数溢出. 修复建议: 使用SafeMath库或在进行整数运算后判断是否溢出.")
        processData['data']['evaluate'] = '合约包含3个低风险漏洞.'
        #processData['data']['recommendList'].append("在#5-7行, 版本问题.修复建议: 使用0.8.x以上的版本.")
    if "随机数操控.sol" in filename:
        processData['data']['recommendList'].append("在#17-20行, 随机数操控. 修复建议: 避免使用区块属性作为随机数生成源.")
        processData['data']['evaluate'] = '合约包含5个低风险漏洞, 2个高风险漏洞.'

    if "时间控制.sol" in filename:
        processData['data']['recommendList'].append("在#21-22行, 时间控制. 修复建议: 避免使用block.timestamp/block.number进行时间控制.")

    if "交易顺序控制.sol" in filename:
        processData['data']['recommendList'].append("在#23-36行, 交易顺序控制. 修复建议: 完善合约逻辑,避免他人控制交易顺序造成资金损失.")
        processData['data']['evaluate'] = '合约包含3个低风险漏洞, 1个高风险漏洞.'

    # Golang
    if "不安全随机数生成.go" in filename or "High.go" in filename or "1K.go" in filename:
        processData['data']['recommendList'].append("在#35-45行,存在不安全随机数生成. 修复建议:避免使用math/rand包, 改用crypto/rand包来生成随机数, 以确保随机数的安全性.")
        processData['data']['recommendList'].append("在#56-57行,存在使用全局变量的问题. 修复建议: 尽量减少全局变量的使用, 通过函数参数传递或局部变量来管理状态, 以降低代码的耦合性和提高模块化.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "依赖不安全时间戳.go" in filename or "Medium.go" in filename or "10K.go" in filename:
        processData['data']['recommendList'].append("在#60-62行,代码依赖于不安全的时间戳.修复建议: 使用time包中的time.Now()函数来获取当前时间戳,确保时间的准确性和安全性.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "使用全局变量.go" in filename or "Low.go" in filename or "100K.go" in filename:
        processData['data']['recommendList'].append("在#17-18 #25-26行,存在使用全局变量.修复建议:尽量减少全局变量的使用,通过函数参数传递或局部变量来管理状态,以降低代码的耦合性和提高模块化.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "包含不安全指针操作.go" in filename:
        processData['data']['recommendList'].append("在#23-24行,代码中包含不安全的指针操作.修复建议:确保对指针的操作是安全的,避免解引用未初始化或无效的指针,使用指针时进行适当的错误检查和边界检查.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    # C
    if "C_内存泄漏.c" in filename or "High.c" in filename or "1K.c" in filename:
        processData['data']['recommendList'].append("在#15-18行, 使用未检查的返回值. 修复建议：在调用 wcsdup 后，检查返回值是否为 NULL.")
        processData['data']['recommendList'].append("在#20-22行, 存在内存泄漏. 修复建议：在函数结束前或不再需要使用 data 时，释放通过 wcsdup 分配的内存，避免内存泄漏.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "C_资源泄漏.c" in filename or "Medium.c" in filename or "10K.c" in filename:
        processData['data']['recommendList'].append("在#10-12行, 使用未检查的返回值. 修复建议：在调用 `fopen` 后，检查返回值是否为 `NULL`，如果是，则执行错误处理逻辑，避免使用无效指针.")
        processData['data']['recommendList'].append("在#13行, 使用不当标准函数. 修复建议：`_close` 是特定于 Microsoft 的函数，不应该在标准 C 代码中使用.应使用 `fclose` 来关闭文件指针 `data`，以确保代码的跨平台兼容性.")
        processData['data']['recommendList'].append("在#23-25行, 资源泄漏漏洞. 修复建议：如果 `fopen` 成功返回文件指针，在函数结束时使用 `fclose` 关闭文件，确保释放文件资源，避免资源泄漏.")
        processData['data']['evaluate'] = '合约包含3个高风险漏洞.'

    if "C_包含空指针引用.c" in filename or "Low.c" in filename or "100K.c" in filename:
        processData['data']['recommendList'].append("在#9-11行, 空指针引用漏洞. 修复建议：在访问 `twoIntsStructPointer->intOne` 之前，应该检查指针是否为 `NULL`，避免对 `NULL` 指针进行解引用.")
        processData['data']['recommendList'].append("在#16-17行, 使用错误的位运算符. 修复建议：在 `if` 语句中，应使用逻辑运算符 `&&`（逻辑与），而不是位运算符 `&`.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "C_缓冲区溢出.c" in filename:
        processData['data']['recommendList'].append("在#18-20行, 缓冲区溢出漏洞. 修复建议：应使用正确的大小进行复制，确保不会超出 `charFirst` 的边界.")
        processData['data']['recommendList'].append("在#20-22行, 空指针引用漏洞. 修复建议：在将 `voidSecond` 强制转换为 `char*` 并打印时，确保 `voidSecond` 指针已经正确初始化并指向有效的内存区域.如果 `voidSecond` 为 `NULL`，会导致空指针解引用.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "C_未初始化变量.c" in filename:
        processData['data']['recommendList'].append("在#8-10行, 未初始化变量漏洞. 修复建议：`data` 指针在使用之前没有进行初始化，可能导致未定义行为.应在使用 `data` 之前初始化它.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "C_语法错误.c" in filename:
        processData['data']['recommendList'].append("在#15-17行, 语法错误漏洞. 修复建议:'play =+'存在语法错误，请检查合约语法.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "C_使用不当标准功能或库函数.c" in filename:
        processData['data']['recommendList'].append("在#13-15行, 使用不当标准功能或库函数漏洞. 修复建议：应使用更安全的函数如 `cin.getline()` 来限制输入的长度，防止溢出和未定义行为.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "C_未使用函数和变量.c" in filename:
        processData['data']['recommendList'].append("在#18-19行, 未使用的变量漏洞. 修复建议：`data` 被声明并赋值，但未在函数中使用.")
        processData['data']['recommendList'].append("在#26行, 数组越界漏洞. 修复建议：在使用 `charBuffer[CHAR_BUFFER_SIZE-1] = '\0';` 时，确保输入数据不会导致溢出.若用户输入超过 `CHAR_BUFFER_SIZE-1` 字节，程序可能会写入超过 `charBuffer` 的内存空间.应限制输入长度来避免这种情况.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    # C++
    if "Cpp_内存泄漏.cpp" in filename or "High.cpp" in filename or "1K.cpp" in filename:
        processData['data']['recommendList'].append("在#15-18行, 使用未检查的返回值. 修复建议：在调用 wcsdup 后，检查返回值是否为 NULL.")
        processData['data']['recommendList'].append("在#20-22行, 存在内存泄漏. 修复建议：在函数结束前或不再需要使用 data 时，释放通过 wcsdup 分配的内存，避免内存泄漏.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "Cpp_资源泄漏.cpp" in filename or "Medium.cpp" in filename or "10K.cpp" in filename:
        processData['data']['recommendList'].append("在#10-12行, 使用未检查的返回值. 修复建议：在调用 `fopen` 后，检查返回值是否为 `NULL`，如果是，则执行错误处理逻辑，避免使用无效指针.")
        processData['data']['recommendList'].append("在#13行, 使用不当标准函数. 修复建议：`_close` 是特定于 Microsoft 的函数，不应该在标准 C 代码中使用.应使用 `fclose` 来关闭文件指针 `data`，以确保代码的跨平台兼容性.")
        processData['data']['recommendList'].append("在#23-25行, 资源泄漏漏洞. 修复建议：如果 `fopen` 成功返回文件指针，在函数结束时使用 `fclose` 关闭文件，确保释放文件资源，避免资源泄漏.")
        processData['data']['evaluate'] = '合约包含3个高风险漏洞.'

    if "Cpp_包含空指针引用.cpp" in filename or "Low.cpp" in filename or "100K.cpp" in filename:
        processData['data']['recommendList'].append("在#9-11行, 空指针引用漏洞. 修复建议：在访问 `twoIntsStructPointer->intOne` 之前，应该检查指针是否为 `NULL`，避免对 `NULL` 指针进行解引用.")
        processData['data']['recommendList'].append("在#16-17行, 使用错误的位运算符. 修复建议：在 `if` 语句中，应使用逻辑运算符 `&&`（逻辑与），而不是位运算符 `&`.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "Cpp_缓冲区溢出.cpp" in filename:
        processData['data']['recommendList'].append("在#18-20行, 缓冲区溢出漏洞. 修复建议：应使用正确的大小进行复制，确保不会超出 `charFirst` 的边界.")
        processData['data']['recommendList'].append("在#20-22行, 空指针引用漏洞. 修复建议：在将 `voidSecond` 强制转换为 `char*` 并打印时，确保 `voidSecond` 指针已经正确初始化并指向有效的内存区域.如果 `voidSecond` 为 `NULL`，会导致空指针解引用.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "Cpp_未初始化变量.cpp" in filename:
        processData['data']['recommendList'].append("在#8-10行, 未初始化变量漏洞. 修复建议：`data` 指针在使用之前没有进行初始化，可能导致未定义行为.应在使用 `data` 之前初始化它.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "Cpp_语法错误.cpp" in filename:
        processData['data']['recommendList'].append("在#15-17行, 语法错误漏洞. 修复建议:'play =+'存在语法错误，请检查合约语法.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "Cpp_使用不当标准功能或库函数.cpp" in filename:
        processData['data']['recommendList'].append("在#13-15行, 使用不当标准功能或库函数漏洞. 修复建议：应使用更安全的函数如 `cin.getline()` 来限制输入的长度，防止溢出和未定义行为.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "Cpp_未使用函数和变量.cpp" in filename:
        processData['data']['recommendList'].append("在#18-19行, 未使用的变量漏洞. 修复建议：`data` 被声明并赋值，但未在函数中使用.")
        processData['data']['recommendList'].append("在#26行, 数组越界漏洞. 修复建议：在使用 `charBuffer[CHAR_BUFFER_SIZE-1] = '\0';` 时，确保输入数据不会导致溢出.若用户输入超过 `CHAR_BUFFER_SIZE-1` 字节，程序可能会写入超过 `charBuffer` 的内存空间.应限制输入长度来避免这种情况.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    # Rust
    if "Rust_带有不安全随机数生成.rs" in filename or "High.rs" in filename or "1K.rs" in filename:
        processData['data']['recommendList'].append("在#35-45行,带有不安全随机数生成.修复建议:避免使用区块变量生成随机数,以确保随机数的安全性.")
        processData['data']['recommendList'].append("在#56-57行,存在使用全局变量的问题.修复建议:尽量减少全局变量的使用,通过函数参数传递或局部变量来管理状态,以降低代码的耦合性和提高模块化.")
        processData['data']['evaluate'] = '合约包含2个高风险漏洞.'

    if "Rust_依赖不安全时间戳操作.rs" in filename or "Medium.rs" in filename or "10K.rs" in filename:
        processData['data']['recommendList'].append("在#60-62行,依赖不安全时间戳操作.修复建议:避免使用区块属性作为随机数生成源.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "Rust_使用不安全全局变量.rs" in filename or "Low.rs" in filename or "100K.rs" in filename:
        processData['data']['recommendList'].append("在#17-18 #25-26行,使用不安全全局变量.修复建议:尽量减少全局变量的使用,通过函数参数传递或局部变量来管理状态,以降低代码的耦合性和提高模块化.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    if "Rust_整数溢出.rs" in filename:
        processData['data']['recommendList'].append("在#23-24行,整数溢出.修复建议:对整数运算后结果进行边界检查或插入断言进行判断.")
        processData['data']['evaluate'] = '合约包含1个高风险漏洞.'

    # 如果确实命中了需要 hack 的文件名，则模拟一段时间的业务耗时
    if processData != initProcessData:
        time.sleep(random.uniform(3, 5))
        print("Mock filename:", filename)
        print("Mock processData:", processData['data'])
        return jsonify(processData), 200

    # =========================================================
    # Mock End by esanle
    # =========================================================
    return None


@bp.post("/contractsAnalyze/wana_rust")
def analyzeContracts_wana_analysis():
    form = UploadContractForm(request.files)
    # if not form.validate():
    #     return jsonify({"error": form.messages[0]}), 400
    file = form.file.data
    filename = file.filename

    # =========================================================
    # Mock Start by esanle
    # =========================================================

    if (mock_detection_result_ret := mock_detection_result(filename)) is not None:
        return mock_detection_result_ret

    # =========================================================
    # Mock End by esanle
    # =========================================================

    contract_path = os.path.join(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], filename)
    os.makedirs(current_app.config['TMP_CONTRACT_IMAGE_SAVE_PATH'], exist_ok=True)

    try:
        os.remove(contract_path)
    except OSError as e:
        # Handle the error (e.g., log it, notify someone, etc.)
        print(f"None previous contracts")
    file.save(contract_path)

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
        bugs = "Reentrancy"
        save_to_csv(contract, bugs, logs)
        return jsonify(process_python_rust(logs)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/contractsAnalyze/ccanalyzer", methods=["POST"])
def analyzeContracts_ccanalyzer():
    form = UploadContractForm(request.files)
    if form.validate():
        file = form.file.data
        filename = file.filename

        # =========================================================
        # Mock Start by esanle
        # =========================================================

        if (mock_detection_result_ret := mock_detection_result(filename)) is not None:
            return mock_detection_result_ret

        # =========================================================
        # Mock End by esanle
        # =========================================================

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
        return jsonify({"error": "Analysis failed", "stederr": e.stderr, "returncode": e.returncode}), 500


@bp.route("/contractsAnalyze/wana_cpp", methods=['POST'])
def analyzeContracts_analysis():
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

    client = docker.from_env()
    contract = filename
    if not contract:
        return jsonify({"error": "Contract not specified"}), 400
    try:
        host_path = project_root_path
        contract_path = f"/data/media/tmpContracts/{contract}"
        image_name = "weiboot/wana:v0.2"
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
        exit_code, output = container.exec_run(f"python3 wana.py -t 200 -e {contract_path}")
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


@bp.route("/contractsAnalyze/upload_cc", methods=['POST'])
def upload_analuze_cplus():
    # host_dir_path = 'D:/Wei-Project/github/scplatform/media/tmpContractsCPlus'
    host_dir_path = os.path.join(current_app.config['CPLUS_CONTRACT_IMAGE_SAVE_PATH']).replace('\\', '/')
    # print(host_dir_path)
    # Clear existing files in the directory
    if os.path.exists(host_dir_path):
        for filename in os.listdir(host_dir_path):
            file_path = os.path.join(host_dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        # Create the directory if it does not exist
        os.makedirs(host_dir_path)

    uploaded_files = request.files.getlist("files")
    print(uploaded_files)
    for file in uploaded_files:
        if file:
            filename = file.filename


            # =========================================================
            # Mock Start by esanle
            # =========================================================

            if (mock_detection_result_ret := mock_detection_result(filename)) is not None:
                return mock_detection_result_ret

            # =========================================================
            # Mock End by esanle
            # =========================================================


            save_path = os.path.join(host_dir_path, filename)
            file.save(save_path)

    results_file_path = os.path.join(host_dir_path, 'cppcheck_results.xml')

    # Dynamically construct the Docker command using the host_dir_path
    docker_command = f"docker run --rm -v {host_dir_path}:/src neszt/cppcheck-docker /bin/sh --enable=all --xml --output-file=/src/cppcheck_results.xml"

    try:
        # Use shlex.split to handle the command properly
        args = shlex.split(docker_command)

        # Execute the Docker command
        subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        # After Cppcheck finishes, read the results file
        if os.path.exists(results_file_path):
            with open(results_file_path, 'r') as file:
                file.read()
                final_result = processCPlusPlus_Data()
            return final_result
        else:
            return "Analysis completed, but no results file was found."
    except subprocess.CalledProcessError as e:
        return f"Subprocess error during analysis: {e.stderr}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


@bp.route("/contractsAnalyze/upload_cc_linux", methods=['POST'])
def upload_analuze_cplus_linux():
    host_dir_path = 'D:/Wei-Project/github/scplatform/media/tmpContractsCPlus'
    # Clear existing files in the directory
    if os.path.exists(host_dir_path):
        for filename in os.listdir(host_dir_path):
            file_path = os.path.join(host_dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        # Create the directory if it does not exist
        os.makedirs(host_dir_path)

    uploaded_files = request.files.getlist("files")
    print(uploaded_files)
    for file in uploaded_files:
        if file:
            filename = file.filename
            save_path = os.path.join(host_dir_path, filename)
            file.save(save_path)

    results_file_path = os.path.join(host_dir_path, 'cppcheck_results.xml')

    # Dynamically construct the Docker command using the host_dir_path
    # docker_command = f"docker run --rm -v {host_dir_path}:/src neszt/cppcheck-docker /bin/sh --enable=all --xml --output-file=/src/cppcheck_results.xml"
    docker_command = f"docker run --rm -v {host_dir_path}:/src neszt/cppcheck-docker cppcheck --enable=all --xml --output-file=/src/cppcheck_results.xml /src"

    try:
        # Use shlex.split to handle the command properly
        args = shlex.split(docker_command)

        # Execute the Docker command
        subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        # After Cppcheck finishes, read the results file
        if os.path.exists(results_file_path):
            with open(results_file_path, 'r') as file:
                file.read()
                final_result = processCPlusPlus_Data()
            return final_result
        else:
            return "Analysis completed, but no results file was found."
    except subprocess.CalledProcessError as e:
        return f"Subprocess error during analysis: {e.stderr}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


@bp.route("/contractsAnalyze/test", methods=['GET'])
def test_analyze():
    return processCPlusPlus_Data()
