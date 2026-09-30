from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import get_current_user
from .models import Transaction, Card, User
from .schemas import TransactionCreate, TransactionResponse


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only customers can create transactions
    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create transactions",
        )

    payment_method = transaction_data.payment_method.upper()

    if payment_method not in {"UPI", "CREDIT_CARD", "DEBIT_CARD"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment method",
        )

    if payment_method == "UPI":
        card_id = None

    else:
        if transaction_data.card_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A card is required for this payment method",
            )

        card = (
            db.query(Card)
            .filter(
                Card.id == transaction_data.card_id,
                Card.user_id == current_user.id,
            )
            .first()
        )

        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found",
            )

        card_id = transaction_data.card_id

    # Check duplicate transaction ID
    existing_transaction = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_id
            == transaction_data.transaction_id
        )
        .first()
    )

    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID already exists",
        )

    transaction = Transaction(
        transaction_id=transaction_data.transaction_id,
        order_id=transaction_data.order_id,
        merchant_name=transaction_data.merchant_name,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        payment_method=payment_method,
        card_id=card_id,
        customer_id=current_user.id,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def get_my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.customer_id == current_user.id)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    return transactions


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_id == transaction_id,
            Transaction.customer_id == current_user.id,
        )
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction