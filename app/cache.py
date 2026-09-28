from cachetools import TTLCache
from app.config import CACHE_TTL

# Max 500 items, each lives for CACHE_TTL seconds
cache = TTLCache(maxsize=500, ttl=CACHE_TTL)
