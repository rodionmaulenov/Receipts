import datetime

import pytest
from app.models import User, Receipt
from tests.conftest import async_session_maker
from tests.test_create_receipt import create_test_token


@pytest.mark.asyncio(scope='session')
async def test_get_receipts(client):
    async with async_session_maker() as session:
        user = User(username="testuser", login="testlogin", hashed_password="hashed_password")
        session.add(user)
        await session.commit()

        receipts = [
            Receipt(user_id=user.id, created_at=datetime.datetime(2021, 1, 1), payment_type='cash',
                    payment_amount=100.0, total=95.0),
            Receipt(user_id=user.id, created_at=datetime.datetime(2021, 1, 1), payment_type='card',
                    payment_amount=200.0, total=195.0)
        ]
        session.add_all(receipts)
        await session.commit()

    token = create_test_token(user_id=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/receipts/", headers=headers)

    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) == 2
    assert receipts[0]['id'] == 1
    assert receipts[1]['id'] == 2

    response = await client.get("/receipts/?receipt_id=1", headers=headers)
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) == 1

    response = await client.get("/receipts/?start_date=2021-01-01&end_date=2021-01-02", headers=headers)
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) == 2

    response = await client.get("/receipts/?payment_type=cash", headers=headers)
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) == 1

    response = await client.get("/receipts/?min_total=100.0", headers=headers)
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) == 1

    response = await client.get("/receipts/?max_total=200.0", headers=headers)
    assert response.status_code == 200
    receipts = response.json()
    assert len(receipts) == 2