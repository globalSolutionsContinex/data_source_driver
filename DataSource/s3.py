import boto3
import boto3.session
from botocore.exceptions import ClientError
from infrastructure import files

import logging
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)


class S3Client:

    def __init__(self, s3_config):
        self.key = s3_config['accessKey']
        self.secret = s3_config['secretKey']
        self.bucket_name = s3_config['bucketName']
        session = boto3.session.Session()
        self.client = session.client(
            's3',
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret
        )
        self.resource = boto3.resource(
            's3',
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret)

        logging.getLogger('boto').setLevel(logging.CRITICAL)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)
        logging.getLogger('boto3').setLevel(logging.CRITICAL)

    def get_url_in_s3(self, key_name):
        return "https://s3-us-west-2.amazonaws.com/" + self.bucket_name + "/" + key_name

    def get_pending_files(self, folder_name, type_file):
        s3_files = self.client.list_objects(Bucket=self.bucket_name, Prefix=folder_name)
        pending_files = s3_files['Contents'] if 'Contents' in s3_files else []
        today_files = []
        for file in pending_files:
            if str(file['Key']).endswith(type_file):
                today_files.append(file['Key'])
        return today_files

    def move_file(self, client, file_path, destiny_path):
        file_path_to = destiny_path + file_path
        self.resource.Object(self.bucket_name, file_path_to).copy_from(
            CopySource="{}/{}".format(self.bucket_name, file_path))
        self.resource.Object(self.bucket_name, file_path).delete()

    def download_file(self, client, key_name, local_path):
        file_name = files.get_file_name(key_name)
        local_path_name = "{}{}".format(local_path, file_name)
        client.download_file(Bucket=self.bucket_name, Key=key_name, Filename=local_path_name)
        return local_path_name

    def upload_file(self, folder_name, file_path):
        with open(file_path, 'rb') as file_to_upload:
            # Do not use the real file name to make difficult to guess the S3 URL
            key_name = folder_name + "/" + files.get_file_name(file_path)
            self.client.upload_fileobj(file_to_upload, self.bucket_name, key_name)
            url_in_s3 = self.get_url_in_s3(key_name)
            return url_in_s3

    def upload_json(self, folder_name, file_name, data):
        key_name = folder_name + "/" + file_name
        self.client.put_object(Body=bytes(data), Bucket=self.bucket_name, Key=key_name, ContentType='application/json')
        url_in_s3 = self.get_url_in_s3(key_name)
        return url_in_s3

    def upload_image(self, folder_name, file_path, filename):
        with open(file_path, 'rb') as file_to_upload:
            # Do not use the real file name to make difficult to guess the S3 URL
            key_name = folder_name + filename
            self.client.upload_fileobj(file_to_upload, self.bucket_name, key_name,
                                       ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"})
            url_in_s3 = self.get_url_in_s3(key_name)
            return url_in_s3

    def delete_image_cache(self, filename, sub_folder):
        try:
            key_name = sub_folder + filename
            self.resource.Object(self.bucket_name, key_name).delete()
        except ClientError as clex:
            return False
        return True

    def exist_file(self, folder_name, file_path):
        try:
            key_name = folder_name + files.get_file_name(file_path)
            self.resource.Object(self.bucket_name, key_name).load()
        except ClientError as clex:
            return False
        return True

