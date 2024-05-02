import re

target_path = 'http://172.25.0.75:18673/api/v1/inside_pay_service/inside_payment/drawback/?/?'
test_path = 'http://172.25.0.75:18673/api/v1/inside_pay_service/inside_payment/drawback/4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f/0.00'

regex_pattern = re.escape(target_path).replace(r"\?", ".*")
pattern = re.compile(regex_pattern)

if pattern.match(test_path):
    print("matched!")