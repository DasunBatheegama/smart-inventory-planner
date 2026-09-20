from math import sqrt


def compute_eoq(annual_demand: float | None, ordering_cost: float | None, holding_cost_per_unit: float | None) -> float | None:
    """
    EOQ = sqrt((2 * Annual Demand * Ordering Cost) / Holding Cost per Unit)
    If ordering_cost or holding_cost_per_unit is missing or zero, return None.
    """
    if annual_demand is None or annual_demand <= 0:
        return None
    if ordering_cost is None or holding_cost_per_unit is None:
        return None
    if holding_cost_per_unit == 0 or ordering_cost == 0:
        return None

    eoq = sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
    return float(eoq)
