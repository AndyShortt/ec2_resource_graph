import boto3
import os
from datetime import datetime
from botocore.config import Config

ec2 = boto3.client('ec2')
sts = boto3.client('sts')

region = os.environ.get('AWS_DEFAULT_REGION')
account= sts.get_caller_identity()['Account']

class EC2Helper(object):
    
    def setConfig(self, newRegion, newAccount, newRole):
        
        # confirm account/region are set, if not use current
        global region
        if not newRegion:
            region = os.environ.get('AWS_DEFAULT_REGION')
            print('No region found, using current')
        else:
            region = newRegion
        
        global account
        if not newAccount:
            account = sts.get_caller_identity()['Account']
            print('No account found, using current')
        else:
            account = newAccount
        
        # get credentials for new account/role
        assumed_role_object=sts.assume_role(
            RoleArn="arn:aws:iam::{}:role/{}".format(account, newRole),
            RoleSessionName="EC2Discovery"
            )
        credentials=assumed_role_object['Credentials']
        
        # setup config file for region setting
        my_config = Config(
        region_name = region
        )
        
        # apply these changes to boto3 client
        global ec2
        ec2 = boto3.client('ec2', 
            config=my_config,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
            )
    
    def getRegion(self):
        return (region)
    
    def getAccount(self):
        return (account)

    def getInstanceByTag(self, tagName, tagValue):
        
        #queries ec2 API to get all instances with a certain tag
        
        response = ec2.describe_instances(
        Filters=[
                {
                    'Name': 'tag:{}'.format(tagName),
                    'Values': [tagValue,],
                },
            ],
        )
        return (response)
    
    
    def getSnapshotByVolume(self, volumeId):
        
        #queries ec2 API to get all ebs snapshots for a volume
        
        response = ec2.describe_snapshots(
        Filters=[
                {
                    'Name': 'volume-id',
                    'Values': [volumeId,],
                },
            ],
        )
        return (response)
    
    
    def getInstancesFromReservation(self, reservation):
        
        #helper for getting all instances in a reservation
        
        return (reservation['Instances'])
    
    
    def getEIPByInstance(self, instance):
        
        #queries ec2 api to get all elastic IP addresses for a given instance
        
        response = ec2.describe_addresses(
        Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [instance['InstanceId'],],
                },
            ],
        )
        return (response)
    
    
    def getReservationFromInfo(self, instance_info):
        
        #helper for getting all reservations from describes_instances result
    
        return (instance_info['Reservations'])
    
    
    def getVolumeFromInstance(self, instance):
        
        #helper for getting all ebs volumes attached to an instance
    
        return (instance['BlockDeviceMappings'])
        
        
    def appendOutput(self, tagName, tagValue, resourceType, Id):
        
        #adds ec2/ebs/snapshot/EIP to the output JSON in proper format
        Identifier = Id
        dateValue = datetime.now().isoformat()
        
        if resourceType == 'Snapshot':
            Identifier = "arn:aws:ec2:" + region + ":" + account + ":snapshot/" + Id
        
        output = {'TagName':tagName, 'TagValue':tagValue,'Region':region,'Account':account,'ResourceType':resourceType, 'Id':Identifier, 'Date':dateValue}
        return (output)
