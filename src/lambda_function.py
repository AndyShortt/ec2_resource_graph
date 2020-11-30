import boto3
import datetime
import json
import os
from ec2_helper import EC2Helper
from elb_helper import ELBHelper

elb_helper = ELBHelper()
ec2_helper = EC2Helper()
s3 = boto3.client('s3')


def lambda_handler(event, context):

    setRegion('us-east-1')
    
    # Inputs
    tagName = os.environ.get("TagName")
    tagValue = os.environ.get("TagValue")
    bucket = os.environ.get("DestinationBucket")
    
    output = discoverResources(tagName,tagValue)
    
    if output == 'No Instances Found':
        return(output)
    else:
        return (save_and_export(tagName, tagValue, bucket, output))

def setRegion(region):

    elb_helper.setRegion(region)
    ec2_helper.setRegion(region)
    

def discoverResources(tagName,tagValue):
    
    # Initial loads
    output = []
    target_groups = elb_helper.getAllTargetGroups()['TargetGroups']
    classic_elbs = elb_helper.getAllClassicLoadBalancers()['LoadBalancerDescriptions']
    instance_info = ec2_helper.getInstanceByTag(tagName, tagValue)
    if not instance_info['Reservations']:
        return ("No Instances Found")

        
    # Loop through instances
    for reservation in ec2_helper.getReservationFromInfo(instance_info):
        for instance in ec2_helper.getInstancesFromReservation(reservation):
            output.append(ec2_helper.appendOutput(tagName,tagValue,'Instance',instance['InstanceId']))
            
            # Loop through Elastic IPs
            for address in ec2_helper.getEIPByInstance(instance)['Addresses']:
                output.append(ec2_helper.appendOutput(tagName,tagValue,'ElasticIP',address['PublicIp']))
            
            # Loop through Volumes
            for volume in ec2_helper.getVolumeFromInstance(instance):
                output.append(ec2_helper.appendOutput(tagName,tagValue,'Volume',volume['Ebs']['VolumeId']))
                
                # Loop through Snapshots
                for snapshot in ec2_helper.getSnapshotByVolume(volume['Ebs']['VolumeId'])['Snapshots']:
                    output.append(ec2_helper.appendOutput(tagName,tagValue,'Snapshot',snapshot['SnapshotId']))
            
            # Loop through ELBs (classic load balancers)
            for elb in classic_elbs:
                
                elbHasInstance = False
                
                for elbinstance in elb['Instances']:
                    
                    if elbinstance['InstanceId'] == instance['InstanceId']:
                        elbHasInstance = True
                
                if elbHasInstance:
                    output.append(elb_helper.appendOutput(tagName,tagValue,'LoadBalancerClassic',elb['LoadBalancerName']))
            
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
                            output.append(elb_helper.appendOutput(tagName,tagValue,'LoadBalancer',balancerArn))
                
                    ## TODO: Discover load balancers based on instance IP address
    return (output)


def save_and_export (tagName, tagValue, bucket, result):

    writeToFile(tagValue,result)
    moveToS3(tagValue,bucket)
    return ("Resource File Generated and Uploaded")
    #print (json.dumps(instance_info, default=datetime_handler))


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