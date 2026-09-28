import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app

HEADERS = {"X-API-Key": "mysecretkey123"}

MOCK_CATEGORIES = [
    {"category_id": "defi", "name": "DeFi"},
    {"category_id": "nft", "name": "NFT"},
]


@pytest.mark.anyio
async def test_list_categories_success():
    with patch(
        "app.routes.categories.fetch_all_categories",
        new_callable=AsyncMock,
        return_value=MOCK_CATEGORIES
    ):
        with patch(
            "app.routes.categories.send_webhook",
            new_callable=AsyncMock
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get(
                    "/categories",
                    headers=HEADERS
                )
                assert response.status_code == 200
                data = response.json()
                assert "data" in data
                assert data["page"] == 1


@pytest.mark.anyio
async def test_list_categories_no_auth():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/categories")
        assert response.status_code == 403
