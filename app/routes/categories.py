from fastapi import APIRouter, Depends, Query
from app.dependencies import verify_api_key
from app.services.coingecko import fetch_all_categories
from app.services.webhook import send_webhook
from app.cache import cache
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/categories")
async def list_categories(
    page_num: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=250),
    _: None = Depends(verify_api_key)
):
    cache_key = f"categories_{page_num}_{per_page}"

    if cache_key in cache:
        logger.info(f"Cache HIT | key: {cache_key}")
        return cache[cache_key]

    logger.info(f"Cache MISS | key: {cache_key}")
    all_categories = await fetch_all_categories()

    # Manual pagination
    start = (page_num - 1) * per_page
    end = start + per_page
    paginated = all_categories[start:end]

    result = {
        "page": page_num,
        "per_page": per_page,
        "total": len(all_categories),
        "data": [
            {
                "category_id": cat["category_id"],
                "name": cat["name"]
            }
            for cat in paginated
        ]
    }

    cache[cache_key] = result

    await send_webhook("categories_fetched", {
        "page": page_num,
        "per_page": per_page
    })

    return result
