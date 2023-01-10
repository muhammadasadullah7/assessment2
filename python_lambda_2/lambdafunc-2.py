import json
import boto3

def lambda_handler(event, context):

    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds=event['EC2']).terminate()
    ec2client = ec2.meta.client
    for vpc_id in event['VPC']:
        ec2client.delete_vpc(VpcId = vpc_id)  
    
    sns_client = boto3.client('sns')
    for sns_arn in event['SNS']:
        sns_client.delete_topic(TopicArn = sns_arn)
    
    body = {
        "input": event
    }
    input_data = json.dumps(event)
    response = {"statusCode": 200, "body": input_data}

    print("Response is ", response)
    

    return response