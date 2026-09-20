from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.db.database import SessionLocal
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.inventory_plan import InventoryPlan
from app.models.product import Product


def create_product(*, sku: str, name: str, category: str = "Electronics", supplier: str = "ACME", current_stock: int = 10) -> str:
    db = SessionLocal()
    try:
        product = Product(
            sku=sku,
            name=name,
            category=category,
            current_stock=current_stock,
            unit_cost=Decimal("10.00"),
            lead_time=7,
            supplier=supplier,
            reorder_point=20,
            safety_stock=5,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product.id
    finally:
        db.close()


def create_plan(
    *,
    product_id: str,
    current_stock: int,
    average_daily_demand: Decimal | None,
    forecast_demand: Decimal | None,
    reorder_point: int | None,
    recommended_order_quantity: int | None,
    days_of_inventory: Decimal | None,
    status: str = "healthy",
) -> str:
    db = SessionLocal()
    try:
        plan = InventoryPlan(
            product_id=product_id,
            current_stock=current_stock,
            average_daily_demand=average_daily_demand,
            forecast_demand=forecast_demand,
            safety_stock=5,
            reorder_point=reorder_point,
            eoq=Decimal("0"),
            recommended_order_quantity=recommended_order_quantity,
            days_of_inventory=days_of_inventory,
            status=status,
            created_at=datetime.now(timezone.utc),
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan.id
    finally:
        db.close()


def get_latest_alert_by_type(product_id: str, alert_type: AlertType):
    db = SessionLocal()
    try:
        return db.query(Alert).filter(Alert.product_id == product_id, Alert.type == alert_type).order_by(Alert.created_at.desc()).first()
    finally:
        db.close()


def test_critical_stock_alert(client):
    product_id = create_product(sku="SKU-CRIT", name="Critical Item", current_stock=0)
    create_plan(
        product_id=product_id,
        current_stock=0,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("30.0"),
        reorder_point=20,
        recommended_order_quantity=25,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["generated"] == 1

    alert = get_latest_alert_by_type(product_id, AlertType.stockout_risk)
    assert alert is not None
    assert alert.severity == AlertSeverity.critical


def test_reorder_required_alert(client):
    product_id = create_product(sku="SKU-REORDER", name="Reorder Item", current_stock=12)
    create_plan(
        product_id=product_id,
        current_stock=12,
        average_daily_demand=Decimal("3.0"),
        forecast_demand=Decimal("90.0"),
        reorder_point=20,
        recommended_order_quantity=18,
        days_of_inventory=Decimal("4.0"),
        status="reorder_now",
    )

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    alert = get_latest_alert_by_type(product_id, AlertType.reorder_required)
    assert alert is not None
    assert "below reorder point" in alert.message


def test_reorder_soon_alert(client):
    product_id = create_product(sku="SKU-SOON", name="Soon Item", current_stock=22)
    create_plan(
        product_id=product_id,
        current_stock=22,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("60.0"),
        reorder_point=20,
        recommended_order_quantity=12,
        days_of_inventory=Decimal("11.0"),
        status="reorder_soon",
    )

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    alert = get_latest_alert_by_type(product_id, AlertType.low_stock)
    assert alert is not None
    assert alert.severity == AlertSeverity.warning


def test_overstock_alert(client):
    product_id = create_product(sku="SKU-OVER", name="Overstock Item", current_stock=100)
    create_plan(
        product_id=product_id,
        current_stock=100,
        average_daily_demand=Decimal("1.0"),
        forecast_demand=Decimal("50.0"),
        reorder_point=20,
        recommended_order_quantity=0,
        days_of_inventory=Decimal("120.0"),
        status="healthy",
    )

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    alert = get_latest_alert_by_type(product_id, AlertType.overstock)
    assert alert is not None
    assert alert.severity == AlertSeverity.info


def test_slow_moving_alert(client):
    product_id = create_product(sku="SKU-SLOW", name="Slow Item", current_stock=60)
    create_plan(
        product_id=product_id,
        current_stock=60,
        average_daily_demand=Decimal("0.2"),
        forecast_demand=Decimal("20.0"),
        reorder_point=20,
        recommended_order_quantity=0,
        days_of_inventory=Decimal("300.0"),
        status="healthy",
    )

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    alert = get_latest_alert_by_type(product_id, AlertType.slow_moving)
    assert alert is not None


def test_duplicate_prevention(client):
    product_id = create_product(sku="SKU-DUP", name="Duplicate Item", current_stock=0)
    create_plan(
        product_id=product_id,
        current_stock=0,
        average_daily_demand=Decimal("1.0"),
        forecast_demand=Decimal("20.0"),
        reorder_point=20,
        recommended_order_quantity=20,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )

    first = client.post("/api/v1/alerts/generate")
    second = client.post("/api/v1/alerts/generate")
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["skipped_duplicates"] >= 1

    db = SessionLocal()
    try:
        count = db.query(Alert).filter(Alert.product_id == product_id, Alert.type == AlertType.stockout_risk).count()
        assert count == 1
    finally:
        db.close()


def test_alert_acknowledgement(client):
    product_id = create_product(sku="SKU-ACK", name="Ack Item", current_stock=0)
    create_plan(
        product_id=product_id,
        current_stock=0,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("30.0"),
        reorder_point=20,
        recommended_order_quantity=25,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )
    client.post("/api/v1/alerts/generate")
    alert = get_latest_alert_by_type(product_id, AlertType.stockout_risk)
    response = client.post(f"/api/v1/alerts/{alert.id}/acknowledge")
    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_alert_resolution(client):
    product_id = create_product(sku="SKU-RES", name="Resolve Item", current_stock=0)
    create_plan(
        product_id=product_id,
        current_stock=0,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("30.0"),
        reorder_point=20,
        recommended_order_quantity=25,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )
    client.post("/api/v1/alerts/generate")
    alert = get_latest_alert_by_type(product_id, AlertType.stockout_risk)
    response = client.post(f"/api/v1/alerts/{alert.id}/resolve")
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_alert_filtering(client):
    product_a = create_product(sku="SKU-FILT-A", name="Filter A", current_stock=0)
    product_b = create_product(sku="SKU-FILT-B", name="Filter B", current_stock=12)
    create_plan(
        product_id=product_a,
        current_stock=0,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("30.0"),
        reorder_point=20,
        recommended_order_quantity=25,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )
    create_plan(
        product_id=product_b,
        current_stock=12,
        average_daily_demand=Decimal("3.0"),
        forecast_demand=Decimal("90.0"),
        reorder_point=20,
        recommended_order_quantity=18,
        days_of_inventory=Decimal("4.0"),
        status="reorder_now",
    )
    client.post("/api/v1/alerts/generate")

    response = client.get("/api/v1/alerts", params={"product_id": product_a, "type": "stockout_risk"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["product_id"] == product_a


def test_alert_summary(client):
    product_id = create_product(sku="SKU-SUM", name="Summary Item", current_stock=0)
    create_plan(
        product_id=product_id,
        current_stock=0,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("30.0"),
        reorder_point=20,
        recommended_order_quantity=25,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )
    client.post("/api/v1/alerts/generate")
    response = client.get("/api/v1/alerts/summary")
    assert response.status_code == 200
    assert response.json()["total_active"] >= 1
    assert response.json()["stockout_risk"] >= 1


def test_invalid_alert_status(client):
    product_id = create_product(sku="SKU-INV-STATUS", name="Status Item", current_stock=0)
    create_plan(
        product_id=product_id,
        current_stock=0,
        average_daily_demand=Decimal("2.0"),
        forecast_demand=Decimal("30.0"),
        reorder_point=20,
        recommended_order_quantity=25,
        days_of_inventory=Decimal("0.0"),
        status="critical",
    )
    client.post("/api/v1/alerts/generate")
    alert = get_latest_alert_by_type(product_id, AlertType.stockout_risk)
    response = client.patch(f"/api/v1/alerts/{alert.id}", json={"status": "bad_status"})
    assert response.status_code == 422


def test_product_with_insufficient_data(client):
    product_id = create_product(sku="SKU-INSUFF", name="Insufficient Item", current_stock=40)
    create_plan(
        product_id=product_id,
        current_stock=40,
        average_daily_demand=None,
        forecast_demand=Decimal("20.0"),
        reorder_point=20,
        recommended_order_quantity=0,
        days_of_inventory=None,
        status="healthy",
    )

    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200
    db = SessionLocal()
    try:
        alerts = db.query(Alert).filter(Alert.product_id == product_id).all()
        assert alerts == []
    finally:
        db.close()