import csv
import logging
import os
from io import StringIO, BytesIO

import pandas as pd
import psutil
from boto3.s3.transfer import TransferConfig
from flask import current_app as app
from memory_profiler import profile
from sqlalchemy import text

from src.main import db
from src.main.common.fileserver.fileserver import ThisFileserverClient
from src.main.common.fileserver.util import MultipartUploader
from src.main.operators.operator import Operator

logger = logging.getLogger(__name__)


def print_memory_usage(label=""):
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    logger.info(f"{label} Memory usage: {memory_usage:.2f} MB")


def get_table_columns(schema_name, table_name):
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' and table_schema = '{schema_name}'"
    return [row[0] for row in db.session.execute(text(query))]


def table_rows_fetcher(schema_name: str, table_name: str, row_chunk_size):
    # NOTE: Do not use fetchmany or yield_per for streaming fetching solely.
    #   It stores all the rows of query result in memory Use it with offset/limit for memory optimization.
    sql_str = f"SELECT * FROM {schema_name}.{table_name} order by id offset :offset limit :limit"
    offset = 0

    fetch_size = 100000
    if row_chunk_size > fetch_size:
        fetch_size = row_chunk_size

    query = db.session.execute(text(sql_str), {"offset": offset, "limit": fetch_size})
    rows = query.fetchmany(fetch_size)
    while rows:
        while rows:
            yield rows
            rows = query.fetchmany(row_chunk_size)

        offset += fetch_size
        query = db.session.execute(text(sql_str), {"offset": offset, "limit": fetch_size})
        rows = query.fetchmany(row_chunk_size)


def table_data_generator(schema_name: str, table_name: str, chunk_size, is_chunk_size_minimum=False):
    with StringIO() as string_buffer:
        byte = b''
        writer = csv.writer(string_buffer)
        columns = get_table_columns(schema_name, table_name)
        writer.writerow(columns)
        row_chunk_size = 1000

        for rows in table_rows_fetcher(schema_name, table_name, row_chunk_size):
            writer.writerows(rows)
            byte += string_buffer.getvalue().encode('utf-8')

            string_buffer.truncate(0)
            string_buffer.seek(0)

            # logger.info(f"buffer size: {len(byte)} bytes before yield")
            while len(byte) >= chunk_size:
                # logger.info(f"buffer size: {len(byte)} bytes")
                if is_chunk_size_minimum:
                    yield byte
                    byte = b''
                else:
                    yield byte[:chunk_size]
                    byte = byte[chunk_size:]

        if len(byte) > 0:
            yield byte


class TableIO:
    def __init__(self, schema_name: str, table_name: str, is_chunk_size_minimum=False):
        self.generator = None
        self.schema_name = schema_name
        self.table_name = table_name
        self.is_chunk_size_minimum = is_chunk_size_minimum

    def read(self, size_: int):
        if self.generator is None:
            self.generator = table_data_generator(
                self.schema_name,
                self.table_name,
                size_,
                is_chunk_size_minimum=self.is_chunk_size_minimum)

        try:
            print_memory_usage()
            return next(self.generator)
        except StopIteration:
            return b''


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
                # memory leak in read_sql_query
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

    @profile
    def execute_alt(self):
        logger.info(f"Upload csv from table: {self.table_name}")
        csv_name = f"{self.table_name}.csv"

        with MultipartUploader(self.fileserver_client, csv_name) as uploader:
            table_io = TableIO(self.schema, self.table_name, is_chunk_size_minimum=True)
            while chunk := table_io.read(self.chunk_size):
                with BytesIO(chunk) as buffer:
                    print_memory_usage("before upload part")
                    uploader.upload_part(buffer)

    @profile
    def execute_raw(self):
        logger.info(f"Upload csv from table: {self.table_name}")

        csv_name = f"{self.table_name}.csv"

        table_buffer = TableIO("temp", self.table_name)

        config = TransferConfig(use_threads=False)
        response = self.fileserver_client.upload_fileobj(fileobj=table_buffer, key=csv_name, config=config)
        logger.info(response)
