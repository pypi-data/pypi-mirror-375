import logging
from typing import Dict, Any, List
from .fetcher import MutualFundFetcher

logger = logging.getLogger(__name__)

class MutualFundAnalyzer:
    def __init__(self, symbols: List[str], no_cache: bool = False):
        self.symbols = symbols
        self.fetcher = MutualFundFetcher(no_cache=no_cache)
        self.fund_data = {}

    def analyze(self) -> List[Dict[str, Any]]:
        """Fetch and analyze data for all mutual fund symbols."""
        results = []
        for symbol in self.symbols:
            self.fund_data = self.fetcher.fetch_fund_data(symbol)
            if not self.fund_data:
                analysis = {"error": f"No data found for {symbol}."}
            else:
                analysis = {
                    'profile': self._analyze_profile(),
                    'top_holdings': self._analyze_top_holdings(),
                    'sector_weightings': self._analyze_sector_weightings(),
                    'performance': self._analyze_performance(),
                }
            analysis['ticker'] = symbol
            results.append(analysis)
        return results

    def _analyze_profile(self) -> Dict[str, Any]:
        """Extract key details from the fund profile."""
        profile = self.fund_data.get('profile', {})
        summary = self.fund_data.get('summary', {})

        if not profile or not isinstance(profile, dict):
            return {}

        # Safely access nested dictionary for expense ratio
        fees_expenses = profile.get('feesExpensesInvestment', {})
        expense_ratio = fees_expenses.get('annualReportExpenseRatio') if isinstance(fees_expenses, dict) else None

        return {
            'name': profile.get('legalName'),
            'family': profile.get('family'),
            'category': profile.get('categoryName'),
            'aum': summary.get('totalAssets'),
            'expense_ratio': expense_ratio,
        }

    def _analyze_top_holdings(self) -> Dict[str, Any]:
        """Format top holdings data."""
        top_holdings = self.fund_data.get('top_holdings', [])
        if not top_holdings or not isinstance(top_holdings, list):
            return {}

        return {
            'holdings': top_holdings,
        }

    def _analyze_sector_weightings(self) -> Dict[str, Any]:
        """Format sector weightings data."""
        sector_weightings_data = self.fund_data.get('sector_weightings', {})
        if not sector_weightings_data or not isinstance(sector_weightings_data, dict):
            return {}

        # Data is like {'TICKER': {'Sector1': weight1, ...}}. Extract inner dict.
        inner_dict = next(iter(sector_weightings_data.values()), {})

        return {
            'sectors': inner_dict,
        }

    def _analyze_performance(self) -> Dict[str, Any]:
        """Extract key performance metrics."""
        performance = self.fund_data.get('performance', {})
        if not performance or not isinstance(performance, dict):
            return {}

        return {
            'ytd_return': performance.get('ytdReturn', {}).get('raw'),
            'beta': performance.get('beta3Year', {}).get('raw'),
            'sharpe_ratio': performance.get('sharpeRatio3Year', {}).get('raw'),
            'annual_returns': performance.get('annualTotalReturns', {}).get('returns', []),
        }
