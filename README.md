# Vetty Crypto API

A production-ready REST API built with FastAPI that serves cryptocurrency data from CoinGecko, with API key authentication, TTL caching, structured logging, webhook notifications, and centralized error handling.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI |
| HTTP Client | httpx (async) |
| Cache | cachetools (TTLCache) |
| Auth | API Key via header |
| External API | CoinGecko (free) |
| Webhook | webhook.site |
| Testing | pytest |

---

## Project Structure

```
vetty-crypto-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── cache.py
│   ├── logger.py
│   ├── exceptions.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── coins.py
│   │   ├── categories.py
│   │   └── markets.py
│   └── services/
│       ├── coingecko.py
│       └── webhook.py
├── tests/
│   ├── test_health.py
│   ├── test_coins.py
│   ├── test_categories.py
│   └── test_markets.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/sidson05/Python-API.git
cd Python-API
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open API docs
```
http://localhost:8000/docs
```

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `API_KEY` | Secret key for protected endpoints | `mysecretkey123` |
| `CACHE_TTL` | Cache duration in seconds | `60` |
| `WEBHOOK_URL` | webhook.site URL for notifications | `https://webhook.site/xxx` |
| `COINGECKO_BASE_URL` | CoinGecko base URL | `https://api.coingecko.com/api/v3` |
| `APP_VERSION` | App version label | `1.0.0` |

---

## API Endpoints

### `GET /health`
No auth required. Returns app and CoinGecko status.

```json
{
  "status": "ok",
  "version": "1.0.0",
  "coingecko": "reachable"
}
```

---

### `GET /coins`
**Auth required:** `x-api-key` header

| Query Param | Type | Default | Description |
|---|---|---|---|
| `page_num` | int | 1 | Page number |
| `per_page` | int | 10 | Results per page (max 250) |

---

### `GET /categories`
**Auth required:** `x-api-key` header

| Query Param | Type | Default | Description |
|---|---|---|---|
| `page_num` | int | 1 | Page number |
| `per_page` | int | 10 | Results per page (max 250) |

---

### `GET /markets`
**Auth required:** `x-api-key` header

| Query Param | Type | Default | Description |
|---|---|---|---|
| `coin_id` | str | None | Filter by coin (e.g. `bitcoin`) |
| `category` | str | None | Filter by category |
| `page_num` | int | 1 | Page number |
| `per_page` | int | 10 | Results per page (max 250) |

---

## Authentication

All protected endpoints require an API key passed as a header:

```
x-api-key: your_secret_key
```

Invalid or missing key returns:
```json
{
  "error": "unauthorized",
  "detail": "Invalid or missing API key",
  "status_code": 401
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Caching

Responses are cached in-memory using TTLCache. Cache duration is controlled by `CACHE_TTL` in `.env`. A cache miss triggers a CoinGecko API call and fires a webhook notification.

---

## Webhook

On every cache miss, a POST request is fired to your `WEBHOOK_URL` with payload:

```json
{
  "event": "market_data_fetched",
  "data": { "coin_id": "bitcoin", "category": null, "page": 1, "per_page": 10 }
}
```

Webhook failures are logged but never break the API response.
