import re

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


def process_log(log_content):
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
