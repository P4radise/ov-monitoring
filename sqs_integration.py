from integration_log import LogLevel
from message_queue_service import MessageQueueService
from message_trackor_management import MessageTrackorManagement, Parser
from message_trackor_service import MessageTrackorService


class Integration(object):
    ITERATION_MAX_NUM = 200

    def __init__(self, ov_auth, ov_integration_log, aws_auth, queue_url, 
                    message_trackors_management, wait_time_seconds):
        self._integration_log = ov_integration_log
        self._message_queue_service = MessageQueueService(aws_auth, queue_url, wait_time_seconds)
        self._parser = Parser(message_trackors_management)

    def start(self):
        self._integration_log.add(LogLevel.INFO, 'Starting Integration')

        iteration_count = 0
        while iteration_count < Integration.ITERATION_MAX_NUM:
            self._integration_log.add(LogLevel.INFO, 'Receiving messages from the SQS queue')

            aws_messages = self._message_queue_service.get_messages()
            if not aws_messages:
                break

            for aws_message in aws_messages:
                self._integration_log.add(LogLevel.DEBUG, 'Message from SQS queue', 'Message:\n{}'.format(aws_message.message))

                message_trackors_data = self._parser.get_message_trackors_data(aws_message)
                for message_trackor_data in message_trackors_data:
                    trackor_service = message_trackor_data.trackor_service
                    is_need_update = message_trackor_data.is_need_update
                    self.trackor_actions(aws_message, trackor_service, is_need_update)

                message_groups_settings = self._parser.get_message_groups_settings(aws_message)
                for message_group_settings in message_groups_settings:
                    message_group_settings.update_groups(aws_message)


                self._message_queue_service.delete_message(aws_message.get_attribute_value(['ReceiptHandle']))
                self._integration_log.add(LogLevel.INFO, 'Message deleted from SQS queue', 'Message:\n{}'.format(aws_message.message))
                
            iteration_count += 1

        if iteration_count == 0:
            self._integration_log.add(LogLevel.WARNING, 'No new messages found')
        elif iteration_count == Integration.ITERATION_MAX_NUM:
            self._integration_log.add(LogLevel.WARNING,
                                        'The number of messages is large or messages are sent more often than the integration has time to complete')
        else:
            self._integration_log.add(LogLevel.INFO, 'No messages')


        group_trackors_data = self._parser.get_group_trackors_data()
        for group_trackor_data in group_trackors_data:
            trackor_service = group_trackor_data.trackor_service
            is_need_update_trackor = group_trackor_data.is_need_update

            messages_groups = group_trackor_data.messages_groups
            for messages_group in messages_groups:
                self.trackor_actions(messages_group, trackor_service, is_need_update_trackor)

        self._integration_log.add(LogLevel.INFO, 'Integration has been completed')

    def trackor_actions(self, data, trackor_service, is_need_update):
        if is_need_update:
            self.update_trackors(trackor_service, data)
        else:
            new_trackor = trackor_service.create_trackor(data)
            self._integration_log.add(LogLevel.INFO, 
                                    'Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                    trackor_id=str(new_trackor['TRACKOR_ID']), trackor_key=new_trackor['TRACKOR_KEY']))

    # data - instance of AmazonMessage or Group class
    def update_trackors(self, message_trackor_service, data):
        found_trackors_data = message_trackor_service.find_trackors(data)
        if len(found_trackors_data) == 0:
            self._integration_log.add(LogLevel.WARNING, 'Trackors not found')

        for trackor_data in found_trackors_data:
            updated_trackor = message_trackor_service.update_specific_trackor(trackor_data['TRACKOR_ID'], data)
        
            self._integration_log.add(LogLevel.INFO, 
                                    'Trackor updated.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                    trackor_id=str(updated_trackor['TRACKOR_ID']), trackor_key=updated_trackor['TRACKOR_KEY']))