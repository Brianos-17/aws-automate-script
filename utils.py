#!/usr/bin/env python3

import time
import boto3
import subprocess
ec2 = boto3.resource('ec2')

# prompt: Message for user
# high: the max number input can't go over
def input_int(prompt, max):
    while True:
        # asks user for input
        int_input = input(prompt)
        
        if int_input == "ex":
            return int_input
        
        # checks to make sure user input is only a number
        # if not then it restarts loop
        if not int_input.isdigit() or int(int_input) >= max:
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
            #Checking is there is a FromPort field as some dont
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
            grp_id =  group[0]
            break
    
    if len(grp_id) == 0:
        print("No appropriate security group found, making a new one")
        return  make_sec_group(port_list)
    else:
        return grp_id

# makes a new security group that allow ports 80 and 22
def make_sec_group(port_list):
    #assigning group name

    port_join = ''.join(sorted(port_list))
    group_name = "auto-secure-group-" + port_join
    # initial creation of security group
    new_sg = ec2.create_security_group(GroupName=group_name,Description='automated secure group')
    # opening of ports 80 and 22
    for port in port_list:
        new_sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=int(port),ToPort=int(port))
        
    # searches security groups for the one just created
    grp_cmd = 'aws ec2 describe-security-groups ' \
              '--filters Name=group-name,Values='+ group_name + ' ' \
              '--query "SecurityGroups[*].[GroupId]"'
    (status, output) = subprocess.getstatusoutput(grp_cmd)
    # returns security group id
    return(output)


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