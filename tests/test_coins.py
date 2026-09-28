import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app

HEADERS = {"X-API-Key": "mysecretkey123"}

MOCK_COINS = [
    {"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"},
    {"id": "ethereum", "name": "Ethereum", "symbol": "eth"},
]


@pytest.mark.anyio
async def test_list_coins_success():
    with patch(
        "app.routes.coins.fetch_all_coins",
        new_callable=AsyncMock,
        return_value=MOCK_COINS
    ):
        with patch("app.routes.coins.send_webhook", new_callable=AsyncMock):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get("/coins", headers=HEADERS)
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert data["page"] == 1


@pytest.mark.anyio
async def test_list_coins_no_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/coins")
        assert response.status_code == 403


@pytest.mark.anyio
async def test_list_coins_wrong_key():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/coins",
            headers={"X-API-Key": "wrongkey"}
        )
        assert response.status_code == 401


@pytest.mark.anyio
async def test_list_coins_pagination():
    with patch(
        "app.routes.coins.fetch_all_coins",
        new_callable=AsyncMock,
        return_value=MOCK_COINS * 5
    ):
        with patch("app.routes.coins.send_webhook", new_callable=AsyncMock):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get(
                    "/coins?page_num=2&per_page=2",
                    headers=HEADERS
                )
                assert response.status_code == 200
                data = response.json()
                assert data["page"] == 2
                assert data["per_page"] == 2


@pytest.mark.anyio
async def test_list_coins_cache_hit():
    with patch(
        "app.routes.coins.fetch_all_coins",
        new_callable=AsyncMock,
        return_value=MOCK_COINS
    ):
        with patch("app.routes.coins.send_webhook", new_callable=AsyncMock):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                # First call — cache miss
                await client.get("/coins?page_num=5", headers=HEADERS)
                # Second call — cache hit
                response = await client.get(
                    "/coins?page_num=5",
                    headers=HEADERS
                )
                assert response.status_code == 200
