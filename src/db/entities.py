from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, JSON, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from utilities import generate_unique_id
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(64), primary_key=True)  # SHA256 hash will be stored as a 64-character hexadecimal string
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True, index=True)
    avatar_uri = Column(String)
    free_tried_count = Column(Integer, default=os.getenv("FREE_TRIED_NUMBER"))
    available_predict_count = Column(Integer, default=os.getenv("MAX_PREDICT_NUMBER_AFTER_PAID"))
    is_paid = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # One to many
    predict_records = relationship("PredictRecord", back_populates="user")
    # One to one
    orders = relationship("Order", back_populates="user")

    def __init__(self, username, email, avatar_uri):
        self.id = generate_unique_id(email)  # Generate ID based on email
        self.username = username
        self.email = email
        self.avatar_uri = avatar_uri

class PredictRecord(Base):
    __tablename__ = "predict_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # One to one
    raw_img_id = Column(UUID(as_uuid=True), ForeignKey("raw_images.id"))
    raw_img = relationship("RawImage", back_populates="predict_record")
    # One to one
    predict_img_id = Column(UUID(as_uuid=True), ForeignKey("predict_images.id"))
    predict_img = relationship("PredictImage", back_populates="predict_record")
    count = Column(Integer)
    boxes = Column(ARRAY(JSON))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="predict_records")
    note = Column(String(200), default="")


class RawImage(Base):
    __tablename__ = "raw_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    uri = Column(String)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    predict_record = relationship("PredictRecord", back_populates="raw_img")

class PredictImage(Base):
    __tablename__ = "predict_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    uri = Column(String)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    predict_record = relationship("PredictRecord", back_populates="predict_img")

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    merchant_order_no = Column(String, index=True)
    raw_order = Column(JSON)
    payment_results = Column(ARRAY(JSON))  # 每期授權收到的raw data
    period_no = Column(String, index=True)   # 委託單
    payment_type = Column(String, default="Subscription")
    is_canceled = Column(Boolean, default=False)
    is_success = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="orders")

