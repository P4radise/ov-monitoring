import re
import json
from sqs_integration import Integration
from integration_log import IntegrationLog, LogLevel
from jsonschema import validate

with open('settings.json', "rb") as PFile:
    settings_data = json.loads(PFile.read().decode('utf-8'))

with open('settings_schema.json', "rb") as PFile:
    data_schema = json.loads(PFile.read().decode('utf-8'))

try:
    validate(instance=settings_data, schema=data_schema)
except Exception as e:
    raise Exception("Incorrect value in the settings file\n{}".format(str(e)))

ov_url = re.sub("^https://", "", settings_data["ovUrl"])
ov_access_key = settings_data["ovAccessKey"]
ov_secret_key = settings_data["ovSecretKey"]
ov_integration_name = settings_data["ovIntegrationName"]
ov_trackor_type = settings_data["trackorType"]
message_body_field = settings_data["messageBodyField"]
sent_datetime_field = settings_data["sentDateTimeField"]

message_filter = settings_data["messageFilter"]
aws_access_key_id = settings_data["awsAccessKeyId"]
aws_secret_access_key = settings_data["awsSecretAccessKey"]
aws_region = settings_data["awsRegion"]
queue_url = settings_data["queueUrl"]

wait_time_seconds = settings_data["waitTimeSeconds"]

with open('ihub_process_id', "rb") as PFile:
    process_id = PFile.read().decode('utf-8')

integration_log = IntegrationLog(process_id, ov_url, ov_access_key, ov_secret_key,
                                                ov_integration_name, ov_token=True)

sqsIntegration = Integration(ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id, integration_log, 
                                aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                                message_body_field, sent_datetime_field, message_filter, wait_time_seconds)

try:
    sqsIntegration.start()
except Exception as e:
    argsCount = len(e.args)
    error_message = str(e.args[0])
    description = str(e.args[1]) if argsCount > 1 else ''
    integration_log.add(LogLevel.ERROR, error_message, description)
    raise Exception(error_message)
