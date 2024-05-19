import os
import sys
from datetime import datetime
from fastapi.requests import Request
from fastapi import HTTPException
import jwt
import hashlib
from jose import JWTError
import logging

main_path = os.path.dirname(os.path.dirname(__file__))

os.makedirs(os.path.join(main_path, "log"), exist_ok=True)
handler_file = logging.FileHandler(os.path.join(main_path, "log", "server.log"), encoding='utf-8')
handler_stream = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s (%(filename)s %(lineno)d)', datefmt='%Y/%m/%d %I:%M:%S')
handler_file.setFormatter(formatter)
handler_stream.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler_file)
logger.addHandler(handler_stream)

def check_envs():
    try:
        if not os.getenv("VERSION"):
            raise Exception("Cannot found environment variable: VERSION")
        if not os.getenv("PORT"):
            raise Exception("Cannot found environment variable: PORT")
        if not os.getenv("DATABASE_URL"):
            raise Exception("Cannot found environment variable: DATABASE_URL")
        if not os.getenv("MINIO_ENDPOINT"):
            raise Exception("Cannot found environment variable: MINIO_ENDPOINT")
        if not os.getenv("WEB_ACCESS_MINIO_ENDPOINT"):
            raise Exception("Cannot found environment variable: WEB_ACCESS_MINIO_ENDPOINT")
        if not os.getenv("MINIO_ACCESS_KEY"):
            raise Exception("Cannot found environment variable: MINIO_ACCESS_KEY")
        if not os.getenv("MINIO_SECRET_KEY"):
            raise Exception("Cannot found environment variable: MINIO_SECRET_KEY")
        if not os.getenv("MINIO_BUCKET_NAME"):
            raise Exception("Cannot found environment variable: MINIO_BUCKET_NAME")
        if not os.getenv("IMAGE_LENGTH_THRESHOLD"):
            raise Exception("Cannot found environment variable: IMAGE_LENGTH_THRESHOLD")
        if not os.getenv("IMAGE_SHRINK_RATIO"):
            raise Exception("Cannot found environment variable: IMAGE_SHRINK_RATIO")
        if not os.getenv("FREE_TRIED_NUMBER"):
            raise Exception("Cannot found environment variable: FREE_TRIED_NUMBER")
        if not os.getenv("MAX_PREDICT_NUMBER_AFTER_PAID"):
            raise Exception("Cannot found environment variable: MAX_PREDICT_NUMBER_AFTER_PAID")
    except Exception as e:
        logger.error(e)
        sys.exit(1)
        
def generate_unique_id(identifier: str) -> str:
    """Generate SHA256 hash of the identifier."""
    return hashlib.sha256(identifier.encode()).hexdigest()


def create_filename() -> str:
    iso_now = datetime.now().isoformat().replace(":", "_").replace(".", "_")
    return f"{iso_now}.png"


def authenticate(req: Request):
    try:
        auth_header = req.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not "Bearer " in auth_header:
            raise HTTPException(status_code=401, detail="Invalid token")

        access_token = auth_header.split("Bearer ")[-1]
        if not access_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        decoded = jwt.decode(access_token, options={"verify_signature": False})
        return decoded
    except (JWTError, HTTPException):
        raise HTTPException(status_code=401, detail="Invalid token")
