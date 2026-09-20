from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductStatsResponse, ProductUpdate
from app.services.product import (
    ProductConflictError,
    ProductNotFoundError,
    create_product,
    delete_product,
    get_product,
    get_product_stats,
    list_products,
    update_product,
)

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=ProductListResponse)
def read_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status: Literal["in-stock", "low-stock", "out-of-stock"] | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    return list_products(db, page=page, page_size=page_size, search=search, category=category, status=status)


@router.get("/products/stats", response_model=ProductStatsResponse)
def read_product_stats(db: Session = Depends(get_db)) -> ProductStatsResponse:
    return get_product_stats(db)


@router.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: str, db: Session = Depends(get_db)) -> ProductResponse:
    try:
        return get_product(db, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductResponse:
    try:
        return create_product(db, payload)
    except ProductConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product_endpoint(product_id: str, payload: ProductUpdate, db: Session = Depends(get_db)) -> ProductResponse:
    try:
        return update_product(db, product_id, payload)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        delete_product(db, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)