def classify_evidence(text: str) -> str:
    """
    Classify evidence based on keywords found in extracted text.
    """

    if not text:
        return "UNCLASSIFIED"

    text_lower = text.lower()

    # ---------------------------------------------
    # Refund evidence
    # ---------------------------------------------

    refund_keywords = [
        "refund",
        "refunded",
        "refund processed",
        "refund issued",
        "money returned",
    ]

    if any(keyword in text_lower for keyword in refund_keywords):
        return "REFUND_CONFIRMATION"

    # ---------------------------------------------
    # Duplicate charge evidence
    # ---------------------------------------------

    duplicate_charge_keywords = [
        "duplicate charge",
        "duplicate payment",
        "charged twice",
        "double charged",
        "charged two times",
        "same transaction charged twice",
    ]

    if any(
        keyword in text_lower
        for keyword in duplicate_charge_keywords
    ):
        return "DUPLICATE_CHARGE_EVIDENCE"

    # ---------------------------------------------
    # Merchant charge ledger confirmation
    # ---------------------------------------------

    charge_ledger_keywords = [
        "transaction ledger",
        "charge ledger",
        "charge count",
        "number of charges",
        "single charge",
        "only one charge",
        "charged once",
    ]

    if any(
        keyword in text_lower
        for keyword in charge_ledger_keywords
    ):
        return "CHARGE_LEDGER_CONFIRMATION"

    # ---------------------------------------------
    # Wrong product evidence
    # ---------------------------------------------

    wrong_product_keywords = [
        "wrong product",
        "wrong item",
        "different product",
        "different item",
        "incorrect product",
        "incorrect item",
        "received a different product",
        "received a different item",
        "item received does not match",
        "product received does not match",
    ]

    if any(
        keyword in text_lower
        for keyword in wrong_product_keywords
    ):
        return "WRONG_PRODUCT_EVIDENCE"

    # ---------------------------------------------
    # Merchant order-item confirmation
    # ---------------------------------------------

    order_item_keywords = [
        "ordered item",
        "ordered product",
        "product shipped",
        "item shipped",
        "sku",
        "product code",
        "item code",
        "order fulfillment",
        "fulfilled item",
    ]

    if any(
        keyword in text_lower
        for keyword in order_item_keywords
    ):
        return "ORDER_ITEM_CONFIRMATION"

    # ---------------------------------------------
    # Merchant product-condition confirmation
    # ---------------------------------------------

    condition_keywords = [
        "good condition",
        "no damage",
        "undamaged",
        "condition verified",
        "condition inspection",
        "passed inspection",
        "product inspected",
    ]

    if any(
        keyword in text_lower
        for keyword in condition_keywords
    ):
        return "PRODUCT_CONDITION_CONFIRMATION"

    # ---------------------------------------------
    # Product damage evidence
    # ---------------------------------------------

    damage_keywords = [
        "damaged",
        "damage",
        "broken",
        "cracked",
        "defective",
        "physically damaged",
        "arrived damaged",
        "received damaged",
    ]

    if any(
        keyword in text_lower
        for keyword in damage_keywords
    ):
        return "DAMAGE_CLAIM"

    # ---------------------------------------------
    # Tracking / shipment evidence
    # Check BEFORE delivery confirmation.
    # ---------------------------------------------

    tracking_keywords = [
        "tracking id",
        "tracking number",
        "tracking code",
        "shipment tracking",
        "shipment status",
        "carrier",
        "in transit",
    ]

    if any(keyword in text_lower for keyword in tracking_keywords):
        return "DELIVERY_TRACKING"

    # ---------------------------------------------
    # Delivery confirmation
    # ---------------------------------------------

    delivery_keywords = [
        "delivery confirmation",
        "successfully delivered",
        "delivery completed",
        "received by",
        "delivered to the customer",
    ]

    if any(keyword in text_lower for keyword in delivery_keywords):
        return "DELIVERY_CONFIRMATION"

    # ---------------------------------------------
    # Purchase receipt
    # ---------------------------------------------

    purchase_keywords = [
        "amount paid",
        "total amount",
        "receipt",
        "invoice",
        "payment status",
    ]

    if any(keyword in text_lower for keyword in purchase_keywords):
        return "PURCHASE_RECEIPT"

    return "UNCLASSIFIED"