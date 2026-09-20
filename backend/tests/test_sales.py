from __future__ import annotations

from io import BytesIO


def product_payload(**overrides):
    payload = {
        "sku": "SKU-1001",
        "name": "Wireless Mouse",
        "category": "Electronics",
        "current_stock": 120,
        "unit_cost": 15,
        "lead_time": 7,
        "supplier": "ABC Supplies",
        "reorder_point": 50,
        "safety_stock": 20,
    }
    payload.update(overrides)
    return payload


def seed_products(client):
    client.post("/api/v1/products", json=product_payload())
    client.post(
        "/api/v1/products",
        json=product_payload(
            sku="SKU-1002",
            name="Mechanical Keyboard",
            current_stock=15,
            unit_cost=65,
            reorder_point=20,
            safety_stock=10,
        ),
    )
    client.post(
        "/api/v1/products",
        json=product_payload(
            sku="SKU-1003",
            name="Office Chair",
            category="Furniture",
            current_stock=0,
            unit_cost=120,
            lead_time=21,
            supplier="FurniCo",
            reorder_point=10,
            safety_stock=5,
        ),
    )


def upload_csv(client, content: str, filename: str = "sales.csv", content_type: str = "text/csv"):
    return client.post(
        "/api/v1/sales/upload",
        files={"file": (filename, BytesIO(content.encode("utf-8")), content_type)},
    )


def test_valid_sales_upload(client):
    seed_products(client)
    response = upload_csv(
        client,
        "Date,SKU,Quantity Sold\n2026-01-01,SKU-1001,25\n2026-01-02,SKU-1001,18\n2026-01-02,SKU-1002,12\n",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["valid_rows"] == 3
    assert data["invalid_rows"] == 0
    assert data["imported_rows"] == 3
    assert data["status"] == "completed"


def test_invalid_file_type(client):
    seed_products(client)
    response = client.post(
        "/api/v1/sales/upload",
        files={"file": ("sales.txt", BytesIO(b"not,csv"), "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only CSV files are supported."


def test_missing_columns(client):
    seed_products(client)
    response = upload_csv(client, "Date,SKU\n2026-01-01,SKU-1001\n")
    assert response.status_code == 400
    assert response.json()["detail"] == "Required columns are missing: Quantity Sold."


def test_invalid_date_quantity_and_unknown_sku_are_reported(client):
    seed_products(client)
    response = upload_csv(
        client,
        "Date,SKU,Quantity Sold\n2026-13-01,SKU-1001,25\n2026-01-02,SKU-1001,abc\n2026-01-03,SKU-9999,10\n",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["valid_rows"] == 0
    assert data["invalid_rows"] == 3
    assert data["imported_rows"] == 0
    assert data["status"] == "failed"
    assert any("Date is invalid" in error["error"] for error in data["errors"])
    assert any("Quantity Sold must be numeric" in error["error"] for error in data["errors"])
    assert any("was not found" in error["error"] for error in data["errors"])


def test_negative_quantity(client):
    seed_products(client)
    response = upload_csv(client, "Date,SKU,Quantity Sold\n2026-01-01,SKU-1001,-1\n")
    assert response.status_code == 200
    data = response.json()
    assert data["invalid_rows"] == 1
    assert data["valid_rows"] == 0
    assert "cannot be negative" in data["errors"][0]["error"]


def test_empty_csv(client):
    seed_products(client)
    response = upload_csv(client, "")
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 0
    assert data["imported_rows"] == 0
    assert data["status"] == "failed"


def test_sales_records_retrieval_and_filtering(client):
    seed_products(client)
    upload_csv(
        client,
        "Date,SKU,Quantity Sold\n2026-01-01,SKU-1001,25\n2026-01-02,SKU-1001,18\n2026-01-03,SKU-1002,12\n",
    )

    response = client.get("/api/v1/sales?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2

    sku_response = client.get("/api/v1/sales?sku=SKU-1002")
    assert sku_response.status_code == 200
    sku_data = sku_response.json()
    assert sku_data["total"] == 1
    assert sku_data["items"][0]["sku"] == "SKU-1002"

    date_response = client.get("/api/v1/sales?start_date=2026-01-02&end_date=2026-01-03")
    assert date_response.status_code == 200
    assert date_response.json()["total"] == 2


def test_sales_record_by_id(client):
    seed_products(client)
    upload_csv(client, "Date,SKU,Quantity Sold\n2026-01-01,SKU-1001,25\n")
    list_response = client.get("/api/v1/sales")
    sales_id = list_response.json()["items"][0]["id"]

    response = client.get(f"/api/v1/sales/{sales_id}")
    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-1001"


def test_sales_summary(client):
    seed_products(client)
    upload_csv(client, "Date,SKU,Quantity Sold\n2026-01-01,SKU-1001,25\n2026-01-03,SKU-1002,12\n")

    response = client.get("/api/v1/sales/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sales_records"] == 2
    assert data["total_units_sold"] == 37
    assert data["products_with_sales"] == 2
    assert data["first_sales_date"] == "2026-01-01"
    assert data["latest_sales_date"] == "2026-01-03"
    assert data["last_upload_date"] is not None


def test_upload_history(client):
    seed_products(client)
    upload_csv(client, "Date,SKU,Quantity Sold\n2026-01-01,SKU-1001,25\n")
    upload_csv(client, "Date,SKU,Quantity Sold\n2026-01-02,SKU-1002,12\n")

    response = client.get("/api/v1/sales/uploads")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["file_name"] == "sales.csv"
