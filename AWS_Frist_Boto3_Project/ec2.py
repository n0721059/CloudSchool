from subprocess import run,PIPE
from os import system
from welcome import welcome
from colorama import Fore, Back, Style
import boto3
import time

def attach_ebs(instance_id,volume_id,device):
    attach_out = run(f"aws ec2 attach-volume --device {device} "
                     f"--instance-id {instance_id} "
                     f"--volume-id {volume_id}",shell=True,capture_output=True)
    if attach_out.returncode == 0 :
        print(Fore.GREEN + f"\nSuccess\n{attach_out.stdout.decode()}")
        print(Style.RESET_ALL)
    else :
        print(Fore.RED + f"Failed\nError :\n{attach_out.stderr.decode()}")
        print(Style.RESET_ALL)

    input("Enter to continue....")

def create_ebs_volume(availability_zone,size,volume_type) :
    ebs_out = run(f"aws ec2 create-volume --availability-zone {availability_zone} --size {size} --volume-type {volume_type}",shell=True,capture_output=True)
    if ebs_out.returncode == 0 :
        print(Fore.GREEN + f"\nSuccess\n{ebs_out.stdout.decode()}")
        print(Style.RESET_ALL)
    else :
        print(Fore.RED + f"Failed\nError :\n{ebs_out.stderr.decode()}")
        print(Style.RESET_ALL)

    input("Enter to continue....")


def add_ingress_rule(sg_id,protocol,toport,cidr):
    ingress_out = run(f"aws ec2 authorize-security-group-ingress --group-id {sg_id} --protocol {protocol} --port {toport} --cidr {cidr}",shell=True,capture_output=True)
    if ingress_out.returncode == 0 :
        print(Fore.GREEN + f"\nSuccessfully Added Rule")
        print(Style.RESET_ALL)
    else :
        print(Fore.RED + f"Failed\nError :\n{ingress_out.stderr.decode()}")
        print(Style.RESET_ALL)

    input("Enter to continue....")

def create_security_group(sg_name,description):
    sg_out = run(f"aws ec2 create-security-group --group-name {sg_name} --description \"{description}\"",shell=True,capture_output=True)
    if sg_out.returncode == 0 :
        print(Fore.GREEN + f"\n\nSuccess\n{sg_out.stdout.decode()}")
        print(Style.RESET_ALL)
    else :
        print(Fore.RED + f"Failed\nError :\n{sg_out.stderr.decode()}")
        print(Style.RESET_ALL)

    print(Fore.YELLOW + "\n\nADD INGRESS OPTION IS RECOMMENDED TO DO NEXT\n")
    print(Style.RESET_ALL)
    input("Enter to continue....")

def create_key_pair(key_name):
    key_out = run(f"aws ec2 create-key-pair --key-name {key_name} --query 'KeyMaterial' --output text > {key_name}",shell=True,capture_output=True)
    key_exe = run(f"chmod 400count {key_name}",shell=True,capture_output=True)
    if key_out.returncode == 0 and key_exe.returncode == 0:
        print(Fore.GREEN + f"\n\nSuccess\n{key_out.stdout.decode()}")
        print(Style.RESET_ALL)
    else :
        print(Fore.RED + f"Failed\nError :\n{key_out.stderr.decode()}")
        print(Style.RESET_ALL)
    input("Enter to continue....")

def launch_instance(security_group,key_pair,count,instance_type="t2.micro",image_id= "ami-0d593311db5abb72b"):
    if image_id == "" or " " :
        image_id = 'ami-0d593311db5abb72b'
    # if count == "" or " ":
    #     count = "1"
    if instance_type == "" or " " :
        instance_type = "t2.micro"
    print(Fore.GREEN + "\nLaunching EC2\n")
    print(Style.RESET_ALL)


    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(
                    ImageId=image_id,  # ami-0d593311db5abb72b
                    MinCount=int(count),  # specifies the minimum number of EC2 instances you want to create
                    MaxCount=int(count),  # specifies the maximum number of EC2 instances you want to create.
                    InstanceType="t2.micro",
                    KeyName=key_pair,
                    SecurityGroupIds = [security_group]
                )
    for instance in instances:
        print(f" {instance_type} \t id {instance.id} is been launched.")
       # print('please wait for instance to be started')
       # instance.wait_until_running()
        print(f'EC2 instance "{instance.id}" has been started')

    input("Enter to continue....")


def list_all_instances():


    client = boto3.client('ec2')
    Myec2 = client.describe_instances()
    for pythonins in Myec2['Reservations']:
         for printout in pythonins['Instances']:
            if printout['State']['Name'] == 'running':
                print(Fore.GREEN + printout['InstanceId'], end='\t')
                print(Style.RESET_ALL, end='')
            else:
                print(Fore.RED + printout['InstanceId'], end='\t')
                print(Style.RESET_ALL, end='')

            print(printout['InstanceType'], end='\t')
            print(printout['State']['Name'])
    input("Enter to continue....")

def terminate_instance(ec2_id):
    ec2_resource = boto3.resource('ec2')
    running_instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    found = False
    for instance in running_instances:
        if instance.instance_id == ec2_id:
            found = True
            instance.terminate()
            print(f"instance {ec2_id} is being terminated")
            break
    if not found:
        print(f"the given {ec2_id} does not match any running instance id ")
    input("Enter to continue....")

def terminate_all_instances():
    ec2_resource = boto3.resource('ec2')
    running_instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    running_instances.terminate()
    input("Enter to continue....")

def ec2():
    while True:
        system("clear")
        print(welcome("AWS EC2"))
        print("""Select from below : 
        1. Launch Instance
        2. Create Key Pair key 
        3. Create Security Group
        4. Add ingress rule
        5. Create EBS Volume
        6. Attach EBS Volume
        7. list all instances
        8. terminate instance
        9. terminate all instances
        10. Go back""")
        choice = input("\nEnter your choice : ")
        if choice == '1' :
            image_id = input("\nEnter Image ID [default Amazon Linux 2]: ")
            count = int(input("Enter no. of instances to launch [default 1]: "))
            print(Fore.GREEN + "\nAvailable Security Groups : \n")
            run("aws ec2 describe-security-groups --query \"SecurityGroups[*].[GroupId,GroupName]\" --output text",shell=True,text=True)
            print(Style.RESET_ALL)
            security_group = input("Enter the security group ids : ")
            print(Fore.GREEN + "\nAvailable Key Pairs : \n")
            run("aws ec2 describe-key-pairs --key-names --query KeyPairs[*].KeyName --output text",shell=True,text=True)
            print(Style.RESET_ALL)
            key_pair = input("Enter name of key-pair : ")
            instance_type = input("Enter the instance type [default t2.micro]: ")
            launch_instance(security_group,key_pair,count,instance_type,image_id)
        elif choice == '2':
            key_name = input("Enter your Key name : ")
            create_key_pair(key_name)
        elif choice == '3' :
            sg_name = input("Enter the Secrity Group name : ")
            description = input("Enter Security Group Descrition : ")
            create_security_group(sg_name,description)
        elif choice == '4' :
            print(Fore.GREEN + "\nAvailable Security Groups : \n")
            run("aws ec2 describe-security-groups --query \"SecurityGroups[*].[GroupId,GroupName]\" --output table",shell=True,text=True)
            print(Style.RESET_ALL)
            sg_id = input("Enter Security Group ID : ")
            protocol = input("Enter Protcol : ")
            toport = input("Enter Port : ")
            cidr = input("Enter CIDR block [x.x.x.x/x]: ")
            add_ingress_rule(sg_id,protocol,toport,cidr)
        elif choice == '5' :
            print(Fore.GREEN + "\nListing Availability Zones : \n")
            run("aws ec2 describe-availability-zones --query \"AvailabilityZones[*].ZoneName\" --output table",shell=True,text=True)
            print(Style.RESET_ALL)
            availability_zone = input("Enter the Availability Zone : ")
            size = input("Enter the size (in GiB) : ")
            volume_type = input("Enter the Volume type : ")
            create_ebs_volume(availability_zone,size,volume_type)
        elif choice == '6' :
            print(Fore.GREEN + "\nListing Currently Running Instances : \n")
            run("aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query \"Reservations[].Instances[*].[InstanceId,Tags[*].Value]\" --output table",shell=True,text=True)
            print(Style.RESET_ALL)
            instance_id = input("Enter Instance ID : ")
            print(Fore.GREEN + "\nListing Available status Volumes Only : \n")
            run("aws ec2 describe-volumes --filters Name=status,Values=available --query \"Volumes[*].[VolumeId,Tags[*].Value]\" --output table",shell=True,text=True)
            print(Style.RESET_ALL)
            volume_id = input("Enter Volume ID : ")
            device = input("Enter Device name [ex : /dev/sdh or /dev/xvdh]: ")
            attach_ebs(instance_id,volume_id,device)
        elif choice == '7':
            list_all_instances()
        elif choice == '8':
            print(Fore.GREEN + "\nListing Currently Running Instances : \n")
            run("aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query \"Reservations[].Instances[*].[InstanceId,Tags[*].Value]\" --output table",
                shell=True, text=True)
            print(Style.RESET_ALL)
            instance_id = input("Enter Instance ID to be terminated : ")
            terminate_instance(instance_id)
        elif choice == '9':
            terminate_all_instances()
        elif choice == '10':
            return
        system("clear")


