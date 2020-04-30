import json
from SqsIntegration import Integration

with open('settings.json', "rb") as PFile:
    pwd_data = json.loads(PFile.read().decode('utf-8'))

ov_url = pwd_data["ovUrl"]
ov_access_key = pwd_data["ovAccessKey"]
ov_secret_key = pwd_data["ovSecretKey"]
ov_trackor_type = pwd_data["trackorType"]
message_body_field = pwd_data["messageBodyField"]
sent_datetime_field = pwd_data["sentDateTimeField"]

aws_access_key_id = pwd_data["awsAccessKeyId"]
aws_secret_access_key = pwd_data["awsSecretAccessKey"]
aws_region = pwd_data["awsRegion"]
queue_url = pwd_data["queueUrl"]

wait_time_seconds = pwd_data["waitTimeSeconds"]

with open('ihub_process_id', "rb") as PFile:
    process_id = PFile.read().decode('utf-8')

sqsIntegration = Integration(ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id, 
                                aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                                message_body_field, sent_datetime_field, wait_time_seconds)
sqsIntegration.start()
