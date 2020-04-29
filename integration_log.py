import json
import requests
from enum import Enum
from curl import Curl


class IntegrationLog(object):

    def __init__(self, process_id, url, username, password, ov_token=False):
        self.url = 'https://' + url
        self.username = username
        self.password = password
        self.processId = process_id
        if ov_token == True:
            self.auth = HTTPBearerAuth(self.username, self.password)
        else:
            self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)

    def add_log(self, log_level, message, description=""):
        parameters = {'message': message, 'description': description, 'log_level_name': log_level}
        json_data = json.dumps(parameters)
        headers = {'content-type': 'application/json'}
        url_log = self.url + "/api/v3/integrations/runs/" + str(self.processId) + "/logs"
        Curl('POST', url_log, data=json_data, headers=headers, auth=self.auth)


class LogLevel(Enum):
    INFO = (0, "Info")
    WARNING = (1, "Warning")
    ERROR = (2, "Error")
    DEBUG = (3, "Debug")

    def __init__(self, log_level_id, log_level_name):
        self.log_level_id = log_level_id
        self.log_level_name = log_level_name

class HTTPBearerAuth(requests.auth.AuthBase):
	def __init__(self, ov_access_key, ov_secret_key):
		self.access_key = ov_access_key
		self.secret_key = ov_secret_key

	def __call__(self, request):
		request.headers['Authorization'] = 'Bearer ' + self.access_key + ':' + self.secret_key
		return request