"""Financial formatting utilities ensuring consistent locale-aware currency and percentage formatting."""
from decimal import Decimal


def format_inr(amount: Decimal | float, show_sign: bool = False) -> str:
    """
    Formats a numeric value into standard Indian numbering system format (e.g. ₹10,84,230.45).
    """
    if amount is None:
        return "₹0.00"
    
    val = float(amount)
    sign = "+" if val > 0 and show_sign else ("-" if val < 0 else "")
    val = abs(val)
    
    parts = f"{val:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]
    
    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last3 = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last3
        
    return f"{sign}₹{formatted_int}.{decimal_part}"


def format_pct(pct: Decimal | float, show_sign: bool = True) -> str:
    """
    Formats percentage values (e.g. +2.34%, -1.82%).
    """
    if pct is None:
        return "0.00%"
    val = float(pct)
    sign = "+" if val > 0 and show_sign else ""
    return f"{sign}{val:.2f}%"
