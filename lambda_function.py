import boto3
import datetime
import json
import os

ec2 = boto3.client('ec2')
elbv2 = boto3.client('elbv2')
elb = boto3.client('elb')
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
    target_groups = getAllTargetGroups()['TargetGroups']
    classic_elbs = getAllClassicLoadBalancers()['LoadBalancerDescriptions']
    instance_info = getInstanceByTag(tagName, tagValue)
    if not instance_info['Reservations']:
        return ("No Instances Found")
        
    # Loop through instances
    for reservation in getReservationFromInfo(instance_info):
        for instance in getInstancesFromReservation(reservation):
            appendOutput(tagName,tagValue,'Instance',instance['InstanceId'])
            
            # Loop through Elastic IPs
            for address in getEIPByInstance(instance)['Addresses']:
                appendOutput(tagName,tagValue,'ElasticIP',address['PublicIp'])
            
            # Loop through Volumes
            for volume in getVolumeFromInstance(instance):
                appendOutput(tagName,tagValue,'Volume',volume['Ebs']['VolumeId'])
                
                # Loop through Snapshots
                for snapshot in getSnapshotByVolume(volume['Ebs']['VolumeId'])['Snapshots']:
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
                    for target in getTargetGroupByBalancer(target_group['TargetGroupArn'])['TargetHealthDescriptions']:
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
    
def getInstanceByTag(tagName, tagValue):
    
    response = ec2.describe_instances(
    Filters=[
            {
                'Name': 'tag:{}'.format(tagName),
                'Values': [tagValue,],
            },
        ],
    )
    return (response)


def getSnapshotByVolume(volumeId):
    
    response = ec2.describe_snapshots(
    Filters=[
            {
                'Name': 'volume-id',
                'Values': [volumeId,],
            },
        ],
    )
    return (response)


def getAllTargetGroups():
    
    response = elbv2.describe_target_groups()
    return (response)

def getTargetGroupByBalancer(balancerARN):
    
    response = elbv2.describe_target_health(
    TargetGroupArn=balancerARN)
    return (response)

def getAllClassicLoadBalancers():
    
    response = elb.describe_load_balancers()
    return (response)

def getInstancesFromReservation(reservation):
    
    return (reservation['Instances'])

def getEIPByInstance(instance):
    
    response = ec2.describe_addresses(
    Filters=[
            {
                'Name': 'instance-id',
                'Values': [instance['InstanceId'],],
            },
        ],
    )
    return (response)

def getReservationFromInfo(instance_info):

    return (instance_info['Reservations'])

def getVolumeFromInstance(instance):

    return (instance['BlockDeviceMappings'])

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")