import boto3
import os
import json
import logging
from datetime import datetime


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)


def lambda_handler(event, context):
    client = boto3.client('amplify')
    app_id = os.environ['AMPLIFY_APP_ID']
    branch_name = os.environ['AMPLIFY_BRANCH_NAME']
    try:
        logger.info(f"Triggering redeploy for app_id={app_id}, branch_name={branch_name}")
        response = client.start_job(
            appId=app_id,
            branchName=branch_name,
            jobType='RELEASE'
        )
        logger.info(f"Amplify start_job response: {response}")
        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DateTimeEncoder)
        }
    except Exception as e:
        logger.error(f"Error triggering Amplify redeploy: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
