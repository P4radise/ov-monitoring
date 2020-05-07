import json
import requests
from enum import Enum
from curl import Curl


class IntegrationLog(object):

    def __init__(self, process_id, url, username, password, integration_name, ov_token=False):
        self.url = 'https://' + url
        self.username = username
        self.password = password
        self.process_id = process_id
        if ov_token == True:
            self.auth = HTTPBearerAuth(self.username, self.password)
        else:
            self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.integration_name = integration_name
        self.integration_params = self.get_integration_params()
        self.integration_log_level_id = self.get_integration_log_level_id()

    def get_integration_params(self):
        headers = {'content-type': 'application/json'}
        url = self.url + "/api/v3/integrations/" + self.integration_name
        curl = Curl('GET', url, headers=headers, auth=self.auth)
        if len(curl.errors) > 0:
            raise Exception(curl.errors)
        return curl.jsonData

    def add_log(self, log_level, message, description=""):
        if log_level.log_level_id <= self.integration_log_level_id:
            parameters = {'message': message, 'description': description, 'log_level_name': log_level.log_level_name}
            json_data = json.dumps(parameters)
            headers = {'content-type': 'application/json'}
            url_log = self.url + "/api/v3/integrations/runs/" + str(self.process_id) + "/logs"
            Curl('POST', url_log, data=json_data, headers=headers, auth=self.auth)
    
    def get_integration_log_level_id(self):
        for log_level in list(LogLevel):
            if log_level.log_level_name == self.integration_params["log_level"]:
                return log_level.log_level_id


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