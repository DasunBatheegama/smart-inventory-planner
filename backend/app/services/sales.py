from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.sales_record import SalesRecord
from app.models.sales_upload import SalesUpload
from app.repositories import sales as sales_repository


class SalesFileError(Exception):
    pass


class SalesValidationError(Exception):
    pass


@dataclass
class SalesUploadErrorItem:
    row: int
    error: str


def _read_csv_text(file: UploadFile) -> str:
    if file.content_type not in {"text/csv", "application/vnd.ms-excel", "application/csv", "text/plain", None}:
        raise SalesFileError("Only CSV files are supported.")
    if not (file.filename or "").lower().endswith(".csv"):
        raise SalesFileError("Only CSV files are supported.")

    contents = file.file.read()
    if not contents:
        return ""
    return contents.decode("utf-8-sig")


def _normalize_headers(headers: list[str]) -> dict[str, str]:
    return {header.strip().lower(): header for header in headers if header}


def _parse_quantity(value: str, row_number: int) -> int:
    try:
        quantity = Decimal(value.strip())
    except (InvalidOperation, AttributeError) as exc:
        raise SalesValidationError(f"Row {row_number}: Quantity Sold must be numeric.") from exc
    if quantity != quantity.to_integral_value():
        raise SalesValidationError(f"Row {row_number}: Quantity Sold must be an integer.")
    if quantity < 0:
        raise SalesValidationError(f"Row {row_number}: Quantity Sold cannot be negative.")
    return int(quantity)


def _parse_date(value: str, row_number: int) -> date:
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError) as exc:
        raise SalesValidationError(f"Row {row_number}: Date is invalid.") from exc


def _iter_rows(text: str):
    if not text.strip():
        return []
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise SalesFileError("Required columns are missing: Date, SKU, Quantity Sold.")
    header_map = _normalize_headers(reader.fieldnames)
    missing = [name for name in ["Date", "SKU", "Quantity Sold"] if name.lower() not in header_map]
    if missing:
        raise SalesFileError(f"Required columns are missing: {', '.join(missing)}.")
    rows = []
    for index, row in enumerate(reader, start=2):
        rows.append((index, row, header_map))
    return rows


def _build_sales_record(db: Session, row_number: int, row: dict[str, str], header_map: dict[str, str]):
    raw_date = row.get(header_map["date"], "")
    raw_sku = row.get(header_map["sku"], "")
    raw_quantity = row.get(header_map["quantity sold"], "")

    if not any([str(raw_date).strip(), str(raw_sku).strip(), str(raw_quantity).strip()]):
        return None, None

    product = sales_repository.get_product_by_sku(db, str(raw_sku).strip())
    if product is None:
        raise SalesValidationError(f"Row {row_number}: Product with SKU '{str(raw_sku).strip()}' was not found.")

    parsed_date = _parse_date(str(raw_date), row_number)
    parsed_quantity = _parse_quantity(str(raw_quantity), row_number)

    return SalesRecord(
        product_id=product.id,
        date=parsed_date,
        quantity_sold=parsed_quantity,
    ), product


def import_sales_csv(db: Session, file: UploadFile):
    file_name = file.filename or "sales.csv"
    upload = sales_repository.create_sales_upload(
        db,
        SalesUpload(
            file_name=file_name,
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            imported_rows=0,
            status="processing",
        ),
    )

    try:
        text = _read_csv_text(file)
        if not text.strip():
            upload.status = "failed"
            sales_repository.update_sales_upload(db, upload)
            return {
                "file_name": file_name,
                "total_rows": 0,
                "valid_rows": 0,
                "invalid_rows": 0,
                "imported_rows": 0,
                "status": "failed",
                "errors": [],
            }

        rows = _iter_rows(text)
        records: list[SalesRecord] = []
        errors: list[SalesUploadErrorItem] = []

        for row_number, row, header_map in rows:
            try:
                result, _product = _build_sales_record(db, row_number, row, header_map)
                if result is None:
                    continue
                records.append(result)
            except SalesValidationError as exc:
                errors.append(SalesUploadErrorItem(row=row_number, error=str(exc)))

        imported_records = sales_repository.create_sales_records(db, records) if records else []
        total_rows = len(rows)
        valid_rows = len(imported_records)
        invalid_rows = len(errors)
        status_value = "completed" if invalid_rows == 0 else ("completed_with_errors" if valid_rows > 0 else "failed")

        upload.total_rows = total_rows
        upload.valid_rows = valid_rows
        upload.invalid_rows = invalid_rows
        upload.imported_rows = len(imported_records)
        upload.status = status_value
        sales_repository.update_sales_upload(db, upload)

        return {
            "file_name": file_name,
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "imported_rows": len(imported_records),
            "status": status_value,
            "errors": [error.__dict__ for error in errors],
        }
    except SalesFileError as exc:
        upload.status = "failed"
        sales_repository.update_sales_upload(db, upload)
        raise


def list_sales_records(db: Session, *, page: int, page_size: int, sku: str | None, start_date: date | None, end_date: date | None):
    offset = (page - 1) * page_size
    rows, total = sales_repository.get_sales_records(
        db,
        offset=offset,
        limit=page_size,
        sku=sku,
        start_date=start_date,
        end_date=end_date,
    )
    items = []
    for sales_record, product in rows:
        items.append(
            {
                "id": sales_record.id,
                "product_id": sales_record.product_id,
                "sku": product.sku,
                "product_name": product.name,
                "date": sales_record.date,
                "quantity_sold": sales_record.quantity_sold,
                "created_at": sales_record.created_at,
            }
        )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_sales_record(db: Session, sales_id: str):
    row = sales_repository.get_sales_by_id_with_product(db, sales_id)
    if row is None:
        return None
    sales_record, product = row
    return {
        "id": sales_record.id,
        "product_id": sales_record.product_id,
        "sku": product.sku,
        "product_name": product.name,
        "date": sales_record.date,
        "quantity_sold": sales_record.quantity_sold,
        "created_at": sales_record.created_at,
    }


def get_sales_summary(db: Session):
    return sales_repository.get_sales_summary(db)


def get_sales_upload_history(db: Session, *, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    items, total = sales_repository.get_upload_history(db, offset=offset, limit=page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}