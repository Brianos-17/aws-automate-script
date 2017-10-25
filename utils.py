#!/usr/bin/env python3

import os
import time
import boto3
import subprocess
ec2 = boto3.resource('ec2')


# prompt: Message for user high: the max number input can't go over
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
# It returns the ID of the group with the appropriate port numbers
def get_sec_group(port_list):
    sec_list = []
    ec2_client = boto3.client('ec2')
    sec_grps = ec2_client.describe_security_groups()
    
    # Loops through the user's security groups
    for group in sec_grps['SecurityGroups']:
        
        ip_perms = group['IpPermissions']
        perms = []
        # loop through available port numbers within the security group
        for port in ip_perms:
            # Checking is there is a FromPort field as some dont
            if 'FromPort' in port:
                # Adds port to list
                perms.append(str(port['FromPort']))
        # tuple variable
        sec_tup = (group['GroupId'], perms)
        # adding tuple to list
        sec_list.append(sec_tup)
    
    # sorting and joining the port_list param
    port_join = ''.join(sorted(port_list))
    grp_id = ''
    # loops through list of tuples and compares the ports to the port_list param
    for group in sec_list:
        ports = ''.join(sorted(group[1]))
        # if the ports match then the security group id will be returned
        if ports == port_join:
            grp_id = group[0]
            break
    
    if len(grp_id) == 0:
        print("No appropriate security group found, making a new one")
        return make_sec_group(port_list)
    else:
        return grp_id


# makes a new security group that allow ports 80 and 22
def make_sec_group(port_list):
    # assigning group name
    port_join = ''.join(sorted(port_list))
    group_name = "auto-secure-group-" + port_join
    # initial creation of security group
    new_sg = ec2.create_security_group(GroupName=group_name, Description='automated secure group')
    # opening of ports 80 and 22
    for port in port_list:
        new_sg.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0", FromPort=int(port), ToPort=int(port))
        
    # searches security groups for the one just created
    grp_cmd = 'aws ec2 describe-security-groups ' \
              '--filters Name=group-name,Values=' + group_name + ' ' \
              '--query "SecurityGroups[*].[GroupId]"'
    (status, output) = subprocess.getstatusoutput(grp_cmd)
    # returns security group id
    return output


# pulls path from key_dir.txt
def get_key():
    # checking if a certain text file exists and will create one if there isn't
    if valid_key():
        key_dir = open('key_dir.txt', 'r+')
        path = key_dir.read()
        
        name = os.path.basename(path)
        name = name[:-4]
        return path, name


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
    print("\n"*20)


# Used by functions to give a clear heading to improve UX
def add_header(title):
    # total width of header = title length * 2
    h_width = len(title)*2
    # a variable that stores the text portion of the title and has it centered
    h_title = str(title).center(h_width + 2)
    # stores a simple decoration that will be printed before and after h_title
    h_dec = "\n+%s+\n" % ("-"*h_width)
    
    # +--------------+
    #      title
    # +--------------+
    print(h_dec + h_title + h_dec)
