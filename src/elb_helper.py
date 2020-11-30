import boto3
from botocore.config import Config

elbv2 = boto3.client('elbv2')
elb = boto3.client('elb')

class ELBHelper(object):
    
    def setRegion(self, region):
        
        my_config = Config(
        region_name = region
        )
        
        global elbv2
        elbv2 = boto3.client('elbv2', config=my_config)
        
        global elb
        elb = boto3.client('elb', config=my_config)


    def getAllTargetGroups(self):
        
        response = elbv2.describe_target_groups()
        return (response)

    
    def getTargetGroupByBalancer(self, balancerARN):
        
        response = elbv2.describe_target_health(
        TargetGroupArn=balancerARN)
        return (response)

    
    def getAllClassicLoadBalancers(self):
        
        response = elb.describe_load_balancers()
        return (response)
    
    
    def appendOutputClassic(self, tagName, tagValue, resourceType, Id, output):

        output = output.append({tagName:tagValue,'ResourceType':resourceType, 'Id':Id})
        return (output)
    
        
    def appendOutput(self, tagName, tagValue, resourceType, Id):

        if resourceType == 'LoadBalancerClassic':
            
            output = {tagName:tagValue,'ResourceType':resourceType, 'Id':Id}
        
        elif resourceType == 'LoadBalancer':
        
            output = {tagName:tagValue,'ResourceType':resourceType, 'Id':Id}
        
        return (output)