import boto3
from flask import current_app as app

from src.main.common.singleton import Singleton


class FileServerClient:
    _s3_client: boto3.client

    def __init__(self, s3_client: boto3.client, bucket: str):
        self._s3_client = s3_client
        self._bucket = bucket

    def create_multipart_upload(self, *, key: str):
        return self._s3_client.create_multipart_upload(Bucket=self._bucket, Key=key)

    def upload_part(self, *, body, key, part_number, upload_id):
        return self._s3_client.upload_part(
            Body=body,
            Bucket=self._bucket,
            Key=key,
            PartNumber=part_number,
            UploadId=upload_id,
        )

    def complete_multipart_upload(self, *, key, multipart_upload, upload_id):
        return self._s3_client.complete_multipart_upload(
            Bucket=self._bucket,
            Key=key,
            MultipartUpload=multipart_upload,
            UploadId=upload_id,
        )

    def abort_multipart_upload(self, *, key, upload_id):
        return self._s3_client.abort_multipart_upload(Bucket=self._bucket, Key=key, UploadId=upload_id)

    def upload_fileobj(self, *, fileobj, key, config=None):
        if config is None:
            return self._s3_client.upload_fileobj(Fileobj=fileobj, Bucket=self._bucket, Key=key)
        return self._s3_client.upload_fileobj(Fileobj=fileobj, Bucket=self._bucket, Key=key, Config=config)


class ThisFileserverClient(FileServerClient, metaclass=Singleton):
    def __init__(self):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=app.config['S3_ACCESS_SECRET'],
            endpoint_url=app.config['S3_ENDPOINT'],
        )
        super().__init__(s3_client, app.config['S3_BUCKET'])
