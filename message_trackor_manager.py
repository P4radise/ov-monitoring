import re
from integration_log import LogLevel

class MessageTrackorManager:
    def __init__(self, message_trackor_service, message_filter, messages_group_manager, is_need_update, integration_log):
        self._message_filter = message_filter
        self._message_trackor_service = message_trackor_service
        self._messages_group_manager = messages_group_manager
        self._is_need_update = is_need_update
        self._integration_log = integration_log

    def is_matched_with_filter(self, ams_message):
        return self._message_filter.is_matched_with_filter(ams_message) if self._message_filter else True

    def process_message(self, aws_message):
        if self.is_matched_with_filter(aws_message):
            if self._messages_group_manager:
                self._messages_group_manager.update_groups(aws_message)
            else:
                self.create_or_update_trackors(aws_message)

    def process_groups(self):
        if self._messages_group_manager:
            messages_groups = self._messages_group_manager.get_formatted_groups()
            
            for messages_group in messages_groups:
                self.create_or_update_trackors(messages_group)

    def create_or_update_trackors(self, aws_message_or_group):
        if self._is_need_update:
            self.update_trackors(aws_message_or_group)
        else:
            new_trackor = self._message_trackor_service.create_trackor(aws_message_or_group)
            self._integration_log.add(LogLevel.INFO, 
                                    'Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                    trackor_id=str(new_trackor['TRACKOR_ID']), trackor_key=new_trackor['TRACKOR_KEY']))

    # aws_message_or_group - instance of AmazonMessage or Group class
    def update_trackors(self, aws_message_or_group):
        found_trackors_data = self._message_trackor_service.find_trackors(aws_message_or_group)
        if len(found_trackors_data) == 0:
            self._integration_log.add(LogLevel.WARNING, 'Trackors not found')

        for trackor_data in found_trackors_data:
            updated_trackor = self._message_trackor_service.update_specific_trackor(trackor_data['TRACKOR_ID'], aws_message_or_group)
        
            self._integration_log.add(LogLevel.INFO, 
                                    'Trackor updated.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                    trackor_id=str(updated_trackor['TRACKOR_ID']), trackor_key=updated_trackor['TRACKOR_KEY']))


class MessageFilter:
    def __init__(self, filter_regexp, atrribute_value_parser):
        self._filter_regexp = filter_regexp
        self._attributes_value = atrribute_value_parser
    
    def is_matched_with_filter(self, ams_message):
        processed_value = self._attributes_value.get_processed_value(ams_message)
        return re.fullmatch(self._filter_regexp, processed_value) is not None