import os
import pickle
import time
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from yahooquery import Ticker

class MutualFundFetcher:
    def __init__(self, cache_dir="cache/mutual_funds", no_cache: bool = False):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = 20 * 3600  # 20 hours in seconds
        self.no_cache = no_cache

    def _get_cache_path(self, ticker_symbol: str) -> Path:
        """Generate the cache file path for a given ticker symbol."""
        return self.cache_dir / f"{ticker_symbol}.pkl"

    def fetch_fund_data(self, ticker_symbol: str) -> Optional[Dict]:
        """Fetch detailed mutual fund data using yahooquery, with caching."""
        cache_path = self._get_cache_path(ticker_symbol)

        # Check if a valid cache file exists and caching is enabled
        if not self.no_cache and cache_path.exists():
            file_mod_time = cache_path.stat().st_mtime
            if (time.time() - file_mod_time) < self.cache_expiry:
                print(f"Loading cached data for {ticker_symbol}")
                with open(cache_path, "rb") as f:
                    return pickle.load(f)

        # Fetch data from yahooquery if cache is invalid or doesn't exist
        print(f"Fetching fresh data for {ticker_symbol}")
        try:
            ticker = Ticker(ticker_symbol)
            profile = ticker.fund_profile
            top_holdings = ticker.fund_top_holdings
            sector_weightings = ticker.fund_sector_weightings
            summary = ticker.summary_detail
            performance = ticker.fund_performance

            data = {
                'profile': profile.get(ticker_symbol) if isinstance(profile, dict) else {},
                'top_holdings': top_holdings.to_dict('records') if isinstance(top_holdings, pd.DataFrame) else {},
                'sector_weightings': sector_weightings.to_dict() if isinstance(sector_weightings, pd.DataFrame) else {},
                'summary': summary.get(ticker_symbol) if isinstance(summary, dict) else {},
                'performance': performance.get(ticker_symbol) if isinstance(performance, dict) else {},
            }

            # Save the fetched data to cache
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)

            return data
        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            return None
