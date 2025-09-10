import logging
import requests
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarketStackFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.marketstack.com/v1/"

    def get_stock_data(self, symbol: str, days: int = 365):
        params = {
            'access_key': self.api_key,
            'symbols': symbol,
            'date_from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            'limit': 1000  # Max limit
        }
        try:
            response = requests.get(f"{self.base_url}eod", params=params)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_code = data.get("error", {}).get("code")
                if error_code == "invalid_access_key":
                    logger.warning("MarketStack API error: you have not supplied a valid API Access Key.")
                else:
                    logger.warning(f"MarketStack API error for {symbol}: {data['error'].get('message')}")
                return None

            if 'data' not in data or not data['data']:
                logger.warning(f"No data returned from MarketStack for {symbol}")
                return None

            df = pd.DataFrame(data['data'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from MarketStack for {symbol}: {e}")
            return None
