import mitmproxy.http
from mitmproxy import ctx
from mitmproxy import flowfilter

class AddHeader:
    def __init__(self):
        self.num = 0

    def response(self, flow):
        self.num = self.num + 1
        flow.response.headers["count"] = str(self.num)

addons = [
    AddHeader()
]