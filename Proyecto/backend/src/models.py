"""
Database models for the Naurat Importation Bot API.

This module defines the SQLAlchemy ORM models used in the database, including:
- `Users`: Represents registered users.
- `Messages`: Stores user messages.
- `ExcelInformation`: Stores product-related information for importation.

Each model is mapped to a corresponding table in the database.
"""

import uuid
from sqlalchemy import JSON, TIMESTAMP, Column, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import String

from src.database import engine, Base


class Users(Base):
    """
    Represents a user in the system.

    Attributes:
        id (UUID): Primary key, uniquely identifies a user.
        google_id (str): Optional Google account ID (unique).
        email (str): User's email address (unique).
        private_id (str): Private identifier (unique).
        created_at (TIMESTAMP): Timestamp of when the user was created.
        messages (relationship): One-to-many relationship with Messages.
        excel_information (relationship): One-to-many relationship with ExcelInformation.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    private_id = Column(String, nullable=True, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    messages = relationship(
        "Messages", back_populates="user", cascade="all, delete-orphan"
    )

    excel_information = relationship(
        "ExcelInformation", back_populates="user", cascade="all, delete-orphan"
    )


class Messages(Base):
    """
    Represents a message sent by a user.

    Attributes:
        id (UUID): Primary key, uniquely identifies a message.
        user_id (UUID): Foreign key referencing the user who sent the message.
        message (JSON): JSON object containing the message content.
        created_at (TIMESTAMP): Timestamp of when the message was created.
        user (relationship): Many-to-one relationship with Users.
    """

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("Users", back_populates="messages")


class ExcelInformation(Base):
    """
    Stores product-related information for importation.

    Attributes:
        id (UUID): Primary key, uniquely identifies a record.
        user_id (UUID): Foreign key referencing the user who owns this data.
        product_name (str): Name of the imported product.
        hs_code (str): Harmonized System code of the product.
        from_country (str): Country of origin.
        cofepris (str): COFEPRIS regulatory information.
        igi_max (str): Maximum General Import Tax.
        igi_reductions (str): Possible IGI reductions.
        iva (str): Value-added tax (IVA).
        dta (str): Customs processing fee (DTA).
        noms (str): Norms and standards applicable.
        created_at (TIMESTAMP): Timestamp of when the record was created.
        user (relationship): Many-to-one relationship with Users.
    """

    __tablename__ = "excel_information"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_name = Column(String, nullable=False)
    hs_code = Column(String, nullable=False)
    from_country = Column(String, nullable=False)
    cofepris = Column(String, nullable=False)
    igi_max = Column(String, nullable=False)
    igi_reductions = Column(String, nullable=False)
    iva = Column(String, nullable=False)
    dta = Column(String, nullable=False)
    noms = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("Users", back_populates="excel_information")


Base.metadata.create_all(bind=engine)
