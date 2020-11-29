import boto3

ec2 = boto3.client('ec2')

class EC2Helper(object):

    def getInstanceByTag(self, tagName, tagValue):
        
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
        
        return (reservation['Instances'])
    
    
    def getEIPByInstance(self, instance):
        
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
    
        return (instance_info['Reservations'])
    
    
    def getVolumeFromInstance(self, instance):
    
        return (instance['BlockDeviceMappings'])