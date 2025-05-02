{
  "Comment": "An example demonstrating Glue Crawler + Athena + SNS notification",
  "StartAt": "Start Crawler",
  "States": {
    "Start Crawler": {
      "Type": "Task",
      "Next": "Get Crawler status",
      "Parameters": {
        "Name": "nyc-fleet-crawler"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:startCrawler"
    },
    "Get Crawler status": {
      "Type": "Task",
      "Next": "Check Crawler status",
      "Parameters": {
        "Name": "nyc-fleet-crawler"
      },
      "Resource": "arn:aws:states:::aws-sdk:glue:getCrawler"
    },
    "Check Crawler status": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.Crawler.State",
          "StringEquals": "RUNNING",
          "Next": "Wait"
        }
      ],
      "Default": "Start an Athena query"
    },
    "Wait": {
      "Type": "Wait",
      "Seconds": 30,
      "Next": "Get Crawler status"
    },
    "Start an Athena query": {
      "Type": "Task",
      "Next": "Get query results",
      "Parameters": {
        "QueryString": "SELECT * FROM nyc_fleet_bucket LIMIT 10",
        "WorkGroup": "primary",
        "QueryExecutionContext": {
          "Database": "nyc_fleet_db"
        },
        "ResultConfiguration": {
          "OutputLocation": "s3://nyc-fleet-bucket/query_results/"
        }
      },
      "Resource": "arn:aws:states:::athena:startQueryExecution.sync"
    },
    "Get query results": {
      "Type": "Task",
      "Next": "Send query results",
      "Parameters": {
        "QueryExecutionId.$": "$.QueryExecution.QueryExecutionId"
      },
      "Resource": "arn:aws:states:::athena:getQueryResults"
    },
    "Send query results": {
      "Type": "Task",
      "End": true,
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:767828767751:AthenaQueryNotificationTopic",
        "Message.$": "$.ResultSet.Rows"
      },
      "Resource": "arn:aws:states:::sns:publish"
    }
  }
}
