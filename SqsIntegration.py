import boto3
import json
import datetime
import onevizion

from curl import Curl
from integration_log import IntegrationLog, LogLevel


class Integration(object):

    def __init__(self, ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id,
                    aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                    message_body_field, sent_datetime_field, wait_time_seconds = 10):

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
        self._ov_access_key = ov_access_key
        self._ov_secret_key = ov_secret_key
        self._ov_trackor_type = ov_trackor_type

        self._queue_url = queue_url
        self._message_body_field = message_body_field
        self._sent_datetime_field = sent_datetime_field
        self._wait_time_seconds = wait_time_seconds

        self._integration_log = IntegrationLog(process_id, self._ov_url, self._ov_access_key, self._ov_secret_key, ov_token=True)
        self._trackor = onevizion.Trackor(self._ov_trackor_type, self._ov_url, self._ov_access_key, self._ov_secret_key, ovToken=True)

    def start(self):
        self._integration_log.add_log(LogLevel.INFO.log_level_name, "Starting Integration")

        MAX_NUMBER_OF_MESSAGES = 10
        ITERATION_MAX_NUM = 200
        iteration_count = 0
        while iteration_count < ITERATION_MAX_NUM:
            try:
                response = self._sqs_client.receive_message(
                    QueueUrl = self._queue_url,
                    AttributeNames = ['SentTimestamp'],
                    MessageAttributeNames = ['All'],
                    MaxNumberOfMessages = MAX_NUMBER_OF_MESSAGES,
                    WaitTimeSeconds = self._wait_time_seconds
                )
            except Exception as e:
                self._integration_log.add_log(LogLevel.ERROR.log_level_name,
                                            'Cannot receive message',
                                            self._queue_url)
                raise Exception('Cannot receive message') from e

            if not 'Messages' in response:
                break

            for message in response['Messages']:
                self.create_trackor(message)
                self.delete_message(message)
                
            iteration_count += 1

        if iteration_count == 0:
            self._integration_log.add_log(LogLevel.WARNING.log_level_name, 'No new messages found')
            
        self._integration_log.add_log(LogLevel.INFO.log_level_name, 'Integration has been completed')

    def create_trackor(self, message):
        sent_timestamp = int(message['Attributes']['SentTimestamp'])
        sent_datetime = datetime.datetime.fromtimestamp(sent_timestamp / 1000)
        fields = {
            self._message_body_field : message['Body'], 
            self._sent_datetime_field : sent_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        self._trackor.create(fields)
        self._integration_log.add_log(LogLevel.DEBUG.log_level_name, 
                                    'Trackor created. Trackor Id = ' + str(self._trackor.jsonData['TRACKOR_ID']) + ' Trackor Key = ' + self._trackor.jsonData['TRACKOR_KEY'])

    def delete_message(self, message):
        try:
            self._sqs_client.delete_message(
                QueueUrl = self._queue_url,
                ReceiptHandle = message['ReceiptHandle']
            )
        except Exception as e:
            self._integration_log.add_log(LogLevel.ERROR.log_level_name,
                                        'Cannot delete message',
                                        message)
            raise Exception('Cannot delete message') from e
        
        self._integration_log.add_log(LogLevel.DEBUG.log_level_name, 
                                    'Message ' + message['MessageId'] + ' deleted')