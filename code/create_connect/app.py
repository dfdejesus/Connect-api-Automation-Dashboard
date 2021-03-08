#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto3
import json
import os
import secrets

connect_client = boto3.client('connect')

def lambda_handler(event, context):

    # Renders the lambda deployment region
    current_region=os.environ['AWS_REGION']
    # Generates an idempotency client token

    client_token = secrets.token_hex(16)
    print(client_token)

    # JSON Object containing required details to create Amazon Connect Cloud Instance
    try:
        response = connect_client.create_instance(
            ClientToken= client_token,
            IdentityManagementType= 'CONNECT_MANAGED',
            InstanceAlias= 'HGSDigital-Connect-Demo',
            InboundCallsEnabled= True,
            OutboundCallsEnabled= False
        )
        if response:
            print('Successfully Created An Amazon Connect Instance.')
            return {'statusCode': 200, 'body': json.dumps(response)}
    except Exception as inst:
        print(inst)
