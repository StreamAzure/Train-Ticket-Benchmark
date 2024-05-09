from mitmproxy import http
import time

OUTPUT_PATH = "interceptor/flows.json"

class HTTPLogger:
    """
    为 request 添加时间戳
    并将流量保存到指定dmp文件
    """

    def __init__(self, output_path):
        self.flow_file = open(output_path, "w")
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
    
    def done(self):
        # 所有流量处理完成后，关闭文件
        self.flow_file.close()

addons = [
    HTTPLogger(OUTPUT_PATH),
]