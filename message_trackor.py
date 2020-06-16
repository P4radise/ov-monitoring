import onevizion
from integration_error import IntegrationError


class MessageTrackor:

    def __init__(self, url, access_key, secret_key, trackor_type, message_body_field, sent_datetime_field, ov_token):
        self._url = url
        self._access_key = access_key
        self._secret_key = secret_key
        self._trackor_type = trackor_type
        self._ov_token = ov_token

        self._message_body_field = message_body_field
        self._sent_datetime_field = sent_datetime_field

        self._trackor = onevizion.Trackor(self._trackor_type, self._url, self._access_key, self._secret_key, ovToken=ov_token)

    def create_trackor(self, message_body, sent_datetime):
        fields = {
            self._message_body_field : message_body,
            self._sent_datetime_field : sent_datetime
        }
        
        self._trackor.create(fields)
        if len(self._trackor.errors) > 0:
            raise IntegrationError('Cannot create Trackor', self._trackor.errors)
    
        return self._trackor.jsonData