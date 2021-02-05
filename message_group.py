from dataclasses import dataclass
from integration_error import IntegrationError


class MessageGroupManager:

    def __init__(self, group_by_settings, values_settings):
        self._group_by_settings = group_by_settings
        self._values_settings = values_settings

        #[Group, ...]
        self._groups = []

    def update_groups(self, aws_message):
        message_group_key_value = self._group_by_settings.get_processed_value(aws_message)
        suitable_group = self.get_group(message_group_key_value)

        for value_settings in self._values_settings:
            value_settings.update_group_value(suitable_group, aws_message)

    def get_group(self, message_group_key_value):
        for group in self._groups:
            if group.key_value == message_group_key_value:
                return group
        
        new_group = Group(key_value=message_group_key_value, values={})
        self._groups.append(new_group)
        return new_group

    @property
    def groups(self):
        return self._groups
    
    def get_formatted_groups(self):
        for group in self._groups:
            for value_settings in self._values_settings:
                value_settings.formatted_value(group)
        
        return self._groups
        

class GroupValuesManager:
    # TODO: add Count, Sum, Avg if needed
    OPERATIONS = {
        'min': lambda x,y: min(int(x), int(y)),
        'max': lambda x,y: max(int(x), int(y))
    }

    def __init__(self, value_name, function_name, value_data):
        self._value_name = value_name
        self._function_name = function_name
        self._value_data = value_data

    @property
    def value_name(self):
        return self._value_name

    @property
    def value_data(self):
        return self._value_data

    def update_group_value(self, group, aws_message):
        value = self._value_data.get_attribute_value(aws_message)
        message_value = self._value_data.get_value_part(value)

        if message_value:
            if self._value_name in group.values:
                group_value = group.values[self._value_name]
                group.values[self._value_name] = GroupValuesManager.OPERATIONS[self._function_name](group_value, message_value)
            else:
                group.values[self._value_name] = message_value

    def formatted_value(self, group):
        if self._value_name in group.values:
            group.values[self._value_name] = self._value_data.formatted_value(group.values[self._value_name])


@dataclass
class Group:
    key_value: str
    # {valueName: value, }
    values: dict