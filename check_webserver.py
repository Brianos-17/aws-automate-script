#!/usr/bin/python3

import sys
import boto3
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

def main():
    print('Hello')

if __name__ == "__main__":
    main()