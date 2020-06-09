import datetime
import re

class AmazonMessage:

    def __init__(self, message):
        self._message = message
    
    def get_body(self):
        try:
            return self._message['Body']
        except Exception as e:
            raise Exception('Cannot get body of message',
                            'Incorrect message structure from SQS.\nParameter "Body"  not found in {message}'.format(
                                message=self._message)) from e

    def get_sent_datetime(self):
        try:
            sent_timestamp = self._message['Attributes']['SentTimestamp']
        except Exception as e:
            raise Exception('Cannot get sent datetime of message', 
                            'Incorrect message structure from SQS.\nParameter "SentTimestamp" not found in Message Attributes \nMessage: {}'.format(
                                self._message)) from e
        try:
            sent_datetime = datetime.datetime.fromtimestamp(int(sent_timestamp) / 1000)
            return sent_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            raise Exception('Cannot get sent datetime of message',
                            'Incorrect timestamp of sent message.\nSent Timestamp: {sent_datetime}\nMessage: {message}'.format(
                                sent_datetime=sent_datetime, message=self._message)) from e
    
    def get_receipt_handle(self):
        try:
             return self._message['ReceiptHandle']
        except Exception as e:
            raise Exception('Cannot remove message from SQS queue',
                            'Incorrect message structure from SQS.\nParameter "ReceiptHandle" not found in Message. \nMessage: {}'.format(
                                self._message)) from e

    def matches_filter(self, filter):
        return re.fullmatch(filter, self.get_body()) != None