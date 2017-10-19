#!/usr/bin/env python3

import sys
import boto3
import time
import subprocess
import os

# Declaring ec2 variable
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

key_dir = ""
inst_ip = ""

# To create an instance and add a tag to it after creation
def create_instance():
    key = "lab00key"
    key_dir = "~/comp_sci/dev-ops/lab00key.pem"
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
            KeyName = key,
            TagSpecifications = tag_spec,
            UserData = '''#!/bin/bash
                yum -y update
                yum -y install nginx
                yum -y install python35
                service nginx start
                chkconfig nginx on
                touch home/ec2-user/testFile''',
            InstanceType = 't2.micro')
        
        print("Created an instance with ID:", instance[0].id)
        time.sleep(5)
        instance[0].reload()
        inst_ip = instance[0].public_ip_address
        print("Public IP address:", inst_ip)
        
        #ssh_cmd = "ssh -i %s ec2-user@%s '%s'"
        
        cmd = "ssh -o StrictHostKeyChecking=no -i" + key_dir + " ec2-user@" + inst_ip + " 'pwd'"
        time.sleep(40)
        (status, output) = subprocess.getstatusoutput(cmd)
        print(output)
        
        add_check_webserver(key_dir, inst_ip)
        
        return (key_dir, inst_ip)
        
    except Exception as error:
        print(error)
    

def add_check_webserver(key_dir, inst_ip):
    scp_cmd = "scp -i " + key_dir + " check_webserver.py ec2-user@" + inst_ip + ":."
    (status, output) = subprocess.getstatusoutput(scp_cmd)
    if status > 0:
        print("check_webserver.py was not added to instance")
    else:
        print("check_webserver.py copied to instance")
        
def run_check_webserver(key_dir, inst_ip):
    run_check = 'ssh -i ' + key_dir + ' ec2-user@' + inst_ip + ' python3 check_webserver.py'
    os.system(run_check)
    
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
    (key_dir, inst_ip) = create_instance()
    print("Checking nginx status...")
    time.sleep(15)
    run_check_webserver(key_dir, inst_ip)
    
if __name__ == "__main__":
    main()