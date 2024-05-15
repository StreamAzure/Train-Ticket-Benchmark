from mitmproxy import http
import time

OUTPUT_REQUEST_PATH = "interceptor/flows.json"
OUTPUT_RESPONSE_PATH = "interceptor/response.json"

class HTTPLogger:
    """
    为 request 添加时间戳
    并将流量保存到指定dmp文件
    """

    def __init__(self, output_req_path, output_res_path):
        self.flow_file = open(output_req_path, "w")
        self.response_flow_file = open(output_res_path, "w")
        self.request_cnt = 0

    def request(self, flow: http.HTTPFlow) -> None:
        # 添加时间戳
        timestamp = str(round(time.time() * 1000))
        flow.request.headers['X-Timestamp'] = timestamp
        req = {
            "id": self.request_cnt,
            "url": flow.request.pretty_url,
            "method": flow.request.method,
            "headers": dict(flow.request.headers),
            "content": flow.request.content.decode()
        }
        self.request_cnt += 1

        self.flow_file.write(str(req))
        self.flow_file.write("\n")
        self.flow_file.flush()
    
    def response(self, flow: http.HTTPFlow) -> None:
        # 添加时间戳
        timestamp = str(round(time.time() * 1000))
        flow.response.headers['X-Timestamp'] = timestamp
        res = {
            "status_code": flow.response.status_code,
            "headers": dict(flow.response.headers),
            "content": flow.response.text
        }

        self.response_flow_file.write(str(res))
        self.response_flow_file.write("\n")
        self.response_flow_file.flush()
    
    def done(self):
        # 所有流量处理完成后，关闭文件
        self.flow_file.close()

addons = [
    HTTPLogger(OUTPUT_REQUEST_PATH, OUTPUT_RESPONSE_PATH),
]