#!/usr/bin/python3

import sys
import boto3

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
        ec2.create_instances(
            ImageId = 'ami-acd005d5',
            MinCount = 1,
            MaxCount = 1,
            TagSpecifications = tag_spec,
            InstanceType = 't2.micro'
        )
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