"""This Lambda module checks the status of the port 22 of EC2 instance created by AWS CloudFormation template.

**Note**: INSTANCE_ID and VPC_CIDR is required as part of the environment variables.
"""

__docformat__ = 'reStructuredText'

import sys
import boto3
from boto3 import ec2
import socket
import os

class InstanceReachability:
    """This class is a container for information about reachability of an EC2 instance at port 22.

    Use this class to print a prettified version of the reachability information.
    """
    def __init__(self, instance_id, private_ip_address = "", reachable = False):
        """Initializes a new InstanceReachability object.

        :param instance_id: Instance ID of an AWS EC2 instance.
        :param private_ip_address: Private ID of the AWS EC2 instance. If the default value \"\" is used, the private IP address will not be used in __str__ method.
        :param reachable: Reachability of the EC2 instance at port 22
        """
        self.instance_id = instance_id
        self.private_ip_address = private_ip_address
        self.reachable = reachable
    
    def __str__(self):
        if (self.private_ip_address != ""):
            return "Instance " + self.instance_id + " with private IP address " + self.private_ip_address + " at port 22 is " + ("reachable." if self.reachable else "not reachable.")
        else:
            return "Instance " + self.instance_id + " is not reachable."
        

def lambda_handler(event, context):
    """Prints status of port 22 that was created from CloudFormation template.

    .. note::
        INSTANCE_ID and VPC_CIDR is required as part of the environment variables.

    :returns: OK status response if the code executes successfully.
    """

    instance_reachabilities = []
    
    connection = boto3.client('ec2', region_name='us-east-2')
    response = connection.describe_instances(InstanceIds=[os.environ['INSTANCE_ID']])
    
    # Made into a loop for scalability to multiple instances
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # If the instance is not running, then add to instance_reachabilities an unreachable instance
            if (instance["State"]["Code"] != 16):
                instance_reachability = InstanceReachability(instance["InstanceId"], reachable = False)
                instance_reachabilities.append(instance_reachability)
                continue
            
            reachable = False
            
            # Iterate through the security groups attached to the instance
            security_group_ids = list((group["GroupId"] for group in instance["SecurityGroups"]))
            for sg in connection.describe_security_groups(GroupIds = security_group_ids)["SecurityGroups"]:
                # Iterate through the NACL of the security group
                for rule in sg["IpPermissions"]:
                    # If any of the NACL rules allow inbound traffic to port 22 from within the VPC, then the instance is reachable on port 22
                    if rule["IpProtocol"] == "tcp" and (rule["FromPort"] == 22 and rule["ToPort"] == 22) and all(ip_range["CidrIp"] == os.environ['VPC_CIDR'] for ip_range in rule["IpRanges"]):
                        reachable = True
                        continue
            
            # Add to instance_reachabilities an instance along with the reachability information
            instance_reachability = InstanceReachability(instance["InstanceId"], instance["PrivateIpAddress"], reachable)
            instance_reachabilities.append(instance_reachability)
    
    # Print the instance reachability infos
    for instance_reachability in instance_reachabilities:
        print(instance_reachability)
    
    # The function executed successfully, so responde with 'Success'.
    return {
        'statusCode': 200,
        'body': "Lambda function executed successfully."
    }