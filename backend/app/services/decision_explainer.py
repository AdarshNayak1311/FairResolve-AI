from .gemini_evidence_extractor import client
from google.genai import types
from pydantic import BaseModel


class GeminiExplanation(BaseModel):
    summary: str
    recommendation: str
    key_finding: str

def generate_ai_explanation(
    dispute_reason: str,
    customer_score: int,
    merchant_score: int,
    decision: str,
    contradictions: list,
    fact_comparison: dict,
) -> dict | None:

    if client is None:
        return None

    prompt = f"""
You are the explanation layer of FairResolve AI, a dispute resolution system.

Generate a neutral, factual explanation of the resolution result.

Important rules:
- Do NOT change the decision.
- Do NOT invent facts.
- Use only the supplied scores, facts, and contradictions.
- Clearly distinguish evidence from conclusions.
- Keep the explanation concise and suitable for a customer-facing dashboard.
- Do not claim certainty when the decision is NEEDS_REVIEW.

Dispute reason:
{dispute_reason}

Customer score:
{customer_score}

Merchant score:
{merchant_score}

Decision:
{decision}

Fact comparison:
{fact_comparison}

Contradictions:
{contradictions}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeminiExplanation,
                temperature=0,
            ),
        )

        if response.parsed is None:
            return None

        return response.parsed.model_dump()

    except Exception as exc:
        print(f"Gemini explanation failed: {exc}")
        return None

def generate_decision_explanation(
    dispute_reason: str,
    customer_score: int,
    merchant_score: int,
    decision: str,
    contradictions: list,
    fact_comparison: dict,
) -> dict:

    ai_explanation = generate_ai_explanation(
        dispute_reason=dispute_reason,
        customer_score=customer_score,
        merchant_score=merchant_score,
        decision=decision,
        contradictions=contradictions,
        fact_comparison=fact_comparison,
    )

    if ai_explanation:
        return ai_explanation
    
    """
    Generate a clear and explainable summary of the dispute decision.
    """

    reason = dispute_reason.upper()

    # --------------------------------------------------
    # PRODUCT NOT RECEIVED
    # --------------------------------------------------

    if reason == "PRODUCT_NOT_RECEIVED":

        delivered = (
            fact_comparison
            .get("delivery_status", {})
            .get("merchant")
        )

        order_match = (
            fact_comparison
            .get("order_id", {})
            .get("match")
        )

        if delivered == "DELIVERED" and order_match:

            summary = (
                "The customer provided evidence of the purchase, "
                "while the merchant provided evidence indicating that "
                "the same order was delivered. The merchant's delivery "
                "evidence directly conflicts with the customer's claim "
                "that the product was not received."
            )

            if decision == "MERCHANT_FAVOR":
                recommendation = (
                    "Based on the available evidence, the dispute "
                    "currently favors the merchant."
                )

            elif decision == "CUSTOMER_FAVOR":
                recommendation = (
                    "Although delivery evidence is present, the overall "
                    "evidence currently favors the customer."
                )

            else:
                recommendation = (
                    "The evidence contains conflicting signals and "
                    "requires further review."
                )

            return {
                "summary": summary,
                "recommendation": recommendation,
                "key_finding": (
                    "Merchant evidence indicates delivery of the "
                    "same order referenced by the customer."
                ),
            }

    # --------------------------------------------------
    # GENERIC FALLBACK
    # --------------------------------------------------

    if decision == "CUSTOMER_FAVOR":
        recommendation = (
            "The available evidence currently favors the customer."
        )

    elif decision == "MERCHANT_FAVOR":
        recommendation = (
            "The available evidence currently favors the merchant."
        )

    else:
        recommendation = (
            "The available evidence is inconclusive and requires "
            "further review."
        )

    return {
        "summary": (
            "The evidence was analyzed using evidence scores, "
            "extracted facts, and detected contradictions."
        ),
        "recommendation": recommendation,
        "key_finding": (
            "Review the evidence comparison and contradictions "
            "for the basis of the decision."
        ),
    }