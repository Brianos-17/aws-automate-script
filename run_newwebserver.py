#!/usr/bin/python3

import sys
import boto3

# Declaring ec2 variable
ec2 = boto3.resource('ec2')

# To create an instance and add a tag to it after creation
def create_instance():
    # string to hold instance name
    value = 'instance name here'
    
    #creation of instance
    new_instance = ec2.create_instances(
        ImageId = 'ami-acd005d5',
        MinCount = 1,
        MaxCount = 1,
        InstanceType = 't2.micro'
    )
    
    #naming of instance
    ec2.create_tags(Resources=[new_instance[0].id], Tags=[{'Key':'Name', 'Value': value}])

def main():
    create_instance()
    
    
if __name__ == "__main__":
    main()