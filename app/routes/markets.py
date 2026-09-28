from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.dependencies import verify_api_key
from app.services.coingecko import fetch_market_data
from app.services.webhook import send_webhook
from app.cache import cache
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/markets")
async def get_market_data(
    coin_id: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=250),
    _: None = Depends(verify_api_key)
):
    # At least one of coin_id or category must be provided
    if not coin_id and not category:
        raise HTTPException(
            status_code=400,
            detail="At least one of coin_id or category must be provided"
        )

    cache_key = f"markets_{coin_id}_{category}_{page_num}_{per_page}"

    if cache_key in cache:
        logger.info(f"Cache HIT | key: {cache_key}")
        return cache[cache_key]

    logger.info(f"Cache MISS | key: {cache_key}")

    data = await fetch_market_data(
        coin_ids=coin_id,
        category=category,
        page=page_num,
        per_page=per_page
    )

    result = {
        "page": page_num,
        "per_page": per_page,
        "currency": "CAD",
        "data": data
    }

    cache[cache_key] = result

    # Fire webhook only on cache miss (fresh data from CoinGecko)
    await send_webhook("market_data_fetched", {
        "coin_id": coin_id,
        "category": category,
        "page": page_num,
        "per_page": per_page
    })

    return result
