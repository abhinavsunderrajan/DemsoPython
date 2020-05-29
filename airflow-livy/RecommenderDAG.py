"""
An example DAG for orchestrating an EMR job
"""
from airflow import DAG
from datetime import datetime
from airflow.operators.bash_operator import BashOperator
from recommendations import LivyOperator
from recommendations import config
import os

# constants
ENV = os.environ['ENV_TYPE']
print(f"The deployed environment is {ENV}")
BASE_PATH = "/app/airflow/dags/recommendations"
PYSPARK_BUCKET = f"{config.py_spark_args['PYSPARK_CODE_PATH'][f'{ENV}']}"
PYSPARK_S3_AWS_PATH = f"{PYSPARK_BUCKET}Sparkcode.py"
PYSPARK_CODE = f"{BASE_PATH}/pyspark/Sparkcode.py"
BOOTSTRAP_SCRIPT = f"{BASE_PATH}/shell_scripts/emr_bootstrap.sh"
BOOTSTRAP_BUCKET = f"{config.py_spark_args['BOOTSTRAP_BUCKET'][f'{ENV}']}"

# launch the EMR cluster start script
launch_command = (f"{BASE_PATH}/shell_scripts/launch_emr_recommendation.sh "
                  f"{config.py_spark_args['EC2_KEY_NAME'][f'{ENV}']} "
                  f"{config.py_spark_args['INSTANCE_PROFILE'][f'{ENV}']} "
                  f"{config.py_spark_args['EMR_MANAGED_MASTER_SECURITY_GROUP'][f'{ENV}']} "
                  f"{config.py_spark_args['EMR_MANAGED_SLAVE_SECURITY_GROUP'][f'{ENV}']} "
                  f"{config.py_spark_args['SUBNET_ID'][f'{ENV}']} "
                  f"{config.py_spark_args['ADDITIONAL_MASTER_SECURITY_GROUPS'][f'{ENV}']} "
                  f"{config.py_spark_args['ADDITIONAL_SLAVE_SECURITY_GROUPS'][f'{ENV}']} "
                  f"{config.py_spark_args['SERVICE_ROLE'][f'{ENV}']} "
                  f"{config.py_spark_args['BOOTSTRAP_PATH'][f'{ENV}']} "
                  f"{config.py_spark_args['LOG_URI'][f'{ENV}']} "
                  f"{config.py_spark_args['SERVICE_ACCESS_SECURITY_GROUP'][f'{ENV}']} "
                  " | jq '.ClusterId'")

upload_s3 = f"aws s3 cp {PYSPARK_CODE} {PYSPARK_BUCKET} && aws s3 cp {BOOTSTRAP_SCRIPT} {BOOTSTRAP_BUCKET}"


# check if EMR cluster status.
check_command = (f'{BASE_PATH}/shell_scripts/checkEMRRunning.sh '
                 ' {{ti.xcom_pull("launch_EMR")}}')

# terminate the EMR cluster.
terminate_command = ('aws --region=us-east-1 emr terminate-clusters '
                     '--cluster-ids  {{ ti.xcom_pull("launch_EMR") }}')


default_args = {
    'owner': 'abhinav',
    'depends_on_past': False,
    'start_date': datetime(2019, 9, 24)
}

# Execute these methods incase the dags succeeds or Fails


def failure_msg(context):
    print("DAG failed .............")
    terminate_EMR.execute(context=context)
    fail_echo = BashOperator(
        task_id='call_slack',
        bash_command='echo "DAG FAILED !!" ')
    return fail_echo.execute(context=context)


# schedule the DAG to run at 05:00 GMT time hours every Monday
dag = DAG('dag_name',
          default_args=default_args,
          schedule_interval="0 20 * * *",
          on_failure_callback=failure_msg,
          catchup=False)


dag_start = BashOperator(
    task_id='dag_start',
    bash_command='echo "DAG Started" ',
    dag=dag
)

upload_pyspark_to_s3 = BashOperator(
    task_id='upload_pyspark_to_s3',
    bash_command=upload_s3,
    dag=dag
)

# Launch EMR cluster and return the cluster ID
launch_EMR = BashOperator(
    task_id='launch_EMR',
    bash_command=launch_command,
    xcom_push=True,
    dag=dag
)

# Check if the cluster is started return the spark master_dns name
check_EMR = BashOperator(
    task_id='check_EMR',
    bash_command=check_command,
    xcom_push=True,
    dag=dag
)

# Submit the Sparkjob at the s3 path to the created EMR cluster.
master_dns = "{{ti.xcom_pull('check_EMR')}}"
als_recommender = LivyOperator.LivyEMRSubmitOperator(
    task_id='als_recommender',
    master_dns=master_dns,
    spark_job_s3_path=PYSPARK_S3_AWS_PATH,
    provide_exec_date=True,
    dag=dag,
    spark_job_args=[config.py_spark_args["arg_name"][f"{ENV}"],
                    config.py_spark_args["arg_name"][f"{ENV}"],
                    ENV],
    on_failure_callback=failure_msg
)


# Terminate the EMR after job completion
terminate_EMR = BashOperator(
    task_id='terminate_EMR',
    bash_command=terminate_command,
    trigger_rule="all_done",
    dag=dag
)

# DAG flow
dag_start >> upload_pyspark_to_s3 >> launch_EMR >> check_EMR >> als_recommender
als_recommender >> terminate_EMR
