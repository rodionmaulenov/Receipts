from decimal import Decimal
from typing import List, Optional

from starlette.responses import PlainTextResponse

from app.models import Receipt, ReceiptItem
from sqlalchemy.orm import selectinload
from app.services import get_current_user, format_receipt
from app.schemas import ReceiptCreate, ProductDisplay, PaymentInfo, ReceiptDisplay
from datetime import datetime, date
from fastapi import Depends, Query, APIRouter, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.database import get_async_session
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post("/receipts/", response_model=ReceiptDisplay)
async def create_receipt(receipt_data: ReceiptCreate, db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(get_current_user)):
    """
        Creates a new receipt based on the products and payment details provided.
        Calculates the total cost of the products and determines the change to be given back.
        Ensures that the payment amount covers the total cost of products, otherwise raises an error.
        Saves the new receipt to the database and returns detailed information about the created receipt.
    """
    # Calculate total and rest
    total = Decimal('0.00')
    for item in receipt_data.products:
        total += Decimal(item.price) * Decimal(item.quantity)
    rest = Decimal(receipt_data.payment.amount) - total

    if rest < Decimal('0.00'):
        raise HTTPException(status_code=400, detail="Payment amount is less than the total price of products.")

    # Create the receipt entry in the database
    new_receipt = Receipt(
        user_id=user.id,
        created_at=datetime.utcnow(),
        payment_type=receipt_data.payment.type,
        payment_amount=Decimal(receipt_data.payment.amount),
        total=total,
        change_given=rest
    )
    db.add(new_receipt)
    await db.commit()
    await db.refresh(new_receipt)

    # Prepare products display information
    products_display = [
        ProductDisplay(
            name=item.name,
            price=Decimal(item.price),
            quantity=Decimal(item.quantity),
            total=Decimal(item.price) * Decimal(item.quantity)
        ) for item in receipt_data.products
    ]

    # Create PaymentInfo
    payment_info = PaymentInfo(
        type=receipt_data.payment.type,
        amount=Decimal(receipt_data.payment.amount)
    )

    # Create and return the final receipt display object
    receipt_display = ReceiptDisplay(
        id=new_receipt.id,
        products=products_display,
        payment=payment_info,
        total=total,
        rest=rest,
        created_at=new_receipt.created_at
    )

    return receipt_display


@router.get("/receipts/", response_model=List[ReceiptDisplay])
async def get_receipts(
        receipt_id: Optional[int] = Query(None, description="Filter by specific receipt ID"),
        start_date: Optional[date] = Query(None, description="Start date for filtering receipts"),
        end_date: Optional[date] = Query(None, description="End date for filtering receipts"),
        min_total: Optional[float] = Query(None, description="Minimum total amount for filtering receipts"),
        max_total: Optional[float] = Query(None, description="Maximum total amount for filtering receipts"),
        payment_type: Optional[str] = Query(None, description="Filter receipts by payment type"),
        limit: int = Query(10, description="Limit number of receipts returned"),
        offset: int = Query(0, description="Offset for pagination"),
        db: AsyncSession = Depends(get_async_session),
        user=Depends(get_current_user)
) -> List[ReceiptDisplay]:
    """
    Retrieves a list of receipts for the authenticated user with optional filtering by receipt ID,
    date range, minimum and maximum total, payment type, and pagination.
    """
    query = select(Receipt).where(Receipt.user_id == user.id).options(
        selectinload(Receipt.items).selectinload(ReceiptItem.product)
    )

    # Apply filtering by receipt ID if provided
    if receipt_id:
        query = query.filter(Receipt.id == receipt_id)

    if start_date:
        query = query.filter(Receipt.created_at >= start_date)
    if end_date:
        query = query.filter(Receipt.created_at <= end_date)
    if min_total:
        query = query.filter(Receipt.total >= Decimal(min_total))
    if max_total:
        query = query.filter(Receipt.total <= Decimal(max_total))
    if payment_type:
        query = query.filter(Receipt.payment_type == payment_type)

    query = query.offset(offset).limit(limit)
    results = await db.execute(query)
    receipts = results.scalars().all()

    response = []
    for receipt in receipts:
        products_display = [
            ProductDisplay(
                name=item.product.name,
                price=f"{item.product.price:.2f}",
                quantity=f"{item.quantity:.2f}",
                total=f"{item.quantity * item.product.price:.2f}"
            ) for item in receipt.items
        ]
        total_products_cost = sum(Decimal(product.total) for product in products_display)
        rest = Decimal(receipt.payment_amount) - total_products_cost

        response.append(ReceiptDisplay(
            id=receipt.id,
            products=products_display,
            payment=PaymentInfo(type=receipt.payment_type, amount=f"{receipt.payment_amount:.2f}"),
            total=f"{receipt.total:.2f}",
            rest=f"{rest:.2f}",
            created_at=receipt.created_at.isoformat()
        ))

    if not response:
        raise HTTPException(status_code=404, detail="No receipts found matching the criteria")

    return response


@router.get("/receipts/{user_id}", response_class=PlainTextResponse)
async def get_receipt(user_id: int, db: AsyncSession = Depends(get_async_session)):
    """
        Retrieves a specific receipt by user ID.
        Includes joined loading of product details associated with the receipt items.
        Returns the formatted receipt details if found, or an error message if not found.
        This function is meant to provide detailed access to an individual receipt's contents.
    """
    result = await db.execute(select(Receipt).where(Receipt.user_id == user_id).options(
        joinedload(Receipt.items).joinedload(ReceiptItem.product)))
    receipt = result.scalars().first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return format_receipt(receipt)
