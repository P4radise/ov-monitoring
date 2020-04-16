import json
from datetime import datetime
import requests


class Curl(object):

    def __init__(self, method='GET', url=None, **kwargs):
        self.method = method
        self.url = url
        self.params = None
        self.data = None
        self.headers = None
        self.cookies = None
        self.files = None
        self.auth = None
        self.timeout = None
        self.allow_redirects = True
        self.proxies = None
        self.hooks = None
        self.stream = None
        self.verify = None
        self.cert = None
        self.json = None
        self.request = None
        self.errors = []
        self.jsonData = {}
        self.args = {}
        self.duration = None
        self.sentUrl = None
        self.sentArgs = None
        for key, value in kwargs.items():
            self.args[key] = value
            setattr(self, key, value)

        if self.url is not None:
            self.runQuery()

    def setArg(self, key, value):
        if value is not None:
            self.args[key] = value

    def runQuery(self):
        self.setArg('params', self.params)
        self.setArg('data', self.data)
        self.setArg('headers', self.headers)
        self.setArg('cookies', self.cookies)
        self.setArg('files', self.files)
        self.setArg('auth', self.auth)
        self.setArg('timeout', self.timeout)
        self.setArg('allow_redirects', self.allow_redirects)
        self.setArg('proxies', self.proxies)
        self.setArg('hooks', self.hooks)
        self.setArg('stream', self.stream)
        self.setArg('verify', self.verify)
        self.setArg('cert', self.cert)
        self.setArg('json', self.json)

        self.errors = []
        self.jsonData = {}
        self.sentUrl = self.url
        self.sentArgs = self.args
        before = datetime.utcnow()
        try:
            self.request = requests.request(self.method, self.url, **self.args)
        except Exception as e:
            self.errors.append(str(e))
        else:
            if self.request.status_code not in range(200, 300):
                self.errors.append(
                    str(self.request.status_code) + " = " + self.request.reason + "\n" + str(self.request.text))
            try:
                self.jsonData = json.loads(self.request.text)
            except Exception as err:
                pass
        after = datetime.utcnow()
        delta = after - before
        self.duration = delta.total_seconds()