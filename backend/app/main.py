from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.forecast import router as forecast_router
from app.api.routes.products import router as products_router
from app.api.routes.sales import router as sales_router

app = FastAPI(
    title="InventIQ API",
    description="AI Inventory Planner for SMEs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    products_router,
    prefix="/api/v1",
)

app.include_router(
    forecast_router,
    prefix="/api/v1",
)

app.include_router(
    sales_router,
    prefix="/api/v1",
)