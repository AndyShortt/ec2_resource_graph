import boto3
import datetime
import json
from ec2_helper import EC2Helper
from elb_helper import ELBHelper

elb_helper = ELBHelper()
ec2_helper = EC2Helper()
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # The purpose of this function is to place a json file in s3 that contains
    #   the various resources associated with ec2 instances that have a certain
    #   tag. For example, if you have 3 ec2 instances with Name:Client1 in
    #   us-east1, then this lambda function should print those instances and
    #   associated ELBS/snapshots/loadbalancers to the file.
    #
    # The expected downstream use of this s3 file is AWS Glue and Athena

    # Inputs sent during lambda invoke
    tagName = event['TagName']
    tagValue = event['TagValue']
    bucket = event['DestinationBucket']
    region = event['Region']
    account = event['Account']
    role = event['LambdaRole']
    
    #helper function to set ELB/EC2 API regions
    # NOTE: We do not change s3 region, assumes lambda runs in same region as bucket
    elb_helper.setConfig(region, account, role)
    ec2_helper.setConfig(region, account, role)
    
    # discover resources and add to JSON
    output = discoverResources(tagName,tagValue)
    
    # If we don't find any ec2 instances, we are done. otherwise generate file
    if output == 'No Instances Found':
        print(output)
        return(output)
    else:
        return (save_and_export(tagName, tagValue, region, account, bucket, output))


def discoverResources(tagName,tagValue):
    #iterates through resources adding them to the JSON output
    
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
                    
                    # Checks if ELB has instance as target
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
                        
                        # Checks if NLB/ALB has instance as target
                        if target['Target']['Id'] == instance['InstanceId']:
                            targetHasInstance = True
                        
                    if targetHasInstance:
                        for balancerArn in target_group['LoadBalancerArns']:
                            output.append(elb_helper.appendOutput(tagName,tagValue,'LoadBalancer',balancerArn))
                
                    ## TODO: Discover load balancers based on instance IP address
                    
    return (output)

def save_and_export (tagName, tagValue, region, account, bucket, result):

    filename = '{}_{}_{}'.format(tagValue, region, account)
    
    writeToFile(filename,result)
    moveToS3(filename,bucket)
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