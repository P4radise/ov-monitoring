import json
from enum import Enum
from curl import Curl


class IntegrationLog(object):

    def __init__(self, process_id, url, username, password):
        self.URL = url
        self.username = username
        self.password = password
        self.processId = process_id

    def add_log(self, log_level, message, description=""):
        parameters = {'message': message, 'description': description, 'log_level_name': log_level}
        json_data = json.dumps(parameters)
        headers = {'content-type': 'application/json'}
        url_log = self.URL + "/api/v3/integrations/runs/" + str(self.processId) + "/logs"
        Curl('POST', url_log, data=json_data, headers=headers, auth=(self.username, self.password))


class LogLevel(Enum):
    INFO = (0, "Info")
    WARNING = (1, "Warning")
    ERROR = (2, "Error")
    DEBUG = (3, "Debug")

    def __init__(self, log_level_id, log_level_name):
        self.log_level_id = id
        self.log_level_name = log_level_name