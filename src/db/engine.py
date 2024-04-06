import os
from urllib.parse import urlparse
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
result = urlparse(DATABASE_URL)
db_name = result.path[1:]   # ex: /pillsCounter

# Create db engine
engine = create_engine(DATABASE_URL)
