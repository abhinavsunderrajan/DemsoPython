import boto3
from botocore.exceptions import ClientError
import logging
import sys

"""
This class is responible for creating a boto s3 client performing routine
operations.
"""


class S3Operations:
    def __init__(self, key=None, secret=None, region=None):

        if region is None:
            if key is None or secret is None:
                self.s3_client = boto3.client('s3')
            else:
                self.s3_client = boto3.client('s3', aws_access_key_id=key,
                                              aws_secret_access_key=secret)
        else:
            if key is None or secret is None:
                self.s3_client = boto3.client('s3', region_name=region)
            else:
                self.s3_client = boto3.client('s3',  aws_access_key_id=key,
                                              aws_secret_access_key=secret,
                                              region_name=region)
            self.location = {'LocationConstraint': region}

        log_format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
        logging.basicConfig(
            format=log_format,
            level=logging.INFO,
            handlers=[logging.StreamHandler(stream=sys.stdout)])

        self.logger = logging.getLogger('lda.trainer')

    def upload_file(self, file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then
        file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Upload the file
        try:
            self.s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            self.logger.error(e)
            return False
        return True

    def create_bucket(self, bucket_name, region=None):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """
        if self.does_bucket_exist(bucket_name):
            self.logger.info(f"{bucket_name} already exists")
            return True

        # Create bucket
        try:
            if region is None:
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.\
                    create_bucket(Bucket=bucket_name,
                                  CreateBucketConfiguration=self.location)
        except ClientError as e:
            self.logger.error(e)
            return False
        return True

    def does_bucket_exist(self, bucket_name):
        # Retrieve the list of existing buckets
        response = self.s3_client.list_buckets()
        for bucket in response['Buckets']:
            if bucket["Name"] == bucket_name:
                return True
        return False

    def list_objects(self, bucket, prefix):
        """
        List objects in the S3 bucket and prefix
        """
        objects = self.s3_client.list_objects(Bucket=bucket, Delimiter='/',
                                              Prefix=prefix, MaxKeys=5000)
        prefix_list = []
        if "CommonPrefixes" in objects:
            for object in objects["CommonPrefixes"]:
                prefix_list.append(object["Prefix"])
        return prefix_list
