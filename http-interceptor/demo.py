from mitmproxy import http
from mitmproxy import ctx
from mitmproxy import flowfilter
import os
import time
import json
class HTTPLogger:
    def __init__(self,filename):
        # 确保日志文件的目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # 打开日志文件
        self.logfile = open(filename, 'a')
        self.id = 0

    def log(self, message):
        log_entry = {
            "id": self.id,
            "type": message["type"],
            "method": message["method"] if "method" in message else None,
            "url": message["url"] if "url" in message else None,
            "headers": message["headers"],
            "body": message["body"]
        }
        # 将日志条目转换为JSON字符串并写入日志文件
        self.logfile.write(json.dumps(log_entry))
        self.logfile.write("\n")
        self.logfile.flush()
        # 更新报文ID计数器
        self.id += 1
    
    def request(self, flow: http.HTTPFlow) -> None:
        timestamp = str(round(time.time() * 1000))
        flow.request.headers['X-Timestamp'] = timestamp
        try:
            request_body = json.loads(flow.request.content.decode('utf-8'))
        except json.JSONDecodeError:
            request_body = flow.request.content.decode('utf-8', errors='ignore') if flow.request.content else None
        # 创建请求的JSON对象
        request_json = {
            "type": "request",
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "headers": dict(flow.request.headers),
            "body": request_body
        }
        self.log(request_json)

    def response(self, flow: http.HTTPFlow) -> None:
        timestamp = str(round(time.time() * 1000))
        flow.response.headers['X-Timestamp'] = timestamp
        try:
            response_body = json.loads(flow.response.content.decode('utf-8'))
        except json.JSONDecodeError:
            response_body = flow.response.content.decode('utf-8', errors='ignore') if flow.response.content else None

        # 记录响应信息
        response_data = {
            "type": "response",
            "status_code": flow.response.status_code,
            "headers": dict(flow.response.headers),
            "body": response_body
        }
        self.log(response_data)

    def done(self):
        # 关闭日志文件
        self.logfile.close()

addons = [
    HTTPLogger('interceptor/http_logs.json')
]