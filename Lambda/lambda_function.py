import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    print("Incoming Event:", json.dumps(event))

    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-1:767828767751:AthenaQueryNotificationTopic'

    try:
        # Check if it's an S3 Event
        if "Records" in event and event["Records"][0].get("eventSource") == "aws:s3":
            record = event["Records"][0]
            bucket_name = record["s3"]["bucket"]["name"]
            object_key = record["s3"]["object"]["key"]
            event_time = record["eventTime"]

            subject = "📦 S3 Bucket Update"
            message = (
                f"🧠 S3 bucket event received.\n\n"
                f"🪣 Bucket: {bucket_name}\n"
                f"📁 Object: {object_key}\n"
                f"🕒 Timestamp: {event_time}"
            )

        # Check if it's an Athena Event via EventBridge
        elif "detail-type" in event and event["detail-type"] == "Athena Query State Change":
            detail = event["detail"]
            query_id = detail.get("queryExecutionId", "Unknown")
            status = detail.get("currentState", "Unknown")
            region = event.get("region", "us-east-1")
            account_id = event.get("account", "Unknown")

            subject = f"🧠 Athena Query {status.title()}"
            message = (
                f"🎯 Athena Query Notification\n\n"
                f"✅ Query Execution ID: {query_id}\n"
                f"📊 Status: {status}\n"
                f"🔗 Console Link: https://{region}.console.aws.amazon.com/athena/home?region={region}#query/history/{query_id}"
            )

        # If neither, treat it as a fallback or unknown
        else:
            subject = "⚠️ Unknown Event Received"
            message = json.dumps(event, indent=2)

        # Send SNS
        response = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )

        print("SNS Response:", response)

        return {
            'statusCode': 200,
            'body': json.dumps('Notification sent.')
        }

    except Exception as e:
        print("Error while handling the event:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
