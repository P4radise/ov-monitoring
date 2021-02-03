# SqsIntegration

Read messages from the AWS SQS and store to the OneVizion Trackors.

## Requirements
- Python 3.7
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
   - ovUrl* - OneVizion URL
   - ovAccessKey* - OneVizion Access Key
   - ovSecretKey* - OneVizion Secret Key
   - ovIntegrationName* - Integration Name in OneVizion Trackor

   Parameters that are used together to get the desired message attribute value. Below they are named MessageAtributeValue:
    * sqsAttribute* - sqs message attribute name. The dot between attribute names means they are nested. Structure of the received sqs message can be seen in the section [receive_message -> Response Syntax](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.receive_message) 
    * valueRegexp - regular expression that is used to get a substring of sqs message attribute value. The absence of this parameter will mean that sqs message attribute value will be used in full. [Regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax)
    * dateTimeFormat - datetime format for converting datetime to string. [Format Codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

   Parameters continued:
    - createTrackors - List that contains at least one object. Use to creating tractors. The absence of this parameter will mean that tractors will not be created:
        - messageFilter - object. The absence of this parameter will mean that the filter is not used and Trackors will be created for all messages. Object can contain:
            - filterRegexp* - Regular expression. A Trackor for the message will be created if the message matches this regular expression. [Regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax)
            - MessageAtributeValue*
        - trackorType* - Trackor Type for adding received messages
        - fieldMappings* - List that contains at least one object. Used to map values to fields on Trackor. Object can contain:
            - ovField* - Field name, received value will be added to this field 
            - MessageAtributeValue - value to add to field.

   - updateTrackors - List that contains at least one object. Use to updating tractors. The absence of this parameter will mean that tractors will not be updated.
        - messageFilter - object. The absence of this parameter will mean that the filter is not used and Trackors will be updated for all messages. See more in createTrackors
        - trackorType* - Trackor Type. Trackors of this type will be updated
        - fieldMappings* - See more in createTrackors
        - trackorFilter* - object. Parameters in it determine which Trackors need to be updated, using the received message. Object contains:
            - searchConditions* - search string. More details can be found in the API documentation in the trackors section in Search Trackors. Parameter names are used instead of values
            - searchConditionsParams - objects list. Object contains:
                - paramName - parameter name. It must be written instead of values in searchConditions
                - groupValueName - an object that contains MessageAtributeValue. ParamName in searchConditions will be replaced with message attribute value

    MessageGroup parameter is added to createTrackors or updateTrackors to get values for a message group:
    - messageGroup - object. It contains:
        - groupBy* - an object that contains MessageAtributeValue. Messages will be grouped by this value.
        - values* - List that contains at least one object. Used to calculate message attribute values by message groups. Object contains:
            - valueName* - value name. It will be used in other parameters
            - function* - aggregate function for calculating values. While only max or min are available.
            - value* - an object that contains MessageAtributeValue. using this, the message attribute values will be obtained for further calculation by groups
    After adding messageGroup, be sure to replace MessageAtributeValue in other parameters with the value in valueName.

   - awsAccessKeyId* - AWS Access Key ID
   - awsSecretAccessKey* - AWS Secret Access Key
   - awsRegion* - AWS Region.
   - queueUrl* - URL of created Queue
   
   - waitTimeSeconds - The duration (in seconds from 0 to 20) for which the call to receive a message waits for a message to arrive in the queue before returning. [Amazon SQS short and long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html)
   
6. Enable the integration

Example of settings.json

```json
{
    "ovUrl": "https://test.onevizion.com",
    "ovAccessKey": "*****",
    "ovSecretKey": "*****",
    "ovIntegrationName": "SqsIntegration",

    "createTrackors": [{
        "messageFilter": {
            "filterRegexp": "(?s)(((?!\"status\")|\"status\":\"(?!OK\")).)*",
            "sqsAttribute": "Body"
        },
        "trackorType": "Trackor Type",
        "fieldMappings": [{
                "ovField": "Field Name",
                "sqsAttribute": "Body"
            }, {
                "ovField": "Field Name",
                "sqsAttribute": "Attributes.SentTimestamp",
                "dateTimeFormat": "%Y-%m-%dT%H:%M:%S"
            }
        ]
    }],

    "updateTrackors": [{
        "messageGroup": {
            "groupBy": {
                "sqsAttribute": "Body",
                "valueRegexp": "(?<=\"install\":\").*?(?=\")"
            },
            "values": [{
                "valueName": "maxSentTimestamp",
                "function": "max",
                "value": {
                    "sqsAttribute": "Attributes.SentTimestamp",
                    "dateTimeFormat": "%Y-%m-%dT%H:%M:%S"
                }
            }]
        },
        "trackorType": "Trackor Type",
        "trackorFilter": {
            "searchConditions": "equal(Field Name, \":value1\") and less(Field Name, :value2)",
            "searchConditionsParams": [{
                    "paramName": "value1",
                    "groupValueName": "groupBy"
                }, {
                    "paramName": "value2",
                    "groupValueName": "maxSentTimestamp"
                }
            ]
        },
        "fieldMappings": [{
                "ovField": "Field Name",
                "groupValueName": "maxSentTimestamp"
            }
        ]
    }],

    "awsAccessKeyId": "*****",
    "awsSecretAccessKey": "*****",
    "awsRegion": "us-east-2",
    "queueUrl" : "https://sqs.us-east-2.amazonaws.com/788508682010/Test",

    "waitTimeSeconds" : 10
}
```