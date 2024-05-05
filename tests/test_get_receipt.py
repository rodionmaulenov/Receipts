import pytest
from httpx import AsyncClient
from app.models import User, Receipt, ReceiptItem, Product
from datetime import datetime

from tests.conftest import async_session_maker


@pytest.fixture
async def setup_receipt():
    async with async_session_maker() as session:
        user = User(username="testuser", login="testlogin", hashed_password="hashed_password")
        product = Product(name="Test Product", price=10.00)
        session.add_all([user, product])
        await session.commit()

        receipt = Receipt(
            user_id=user.id,
            created_at=datetime.now(),
            payment_type='cash',
            payment_amount=100.00,
            total=95.00
        )
        receipt_item = ReceiptItem(
            receipt=receipt,
            product=product,
            quantity=5,
        )
        session.add_all([receipt, receipt_item])
        await session.commit()

        return receipt.id


@pytest.mark.asyncio(scope='session')
async def test_get_receipt(setup_receipt, client: AsyncClient):
    receipt_id = setup_receipt
    response = await client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    receipt_details = response.text

    assert "ФОП Джонсонок Борис" in receipt_details
    assert "=======================" in receipt_details
    assert "Test Product 5 x 10.00 50.00" in receipt_details
    assert "-----------------------" in receipt_details
    assert "СУМА 50.00" in receipt_details
    assert "Картка 100.00" in receipt_details
    assert "Решта 50.00" in receipt_details
    assert "=======================" in receipt_details


