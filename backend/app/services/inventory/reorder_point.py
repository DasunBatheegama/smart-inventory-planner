def compute_reorder_point(avg_daily_demand: float, lead_time_days: int, safety_stock: int) -> int:
    if avg_daily_demand is None:
        raise ValueError("Average daily demand is required to compute lead time demand.")
    if lead_time_days is None or lead_time_days < 0:
        raise ValueError("Invalid lead time for reorder point calculation.")

    lead_time_demand = avg_daily_demand * lead_time_days
    rp = lead_time_demand + (safety_stock or 0)
    return int(round(rp))
