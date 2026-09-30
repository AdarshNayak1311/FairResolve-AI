from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import get_current_user
from .models import Card, User
from .schemas import CardCreate, CardResponse


router = APIRouter(
    prefix="/api/cards",
    tags=["Cards"],
)


@router.post(
    "",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_card(
    card_data: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only customers can add cards
    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can add cards",
        )

    # Check whether this card already exists
    existing_card = (
        db.query(Card)
        .filter(Card.card_number == card_data.card_number)
        .first()
    )

    if existing_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card already exists",
        )

    card = Card(
        card_number=card_data.card_number,
        card_type=card_data.card_type,
        user_id=current_user.id,
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return card


@router.get(
    "",
    response_model=list[CardResponse],
)
def get_my_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cards = (
        db.query(Card)
        .filter(Card.user_id == current_user.id)
        .all()
    )

    return cards


@router.get(
    "/{card_id}",
    response_model=CardResponse,
)
def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    card = (
        db.query(Card)
        .filter(
            Card.id == card_id,
            Card.user_id == current_user.id,
        )
        .first()
    )

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )

    return card