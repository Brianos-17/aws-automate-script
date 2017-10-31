# Create, Launch and Monitor Script for AWS
## Assignment for Developer Operations

### Instructions:

##### Starting Up
Start up run_newwebserver.py.
You will be asked for the path to your key.pem file. 
It will store the path in .txt file so don't worry if you start up and it doesn't ask for it again

##### Creating an Instance
When creating a new instance the script will search your security groups associated with your default VPC
It is known to cause an Auth error when trying to retrieve the security groups. If you get a similar message then
you'll have to manually input your security group ID in the new_instance()


### Core assignemnt spec:

To automate, using Python3, the process of creating, launching and monitoring a public-facing web server in Amazon cloud.
The web server will run on an EC2 instance and display static conent that is stored in S3. 

### Details:
##### run_newwebserver.py:
- To launch a new Amazon EC2 micro instance with a free tier Amazon Linux AMI
- Using Boto3 API & Amazon credentials
- Launches into appropriate security group
- Accesses your instance using SSH key
- Creates an S3 bucket and copy an image up to bucket
- Configure nginx home page should then display this image 

##### User Data start-up script:

- Used when creating instance
- Apply required patches to OS
- Installs nginx web server
- Installs python35

##### check_webserver.py:

- Copied and stored on instance when the instance is created
- Checks is nginx is running and asks user if they wish to run/stop nginx