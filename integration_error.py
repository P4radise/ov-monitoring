class IntegrationError(Exception):
    def __init__(self, error_message, description):
        self._message = error_message
        self._description = description

    @property
    def message(self):
        return self._message

    @property
    def description(self):
        return self._description