import json
from SqsIntegration import Integration

with open('settings.json', "rb") as PFile:
    pwd_data = json.loads(PFile.read().decode('utf-8'))

ov_url = 'https://' + pwd_data["ovUrl"]
ov_access_key = pwd_data["ovAccessKey"]
ov_secret_key = pwd_data["ovSecretKey"]
ov_tt = pwd_data["trackorType"]

aws_access_key_id = pwd_data["awsAccessKeyId"]
aws_secret_access_key = pwd_data["awsSecretAccessKey"]
aws_region = pwd_data["awsRegion"]
queue_url = pwd_data["queueUrl"]

iteration_max_num = pwd_data["iterationMaxNum"]

with open('ihub_process_id', "rb") as PFile:
    process_id = PFile.read().decode('utf-8')

sqsIntegration = Integration(ov_url, ov_access_key, ov_secret_key, ov_tt, process_id, 
                                aws_access_key_id, aws_secret_access_key, aws_region)
sqsIntegration.start(queue_url, iteration_max_num)
