import boto3
import os
import json
import logging
from datetime import datetime, timezone, timedelta


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
        logger.info(f"Checking last deployment for app_id={app_id}, branch_name={branch_name}")
        jobs = client.list_jobs(appId=app_id, branchName=branch_name, maxResults=1)
        last_deploy_time = None
        if jobs.get('jobSummaries'):
            last_job = jobs['jobSummaries'][0]
            if last_job.get('status') == 'SUCCEED' and last_job.get('endTime'):
                last_deploy_time = last_job['endTime']
                if isinstance(last_deploy_time, str):
                    last_deploy_time = datetime.fromisoformat(last_deploy_time.replace('Z', '+00:00'))
                elif not last_deploy_time.tzinfo:
                    last_deploy_time = last_deploy_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if last_deploy_time and (now - last_deploy_time) < timedelta(hours=1):
            logger.info(f"Last deployment was at {last_deploy_time}, less than 1 hour ago. Skipping redeploy.")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Branch was deployed less than 1 hour ago. Skipping redeploy.",
                    "last_deploy_time": last_deploy_time.isoformat()
                })
            }
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
