from decimal import Decimal
from typing import Optional

from app.services.inventory.eoq import compute_eoq
from app.services.inventory.reorder_point import compute_reorder_point
from app.services.inventory.safety_stock import compute_safety_stock


def plan_inventory(
    *,
    current_stock: int,
    avg_daily_demand: Optional[float],
    forecast_demand: Optional[float],
    lead_time: int,
    service_level: float,
    ordering_cost: Optional[float] = None,
    holding_cost_per_unit: Optional[float] = None,
    review_period: int = 30,
    reorder_soon_pct: float = 0.2,
):
    # Validate avg_daily_demand
    if avg_daily_demand is None:
        raise ValueError("Insufficient historical demand to compute average daily demand.")

    # compute demand stddev should be provided upstream; planner expects avg and demand_std
    # caller should provide demand_std; but compute_safety_stock requires demand_std; for now,
    # assume caller computed and passed as avg_daily_demand_std via forecast_demand param if needed
    # For clarity here, we treat forecast_demand as not used for safety stock.

    # For safety, set demand_std approximate from avg_daily_demand if forecast_demand provided? No.
    # This planner expects a separate path for demand_std; keep interface minimal here.

    # Safety stock and reorder point are computed elsewhere with explicit demand_std; raise if missing
    raise NotImplementedError("Use service.generate_inventory_plan() which calls calculation modules with demand stats.")
