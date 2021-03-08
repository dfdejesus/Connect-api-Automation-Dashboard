#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto3
import botocore
import json
import os
from datetime import datetime

connect_client = boto3.client('connect')
sts_connection = boto3.client('sts')
acct_b = sts_connection.assume_role(
    RoleArn="arn:aws:iam::052548640545:role/AmazonCrossRoleDynamoDBAccess",
    RoleSessionName="cross_acct_lambda"
)
# Getting the temporary credentials to access cross-account resources
ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
SESSION_TOKEN = acct_b['Credentials']['SessionToken']

dynamodb_client = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN)

print("boto3 version:"+boto3.__version__)

# Instance Id
Instanceid = "b585afc9-d645-4eb1-a595-a481a4bfe0fa"
current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

# Initializes an empty Dictionary
RoutingProfileConfigList = {}

def lambda_handler(event, context):
    # Note: Make Sure Hours Of Operation is Already created in amazon connect instance 
    # in order to create queues successfully

    # Renders the lambda deployment region
    current_region=os.environ['AWS_REGION']

    # Initilized Empty Variable to Store Queue Information
    RoutingProfileSummaryList = None    

    # JSON Object containing required details to list connect routing profiles
    try:
        response = connect_client.list_routing_profiles(
            InstanceId= Instanceid
        )
        if response:
            RoutingProfileSummaryList = response['RoutingProfileSummaryList']
            for list in RoutingProfileSummaryList:
                RoutingProfileid = list['Id']
                rpd_output = routing_profile_describe(RoutingProfileid)
            return {'statusCode': 200, 'body': json.dumps(response)}
    except Exception as inst:
        print(inst)

# Describes the specified routing profile
def routing_profile_describe(RoutingProfileid):
    try:
        result = connect_client.describe_routing_profile(
            InstanceId= Instanceid,
            RoutingProfileId= RoutingProfileid
        )

        # Calling routing profile queues opeation
        rpq_output = routing_profile_queue_describe(result)
        if rpq_output:
            # Updating Queue Details in DynamoDB
            update_routing_profile(rpq_output)
        return rpq_output
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Routing Profile Describe Operation succeeded:")
        print(json.dumps(result, indent=4, sort_keys=True))

# Lists the queues associated with a routing profile
def routing_profile_queue_describe(result):
    RoutingProfileid = result['RoutingProfile']['RoutingProfileId']
    try:
        response = connect_client.list_routing_profile_queues(
            InstanceId= Instanceid,
            RoutingProfileId= RoutingProfileid
        )
        RoutingProfileQueueSummary = response['RoutingProfileQueueConfigSummaryList']

        # Appending the results to the dictonary
        RoutingProfileConfigList['RoutingProfile'] = result['RoutingProfile']
        RoutingProfileConfigList['RoutingProfile']['RoutingProfileQueueConfigSummaryList'] = RoutingProfileQueueSummary
        
        return RoutingProfileConfigList
        
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Queues associated with routing profiles listing succeeded:")
        print(json.dumps(response, indent=4, sort_keys=True))

# DynamoDB Update Opeation To Store Connect Queue Details  
def update_routing_profile(RoutingProfileConfigList):
    ddbtable = dynamodb_client.Table('Routing_Profiles_Config')
    try:
        response = ddbtable.update_item(
            Key={
                    'InstanceId': Instanceid,
                    'RoutingProfileId': RoutingProfileConfigList['RoutingProfile']['RoutingProfileId']
                },
            UpdateExpression="set RoutingProfileConfig = :rqc, CreatedAt = :CreatedAt, RoutingProfileName = :profilename",
            ExpressionAttributeValues={
                    ':rqc': RoutingProfileConfigList['RoutingProfile'],
                    ':CreatedAt': current_time,
                    ':profilename': RoutingProfileConfigList['RoutingProfile']['Name']
                },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("UpdateItem succeeded:")
        print(json.dumps(response, indent=4, sort_keys=True))