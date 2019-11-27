import boto3
from botocore.exceptions import ClientError
import time
import os
from config import *

ec2 = boto3.client('ec2')
ec2ohio = boto3.client('ec2',region_name="us-east-2")

ec2R = boto3.resource('ec2')
ec2Rohio = boto3.resource('ec2',region_name="us-east-2")

client = boto3.client('elbv2')
autoscale = boto3.client('autoscaling')


def DestroySecuriryGroup(ec2,groupName):
    print("Deleting Security Group")
    time.sleep(10)
    try:
        response = ec2.describe_security_groups(GroupNames=[groupName])
        try:
            response = ec2.delete_security_group(GroupName=groupName)
            print('Security Group Deleted')
        except ClientError as e:
            print(e)
    except:
        print("Group does not exists")

    

def CreateSecurityGroup(ec2,groupName): 
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    try:
        response = ec2.create_security_group(GroupName=groupName,
                                            Description='Security Group Aps Lucas',
                                            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id)
        print('Ingress Successfully Set %s' % data)

        return (security_group_id)
        
    except ClientError as e:

        response = ec2.describe_security_groups(
    Filters=[
        {
            'Name': 'group-name',
            'Values': [
                '{}'.format(groupName),
            ]
        },
    ],)

    id=response['SecurityGroups'][0]['GroupId']

    return id


def DestroyKeyPair(ec2,keyName):
    os.system("chmod 777 {}".format(keyName)+".pem")
    try:
        response = ec2.describe_key_pairs(KeyNames=[keyName])
        ec2.delete_key_pair(KeyName=keyName)
        print("Key deleted")
    except ClientError as e:
        print("Key does not exists")

def CreateKeyPair(ec2,keyName): 
    outfile = open('{}'.format(keyName)+'.pem','w')
    key_pair=ec2.create_key_pair(KeyName=keyName)
    KeyPairOut =key_pair["KeyMaterial"]
    outfile.write(KeyPairOut)
    os.system("chmod 400 {}".format(keyName)+".pem")

def CreateInstanceUbunto18(ec2,ec2R,imageId,zone,instanceName,groupName,keyName,userData):
    keyresponse = ec2.describe_key_pairs(KeyNames=[keyName])
    keyN= keyresponse["KeyPairs"][0]["KeyName"]
    GroupResponce = ec2.describe_security_groups(GroupNames=[groupName])
    Groupid=GroupResponce["SecurityGroups"][0]['GroupId']
    instance = ec2R.create_instances(DryRun=False,
    ImageId=imageId,
    MinCount=1,
    MaxCount=1,
    KeyName=keyN,
    Placement={'AvailabilityZone': zone},
    SecurityGroupIds=[Groupid],
    InstanceType='t2.micro',
    UserData=userData,
    TagSpecifications=[{
        'ResourceType':'instance',
        'Tags': [
            {
                'Key': 'Owner',
                'Value': 'Lucas'},
                {
                'Key': 'Name',
                'Value': instanceName},
                ]
            },
        ],
    )

    ids=[]

    for i in instance:
        ids.append(i.id)

    print("Waiting for instance: {} to be ready".format(instanceName))

    waiter = ec2.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=ids)
    
    print("Instance: {} is ready".format(instanceName))

    return instance

def DestroyInstances(ec2,ec2R,key,value):
    response = ec2.describe_instances(
    Filters=[
        {
            'Name': 'tag:{}'.format(key),
            'Values': ['{}'.format(value)]
        },
    ],
    DryRun=False,
    MaxResults=5)
    ifnull=response["Reservations"]
    if ifnull != []:
        try:
            print("Waiting for instances with key: {} and value: {} to terminate".format(key,value))
            ec2R.instances.filter(Filters=[{
                'Name': 'tag:{}'.format(key),
                'Values': ['{}'.format(value)]
            },]).terminate()
            waiter = ec2.get_waiter('instance_terminated')
            waiter.wait(
            Filters=[{
                'Name': 'tag:{}'.format(key),
                'Values': ['{}'.format(value)]
            },])
            print(" All Instances Terminated")
        except ClientError as e:
            print("Instance with key {} and value {} not found".format(key,value))



def CreateImage(idlist,name):
    response = ec2.create_image(InstanceId=idlist[0].id,Name=name)
    id=response['ImageId']
    print("Waiting for AMI to be available")
    waiterAMI=ec2.get_waiter('image_available')
    waiterAMI.wait(ImageIds=[id])
    print("AMI availiable")
    return id

def DestroyImage(name):
    try:
        response = ec2.describe_images(
        Filters=[
            {
                'Name': 'name',
                'Values': [name]
            },
        ],)
        
        AMIid=(response["Images"][0]['ImageId'])
        
        ec2.deregister_image(
        ImageId=AMIid)

    except:
        print("AMI does not exists")



def DestroyLoadBalancer(loadBalancerName):
    try:
        print("Waiting for Load Balancer to be deleted")
        loadBalancerARN = client.describe_load_balancers(
        Names=[loadBalancerName])["LoadBalancers"][0]['LoadBalancerArn']
        waiterLoadBancer=client.get_waiter('load_balancers_deleted')

        client.delete_load_balancer(
        LoadBalancerArn=loadBalancerARN)

        waiterLoadBancer.wait(
        LoadBalancerArns=[loadBalancerARN])

        time.sleep(20)
        print("Load Balancer deleted")

    except ClientError as e:
            print(e)

def CreateLoadBalancer(LoadBalancerName,securityGroupID):
    response = client.create_load_balancer(
    Name=LoadBalancerName,
    Subnets=['subnet-ba883ae6',
    'subnet-37d86850',
    'subnet-dc55e9f2',
    'subnet-df95d495',
    'subnet-dfad6ae1',
    'subnet-df0f78d0'
    ],
    SecurityGroups=[
        securityGroupID,
    ],
    Scheme='internet-facing',
    Tags=[
        {
            'Key': 'Owner',
            'Value': 'Lucas'
        },
    ],
    Type='application',
    IpAddressType='ipv4'

 
)

def CreateTargetGroup(targetGroupName):  #deletar se existir

    response = client.create_target_group(
    Name=targetGroupName,
    Protocol='HTTP',
    Port=5000,
    VpcId='vpc-1ce22266',
    HealthCheckProtocol='HTTP',
    HealthCheckPath='/',
    TargetType='instance')
    tg = client.describe_target_groups(
        Names=[
            targetGroupName,
        ]
    )

    targetGroupARN=tg["TargetGroups"][0]["TargetGroupArn"]

    return targetGroupARN


def DestroyTargetGroup(targetGroupName):
    try:
        tg = client.describe_target_groups(
            Names=[
                targetGroupName,
            ]
        )

        targetGroupARN=tg["TargetGroups"][0]["TargetGroupArn"]

        try:
            client.delete_target_group(TargetGroupArn=targetGroupARN,)
            print("Target Group deleted")
        except ClientError as e:
            print(e)
    except ClientError as e:
        print("Target Group does not exists")
      

def RegisterTargetsAndListener(targetGroupARN,idList,loadBalancerName):

    ids=[]

    for instance in idList:
        ids.append(instance.id)


    loadBalancerARN = client.describe_load_balancers(
        Names=[loadBalancerName])["LoadBalancers"][0]['LoadBalancerArn']
    
    client.create_listener(
    DefaultActions=[
        {
            'TargetGroupArn':targetGroupARN,
            'Type': 'forward',
        },],
    LoadBalancerArn=loadBalancerARN,
    Port=5000,
    Protocol='HTTP',
)

def CreateLaunchConfiguration(launchName,keyName,securityGroupID,userData):
    response = autoscale.create_launch_configuration(
    LaunchConfigurationName=launchName,
    KeyName=keyName,
    SecurityGroups=[
        securityGroupID,
    ],
    InstanceType='t2.micro',
    ImageId='ami-04b9e92b5572fa0d1',
    UserData=userData,
    InstanceMonitoring={
        'Enabled': True
    },
)


def DestroyLaunchConfiguration(launchName):
    try:
        autoscale.delete_launch_configuration(
        LaunchConfigurationName=launchName)
    except ClientError as e:
        print("LaunchConfiguration does not exists")


def AutoScalingWaiter(names):
    waiting=True
    print("Waiting for AutoScaleGroup to be deleted")
    while(waiting):
        response = autoscale.describe_auto_scaling_groups(
        AutoScalingGroupNames=names,)['AutoScalingGroups']
        if(len(response)==0):
            waiting=False
        time.sleep(3)

    time.sleep(10)
    print("AutoScalingGroup Deleted")


 

def CreateAutoScalingGroup(autoScalingName,launchName,targetGroupARN):
    response = autoscale.create_auto_scaling_group(
    AutoScalingGroupName=autoScalingName,
    LaunchConfigurationName=launchName,
    MinSize=1,
    MaxSize=3,
    DesiredCapacity=1,
    DefaultCooldown=100,

    TargetGroupARNs=[
        targetGroupARN,
    ],
    AvailabilityZones=["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1e", "us-east-1f"],
    HealthCheckGracePeriod=123,
    
)

def DestroyAutoScalingGroup(autoName):
    try:
        autoscale.delete_auto_scaling_group(
        AutoScalingGroupName=autoName,
        ForceDelete=True)
        AutoScalingWaiter([autoName])
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait(
            Filters=[{
                'Name': 'tag:aws:autoscaling:groupName',
                'Values': [autoName]
            },])
    except ClientError as e:
        print("AutoScaleGroup does not exists")


def GetIps(ec2,idList):
    ids=[]
    for instance in idList:
        ids.append(instance.id)

    
    instance_ip = ec2.describe_instances(InstanceIds=[ids[0]])["Reservations"][0]["Instances"][0]["PublicIpAddress"]
    return instance_ip


def Add_Inbound_Rule(ec2, groupName,ip,port):
    response = ec2.authorize_security_group_ingress(
        GroupName=groupName,
        # GroupId="sg-037ca28dda16a98e6"
        IpPermissions=[
            {
                'FromPort': port,
                'IpProtocol': 'TCP',
                'IpRanges': [
                    {
                        'CidrIp': '{}'.format(ip),
                    },
                ],
                'ToPort': port
            }
        ]
    )







def LaunchVirginia(Name,instanceName,groupName,keyName,loadBalancerName,amiId,zone,targetGroupName,launchName,autoName,userDataRedi,userDataAutoS):
    print("Starting Virginia Application")
    DestroyInstances(ec2,ec2R,"Owner",Name)
    DestroyAutoScalingGroup(autoName)
    DestroyLaunchConfiguration(launchName)
    DestroyLoadBalancer(loadBalancerName)
    DestroyTargetGroup(targetGroupName)
    DestroyKeyPair(ec2,keyName)
    CreateKeyPair(ec2,keyName)
    DestroySecuriryGroup(ec2,groupName)
    securityGroupID=CreateSecurityGroup(ec2,groupName)
    Add_Inbound_Rule(ec2,groupName,"0.0.0.0/0",22)
    Add_Inbound_Rule(ec2,groupName,"0.0.0.0/0",5000)
    print("Launching Virginia Redirector")
    idRedirect=CreateInstanceUbunto18(ec2,ec2R,amiId,zone,instanceName,groupName,keyName,userDataRedi)
    CreateLoadBalancer(loadBalancerName,securityGroupID)
    TGarn=CreateTargetGroup(targetGroupName)
    RegisterTargetsAndListener(TGarn,idRedirect,loadBalancerName)
    ipRedirect=GetIps(ec2,idRedirect)
    userDataAutoS=userDataAutoS.replace("@",ipRedirect)
    CreateLaunchConfiguration(launchName,keyName,securityGroupID,userDataAutoS)
    print("Launching Virginia AutoScalingGroup")
    CreateAutoScalingGroup(autoName,launchName,TGarn)
    ipRedirect=GetIps(ec2,idRedirect)
    return ipRedirect

def LaunchOhio(Name,clientName,mongoName,amiId,zone,groupName,keyName,userDataClient,userDataMongo):
     print("Starting Ohio Application")
     DestroyInstances(ec2ohio,ec2Rohio,"Owner",Name)
     DestroyKeyPair(ec2ohio,keyName)
     DestroySecuriryGroup(ec2ohio,groupName)
     CreateKeyPair(ec2ohio,keyName)
     securityGroupID=CreateSecurityGroup(ec2ohio,groupName)
     print("Launching Ohio DataBase")
     idMongo=CreateInstanceUbunto18(ec2ohio,ec2Rohio,amiId,zone,mongoName,groupName,keyName,userDataMongo)
     mongoIp=GetIps(ec2ohio,idMongo)
     userDataClient=userDataClient.replace("@",mongoIp)
     print("Launching Ohio MicroService")
     microServiceId=CreateInstanceUbunto18(ec2ohio,ec2Rohio,amiId,zone,clientName,groupName,keyName,userDataClient)
     microServiceIp=GetIps(ec2ohio,microServiceId)
     Add_Inbound_Rule(ec2ohio,groupName,microServiceIp+"/32",27017)
     return microServiceIp




if __name__ == '__main__':
    print("Starting Application")
    microServiceIp=LaunchOhio(NameOh,instanceNameClientOh,instanceNameMongoOh,amiIdOh,zoneOh,groupNameOh,keyNameOh,userDataClientOh,userDataMongoOh)
    userDataRedi=userDatav.replace("@",microServiceIp)
    ipRed=LaunchVirginia(Namev,instanceNamev,groupNamev,keyNamev,loadBalancerNamev,amiIDv,zonev,targetGroupNamev,launchNamev,autoNamev,userDataRedi,userDatav)
    Add_Inbound_Rule(ec2ohio,groupNameOh,ipRed+"/32",5000)
    print("\a")
