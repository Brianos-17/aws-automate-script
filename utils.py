#!/usr/bin/env python3

import os
import time
import boto3
import subprocess
ec2 = boto3.resource('ec2')

# used to check if what the user input is a valid integer
# prompt: Message for user
# high: the max number input can't go over
def input_int(prompt, max_in):
    while True:
        # asks user for input
        int_input = input(prompt)
        
        if int_input == "ex":
            return int_input
        
        # checks to make sure user input is only a number
        # if not then it restarts loop
        if not int_input.isdigit() or int(int_input) >= max_in:
            print('Invalid input: ' + str(int_input) + '\n')
            continue
        else:
            return int_input


# A function to search user's security groups
# It returns the ID of the group with port numbers matching in param port_list
# This function loops through all of the user's security groups, it runs the first loop
# to check if the Sec Group has any open ports AND belongs to the Default VPC
# There is then a second loop that checks for a Sec Group that has ports 80 and 22 open ONLY
def get_sec_group(port_list):
    ec2_client = boto3.client('ec2')
    sec_grps = ec2_client.describe_security_groups()['SecurityGroups']
    default_vpc_id = ''

    # searching for user's default VPC id
    for vpc in ec2.vpcs.all():
        if vpc.is_default:
            # puts the VPC's ID into a variable to be used later
            default_vpc_id = vpc.vpc_id
            print("Default VPC ID: " + default_vpc_id)
            break

    grp_id = ''
    # This loops though the user's security groups and stores the Security Group's ID and their open Ports into a list
    # Each security group can have a varying amount of open ports, one could have 0 open ports, another could have ports 22, 25, 80
    # This loop filters out all security groups that either dont have ANY ports open AND if they belong to the Defualt VPC
    for group in sec_grps:
        
        # checks if the security group is in the default VPC group
        if group['VpcId'] == default_vpc_id:
            open_ports = []
            # loop through available port numbers within the security group
            for port in group['IpPermissions']:
                # Checking is there is a FromPort field as some dont
                if 'FromPort' in port:
                    # Adds port to list
                    # reason for list is so it can be sorted later
                    open_ports.append(str(port['FromPort']))
            
            # checking if any open ports were found
            if len(open_ports) > 0:
                # sorting of port_list param and open_ports variable
                port_list_srt = ''.join(sorted(port_list))
                open_ports_srt = ''.join(sorted(open_ports))
                
                # if found open_ports match the param port_list then
                # it'll assign the Sec Group ID to grp_id and break from the loop
                if open_ports_srt == port_list_srt:
                    grp_id = group['GroupId']
                    break
    
    # this checks if an appropriate security group was found
    # if none are found then one is made
    if len(grp_id) == 0:
        print("No appropriate security group found, making a new one")
        return make_sec_group(port_list)
    else:
        return grp_id


# makes a new security group that open the ports passed in from param port_list
# port_list is currently [80, 22]
def make_sec_group(port_list):
    print("So security group with just ports 80 and 22 were found.")
    print("Making an appropriate one now...")
    # assigning group name
    port_join = ''.join(sorted(port_list))
    group_name = "auto-secure-group-" + port_join
    # initial creation of security group
    new_sg = ec2.create_security_group(GroupName=group_name, Description='automated secure group')
    # the for loop goes through the ports from param port_list and will open them
    for port in port_list:
        new_sg.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=int(port), ToPort=int(port))
        
    # searches the ID of the security group just created
    # it uses 'group_name' as a filter
    grp_cmd = 'aws ec2 describe-security-groups ' \
              '--filters Name=group-name,Values=' + group_name + ' ' \
              '--query "SecurityGroups[*].[GroupId]"'
    (status, output) = subprocess.getstatusoutput(grp_cmd)
    # returns id of newly created security group
    if status == 0:
        print("Created Security Group: " +  group_name)
        return output
    else:
        print("Failed to create security group: " + group_name)
        print(output)


# pulls path from key_dir.txt
def get_key():
    # checking if a certain text file exists and will create one if there isn't
    if valid_key():
        key_dir = open('key_dir.txt', 'r+')
        path = key_dir.read()
        
        name = os.path.basename(path)
        name = name[:-4]
        return path, name


# this function seaches for a file called key_dir.txt which is used to store the absolute path of the user's .pem file
# it checks that the .txt file exists and then opens the file to read it
# if the .txt isn't found then one is created
# if the .txt file is blank or the stored path doesn't exist then it will ask the user to input a path
# the user cant escape from this loop until they input a valid path as the key file is required
def valid_key():
    # checking if a certain text file exists and will create one if there isn't
    if os.path.exists('key_dir.txt'):
        key_dir = open('key_dir.txt', 'r+')
    else:
        key_dir = open('key_dir.txt', 'w+')
    # reading the text from key_dir.txt
    path = key_dir.read()
    # If the text file is blank then it'll request a key path from the user before they can proceed
    if (len(path) == 0) or (not os.path.isfile(path)):
        # a while loop incase of invalid input
        add_header("No key detected")
        print("A key is required to use this service.")
        print("Please input the path to your key:")
        print("Note: If giving an absolute path use /home/[user]/to/dir instead of /~/to/dir/")
        while True:
            in_path = input("> ")
            # boolean to check if the path given leads to a file
            is_file = os.path.isfile(in_path)
            # boolean to ensure the given file ends in .pem
            is_key = os.path.basename(in_path)[-4:] == '.pem'
            
            # if both are true then it will add absolut path of the key to a text file
            if is_file and is_key:
                abs_path = os.path.abspath(in_path)
                print("Key Found: " + abs_path)
                # overwrites any data in the current text file
                key_dir = open('key_dir.txt', 'w')
                # writing to file
                key_dir.write(str(abs_path))
                return True
            # prompts user of invalid input and loops back
            else:
                print("\nInvalid input: " + in_path)
    else:
        return True


# A set of commands to avoid repeating code
def return_menu():
    print("\nReturning to menu...")
    time.sleep(5)
    clear()


# Adds 20 blank lines to console to clear it of unnecessary text
def clear():
    print("\n"*50)


# Used by functions to give a clear heading to improve UX
def add_header(title):
    # total width of header = title length * 2
    h_width = len(title)*2
    # a variable that stores the text portion of the title and has it centered
    h_title = str(title).center(h_width + 2)
    # stores a simple decoration that will be printed before and after h_title
    h_dec = "\n+%s+\n" % ("-"*h_width)
    
    # Result:
    # +--------------+
    #      title
    # +--------------+
    print(h_dec + h_title + h_dec)
