from __future__ import annotations

from datetime import date, timedelta
from statistics import mean


def forecast_daily_moving_average(history: list[float], forecast_start: date, forecast_days: int, window: int = 30) -> list[tuple[date, float]]:
    if not history:
        return []

    window_size = min(window, len(history))
    baseline = float(mean(history[-window_size:]))
    return [(forecast_start + timedelta(days=offset), baseline) for offset in range(forecast_days)]