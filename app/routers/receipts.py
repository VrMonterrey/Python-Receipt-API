from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Receipt, User, Product, receipt_product
from app.schemas import ReceiptOut, ReceiptFilter, ReceiptCreate, ProductOut
from app.auth import get_current_user
from typing import List, Optional, Literal
from datetime import datetime, timezone

router = APIRouter()


@router.post("/", response_model=ReceiptOut)
def create_receipt(
    receipt: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = sum([p.price * p.quantity for p in receipt.products])
    if receipt.payment.amount < total:
        raise HTTPException(status_code=400, detail="Insufficient payment")
    rest = receipt.payment.amount - total

    new_receipt = Receipt(
        total=total,
        created_at=datetime.now(timezone.utc),
        payment_type=receipt.payment.type,
        payment_amount=receipt.payment.amount,
        owner=current_user,
    )
    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)

    for product in receipt.products:
        db_product = (
            db.query(Product)
            .filter(Product.name == product.name, Product.price == product.price)
            .first()
        )
        if not db_product:
            db_product = Product(name=product.name, price=product.price)
            db.add(db_product)
            db.commit()
            db.refresh(db_product)

        db.execute(
            receipt_product.insert().values(
                receipt_id=new_receipt.id,
                product_id=db_product.id,
                quantity=product.quantity,
            )
        )

    db.commit()

    product_out = db.execute(
        text(
            """
        SELECT p.name, p.price, rp.quantity 
        FROM receipt_product rp
        JOIN products p ON p.id = rp.product_id
        WHERE rp.receipt_id = :receipt_id
    """
        ),
        {"receipt_id": new_receipt.id},
    ).fetchall()
    product_out_list = [
        ProductOut(name=prod.name, price=prod.price, total=prod.price * prod.quantity)
        for prod in product_out
    ]
    return {
        "id": new_receipt.id,
        "products": product_out_list,
        "total": total,
        "rest": rest,
        "created_at": new_receipt.created_at,
        "payment": receipt.payment,
    }


@router.get("/", response_model=List[ReceiptOut])
def list_receipts(
    start_date: Optional[datetime] = Query(
        None, description="Filter receipts starting from this datetime (inclusive). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Filter receipts up to this datetime (inclusive). Format: YYYY-MM-DDTHH:MM:SS"
    ),
    min_total: Optional[float] = Query(
        None, description="Filter receipts with a total greater than or equal to this amount"
    ),
    payment_type: Optional[Literal["cash", "cashless"]] = Query(
        None, description="Filter receipts by payment type"
    ),
    skip: Optional[int] = Query(
        0, description="Number of records to skip (for pagination)"
    ),
    limit: Optional[int] = Query(
        10, description="Maximum number of records to return (for pagination)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Receipt).filter(Receipt.user_id == current_user.id)

    if start_date:
        query = query.filter(Receipt.created_at >= start_date)
    if end_date:
        query = query.filter(Receipt.created_at <= end_date)
    if min_total:
        query = query.filter(Receipt.total >= min_total)
    if payment_type:
        query = query.filter(Receipt.payment_type == payment_type)

    query = query.offset(skip).limit(limit)

    receipts = query.all()

    result = []
    for receipt in receipts:
        product_out = db.execute(
            text(
                """
                SELECT p.name, p.price, rp.quantity 
                FROM receipt_product rp
                JOIN products p ON p.id = rp.product_id
                WHERE rp.receipt_id = :receipt_id
                """
            ),
            {"receipt_id": receipt.id},
        ).fetchall()

        product_out_list = [
            ProductOut(name=prod.name, price=prod.price, total=prod.price * prod.quantity)
            for prod in product_out
        ]

        result.append(
            {
                "id": receipt.id,
                "products": product_out_list,
                "total": receipt.total,
                "rest": receipt.payment_amount - receipt.total,
                "created_at": receipt.created_at,
                "payment": {
                    "type": receipt.payment_type,
                    "amount": receipt.payment_amount,
                },
            }
        )

    return result


@router.get("/{receipt_id}", response_model=ReceiptOut)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = (
        db.query(Receipt)
        .filter(Receipt.id == receipt_id, Receipt.user_id == current_user.id)
        .first()
    )

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    product_out = db.execute(
        text(
            """
            SELECT p.name, p.price, rp.quantity 
            FROM receipt_product rp
            JOIN products p ON p.id = rp.product_id
            WHERE rp.receipt_id = :receipt_id
            """
        ),
        {"receipt_id": receipt.id},
    ).fetchall()

    product_out_list = [
        ProductOut(name=prod.name, price=prod.price, total=prod.price * prod.quantity)
        for prod in product_out
    ]

    return {
        "id": receipt.id,
        "products": product_out_list,
        "total": receipt.total,
        "rest": receipt.payment_amount - receipt.total,
        "created_at": receipt.created_at,
        "payment": {"type": receipt.payment_type, "amount": receipt.payment_amount},
    }
