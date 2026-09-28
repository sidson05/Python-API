import httpx
from app.config import COINGECKO_BASE_URL
from app.logger import get_logger
from app.exceptions import AppException

logger = get_logger(__name__)


async def check_coingecko_health() -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{COINGECKO_BASE_URL}/ping")
            response.raise_for_status()
            data = response.json()
            return {
                "status": "reachable",
                "version": data.get("gecko_says", "unknown")
            }
    except Exception:
        logger.warning("CoinGecko is unreachable")
        return {
            "status": "unreachable",
            "version": None
        }


async def fetch_all_coins() -> list:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            logger.info("Fetching all coins from CoinGecko")
            response = await client.get(f"{COINGECKO_BASE_URL}/coins/list")
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error("Timeout while fetching coins")
        raise AppException(
            status_code=504,
            error="gateway_timeout",
            detail="CoinGecko API timed out"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"CoinGecko error: {e.response.status_code}")
        raise AppException(
            status_code=502,
            error="bad_gateway",
            detail="CoinGecko API returned an error"
        )
    except Exception:
        logger.error("Unexpected error fetching coins")
        raise AppException(
            status_code=500,
            error="internal_server_error",
            detail="Failed to fetch coins"
        )


async def fetch_all_categories() -> list:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            logger.info("Fetching all categories from CoinGecko")
            response = await client.get(
                f"{COINGECKO_BASE_URL}/coins/categories/list"
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error("Timeout while fetching categories")
        raise AppException(
            status_code=504,
            error="gateway_timeout",
            detail="CoinGecko API timed out"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"CoinGecko error: {e.response.status_code}")
        raise AppException(
            status_code=502,
            error="bad_gateway",
            detail="CoinGecko API returned an error"
        )
    except Exception:
        logger.error("Unexpected error fetching categories")
        raise AppException(
            status_code=500,
            error="internal_server_error",
            detail="Failed to fetch categories"
        )


async def fetch_market_data(
    coin_ids: str = None,
    category: str = None,
    page: int = 1,
    per_page: int = 10
) -> list:
    params = {
        "vs_currency": "cad",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False
    }

    if coin_ids:
        params["ids"] = coin_ids
    if category:
        params["category"] = category

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            logger.info(f"Fetching market data | params: {params}")
            response = await client.get(
                f"{COINGECKO_BASE_URL}/coins/markets",
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error("Timeout while fetching market data")
        raise AppException(
            status_code=504,
            error="gateway_timeout",
            detail="CoinGecko API timed out"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"CoinGecko error: {e.response.status_code}")
        raise AppException(
            status_code=502,
            error="bad_gateway",
            detail="CoinGecko API returned an error"
        )
    except Exception:
        logger.error("Unexpected error fetching market data")
        raise AppException(
            status_code=500,
            error="internal_server_error",
            detail="Failed to fetch market data"
        )
