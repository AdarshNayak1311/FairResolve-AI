import os
from typing import Literal

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()


MODEL_NAME = "gemini-3.5-flash-lite"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiEvidenceResult(BaseModel):
    evidence_type: Literal[
        "PURCHASE_RECEIPT",
        "REFUND_CONFIRMATION",
        "DELIVERY_TRACKING",
        "DELIVERY_CONFIRMATION",
        "WRONG_PRODUCT_EVIDENCE",
        "ORDER_ITEM_CONFIRMATION",
        "DAMAGE_CLAIM",
        "PRODUCT_CONDITION_CONFIRMATION",
        "DUPLICATE_CHARGE_EVIDENCE",
        "CHARGE_LEDGER_CONFIRMATION",
        "UNCLASSIFIED",
    ] = "UNCLASSIFIED"

    order_id: str | None = None
    amount: float | None = None
    currency: str | None = None
    tracking_id: str | None = None

    delivery_status: Literal[
        "DELIVERED",
        "IN_TRANSIT",
    ] | None = None

    refund_status: Literal[
        "PROCESSED",
    ] | None = None

    date: str | None = None

    ordered_product: str | None = None
    received_product: str | None = None

    damage_status: Literal[
        "DAMAGED",
        "NOT_DAMAGED",
    ] | None = None

    charge_count: int | None = None

    summary: str = Field(
        default="",
        description="Brief factual summary of the evidence.",
    )


client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)


def analyze_evidence(text: str) -> GeminiEvidenceResult | None:
    """
    Analyze evidence text using Gemini.

    Returns structured AI output on success.
    Returns None on missing API key or any AI/API error,
    allowing the existing rule-based fallback to continue.
    """

    if not text or not text.strip():
        return None

    if client is None:
        print("Gemini API key not configured. Using fallback extraction.")
        return None

    prompt = f"""
You are an evidence extraction system for a payment dispute resolution platform.

Analyze the evidence text below and extract ONLY facts explicitly supported
by the document.

Do not invent, guess, or infer missing values.

Classify the document into exactly one supported evidence type.

Important rules:
- Use UNCLASSIFIED when the evidence type is unclear.
- Extract order ID only when an explicit Order ID, Order Number, or Order #
  appears.
- Extract amount only when an amount is explicitly present.
- Extract product names only when the document explicitly identifies them.
- Extract charge_count only when the document explicitly gives a number of
  charges or clearly states charged twice/double charged.
- Use DAMAGED only when the document explicitly indicates damage.
- Use NOT_DAMAGED only when the document explicitly indicates no damage,
  good condition, or an equivalent statement.
- Do not convert opinions into facts.

Evidence text:

{text}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiEvidenceResult,
                temperature=0,
            ),
        )

        if response.parsed is None:
            print("Gemini returned no structured result.")
            return None

        return response.parsed

    except Exception as exc:
        print(f"Gemini evidence analysis failed: {exc}")
        return None


def ai_result_to_facts(
    result: GeminiEvidenceResult,
) -> dict:
    """
    Convert Gemini's structured result into the same fact format
    already used by FairResolve.
    """

    facts = {}

    fields = [
        "order_id",
        "amount",
        "currency",
        "tracking_id",
        "delivery_status",
        "refund_status",
        "date",
        "ordered_product",
        "received_product",
        "damage_status",
        "charge_count",
    ]

    for field in fields:
        value = getattr(result, field)

        if value is not None:
            facts[field] = value

    return facts