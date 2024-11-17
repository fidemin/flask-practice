import logging

from src.main.common.fileserver.fileserver import FileServerClient

logger = logging.getLogger(__name__)


class MultipartUploader:
    def __init__(self, fileserver_client: FileServerClient, filename):
        self.fileserver_client = fileserver_client
        self.filename = filename
        self.parts = []
        self.part_number = 1
        self.upload_id = None

    def __enter__(self):
        response = self.fileserver_client.create_multipart_upload(key=self.filename)
        self.upload_id = response["UploadId"]
        logger.info(f"Initialized multipart upload: {self.upload_id}")
        return self

    def upload_part(self, buffer):
        response = self.fileserver_client.upload_part(
            body=buffer,
            key=self.filename,
            part_number=self.part_number,
            upload_id=self.upload_id,

        )
        logger.info(f"Uploaded part {self.part_number}, size {buffer.tell()} bytes.")
        self.parts.append({"PartNumber": self.part_number, "ETag": response["ETag"]})
        self.part_number += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.fileserver_client.abort_multipart_upload(
                key=self.filename,
                upload_id=self.upload_id,
            )
            logger.error(f"Failed to upload: {self.filename}")
        else:
            self.fileserver_client.complete_multipart_upload(
                key=self.filename,
                multipart_upload={"Parts": self.parts},
                upload_id=self.upload_id,
            )
            logger.info(f"Upload complete: {self.filename}")
