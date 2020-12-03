from integration_log import LogLevel
from message_queue_service import MessageQueueService
from message_trackor import MessageTrackor


class Integration(object):
    ITERATION_MAX_NUM = 200

    def __init__(self, ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id, ov_integration_log,
                    aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                    message_body_field, sent_datetime_field, message_filter, wait_time_seconds):
        self._message_filter = message_filter
        self._integration_log = ov_integration_log

        self._message_queue_service = MessageQueueService(aws_access_key_id, aws_secret_access_key, aws_region,
                                                            queue_url, wait_time_seconds)
        self._message_trackor = MessageTrackor(ov_url, ov_access_key, ov_secret_key, 
                                                ov_trackor_type, message_body_field, sent_datetime_field)

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
                
                message_body = aws_message.get_body()
                self._integration_log.add(LogLevel.DEBUG, 'Message Body = {}'.format(message_body))

                is_matched_with_filter = True if self._message_filter is None else aws_message.matches_filter(self._message_filter)

                if is_matched_with_filter:
                    sent_datetime = aws_message.get_sent_datetime()
                    self._integration_log.add(LogLevel.DEBUG, 'Sent timestamp of message = {}'.format(sent_datetime))

                    trackor = self._message_trackor.create_trackor(message_body, sent_datetime)

                    self._integration_log.add(LogLevel.INFO, 
                                                'Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                                trackor_id=str(trackor['TRACKOR_ID']), trackor_key=trackor['TRACKOR_KEY']))
                else:
                    self._integration_log.add(LogLevel.INFO, 
                                        'Message does not match filter specified in the settings file', 
                                        'Message Body = {}'.format(message_body))
                    
                self._message_queue_service.delete_message(aws_message.get_receipt_handle())
                self._integration_log.add(LogLevel.INFO, 'Message deleted from SQS queue', 'Message: {}'.format(aws_message.message))
                
            iteration_count += 1

        if iteration_count == 0:
            self._integration_log.add(LogLevel.WARNING, 'No new messages found')
        elif iteration_count == Integration.ITERATION_MAX_NUM:
            self._integration_log.add(LogLevel.WARNING,
                                        'The number of messages is large or messages are sent more often than the integration has time to complete')
        else:
            self._integration_log.add(LogLevel.INFO, 'No messages')
            
        self._integration_log.add(LogLevel.INFO, 'Integration has been completed')