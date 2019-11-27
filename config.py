#Virginia Config
Namev="Lucas"
instanceNamev="LucasInstanceV"
groupNamev="LucasSecurityGroupV"
keyNamev="LucasVirginiaKey"
loadBalancerNamev="LucasLoadBalancerV"
targetGroupNamev="LucasTargetGroupV"
launchNamev="LucasLaunchConfigV"
autoNamev="LucasAutoScaleV"
amiIDv="ami-04b9e92b5572fa0d1"
zonev="us-east-1a"
userDatav='''#! /bin/bash
sudo apt-get update
sudo apt-get -y install python-pip
cd home/ubuntu/
git clone https://github.com/LucasVaz97/PythonWebServers.git
cd PythonWebServers/
cd Redirects/
echo "export REDIRECTIP=@" > var.rc
source var.rc
pip install -r requirements.txt
python run-app.py
    '''

#Ohio Config
NameOh="Lucas"
instanceNameClientOh="LucasInstanceClientOh"
instanceNameMongoOh="LucasInstanceMongoOh"
amiIdOh="ami-0d5d9d301c853a04a"
zoneOh="us-east-2a"
groupNameOh="LucasSecurityGroupO"
keyNameOh="LucasOhioKey"
userDataClientOh='''#! /bin/bash
sudo apt-get update
sudo apt-get -y install python-pip
cd home/ubuntu/
git clone https://github.com/LucasVaz97/PythonWebServers.git
cd PythonWebServers/
cd MicroService/
echo "export SERVERIP=@" > var.rc
source var.rc
pip install -r requirements.txt
python run-app.py
'''

userDataMongoOh='''#! /bin/bash
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
sudo apt-get install gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
sed -i "s,\\(^[[:blank:]]*bindIp:\\) .*,\\1 0.0.0.0," /etc/mongod.conf
sudo service mongod start'''

