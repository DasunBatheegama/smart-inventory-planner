from __future__ import annotations

from datetime import date, timedelta

try:
    from statsmodels.tsa.holtwinters import SimpleExpSmoothing
except Exception:  # pragma: no cover - import compatibility fallback
    SimpleExpSmoothing = None


def _fallback_simple_exponential_smoothing(history: list[float], forecast_days: int) -> list[float]:
    alpha = 0.4
    level = float(history[0])
    for value in history[1:]:
        level = alpha * float(value) + (1 - alpha) * level
    return [level for _ in range(forecast_days)]


def forecast_daily_exponential_smoothing(history: list[float], forecast_start: date, forecast_days: int) -> list[tuple[date, float]]:
    if not history:
        return []

    if SimpleExpSmoothing is None:
        predictions = _fallback_simple_exponential_smoothing(history, forecast_days)
    else:
        model = SimpleExpSmoothing(history, initialization_method="estimated")
        fitted = model.fit(optimized=True)
        predictions = [float(value) for value in fitted.forecast(forecast_days)]

    return [(forecast_start + timedelta(days=offset), float(predictions[offset])) for offset in range(forecast_days)]