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