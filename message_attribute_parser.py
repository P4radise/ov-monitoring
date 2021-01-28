import re
import datetime
from integration_error import IntegrationError

class MessagesAttributeParser:

    def __init__(self, sqs_attribute, value_regexp, datetime_format):
        self._sqs_attribute = sqs_attribute
        self._value_regexp = value_regexp
        self._datetime_format = datetime_format
    
    def get_attribute_value(self, aws_message):
        attributes = self._sqs_attribute.split('.')
        return aws_message.get_attribute_value(attributes)

    def get_value_part(self, value):
        try:
            value_part = re.findall(self._value_regexp, value)[0]
        except Exception as e:
            raise IntegrationError('Cannot get value part. Value regexp = {}'.format(self._value_regexp), str(e))
        
        if not isinstance(value_part, str):
            raise IntegrationError('Value part is not a string.', 'Value = {}; Value regexp = {}'.format(value, self._value_regexp))
        return value_part

    def get_processed_value(self, aws_message):
        value = self.get_attribute_value(aws_message)
        processed_value = self.get_value_part(value) if self._value_regexp else value

        if self.is_datetime():
            try:
                sent_datetime = datetime.datetime.fromtimestamp(int(processed_value) / 1000)
            except Exception as e:
                raise IntegrationError('Cannot converted timestamp to datetime. Timestamp = {}'.format(processed_value), str(e))
        
            processed_value = sent_datetime.strftime(self._datetime_format)

        return processed_value

    def is_datetime(self):
        return self._datetime_format is not None