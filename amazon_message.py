import datetime
import re

class AmazonMessage:

    def __init__(self, message):
        self._message = message
    
    @property
    def message(self):
        return self._message

    def get_body(self):
        return self._message['Body']

    def get_sent_datetime(self):
        sent_timestamp = self._message['Attributes']['SentTimestamp']

        sent_datetime = datetime.datetime.fromtimestamp(int(sent_timestamp) / 1000)
        return sent_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    
    def get_receipt_handle(self):
        return self._message['ReceiptHandle']

    def matches_filter(self, filter):
        return re.fullmatch(filter, self.get_body()) is not None