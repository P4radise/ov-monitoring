import boto3
import datetime

class MessageQueueService:
    MAX_NUMBER_OF_MESSAGES = 10

    def __init__(self, access_key_id, secret_access_key, aws_region, queue_url, wait_time_seconds=10):
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._aws_region = aws_region
        self._queue_url = queue_url
        self._wait_time_seconds = wait_time_seconds

        self._sqs_client = boto3.client(
            'sqs', 
            region_name=self._aws_region, 
            aws_access_key_id=self._access_key_id, 
            aws_secret_access_key=self._secret_access_key
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
            raise Exception('Cannot get messages from SQS queue', str(e))

        if 'Messages' in response:
            return response['Messages']
        else:
            return None

    def delete_message(self, receipt_handle):
        try:
            self._sqs_client.delete_message(
                QueueUrl = self._queue_url,
                ReceiptHandle = receipt_handle
            )
        except Exception as e:
            raise Exception('Cannot remove message from SQS queue', str(e))