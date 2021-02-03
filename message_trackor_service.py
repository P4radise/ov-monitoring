import json
import onevizion
from curl import Curl
from integration_error import IntegrationError
from integration_log import HTTPBearerAuth
from message_group import Group


class MessageTrackorService:
    def __init__(self, ov_auth, trackor_type, field_mappings, trackor_filter):
        self._ov_auth = ov_auth
        self._trackor = onevizion.Trackor(trackor_type, ov_auth.url, ov_auth.access_key, ov_auth.secret_key, ovToken=ov_auth.is_token_auth)
        self._field_mappings = field_mappings
        self._trackor_filter = trackor_filter

    # data - instance of AmazonMessage or Group class
    def create_trackor(self, data):
        fields = self._field_mappings.get_ready_fields_mapping(data)
        self._trackor.create(fields)
        if len(self._trackor.errors) > 0:
            raise IntegrationError('Cannot create Trackor', self._trackor.errors)
    
        return self._trackor.jsonData

    # data - instance of AmazonMessage or Group class
    def update_specific_trackor(self, trackor_id, data):
        headers = {'content-type': 'application/json'}
        url = 'https://' + self._ov_auth.url + '/api/v3/trackors/' + str(trackor_id)
        fields = self._field_mappings.get_ready_fields_mapping(data)

        curl = Curl('PUT', url, headers=headers, auth=HTTPBearerAuth(self._ov_auth.access_key, self._ov_auth.secret_key), data=json.dumps(fields))
        if len(curl.errors) > 0:
            raise Exception(curl.errors)
        
        return curl.jsonData

    # data - instance of AmazonMessage or Group class
    def find_trackors(self, data):
        search_conditions = self._trackor_filter.get_ready_search_conditions(data)

        self._trackor.read(search=search_conditions, fields=['xitor_key'])
        if len(self._trackor.errors) > 0:
            raise IntegrationError('Error while filtering existing trackors', self._trackor.errors)
        
        return self._trackor.jsonData


class TrackorFilter:

    def __init__(self, search_conditions, search_conditions_params):
        self._search_conditions = search_conditions
        self._search_conditions_params = search_conditions_params

    # data - instance of AmazonMessage or Group class
    def get_ready_search_conditions(self, data):
        ready_serach_conditions = self._search_conditions
        
        if not self._search_conditions_params:
            return ready_serach_conditions

        for param_name, param_value_settings in self._search_conditions_params.items():
            if isinstance(data, Group):
                group_value_name = param_value_settings['group_value_name']
                value = data.key_value if group_value_name == 'groupBy' else data.values[group_value_name]
            else:
                value = param_value_settings.get_processed_value(data)

            ready_serach_conditions = ready_serach_conditions.replace(':' + param_name, value)
        return ready_serach_conditions


class FieldMappings:
    def __init__(self, fields_values):
        self._fields_values = fields_values
    
    # data - instance of AmazonMessage or Group class
    def get_ready_fields_mapping(self, data):
        fields = {}
        for ov_field_name,value_data in self._fields_values.items():
            if isinstance(data, Group):
                group_value_name = value_data['group_value_name']
                fields[ov_field_name] = data.key_value if group_value_name == 'groupBy' else data.values[group_value_name]
            else:
                fields[ov_field_name] = value_data.get_processed_value(data)
        
        return fields