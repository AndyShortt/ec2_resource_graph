import boto3
import os
from datetime import datetime
from botocore.config import Config

elbv2 = boto3.client('elbv2')
elb = boto3.client('elb')
sts = boto3.client('sts')

region = os.environ.get('AWS_DEFAULT_REGION')
account = sts.get_caller_identity()['Account']

class ELBHelper(object):
    
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
            RoleSessionName="ELBDiscovery"
            )
        credentials=assumed_role_object['Credentials']
        
        # setup config file for region setting
        my_config = Config(
        region_name = region
        )
            
        global elbv2
        elbv2 = boto3.client('elbv2', 
            config=my_config,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
            )
            
        global elb
        elb = boto3.client('elb', 
            config=my_config,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
            )

    def getRegion(self):
        return (region)
    
    def getAccount(self):
        return (account)

    def getAllTargetGroups(self):
        
        #queries ALB/NLB API to get all target groups
        
        response = elbv2.describe_target_groups()
        return (response)

    
    def getTargetGroupByBalancer(self, balancerARN):
        
        #queries ALB/NLB API to get instances/IPs based on target group
        
        response = elbv2.describe_target_health(
        TargetGroupArn=balancerARN)
        return (response)

    
    def getAllClassicLoadBalancers(self):
        
        #queries ELB classic API to get all ELB load balancers
        
        response = elb.describe_load_balancers()
        return (response)
    
        
    def appendOutput(self, tagName, tagValue, resourceType, Id):

        #adds ELB/ALB/NLB to the output JSON in proper format
        Identifier = Id
        dateValue = datetime.now().isoformat()

        if resourceType == 'LoadBalancerClassic':
            Identifier = "arn:aws:elasticloadbalancing:" + region + ":" + account + ":loadbalancer/" + Id
        
        output = {'TagName':tagName, 'TagValue':tagValue,'Region':region,'Account':account,'ResourceType':resourceType, 'Id':Identifier, 'Date':dateValue}
        return (output)