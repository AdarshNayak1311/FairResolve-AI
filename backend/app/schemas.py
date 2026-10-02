from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    INVESTIGATOR = "investigator"

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.CUSTOMER

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value

class CardCreate(BaseModel):
    card_number: str
    card_type: str


class CardResponse(BaseModel):
    id: int
    card_number: str
    card_type: str

    model_config = ConfigDict(from_attributes=True)

class TransactionCreate(BaseModel):
    transaction_id: str
    order_id: str
    merchant_name: str
    amount: float
    currency: str = "INR"
    payment_method: str
    card_id: int | None = None


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    order_id: str | None = None
    merchant_name: str
    amount: float
    currency: str
    payment_method: str
    transaction_date: datetime
    card_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class DisputeCreate(BaseModel):
    transaction_id: str
    reason: str
    description: str | None = None


class DisputeResponse(BaseModel):
    id: int
    dispute_id: str
    reason: str
    description: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
    transaction_id: int
    customer_id: int

    model_config = ConfigDict(from_attributes=True)

class EvidenceCreate(BaseModel):
    file_name: str
    evidence_type: str
    submitted_by: str
    extracted_text: str | None = None

class EvidenceResponse(BaseModel):
    id: int
    file_name: str
    file_path: str | None
    evidence_type: str
    submitted_by: str
    extracted_text: str | None
    uploaded_at: datetime
    dispute_id: int

    model_config = ConfigDict(from_attributes=True)

class MerchantDisputeResponse(BaseModel):
    id: int
    dispute_id: str
    reason: str
    description: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
    transaction_id: int
    customer_id: int

    model_config = ConfigDict(from_attributes=True)

class DisputeStatusUpdate(BaseModel):
    status: str
    details: str | None = None


class AuditLogResponse(BaseModel):
    id: int
    action: str
    actor: str
    details: str | None
    timestamp: datetime
    dispute_id: int

    model_config = ConfigDict(from_attributes=True)