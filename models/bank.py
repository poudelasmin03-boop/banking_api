from database.db import Base
from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)

from sqlalchemy.orm import relationship
from datetime import timedelta, timezone, datetime
import enum


class DbUser(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    create_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


### Making a Choices
class AccountType(enum.Enum):
    saving = "saving"
    current = "current"


class AccountStatus(enum.Enum):
    active = "active"
    closed = "closed"
    blocked = "blocked"


class DbOpenAccount(Base):
    __tablename__ = "CreateAccount"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_no = Column(String, nullable=False)
    create_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    account = relationship("DbAccount", back_populates="open_account")


class DbAccount(Base):
    __tablename__ = "Account"
    id = Column(Integer, primary_key=True, index=True)

    account_nbr = Column(String, unique=True, nullable=False)
    balance = Column(Float, default=0.00)
    account_type = Column(Enum(AccountType), default=AccountType.saving)
    account_status = Column(Enum(AccountStatus), default=AccountStatus.active)
    create_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    open_id = Column(Integer, ForeignKey("CreateAccount.id"))
    open_account = relationship("DbOpenAccount", back_populates="account")
