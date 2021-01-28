import re
import json
import onevizion
from curl import Curl
from integration_error import IntegrationError
from integration_log import HTTPBearerAuth


class MessageTrackor:
    def __init__(self, ov_auth, trackor_type, message_filter, field_mappings, trackor_filter):
        self._message_filter = message_filter
        self._ov_auth = ov_auth
        self._trackor = onevizion.Trackor(trackor_type, ov_auth.url, ov_auth.access_key, ov_auth.secret_key, ovToken=ov_auth.is_token_auth)
        self._field_mappings = field_mappings
        self._trackor_filter = trackor_filter

    def is_matched_with_filter(self, ams_message):
        return self._message_filter.is_matched_with_filter(ams_message) if self._message_filter else True

    def create_trackor(self, aws_message):
        fields = self._field_mappings.get_ready_fields_mapping(aws_message)
        self._trackor.create(fields)
        if len(self._trackor.errors) > 0:
            raise IntegrationError('Cannot create Trackor', self._trackor.errors)
    
        return self._trackor.jsonData

    def update_trackor(self, trackor_id, aws_message):
        headers = {'content-type': 'application/json'}
        url = 'http://' + self._ov_auth.url + '/api/v3/trackors/' + str(trackor_id)
        fields = self._field_mappings.get_ready_fields_mapping(aws_message)

        curl = Curl('PUT', url, headers=headers, auth=HTTPBearerAuth(self._ov_auth.access_key, self._ov_auth.secret_key), data=json.dumps(fields))
        if len(curl.errors) > 0:
            raise Exception(curl.errors)
        
        return curl.jsonData

    def find_trackors(self, aws_message):
        search_conditions = self._trackor_filter.get_ready_search_conditions(aws_message)

        self._trackor.read(search=search_conditions, fields=['xitor_key'])
        if len(self._trackor.errors) > 0:
            raise IntegrationError('Error while filtering existing trackors', self._trackor.errors)
        
        return self._trackor.jsonData

class MessageFilter:
    def __init__(self, filter_regexp, atrribute_value_parser):
        self._filter_regexp = filter_regexp
        self._attributes_value = atrribute_value_parser
    
    def is_matched_with_filter(self, ams_message):
        processed_value = self._attributes_value.get_processed_value(ams_message)
        return re.fullmatch(self._filter_regexp, processed_value) is not None


class TrackorFilter:

    def __init__(self, search_conditions, search_conditions_params):
        self._search_conditions = search_conditions
        self._search_conditions_params = search_conditions_params

    def get_ready_search_conditions(self, aws_message):
        ready_serach_conditions = self._search_conditions
        
        if not self._search_conditions_params:
            return ready_serach_conditions

        for param_name in self._search_conditions_params:
            search_conditions_param = self._search_conditions_params[param_name]
            value = search_conditions_param.get_processed_value(aws_message)

            ready_serach_conditions = ready_serach_conditions.replace(':' + param_name, value)
        return ready_serach_conditions

class FieldMappings:
    def __init__(self, fields_values):
        self._fields_values = fields_values
    
    def get_ready_fields_mapping(self, aws_message):
        fields = {}
        for ov_field_name in self._fields_values:
            fields[ov_field_name] = self._fields_values[ov_field_name].get_processed_value(aws_message)
        
        return fields