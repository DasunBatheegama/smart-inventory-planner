from __future__ import annotations

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_products(
    db: Session,
    *,
    filters: list | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Product], int]:
    query = select(Product)
    count_query = select(func.count()).select_from(Product)

    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)

    total = db.scalar(count_query) or 0
    items = db.scalars(query.order_by(Product.created_at.desc()).offset(offset).limit(limit)).all()
    return items, total


def get_product_by_id(db: Session, product_id: str) -> Product | None:
    return db.get(Product, product_id)


def get_product_by_sku(db: Session, sku: str) -> Product | None:
    return db.scalar(select(Product).where(Product.sku == sku))


def create_product(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def get_product_stats(db: Session) -> dict[str, float | int]:
    total_products = db.scalar(select(func.count()).select_from(Product)) or 0
    total_inventory_value = db.scalar(
        select(func.coalesce(func.sum(Product.current_stock * Product.unit_cost), 0))
    ) or 0
    low_stock_products = db.scalar(
        select(
            func.count().filter(
                and_(Product.current_stock > 0, Product.current_stock <= Product.reorder_point)
            )
        )
    ) or 0
    out_of_stock_products = db.scalar(select(func.count().filter(Product.current_stock <= 0))) or 0
    average_stock_level = db.scalar(select(func.coalesce(func.avg(Product.current_stock), 0))) or 0

    return {
        "total_products": int(total_products),
        "total_inventory_value": float(total_inventory_value),
        "low_stock_products": int(low_stock_products),
        "out_of_stock_products": int(out_of_stock_products),
        "average_stock_level": float(average_stock_level),
    }