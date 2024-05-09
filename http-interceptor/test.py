import re

# target_path = '/api/v1/inside_pay_service/inside_payment/drawback/?/?'
# test_path = 'http://172.25.0.75:18673/api/v1/inside_pay_service/inside_payment/drawback/4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f/0.00'

target_path = '/api/v1/orderOtherService/orderOther/?'
test_path = 'http://172.19.0.40:12032/api/v1/orderOtherService/orderOther/cb5fa40f-7def-45d8-a5c5-eb29d42134bc'

test_path = re.sub(r'http://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d+', '', test_path)

regex_pattern = re.escape(target_path).replace(r"\?", ".*")
pattern = re.compile(regex_pattern)

if pattern.match(test_path):
    print("matched!")