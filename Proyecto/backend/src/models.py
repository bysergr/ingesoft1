import uuid
from sqlalchemy import JSON, TIMESTAMP, Column, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import String


from src.database import engine, Base



class Users(Base):
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
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("Users", back_populates="messages")


class ExcelInformation(Base):
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