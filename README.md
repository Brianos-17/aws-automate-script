# Create, Launch and Monitor Script for AWS
## Assignment for Developer Operations

#### Core assignemnt spec:

To automate, using Python3, the process of creating, launching and monitoring a public-facing web server in Amazon cloud.
The web server will run on an EC2 instance and display static conent that is stored in S3. 

#### Details:
##### run_newwebserver.py:
- To launch a new Amazon EC2 micro instance with a free tier Amazon Linux AMI
- Using Boto3 API & Amazon credentials
- Launches into appropriate security group
- Accessible using SSH key
- Create an S3 bucket and copy an image up to bucket
- Configure nginx home page should then display this image 

##### User Data start-up script:

- Used when creating instance
- Apply required patches to OS
- Install nginx web server

##### check_webserver.py:

- Program uses scp tp copy check_webserver.py script from your machine to the new instance and then execute
- EG: Using ssh remote command execution
- Connecting via ssh/scp requires public IP or DNS name of your instance
- If it detects nginx isn't running then it should be started up