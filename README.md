# ec2_resource_graph

## What it does

Traverses resource associations based on an EC2 tag. Currently includes EBS volumes, snapshots, and ALB/NLB.

## Pre-requisits
AWS API and SAM CLI installed
Note: AWS Cloud9 was used in development, these come pre-installed

## Deployment

1. Copy directory from github  
2. run SAM build command  
```sh  
$ sam build
```  
3. run SAM deploy, add parameters for EC2 Tag Key (TagKey) and EC2 Tag Value (TagValue) and S3 bucket for results (DestinationBucket)  
```sh  
$ sam deploy --guided
```  
4. Walk through the questions presented. Everything can be kept as default except the Parameters.
- For "Parameter Key" enter the EC2 tag key, such as "Name"
- For "Parameter Value" enter the EC2 Tag value, such as "Client1"
- For "Parameter DestinationBucket" enter the S3 bucket name where results should be stored for Athena to query
