# python-trading-212 (WIP)

A lightweight Python client for the [Trading 212 API](https://t212public-api-docs.redoc.ly/), providing both **asynchronous** and **synchronous** interfaces.

- `AsyncTrading212Client`: async client built with `aiohttp`
- `Trading212Client`: sync client built with `requests`

---

## Installation

```bash
pip install trading-212-client
````

---

## Configuration

Set your Trading 212 API key and environment as environment variables:

```bash
export T212_API_KEY=123_YOUR_API_KEY
export T212_ENVIRONMENT=live   # or demo
```

---

## Usage

### AsyncTrading212Client

This client uses `aiohttp` for asynchronous requests.

```python
from t212 import AsyncTrading212Client
import asyncio

async def main():
    client = AsyncTrading212Client()

    # Fetch account balance
    cash = await client.fetch_account_cash()
    print(cash.model_dump(mode="json"))

    # Fetch exchanges
    exchanges = await client.exchange_list()
    print(exchanges.model_dump(mode="json"))

    await client.close_client()

asyncio.run(main())
```

> ✅ Use `await` inside an async function
> ✅ Always close the client when finished (`close_client()`)

---

### Trading212Client

This client uses `requests` for synchronous requests.

```python
from t212 import Trading212Client

client = Trading212Client()

# Fetch account balance
cash = client.fetch_account_cash()
print(cash.model_dump(mode="json"))

# Fetch exchanges
exchanges = client.exchange_list()
print(exchanges.model_dump(mode="json"))
```

---

## Features

* ✅ Fully typed responses (using Pydantic models)
* ✅ Both sync & async client implementations
* ✅ Easy environment setup via env vars
* 🚧 Work in progress (POST endpoints not yet implemented)

---

## Roadmap

* [x] All GET endpoints implemented for async client
* [ ] All POST endpoints implemented for async client
* [x] All GET endpoints implemented for sync client
* [ ] All POST endpoints implemented for sync client
* [x] Deploy on PyPI
* [ ] Add unit tests & CI pipeline
* [ ] Add usage examples for POST endpoints (when available)

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you’d like to help improve the project.

---

## Disclaimer

This library is **unofficial** and not affiliated with Trading 212. Use at your own risk. Trading involves risk of financial loss.

