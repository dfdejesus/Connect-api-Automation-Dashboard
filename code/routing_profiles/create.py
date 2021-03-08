#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto3
import json
import os
import decimal
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

print("boto3 version:"+boto3.__version__)

# Instance Id
Instanceid = "b585afc9-d645-4eb1-a595-a481a4bfe0fa"
current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
routing_config = {}
routing_queues = []

def lambda_handler(event, context):
    # Make Sure Amazon Conenct Queues Are Created In connect instance.

    # Renders the lambda deployment region
    current_region=os.environ['AWS_REGION']
    
    # Calling get_routing_profiles dynamodb query function
    ddbtable = dynamodb_client.Table('Routing_Profiles_Config')
    try:
        # Querying DynamoDB Table Using Instance Id Primary Key
        response = ddbtable.query(
            KeyConditionExpression=Key('InstanceId').eq(Instanceid)
        )
        for i in response['Items']:
            # Four Variables to Declare 
            InstanceId='string'
            RoutingProfileName='string'
            RoutingProfileDescription='string'
            DefaultOutboundQueueId='string'
            # Check if RoutingProfileQueueConfigSummaryList is present
            queueconfiglist = []
            mediaconcurrency = []
            for queusummary in i['RoutingProfileQueueConfigSummaryList']:
                queueconfig = {}
                queueconfig['QueueReference'] = {'QueueId': '', 'Channel': ''}
                queueconfig['Priority'] = ''
                queueconfig['Delay'] = ''
                queueconfiglist.append(queueconfig)
            for media in i['RoutingProfileConfig']['MediaConcurrencies']:
                mediaconfig = {}
                mediaconfig['Concurrency'] = int()
                mediaconfig['Channel'] = ''
                mediaconcurrency.append(mediaconfig)
            # QueueConfigs = queueconfiglist
            finalroutingconfig= {
                'InstanceId': InstanceId,
                'Name': RoutingProfileName,
                'Description': RoutingProfileDescription,
                'DefaultOutboundQueueId': DefaultOutboundQueueId,
                'QueueConfigs': queueconfiglist,
                'MediaConcurrencies': mediaconcurrency
            }
            routing_profile_config(finalroutingconfig)
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Query Operation succeeded:")

def routing_profile_config(finalroutingconfig):
    try:
        result = connect_client.create_routing_profile(
            InstanceId=finalroutingconfig['Instanceid'],
            Name='string',
            Description='string',
            DefaultOutboundQueueId='string',
            QueueConfigs= '',
            MediaConcurrencies= ''
        )
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Succeessfully Created Routing Profiles:")
        print(json.dumps(result, indent=4, sort_keys=True))