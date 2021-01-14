# ec2_resource_graph

## What it does

Traverses resource associations based on an EC2 tag. Puts output into JSON file in S3 (for use by Glue/Athena). Currently includes EC2 instances, EBS volumes, snapshots, and ALB/NLB, EIP, Classic LB.

## Pre-requisits
AWS API and SAM CLI installed
Note: AWS Cloud9 was used in development, these come pre-installed

## Deployment

1. Clone this repository from github.  
```sh  
$ git clone https://github.com/AndyShortt/this_repo_name.git
$ cd ec2_resource_graph/
```  

2. Run SAM build command.  
```sh  
$ sam build
```  

3. Run SAM deploy. Name stack and accept defaults or enter Y on other inputs.  
```sh  
$ sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
```  

4. Log into AWS CloudFormation, deploy new StackSet to accounts you will include in resource discovery. Only region required is us-east-1 since IAM is global. Use the template named "ResourceDiscoveryLambda.yaml" in the root directory as your Cloudformation templated for the StackSet, make sure to click the checkbox on the "Review" screen to allow it to created named IAM resources.  

5.Update parameters in params.json to reflect the EC2 tags, accounts, regions, and output bucket for S3 files.  

6. Find the "lambaController" lambda function that SAM created in the lambda console. Note the name. Invoke lambda  
```sh  
$ aws lambda invoke --function-name your-app-lambdaController-123 --payload file://params.json out.txt
```  

7. Check s3 bucket for output  
