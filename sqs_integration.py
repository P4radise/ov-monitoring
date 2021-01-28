from integration_log import LogLevel
from message_queue_service import MessageQueueService
from message_trackor import MessageTrackor


class Integration(object):
    ITERATION_MAX_NUM = 200

    def __init__(self, ov_auth, ov_integration_log, aws_auth, queue_url, 
                    message_trackors, wait_time_seconds):
        self._integration_log = ov_integration_log
        self._message_trackors = message_trackors
        self._message_queue_service = MessageQueueService(aws_auth, queue_url, wait_time_seconds)

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

                for message_trackor in self._message_trackors:
                    if message_trackor.is_matched_with_filter(aws_message):
                        if message_trackor.is_group_trackor():
                            message_trackor.update_group(aws_message)
                        else:
                            if message_trackor.is_update():
                                self.update_trackors(message_trackor, aws_message)
                            else:
                                new_trackor = message_trackor.create_trackor(aws_message)
                                self._integration_log.add(LogLevel.INFO, 
                                                    'Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                                    trackor_id=str(new_trackor['TRACKOR_ID']), trackor_key=new_trackor['TRACKOR_KEY']))
                    else:
                        self._integration_log.add(LogLevel.DEBUG, 'Message does not match the filter', 
                                                    'Message:\n{}'.format(aws_message.message))

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

        for message_trackor in self._message_trackors:
            if message_trackor.is_group_trackor():
                groups = message_trackor.get_groups()
                for group in groups:
                    if message_trackor.is_update():
                        self.update_trackors(message_trackor, group)
                    else:
                        new_trackor = message_trackor.create_trackor(group)
                        self._integration_log.add(LogLevel.INFO, 
                                                'Messages Group Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                                trackor_id=str(new_trackor['TRACKOR_ID']), trackor_key=new_trackor['TRACKOR_KEY']))

        self._integration_log.add(LogLevel.INFO, 'Integration has been completed')


    # data - instance of AmazonMessage or Group class
    def update_trackors(self, message_trackor, data):
        found_trackors_data = message_trackor.find_trackors(data)
        if len(found_trackors_data) == 0:
            self._integration_log.add(LogLevel.WARNING, 'Trackors not found')

        for trackor_data in found_trackors_data:
            updated_trackor = message_trackor.update_specific_trackor(trackor_data['TRACKOR_ID'], data)
        
            self._integration_log.add(LogLevel.INFO, 
                                    'Trackor updated.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                    trackor_id=str(updated_trackor['TRACKOR_ID']), trackor_key=updated_trackor['TRACKOR_KEY']))