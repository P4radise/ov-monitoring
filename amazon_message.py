from integration_error import IntegrationError

class AmazonMessage:

    def __init__(self, message):
        self._message = message
    
    @property
    def message(self):
        return self._message

    def get_attribute_value(self, attribute_path):
        value = self._message
        try:
            for attribute in attribute_path:
                value = value[attribute]
        except Exception as e:
            raise IntegrationError('Cannot get message attribute value. Attribute [{}]'.format('. '.join(attribute_path)), str(e))

        return value
