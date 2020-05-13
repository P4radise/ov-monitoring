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
        response = self._sqs_client.receive_message(
            QueueUrl = self._queue_url,
            AttributeNames = ['SentTimestamp'],
            MessageAttributeNames = ['All'],
            MaxNumberOfMessages = MessageQueueService.MAX_NUMBER_OF_MESSAGES,
            WaitTimeSeconds = self._wait_time_seconds
        )

        if 'Messages' in response:
            return response['Messages']
        else:
            return None

    def delete_message(self, message):
        receipt_handle = self.get_message_param(message, 'ReceiptHandle')

        self._sqs_client.delete_message(
            QueueUrl = self._queue_url,
            ReceiptHandle = receipt_handle
        )

    def get_message_param(self, message, param):
        if param in message:
            return message[param]
        else:
            raise Exception('Incorrect message structure from SQS.\nParameter "{param}"  not found in {message}'.format(
                                param=param, message=message))

    def get_sent_datetime(self, message):
        message_attribs = self.get_message_param(message, 'Attributes')
        sent_timestamp = self.get_message_param(message_attribs, 'SentTimestamp')

        try:
            sent_datetime = datetime.datetime.fromtimestamp(int(sent_timestamp) / 1000)
            return sent_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            raise Exception('Incorrect timestamp of sent message.\nSent Timestamp: {sent_datetime}\nMessage: {message}'.format(
                                sent_datetime=sent_datetime, message=message)) from e