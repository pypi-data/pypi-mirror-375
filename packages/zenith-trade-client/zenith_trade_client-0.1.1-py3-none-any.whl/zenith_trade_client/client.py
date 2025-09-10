import requests
from typing import List, Dict, Any, Optional

class ZenithTradeClient:
    def __init__(self, mode: str = None, tailscale_host: str = "teesta", port: int = 8000):
        """
        Python client for Zenith-Trade backend.
        :param base_url: URL where FastAPI service is hosted
        """
        
        if mode is None or mode == "localhost":
            base_url = f"http://localhost:{port}"
        else:
            base_url = f"http://{tailscale_host}:{port}"
        
        self.base_url = base_url.rstrip("/")

    # -------------------------------
    # Exchange APIs
    # -------------------------------
    def list_exchanges(self) -> Dict[str, Any]:
        """Get all available exchanges with metadata."""
        url = f"{self.base_url}/exchanges"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_exchange_info(self, exchange: str, datasource: str = None) -> Dict[str, Any]:
        """
        Get exchange metadata.
        - If datasource is None → return full exchange info
        - If datasource provided → return datasource-specific info
        """
        if datasource is None:
            url = f"{self.base_url}/exchanges/{exchange}"
        else:
            url = f"{self.base_url}/exchanges/{exchange}/{datasource}"

        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # -------------------------------
    # Data APIs
    # -------------------------------
    def check_data_availability(
        self, 
        exchange: str, 
        symbol: str, 
        data_type: str, 
        from_date: str, 
        to_date: str
    ) -> Dict[str, Any]:
        """
        Check whether requested data is in ClickHouse, Storage, or needs to be fetched from Tardis.
        """
        url = f"{self.base_url}/data"
        payload = {
            "exchange": exchange,
            "symbol": symbol,
            "data_type": data_type,
            "from_date": from_date,
            "to_date": to_date
        }
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
