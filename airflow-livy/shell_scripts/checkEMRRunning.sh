#!/bin/bash
interval=120
((end_time=${SECONDS}+3600))

clusterId=$(echo $1 | sed "s/\"//g")
echo "Checking status for cluster $clusterId"
while ((${SECONDS} < ${end_time}))
do
  status=$(aws --region=us-east-1 emr describe-cluster --cluster-id $clusterId | jq '. |  .Cluster.Status.State' | sed "s/\"//g")
  echo "$status"
  if [ "$status" = "WAITING" ] ;
    then
    echo "$status"
    echo "EMR cluster $1 is started successfully"
    masterDNS=$(aws --region=us-east-1 emr describe-cluster --cluster-id $clusterId | jq '. |  .Cluster.MasterPublicDnsName'| sed "s/\"//g")
    echo "$masterDNS"
    exit 0
  elif [ "$status" = "RUNNING" ] ;
    then
    echo "EMR cluster $1 is started successfully"
    masterDNS=$(aws --region=us-east-1 emr describe-cluster --cluster-id $clusterId | jq '. |  .Cluster.MasterPublicDnsName' | sed "s/\"//g")
    echo "$masterDNS"
    exit 0
  elif [ "$status" = "STARTING" ] ;
    then
    echo "EMR cluster $1 is starting .............."
  elif [ "$status" = "TERMINATING" ] ;
    then
    echo "EMR cluster $1 is TERMINATING.............."
    exit 1
  elif [ "$status" = "TERMINATED" ] ;
    then
    echo "EMR cluster $1 is TERMINATED !"
    exit 1
  fi
  sleep ${interval}
done
echo "$status"
echo "Failed to start the cluster"
exit 1
