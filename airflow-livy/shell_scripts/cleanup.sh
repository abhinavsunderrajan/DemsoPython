#!/bin/bash
set -e

clusterid=$(echo $1 | sed "s/\"//g")

{ #'try' block
aws --region=us-east-1 emr terminate-clusters --cluster-ids ${clusterid}
echo "Terminated cluster "${clusterid}

} || {
    echo "Something Failed , Please check"
    return 1
}
