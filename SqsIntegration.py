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
        self._exception_handling = ExceptionHandling()

    def start(self):
        self._integration_log.add_log(LogLevel.INFO, 'Starting Integration')

        iteration_count = 0
        while iteration_count < Integration.ITERATION_MAX_NUM:
            self._integration_log.add_log(LogLevel.INFO, 'Receiving messages from the SQS queue')
            try:
                messages = self._message_queue_service.get_messages()
            except Exception as e:
                description = self._exception_handling.get_description(e, MessageQueueService.SYSTEM_NAME)
                self.integration_stop(e, LogLevel.ERROR, 'Cannot get messages from SQS queue', description)

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
                    description = self._exception_handling.get_description(e, MessageTrackor.SYSTEM_NAME)
                    self.integration_stop(e, LogLevel.ERROR, 'Cannot Trackor create', description)

                self._integration_log.add_log(LogLevel.INFO, 
                                            'Trackor created.\nTrackor Id = {trackor_id}\nTrackor Key = {trackor_key}'.format(
                                            trackor_id=str(trackor['TRACKOR_ID']), trackor_key=trackor['TRACKOR_KEY']))
                
                try:
                    self._message_queue_service.delete_message(message)
                except Exception as e:
                    description = self._exception_handling.get_description(e, MessageQueueService.SYSTEM_NAME)
                    self.integration_stop(e, LogLevel.ERROR, 'Cannot remove message from SQS queue', description)

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


class ExceptionHandling:
    comments = {
        401: 'Please make sure that the Access and Private keys of {system} user are correct, also that the token is active.',
        403: 'Please check the privileges of {system} user created for integration, also pay attention to the token.',
        404: 'Please take a look at the file with the integration settings, make sure that {system} param are filled correctly.'
    }

    def get_comment(self, status_code, system):
        status_code = int(status_code)
        if int(status_code) in ExceptionHandling.comments:
            return ExceptionHandling.comments[status_code].format(system=system)
        else:
            return ''
    
    def get_description(self, exc, system_name):
        error_message = str(exc)

        try:
            status_code = exc.response['ResponseMetadata']['HTTPStatusCode']
        except Exception:
            status_code = -1

        if status_code == -1 and hasattr(exc.args[0], 'status_code'):
            status_code = exc.args[0].status_code
            error_message = exc.args[0].text
        
        description = self.get_comment(status_code, system=system_name)
        if description == '':
            return error_message
        else:
            return '{description}\n{error}'.format(description=description, error=error_message)