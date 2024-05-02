import re
from collections import Counter
import difflib

def is_id_field(key):
    # 检查字段名是否包含 'id' 或类似的名称
    return 'id' in key.lower()

def is_datetime_field(key, value):
    if not isinstance(value, str):
        return False

    # 检查字段是否疑似日期时间
    # 2024-05-02 18:07:19 2024-05-02 2024-05-02 18:07
    datetime_pattern = r'\b\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}(?::\d{2})?)?\b'
    is_datetime_value = re.match(datetime_pattern, value) is not None

    # 检查字段名是否包含某些关键字
    keywords = ["Date", "Time","_date","_time","date_","time_"]
    is_datetime_key = any(keyword in key for keyword in keywords)

    return is_datetime_value and is_datetime_key

def calculate_match_rate(dict_str1, dict_str2):
    def pre_process(dict_str1, dict_str2):
        # 将字符串转换为字典
        dict1 = eval(dict_str1)
        dict2 = eval(dict_str2)

        # 排除特定字段
        filtered_dict1 = {k: v for k, v in dict1.items() if not is_id_field(k) and not is_datetime_field(k, v)}
        filtered_dict2 = {k: v for k, v in dict2.items() if not is_id_field(k) and not is_datetime_field(k, v)}

        # 将过滤后的字典转换为字符串以进行匹配
        str1 = str(filtered_dict1)
        str2 = str(filtered_dict2)

        return str1, str2
    
    str1, str2 = pre_process(dict_str1, dict_str2)
    # 计算两个字符串的匹配率
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()

def _match_body(target_body, body) -> bool:
    # 字符串相似程度大于等于指定阈值
    # 视为 body 匹配成功
    match_ratio = calculate_match_rate(target_body, body)
    threshold = 0.9
    return match_ratio >= threshold

def _match_path(target_path, path) -> bool:
    # 去除 url 中的 http, ip, 端口前缀
    # 再排除掉路径中的变量部分
    path = re.sub(r'http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d+', '', path)
    regex_pattern = re.escape(target_path).replace(r"\?", ".*")
    pattern = re.compile(regex_pattern)

    return pattern.match(path) is not None

def _match_method(target_method, method) -> bool:
    return method == target_method

def match_request(target_path, target_method, target_body, now_path, now_method, now_body)-> bool:

    return _match_method(target_method, now_method) and _match_path(target_path, now_path) and _match_body(target_body, now_body)

if __name__ == "__main__":
    # 示例字典字符串
    dict_str1 = "{'id': 'cb5fa40f-7def-45d8-a5c5-eb29d42134bc', 'boughtDate': '2024-05-02 18:07:19', 'travelDate': '2024-05-02', 'travelTime': '2013-05-04 09:51:52', 'accountId': '4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f', 'contactsName': 'Contacts_Two', 'documentType': 1, 'contactsDocumentNumber': 'DocumentNumber_Two', 'trainNumber': 'Z1234', 'coachNumber': 5, 'seatClass': 2, 'seatNumber': '876161173', 'from': 'shanghai', 'to': 'nanjing', 'status': 4, 'price': '350.0', 'differenceMoney': '0.0'}"
    dict_str2 = "{'id': 'cb5fa40f-7def-45d8-a5c5-eb435435443c', 'boughtDate': '2024-05-02 18:37:19', 'travelDate': '2024-25-02', 'travelTime': '2013-05-04 09:51:52', 'accountId': '4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f', 'contactsName': 'Contacts_Two', 'documentType': 1, 'contactsDocumentNumber': 'DocumentNumber_Two', 'trainNumber': 'Z1234', 'coachNumber': 5, 'seatClass': 2, 'seatNumber': '876161173', 'from': 'shanghai', 'to': 'nanjing', 'status': 7, 'price': '350.0', 'differenceMoney': '0.0'}"

    calculate_match_rate(dict_str1, dict_str2)

