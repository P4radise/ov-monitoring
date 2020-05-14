from integration_log import IntegrationLog, LogLevel
from message_queue_service import MessageQueueService
from message_trackor import MessageTrackor


class Integration(object):
    ITERATION_MAX_NUM = 200

    def __init__(self, ov_url, ov_access_key, ov_secret_key, ov_trackor_type, process_id, ov_integration_name,
                    aws_access_key_id, aws_secret_access_key, aws_region, queue_url, 
                    message_body_field, sent_datetime_field, wait_time_seconds):

        self._message_queue_service = MessageQueueService(aws_access_key_id, aws_secret_access_key, aws_region,
                                                            queue_url, wait_time_seconds)
        self._integration_log = IntegrationLog(process_id, ov_url, ov_access_key, ov_secret_key,
                                                ov_integration_name, ov_token=True)
        self._message_trackor = MessageTrackor(ov_url, ov_access_key, ov_secret_key, 
                                                ov_trackor_type, message_body_field, sent_datetime_field, ov_token=True)

    def start(self):
        self._integration_log.add_log(LogLevel.INFO, 'Starting Integration')

        iteration_count = 0
        while iteration_count < Integration.ITERATION_MAX_NUM:
            self._integration_log.add_log(LogLevel.INFO, 'Receiving messages from the SQS queue')
            try:
                messages = self._message_queue_service.get_messages()
            except Exception as e:
                self.integration_stop(e, LogLevel.ERROR, 'Cannot get messages from SQS queue', str(e))

            if messages is None:
                break

            for message in messages:
                self._integration_log.add_log(LogLevel.DEBUG, 'Message from SQS queue', 'Message:\n{}'.format(message))
                
                try:
                    message_body = self._message_queue_service.get_message_param(message, 'Body')
                except Exception as e:
                    self.integration_stop(e, LogLevel.ERROR, 'Cannot get body of message', str(e))
                
                self._integration_log.add_log(LogLevel.DEBUG, 'Message Body = {}'.format(message_body))

                try:
                    sent_datetime = self._message_queue_service.get_sent_datetime(message)
                except Exception as e:
                    self.integration_stop(e, LogLevel.ERROR, 'Cannot get sent datetime of message', str(e))

                self._integration_log.add_log(LogLevel.DEBUG, 'Sent timestamp of message = {}'.format(sent_datetime))

                try:
                    trackor = self._message_trackor.create_trackor(message_body, sent_datetime)
                except Exception as e:
                    self.integration_stop(e, LogLevel.ERROR, 'Cannot create Trackor', str(e))

                self._integration_log.add_log(LogLevel.INFO, 
                                            'Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                            trackor_id=str(trackor['TRACKOR_ID']), trackor_key=trackor['TRACKOR_KEY']))
                
                try:
                    self._message_queue_service.delete_message(message)
                except Exception as e:
                    self.integration_stop(e, LogLevel.ERROR, 'Cannot remove message from SQS queue', str(e))

                self._integration_log.add_log(LogLevel.INFO, 'Message deleted from SQS queue', 'Message: {}'.format(message))
                
            iteration_count += 1

        if iteration_count == 0:
            self._integration_log.add_log(LogLevel.WARNING, 'No new messages found')
        elif iteration_count == Integration.ITERATION_MAX_NUM:
            self._integration_log.add_log(LogLevel.WARNING,
                                        'The number of messages is large or messages are sent more often than the integration has time to complete')
        else:
            self._integration_log.add_log(LogLevel.INFO, 'No messages')
            
        self._integration_log.add_log(LogLevel.INFO, 'Integration has been completed')

    def integration_stop(self, e, log_level, message, description):
        self._integration_log.add_log(log_level, message, description)
        raise Exception(message) from e