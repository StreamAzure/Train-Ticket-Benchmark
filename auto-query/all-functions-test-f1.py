import time
import requests

"""
全流程测试
针对 F1 （F1只在对普通票操作时出问题）
因此只对普通票操作
"""

datestr = time.strftime("%Y-%m-%d", time.localtime())

address = "http://localhost:8080"
uid = ""
token = ""
headers = {
            'Proxy-Connection': 'keep-alive',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }

place_pair = ("Shang Hai", "Nan Jing")

def login(username="fdse_microservice", password="111111") -> bool:
    """
    登陆并建立session，返回登陆结果
    """
    global uid, headers, address, token
    url = f"{address}/api/v1/users/login"

    data = '{"username":"' + username + '","password":"' + \
        password + '","verificationCode":"1234"}'

    # 获取cookies
    verify_url = address + '/api/v1/verifycode/generate'
    r = requests.get(url=verify_url)
    r = requests.post(url=url, headers=headers,
                            data=data, verify=False)

    if r.status_code == 200:
        data = r.json().get("data")
        uid = data.get("userId")
        token = data.get("token")
        headers["Authorization"] = f"Bearer {token}"
        print(f"login success, uid: {uid}")
        return True
    else:
        print("login failed")
        return False
    
def query_tickets():
    global uid, headers, address, token
    # =================== 普通车票查询 =====================
    query_url = f"{address}/api/v1/travel2service/trips/left"
    query_payload = {
                "departureTime": datestr,
                "startPlace": place_pair[0],
                "endPlace": place_pair[1],
            }
    print("发送车票查询请求")
    response = requests.post(query_url, timeout=5, headers=headers, json = query_payload)
    if response.status_code == 200:
        res_data = response.json()
        if res_data["status"] == 1:
            print("车票查询成功")
            return res_data
        else:
            print(f"车票查询失败，{res_data}")
    else:
        raise Exception(f"查询请求失败，状态码：{response.status_code}")
                
def preserve_normal_ticket(trip_id, contacts_id):
    global uid, headers, address, token
    # =================== 普通车票预订 =====================
    preserve_url = f"{address}/api/v1/preserveotherservice/preserveOther"
    preserve_payload = {
        "accountId": uid,
        "assurance": "0",
        "contactsId": contacts_id,
        "date": datestr,
        "from": place_pair[0],
        "to": place_pair[1],
        "tripId": trip_id,
        "foodType": "0",
        "seatType": 2
    }
    
    print("发送车票预订请求")
    response = requests.post(preserve_url, timeout=5, headers=headers, json = preserve_payload)
    if response.status_code == 200:
        res_data = response.json()
        if res_data["status"] == 1:
            print("车票预订成功")
            return res_data
        else:
            print(f"车票预订失败，{res_data}")
    else:
        raise Exception(f"预订请求失败，状态码：{response.status_code}")
            
def pay_ticket(trip_id, order_id: str):
    global uid, headers, address, token
    pay_url = f"{address}/api/v1/inside_pay_service/inside_payment"
    pay_paytload = {
        "orderId": order_id,
        "tripId": trip_id
    }

    response = requests.post(pay_url, timeout=5, headers=headers, json=pay_paytload)
    if response.status_code == 200:
        print("车票支付")
        return response.json()
    else:
        raise Exception(f"车票支付失败，状态码：{response.status_code}")

def cancel_ticket(order_id:str):
    global uid, headers, address, token
    cancel_url = f"{address}/api/v1/cancelservice/cancel/{order_id}/{uid}"

    response =  requests.get(cancel_url, timeout=5, headers=headers)
    if response.status_code == 200:
        print("车票取消")
    else:
        raise Exception(f"车票取消失败，状态码：{response.status_code}")

def main():
    trip_id = "Z1234"
    # 每次重启数据库时 contact_id 会改变
    contact_id = "5b91d286-6b23-48fe-8e3c-a4fe815a74ed" 

    query_tickets()
    data = preserve_normal_ticket(trip_id, contact_id)
    order_id = data["data"]

    pay_ticket(trip_id, order_id)
    cancel_ticket(order_id)

login()
main()