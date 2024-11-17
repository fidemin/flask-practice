import csv
import logging
from io import StringIO, BytesIO

import pandas as pd
from flask import current_app as app
from memory_profiler import profile
from sqlalchemy import text

from src.main import db
from src.main.common.fileserver.fileserver import ThisFileserverClient
from src.main.common.fileserver.util import MultipartUploader
from src.main.operators.operator import Operator

logger = logging.getLogger(__name__)


def get_table_columns(table_name):
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
    return [row[0] for row in db.session.execute(text(query))]


class UploadCSVFromTableOperator(Operator):
    def __init__(self, **kwargs):
        self.table_name = kwargs["table_name"]
        self.schema = "temp"

        # NOTE: s3 client multipart requires minimum 5MB part size
        min_chunk_size = 5 * 1024 * 1024  # 5MB
        self.chunk_size = kwargs.get("chunk_size", min_chunk_size)  # default: 5MB
        assert self.chunk_size >= min_chunk_size, "chunk_size should be greater than 5MB"

        self.bucket = app.config['S3_BUCKET']
        self.fileserver_client = ThisFileserverClient()

    @profile
    def execute(self):
        logger.info(f"Upload csv from table: {self.table_name}")
        query = f"SELECT * FROM {self.schema}.{self.table_name} order by id"

        csv_name = f"{self.table_name}.csv"

        with MultipartUploader(self.fileserver_client, csv_name) as uploader:
            first_chunk = True
            with BytesIO() as buffer:
                for chunk in pd.read_sql_query(query, chunksize=50000, con=db.engine):
                    logger.info(f"chunk memory use: {chunk.memory_usage().sum()}")
                    with StringIO() as string_buffer:
                        chunk.to_csv(string_buffer, index=False, header=first_chunk)
                        first_chunk = False

                        buffer.write(string_buffer.getvalue().encode('utf-8'))

                        if buffer.tell() >= self.chunk_size:
                            logger.info(f"buffer size: {buffer.tell()} bytes")
                            buffer.seek(0)
                            uploader.upload_part(buffer)

                            # reset buffer
                            buffer.seek(0)
                            buffer.truncate(0)

                if buffer.tell() > 0:
                    buffer.seek(0)
                    uploader.upload_part(buffer)

    def execute_alt(self):
        logger.info(f"Upload csv from table: {self.table_name}")
        query = f"SELECT * FROM {self.schema}.{self.table_name} order by id"

        csv_name = f"{self.table_name}.csv"

        with MultipartUploader(self.fileserver_client, csv_name) as uploader:
            first_chunk = True
            with BytesIO() as buffer:
                for rows in db.session.execute(text(query)).yield_per(50000):
                    with StringIO() as string_buffer:
                        writer = csv.writer(string_buffer)
                        if first_chunk:
                            columns = get_table_columns(self.table_name)
                            writer.writerow(columns)
                        first_chunk = False

                        writer.writerow(rows)
                        buffer.write(string_buffer.getvalue().encode('utf-8'))

                        if buffer.tell() >= self.chunk_size:
                            logger.info(f"buffer size: {buffer.tell()} bytes")
                            buffer.seek(0)
                            uploader.upload_part(buffer)

                            # reset buffer
                            buffer.seek(0)
                            buffer.truncate(0)

                if buffer.tell() > 0:
                    buffer.seek(0)
                    uploader.upload_part(buffer)
