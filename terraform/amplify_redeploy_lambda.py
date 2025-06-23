import boto3
import os

def lambda_handler(event, context):
    client = boto3.client('amplify')
    app_id = os.environ['AMPLIFY_APP_ID']
    branch_name = os.environ['AMPLIFY_BRANCH_NAME']
    response = client.start_job(
        appId=app_id,
        branchName=branch_name,
        jobType='RELEASE'
    )
    return response
