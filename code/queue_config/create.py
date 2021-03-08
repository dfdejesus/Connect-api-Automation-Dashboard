#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto3
import botocore
import json
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

connect_client = boto3.client('connect')
sts_connection = boto3.client('sts')
acct_b = sts_connection.assume_role(
    RoleArn="arn:aws:iam::052548640545:role/AmazonCrossRoleDynamoDBAccess",
    RoleSessionName="cross_acct_lambda"
)

ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
SESSION_TOKEN = acct_b['Credentials']['SessionToken']

dynamodb_client = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN)
        
# Instance Id
Instanceid = "b585afc9-d645-4eb1-a595-a481a4bfe0fa"
current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
hoo = "fca88d46-7a4a-41e7-a5b2-98c7426a2e64"

def lambda_handler(event, context):
    # Make Sure Amazon Conenct Queues Are Created In connect instance.

    # Renders the lambda deployment region
    current_region=os.environ['AWS_REGION']
    
    # Calling get_routing_profiles dynamodb query function
    ddbtable = dynamodb_client.Table('Queue_Config')
    try:
        # Querying DynamoDB Table Using Instance Id Primary Key
        response = ddbtable.query(
            KeyConditionExpression=Key('InstanceId').eq(Instanceid)
        )
        for i in response['Items']:
            # OutboundCallerConfig = {}
            print(i['QueueConfig'])
            QueueName = i['QueueConfig']['Name']
            Description = i['QueueConfig']['Description']
            InstanceId = "bfb4d941-d847-4339-bbbf-2192291b45b0"
            # OutboundCallerConfig = i['QueueConfig']['OutboundCallerConfig']
            HoursOfOperationId = hoo
            finalqueueconfig = {
                'QueueName' : QueueName,
                'Description': Description,
                'InstanceId' : "bfb4d941-d847-4339-bbbf-2192291b45b0",
                # 'OutboundCallerConfig' : OutboundCallerConfig,
                'HoursOfOperationId' : HoursOfOperationId
            }
            create_queue_config(finalqueueconfig)
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Query Operation succeeded:")

# Create Queue Connect API Operation   
def create_queue_config(finalqueueconfig):
    try:
        result = connect_client.create_queue(
            InstanceId=finalqueueconfig['InstanceId'],
            Name=finalqueueconfig['QueueName'],
            Description=finalqueueconfig['Description'],
            # OutboundCallerConfig= finalqueueconfig['OutboundCallerConfig'],
            HoursOfOperationId=finalqueueconfig['HoursOfOperationId']
        )
        return result
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Query Operation succeeded:")