import re


def extract_facts(text: str) -> dict:
    """
    Extract useful structured facts from evidence text.
    """

    if not text:
        return {}

    facts = {}

    # --------------------------------------------------
    # Order ID
    # --------------------------------------------------

    order_match = re.search(
        r"\bOrder\s*(?:ID|Number|#)\s*[:#-]?\s*([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE,
    )

    if order_match:
        facts["order_id"] = order_match.group(1)

    # --------------------------------------------------
    # Tracking ID
    # --------------------------------------------------

    tracking_match = re.search(
        r"\bTracking\s+(?:ID|Number|Code)\s*[:#-]\s*([A-Za-z0-9-]+)",
        text,
        re.IGNORECASE,
    )

    if tracking_match:
        facts["tracking_id"] = tracking_match.group(1)

    # --------------------------------------------------
    # Amount
    # --------------------------------------------------

    amount_match = re.search(
        r"\b(?:amount\s*paid|refund\s*amount|total\s*amount|amount)"
        r"\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    if amount_match:
        amount_string = amount_match.group(1).replace(",", "")
        facts["amount"] = float(amount_string)

    # --------------------------------------------------
    # Currency
    # --------------------------------------------------

    currency_match = re.search(
        r"\b(INR|USD|EUR|GBP)\b|₹|\bRs\.?",
        text,
        re.IGNORECASE,
    )

    if currency_match:
        currency = currency_match.group(1)

        if currency:
            facts["currency"] = currency.upper()
        elif "₹" in currency_match.group(0) or re.search(
            r"\bRs\.?",
            currency_match.group(0),
            re.IGNORECASE,
        ):
            facts["currency"] = "INR"

    # --------------------------------------------------
    # Delivery status
    # --------------------------------------------------

    if re.search(
        r"\b(delivered|delivery completed|successfully delivered)\b",
        text,
        re.IGNORECASE,
    ):
        facts["delivery_status"] = "DELIVERED"

    elif re.search(
        r"\b(in[\s_-]*transit|shipped)\b",
        text,
        re.IGNORECASE,
    ):
        facts["delivery_status"] = "IN_TRANSIT"

    # --------------------------------------------------
    # Refund status
    # --------------------------------------------------

    if re.search(
        r"\b(refund processed|refund issued|refunded|refund completed)\b",
        text,
        re.IGNORECASE,
    ):
        facts["refund_status"] = "PROCESSED"


        # --------------------------------------------------
    # Ordered product
    # --------------------------------------------------

    ordered_product_match = re.search(
        r"\b(?:ordered|purchased)\s+"
        r"(?:product|item)?\s*[:\-]?\s*"
        r"([A-Za-z0-9][^,\n.;]{2,80})",
        text,
        re.IGNORECASE,
    )

    if ordered_product_match:
        facts["ordered_product"] = (
            ordered_product_match.group(1).strip()
        )

    # --------------------------------------------------
    # Received product
    # --------------------------------------------------

    received_product_match = re.search(
        r"\b(?:received|got)\s+"
        r"(?:product|item)?\s*[:\-]?\s*"
        r"([A-Za-z0-9][^,\n.;]{2,80})",
        text,
        re.IGNORECASE,
    )

    if received_product_match:
        facts["received_product"] = (
            received_product_match.group(1).strip()
        )

    # --------------------------------------------------
    # Damage status
    # --------------------------------------------------

    if re.search(
        r"\b(no damage|undamaged|good condition|condition verified)\b",
        text,
        re.IGNORECASE,
    ):
        facts["damage_status"] = "NOT_DAMAGED"

    elif re.search(
        r"\b(damaged|broken|cracked|defective|physical damage)\b",
        text,
        re.IGNORECASE,
    ):
        facts["damage_status"] = "DAMAGED"

    # --------------------------------------------------
    # Duplicate charge count
    # --------------------------------------------------

    charge_count_match = re.search(
        r"\b(?:charge count|number of charges|charges)\s*[:\-]?\s*(\d+)",
        text,
        re.IGNORECASE,
    )

    if charge_count_match:
        facts["charge_count"] = int(
            charge_count_match.group(1)
        )

    elif re.search(
        r"\b(charged twice|double charged|duplicate charge|duplicate payment)\b",
        text,
        re.IGNORECASE,
    ):
        facts["charge_count"] = 2

    # --------------------------------------------------
    # Date
    # --------------------------------------------------

    date_match = re.search(
        r"\b(\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4})\b",
        text,
        re.IGNORECASE,
    )

    if date_match:
        facts["date"] = date_match.group(1)

    return facts