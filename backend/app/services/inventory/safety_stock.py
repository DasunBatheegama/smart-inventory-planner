from math import sqrt

Z_TABLE = {
    0.9: 1.2815515655446004,
    0.95: 1.6448536269514722,
    0.98: 2.0537489106318226,
    0.99: 2.3263478740408408,
}


def lookup_z(service_level: float) -> float:
    if service_level in Z_TABLE:
        return Z_TABLE[service_level]
    # linear interpolation between nearest keys
    keys = sorted(Z_TABLE.keys())
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        if a < service_level < b:
            za, zb = Z_TABLE[a], Z_TABLE[b]
            t = (service_level - a) / (b - a)
            return za + (zb - za) * t
    # fallback to 95%
    return Z_TABLE[0.95]


def compute_safety_stock(service_level: float, demand_std: float, lead_time_days: int) -> int:
    """
    Safety Stock = Z * demand_std * sqrt(lead_time)

    demand_std: standard deviation of daily demand
    lead_time_days: integer days
    Returns rounded integer safety stock.
    """
    if demand_std is None:
        raise ValueError("Insufficient historical demand data to compute demand variability.")
    if lead_time_days is None or lead_time_days <= 0:
        raise ValueError("Invalid lead time for safety stock calculation.")

    z = lookup_z(service_level)
    ss = z * demand_std * sqrt(lead_time_days)
    return int(round(ss))
