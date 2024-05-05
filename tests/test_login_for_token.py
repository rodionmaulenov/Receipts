import pytest
from fastapi import status
from passlib.context import CryptContext
from app.models import User
from tests.conftest import async_session_maker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio(scope='session')
async def test_login_for_access_token(client):
    async with async_session_maker() as session:
        hashed_password = pwd_context.hash("Broo")
        test_user = User(username="TimurBro", login='timue123', hashed_password=hashed_password)
        session.add(test_user)
        await session.commit()

    form_data = {
        "username": "TimurBro",
        "password": "Broo"
    }

    response = await client.post("/token", data=form_data)

    assert response.status_code == status.HTTP_200_OK
    token_data = response.json()
    assert 'access_token' in token_data
    assert token_data['token_type'] == "bearer"
