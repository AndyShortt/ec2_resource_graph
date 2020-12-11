import boto3
import json
import os
import time

lambdaclient = boto3.client('lambda')

def lambda_handler(event, context):
    
    # Inputs
    regions = 'us-east-1, us-west-2, ca-central-1, eu-west-1, ap-southeast-1'
    accounts = '313021996969'
    lambdaRole = os.environ.get("LambdaRole")
    functionName = os.environ.get("LambdaFunction")
    tagName = os.environ.get("TagName")
    tagValue = os.environ.get("TagValue")
    bucket = os.environ.get("DestinationBucket")
    
    try:
        accountList = accounts.split(",")
        regionList = regions.split(",")
    except:
        return("Input error, unable to parse account/region list")
    
    
    if len(accountList) < 1 or len(regionList) < 1:
        return("Input error, no regions or accounts entered")
    
    for account in accountList:
        account = account.strip()
        
        for region in regionList:
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
            
