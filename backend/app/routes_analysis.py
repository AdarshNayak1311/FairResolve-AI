from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from .database import get_db
from .dependencies import get_current_user
from .models import Dispute, Evidence, User, AuditLog
from .services.fairness_engine import calculate_evidence_score
from .services.fact_extractor import extract_facts
from .services.decision_explainer import generate_decision_explanation


router = APIRouter(
    prefix="/api/disputes",
    tags=["Dispute Analysis"],
)


@router.get("/{dispute_id}/analyze")
def analyze_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find dispute
    dispute = (
        db.query(Dispute)
        .filter(Dispute.dispute_id == dispute_id)
        .first()
    )

    if not dispute:
        raise HTTPException(
            status_code=404,
            detail="Dispute not found",
        )

    # Get all evidence for this dispute
    evidence_records = (
        db.query(Evidence)
        .filter(Evidence.dispute_id == dispute.id)
        .all()
    )

    # Get transaction details for relevance checking
    transaction = dispute.transaction

    if not transaction:
        raise HTTPException(
            status_code=400,
            detail="Transaction not found for this dispute",
        )

    # Verify access to this dispute
    if current_user.role == "CUSTOMER":
        if dispute.customer_id != current_user.id:
            raise HTTPException(
                status_code=404,
                detail="Dispute not found",
            )

    elif current_user.role == "MERCHANT":
        if transaction.merchant_name != current_user.name:
            raise HTTPException(
                status_code=404,
                detail="Dispute not found",
            )

    elif current_user.role == "INVESTIGATOR":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid user role",
        )

    transaction_order_id = transaction.order_id
    transaction_amount = transaction.amount
    transaction_currency = transaction.currency

    if not evidence_records:
        raise HTTPException(
            status_code=400,
            detail="No evidence available for this dispute",
        )

    # Convert evidence records into relevant and excluded evidence
    evidence_data = []
    excluded_evidence = []

    for evidence in evidence_records:
        facts = evidence.extracted_facts or {}

        if not facts and evidence.extracted_text:
            facts = extract_facts(evidence.extracted_text)

        evidence_order_id = facts.get("order_id")
        evidence_amount = facts.get("amount")
        evidence_currency = facts.get("currency")

        exclusion_reason = None

        # --------------------------------------------------
        # RELEVANCE CHECK
        # --------------------------------------------------

        # 1. Order ID check
        if evidence_order_id:

            if (
                transaction_order_id
                and str(evidence_order_id) != str(transaction_order_id)
            ):
                exclusion_reason = (
                    f"Order ID {evidence_order_id} does not match "
                    f"disputed order ID {transaction_order_id}."
                )

        # 2. Amount check
        if (
            exclusion_reason is None
            and evidence_amount is not None
        ):

            if float(evidence_amount) != float(transaction_amount):
                exclusion_reason = (
                    f"Amount {evidence_amount} does not match "
                    f"disputed transaction amount {transaction_amount}."
                )

        # 3. Currency check
        if (
            exclusion_reason is None
            and evidence_currency
        ):

            if (
                transaction_currency
                and evidence_currency.upper()
                != transaction_currency.upper()
            ):
                exclusion_reason = (
                    f"Currency {evidence_currency} does not match "
                    f"transaction currency {transaction_currency}."
                )

        # --------------------------------------------------
        # EXCLUDE IRRELEVANT EVIDENCE
        # --------------------------------------------------

        if exclusion_reason:

            excluded_evidence.append(
                {
                    "evidence_id": evidence.id,
                    "file_name": evidence.file_name,
                    "reason": exclusion_reason,
                }
            )

            continue

        # --------------------------------------------------
        # INCLUDE RELEVANT EVIDENCE
        # --------------------------------------------------

        evidence_data.append(
            {
                "id": evidence.id,
                "file_name": evidence.file_name,
                "submitted_by": evidence.submitted_by,
                "evidence_type": evidence.evidence_type,
                "extracted_facts": facts,
                "extracted_text": evidence.extracted_text,
            }
        )

    # Run fairness engine FIRST
    result = calculate_evidence_score(
        evidence_data,
        dispute.reason,
    )

    # Generate human-readable explanation
    explanation = generate_decision_explanation(
        dispute_reason=dispute.reason,
        customer_score=result["customer_score"],
        merchant_score=result["merchant_score"],
        decision=result["decision"],
        contradictions=result["contradictions"],
        fact_comparison=result["fact_comparison"],
    )

    # Update dispute status based on analysis
    if result["decision"] in ["CUSTOMER_FAVOR", "MERCHANT_FAVOR"]:
        dispute.status = "RESOLVED"
        dispute.resolved_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        dispute.status = "IN_REVIEW"
        dispute.resolved_at = None

    # Create audit log only if this dispute has not already been analyzed
    existing_analysis_log = (
        db.query(AuditLog)
        .filter(
            AuditLog.dispute_id == dispute.id,
            AuditLog.action == "DISPUTE_ANALYZED",
        )
        .first()
    )

    if not existing_analysis_log:
        audit_log = AuditLog(
            action="DISPUTE_ANALYZED",
            actor=current_user.email,
            details=(
                f"AI analysis completed. "
                f"Decision: {result['decision']}. "
                f"Customer score: {result['customer_score']}. "
                f"Merchant score: {result['merchant_score']}. "
                f"Confidence: {result['confidence']}."
            ),
            dispute_id=dispute.id,
        )

        db.add(audit_log)

    db.commit()

    return {
        "dispute_id": dispute.dispute_id,
        "relevant_evidence": evidence_data,
        "excluded_evidence": excluded_evidence,
        "result": result,
        "explanation": explanation,
    }