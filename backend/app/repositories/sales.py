from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sales_record import SalesRecord
from app.models.sales_upload import SalesUpload


def get_sales_record_by_id(db: Session, sales_id: str) -> SalesRecord | None:
    return db.get(SalesRecord, sales_id)


def get_sales_by_id_with_product(db: Session, sales_id: str):
    return db.execute(
        select(SalesRecord, Product)
        .join(Product, Product.id == SalesRecord.product_id)
        .where(SalesRecord.id == sales_id)
    ).first()


def get_sales_records(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 20,
    sku: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[list[tuple[SalesRecord, Product]], int]:
    query = select(SalesRecord, Product).join(Product, Product.id == SalesRecord.product_id)
    count_query = select(func.count()).select_from(SalesRecord).join(Product, Product.id == SalesRecord.product_id)

    if sku:
        query = query.where(Product.sku == sku)
        count_query = count_query.where(Product.sku == sku)
    if start_date:
        query = query.where(SalesRecord.date >= start_date)
        count_query = count_query.where(SalesRecord.date >= start_date)
    if end_date:
        query = query.where(SalesRecord.date <= end_date)
        count_query = count_query.where(SalesRecord.date <= end_date)

    total = db.scalar(count_query) or 0
    rows = db.execute(query.order_by(SalesRecord.date.desc(), SalesRecord.created_at.desc()).offset(offset).limit(limit)).all()
    return rows, total


def create_sales_records(db: Session, records: list[SalesRecord]) -> list[SalesRecord]:
    db.add_all(records)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def create_sales_upload(db: Session, upload: SalesUpload) -> SalesUpload:
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


def update_sales_upload(db: Session, upload: SalesUpload) -> SalesUpload:
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


def get_upload_history(db: Session, *, offset: int = 0, limit: int = 20) -> tuple[list[SalesUpload], int]:
    query = select(SalesUpload).order_by(SalesUpload.created_at.desc())
    count_query = select(func.count()).select_from(SalesUpload)
    total = db.scalar(count_query) or 0
    items = db.scalars(query.offset(offset).limit(limit)).all()
    return items, total


def get_sales_summary(db: Session) -> dict[str, object]:
    total_sales_records = db.scalar(select(func.count()).select_from(SalesRecord)) or 0
    total_units_sold = db.scalar(select(func.coalesce(func.sum(SalesRecord.quantity_sold), 0))) or 0
    products_with_sales = db.scalar(select(func.count(func.distinct(SalesRecord.product_id)))) or 0
    first_sales_date = db.scalar(select(func.min(SalesRecord.date)))
    latest_sales_date = db.scalar(select(func.max(SalesRecord.date)))
    last_upload_date = db.scalar(select(func.max(SalesUpload.created_at)))

    return {
        "total_sales_records": int(total_sales_records),
        "total_units_sold": int(total_units_sold),
        "products_with_sales": int(products_with_sales),
        "first_sales_date": first_sales_date,
        "latest_sales_date": latest_sales_date,
        "last_upload_date": last_upload_date,
    }


def get_product_by_sku(db: Session, sku: str) -> Product | None:
    return db.scalar(select(Product).where(Product.sku == sku))