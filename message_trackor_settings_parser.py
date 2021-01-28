from message_trackor import MessageTrackor, MessageFilter, TrackorFilter, FieldMappings
from message_attribute_parser import MessagesAttributeParser


class MessageTrackorSettingsParser:

    @staticmethod
    def get_message_trackors(message_trackor_settings, is_update_trackor, ov_auth):
        message_trackors = []
        for settings_data in message_trackor_settings:
            message_filter = MessageTrackorSettingsParser.get_message_filter(settings_data["messageFilter"]) if "messageFilter" in settings_data else None
            trackor_type = settings_data["trackorType"]
            field_mappings = MessageTrackorSettingsParser.get_field_mappings(settings_data["fieldMappings"])

            if is_update_trackor and "trackorFilter" in settings_data:
                trackor_filter_settings = settings_data["trackorFilter"]
                search_conditions_params = MessageTrackorSettingsParser.get_search_conditions_params(trackor_filter_settings["searchConditionsParams"]) if "searchConditionsParams" in trackor_filter_settings else None

                trackor_filter = TrackorFilter(trackor_filter_settings["searchConditions"], search_conditions_params)
            else:
                trackor_filter = None

            massage_trackor = MessageTrackor(ov_auth, trackor_type, message_filter, field_mappings, trackor_filter)
            message_trackors.append(massage_trackor)

        return message_trackors

    @staticmethod
    def get_messages_attribute_value(data):
        sqs_attribute = data["sqsAttribute"]
        value_regexp = data["valueRegexp"] if "valueRegexp" in data else None
        datetime_format = data["dateTimeFormat"] if "dateTimeFormat" in data else None

        return MessagesAttributeParser(sqs_attribute, value_regexp, datetime_format)

    @staticmethod
    def get_message_filter(message_filter_data):
        messages_attribute_value = MessageTrackorSettingsParser.get_messages_attribute_value(message_filter_data)
        return MessageFilter(message_filter_data["filterRegexp"], messages_attribute_value)
        
    @staticmethod
    def get_field_mappings(field_mappings_settings):
        field_mappings_data = {}
        for field_mapping in field_mappings_settings:
            ov_field_name = field_mapping["ovField"]
            messages_attribute_value = MessageTrackorSettingsParser.get_messages_attribute_value(field_mapping)
            field_mappings_data[ov_field_name] = messages_attribute_value

        return FieldMappings(field_mappings_data)

    @staticmethod
    def get_search_conditions_params(search_conditions_params_settings):
        search_conditions_params = {}
        for param in search_conditions_params_settings:
            param_name = param["paramName"]
            attribute_value = MessageTrackorSettingsParser.get_messages_attribute_value(param)
            search_conditions_params[param_name] = attribute_value

        return search_conditions_params