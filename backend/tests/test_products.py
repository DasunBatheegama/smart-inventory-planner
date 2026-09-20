from __future__ import annotations


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


def test_create_product(client):
    response = client.post("/api/v1/products", json=product_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-1001"
    assert data["status"] == "in-stock"
    assert data["inventory_value"] == 1800.0


def test_get_product(client):
    created = client.post("/api/v1/products", json=product_payload()).json()
    response = client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-1001"


def test_list_products(client):
    seed_products(client)
    response = client.get("/api/v1/products?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2


def test_search_products(client):
    seed_products(client)
    response = client.get("/api/v1/products?search=mouse")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Wireless Mouse"


def test_update_product(client):
    created = client.post("/api/v1/products", json=product_payload()).json()
    response = client.put(
        f"/api/v1/products/{created['id']}",
        json={"current_stock": 10, "reorder_point": 20},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_stock"] == 10
    assert data["status"] == "low-stock"


def test_delete_product(client):
    created = client.post("/api/v1/products", json=product_payload()).json()
    response = client.delete(f"/api/v1/products/{created['id']}")
    assert response.status_code == 204
    missing = client.get(f"/api/v1/products/{created['id']}")
    assert missing.status_code == 404


def test_duplicate_sku(client):
    first = client.post("/api/v1/products", json=product_payload())
    assert first.status_code == 201
    duplicate = client.post("/api/v1/products", json=product_payload())
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Product with SKU 'SKU-1001' already exists."


def test_invalid_negative_stock(client):
    response = client.post("/api/v1/products", json=product_payload(current_stock=-1))
    assert response.status_code == 422


def test_invalid_negative_cost(client):
    response = client.post("/api/v1/products", json=product_payload(unit_cost=-1))
    assert response.status_code == 422


def test_product_not_found(client):
    response = client.get("/api/v1/products/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_product_statistics(client):
    seed_products(client)
    response = client.get("/api/v1/products/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_products"] == 3
    assert data["low_stock_products"] == 1
    assert data["out_of_stock_products"] == 1
    assert data["total_inventory_value"] == 2775.0