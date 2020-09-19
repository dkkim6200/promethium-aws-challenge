import sys
import boto3
from boto3 import ec2
import socket

#listOfInstances=""
#messages="Following Instances have port 22 open"

class InstanceReachability:
    def __init__(self, instance_id, private_ip_address, reachable):
        self.instance_id = instance_id
        self.private_ip_address = private_ip_address
        self.reachable = reachable
    
    def __str__(self):
        return "Instance " + self.instance_id + " with private IP address " + self.private_ip_address + " at port 22 is " + ("reachable." if self.reachable else "not reachable.")
        

def lambda_handler(event, context):
    instance_reachabilities = []
    
    connection = boto3.client('ec2', region_name='us-east-2')
    response = connection.describe_instances()
    
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            reachable = False
            
            security_group_ids = list((group["GroupId"] for group in instance["SecurityGroups"]))
            for sg in connection.describe_security_groups(GroupIds = security_group_ids)["SecurityGroups"]:
                for rule in sg["IpPermissions"]:
                    if (rule["FromPort"] == 22 and rule["ToPort"] == 22) and all(ip_range["CidrIp"] == "0.0.0.0/0" for ip_range in rule["IpRanges"]):
                        reachable = instance["State"]["Name"] == "running"
            
            instance_reachability = InstanceReachability(instance["InstanceId"], instance["PrivateIpAddress"], reachable)
            instance_reachabilities.append(instance_reachability)
    
    for instance_reachability in instance_reachabilities:
        print(instance_reachability)
        
    return {
        'statusCode': 200,
        'body': "Lambda function executed successfully."
    }