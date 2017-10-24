#!/usr/bin/env python3

import boto3
import time
import subprocess
import os
from utils import input_int
from utils import clear
from utils import add_header
from utils import return_menu
from utils import get_sec_group
from utils import get_key

# Declaring ec2 and s3 variable
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

# To create an instance and add a tag to it after creation
def create_instance():
    add_header("Creating Instance")
    # function to get the key path and key name
    (key_dir, key_nm) = get_key()
    value = input("Enter instance tag name:\n> ")
    # Holds tag info
    tags = [{'Key': 'Name', 'Value': value}]
    # Used for TagSpecification field to name the instance
    tag_spec = [{'ResourceType': 'instance', 'Tags': tags}]
    
    # gets the users security group that allows port 80 and 22
    port_list = ['80', '22']
    sec_grp_id = get_sec_group(port_list)
    # A try/except to prevent the script from crashing
    try:
        # creation of instance
        instance = ec2.create_instances(
            ImageId='ami-acd005d5',
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[sec_grp_id],
            KeyName=key_nm,
            TagSpecifications=tag_spec,
            UserData='''#!/bin/bash
                yum -y update
                yum -y install nginx
                yum -y install python35
                service nginx start
                chkconfig nginx on
                touch home/ec2-user/testFile''',
            InstanceType='t2.micro')
        
        print("Created an instance with ID:", instance[0].id)
        time.sleep(5)
        instance[0].reload()
        inst_ip = instance[0].public_ip_address
        print("Public IP address:", inst_ip)
        
        # ssh_cmd = "ssh -i %s ec2-user@%s '%s'"
        
        cmd = "ssh -o StrictHostKeyChecking=no -i" + key_dir + " ec2-user@" + inst_ip + " 'pwd'"
        time.sleep(60)
        (status, output) = subprocess.getstatusoutput(cmd)
        print(output)
        
        scp_cmd = "scp -i " + key_dir + " check_webserver.py ec2-user@" + inst_ip + ":."
        (status, output) = subprocess.getstatusoutput(scp_cmd)
        if status > 0:
            print("check_webserver.py was not added to instance")
        else:
            print("Copied check_webserver.py to instance")
        
        return inst_ip
        
    except Exception as error:
        print(error)
    

# Function to run the check_webserver.py file that's stored in the EC2 instance
def run_check_webserver(inst_ip):
    add_header("Checking Webserver")
    # function to get the key path and key name
    (key_dir, key_nm) = get_key()
    run_check = 'ssh -i ' + key_dir + ' ec2-user@' + inst_ip + ' python3 check_webserver.py'
    os.system(run_check)

    
# Function to create a new bucket
def new_bucket():
    add_header("Creating Bucket")
    # a while loop incase the user's bucket name in already taken or incorrect syntax
    while True:
        # asks for user to input bucket name
        print("\nBack to menu type: ex")
        be_name = input("Enter Bucket name: ")
        # if user types "ex" it'll exit out of the create_bucket() function
        if be_name == "ex":
            return
            
        # A try/except to prevent the script from crashing
        try:
            # Creates a bucket and setting its location to the Ireland servers
            response = s3.create_bucket(Bucket=be_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
            # prints out its result to console for user
            print("\nBucket successfully created!")
            print(response)
            return
        except Exception as error:
            # prints out error to console for user
            print("ERROR: \n" + str(error))


# To upload an object to a specified bucket
def put_bucket(bucket, path):
    # A try/except to prevent the script from crashing
    try:
        print("\nUploading files...\n")
        # checks if path is a directory
        if os.path.isdir(path):
            # if true it'll loop through the directory and upload each file within it
            for root, dirs, files in os.walk(path):
                for file in files:
                    full_path  = os.path.join(root + '/' + file)
                    s3.meta.client.upload_file(full_path, bucket, file)
                    print("Uploaded: " + file)
        
        # if path points to a specific file
        else:
            s3.Object(bucket, path).put(Body=open(path, 'rb'))
            # prints out its result to console for user
            print("Uploaded: " + os.path.basename(path))
        
    except Exception as error:
        # prints out error to console for user
        print(error)


def list_buckets():
    bucket_list = []
    
    for bucket in s3.buckets.all():
        bucket_list.append(bucket.name)
    
    if len(bucket_list) == 1:
        print(bucket_list[0])
    
    elif len(bucket_list) > 1:
        max_w = 33
        w = 25
    
        title = "|%s|" % "Bucket List".center(max_w)
        dec = "+%s+" % ("-"*max_w)
        col_names = "|%s|%s|" % ("#".center(7), "Name".center(w))
    
        list_str = ""
        for bucket in bucket_list:
            index = str(bucket_list.index(bucket))
            line = "|%s|%s|" % (index.center(7), bucket.center(w))
            list_str += "\n" + line
    
        print(dec + "\n" + title + "\n" + dec + "\n" + col_names + "\n" + dec + list_str + "\n" + dec)
        i = input_int("Select bucket number(#):\n> ", len(bucket_list))
        # checks user input
        if i == "ex":
            return
        else:
            return bucket_list[int(i)]
    # if 0 buckets are found this is printed to console
    else:
        print("No buckets detected!")


def list_instances():
    inst_list = []
    
    # For each loop to collect and store all instances of the user
    for inst in ec2.instances.all():
        if inst.state['Name'] == "running":
            inst_tup = (inst.tags[0]['Value'], inst.id, inst.public_ip_address, inst.state['Name'])
            inst_list.append(inst_tup)
        # if instance is not running it sets the ip to a blank string to avoid null pointer errors
        else:
            inst_tup = (inst.tags[0]['Value'], inst.id, "", inst.state['Name'])
            inst_list.append(inst_tup)
    
    #if there is only 1 instance it doesn't print out a list and will return it straight away
    if len(inst_list) == 1:
        return inst_list[0]
    
    elif len(inst_list) > 1:
        # max width of list card that will display the list
        # in a neat and structured format
        max_w = 111
        # width of columns
        w = 25
        # header title
        title = "|%s|" % "Instance List".center(max_w)
        # decoration will print similar to: +-----------------+
        dec = "+%s+" % ("-"*max_w)
        # coloum headers are centered before added into the string
        col_names = "|%s|%s|%s|%s|%s|" % ("#".center(7), "Name".center(w), "ID".center(w), "Public IP".center(w), "State".center(w))
        #will store the instance info rows
        list_str = ""
        # loops through the found instances
        for inst in inst_list:
            # getting the index of instance
            index = str(inst_list.index(inst))
            # similar to col_names above. centering before adding to string as character width will vary
            line = "|%s|%s|%s|%s|%s|" % (index.center(7), inst[0].center(w), inst[1].center(w), inst[2].center(w), inst[3].center(w))
            # line variable is added to list_str
            list_str += "\n" + line
        # all the gathered and formatted data is then printed to console
        print(dec + "\n" + title + "\n" + dec + "\n" + col_names + "\n" + dec + list_str + "\n" + dec)
        # User is then asked for input
        print("\nExit: ex")
        i = input_int("Select instance number(#):\n> ", len(inst_list))
        
        # checks user input
        if i == "ex":
            return
        else:
            return inst_list[int(i)]
    # if 0 instances are found this is printed to console
    else:
        print("No instances detected!")


# Creates new instance, copies check_webserver.py to instance and runs it remotely
# function is created to avoid duplication as code is used in menu option 1 & 4
def new_instance():
    clear()
    # function creates a new instance and returns the public IP
    inst_ip = create_instance()
    time.sleep(15)
    # .py file that is copied to instance is run remotely through ssh
    run_check_webserver(inst_ip)


def main():

    while True:
        menu = open('menu.txt', 'rU')
        print(menu.read())
        menu_in = input_int("> ", 6)
        
        #------------------------------------------------------------------------#
        # Option 1: CREATE INSTANCE AND BUCKET
        # When instance is made, check_webserver.py is added and run
        if menu_in == "1":
            # create_instance() and run_check_webserver() functions
            new_instance()
            time.sleep(5)
            # function creates new bucket
            new_bucket()
            return_menu()
            
        #------------------------------------------------------------------------#
        # Option 2: CHECK WEBSERVER
        # User will select an instance and run_check_webserver() will be called
        elif menu_in == "2":
            clear()
            # function asks for user input and returns the selected instance
            inst = list_instances()
            # Checks if at lease 1 instance was returned
            if inst is not None:
                # A try/except to prevent the script from crashing
                try:
                    # Will call function to ssh to instance and run the .py file stored on it
                    run_check_webserver(inst[2])
                except Exception as error:
                    # prints out error to console for user
                    print(error)
                
            input("\nPress Enter to return to menu...")
            return_menu()
            
        #------------------------------------------------------------------------#
        # Option 3: UPLOAD TO BUCKET
        # asks for path to file to be uploaded, has user pick bucket
        elif menu_in == "3":
            clear()
            add_header("Upload to Bucket")
            to_dir = input("Enter file path\n> ")
            if os.path.exists(to_dir):
                bucket = list_buckets()
                if bucket is not None:
                    # A try/except to prevent the script from crashing
                    try:
                        put_bucket(bucket, to_dir)
                        input("\nPress enter to return to menu...")
                    except Exception as error:
                        # prints out error to console for user
                        print(error)
            else:
                print("Invalid path input: " + to_dir)
            
            return_menu()
            
        #------------------------------------------------------------------------#
        # Option 4:
        # runs new_instance() without the new_bucket()
        elif menu_in == "4":
            new_instance()
            return_menu()
            
        #------------------------------------------------------------------------#
        # runs new_instance() without the new_bucket()
        elif menu_in == "5":
            clear()
            new_bucket()
            return_menu()
            
        #------------------------------------------------------------------------#
        # exits and ends script
        elif menu_in == "ex":
            print("\nExiting...")
            time.sleep(3)
            print("Goodbye.")
            break
        #------------------------------------------------------------------------#
        else:
            continue
    
if __name__ == "__main__":
    main()