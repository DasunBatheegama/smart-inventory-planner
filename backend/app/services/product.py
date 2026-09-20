from __future__ import annotations

from decimal import Decimal
from math import ceil

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories import product as product_repository
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductStatsResponse,
    ProductUpdate,
)


class ProductNotFoundError(Exception):
    pass


class ProductConflictError(Exception):
    pass


def _calculate_status(current_stock: int, reorder_point: int) -> str:
    if current_stock <= 0:
        return "out-of-stock"
    if current_stock <= reorder_point:
        return "low-stock"
    return "in-stock"


def _to_response(product: Product) -> ProductResponse:
    status = _calculate_status(product.current_stock, product.reorder_point)
    inventory_value = float(Decimal(str(product.current_stock)) * Decimal(str(product.unit_cost)))
    return ProductResponse.model_validate(
        {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "current_stock": product.current_stock,
            "unit_cost": float(product.unit_cost),
            "lead_time": product.lead_time,
            "supplier": product.supplier,
            "reorder_point": product.reorder_point,
            "safety_stock": product.safety_stock,
            "status": status,
            "inventory_value": inventory_value,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }
    )


def _build_filters(*, search: str | None = None, category: str | None = None, status: str | None = None) -> list:
    filters: list = []

    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Product.sku.ilike(term), Product.name.ilike(term)))

    if category:
        filters.append(Product.category == category)

    if status == "out-of-stock":
        filters.append(Product.current_stock <= 0)
    elif status == "low-stock":
        filters.append(and_(Product.current_stock > 0, Product.current_stock <= Product.reorder_point))
    elif status == "in-stock":
        filters.append(Product.current_stock > Product.reorder_point)

    return filters


def list_products(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> ProductListResponse:
    filters = _build_filters(search=search, category=category, status=status)
    offset = (page - 1) * page_size
    products, total = product_repository.get_products(db, filters=filters, offset=offset, limit=page_size)
    total_pages = ceil(total / page_size) if total else 0
    return ProductListResponse(
        items=[_to_response(product) for product in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_product(db: Session, product_id: str) -> ProductResponse:
    product = product_repository.get_product_by_id(db, product_id)
    if product is None:
        raise ProductNotFoundError("Product not found.")
    return _to_response(product)


def create_product(db: Session, payload: ProductCreate) -> ProductResponse:
    existing = product_repository.get_product_by_sku(db, payload.sku)
    if existing is not None:
        raise ProductConflictError(f"Product with SKU '{payload.sku}' already exists.")

    product = Product(
        sku=payload.sku,
        name=payload.name,
        category=payload.category,
        current_stock=payload.current_stock,
        unit_cost=payload.unit_cost,
        lead_time=payload.lead_time,
        supplier=payload.supplier,
        reorder_point=payload.reorder_point,
        safety_stock=payload.safety_stock,
    )
    return _to_response(product_repository.create_product(db, product))


def update_product(db: Session, product_id: str, payload: ProductUpdate) -> ProductResponse:
    product = product_repository.get_product_by_id(db, product_id)
    if product is None:
        raise ProductNotFoundError("Product not found.")

    if payload.sku and payload.sku != product.sku:
        existing = product_repository.get_product_by_sku(db, payload.sku)
        if existing is not None and existing.id != product.id:
            raise ProductConflictError(f"Product with SKU '{payload.sku}' already exists.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    return _to_response(product_repository.update_product(db, product))


def delete_product(db: Session, product_id: str) -> None:
    product = product_repository.get_product_by_id(db, product_id)
    if product is None:
        raise ProductNotFoundError("Product not found.")
    product_repository.delete_product(db, product)


def get_product_stats(db: Session) -> ProductStatsResponse:
    return ProductStatsResponse.model_validate(product_repository.get_product_stats(db))