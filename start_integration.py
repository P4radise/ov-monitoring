import json
from sqs_integration import Integration

with open('settings.json', "rb") as PFile:
    settings_data = json.loads(PFile.read().decode('utf-8'))

ov_url = settings_data["ovUrl"]
ov_access_key = settings_data["ovAccessKey"]
ov_secret_key = settings_data["ovSecretKey"]
ov_integration_name = settings_data["ovIntegrationName"]
ov_trackor_type = settings_data["trackorType"]
message_body_field = settings_data["messageBodyField"]
sent_datetime_field = settings_data["sentDateTimeField"]

aws_access_key_id = settings_data["awsAccessKeyId"]
aws_secret_access_key = settings_data["awsSecretAccessKey"]
aws_region = settings_data["awsRegion"]
queue_url = settings_data["queueUrl"]

wait_time_seconds = settings_data["waitTimeSeconds"]

with open('ihub_process_id', "rb") as PFile:
    process_id = PFile.read().decode('utf-8')

sqsIntegration = Integration(ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id, ov_integration_name, 
                                aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                                message_body_field, sent_datetime_field, wait_time_seconds)
sqsIntegration.start()
