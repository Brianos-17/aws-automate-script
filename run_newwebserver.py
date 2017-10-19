#!/usr/bin/python3

import sys
import boto3
import time
import subprocess

# Declaring ec2 variable
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

# To create an instance and add a tag to it after creation
def create_instance():
    # string to hold instance name
    value = 'instance name here'
    # Holds tag info
    tags = [{'Key': 'Name', 'Value': value}]
    # Used for TagSpecification field to name the instance
    tag_spec = [{'ResourceType': 'instance', 'Tags': tags}]

    # A try/except to prevent the script from crashing
    try:
        #creation of instance
        instance = ec2.create_instances(
            ImageId = 'ami-acd005d5',
            MinCount = 1,
            MaxCount = 1,
            SecurityGroupIds= ['sg-872f06ff'],
            KeyName = "lab00key",
            TagSpecifications = tag_spec,
            UserData = '''#!/bin/bash
                yum -y update
                yum -y install nginx
                service nginx start
                chkconfig nginx on
                touch home/ec2-user/testFile''',
            InstanceType = 't2.micro')
        
        print("An instance with ID", instance[0].id, "has been created.")
        time.sleep(5)
        instance[0].reload()
        print("Public IP address:", instance[0].public_ip_address)
        
        cmd = "ssh -o StrictHostKeyChecking=no -i lab00key.pem ec2-user@" + instance[0].public_ip_address + " 'pwd'"
        time.sleep(60)
        (status, output) = subprocess.getstatusoutput(cmd)
        print(output)
        
    except Exception as error:
        print(error)
    
    
# Function to create a new bucket
# TODO: create while loop incase bucket name is not unique
def create_bucket(name):
    # A try/except to prevent the script from crashing
    try:
        # Creates a bucket naming it with the 'name' param and setting its location to the Ireland servers
        response = s3.create_bucket(Bucket=name, CreateBucketconfiguration={'LocationConstraint': 'eu-west-1'})
        # prints out its result to console for user
        print(response)
    except Exception as error:
        # prints out error to console for user
        print(error)


# To upload an object to a specified bucket
def put_bucket(bucket, file):
    # A try/except to prevent the script from crashing
    try:
        # uploading file to the specified bucket
        response = s3.Object(bucket, file).put(Body=open(file, 'rb'))
        # prints out its result to console for user
        print(response)
    except Exception as error:
        # prints out error to console for user
        print(error)
    
    
def main():
    create_instance()
    
    
if __name__ == "__main__":
    main()