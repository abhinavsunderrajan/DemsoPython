from airflow.models.baseoperator import BaseOperator
import logging
import json
import requests
import time

"""
Extend the airflow Base operator to submit jobs to a created EMR cluster.
"""


class LivyEMRSubmitOperator(BaseOperator):
    """
    Executes the EMR spark submit.
    :param master_dns: the ip of the EMR cluster master node.
    :param spark_job_s3_path: The path of your pyspark job in s3
    :param provide_exec_date boolean to provide the execution date as an
        argument to your pyspark job. Note that year, month and day will be
        added as program to the begining of program arguments
        if this is set to True.
    :param spark_job_args: The arguments to your pyspark job.
    """
    template_fields = ('master_dns', 'spark_job_s3_path')
    ui_color = '#f08b43'

    def __init__(self, master_dns, spark_job_s3_path, provide_exec_date=False,
                 spark_job_args=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master_dns = master_dns
        self.spark_job_args = spark_job_args
        self.spark_job_s3_path = spark_job_s3_path
        self.provide_exec_date = provide_exec_date

    """
    This method needs to be overriden to execute the desired actions
    of your custom operator.
    """

    def execute(self,  context):

        logging.info("Calling spark job on Master : " + self.master_dns)
        logging.info("Reading pyspark script from: " + self.spark_job_s3_path)
        logging.info("Calling spark_submit........")
        # provide context if execution date is required for the spark job
        if self.provide_exec_date:
            exec_date = context["execution_date"]
            print(exec_date)
            self.spark_job_args.insert(0, exec_date.year)
            self.spark_job_args.insert(1, exec_date.month)
            self.spark_job_args.insert(2, exec_date.day)

        host = 'http://' + self.master_dns + ':8998'
        data = {'file': self.spark_job_s3_path,
                "args": self.spark_job_args}
        headers = {'Content-Type': 'application/json'}
        print("Calling request........")
        response = requests.post(host + '/batches', data=json.dumps(data),
                                 headers=headers)
        logging.info(response.json())
        self.track_statement_progress(response.headers)

    """
    Track the progress of your livy job every 30 seconds.
    """

    def track_statement_progress(self, response_headers):
        statement_status = ''
        host = 'http://' + self.master_dns + ':8998'
        session_url = host + response_headers['location'].\
            split('/statements', 1)[0]
        while statement_status != 'success':
            statement_url = host + response_headers['location']
            statement_response = requests.get(
                statement_url, headers={'Content-Type': 'application/json'})
            statement_status = statement_response.json()['state']
            logging.info('Statement status: ' + statement_status)
            lines = requests.get(session_url + '/log',
                                 headers={'Content-Type':
                                          'application/json'}).json()['log']
            for line in lines:
                logging.info(line)
            if statement_status == 'dead':
                raise ValueError(f'Exception in the app : {statement_status}')

            if 'progress' in statement_response.json():
                progress_info = str(statement_response.json()['progress'])
                logging.info(f'Progress: {progress_info}')
            time.sleep(30)
