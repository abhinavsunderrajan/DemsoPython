#!/bin/bash
sudo chmod 444 /var/aws/emr/userData.json
sudo python3 -m pip install --upgrade pip
sudo python3 -m pip install pandas
sudo python3 -m pip install matplotlib
sudo python3 -m pip install seaborn
sudo python3 -m pip install scikit-learn
sudo python3 -m pip install boto3
sudo python3 -m pip install pymysql
sudo python3 -m pip install pyarrow==0.14.1
