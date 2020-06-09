import re
import json
from sqs_integration import Integration
from integration_log import IntegrationLog, LogLevel

integration_log = None
error_text = ''

def add_error_text(text):
    global error_text
    error_text = error_text + '\n' if error_text else ''
    error_text += text

with open('settings.json', "rb") as PFile:
    settings_data = json.loads(PFile.read().decode('utf-8'))

ov_url = settings_data["ovUrl"]
if not ov_url or not isinstance(ov_url, str) or re.match('https?://', ov_url):
    add_error_text('ovUrl must be a string and not contain a protocol (http or https)')

ov_access_key = settings_data["ovAccessKey"]
if not ov_access_key or not isinstance(ov_access_key, str):
    add_error_text('ovAccessKey cannot be empty and must be a string')

ov_secret_key = settings_data["ovSecretKey"]
if not ov_secret_key or not isinstance(ov_secret_key, str):
    add_error_text('ovSecretKey cannot be empty and must be a string')

ov_integration_name = settings_data["ovIntegrationName"]
if not ov_integration_name or not isinstance(ov_integration_name, str):
    add_error_text('ovSecretKey cannot be empty and must be a string')

with open('ihub_process_id', "rb") as PFile:
    process_id = PFile.read().decode('utf-8')

if not error_text:
    integration_log = IntegrationLog(process_id, ov_url, ov_access_key, ov_secret_key,
                                                ov_integration_name, ov_token=True)

ov_trackor_type = settings_data["trackorType"]
if not ov_trackor_type or not isinstance(ov_trackor_type, str):
    add_error_text('ov_trackor_type cannot be empty and must be a string')

message_body_field = settings_data["messageBodyField"]
if not message_body_field or not isinstance(message_body_field, str):
    add_error_text('messageBodyField cannot be empty and must be a string')

sent_datetime_field = settings_data["sentDateTimeField"]
if not sent_datetime_field or not isinstance(sent_datetime_field, str):
    add_error_text('sentDateTimeField cannot be empty and must be a string')

message_filter = settings_data["messageFilter"]
if message_filter is not None and not isinstance(message_filter, str):
    add_error_text("messageFilter must be a string")

aws_access_key_id = settings_data["awsAccessKeyId"]
if not aws_access_key_id or not isinstance(aws_access_key_id, str):
    add_error_text('awsAccessKeyId cannot be empty and must be a string')

aws_secret_access_key = settings_data["awsSecretAccessKey"]
if not aws_secret_access_key or not isinstance(aws_secret_access_key, str):
    add_error_text('awsSecretAccessKey cannot be empty and must be a string')

aws_region = settings_data["awsRegion"]
if not aws_region or not isinstance(aws_region, str):
    add_error_text('awsRegion cannot be empty and must be a string')

queue_url = settings_data["queueUrl"]
if not queue_url or not isinstance(queue_url, str) or not re.match('https?://', queue_url):
    add_error_text('queueUrl must be a string and start with a protocol (http or https)')

wait_time_seconds = settings_data["waitTimeSeconds"]
if wait_time_seconds is not None and (not isinstance(wait_time_seconds, int) or wait_time_seconds < 0 or wait_time_seconds > 20):
    add_error_text('waitTimeSeconds value must be an integer between 0 and 20 or null')

if integration_log and error_text:
    integration_log.add(LogLevel.ERROR, 'Incorrect value(s) ​​in the settings file', error_text)
    raise Exception('Incorrect value(s) ​​in the settings file')
elif error_text:
    raise Exception('Incorrect value(s) ​​in the settings file.\n{}'.format(error_text))

sqsIntegration = Integration(ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id, integration_log, 
                                aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                                message_body_field, sent_datetime_field, message_filter, wait_time_seconds)

try:
    sqsIntegration.start()
except Exception as e:
    argsCount = len(e.args)
    description = e.args[1] if argsCount > 1 else ''
    integration_log.add(LogLevel.ERROR, e.args[0], description)
    raise Exception(e.args[0])
