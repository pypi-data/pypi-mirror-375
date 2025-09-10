"""
Mutual Fund Data Fetcher

This module handles fetching and caching mutual fund data from the mfapi.in API.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from ..config.settings import get_settings
from ..config.constants import APIConfig

logger = logging.getLogger(__name__)


class MutualFundFetcher:
    """Fetches and caches mutual fund data from the mfapi.in API."""

    def __init__(self, cache_dir: Optional[Path] = None):
        settings = get_settings()
        if cache_dir is None:
            self.cache_dir = settings.DATA_DIR / "cache" / "mutual_funds"
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        api_config = APIConfig.MF_API
        self.base_url = api_config["base_url"]
        self.timeout = api_config["timeout"]

        self.fund_list_cache_file = self.cache_dir / "mutual_funds_list.json"
        self.fund_details_cache_dir = self.cache_dir / "mutual_fund_details"
        self.fund_details_cache_dir.mkdir(exist_ok=True)

    def _is_cache_valid(self, cache_file: Path, max_age_hours: int) -> bool:
        """Check if a cache file is valid based on its age."""
        if not cache_file.exists():
            return False
        try:
            file_mod_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            return (datetime.now() - file_mod_time) < timedelta(hours=max_age_hours)
        except (OSError, ValueError):
            return False

    def get_fund_list(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetches the list of all mutual funds from mfapi.in, using a daily cache."""
        if not force_refresh and self._is_cache_valid(self.fund_list_cache_file, 24):
            logger.info("Loading mutual fund list from cache.")
            try:
                with open(self.fund_list_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure data is a list of dictionaries
                    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                        return data
                    else:
                        logger.warning("Cache data is not in the expected format (list of dicts). Refetching.")
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Error reading cache file {self.fund_list_cache_file}: {e}")

        logger.info("Fetching fresh mutual fund list from mfapi.in API.")
        try:
            response = requests.get(f"{self.base_url}/mf", timeout=self.timeout)
            response.raise_for_status()
            fund_list = response.json()

            if not isinstance(fund_list, list):
                logger.error(f"API returned unexpected data format: {type(fund_list)}")
                return []

            with open(self.fund_list_cache_file, 'w', encoding='utf-8') as f:
                json.dump(fund_list, f, indent=2)
            logger.info(f"Successfully fetched and cached {len(fund_list)} mutual funds.")
            return fund_list
        except requests.RequestException as e:
            logger.error(f"Failed to fetch mutual fund list: {e}")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from API response.")

        if self.fund_list_cache_file.exists():
            logger.warning("Returning stale fund list from cache as a fallback.")
            try:
                with open(self.fund_list_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def find_fund_by_name(self, fund_name: str) -> Optional[Dict[str, Any]]:
        """Finds a mutual fund by its name using a partial, case-insensitive match."""
        fund_list = self.get_fund_list()
        if not fund_list:
            return None

        search_term = fund_name.strip().lower()
        # First, try for an exact match
        for fund in fund_list:
            if fund.get('schemeName', '').strip().lower() == search_term:
                logger.info(f"Found exact match for '{fund_name}'.")
                return fund

        # If no exact match, try for a partial match
        for fund in fund_list:
            if search_term in fund.get('schemeName', '').strip().lower():
                logger.info(f"Found partial match for '{fund_name}': {fund.get('schemeName')}")
                return fund
        
        logger.warning(f"Could not find any fund matching '{fund_name}'.")
        return None

    def get_fund_details(self, scheme_code: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Fetches detailed information for a specific mutual fund, with 6-hour caching."""
        cache_file = self.fund_details_cache_dir / f"{scheme_code}.json"
        if not force_refresh and self._is_cache_valid(cache_file, 6):
            logger.info(f"Loading details for fund {scheme_code} from cache.")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Error reading cache file {cache_file}: {e}")

        logger.info(f"Fetching fresh details for fund {scheme_code} from API.")
        try:
            url = f"{self.base_url}/mf/{scheme_code}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            fund_details = response.json()
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(fund_details, f, indent=2)
            logger.info(f"Successfully fetched and cached details for fund {scheme_code}.")
            return fund_details
        except requests.RequestException as e:
            logger.error(f"Failed to fetch details for fund {scheme_code}: {e}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from API response for {scheme_code}.")

        if cache_file.exists():
            logger.warning(f"Returning stale details for fund {scheme_code} from cache.")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return None
