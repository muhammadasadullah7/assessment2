import json
import boto3
import random
from datetime import datetime
from datetime import timedelta

def createEC2(number):
    id = []
    ec2 = boto3.resource('ec2')
    for index in range(number):
        instance = ec2.create_instances(
            ImageId="ami-0b0dcb5067f052a63",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
        )
        id.append(str(instance[0].id))
    return id


def createVPC(number):
    #cidr_ranges = ['192.168.1.0/24', '192.168.2.0/24', '192.168.3.0/24', '192.168.4.0/24', '192.168.5.0/24']
    id = []
    ec2 = boto3.resource('ec2')
    for index in range(number):
        ip_cidr = "192.168."+str(index+1)+".0/24"
        vpc = ec2.create_vpc(CidrBlock=ip_cidr)
        id.append(vpc.id)
    return id
    
def createSNS(number):
    id = []
    sns_client = boto3.client('sns')
    for index in range(number):
        sns = sns_client.create_topic(Name='topic-'+str(random.randint(1000, 9999)))
        id.append(sns['TopicArn'])
        #id.append(sns['TopicArn'].split(":")[-1])
    return id

def lambda_handler(event, context):

    body = {
        "input": event
    }
    input_data = json.dumps(event['body'])
    #input_data = json.dumps(event)
    #response = {"statusCode": 200, "body": json.dumps(body)}
    #response = {"statusCode": 200, "body": json.dumps(event['headers']['X-Forwarded-For'])}
    response2 = {"statusCode": 200, "body": input_data}
    #['queryStringParameters']['name']
    #response = {"statusCode": 200, "body": json.dumps(event)}

    # message = 'Hello {} !'.format(event['key1'])
    # return {
    #     'message' : "Hellooooo" #message
    # }
    # input_data = str(input_data)
    # input_data = eval(input_data)
    # print (input_data)
    # print(type(input_data))
    
    # print("New instance created:", instance[0].id)
    #return {"statusCode": 200, "body": input_data+"hello"}
    #input_data_dict = eval(input_data)
    #print (input_data_dict)
    #return {"statusCode": 200, "body": input_data}
#     input_data_dict = {
#     "VPC": "1",
#     "EC2": "1",
#     "SNS": "0"
#   }
    #input_data_dict_1 = json.loads(input_data)
    #input_data_dict = input_data_dict_1.copy()
    #print(input_data_dict)
    #print(type(input_data_dict))
    #print(input_data_dict['VPC'])
    #print(input_data_dict['EC2'])
    
    
    #val = input_data_dict['SNS']
    #print (type(val))
    
    #print (input_data)
    #res = [int(i) for i in input_data.split() if i.isdigit()]
    #print(res)
    print ("Data is ",input_data)
    list_VPC = createVPC(int(input_data[12]))
    list_EC2 = createEC2(int(input_data[26]))
    list_SNS = createSNS(int(input_data[40]))

    # list_SNS = createSNS(1)
    # list_VPC = createVPC(0)
    # list_EC2 = createEC2(0)
    
    arg_dict = {}
    arg_dict['VPC']=list_VPC
    arg_dict['EC2']=list_EC2
    arg_dict['SNS']=list_SNS
    # for index, vpc_id in enumerate(list_VPC):
    #     key= "vpc["+str(index)+"]"
    #     value = vpc_id
    #     arg_dict[key] = value
    
    # for index, ec2_id in enumerate(list_EC2):
    #     key= "ec2["+str(index)+"]"
    #     value = ec2_id
    #     arg_dict[key] = value
        
    # print ("Dict is", arg_dict)
    
    client = boto3.client('iam')
    event_role = client.get_role(
    RoleName='permission_eventbridge')['Role']['Arn']
    print(event_role)
    
#    cron_sec = 'cron(* * * * ? *)'
    cron_sec = 'rate(60 minutes)'
    
    lambda_client =  boto3.client('lambda')
    lambda_2_arn = lambda_client.get_function(
    FunctionName='lambda-2-function')['Configuration']['FunctionArn']
    
    print(lambda_2_arn)
    
    delete_time = datetime.now()+timedelta(minutes = 3)
    del_time = f"cron({delete_time.minute} {delete_time.hour} {delete_time.day} {delete_time.month} ? {delete_time.year})"
    # print(del_time)
    rule_id = "deleteResources-"+str(random.randint(1000, 9999))
    
    #del_time = cron_sec
    event_client = boto3.client('events')
    
    put_rule_lambda_2 = event_client.put_rule(
    Name=rule_id,
    ScheduleExpression=del_time,
    State='ENABLED',
    Description='Delete Resources',
    RoleArn=event_role,
    # Tags=[
    #     {
    #         'Key': 'string',
    #         'Value': 'string'
    #     }
    # ]
    )
    
    # print("Rule is ",put_rule_lambda_2)
    
    put_target_lambda_2 = event_client.put_targets(
            Rule=rule_id,
            Targets=[{
                'Id': 'lambda-2-function',
                'Arn': lambda_2_arn,
                'Input': json.dumps(arg_dict)
            }]
        )
        
    add_lambda_permission = lambda_client.add_permission(
            FunctionName=lambda_2_arn,
            StatementId=rule_id,
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=put_rule_lambda_2['RuleArn']
        )

# Put an event
#json.dumps({'VPC': list_VPC, 'EC2': list_EC2})
#'Detail': "{ \"key1\": \"value1\", \"key2\": \"value2\" }",

    response = event_client.put_events(
        Entries=[
            {
                'Source': 'website_data',
                'DetailType': 'deleteResources',
                'Detail': json.dumps(event),
                'Resources': [
                    lambda_2_arn,
                ]
            }
        ]
    )
    print("Response is ",response)
    
    # response = event_client.put_events(
    # Entries=[
    #     {
    #         'Time': datetime.now(),
    #         'Source': 'Publisher Lambda',
    #         'Resources': [],
    #         'DetailType': 'Send event from First Lambda',
    #         'Detail': json.dumps(event),
    #         #'EventBusName': '',
    #         'TraceHeader': 'Demo POC'
    #     }
    # ]
    # )
    # print("Response is ",response)
    
    # print("Rule is: ",put_rule_lambda_2)
    # print("Target is: ",put_target_lambda_2)
    #print("Event is: ",put_target_lambda_2)
    # print (list_VPC)
    # print (list_EC2)
    #return {"statusCode": 200, "body": input_data[12:]+"oay"+datacopy}
    #return response
    return {"statusCode": 200, "body": "VPCs are: "+' '.join(list_VPC)+" EC2s are "+' '.join(list_EC2)+" and SNS are "+' '.join(list_SNS)}
    #return {"statusCode": 200, "body": "VPCs are: "+list_VPC+"and EC2s are "+list_EC2}
    # for index, (key, value) in enumerate(input_data_dict.items()):
    #     print(index, key, value)
    #     if key == "EC2":
    #         createEC2(int(value))
    #     elif key == "VPC":
    #         createVPC(int(value))
    #     else:
    #         pass
    # return response