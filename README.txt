# Install flask on EC2 
# Either add "sudo" before all commands or use "sudo su" first

#!/bin/bash
sudo su
yum update -y
yum install git -y
git clone https://github.com/kangeekoo/employee.git
cd aws-live
ls
yum install python-pip -y
pip3 install flask
pip3 install pymysql
pip3 install boto3
pip3 install DateTime
python3 EmpApp.py
