# Promethium AWS Challenge

## Introduction

This project tackles Promethium's AWS Challenge. The project creates the following:
* Private EC2 instance that only allows outbound access to the Internet.
    * No public IP.
    * Outsider can only respond to requests, and no access shall be allows to the EC2 instance in any other circumstance.
    * Inbound SSH access allowed within the same VPC.
* Lambda function that periodically checks the status of port 22 for the EC2 instance created above.


## Tech Stack

* AWS CloudFormation
    * Used to create the AWS VPC, EC2, Lambda stack.
* Python 3.8
    * Used for the Lambda function.


## Steps for VPC + EC2 + Lambda Creation

1. Create VPC.
    * CIDR: 10.100.0.0/16
1. Create Internet gateway for the public subnet.
1. Attach Internet gateway to VPC.
1. Create 2 subnets: 1 public, 1 private.
    * Public: 10.100.1.0/24
    * Private: 10.100.2.0/24
1. Create a NAT gateway for the private subnet.
1. Create a Route Table for private subnet.
    * Add 0.0.0.0/0 nat-GW_ID to the routes.
1. Create a Route Table for public subnet.
    * Add 0.0.0.0/0 igw-GW_ID to the routes.
1. Change route table association for 2 subnets.
1. Create a security group.
    * Allow SSH from anywhere within the VPC (10.100.0.0/16 at port 22)
1. Create EC2 instance.
    1. Change Network to the VPC I created from #1.
    1. Change Subnet to private subnet from #4.
    1. Change security group to group from #9.
1. Create an IAM role with the following policies:
    * AmazonEC2ReadOnlyAccess
    * AWSLambdaBasicExecutionRole
1. Create Lambda function for checking port 22 status.
    * **NOTE**: The Python 3.8 code must be uploaded to S3.
1. Create a scheduled event that calls the Lambda function
    * Rate: 1 minute
    * Must be provided with a permission `lambda:InvokeFunction`


## Output Stack

![Image of output stack](https://github.com/dkkim6200/promethium-aws-challenge/raw/master/template_visualization.png)
