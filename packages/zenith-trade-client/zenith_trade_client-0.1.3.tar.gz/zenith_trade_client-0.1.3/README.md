# Zenith Trade Client

A simple Python client to interact with the **Zenith-Trade FastAPI backend**.

## Installation
``` bash
pip install zenith-trade-client
```

## 🚀 Usage

### Import the client

``` python
from zenith_trade_client import ZenithTradeClient
# default: mode="localhost", port=8000 (works on in-house server)
client = ZenithTradeClient()

# OR: Remote via Tailscale hostname
client = ZenithTradeClient(mode="tailscale", tailscale_host="", port=8000)
```

### List All Exchanges

``` python
exchanges = client.list_exchanges()
print(exchanges)
```

### Get Exchange Info

``` python
info = client.get_exchange_info("lmax_futures")
print(info)
```

### Check Data Availability

``` python
availability = client.check_data_availability(
    exchange="binance",
    symbols=["BTCUSDT", "ETHUSDT"],
    data_types=["trades", "book_snapshot_5"],
    from_date="2025-09-01",
    to_date="2025-09-08"
)
print(availability)
```