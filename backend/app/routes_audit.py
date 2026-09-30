from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import get_current_user
from .models import Dispute, AuditLog, User, Transaction
from .schemas import AuditLogResponse


router = APIRouter(
    prefix="/api/disputes",
    tags=["Audit & Status"],
)


@router.get(
    "/{dispute_id}/audit-logs",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
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
        query = query.filter(
            Dispute.customer_id == current_user.id
        )

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

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.dispute_id == dispute.id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )

    return logs