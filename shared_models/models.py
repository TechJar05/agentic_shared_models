import enum
from sqlalchemy import (
    Column, String, Integer, Boolean, Text,
    ForeignKey, TIMESTAMP, JSON, Enum as SQLEnum
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# 🔹 Role Enum
class RoleEnum(str, enum.Enum):
    md = "md"
    admin = "admin"


# 🔹 Centralized User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Only needed for admin
    is_verified = Column(Boolean, default=False)   # After OTP verification
    is_approved = Column(Boolean, default=False)   # ✅ Approved by admin only
    role = Column(SQLEnum(RoleEnum), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


# 🔹 OTP Verification Table
class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, index=True)
    otp_code = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    is_used = Column(Boolean, default=False)


# 🔹 Employees
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=True)
    current_task_count = Column(Integer, default=0)
    max_capacity = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())


# 🔹 Tasks
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_number = Column(Integer, unique=True, index=True, nullable=False)

    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("employees.id"))
    status = Column(String, default="pending")
    status_pending_approval = Column(Boolean, default=False)

    # For approval process
    requested_status = Column(String, nullable=True)
    completion_requested_at = Column(TIMESTAMP, nullable=True)
    md_approval_status = Column(String, nullable=True)

    priority = Column(String, nullable=True)
    deadline = Column(TIMESTAMP, nullable=True)
    attachments = Column(JSON, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", backref="created_tasks", foreign_keys=[created_by_id])

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())

    # Deadline justification
    justification_text = Column(Text, nullable=True)
    justification_pending = Column(Boolean, default=False)
    deadline_extension_count = Column(Integer, default=0)
    max_extensions_allowed = Column(Integer, default=2)


# 🔹 Message Log
class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)


# 🔹 Document Table
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_url = Column(String, nullable=False)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    doc_metadata = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
