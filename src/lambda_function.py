import boto3
import datetime
import json
import os
from ec2_helper import EC2Helper
from elb_helper import ELBHelper

elb_helper = ELBHelper()
ec2_helper = EC2Helper()
s3 = boto3.client('s3')

output = []

def lambda_handler(event, context):
    
    # Globals
    global output
    output = []
    
    # Inputs
    tagName = 'Name'
    tagValue = 'ec2-tag-value'
    bucket = 'sample-s3-bucket'
    
    # Initial loads
    target_groups = elb_helper.getAllTargetGroups()['TargetGroups']
    classic_elbs = elb_helper.getAllClassicLoadBalancers()['LoadBalancerDescriptions']
    instance_info = ec2_helper.getInstanceByTag(tagName, tagValue)
    if not instance_info['Reservations']:
        return ("No Instances Found")
        
    # Loop through instances
    for reservation in ec2_helper.getReservationFromInfo(instance_info):
        for instance in ec2_helper.getInstancesFromReservation(reservation):
            appendOutput(tagName,tagValue,'Instance',instance['InstanceId'])
            
            # Loop through Elastic IPs
            for address in ec2_helper.getEIPByInstance(instance)['Addresses']:
                appendOutput(tagName,tagValue,'ElasticIP',address['PublicIp'])
            
            # Loop through Volumes
            for volume in ec2_helper.getVolumeFromInstance(instance):
                appendOutput(tagName,tagValue,'Volume',volume['Ebs']['VolumeId'])
                
                # Loop through Snapshots
                for snapshot in ec2_helper.getSnapshotByVolume(volume['Ebs']['VolumeId'])['Snapshots']:
                    appendOutput(tagName,tagValue,'Snapshot',snapshot['SnapshotId'])
            
            # Loop through ELBs (classic load balancers)
            for elb in classic_elbs:
                
                elbHasInstance = False
                
                for instance in elb['Instances']:
                    
                    if instance['InstanceId'] == instance['InstanceId']:
                        elbHasInstance = True
                
                if elbHasInstance:
                    appendOutput(tagName,tagValue,'Balancer',elb['LoadBalancerName'])
            
            # Loop through Target Groups (For ALB/NLBs)
            for target_group in target_groups:
                
                if target_group['TargetType'] == 'instance':
                    
                    targetHasInstance = False
                    
                    # Loop through Targets
                    for target in elb_helper.getTargetGroupByBalancer(target_group['TargetGroupArn'])['TargetHealthDescriptions']:
                        if target['Target']['Id'] == instance['InstanceId']:
                            targetHasInstance = True
                        
                    if targetHasInstance:
                        for balancerArn in target_group['LoadBalancerArns']:
                            appendOutput(tagName,tagValue,'Balancer',balancerArn)
                
                ## TODO: Discover load balancers based on instance IP address
    
    writeToFile(tagValue,output)
    moveToS3(tagValue,bucket)
    return ("Resource File Generated and Uploaded")
    #print (json.dumps(instance_info, default=datetime_handler))

def appendOutput(tagName, tagValue, resourceType, Id):

    output.append({tagName:tagValue,'ResourceType':resourceType, 'Id':Id})

def writeToFile(filename, jsonfile):
    
    with open('//tmp/{}.json'.format(filename), 'w') as outfile:
        for element in jsonfile:
            json.dump(element, outfile)
            outfile.write("\n")
        
def moveToS3(filename, bucket):

    response = s3.upload_file('//tmp/{}.json'.format(filename), bucket, 'resources/{}.json'.format(filename))


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")