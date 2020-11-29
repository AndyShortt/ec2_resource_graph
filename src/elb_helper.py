import boto3

elbv2 = boto3.client('elbv2')
elb = boto3.client('elb')

class ELBHelper(object):

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