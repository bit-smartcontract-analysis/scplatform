import re
import os
from datetime import datetime
import csv
from typing import Dict, Any
import xml.etree.ElementTree as ET
from flask import current_app

project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


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
            "evaluate": "",
            "recommendList": []
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
        result['data']['evaluate'] = f"合约包含{vulner_count} 个高风险漏洞，需要立即修复."
    elif security_level == "Medium":
        result['data']['evaluate'] = f"合约包含{vulner_count} 个中风险漏洞，需要重新审阅代码."
    elif security_level == "Low":
        result['data']['evaluate'] = f"合约{vulner_count}个低风险漏洞."
    else:
        result['data']['securityLevel'] = "None"
        result['data']['evaluate'] = "没有风险的合约."

    result['data']['recommendList'] = analysisData(result['data']['vulnerList'])

    return result


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


def process_log_rust(log):

    file_name_match = re.search(r"Smart Contract = (\w+)", log)
    if file_name_match:
        file_name = file_name_match.group(1)
    else:
        return {
            "msg": "错误结果",
            "code": "9999",
            "data": None
        }

    # Initialize the output structure
    output = {
        "msg": "success",
        "code": "0",
        "data": {
            "vulnerList": "",
            "securityLevel": "None",  # Default to None unless vulnerabilities are found
            "evaluate": ""
        },
        "logs": log
    }

    # Compile a regex pattern to find vulnerabilities associated with the file
    vulner_pattern = re.compile(rf"{file_name}: (\w+ vulnerability found)")
    vulner_matches = vulner_pattern.findall(log)

    if vulner_matches:
        # Join the found vulnerabilities and remove the timestamp
        vulner_list = [re.sub(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} ', '', match) for match in vulner_matches]
        output["data"]["vulnerList"] = ", ".join(vulner_list)
        output["data"]["securityLevel"] = "Low"  # Assuming "Low" if any vulnerabilities are found

    securityLevel = output["data"]["securityLevel"]
    if securityLevel == "High":
        evaluate = "合约包含高级安全漏洞，请立即修复"
    elif securityLevel == "Medium":
        evaluate = "合约包含中级安全漏洞"
    elif securityLevel == "Low":
        evaluate = "合约包含低级安全漏洞"
    else:
        evaluate = "无漏洞发现"

    output["data"]["evaluate"] = evaluate

    return output


def process_python_rust(log: str) -> Dict[str, Any]:
    # Print the log for debugging
    print(log)

    # Attempt to extract the file name of the smart contract
    file_name_match = re.search(r"Smart Contract = (\w+)", log)
    if not file_name_match:
        return {"msg": "错误结果", "code": "9999", "data": None}

    file_name = file_name_match.group(1)

    # Prepare the output structure
    output = {
        "msg": "success",
        "code": "0",
        "data": {
            "vulnerList": [],
            "recommendList": [],
            "securityLevel": "None",  # Default security level
            "evaluate": ""
        },
        "logs": log
    }

    # Define the mapping from vulnerability keywords to their translations
    vulner_translation = {
        "overflow vulnerability found": "整数溢出. 修复建议：请为您的合约使用高版本,或使用SafeMath库进行算术运算.",
        "reentrancy vulnerability found": "重入",
        "unchecked return value vulnerability found": "未检出返回值"
    }

    # Compile a regex pattern to find vulnerabilities
    vulner_pattern = re.compile(rf"{file_name}: (\w+ vulnerability found)")
    for match in re.finditer(vulner_pattern, log):
        vulner_key = match.group(1)
        # Translate and add to the list
        if vulner_key in vulner_translation:
            output["data"]["vulnerList"].append(vulner_key)
            output["data"]["recommendList"].append(vulner_translation[vulner_key])

    # Set security level based on found vulnerabilities
    if output["data"]["vulnerList"]:
        output["data"]["securityLevel"] = "Low"  # This can be adjusted based on actual vulnerability severity

    # Provide an evaluation based on security level
    security_level_mapping = {
        "High": "合约包含高级安全漏洞，请立即修复",
        "Medium": "合约包含中级安全漏洞",
        "Low": "合约包含低级安全漏洞",
        "None": "无漏洞发现"
    }
    output["data"]["evaluate"] = security_level_mapping[output["data"]["securityLevel"]]

    return output


def process_log_ccanalyzer(raw_output):
    if not hasattr(raw_output, 'stdout') or not hasattr(raw_output, 'stderr'):
        raise ValueError("processResult must have 'stdout' and 'stderr' attributes")

    # Check if stderr is not empty and return an error message
    if raw_output.stderr.strip():
        return {"msg": "错误结果", "code": "9999", "data": None}

    # Regular expression to find vulnerabilities
    vuln_pattern = re.compile(
        r"## Category\s+(.*?)\n## Function\s+(.*?)\n.*?## Position\s+(.*?)\n",
        re.DOTALL
    )

    # Extract vulnerabilities
    vulnerabilities = vuln_pattern.findall(raw_output.stdout)

    # Process extracted vulnerabilities to format them into readable strings
    vulnerList = []
    recommendList = []
    for category, function, position in vulnerabilities:
        position_clean = position.strip()
        vulnerList.append(f"{category} 在 `{function}`中: {position_clean}")
        if category == "External Library":
            recommendation = "检查外部库的安全性"
        elif category == "Global Variable":
            recommendation = "验证全局变量的使用是否安全"
        elif category == "MapIter":
            recommendation = "优化映射迭代器的使用以防止性能问题"
        else:
            recommendation = "进行进一步的检查"

        recommendList.append(f"位置: {position_clean}, {category}. 修复建议：{recommendation}")

    # # Initialize security level flags
    has_external_library = any("External Library" in v for v in vulnerList)
    has_global_variable = any("Global Variable" in v for v in vulnerList)
    has_map_iterations = any("MapIter" in v for v in vulnerList)
    #
    # # Assign a security level based on extracted vulnerabilities
    if has_map_iterations:
        securityLevel = "Medium"
    elif has_external_library or has_global_variable:
        securityLevel = "Low"
    else:
        securityLevel = "None"

    # General evaluation
    evaluate = f"需要修复{len(vulnerList)}个漏洞,请参考https://goethereumbook.org/smart-contract-deploy/"

    # Construct the JSON structure
    result = {
        "msg": "success",
        "code": "0",
        "data": {
            "vulnerList": vulnerList,
            "recommendList": recommendList,
            "securityLevel": securityLevel,
            "evaluate": evaluate
        }
    }

    return result


def analysisData(vulnerList):

    vulnerability_map = {
        "Reentrancy": "重入漏洞. 修复建议: 使用Checks-Effects-Interactions模式.Check:：首先,验证所有条件和要求; Effects: 在调用外部合约之前更新合约的状态; Interactions:最后与其他合约交互（例如发送以太币）.",
        "Low level call": "低级别调用(call). 修复建议: 避免调用低阶函数(call, delegatecall, callcode), 或是验证返回函数.",
        "be declared external": "被外部接口调用. 修复建议: 尽可能限制外部调用的使用.",
        "Detected issues with version pragma": "版本问题. 修复建议: 使用0.8.x以上的版本.",
        "external calls inside a loop": "循环内的外部调用. 修复建议: 尽可能限制外部调用的使用，尤其是在循环内.",
        "tx.origin for authorization": "tx.origin授权. 修复建议: 始终使用 msg.sender 而不是 tx.origin 进行身份验证和授权. msg.sender准确地代表当前调用的直接发起者, 确保只有直接与您的合约交互的实体才能通过身份验证.",
        "Usage of \"sha3()\" should be replaced with \"keccak256()\"": "错误的使用废弃函数sha3(). 修复建议: 使用keccak256()代替sha3().",
        "Usage of \"throw\" should be replaced with \"revert()\"": "错误的使用废弃函数throw(). 修复建议: 使用revert()代替throw()",
        "Usage of \"suicide()\" should be replaced with \"selfdestruct()\"": "错误的使用废弃函数suicide(). 修复建议: 使用selfdestruct()代替suicide()",
        "Contract locking ether found": "合约中以太币被锁. 修复建议: 确保您的合约包含允许提取合约中存储的以太币的功能。这可以是只能由授权地址调用的专用提款功能，也可以是用于去中心化提款的更开放的拉式支付系统.",
        "uses delegatecall": "代理问题. 修复建议: 在使用 delegatecall 之前，请充分理解其含义。它在您的合约存储上下文中执行另一个合约的代码，这意味着被调用的合约可以更改您的合约的状态.",
        "sends eth to arbitrary user Dangerous calls": "发送以太币给任意用户. 修复建议: 在发送 ETH 之前, 请确保收件人地址有效且符合预期.这可能涉及检查该地址是否不是零地址 (0x0),并根据上下文确保它属于允许的地址列表.",
        "allows anyone to destruct the contract": "允许任何人摧毁合约. 修复建议: 将调用自毁功能的能力限制为选定的一组地址，通常仅限于合约所有者或一组受信任的管理员。这可以通过修改器来实现，修改器根据授权地址列表检查调用者的地址.",
        "incorrect ERC20 function interface(s)": "不正确的ERC20功能接口. 修复建议: 确保您的合约实现了ERC20标准中指定的所有强制功能和事件.这包括totalSupply、balanceOf、transfer、transferFrom、approve和allowance函数,以及Transfer和Approval事件.",
        "a dangerous strict equality": "危险的等号. 修复建议: 不使用==符号.",
        "is not in mixedCase": "大小写混合. 修复建议: 重新检查代码,尤其大小写",
        "a local variable never initialiazed": "从未初始化的局部变量. 修复建议: 声明局部变量时,始终显式初始化它们.这种做法可确保您的变量在使用之前具有已知的状态."
    }

    adjusted_mapped_results = []

    # Perform the iteration and mapping process again, now including line numbers
    for item in vulnerList:
        for key, value in vulnerability_map.items():
            if key in item:
                # Extract the line numbers using a regular expression
                line_numbers = re.findall(r'#\d+-\d+', item)
                line_numbers_str = " ".join(line_numbers)  # Join all found line numbers with a space
                # Append the vulnerability translation along with line numbers to the results list
                if line_numbers_str:  # Only append if line numbers were found
                    adjusted_mapped_results.append(f"在{line_numbers_str}行, {value} ")
                else:
                    adjusted_mapped_results.append(value)

    return adjusted_mapped_results



def recommendData():
    # Redefine the vulnerList with the given vulnerabilities
    vulnerList = [
        "Reentrancy in Reentrance.withdraw (#21-31): External calls: - msg.sender.call.value(_amount)() (#24-27) State variables written after the call(s): - balances (#27-31)",
        "Reentrance.donate (#13-17) should be declared external Reentrance.balanceOf (#17-21) should be declared external Reentrance.withdraw (#21-31) should be declared external Reentrance.fallback (#32) should be declared external",
        "Detected issues with version pragma in #7-9): it allows old versions",
        "Low level call in Reentrance.withdraw (#21-31): -msg.sender.call.value(_amount)() #24-27",
        "Parameter '_to' of Reentrance.donate (#13) is not in mixedCase Parameter '_who' of Reentrance.balanceOf (#17) is not in mixedCase Parameter '_amount' of Reentrance.withdraw (#21-22) is not in mixedCase"
    ]

    # Define an additional mapping for recommendations based on the identified vulnerabilities
    recommendation_map = {
        "Reentrancy": "使用Checks-Effects-Interactions模式.Check:：首先,验证所有条件和要求; Effects: 在调用外部合约之前更新合约的状态; Interactions:最后与其他合约交互（例如发送以太币）.",
        "Low level call": "低级别调用(call)",
        "be declared external": "避免调用低阶函数(call, delegatecall, callcode). 或是验证返回函数",
        "Detected issues with version pragma": "使用0.8.x以上的版本",
        "external calls inside a loop": "尽可能限制外部调用的使用，尤其是在循环内",
        "tx.origin for authorization": "始终使用 msg.sender 而不是 tx.origin 进行身份验证和授权. msg.sender准确地代表当前调用的直接发起者, 确保只有直接与您的合约交互的实体才能通过身份验证.",
        "Usage of \"sha3()\" should be replaced with \"keccak256()\"": "使用keccak256()代替sha3()",
        "Usage of \"throw\" should be replaced with \"revert()\"": "使用revert()代替throw()",
        "Usage of \"suicide()\" should be replaced with \"selfdestruct()\"": "使用selfdestruct()代替suicide()",
        "Contract locking ether found": "确保您的合约包含允许提取合约中存储的以太币的功能。这可以是只能由授权地址调用的专用提款功能，也可以是用于去中心化提款的更开放的拉式支付系统",
        "uses delegatecall": "在使用 delegatecall 之前，请充分理解其含义。它在您的合约存储上下文中执行另一个合约的代码，这意味着被调用的合约可以更改您的合约的状态。",
        "sends eth to arbitrary user Dangerous calls": "在发送 ETH 之前，请确保收件人地址有效且符合预期。这可能涉及检查该地址是否不是零地址 (0x0)，并根据上下文确保它属于允许的地址列表。",
        "allows anyone to destruct the contract": "将调用自毁功能的能力限制为选定的一组地址，通常仅限于合约所有者或一组受信任的管理员。这可以通过修改器来实现，修改器根据授权地址列表检查调用者的地址",
        "incorrect ERC20 function interface(s)": "确保您的合约实现了 ERC20 标准中指定的所有强制功能和事件。这包括totalSupply、balanceOf、transfer、transferFrom、approve和allowance函数，以及Transfer和Approval事件。",
        "a dangerous strict equality": "不使用==符号",
        "is not in mixedCase": "重新检查代码",
        "a local variable never initialiazed": "初始化局部变量"
    }

    # Initialize a list to hold the recommendation results
    recommendList = []

    # Iterate through vulnerList to apply the recommendations based on the identified issues
    for item in vulnerList:
        for key, value in recommendation_map.items():
            if key in item:
                recommendList.append(value)

    return recommendList


def processCPlusPlus():
    tree = ET.parse('D:/Wei-Project/github/scplatform/media/tmpContractsCPlus/cppcheck_results.xml')
    root = tree.getroot()

    # Filter for errors with severity "error" or "style"
    filtered_errors = []
    for error in root.findall('.//error'):
        if error.get('severity') in ['error', 'style']:
            error_details = {
                'id': error.get('id'),
                'severity': error.get('severity'),
                'message': error.get('msg'),
                'locations': [
                    {'file': loc.get('file'), 'line': loc.get('line'), 'column': loc.get('column')}
                    for loc in error.findall('.//location')
                ]
            }
            filtered_errors.append(error_details)

    return filtered_errors


# error_list = [
#     {
#         "id": "knownConditionTrueFalse",
#         "locations": [
#             {
#                 "column": "16",
#                 "file": "/src/basic_iterator.cc",
#                 "line": "83"
#             },
#             {
#                 "column": "13",
#                 "file": "/src/basic_iterator.cc",
#                 "line": "63"
#             }
#         ],
#         "message": "Return value '!ret' is always true",
#         "severity": "style"
#     },
#     {
#         "id": "syntaxError",
#         "locations": [
#             {
#                 "column": "25",
#                 "file": "/bin/sh",
#                 "line": "1"
#             }
#         ],
#         "message": "The code contains unhandled character(s) (character code=209). Neither unicode nor extended ascii is supported.",
#         "severity": "error"
#     }
# ]


def analysisCPlusPlusData(error_list):
    response = {
        "msg": "success",
        "code": "0",
        "data": {
            "vulnerList": [],  # This will be filled with the details of filtered_errors
            "securityLevel": "None",  # To be determined
            "evaluate": "Assessment of vulnerabilities based on cppcheck results."
        }
    }

    # Assuming filtered_errors contains the list of filtered errors
    for error in error_list:
        # Adjusting severity for display in the vulnerList
        display_severity = "Low" if error['severity'] == 'style' else "High" if error[
                                                                                    'severity'] == 'error' else "Unknown"
        locations_str = "; ".join(
            [f"File: {loc['file']}, Line: {loc['line']}, Column: {loc['column']}" for loc in error['locations']])

        vulnerability = {
            "ID": error['id'],
            "Severity": display_severity,  # Adjusting based on your requirement
            "Message": error['message'],
            "Locations": locations_str
        }
        response["data"]["vulnerList"].append(vulnerability)

    # Determining the overall security level based on the highest severity found
    severities = [error['severity'] for error in error_list]
    if "error" in severities:
        response["data"]["securityLevel"] = "High"
    elif "style" in severities:
        response["data"]["securityLevel"] = "Low"
    else:
        response["data"]["securityLevel"] = "None"

    # Now, the response object is ready and adjusted to your specifications
    return response


def processCPlusPlus_Data():
    host_dir_path = os.path.join(current_app.config['CPLUS_CONTRACT_IMAGE_SAVE_PATH']).replace('\\', '/')
    tree = ET.parse(f'{host_dir_path}/cppcheck_results.xml')
    root = tree.getroot()

    # Filter for errors with severity "error" or "style"
    filtered_errors = []
    for error in root.findall('.//error'):
        if error.get('severity') in ['error', 'style']:
            error_details = {
                'id': error.get('id'),
                'severity': error.get('severity'),
                'message': error.get('msg'),
                'locations': [
                    {'file': loc.get('file'), 'line': loc.get('line'), 'column': loc.get('column')}
                    for loc in error.findall('.//location')
                ]
            }
            filtered_errors.append(error_details)

    results = analysisCPlusPlusData(filtered_errors)

    return results
