from app.api.routes.health import router as health_router
from app.api.routes.forecast import router as forecast_router
from app.api.routes.products import router as products_router

__all__ = ["health_router", "forecast_router", "products_router"]