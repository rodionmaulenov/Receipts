import pytest
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.models import User
from tests.conftest import async_session_maker

SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_token(user_id: int, expires_delta: timedelta = timedelta(minutes=30)):
    """Generate a JWT token for testing."""
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@pytest.mark.asyncio(scope='session')
async def test_create_receipt(client):
    async with async_session_maker() as session:
        hashed_password = pwd_context.hash("Broo")
        test_user = User(username="TimurBro", login='timue123', hashed_password=hashed_password)
        session.add(test_user)
        await session.commit()

    token = create_test_token(user_id=test_user.id)

    receipt_data = {
        "products": [
            {"name": "Apple1", "price": "0.50", "quantity": "10"},
            {"name": "Banana1", "price": "0.30", "quantity": "5"}
        ],
        "payment": {
            "type": "cash",
            "amount": "10.00"
        }
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/receipts/", headers=headers, json=receipt_data)

    assert response.status_code == 200
    data = response.json()
    assert data['total'] == '6.50'
    assert data['rest'] == '3.50'
    assert len(data['products']) == 2
    assert data['payment']['type'] == 'cash'
    assert data['payment']['amount'] == '10.00'


@pytest.mark.asyncio(scope='session')
async def test_create_receipt_when_user_not_exists(client):
    token = create_test_token(user_id=999)

    # Prepare receipt data
    receipt_data = {
        "products": [
            {"name": "Apple1", "price": "0.50", "quantity": "10"},
            {"name": "Banana1", "price": "0.30", "quantity": "5"}
        ],
        "payment": {
            "type": "cash",
            "amount": "10.00"
        }
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/receipts/", headers=headers, json=receipt_data)
    assert response.status_code == 404


