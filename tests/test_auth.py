import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testusername",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testusername"
    assert "password" not in data


@pytest.mark.asyncio
async def test_duplicate_register(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrongpass(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401


async def test_login_nonexist_user(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": "noneexistusername",
            "password": "testpassword"
        }
    )
    assert response.status_code == 401