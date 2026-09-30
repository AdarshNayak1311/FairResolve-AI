from .services.pdf_extractor import extract_text_from_pdf
from .services.evidence_classifier import classify_evidence
from .services.fact_extractor import extract_facts
from .services.gemini_evidence_extractor import (
    analyze_evidence,
    ai_result_to_facts,
)

import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status,
)
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import get_current_user
from .models import Dispute, Evidence, User


router = APIRouter(
    prefix="/api/disputes",
    tags=["Evidence Upload"],
)


UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


@router.post(
    "/{dispute_id}/upload-evidence",
    status_code=status.HTTP_201_CREATED,
)
async def upload_evidence(
    dispute_id: str,
    file: UploadFile = File(...),
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
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot upload evidence to this dispute",
            )

    elif current_user.role == "MERCHANT":
        if not transaction or transaction.merchant_name != current_user.name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot upload evidence to this dispute",
            )

    elif current_user.role == "INVESTIGATOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investigators cannot upload evidence",
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role",
        )

    
    # Check file extension
    original_name = file.filename or ""
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, PNG, JPG and JPEG files are allowed",
        )

    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename,
    )

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    # Extract text and analyze PDF evidence
    extracted_text = None
    evidence_type = "UNCLASSIFIED"
    extracted_facts = {}

    if extension == ".pdf":
        try:
            extracted_text = extract_text_from_pdf(file_path)

            if extracted_text:
                # ---------------------------------------------
                # Try Gemini AI first
                # ---------------------------------------------

                ai_result = analyze_evidence(extracted_text)

                if ai_result:
                    evidence_type = ai_result.evidence_type
                    extracted_facts = ai_result_to_facts(ai_result)

                    if ai_result.summary:
                        extracted_facts["ai_summary"] = ai_result.summary

                    print(
                        f"Gemini AI analyzed evidence as: "
                        f"{evidence_type}"
                    )

                else:
                    # -----------------------------------------
                    # Existing rule-based fallback
                    # -----------------------------------------

                    print(
                        "Gemini unavailable. "
                        "Using rule-based evidence extraction."
                    )

                    evidence_type = classify_evidence(extracted_text)
                    extracted_facts = extract_facts(extracted_text)

        except Exception as exc:
            print(f"Evidence processing failed: {exc}")

            extracted_text = None
            evidence_type = "UNCLASSIFIED"
            extracted_facts = {}

    # Determine who submitted the evidence
    submitted_by = current_user.role
    # if current_user.role == "CUSTOMER":
    #     submitted_by = "CUSTOMER"
    # elif current_user.role == "MERCHANT":
    #     submitted_by = "MERCHANT"
    # else:
    #     submitted_by = "INVESTIGATOR"

    # Create database record
    evidence = Evidence(
        file_name=original_name,
        file_path=file_path,
        evidence_type=evidence_type,
        submitted_by=submitted_by,
        extracted_text=extracted_text,
        extracted_facts=extracted_facts,
        dispute_id=dispute.id,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return {
        "message": "Evidence uploaded successfully",
        "evidence_id": evidence.id,
        "file_name": evidence.file_name,
        "file_path": evidence.file_path,
        "evidence_type": evidence.evidence_type,
        "submitted_by": evidence.submitted_by,
    }