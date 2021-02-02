from integration_log import LogLevel
from message_queue_service import MessageQueueService
from message_trackor_manager import MessageTrackorManager
from message_trackor_service import MessageTrackorService


class Integration(object):
    ITERATION_MAX_NUM = 200

    def __init__(self, ov_auth, ov_integration_log, aws_auth, queue_url, 
                    message_trackors_managers, wait_time_seconds):
        self._integration_log = ov_integration_log
        self._message_queue_service = MessageQueueService(aws_auth, queue_url, wait_time_seconds)
        self._message_trackors_managers = message_trackors_managers

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

                for message_trackors_manager in self._message_trackors_managers:
                    message_trackors_manager.parse_message(aws_message)

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

        for message_trackors_manager in self._message_trackors_managers:
            message_trackors_manager.process_groups()

        self._integration_log.add(LogLevel.INFO, 'Integration has been completed')