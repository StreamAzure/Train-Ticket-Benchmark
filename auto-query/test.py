import requests
import time

headers = {
    'Proxy-Connection': 'keep-alive',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}
address = "http://localhost:8080"
uid = ""

def send_a_request():
    """
    构造并发送 HTTP 请求。
    """
    # 设置请求头
    global headers, address
    http_url = "http://localhost:8080/api/v1/orderOtherService2/welcome"
    api_index = http_url.find("/api")
    http_url = address + http_url[api_index:]
    print(f"Request: {http_url}")
    response = requests.get(http_url, headers=headers)

    print(f"Response: {response.text}")
    return response

def _query_orders_all_info() -> list[tuple]:
    """
    查询订单信息
    返回(orderId, tripId) triple list for consign service
    :param headers:
    :return:
    """

    global headers, address, uid

    url = f"{address}/api/v1/orderOtherService/orderOther/refresh"

    payload = {
        "loginId": uid,
    }

    response = requests.post(url=url, headers=headers, json=payload)
    if response.status_code != 200 or response.json().get("data") is None:
        print(f"query orders failed, response data is {response.text}")
        return None

    data = response.json().get("data")
    pairs = []
    for d in data:
        result = {}
        result["accountId"] = d.get("accountId")
        result["targetDate"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        result["orderId"] = d.get("id")
        result["from"] = d.get("from")
        result["to"] = d.get("to")
        pairs.append(result)
    print(f"queried {len(pairs)} orders")

    return pairs

def login(username="fdse_microservice", password="111111") -> bool:
    """
    登陆并建立session，返回登陆结果
    """
    global headers, address
    url = address + "/api/v1/users/login"
    data = '{"username":"' + username + '","password":"' + \
           password + '","verificationCode":"1234"}'
    # 获取cookies
    verify_url = "http://localhost:8080" + '/api/v1/verifycode/generate'
    r = requests.get(url=verify_url)
    r = requests.post(url=url, headers=headers,
                      data=data, verify=False)

    if r.status_code == 200:
        data = r.json().get("data")
        uid = data.get("userId")
        token = data.get("token")
        headers["Authorization"] = f"Bearer {token}"
        print(f"login success, uid: {uid}")
        print(f"login success, token: {token}")
        return True
    else:
        print("login failed")
        return False


if __name__ == '__main__':
    # 获取 Token
    login()
    _query_orders_all_info()