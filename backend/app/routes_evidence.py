from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import get_current_user
from .models import Evidence, Dispute, User
from .schemas import EvidenceResponse


router = APIRouter(
    prefix="/api/disputes",
    tags=["Evidence"],
)

@router.get(
    "/{dispute_id}/evidence",
    response_model=list[EvidenceResponse],
)
def get_dispute_evidence(
    dispute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find the dispute
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

    transaction = dispute.transaction

    if current_user.role == "CUSTOMER":
        if dispute.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found",
            )

    elif current_user.role == "MERCHANT":
        if not transaction or transaction.merchant_name != current_user.name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found",
            )

    elif current_user.role == "INVESTIGATOR":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    evidence = (
        db.query(Evidence)
        .filter(Evidence.dispute_id == dispute.id)
        .order_by(Evidence.uploaded_at.desc())
        .all()
    )

    return evidence