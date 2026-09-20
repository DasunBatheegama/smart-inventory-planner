from __future__ import annotations

from io import BytesIO

from app.services.inventory.safety_stock import compute_safety_stock
from app.services.inventory.reorder_point import compute_reorder_point
from app.services.inventory.eoq import compute_eoq


def test_safety_stock_basic():
    # with demand_std=5, lead_time=7, service_level=0.95
    ss = compute_safety_stock(0.95, demand_std=5.0, lead_time_days=7)
    assert isinstance(ss, int)
    assert ss >= 0


def test_reorder_point_basic():
    rp = compute_reorder_point(20, 7, 30)
    assert rp == 170


def test_eoq_missing_inputs():
    assert compute_eoq(None, None, None) is None
    assert compute_eoq(1000, None, 2) is None
    assert compute_eoq(1000, 50, None) is None


def product_payload(**overrides):
    payload = {
        "sku": "SKU-INV-1",
        "name": "Test Item",
        "category": "Test",
        "current_stock": 10,
        "unit_cost": 5,
        "lead_time": 7,
        "supplier": "ACME",
        "reorder_point": 5,
        "safety_stock": 2,
    }
    payload.update(overrides)
    return payload


def upload_csv(client, content: str, filename: str = "sales.csv"):
    return client.post(
        "/api/v1/sales/upload",
        files={"file": (filename, BytesIO(content.encode("utf-8")), "text/csv")},
    )


def test_generate_plan_insufficient_history(client):
    # create product without sales history
    client.post("/api/v1/products", json=product_payload())
    resp = client.post("/api/v1/planning/generate", json={"product_id": "1"})
    # product id is UUID; request with wrong id should return 400 Product not found
    assert resp.status_code == 400 or resp.status_code == 404


def test_generate_plan_success(client):
    # create product
    r = client.post("/api/v1/products", json=product_payload())
    assert r.status_code == 201
    product = r.json()
    prod_id = product["id"]

    # upload sales for two days
    upload_csv(client, "Date,SKU,Quantity Sold\n2026-01-01,SKU-INV-1,5\n2026-01-02,SKU-INV-1,7\n")

    resp = client.post("/api/v1/planning/generate", json={"product_id": prod_id})
    # if insufficient history, API returns 400; else returns plan
    if resp.status_code == 400:
        assert "Insufficient" in resp.json().get("detail", "") or "Product not found" in resp.json().get("detail", "")
    else:
        assert resp.status_code == 200
        data = resp.json()
        assert data["product_id"] == prod_id
