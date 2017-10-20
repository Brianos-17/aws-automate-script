#!/usr/bin/env python3

import sys
import boto3
import time
import subprocess
import os

# Declaring ec2 variable
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

#Used by functions to give a clear heading to improve UX
def add_header(title):
    #total width of header = title length * 2
    h_width = len(title)*2
    #a variable that stores the text portion of the title and has it centered
    h_title = str(title).center(h_width + 2, ' ')
    #stores a simple decoration that will be printed before and after h_title
    h_dec = "\n+%s+\n" % ("-"*h_width)
    
    # +--------------+
    #      title
    # +--------------+
    print(h_dec + h_title + h_dec)


# To create an instance and add a tag to it after creation
def create_instance():
    add_header("Creating Instance")
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

        scp_cmd = "scp -i " + key_dir + " check_webserver.py ec2-user@" + inst_ip + ":."
        (status, output) = subprocess.getstatusoutput(scp_cmd)
        if status > 0:
            print("check_webserver.py was not added to instance")
        else:
            print(" Copied check_webserver.py to instance")
        
        return (key_dir, inst_ip)
        
    except Exception as error:
        print(error)
    
# Function to run the check_webserver.py file that's stored in the EC2 instance
def run_check_webserver(key_dir, inst_ip):
    run_check = 'ssh -i ' + key_dir + ' ec2-user@' + inst_ip + ' python3 check_webserver.py'
    os.system(run_check)
    
# Function to create a new bucket
def create_bucket():
    is_unique = False
    # a while loop incase the user's bucket name in already taken or incorrect syntax
    while not is_unique:
        
        #asks for user to input bucket name
        print("\nBack to menu type: ex")
        be_name = input("Enter Bucket name: ")
        #if user types "ex" it'll exit out of the create_bucket() function
        if be_name == "ex":
            print("\nReturning to menu...")
            time.sleep(3)
            return
            
        # A try/except to prevent the script from crashing
        try:
            # Creates a bucket naming it with the 'name' param and setting its location to the Ireland servers
            response = s3.create_bucket(Bucket=be_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
            # prints out its result to console for user
            print("\nBucket successfully created!")
            print(response)
            is_unique = True
        except Exception as error:
            # prints out error to console for user
            print("ERROR: \n" + str(error))


# To upload an object to a specified bucket
def put_bucket(bucket, file):
    add_header("Uploading file to bucket")
    # A try/except to prevent the script from crashing
    if not bucket and not file:
        print("No bucket or file")
        
    try:
        # uploading file to the specified bucket
        response = s3.Object(bucket, file).put(Body=open(file, 'rb'))
        # prints out its result to console for user
        print(response)
    except Exception as error:
        # prints out error to console for user
        print(error)
    
    
def main():
    #(key_dir, inst_ip) = create_instance()
    #print("Checking nginx status...")
    #time.sleep(15)
    #run_check_webserver(key_dir, inst_ip)

    #print("\n+----------------+")
    #print("Creating a bucket")
    #print("+----------------+")
    #time.sleep(5)
    #create_bucket()
    #put_bucket(None, None)
    
if __name__ == "__main__":
    main()