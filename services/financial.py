from decimal import Decimal
from typing import Dict, Any

def calculate_service_settlement(
    gross_amount: Decimal, 
    cmv_cost: Decimal, 
    salon_commission_rate: Decimal,
    commission_base_type: str = "GROSS"
) -> Dict[str, Decimal]:
    rate = salon_commission_rate / Decimal("100.00")
    if commission_base_type == "GROSS":
        salon_fee = gross_amount * rate
        net_amount = gross_amount - salon_fee - cmv_cost
    else:
        amount_after_cmv = max(Decimal("0.00"), gross_amount - cmv_cost)
        salon_fee = amount_after_cmv * rate
        net_amount = gross_amount - salon_fee - cmv_cost

    return {
        "gross_amount": round(gross_amount, 2),
        "cmv_cost": round(cmv_cost, 2),
        "salon_fee": round(salon_fee, 2),
        "net_amount": round(net_amount, 2)
    }

def calculate_prolabore_status(
    total_net_profit: Decimal,
    prolabore_target: Decimal,
    total_withdrawals: Decimal
) -> Dict[str, Any]:
    remaining_prolabore = max(Decimal("0.00"), prolabore_target - total_withdrawals)
    business_cash = total_net_profit - total_withdrawals
    percentage_withdrawn = Decimal("0.00")
    if prolabore_target > Decimal("0.00"):
        percentage_withdrawn = min(Decimal("100.00"), (total_withdrawals / prolabore_target) * Decimal("100.00"))

    return {
        "prolabore_target": round(prolabore_target, 2),
        "total_withdrawals": round(total_withdrawals, 2),
        "remaining_prolabore": round(remaining_prolabore, 2),
        "percentage_withdrawn": round(percentage_withdrawn, 1),
        "business_cash_available": round(business_cash, 2)
    }
