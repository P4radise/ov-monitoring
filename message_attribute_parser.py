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
        if not self._value_regexp:
            return value

        value_part_list = re.findall(self._value_regexp, value)
        if not value_part_list:
            value_part = ''
        else:
            try:
                value_part = value_part_list[0]
            except Exception as e:
                raise IntegrationError('Cannot get value part. Value regexp = {}'.format(self._value_regexp), str(e))
        
        if not isinstance(value_part, str):
            raise IntegrationError('Value part is not a string.', 'Value = {}; Value regexp = {}'.format(value, self._value_regexp))
        return value_part

    def get_processed_value(self, aws_message):
        value = self.get_attribute_value(aws_message)
        processed_value = self.get_value_part(value)

        return self.formatted_value(processed_value)

    def is_timestamp(self):
        return self._datetime_format is not None

    def timestamp_to_datetime(self, value):
        try:
            sent_datetime = datetime.datetime.fromtimestamp(int(value) / 1000)
        except Exception as e:
            raise IntegrationError('Cannot converted timestamp to datetime. Timestamp = {}'.format(value), str(e))
    
        return sent_datetime.strftime(self._datetime_format)

    def formatted_value(self, value):
        #TODO add cast to different formats if need
        return self.timestamp_to_datetime(value) if self.is_timestamp() else value