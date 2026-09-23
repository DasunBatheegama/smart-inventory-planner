from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO

import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.tools.inventory_tools import (
    InventoryToolError,
    InventoryToolProductNotFoundError,
    generate_plan_for_product,
    generate_plans_for_all_products,
    get_inventory_health,
    get_inventory_plans,
    get_latest_plan_for_product,
    get_reorder_recommendations,
)
from app.db.database import SessionLocal
from app.db.database import get_db
from app.schemas.agent import InventoryAgentRequest


def product_payload(**overrides):
    payload = {
        "sku": "SKU-7001",
        "name": "Inventory Tool Widget",
        "category": "Electronics",
        "current_stock": 120,
        "unit_cost": 25,
        "lead_time": 7,
        "supplier": "Inventory Supplies",
        "reorder_point": 30,
        "safety_stock": 10,
    }
    payload.update(overrides)
    return payload


def create_product(client, sku="SKU-7001"):
    response = client.post("/api/v1/products", json=product_payload(sku=sku))
    assert response.status_code == 201
    return response.json()


def upload_sales_csv(client, sku: str, start_date: date, days: int, quantity: int = 10) -> None:
    rows = ["Date,SKU,Quantity Sold"]
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        rows.append(f"{current_date.isoformat()},{sku},{quantity}")
    response = client.post(
        "/api/v1/sales/upload",
        files={"file": ("sales.csv", BytesIO("\n".join(rows).encode("utf-8")), "text/csv")},
    )
    assert response.status_code == 200


def seed_plan(client, db, sku: str, days: int = 60, service_level: float = 0.95):
    product = create_product(client, sku=sku)
    upload_sales_csv(client, product["sku"], date(2026, 1, 1), days)
    response = client.post(
        "/api/v1/planning/generate",
        json={"product_id": product["id"], "service_level": service_level},
    )
    assert response.status_code == 200
    return product


def open_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def db():
    yield from open_session()


def test_generate_plan_for_product_returns_plan(client, db):
    product = seed_plan(client, sku="SKU-7101", db=db)
    plan = generate_plan_for_product(db, product["id"])
    assert plan is not None
    assert plan["product_id"] == product["id"]


def test_generate_plan_for_product_missing_product_raises(client, db):
    with pytest.raises(InventoryToolProductNotFoundError):
        generate_plan_for_product(db, "missing-product")


def test_generate_plans_for_all_products_returns_plans(client, db):
    product = seed_plan(client, sku="SKU-7102", db=db)
    plans = generate_plans_for_all_products(db)
    assert any(plan["product_id"] == product["id"] for plan in plans)


def test_get_inventory_health_returns_data(client, db):
    seed_plan(client, sku="SKU-7103", db=db)
    health = get_inventory_health(db)
    assert health is not None
    assert set(health) >= {"health_score", "healthy_count", "reorder_soon_count", "reorder_now_count", "critical_count"}
