from fastapi import FastAPI
from app.config import APP_VERSION
from app.exceptions import (
    AppException,
    app_exception_handler,
    global_exception_handler,
)
from app.routes import health, coins, categories, markets

app = FastAPI(
    title="Vetty Crypto API",
    description="Cryptocurrency market data API powered by CoinGecko",
    version=APP_VERSION
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routes
app.include_router(health.router, tags=["Health"])
app.include_router(coins.router, tags=["Coins"])
app.include_router(categories.router, tags=["Categories"])
app.include_router(markets.router, tags=["Markets"])
