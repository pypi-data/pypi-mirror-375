import requests
from typing import List, Dict, Any

def search_symbols(query: str) -> List[Dict[str, Any]]:
    """Searches for Indian mutual funds using the mfapi.in API."""
    try:
        # mfapi.in provides a single endpoint to get all funds.
        # We fetch the whole list and search locally.
        url = "https://api.mfapi.in/mf"
        response = requests.get(url)
        response.raise_for_status()
        all_funds = response.json()

        # Filter the list based on the query (case-insensitive)
        results = []
        query_words = query.lower().split()
        for fund in all_funds:
            scheme_name_lower = fund['schemeName'].lower()
            if all(word in scheme_name_lower for word in query_words):
                results.append({
                    "symbol": fund['schemeCode'],
                    "name": fund['schemeName']
                })
        
        return results

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during symbol search: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
