import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app

HEADERS = {"X-API-Key": "mysecretkey123"}

MOCK_MARKET_DATA = [
    {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 45000,
        "market_cap": 900000000
    }
]


@pytest.mark.anyio
async def test_markets_with_coin_id():
    with patch(
        "app.routes.markets.fetch_market_data",
        new_callable=AsyncMock,
        return_value=MOCK_MARKET_DATA
    ):
        with patch(
            "app.routes.markets.send_webhook",
            new_callable=AsyncMock
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get(
                    "/markets?coin_id=bitcoin",
                    headers=HEADERS
                )
                assert response.status_code == 200
                data = response.json()
                assert data["currency"] == "CAD"
                assert "data" in data


@pytest.mark.anyio
async def test_markets_with_category():
    with patch(
        "app.routes.markets.fetch_market_data",
        new_callable=AsyncMock,
        return_value=MOCK_MARKET_DATA
    ):
        with patch(
            "app.routes.markets.send_webhook",
            new_callable=AsyncMock
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get(
                    "/markets?category=defi",
                    headers=HEADERS
                )
                assert response.status_code == 200


@pytest.mark.anyio
async def test_markets_no_params():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/markets", headers=HEADERS)
        assert response.status_code == 400


@pytest.mark.anyio
async def test_markets_no_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/markets?coin_id=bitcoin")
        assert response.status_code == 403


@pytest.mark.anyio
async def test_markets_with_both_params():
    with patch(
        "app.routes.markets.fetch_market_data",
        new_callable=AsyncMock,
        return_value=MOCK_MARKET_DATA
    ):
        with patch(
            "app.routes.markets.send_webhook",
            new_callable=AsyncMock
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get(
                    "/markets?coin_id=bitcoin&category=defi",
                    headers=HEADERS
                )
                assert response.status_code == 200
                data = response.json()
                assert data["currency"] == "CAD"


@pytest.mark.anyio
async def test_markets_cache_hit():
    with patch(
        "app.routes.markets.fetch_market_data",
        new_callable=AsyncMock,
        return_value=MOCK_MARKET_DATA
    ):
        with patch(
            "app.routes.markets.send_webhook",
            new_callable=AsyncMock
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                # First call — cache miss
                await client.get(
                    "/markets?coin_id=ethereum&page_num=3",
                    headers=HEADERS
                )
                # Second call — cache hit
                response = await client.get(
                    "/markets?coin_id=ethereum&page_num=3",
                    headers=HEADERS
                )
                assert response.status_code == 200


@pytest.mark.anyio
async def test_markets_pagination():
    with patch(
        "app.routes.markets.fetch_market_data",
        new_callable=AsyncMock,
        return_value=MOCK_MARKET_DATA
    ):
        with patch(
            "app.routes.markets.send_webhook",
            new_callable=AsyncMock
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get(
                    "/markets?coin_id=bitcoin&page_num=2&per_page=5",
                    headers=HEADERS
                )
                assert response.status_code == 200
                data = response.json()
                assert data["page"] == 2
                assert data["per_page"] == 5
