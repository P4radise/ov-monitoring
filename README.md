# SqsIntegration

Read messages from the AWS SQS and store to the OneVizion Trackors.

## Requirements
- Python 3
- Requests - [library for python](https://requests.readthedocs.io/en/master/)
- boto3 - [Boto is the Amazon Web Services (AWS) SDK for Python](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- jsonschema - [Implementation of JSON Schema for Python](https://python-jsonschema.readthedocs.io/en/stable/)

## AWS Configuration
1. Log into AWS console.
2. In SQS section, create a new separate standard Queue. [Creating an Amazon SQS queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-create-queue.html). It is recommended that you keep the default settings.
However, if you decide to change them, then pay special attention if the value of the Message Retention Period parameter is too small, then the message may be deleted before it is added to the OneVizion Trackors.
3. Configure sending messages to the created Queue. For example, messages can be generated using OneVizion monitoring.
4. Create an IAM policy using the json example below, where \<SQS ARN\> is [Amazon Resource Name](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) of the SQS created on step 2.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:DeleteMessage",
                "sqs:ReceiveMessage"
            ],
            "Resource": "<SQS ARN>"
        }
    ]
}
```

5. Create an IAM user and store credentials.
6. Attach this new IAM policy to the IAM user.


## Usage
1. Create Trackor Type that will store messages. In this Trackor Type there should be a field in which the received message will be stored, as well as a field in which the date and time of sending the message will be stored.
2. Install this integration
3. Create dedicated account for integration with following privs:
   * WEB_SERVICES R
   * ADMIN_INTEGRATION R
   * ADMIN_INTEGRATION_LOG RA
   * \<Trackor Type\> RA
   * \<Trackor Type Tab containing messageBodyField and sentDateTimeField\> RE
4. Create a token for the account created on step 3
5. Fill the integration settings file
   - ovUrl - OneVizion URL
   - ovAccessKey - OneVizion Access Key
   - ovSecretKey - OneVizion Secret Key
   - ovIntegrationName - Integration Name in OneVizion Trackor
   - trackorType - Trackor Type for adding received messages
   - messageBodyField - Field Name. The body of the received message will be inserted into this field. This field must belong to the Trackor Type you specified
   - sentDateTimeField - Field Name. The datetime the message was sent will be inserted into this field. This field must belong to the Trackor Type you specified 
   - messageFilter - Regular expression. A Trackor for the message will be created if the message matches this regular expression. null in the value of this param will mean that the filter is not used and Trackors will be created for all messages. [Regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax)

   - awsAccessKeyId - AWS Access Key ID
   - awsSecretAccessKey - AWS Secret Access Key
   - awsRegion - AWS Region.
   - queueUrl - URL of created Queue
   
   - waitTimeSeconds - The duration (in seconds from 0 to 20) for which the call to receive a message waits for a message to arrive in the queue before returning. [Amazon SQS short and long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html)
   
6. Enable the integration

Example of settings.json

```json
{
    "ovUrl": "test.onevizion.com",
    "ovAccessKey": "*****",
    "ovSecretKey": "*****",
    "ovIntegrationName": "SqsIntegration",
    "trackorType" : "Trackor Type",
    "messageBodyField" : "Field Name",
    "sentDateTimeField" : "Field Name",
    "messageFilter" : null,

    "awsAccessKeyId": "*****",
    "awsSecretAccessKey": "*****",
    "awsRegion": "us-east-2",
    "queueUrl" : "https://sqs.us-east-2.amazonaws.com/788508682010/Test",

    "waitTimeSeconds" : 10
}
```