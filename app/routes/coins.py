from fastapi import APIRouter, Depends, Query
from app.dependencies import verify_api_key
from app.services.coingecko import fetch_all_coins
from app.services.webhook import send_webhook
from app.cache import cache
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/coins")
async def list_coins(
    page_num: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=250),
    _: None = Depends(verify_api_key)
):
    cache_key = f"coins_{page_num}_{per_page}"

    if cache_key in cache:
        logger.info(f"Cache HIT | key: {cache_key}")
        return cache[cache_key]

    logger.info(f"Cache MISS | key: {cache_key}")
    all_coins = await fetch_all_coins()

    # Manual pagination since CoinGecko /coins/list returns everything
    start = (page_num - 1) * per_page
    end = start + per_page
    paginated = all_coins[start:end]

    result = {
        "page": page_num,
        "per_page": per_page,
        "total": len(all_coins),
        "data": [
            {
                "id": coin["id"],
                "name": coin["name"],
                "symbol": coin["symbol"]
            }
            for coin in paginated
        ]
    }

    cache[cache_key] = result

    await send_webhook("coins_fetched", {
        "page": page_num,
        "per_page": per_page
    })

    return result
