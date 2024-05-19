from minio import Minio
import os
from typing import Dict
from utilities import logger

class ImageUploader:
    def __init__(self, settings: Dict) -> None:
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("DEV_MODE").upper() != "TRUE"    # Set to True if SSL/TLS is enabled
        )
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME")
        self.settings = settings

        # Create the bucket if it doesn't exist.
        found = self.client.bucket_exists(self.bucket_name)
        if not found:
            self.client.make_bucket(self.bucket_name)
            logger.info(f"Created bucket {self.bucket_name}")
        else:
            logger.info(f"Bucket {self.bucket_name} already exists")

    def upload(self, file_path: str, destination_filename: str) -> str:
        # Upload the file, renaming it in the process
        self.client.fput_object(
            bucket_name=self.bucket_name, 
            object_name=destination_filename, 
            file_path=file_path,
        )
        
        img_url = f"{os.getenv('WEB_ACCESS_MINIO_ENDPOINT')}/{self.bucket_name}/{destination_filename}"
        logger.info(f"{file_path} successfully uploaded as object {destination_filename} to bucket {self.bucket_name}, url is {img_url}")

        return img_url