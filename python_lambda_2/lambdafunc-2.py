import json
import boto3

def lambda_handler(event, context):

    body = {
        "input": event
    }
    input_data = json.dumps(event['body'])
    response = {"statusCode": 200, "body": input_data}

    return response