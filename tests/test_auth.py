import pytest


@pytest.mark.asyncio(scope='session')
async def test_create_user(client):
    user_data = {
        "username": "TimurBro",
        "login": "Broo",
        "password": "password"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 200


@pytest.mark.asyncio(scope='session')
async def test_create_user_already_exists(client):
    user_data = {
        "username": "TimurBro",
        "login": "Broo",
        "password": "password"
    }

    response = await client.post("/users/", json=user_data)
    assert response.status_code == 400, 'Login already registered'
