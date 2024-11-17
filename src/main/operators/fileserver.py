import logging
from io import StringIO, BytesIO

import boto3
import pandas as pd
from flask import current_app as app

from src.main import db
from src.main.operators.operator import Operator

logger = logging.getLogger(__name__)


class MultipartUploader:
    def __init__(self, s3_client, bucket, filename, chunk_size):
        self.s3_client = s3_client
        self.bucket = bucket
        self.filename = filename
        self.chunk_size = chunk_size
        self.parts = []
        self.part_number = 1
        self.upload_id = None

    def __enter__(self):
        response = self.s3_client.create_multipart_upload(Bucket=self.bucket, Key=self.filename)
        self.upload_id = response["UploadId"]
        logger.info(f"Initialized multipart upload: {self.upload_id}")
        return self

    def upload_part(self, buffer):
        response = self.s3_client.upload_part(
            Body=buffer,
            Bucket=self.bucket,
            Key=self.filename,
            PartNumber=self.part_number,
            UploadId=self.upload_id,
        )
        logger.debug(f"Uploaded part {self.part_number}, size {buffer.tell()} bytes.")
        self.parts.append({"PartNumber": self.part_number, "ETag": response["ETag"]})
        self.part_number += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.s3_client.abort_multipart_upload(Bucket=self.bucket, Key=self.filename, UploadId=self.upload_id)
            logger.error(f"Failed to upload: {self.filename}")
        else:
            self.s3_client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=self.filename,
                MultipartUpload={"Parts": self.parts},
                UploadId=self.upload_id,
            )
            logger.info(f"Upload complete: {self.filename}")


class UploadCSVFromTableOperator(Operator):
    def __init__(self, **kwargs):
        self.table_name = kwargs["table_name"]
        self.schema = "temp"

        # NOTE: s3 client multipart requires minimum 5MB part size
        min_chunk_size = 5 * 1024 * 1024  # 5MB
        self.chunk_size = kwargs.get("chunk_size", min_chunk_size)  # default: 5MB
        assert self.chunk_size >= min_chunk_size, "chunk_size should be greater than 5MB"

        self.bucket = app.config['S3_BUCKET']
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=app.config['S3_ACCESS_SECRET'],
            endpoint_url=app.config['S3_ENDPOINT'],
        )

    def execute(self):
        logger.info(f"Upload csv from table: {self.table_name}")
        query = f"SELECT * FROM {self.schema}.{self.table_name} order by id"

        csv_name = f"{self.table_name}.csv"

        with MultipartUploader(self.s3_client, self.bucket, csv_name, self.chunk_size) as uploader:
            first_chunk = True
            with BytesIO() as buffer:
                for chunk in pd.read_sql_query(query, chunksize=10000, con=db.engine):
                    with StringIO() as string_buffer:
                        chunk.to_csv(string_buffer, index=False, header=first_chunk)
                        first_chunk = False

                        buffer.write(string_buffer.getvalue().encode('utf-8'))

                        if buffer.tell() >= self.chunk_size:
                            buffer.seek(0)
                            uploader.upload_part(buffer)
                            buffer.seek(0)
                            buffer.truncate()

                if buffer.tell() > 0:
                    buffer.seek(0)
                    uploader.upload_part(buffer)

        logger.info(f"Upload complete: {csv_name}")

    def execute_alt(self):
        # OLD implementation
        logger.info(f"Upload csv from table: {self.table_name}")
        query = f"SELECT * FROM {self.schema}.{self.table_name} order by id"

        csv_name = f"{self.table_name}.csv"

        multi_part_upload = self.s3_client.create_multipart_upload(
            Bucket=self.bucket,
            Key=csv_name,
        )

        part_number = 1
        first_chunk = True
        parts = []
        with BytesIO() as buffer:
            for chunk in pd.read_sql_query(query, chunksize=10000, con=db.engine):
                with StringIO() as string_buffer:
                    chunk.to_csv(string_buffer, index=False, header=first_chunk)
                    first_chunk = False

                    buffer.write(string_buffer.getvalue().encode('utf-8'))

                    if buffer.tell() >= self.chunk_size:
                        buffer.seek(0)

                        response = self.s3_client.upload_part(
                            Body=buffer,
                            Bucket=self.bucket,
                            Key=csv_name,
                            PartNumber=part_number,
                            UploadId=multi_part_upload["UploadId"],
                        )
                        parts.append({"PartNumber": part_number, "ETag": response["ETag"]})
                        part_number += 1

                        buffer.seek(0)
                        buffer.truncate()

            if buffer.tell() > 0:  # upload the remaining data
                buffer.seek(0)
                response = self.s3_client.upload_part(
                    Body=buffer,
                    Bucket=self.bucket,
                    Key=csv_name,
                    PartNumber=part_number,
                    UploadId=multi_part_upload["UploadId"],
                )
                parts.append({"PartNumber": part_number, "ETag": response["ETag"]})

        self.s3_client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=csv_name,
            MultipartUpload={"Parts": parts},
            UploadId=multi_part_upload["UploadId"],
        )

        logger.info(f"Upload complete: {csv_name}")
