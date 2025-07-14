import boto3
import os
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Glue client
glue_client = boto3.client('glue')

# Lambda handler function
def lambda_handler(event, context):
    """
    AWS Lambda function that triggers a Glue job when new data is added to S3.
    
    Parameters:
    event (dict): Event data from S3 trigger
    context (LambdaContext): Lambda context object
    
    Returns:
    dict: Response with status of Glue job execution
    """
    try:
        logger.info("Received S3 event: " + json.dumps(event))
        
        # Extract bucket and key from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Bucket: {bucket}, Key: {key}")
        
        # Get the Glue job name from environment variable or use default
        glue_job_name = os.environ.get('GLUE_JOB_NAME', 'bovespa-etl-job')
        
        # Start the Glue job
        response = glue_client.start_job_run(
            JobName=glue_job_name,
            Arguments={
                '--S3_BUCKET': bucket,
                '--S3_KEY': key
            }
        )
        
        job_run_id = response['JobRunId']
        logger.info(f"Started Glue job {glue_job_name} with run ID: {job_run_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully started Glue job {glue_job_name}',
                'jobRunId': job_run_id
            })
        }
    except Exception as e:
        logger.error(f"Error starting Glue job: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error starting Glue job: {str(e)}'
            })
        }
