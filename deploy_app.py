import boto3
import paramiko
import urllib.request
import time

# Connect to EC2
# Create an EC2 client
ec2 = boto3.client(
    'ec2',
    region_name='us-east-1'
    #aws_access_key_id and aws_secret_access_key has to be alredy added to the aws configure on your PC!
    # In addition, make sure that your computer time is synced with aws time. if not, it wont work - credential error. 
)

# Create a new security group
security_group = ec2.create_security_group(
    GroupName='my-parkinglot-app-security-group',
    Description='My Parking Lot App Security Group'
)

# get public IP address
my_ip = urllib.request.urlopen('http://checkip.amazonaws.com/').read().decode('utf-8').strip()

# authorize inbound traffic to security group from my IP address only
ec2.authorize_security_group_ingress(
    GroupId=security_group['GroupId'],
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': my_ip + '/32'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': my_ip + '/32'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 5000,
            'ToPort': 5000,
            'IpRanges': [{'CidrIp': my_ip + '/32'}]
        }
    ]
)

# Create a new key pair
key_pair = ec2.create_key_pair(KeyName='my-parkinglot-app-key-pair')

# Save the private key to a file
with open('my-parkinglot-app-key-pair.pem', 'w') as file:
    file.write(key_pair['KeyMaterial'])

# Launch a new EC2 instance
instance = ec2.run_instances(
    ImageId='ami-007855ac798b5175e',
    InstanceType='t2.micro',
    KeyName='my-parkinglot-app-key-pair',
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[security_group['GroupId']]
)['Instances'][0]

# Add a name tag to the instance
instance_id = instance['InstanceId']
instance_name = 'my-instance-parkinglot-app'
ec2.create_tags(
    Resources=[instance_id],
    Tags=[
        {'Key': 'Name', 'Value': instance_name},
    ]
)

# Wait for the instance to be running
instance_id = instance['InstanceId']
status = ''
while status != 'running':
    response = ec2.describe_instances(InstanceIds=[instance_id])
    status = response['Reservations'][0]['Instances'][0]['State']['Name']
    if status == 'running':
        break
    time.sleep(10)  # Wait for 10 seconds before checking again

# Wait for the instance to have an IP address
while True:
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    if 'PublicIpAddress' in instance:
        break
    time.sleep(5)

time.sleep(10)

# Connect to the instance via SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=instance['PublicDnsName'],
    username='ubuntu',
    key_filename='my-parkinglot-app-key-pair.pem'
)

# Execute commands on instance using SSH
commands = [
    'sudo apt-get update',
    'sudo apt-get install -y python3-pip git',
    'git clone https://github.com/yongarber/cloud-computing-ex1.git',
    'cd cloud-computing-ex1 && git pull',
    'sudo pip3 install -r cloud-computing-ex1/requirements.txt',
    'nohup sudo python3 cloud-computing-ex1/server.py > server.log 2>&1 &',
    'echo Running Application',
    'echo Please use POST http://{ip}:443/entry?plate=123-123-123\&parkingLot=382'.format(ip = instance['PublicIpAddress'])
]
for command in commands:
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())

# Close SSH connection
ssh.close()