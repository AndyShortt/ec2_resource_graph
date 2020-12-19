import boto3
import json
import os
import time

lambdaclient = boto3.client('lambda')

def lambda_handler(event, context):
    
    # Inputs
    regions = event['regions']
    accounts = event['accounts']
    lambdaRole = event['lambdaRole']
    functionName = os.environ.get("LambdaFunction")
    tagName = event['tagName']
    tagValue = event['tagValue']
    bucket = event['outputBucket']
    
    if len(accounts) < 1 or len(regions) < 1:
        return("Input error, no regions or accounts entered")
    
    for account in accounts:
        account = account.strip()
        
        for region in regions:
            region = region.strip()
            
            params = {
                "Region" : region,
                "Account": account,
                "LambdaRole": lambdaRole,
                "TagName": tagName,
                "TagValue": tagValue,
                "DestinationBucket": bucket
            }
            
            response = lambdaclient.invoke(
                FunctionName=functionName,
                InvocationType='Event',
                Payload=json.dumps(params)
            )
            
            print("Invoked {} in region {} for account {}".format(functionName, region, account))
            
            time.sleep(1)
            
