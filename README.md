# ec2_resource_graph
Traverses resource associations based on an EC2 tag. Currently includes EBS, Snapshots, and ALB/NLB.

Assumes an AWS Lambda operating environment with Python 3 and execution role with access to EC2, ALB, and S3 APIs.

Change global tag and bucket variables to include your specifics. Change these to OS enviornment vairables in order to run for multiple sets of tags without changing code.
