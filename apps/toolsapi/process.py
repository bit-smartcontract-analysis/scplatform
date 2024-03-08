import re
import os
from datetime import datetime
import csv

project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def process_slither_data(log_data):
    detector_blocks = log_data.split('INFO:Detectors:')[1:]

    file_path_pattern = r"/data/media/tmpContracts/[\w\.]+"

    # Clean and extract information from each block
    extracted_info = []
    for block in detector_blocks:
        # Remove ANSI escape sequences for colors
        clean_block = re.sub(r'\x1b\[\d+m', '', block).strip()
        # Remove backslashes for new lines and tabs, replace with actual new lines and tabs
        clean_block = clean_block.replace('\\n', '\n').replace('\\t', '\t')
        clean_block = re.sub(file_path_pattern, '', clean_block)
        extracted_info.append(clean_block)

    return extracted_info


def process_log_slither(log_content):
    # Initialize the result structure for success case
    result = {
        "msg": "success",
        "code": "0",
        "data": {
            "vulnerList": [],
            "securityLevel": "",
            "evaluate": ""
        }
    }

    # Check for error in log content
    if "ERROR:root:" in log_content:
        # Error output format
        return {
            "msg": "错误结果",
            "code": "9999",
            "data": None
        }

    vulnerability_patterns = {
        'High': re.compile(r'\x1b\[91m(.*?)Reference:', re.DOTALL),
        'Medium': re.compile(r'\x1b\[93m(.*?)Reference:', re.DOTALL),
        'Low': re.compile(r'\x1b\[92m(.*?)Reference:', re.DOTALL)
    }

    pattern_remove = r"/data/media/tmpContracts/[^)]+\.sol"

    # Identify vulnerabilities and classify by severity
    for level, pattern in vulnerability_patterns.items():
        matches = pattern.findall(log_content)
        if matches:
            for match in matches:
                # Cleaning and formatting the extracted information
                clean_match = " ".join(match.replace('\n', ' ').split())
                result['data']['vulnerList'].append(clean_match)
                vulnerList = result['data']['vulnerList']
                cleaned_vulnerList = [re.sub(pattern_remove, "", item) for item in vulnerList]
                result['data']['vulnerList'] = cleaned_vulnerList

            # Set security level based on the highest severity found
            if not result['data']['securityLevel'] or (
                    level == 'High' or (level == 'Medium' and result['data']['securityLevel'] != 'High')):
                result['data']['securityLevel'] = level

    # Determine evaluation based on security level
    security_level = result['data']['securityLevel']
    vulner_count = len(result['data']['vulnerList'])
    if security_level == "High":
        result['data']['evaluate'] = f"Contract contains {vulner_count} high severity vulnerabilities. Immediate action required."
    elif security_level == "Medium":
        result['data']['evaluate'] = f"Contract contains {vulner_count} medium severity issues. Review recommended."
    elif security_level == "Low":
        result['data']['evaluate'] = f"Contract contains {vulner_count} low severity issues. Minimal risk."
    else:
        result['data']['securityLevel'] = "None"
        result['data']['evaluate'] = "No vulnerabilities found. Contract is safe."

    return result


def save_to_csv(contract_name, bugs_name, logs):
    save_dir = os.path.join(project_root_path, "media/logs")
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    timestamp_log = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field_names = ["contract_name", "bugs_name", "timestamp", "logs"]
    save_path = os.path.join(save_dir, f"{timestamp}.csv")
    data = [contract_name, bugs_name, timestamp_log, logs]

    with open(save_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(field_names)
        writer.writerow(data)


def process_log_evulhunter(log):
    # Updated security levels mapping with appropriate vulnerability descriptions
    security_levels = {
        "fake EOS transfer": "High",
        "fake transfer notice": "Medium",
    }

    # Initialize default values
    vulnerList = []
    securityLevel = "None"
    evaluate = ""

    # Check for the presence of an error in the log
    if "Traceback (most recent call last):" in log or "KeyError" in log:
        return {
            "msg": "错误结果",
            "code": "9999",
            "data": None
        }

    # Check if log contains "result"
    if "######result########" in log:
        result_sections = log.split("######result########")
        if len(result_sections) > 2:  # Ensuring there's a result section before the last marker
            result_section = result_sections[-2]

            # Special handling for "No Vul2."
            if "No Vul2." in result_section:
                evaluate = "No vulnerabilities found."
            else:
                for line in result_section.split('\n'):
                    if "Vul" in line:
                        # Extracting the vulnerability description
                        vulner_name = line.split("!")[1].strip() if "!" in line else line.strip()
                        # Check against known vulnerabilities
                        if vulner_name.lower() in security_levels:
                            vulnerList.append(vulner_name)
                            securityLevel = security_levels[vulner_name.lower()]

                if securityLevel == "High":
                    evaluate = "Contract contains high severity vulnerabilities. Immediate action required."
                elif securityLevel == "Medium":
                    evaluate = "Contract contains medium severity issues. Review recommended."
                elif securityLevel == "Low":
                    evaluate = "Contract contains low severity issues. Minimal risk."
                else:
                    evaluate = "No vulnerabilities found."
        else:
            evaluate = "No vulnerabilities found."
    else:
        evaluate = "No vulnerabilities found."

    # Construct the output dictionary
    output = {
        "msg": "success",
        "code": "0",
        "logs": log,
        "data": {
            "vulnerList": vulnerList,
            "securityLevel": securityLevel,
            "evaluate": evaluate
        }
    }

    return output
