from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Receipt, User, Product, receipt_product
from app.schemas import ReceiptOut, ProductOut, ReceiptCreate
from app.auth import get_current_user
from typing import List, Optional, Literal
from datetime import datetime, timezone
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.post(
    "/",
    response_model=ReceiptOut,
    summary="Create a new receipt",
    description="""
    Creates a new sales receipt with a list of products and payment details.
    \nReturns the newly created receipt.
    """
)
def create_receipt(
    receipt: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    valid_products = [p for p in receipt.products if p.quantity > 0]

    if not valid_products:
        raise HTTPException(status_code=400, detail="No products were bought.")

    total = sum([p.price * p.quantity for p in valid_products])
    if receipt.payment.amount < total:
        raise HTTPException(status_code=400, detail="Insufficient payment")

    new_receipt = Receipt(
        total=total,
        created_at=datetime.now(timezone.utc),
        payment_type=receipt.payment.type,
        payment_amount=receipt.payment.amount if receipt.payment.type == 'cash' else total,
        owner=current_user,
    )

    rest = new_receipt.payment_amount - total

    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)

    for product in valid_products:
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
        "payment": {
            "type": new_receipt.payment_type,
            "amount": new_receipt.payment_amount,
        }
    }

@router.get(
    "/",
    response_model=List[ReceiptOut],
    summary="List receipts",
    description="""
    List all receipts for the authenticated user, with optional filtering by:
    \n- `start_date`: Filter receipts starting from this datetime.
    \n- `end_date`: Filter receipts up to this datetime.
    \n- `min_total`: Minimum total price of receipts.
    \n- `payment_type`: Filter by payment type (cash/cashless).
    \nPagination is supported using `skip` and `limit`.
    """
)
def list_receipts(
    start_date: Optional[datetime] = Query(
        None,
        description="Filter receipts starting from this datetime (inclusive). Format: YYYY-MM-DDTHH:MM:SS",
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter receipts up to this datetime (inclusive). Format: YYYY-MM-DDTHH:MM:SS",
    ),
    min_total: Optional[float] = Query(
        None,
        description="Filter receipts with a total greater than or equal to this amount",
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
            ProductOut(
                name=prod.name, price=prod.price, total=prod.price * prod.quantity
            )
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

@router.get(
    "/{receipt_id}",
    response_class=PlainTextResponse,
    summary="Get public receipt",
    description="""
    Retrieve a plain text version of a receipt. This endpoint can be accessed by anyone without authentication.
    Customize the width of each line using the `line_width` parameter.
    """
)
def get_public_receipt(
    receipt_id: int, 
    line_width: int = 30,
    db: Session = Depends(get_db)
):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    
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

    receipt_text = build_receipt_text(receipt, product_out, line_width)
    
    return receipt_text


def build_receipt_text(receipt: Receipt, product_out: list, line_width: int) -> str:
    receipt_lines = []

    receipt_lines.append(receipt.owner.username.center(line_width))
    receipt_lines.append("=" * line_width)
    
    for prod in product_out:
        quantity = prod.quantity
        price = prod.price
        total = price * quantity

        quantity_price_str = f"{quantity:.2f} x {price:.2f}"
        receipt_lines.append(quantity_price_str)
        product_name_str = prod.name
        total_str = f"{total:.2f}"

        receipt_lines.append(product_name_str.ljust(line_width - len(total_str)) + total_str)
        receipt_lines.append("-" * line_width)

    receipt_lines.append("=" * line_width)

    change = receipt.payment_amount - receipt.total

    receipt_lines.append(f"СУМА".ljust(line_width - len(f"{receipt.total:.2f}")) + f"{receipt.total:.2f}")
    payment_type = "Готівка" if receipt.payment_type == "cash" else "Картка"
    receipt_lines.append(f"{payment_type}".ljust(line_width - len(f"{receipt.payment_amount:.2f}")) + f"{receipt.payment_amount:.2f}")
    receipt_lines.append(f"Решта".ljust(line_width - len(f"{change:.2f}")) + f"{change:.2f}")
    
    receipt_lines.append("=" * line_width)

    receipt_lines.append(f"{receipt.created_at.strftime('%d.%m.%Y %H:%M')}".center(line_width))
    receipt_lines.append("Дякуємо за покупку!".center(line_width))

    return "\n".join(receipt_lines)