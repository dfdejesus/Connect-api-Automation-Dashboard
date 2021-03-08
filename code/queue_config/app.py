#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto3
import botocore
import json
import os

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

print("boto3 version:"+boto3.__version__)

# Instance Id
Instanceid = "b585afc9-d645-4eb1-a595-a481a4bfe0fa"

def lambda_handler(event, context):
    # Note: Make Sure Hours Of Operation is Already created in amazon connect instance 
    # in order to create queues successfully

    # Renders the lambda deployment region
    current_region=os.environ['AWS_REGION']

    # Initilized Empty Variable to Store Queue Information
    QueueSummarylist = None

    # JSON Object containing required details to create Amazon Connect Cloud Instance
    try:
        response = connect_client.list_queues(
            InstanceId= Instanceid,
            QueueTypes= [
                'STANDARD'
            ]
        )
        if response:
            print('Successfully listed An Amazon Connect Instance queues.')
            QueueSummarylist = response['QueueSummaryList']
            print(QueueSummarylist)
            for list in QueueSummarylist:                
                Queueid = list['Id']
                queue_describe(Instanceid, Queueid)               
            return {'statusCode': 200, 'body': json.dumps(response)}
    except Exception as inst:
        print(inst)

# Calling amazon connect Describe_queue API
def queue_describe(Instanceid, Queueid):
    try:
        result = connect_client.describe_queue(
            InstanceId= Instanceid,
            QueueId= Queueid
        )
        # Updating Queue Details in DynamoDB
        update_queue_config(result)
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Describe Operation succeeded:")
        print(json.dumps(response, indent=4, sort_keys=True))

# DynamoDB Update Opeation To Store Connect Queue Details  
def update_queue_config(result):
    ddbtable = dynamodb_client.Table('Queue_Config')
    try:
        response = ddbtable.update_item(
            Key={
                    'InstanceId': Instanceid,
                    'QueueId': result['Queue']['QueueId']
                },
            UpdateExpression="set QueueConfig = :qc",
            ExpressionAttributeValues={
                    ':qc': result['Queue']
                },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("UpdateItem succeeded:")
        print(json.dumps(response, indent=4, sort_keys=True))