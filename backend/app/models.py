from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base

import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    INVESTIGATOR = "investigator"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(
        SQLEnum(
            UserRole,
            name="userrole",
            values_callable=lambda enum_cls: [e.value.upper() for e in enum_cls],
        ),
        nullable=False,
    )

    cards = relationship(
        "Card",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    disputes = relationship(
        "Dispute",
        back_populates="customer",
        foreign_keys="Dispute.customer_id",
    )


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String, unique=True, nullable=False)
    card_type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="cards")

    transactions = relationship(
        "Transaction",
        back_populates="card",
        cascade="all, delete-orphan",
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    order_id = Column(String, nullable=True)
    merchant_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    payment_method = Column(String, nullable=False, default="CREDIT_CARD")
    transaction_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    card = relationship("Card", back_populates="transactions")
    customer = relationship("User")

    dispute = relationship(
        "Dispute",
        back_populates="transaction",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)

    dispute_id = Column(String, unique=True, index=True, nullable=False)

    reason = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(String, default="OPEN", nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    resolved_at = Column(DateTime, nullable=True)

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False,
    )

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    transaction = relationship(
        "Transaction",
        back_populates="dispute",
    )

    customer = relationship(
        "User",
        back_populates="disputes",
        foreign_keys=[customer_id],
    )

    evidence = relationship(
        "Evidence",
        back_populates="dispute",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="dispute",
        cascade="all, delete-orphan",
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)

    evidence_type = Column(String, nullable=False)
    submitted_by = Column(String, nullable=False)

    extracted_text = Column(Text, nullable=True)
    extracted_facts = Column(JSONB, nullable=True)

    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    dispute_id = Column(
        Integer,
        ForeignKey("disputes.id"),
        nullable=False,
    )

    dispute = relationship(
        "Dispute",
        back_populates="evidence",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)

    details = Column(Text, nullable=True)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    dispute_id = Column(
        Integer,
        ForeignKey("disputes.id"),
        nullable=False,
    )

    dispute = relationship(
        "Dispute",
        back_populates="audit_logs",
    )