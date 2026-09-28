from fastapi import APIRouter
from app.config import APP_VERSION
from app.services.coingecko import check_coingecko_health
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    logger.info("Health check requested")
    coingecko_status = await check_coingecko_health()

    return {
        "status": "healthy",
        "version": APP_VERSION,
        "coingecko": coingecko_status
    }
