from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.config import API_KEY

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)):
    if not key:
        raise HTTPException(
            status_code=403,
            detail="Not authenticated"
        )
    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
