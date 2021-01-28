import boto3
import datetime
from amazon_message import AmazonMessage
from integration_error import IntegrationError

class MessageQueueService:
    MAX_NUMBER_OF_MESSAGES = 10

    def __init__(self, aws_auth, queue_url, wait_time_seconds):
        self._aws_auth = aws_auth
        self._queue_url = queue_url
        self._wait_time_seconds = wait_time_seconds or 10

        self._sqs_client = boto3.client(
            'sqs', 
            region_name=self._aws_auth.region, 
            aws_access_key_id=self._aws_auth.access_key_id, 
            aws_secret_access_key=self._aws_auth.secret_access_key
        )

    def get_messages(self):
        try:
            response = self._sqs_client.receive_message(
                QueueUrl = self._queue_url,
                AttributeNames = ['SentTimestamp'],
                MessageAttributeNames = ['All'],
                MaxNumberOfMessages = MessageQueueService.MAX_NUMBER_OF_MESSAGES,
                WaitTimeSeconds = self._wait_time_seconds
            )
        except Exception as e:
            raise IntegrationError('Cannot get messages from SQS queue', str(e))

        amazon_messages = []
        if 'Messages' in response:
            for message in response['Messages']:
                amazon_messages.append(AmazonMessage(message))
        
        return amazon_messages

    def delete_message(self, receipt_handle):
        try:
            self._sqs_client.delete_message(
                QueueUrl = self._queue_url,
                ReceiptHandle = receipt_handle
            )
        except Exception as e:
            raise IntegrationError('Cannot remove message from SQS queue', str(e))