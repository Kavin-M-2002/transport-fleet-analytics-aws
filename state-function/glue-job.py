{
  "Comment": "NYC Fleet Data Pipeline - Enhanced Notifications",
  "StartAt": "Start Glue Job",
  "States": {
    "Start Glue Job": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "nyc-data"
      },
      "Next": "Start Athena Query"
    },
    "Start Athena Query": {
      "Type": "Task",
      "Resource": "arn:aws:states:::athena:startQueryExecution",
      "Parameters": {
        "QueryString": "SELECT * FROM nyc_fleet_db.nyc_fleet_bucket LIMIT 10;",
        "QueryExecutionContext": {
          "Database": "nyc_fleet_db"
        },
        "ResultConfiguration": {
          "OutputLocation": "s3://nyc-fleet-bucket/query-results/"
        }
      },
      "Next": "Wait Before Check"
    },
    "Wait Before Check": {
      "Type": "Wait",
      "Seconds": 5,
      "Next": "Check Query Status"
    },
    "Check Query Status": {
      "Type": "Task",
      "Resource": "arn:aws:states:::athena:getQueryExecution",
      "Parameters": {
        "QueryExecutionId.$": "$.QueryExecutionId"
      },
      "Next": "Is Query Succeeded"
    },
    "Is Query Succeeded": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.QueryExecution.Status.State",
          "StringEquals": "SUCCEEDED",
          "Next": "NotifySuccess"
        },
        {
          "Variable": "$.QueryExecution.Status.State",
          "StringEquals": "FAILED",
          "Next": "NotifyFailure"
        }
      ],
      "Default": "Wait Before Check"
    },
    "NotifySuccess": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:767828767751:function:SendAthenaNotification",
      "Parameters": {
        "database": "nyc_fleet_db",
        "table": "nyc_fleet_bucket",
        "status": "Success",
        "timestamp.$": "$.QueryExecution.Status.SubmissionDateTime"
      },
      "End": true
    },
    "NotifyFailure": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:767828767751:function:SendAthenaNotification",
      "Parameters": {
        "database": "nyc_fleet_db",
        "table": "nyc_fleet_bucket",
        "status": "Failed",
        "timestamp.$": "$$.State.EnteredTime"
      },
      "End": true
    }
  }
}
