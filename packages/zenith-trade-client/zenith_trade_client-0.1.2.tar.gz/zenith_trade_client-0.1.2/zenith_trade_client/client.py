import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

class ZenithTradeClient:
    def __init__(self, mode: str = None, tailscale_host: str = "teesta", port: int = 8000):
        """
        Python client for Zenith-Trade backend.
        :param mode: 'localhost' or any other mode to choose base URL
        :param tailscale_host: hostname for non-localhost mode
        :param port: backend port
        """
        if mode is None or mode == "localhost":
            base_url = f"http://localhost:{port}"
        else:
            base_url = f"http://{tailscale_host}:{port}"
        
        self.base_url = base_url.rstrip("/")

    # -------------------------------
    # Input validation
    # -------------------------------
    @staticmethod
    def _validate_dates(from_date: str, to_date: str):
        """Validate that dates are in YYYY-MM-DD format and from_date <= to_date."""
        try:
            start = datetime.strptime(from_date, "%Y-%m-%d")
            end = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Dates must be in 'YYYY-MM-DD' format")
        if end < start:
            raise ValueError("to_date must be greater than or equal to from_date")

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
        """Get exchange metadata. If datasource provided, return datasource-specific info."""
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
        symbols: List[str], 
        data_types: List[str], 
        from_date: str, 
        to_date: str
    ) -> Dict[str, Any]:
        """
        symbols: list of strings, e.g., ["BTCUSDT", "ETHUSDT"]
        data_types: list of strings, e.g., ["book_snapshot_5", "trades"]
        from_date, to_date: 'YYYY-MM-DD' format
        Raises ValueError if dates invalid
        """
        # Validate dates first
        self._validate_dates(from_date, to_date)

        url = f"{self.base_url}/data"
        payload = {
            "exchange": exchange,
            "symbols": symbols,
            "data_types": data_types,
            "from_date": from_date,
            "to_date": to_date
        }
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
