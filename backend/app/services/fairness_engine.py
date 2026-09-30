from typing import List, Dict


def calculate_evidence_score(
    evidence: List[Dict],
    dispute_reason: str,
) -> Dict:
    """
    Calculate explainable evidence scores and compare
    important facts between customer and merchant evidence.
    """

    customer_score = 0
    merchant_score = 0

    customer_reasons = []
    merchant_reasons = []

    customer_types = set()
    merchant_types = set()

    customer_facts = set()
    merchant_facts = set()

    customer_fact_values = {}
    merchant_fact_values = {}

    # ==================================================
    # PROCESS EVIDENCE
    # ==================================================

    for item in evidence:

        submitted_by = item.get("submitted_by", "").upper()
        evidence_type = item.get("evidence_type", "").upper()
        facts = item.get("extracted_facts") or {}

        # ----------------------------------------------
        # CUSTOMER EVIDENCE
        # ----------------------------------------------

        if submitted_by == "CUSTOMER":

            if (
                evidence_type == "PURCHASE_RECEIPT"
                and evidence_type not in customer_types
            ):
                customer_score += 20
                customer_types.add(evidence_type)

                customer_reasons.append(
                    "Customer provided a purchase receipt."
                )

            if (
                evidence_type == "REFUND_CONFIRMATION"
                and evidence_type not in customer_types
            ):
                customer_score += 40
                customer_types.add(evidence_type)

                customer_reasons.append(
                    "Customer provided evidence of a refund."
                )

            if (
                evidence_type == "WRONG_PRODUCT_EVIDENCE"
                and evidence_type not in customer_types
            ):
                customer_score += 35
                customer_types.add(evidence_type)

                customer_reasons.append(
                    "Customer provided evidence that the received product "
                    "did not match the expected product."
                )

            if (
                evidence_type == "DAMAGE_CLAIM"
                and evidence_type not in customer_types
            ):
                customer_score += 35
                customer_types.add(evidence_type)

                customer_reasons.append(
                    "Customer provided evidence of product damage."
                )

            if (
                evidence_type == "DUPLICATE_CHARGE_EVIDENCE"
                and evidence_type not in customer_types
            ):
                customer_score += 40
                customer_types.add(evidence_type)

                customer_reasons.append(
                    "Customer provided evidence of a duplicate charge."
                )

            if (
                facts.get("order_id")
                and "order_id" not in customer_facts
            ):
                customer_score += 10
                customer_facts.add("order_id")
                customer_fact_values["order_id"] = facts["order_id"]

                customer_reasons.append(
                    "Customer evidence contains an order ID."
                )

            if (
                facts.get("amount") is not None
                and "amount" not in customer_facts
            ):
                customer_score += 10
                customer_facts.add("amount")
                customer_fact_values["amount"] = facts["amount"]

                customer_reasons.append(
                    "Customer evidence contains a transaction amount."
                )

            if facts.get("date") and "date" not in customer_facts:
                customer_fact_values["date"] = facts["date"]

            if facts.get("ordered_product"):
                customer_fact_values["ordered_product"] = (
                    facts["ordered_product"]
                )

            if facts.get("received_product"):
                customer_fact_values["received_product"] = (
                    facts["received_product"]
                )

            if facts.get("damage_status"):
                customer_fact_values["damage_status"] = (
                    facts["damage_status"]
                )

            if facts.get("charge_count") is not None:
                customer_fact_values["charge_count"] = (
                    facts["charge_count"]
                )

        # ----------------------------------------------
        # MERCHANT EVIDENCE
        # ----------------------------------------------

        if submitted_by == "MERCHANT":

            if (
                evidence_type == "DELIVERY_CONFIRMATION"
                and evidence_type not in merchant_types
            ):
                merchant_score += 40
                merchant_types.add(evidence_type)

                merchant_reasons.append(
                    "Merchant provided delivery confirmation."
                )

            if (
                evidence_type == "DELIVERY_TRACKING"
                and evidence_type not in merchant_types
            ):
                merchant_score += 30
                merchant_types.add(evidence_type)

                merchant_reasons.append(
                    "Merchant provided shipment tracking evidence."
                )

            if (
                evidence_type == "ORDER_ITEM_CONFIRMATION"
                and evidence_type not in merchant_types
            ):
                merchant_score += 40
                merchant_types.add(evidence_type)

                merchant_reasons.append(
                    "Merchant provided evidence of the fulfilled product."
                )

            if (
                evidence_type == "PRODUCT_CONDITION_CONFIRMATION"
                and evidence_type not in merchant_types
            ):
                merchant_score += 40
                merchant_types.add(evidence_type)

                merchant_reasons.append(
                    "Merchant provided evidence about the product condition."
                )

            if (
                evidence_type == "CHARGE_LEDGER_CONFIRMATION"
                and evidence_type not in merchant_types
            ):
                merchant_score += 40
                merchant_types.add(evidence_type)

                merchant_reasons.append(
                    "Merchant provided transaction-charge records."
                )

            if (
                facts.get("delivery_status") == "DELIVERED"
                and "delivery_status" not in merchant_facts
            ):
                merchant_score += 20
                merchant_facts.add("delivery_status")
                merchant_fact_values["delivery_status"] = (
                    facts["delivery_status"]
                )

                merchant_reasons.append(
                    "Evidence confirms the order was delivered."
                )

            if (
                facts.get("tracking_id")
                and "tracking_id" not in merchant_facts
            ):
                merchant_score += 10
                merchant_facts.add("tracking_id")
                merchant_fact_values["tracking_id"] = (
                    facts["tracking_id"]
                )

                merchant_reasons.append(
                    "Merchant evidence contains a tracking ID."
                )

            if facts.get("order_id"):
                merchant_fact_values["order_id"] = facts["order_id"]

            if facts.get("date"):
                merchant_fact_values["date"] = facts["date"]

            if facts.get("ordered_product"):
                merchant_fact_values["ordered_product"] = (
                    facts["ordered_product"]
                )

            if facts.get("received_product"):
                merchant_fact_values["received_product"] = (
                    facts["received_product"]
                )

            if facts.get("damage_status"):
                merchant_fact_values["damage_status"] = (
                    facts["damage_status"]
                )

            if facts.get("charge_count") is not None:
                merchant_fact_values["charge_count"] = (
                    facts["charge_count"]
                )

    # ==================================================
    # LIMIT SCORES
    # ==================================================

    customer_score = min(customer_score, 100)
    merchant_score = min(merchant_score, 100)

    # ==================================================
    # FACT COMPARISON
    # ==================================================

    fact_comparison = {}

    customer_order_id = customer_fact_values.get("order_id")
    merchant_order_id = merchant_fact_values.get("order_id")

    if customer_order_id or merchant_order_id:
        fact_comparison["order_id"] = {
            "customer": customer_order_id,
            "merchant": merchant_order_id,
            "match": (
                customer_order_id is not None
                and merchant_order_id is not None
                and customer_order_id == merchant_order_id
            ),
        }

    customer_date = customer_fact_values.get("date")
    merchant_date = merchant_fact_values.get("date")

    if customer_date or merchant_date:
        fact_comparison["date"] = {
            "customer": customer_date,
            "merchant": merchant_date,
            "match": (
                customer_date is not None
                and merchant_date is not None
                and customer_date == merchant_date
            ),
        }

    customer_amount = customer_fact_values.get("amount")

    if customer_amount is not None:
        fact_comparison["amount"] = {
            "customer": customer_amount,
        }

    merchant_delivery_status = merchant_fact_values.get(
        "delivery_status"
    )

    if merchant_delivery_status:
        fact_comparison["delivery_status"] = {
            "merchant": merchant_delivery_status,
        }

    merchant_tracking_id = merchant_fact_values.get("tracking_id")

    if merchant_tracking_id:
        fact_comparison["tracking_id"] = {
            "merchant": merchant_tracking_id,
        }

    customer_ordered_product = customer_fact_values.get(
        "ordered_product"
    )
    merchant_ordered_product = merchant_fact_values.get(
        "ordered_product"
    )

    customer_received_product = customer_fact_values.get(
        "received_product"
    )
    merchant_received_product = merchant_fact_values.get(
        "received_product"
    )

    if (
        customer_ordered_product
        or merchant_ordered_product
        or customer_received_product
        or merchant_received_product
    ):
        fact_comparison["product"] = {
            "customer_ordered": customer_ordered_product,
            "merchant_ordered": merchant_ordered_product,
            "customer_received": customer_received_product,
            "merchant_received": merchant_received_product,
        }

    customer_damage_status = customer_fact_values.get(
        "damage_status"
    )
    merchant_damage_status = merchant_fact_values.get(
        "damage_status"
    )

    if customer_damage_status or merchant_damage_status:
        fact_comparison["damage_status"] = {
            "customer": customer_damage_status,
            "merchant": merchant_damage_status,
        }

    customer_charge_count = customer_fact_values.get(
        "charge_count"
    )
    merchant_charge_count = merchant_fact_values.get(
        "charge_count"
    )

    if (
        customer_charge_count is not None
        or merchant_charge_count is not None
    ):
        fact_comparison["charge_count"] = {
            "customer": customer_charge_count,
            "merchant": merchant_charge_count,
        }

    # ==================================================
    # CONTRADICTION DETECTION
    # ==================================================

    contradictions = []

    reason = dispute_reason.upper()

    # --------------------------------------------------
    # Merchant delivery conflict
    # --------------------------------------------------

    merchant_delivery_statuses = set()

    for item in evidence:

        if item.get("submitted_by", "").upper() != "MERCHANT":
            continue

        facts = item.get("extracted_facts") or {}
        delivery_status = facts.get("delivery_status")

        if delivery_status:
            merchant_delivery_statuses.add(
                delivery_status.upper()
            )

    if len(merchant_delivery_statuses) > 1:
        contradictions.append(
            {
                "type": "MERCHANT_DELIVERY_STATUS_CONFLICT",
                "severity": "HIGH",
                "message": (
                    "Merchant evidence contains conflicting delivery "
                    "statuses."
                ),
            }
        )

    # --------------------------------------------------
    # Product not received
    # --------------------------------------------------

    if (
        reason == "PRODUCT_NOT_RECEIVED"
        and merchant_delivery_status == "DELIVERED"
    ):
        contradictions.append(
            {
                "type": "PRODUCT_NOT_RECEIVED_VS_DELIVERED",
                "severity": "HIGH",
                "message": (
                    "The customer claims the product was not received, "
                    "while merchant evidence indicates that the order "
                    "was delivered."
                ),
            }
        )

    # --------------------------------------------------
    # Wrong product
    # --------------------------------------------------

    if (
        reason == "WRONG_PRODUCT"
        and customer_received_product
        and merchant_ordered_product
        and customer_received_product.lower()
        != merchant_ordered_product.lower()
    ):
        contradictions.append(
            {
                "type": "WRONG_PRODUCT_MISMATCH",
                "severity": "HIGH",
                "message": (
                    "Customer evidence identifies a received product "
                    "that differs from the product shown in merchant "
                    "fulfillment evidence."
                ),
            }
        )

    # --------------------------------------------------
    # Product damaged
    # --------------------------------------------------

    if (
        reason == "PRODUCT_DAMAGED"
        and customer_damage_status == "DAMAGED"
        and merchant_damage_status == "NOT_DAMAGED"
    ):
        contradictions.append(
            {
                "type": "DAMAGE_STATUS_CONFLICT",
                "severity": "HIGH",
                "message": (
                    "Customer evidence reports product damage while "
                    "merchant evidence reports the product as undamaged."
                ),
            }
        )

    # --------------------------------------------------
    # Duplicate charge
    # --------------------------------------------------

    if (
        reason == "DUPLICATE_CHARGE"
        and customer_charge_count is not None
        and merchant_charge_count is not None
        and customer_charge_count != merchant_charge_count
    ):
        contradictions.append(
            {
                "type": "CHARGE_COUNT_MISMATCH",
                "severity": "HIGH",
                "message": (
                    "Customer and merchant evidence report different "
                    "numbers of charges for the transaction."
                ),
            }
        )

    # Order ID mismatch
    if (
        customer_order_id
        and merchant_order_id
        and customer_order_id != merchant_order_id
    ):
        contradictions.append(
            {
                "type": "ORDER_ID_MISMATCH",
                "severity": "HIGH",
                "message": (
                    "Customer and merchant evidence refer to different "
                    "order IDs."
                ),
            }
        )

    # Date mismatch
    if (
        customer_date
        and merchant_date
        and customer_date != merchant_date
    ):
        contradictions.append(
            {
                "type": "DATE_MISMATCH",
                "severity": "MEDIUM",
                "message": (
                    "Customer and merchant evidence contain different dates."
                ),
            }
        )

    # ==================================================
    # DISPUTE-SPECIFIC EVIDENCE STRENGTH
    # ==================================================

    customer_direct_evidence = 0
    merchant_direct_evidence = 0

    if reason == "PRODUCT_NOT_RECEIVED":

        if merchant_delivery_status == "DELIVERED":
            merchant_direct_evidence += 40

        if "DELIVERY_CONFIRMATION" in merchant_types:
            merchant_direct_evidence += 30

        if "DELIVERY_TRACKING" in merchant_types:
            merchant_direct_evidence += 20

        if "PURCHASE_RECEIPT" in customer_types:
            customer_direct_evidence += 10

    elif reason == "WRONG_PRODUCT":

        if "WRONG_PRODUCT_EVIDENCE" in customer_types:
            customer_direct_evidence += 40

        if "ORDER_ITEM_CONFIRMATION" in merchant_types:
            merchant_direct_evidence += 40

        if (
            customer_received_product
            and merchant_ordered_product
            and customer_received_product.lower()
            != merchant_ordered_product.lower()
        ):
            customer_direct_evidence += 30

    elif reason == "PRODUCT_DAMAGED":

        if "DAMAGE_CLAIM" in customer_types:
            customer_direct_evidence += 40

        if "PRODUCT_CONDITION_CONFIRMATION" in merchant_types:
            merchant_direct_evidence += 40

        if customer_damage_status == "DAMAGED":
            customer_direct_evidence += 20

        if merchant_damage_status == "NOT_DAMAGED":
            merchant_direct_evidence += 20

    elif reason == "DUPLICATE_CHARGE":

        if "DUPLICATE_CHARGE_EVIDENCE" in customer_types:
            customer_direct_evidence += 40

        if "CHARGE_LEDGER_CONFIRMATION" in merchant_types:
            merchant_direct_evidence += 40

        if (
            customer_charge_count is not None
            and customer_charge_count > 1
        ):
            customer_direct_evidence += 30

        if (
            merchant_charge_count is not None
            and merchant_charge_count == 1
        ):
            merchant_direct_evidence += 30

    # ==================================================
    # CHECK BOTH SIDES OF EVIDENCE
    # ==================================================

    has_customer_evidence = any(
        item.get("submitted_by", "").upper() == "CUSTOMER"
        for item in evidence
    )

    has_merchant_evidence = any(
        item.get("submitted_by", "").upper() == "MERCHANT"
        for item in evidence
    )

    # ==================================================
    # DETERMINE OUTCOME
    # ==================================================

    difference = abs(customer_score - merchant_score)

    if not has_customer_evidence or not has_merchant_evidence:
        decision = "NEEDS_REVIEW"
        confidence = 0

    elif customer_score == 0 and merchant_score == 0:
        decision = "NEEDS_REVIEW"
        confidence = 0

    elif contradictions:

        has_high_delivery_conflict = any(
            contradiction["severity"] == "HIGH"
            and contradiction["type"]
            == "MERCHANT_DELIVERY_STATUS_CONFLICT"
            for contradiction in contradictions
        )

        if has_high_delivery_conflict:
            decision = "NEEDS_REVIEW"
            confidence = 50

        elif reason == "PRODUCT_NOT_RECEIVED":

            if merchant_direct_evidence >= 60:
                decision = "MERCHANT_FAVOR"
                confidence = min(
                    100,
                    merchant_score
                    + merchant_direct_evidence // 2,
                )

            else:
                decision = "NEEDS_REVIEW"
                confidence = 50

        elif reason == "WRONG_PRODUCT":

            if (
                "WRONG_PRODUCT_MISMATCH"
                in [
                    contradiction["type"]
                    for contradiction in contradictions
                ]
            ):
                decision = "CUSTOMER_FAVOR"
                confidence = min(
                    100,
                    max(
                        customer_score,
                        customer_direct_evidence,
                    ),
                )

            else:
                decision = "NEEDS_REVIEW"
                confidence = 50

        elif reason == "PRODUCT_DAMAGED":

            decision = "NEEDS_REVIEW"
            confidence = 50

        elif reason == "DUPLICATE_CHARGE":

            decision = "NEEDS_REVIEW"
            confidence = 50

        elif difference < 15:

            decision = "NEEDS_REVIEW"
            confidence = 50

        elif customer_score > merchant_score:

            decision = "CUSTOMER_FAVOR"
            confidence = customer_score

        else:

            decision = "MERCHANT_FAVOR"
            confidence = merchant_score

    elif difference < 15:

        decision = "NEEDS_REVIEW"
        confidence = 50

    elif customer_score > merchant_score:

        decision = "CUSTOMER_FAVOR"
        confidence = customer_score

    else:

        decision = "MERCHANT_FAVOR"
        confidence = merchant_score

    return {
        "customer_score": customer_score,
        "merchant_score": merchant_score,
        "customer_direct_evidence": customer_direct_evidence,
        "merchant_direct_evidence": merchant_direct_evidence,
        "decision": decision,
        "confidence": confidence,
        "customer_reasons": customer_reasons,
        "merchant_reasons": merchant_reasons,
        "fact_comparison": fact_comparison,
        "contradictions": contradictions,
    }