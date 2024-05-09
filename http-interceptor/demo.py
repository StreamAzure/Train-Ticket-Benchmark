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
            data = f.read()
            data = json.loads(data)
        return data

    def log(self, message):
        self.logfile.write(json.dumps(message, indent=4, default=str))
        self.logfile.write("\n")
        self.logfile.flush()

    def _get_target_reqs(self, pair):
        target_reqs = []
        target_reqs.append(json.loads(pair[0]))
        target_reqs.append(json.loads(pair[1]))
        return target_reqs
    
    def _match(self, req, url, method, body):
        if match_request(req['url'], req['method'], req['body'], url, method, body):
            request_json = {
                "method": method,
                "url": url,
                "body": body,
            }
            self.log(req)
            self.target_reqs.pop(0) # pair 中其中一个请求已到达
            self.log(request_json)
        else:
            self.log("req match failed")
    
    def request(self, flow: http.HTTPFlow) -> None:
        timestamp = str(round(time.time() * 1000))
        flow.request.headers['X-Timestamp'] = timestamp
        if len(self.target_reqs) == 0 :
            return

        self.log("testing...")

        url = flow.request.url
        method = flow.request.method
        body = json.loads(flow.request.content.decode('utf-8')) if flow.request.content and flow.request.headers.get("Content-Type") == "application/json" else flow.request.text
        
        # 针对当前请求对进行拦截
        if len(self.target_reqs) > 1:
            req1 = self.target_reqs[0]
            req2 = self.target_reqs[1]
            self._match(req1, url, method, body)
            self._match(req2, url, method, body)
        else:
            req = self.target_reqs[0]
            self._match(req, url, method, body)
            
        if len(self.target_reqs) == 0: # 完成一个请求对的监听匹配
            self.log(f"request pair: {self.testing_id} done") 
            self.testing_id += 1

        if(self.testing_id >= len(self.candidate_pairs)):
            self.log(f"candidate_pairs test all done!")
            self.done()
        else:
            # 测试下一个请求对
            self.target_reqs = self._get_target_reqs(self.candidate_pairs[str(self.testing_id)])

    def done(self):
        # 关闭日志文件
        self.logfile.close()

class HTTPLogger:
    """
    打印所有请求数据
    """
    def __init__(self,filename):
        # 确保日志文件的目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # 打开日志文件
        self.logfile = open(filename, 'a')

    def log(self, message):
        # self.logfile.write(json.dumps(message, indent=4, sort_keys=True, default=str))
        self.logfile.write(json.dumps(message))
        self.logfile.write("\n")
        self.logfile.flush()
    
    def request(self, flow: http.HTTPFlow) -> None:
        # 添加时间戳
        timestamp = str(round(time.time() * 1000))
        flow.request.headers['X-Timestamp'] = timestamp
        message = {
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "headers": dict(flow.request.headers),
            "body": json.loads(flow.request.content.decode('utf-8')) if flow.request.content and flow.request.headers.get("Content-Type") == "application/json" else flow.request.text,
        }
        self.log(message)

normal_log = 'interceptor/log.json'
intercept_log = 'interceptor/intercept_log.json'
candidate_pair_file = 'interceptor/candidate-pairs.json'

addons = [
    HTTPLogger(normal_log),
    Filter(intercept_log, candidate_pair_file),
]