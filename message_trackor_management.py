import re


class MessageTrackorManagement:
    def __init__(self, message_trackor_service, message_filter, messages_group_management, is_need_update):
        self._message_filter = message_filter
        self._message_trackor_service = message_trackor_service
        self._messages_group_management = messages_group_management
        self._is_need_update = is_need_update

    @property
    def message_trackor_service(self):
        return self._message_trackor_service

    @property
    def messages_group_management(self):
        return self._messages_group_management
    
    @property
    def is_need_update(self):
        return self._is_need_update

    def is_matched_with_filter(self, ams_message):
        return self._message_filter.is_matched_with_filter(ams_message) if self._message_filter else True


class MessageFilter:
    def __init__(self, filter_regexp, atrribute_value_parser):
        self._filter_regexp = filter_regexp
        self._attributes_value = atrribute_value_parser
    
    def is_matched_with_filter(self, ams_message):
        processed_value = self._attributes_value.get_processed_value(ams_message)
        return re.fullmatch(self._filter_regexp, processed_value) is not None


class Parser:
    def __init__(self, message_trackors_management):
        self._message_trackors_management = message_trackors_management

    def get_message_trackors_data(self, aws_message):
        message_trackors_data = []
        for message_trackor_management in self._message_trackors_management:
            if message_trackor_management.is_matched_with_filter(aws_message) and not message_trackor_management.messages_group_management:
                message_trackor = message_trackor_management._message_trackor_service
                is_need_update = message_trackor_management.is_need_update
                
                message_trackor_data = TrackorDataObject(message_trackor, is_need_update)
                message_trackors_data.append(message_trackor_data)
        return message_trackors_data

    def get_message_groups_settings(self, aws_message):
        message_groups_settings = []
        for message_trackor_management in self._message_trackors_management:
            if message_trackor_management.is_matched_with_filter(aws_message) and message_trackor_management.messages_group_management:
                message_groups_settings.append(message_trackor_management.messages_group_management)
        return message_groups_settings

    def get_group_trackors_data(self):
        group_trackors_data = []
        for message_trackor_management in self._message_trackors_management:
            if message_trackor_management.messages_group_management:
                message_trackor = message_trackor_management._message_trackor_service
                is_need_update = message_trackor_management.is_need_update

                messages_groups_management = message_trackor_management.messages_group_management
                message_groups = messages_groups_management.get_formatted_groups()
                
                group_trackor_data = TrackorDataObject(message_trackor, is_need_update, message_groups)
                group_trackors_data.append(group_trackor_data)
        return group_trackors_data


class TrackorDataObject:
    def __init__(self, trackor_service, is_need_update, messages_groups=None):
        self.trackor_service = trackor_service
        self.is_need_update = is_need_update
        self.messages_groups = messages_groups