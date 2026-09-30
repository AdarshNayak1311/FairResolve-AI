from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from .database import get_db
from .dependencies import get_current_user
from .models import Dispute, Transaction, User, AuditLog
from .schemas import DisputeCreate, DisputeResponse


router = APIRouter(
    prefix="/api/disputes",
    tags=["Disputes"],
)


@router.post(
    "",
    response_model=DisputeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dispute(
    dispute_data: DisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only customers can create disputes
    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create disputes",
        )

    # Find the transaction and make sure it belongs to this customer
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_id == dispute_data.transaction_id,
            Transaction.customer_id == current_user.id,
        )
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    # One transaction can only have one dispute
    existing_dispute = (
        db.query(Dispute)
        .filter(Dispute.transaction_id == transaction.id)
        .first()
    )

    if existing_dispute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This transaction already has a dispute",
        )

    # Generate a human-readable dispute ID
    dispute_id = f"DIS-{uuid.uuid4().hex[:8].upper()}"

    dispute = Dispute(
        dispute_id=dispute_id,
        reason=dispute_data.reason,
        description=dispute_data.description,
        status="OPEN",
        transaction_id=transaction.id,
        customer_id=current_user.id,
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)

    return dispute


@router.get("", response_model=list[DisputeResponse])
def get_my_disputes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "CUSTOMER":
        disputes = (
            db.query(Dispute)
            .filter(Dispute.customer_id == current_user.id)
            .order_by(Dispute.created_at.desc())
            .all()
        )

    elif current_user.role == "MERCHANT":
        disputes = (
            db.query(Dispute)
            .join(Transaction)
            .filter(Transaction.merchant_name == current_user.name)
            .order_by(Dispute.created_at.desc())
            .all()
        )

    elif current_user.role == "INVESTIGATOR":
        disputes = (
            db.query(Dispute)
            .order_by(Dispute.created_at.desc())
            .all()
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    return disputes


@router.get("/{dispute_id}", response_model=DisputeResponse)
def get_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Dispute)
        .join(Transaction)
        .filter(Dispute.dispute_id == dispute_id)
    )

    if current_user.role == "CUSTOMER":
        query = query.filter(Dispute.customer_id == current_user.id)

    elif current_user.role == "MERCHANT":
        query = query.filter(
            Transaction.merchant_name == current_user.name
        )

    elif current_user.role == "INVESTIGATOR":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    dispute = query.first()

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found",
        )

    return dispute

@router.patch(
    "/{dispute_id}/resolve",
    response_model=DisputeResponse,
)
def resolve_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only investigators can resolve disputes
    if current_user.role != "INVESTIGATOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only investigators can resolve disputes",
        )

    dispute = (
        db.query(Dispute)
        .filter(Dispute.dispute_id == dispute_id)
        .first()
    )

    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found",
        )

    dispute.status = "RESOLVED"
    dispute.resolved_at = datetime.now(timezone.utc)

    audit_log = AuditLog(
        action="DISPUTE_RESOLVED",
        actor=current_user.email,
        details=f"Dispute {dispute.dispute_id} resolved by investigator.",
        dispute_id=dispute.id,
    )

    db.add(audit_log)

    db.commit()
    db.refresh(dispute)

    return dispute