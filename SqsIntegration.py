import boto3
import json
import onevizion
import datetime

from curl import Curl
from integration_log import IntegrationLog, LogLevel


class Integration(object):

    def __init__(self, ov_url, ov_username, ov_pwd, ov_tt, process_id, 
                    aws_access_key_id, aws_secret_access_key, aws_region):

        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_region = aws_region
        self._sqs_client = boto3.client(
            'sqs', 
            region_name=self._aws_region, 
            aws_access_key_id = self._aws_access_key_id, 
            aws_secret_access_key = self._aws_secret_access_key
        )

        self._ov_url = ov_url
        self._ov_username = ov_username
        self._ov_pwd = ov_pwd
        self._ov_tt = ov_tt
        self._trackor = onevizion.Trackor(self._ov_tt, self._ov_url, self._ov_username, self._ov_pwd)
        self._integration_log = IntegrationLog(process_id, ov_url, ov_username, ov_pwd)
        self._headers = {'content-type': 'application/json'}

    def start(self, queue_url, iteration_max_num = 100):
        self._integration_log.add_log(LogLevel.INFO.log_level_name, "Starting Integration")

        iteration_count = 0
        while iteration_count < iteration_max_num:
            try:
                response = self._sqs_client.receive_message(
                    QueueUrl = queue_url,
                    AttributeNames = ['SentTimestamp'],
                    MessageAttributeNames = ['All'],
                    MaxNumberOfMessages = 10,
                    WaitTimeSeconds = 10
                )
            except Exception as e:
                    self._integration_log.add_log(LogLevel.ERROR.log_level_name,
                                                'Cannot receive message',
                                                queue_url)
                    raise Exception('Cannot receive message') from e

            if not 'Messages' in response:
                break

            for message in response['Messages']:
                sent_timestamp = int(message['Attributes']['SentTimestamp'])
                sent_datetime = datetime.datetime.fromtimestamp(sent_timestamp / 1000)
                fields = {
                    'MEVT_MESSAGE' : message['Body'], 
                    'MEVT_DATETIME' :  sent_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                }
                test = self.create_trackor(fields)

                try:
                    self._sqs_client.delete_message(
                        QueueUrl = queue_url,
                        ReceiptHandle = message['ReceiptHandle']
                    )
                except Exception as e:
                    self._integration_log.add_log(LogLevel.ERROR.log_level_name,
                                                'Cannot delete message',
                                                message)
                    raise Exception('Cannot delete message') from e

            iteration_count += 1

        if iteration_count == 0:
            self._integration_log.add_log(LogLevel.WARNING.log_level_name, 'No new messages found')
            
        self._integration_log.add_log(LogLevel.INFO.log_level_name, 'Integration has been completed')

    def create_trackor(self, fields):
        url = self._ov_url + '/api/v3/trackor_types/' + str(self._ov_tt) + '/trackors'
        data = {'fields': fields}
        curl = Curl('POST', url, headers=self._headers, auth=(self._ov_username, self._ov_pwd), data=json.dumps(data))
        if len(curl.errors) > 0:
            raise Exception(curl.errors)
        return curl.jsonData