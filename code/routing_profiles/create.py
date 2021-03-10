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
            InstanceId='bfb4d941-d847-4339-bbbf-2192291b45b0'
            RoutingProfileName=i['RoutingProfileName']
            RoutingProfileDescription=i['RoutingProfileConfig']['Description']
            DefaultOutboundQueueId='67a8f931-a58e-4d25-a256-8d4a682dec69'
            # Check if RoutingProfileQueueConfigSummaryList is present
            queueconfiglist = []
            mediaconcurrency = []
            queueispresent = []
            if RoutingProfileName != 'Basic Routing Profile':
                for queusummary in i['RoutingProfileConfig']['RoutingProfileQueueConfigSummaryList']:
                    queueconfig = {}
                    queueinfo = list_queue_details(queusummary)
                    if queueinfo != []:
                        queueispresent.append(queueinfo)
                        print("Queue Info Swapnil",queueinfo)
                        qid = queueinfo[0]['QueueId']
                        if qid != "":
                            queueId = queueinfo[0]['QueueId']
                            queueconfig['QueueReference'] = {'QueueId': queueId, 'Channel': queusummary['Channel']}
                            queueconfig['Priority'] = int(queusummary['Priority'])
                            queueconfig['Delay'] = int(queusummary['Delay'])
                            queueconfiglist.append(queueconfig)
                        else:
                            print("QueueId Not Found")
                    print(queueconfiglist)
                for media in i['RoutingProfileConfig']['MediaConcurrencies']:
                    mediaconfig = {}
                    mediaconfig['Concurrency'] = int(media['Concurrency'])
                    mediaconfig['Channel'] = media['Channel']
                    mediaconcurrency.append(mediaconfig)
                # QueueConfigs = queueconfiglist
                if queueispresent != []:
                    finalroutingconfig= {
                        'InstanceId': InstanceId,
                        'Name': RoutingProfileName,
                        'Description': RoutingProfileDescription,
                        'DefaultOutboundQueueId': DefaultOutboundQueueId,
                        'QueueConfigs': queueconfiglist,
                        'MediaConcurrencies': mediaconcurrency
                    }
                    try:
                        routing_profile_config(finalroutingconfig)
                    except Exception as e:
                        pass
            else:
                print("No Result Found")
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Query Operation succeeded:")

# Creates a new routing profile.
def routing_profile_config(finalroutingconfig):
    print(finalroutingconfig)
    try:
        result = connect_client.create_routing_profile(
            InstanceId=finalroutingconfig['InstanceId'],
            Name=finalroutingconfig['Name'],
            Description=finalroutingconfig['Description'],
            DefaultOutboundQueueId=finalroutingconfig['DefaultOutboundQueueId'],
            QueueConfigs= finalroutingconfig['QueueConfigs'],
            MediaConcurrencies= finalroutingconfig['MediaConcurrencies']
        )
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Succeessfully Created Routing Profiles:")
        print(json.dumps(result, indent=4, sort_keys=True))

# Get Queue Details From The Target Connect Instance
def list_queue_details(queusummary):
    print("Queue Summary")
    print(queusummary)
    # JSON Object containing required details to create Amazon Connect Cloud Instance
    try:
        response = connect_client.list_queues(
            InstanceId= 'bfb4d941-d847-4339-bbbf-2192291b45b0',
            QueueTypes= [
                'STANDARD'
            ]
        )
        if response:
            QueueSummarylist = response['QueueSummaryList']
            listofqueues = []
            for qlist in QueueSummarylist:
                queueassign = {}
                if qlist['Name'] == queusummary['QueueName']:
                    queueassign['QueueName'] = qlist['Name']
                    queueassign['QueueId'] = qlist['Id']
                    listofqueues.append(queueassign)
                else:
                    continue
            return listofqueues
            return {'statusCode': 200, 'body': json.dumps(response)}
    except Exception as e:
        raise e
        print(e.response['Error']['Message'])
    else:
        print("Succeessfully Created Routing Profiles:")
        print(json.dumps(result, indent=4, sort_keys=True))