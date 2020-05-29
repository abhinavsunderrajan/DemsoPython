EC2_KEY_NAME=$1
INSTANCE_PROFILE=$2
EMR_MANAGED_MASTER_SECURITY_GROUP=$3
EMR_MANAGED_SLAVE_SECURITY_GROUP=$4
SUBNET_ID=$5
ADDITIONAL_MASTER_SECURITY_GROUPS=$6
ADDITIONAL_SLAVE_SECURITY_GROUPS=$7
SERVICE_ROLE=$8
BOOTSTRAP_PATH=$9
LOG_URI=${10}
SERVICE_ACCESS_SECURITY_GROUP=${11}

aws --region=us-east-1 emr create-cluster \
--auto-scaling-role EMR_AutoScaling_DefaultRole \
--applications Name=Hadoop Name=Ganglia Name=Spark Name=Livy \
--ebs-root-volume-size 10 \
--no-termination-protected \
--visible-to-all-users \
--no-auto-terminate \
--ec2-attributes KeyName=${EC2_KEY_NAME},InstanceProfile=${INSTANCE_PROFILE},ServiceAccessSecurityGroup=${SERVICE_ACCESS_SECURITY_GROUP},EmrManagedMasterSecurityGroup=${EMR_MANAGED_MASTER_SECURITY_GROUP},EmrManagedSlaveSecurityGroup=${EMR_MANAGED_SLAVE_SECURITY_GROUP},AdditionalMasterSecurityGroups=${ADDITIONAL_MASTER_SECURITY_GROUPS},AdditionalSlaveSecurityGroups=${ADDITIONAL_SLAVE_SECURITY_GROUPS},SubnetId=${SUBNET_ID} \
--service-role ${SERVICE_ROLE} \
--bootstrap-actions Path=${BOOTSTRAP_PATH} \
--enable-debugging \
 --release-label emr-5.27.0 \
 --log-uri ${LOG_URI} \
 --name 'emr_job_name' \
 --tags project=tag_name \
 --instance-groups '[{
                        "InstanceCount":1,
                        "InstanceGroupType":"MASTER",
                        "InstanceType":"m3.xlarge",
                        "Name":"Master - 1"
                    },
                    {
                        "InstanceCount":6,
                        "InstanceGroupType":"CORE",
                        "InstanceType":"m3.xlarge",
                        "Name":"Core - 2"
                    }]' \
--configurations '[
                   {
                      "Classification":"spark-log4j",
                      "Properties":{
                         "log4j.rootCategory":"ERROR, console"
                      }
                   },
                   {
                      "Classification":"spark",
                      "Properties":{
                         "maximizeResourceAllocation":"false"
                      }
                   },
                   {
                      "Classification":"livy-conf",
                      "Properties":{
                         "livy.server.session.timeout":"5h"
                      }
                   },
                   {
                      "Classification":"spark-defaults",
                      "Properties":{
                         "spark.executor.memory":"8G",
                         "spark.driver.memory":"8G",
                         "spark.executor.cores":"3",
                         "spark.executor.instances":"6",
                         "spark.dynamicAllocation.enabled":"false",
                         "spark.default.parallelism":"18"
                      }
                   },
                   {
                      "Classification":"spark-env",
                      "Properties":{

                      },
                      "Configurations":[
                         {
                            "Classification":"export",
                            "Properties":{
                               "PYSPARK_PYTHON":"python36",
                               "ARROW_PRE_0_15_IPC_FORMAT":"1"
                            },
                            "Configurations":[

                            ]
                         }
                      ]
                  },
                  {
                    "Classification": "yarn-env",
                    "Configurations": [
                    {
                    "Classification": "export",
                    "Configurations": [],
                    "Properties": { "ARROW_PRE_0_15_IPC_FORMAT": "1" }
                    }
                    ],
                    "Properties": {}
                    }
                ]'
