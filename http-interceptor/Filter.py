from mitmproxy import http
from mitmproxy import ctx
from mitmproxy import flowfilter
from match_request import match_request
import re
import os
import time
import json

class Filter:
    """
    根据输入的 candidate_pairs 文件中的 request pair 拦截请求
    匹配条件：
    - method 相同 && path 相同
    - 对于 POST、PUT、DELETE 请求，对 body 进行匹配
        - 我们只需判断是否是某个操作的请求，所以启发式去除 ID、time 等因实际情况而不同的字段，再匹配余下内容
            - 匹配全部文本再计算匹配率
            - 不能只匹配字段名，否则无法区分 F1 case 中的情形
    若拦截到目标请求：
    - 
    """
    def __init__(self, log_file, candidate_pairs_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)  # 确保日志文件的目录存在
        self.logfile = open(log_file, 'a') # 打开日志文件
        self.candidate_pairs = self._read_candidate_pairs(candidate_pairs_file) # 读取候选请求对
        self.testing_id = 0 # 当前正在匹配的 candidate_pair
        self.target_reqs = self._get_target_reqs(self.candidate_pairs[str(self.testing_id)])

    def _read_candidate_pairs(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data

    def log(self, message):
        self.logfile.write(json.dumps(message, indent=4, default=str))
        self.logfile.write("\n")
        self.logfile.flush()

    def _get_target_reqs(self, pair):
        target_reqs = []
        for req in pair:
            parts = req.split()
            if len(parts) > 1: 
                method = parts[1]
                path = parts[2]
                body = parts[3] if len(parts) >= 4 else ""
                target_reqs.append({
                    "method": method,
                    "path": path,
                    "body": body 
                })
            else:
                raise ValueError("Invalid request string format")

        return target_reqs
    
    def request(self, flow: http.HTTPFlow) -> None:
        timestamp = str(round(time.time() * 1000))
        flow.request.headers['X-Timestamp'] = timestamp
        # ctx.log.info(target_reqs)
        if len(self.target_reqs) == 0 :
            return
           
        # 针对当前请求对进行拦截
        for i, req in enumerate(self.target_reqs):
            # 如果满足所有配对条件
            # 拦截
            if match_request(req['path'], req['method'], req['body'], flow.request.url, flow.request.method, flow.request.content):
                request_json = {
                    "method": flow.request.method,
                    "url": flow.request.pretty_url,
                    # "headers": dict(flow.request.headers),
                    "body": json.loads(flow.request.content.decode('utf-8')) if flow.request.content and flow.request.headers.get("Content-Type") == "application/json" else flow.request.text,
                }
                self.log(req)
                self.target_reqs.pop(i) # pair 中其中一个请求已到达
                self.log(request_json)
        
        self.log(f"request pair: {self.testing_id} done")
        self.testing_id += 1
        if(self.testing_id >= len(self.candidate_pairs)):
            self.log(f"candidate_pairs test all done!")
            self.done()
        else:
            # 测试下一个请求对
            self.target_reqs = self._get_target_reqs(self.candidate_pairs[str(self.testing_id)])

    # def response(self, flow: http.HTTPFlow) -> None:
    #     timestamp = str(round(time.time() * 1000))
    #     flow.response.headers['X-Timestamp'] = timestamp
    #     try:
    #         response_body = json.loads(flow.response.content.decode('utf-8'))
    #     except json.JSONDecodeError:
    #         response_body = flow.response.content.decode('utf-8', errors='ignore') if flow.response.content else None

    #     # 记录响应信息
    #     response_data = {
    #         "type": "response",
    #         "status_code": flow.response.status_code,
    #         "headers": dict(flow.response.headers),
    #         "body": response_body
    #     }
    #     self.log(response_data)

    def done(self):
        # 关闭日志文件
        self.logfile.close()