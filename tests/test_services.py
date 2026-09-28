import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from app.services.coingecko import (
    check_coingecko_health,
    fetch_all_coins,
    fetch_all_categories,
    fetch_market_data
)
from app.services.webhook import send_webhook
from app.exceptions import AppException


@pytest.mark.anyio
async def test_check_coingecko_health_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"gecko_says": "v1.0.0"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )
        result = await check_coingecko_health()
        assert result["status"] == "reachable"


@pytest.mark.anyio
async def test_check_coingecko_health_failure():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Connection error")
        )
        result = await check_coingecko_health()
        assert result["status"] == "unreachable"
        assert result["version"] is None


@pytest.mark.anyio
async def test_fetch_all_coins_timeout():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        with pytest.raises(AppException) as exc:
            await fetch_all_coins()
        assert exc.value.status_code == 504


@pytest.mark.anyio
async def test_fetch_all_categories_timeout():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        with pytest.raises(AppException) as exc:
            await fetch_all_categories()
        assert exc.value.status_code == 504


@pytest.mark.anyio
async def test_fetch_market_data_timeout():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        with pytest.raises(AppException) as exc:
            await fetch_market_data(coin_ids="bitcoin")
        assert exc.value.status_code == 504


@pytest.mark.anyio
async def test_send_webhook_success():
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        # Should not raise
        await send_webhook("test_event", {"key": "value"})


@pytest.mark.anyio
async def test_send_webhook_no_url():
    with patch("app.services.webhook.WEBHOOK_URL", None):
        # Should not raise, just log warning
        await send_webhook("test_event", {"key": "value"})


@pytest.mark.anyio
async def test_send_webhook_failure():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=Exception("Failed")
        )
        # Should not raise — webhook failure must not break the API
        await send_webhook("test_event", {"key": "value"})
