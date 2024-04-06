from sqlalchemy.orm import sessionmaker
from db.engine import engine

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
