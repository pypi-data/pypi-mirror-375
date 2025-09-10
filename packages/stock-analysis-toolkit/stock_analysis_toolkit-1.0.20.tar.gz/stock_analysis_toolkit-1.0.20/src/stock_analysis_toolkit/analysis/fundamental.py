"""
Fundamental analysis module for stock data.
"""

from typing import Dict, Any
import yfinance as yf
import logging

logger = logging.getLogger(__name__)


def get_company_info(symbol: str) -> Dict[str, Any]:
    """
    Get fundamental information about a company.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Dictionary containing company information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or info.get('marketCap') is None or info.get('marketCap') == 0:
            logger.warning(f"No fundamental info found for {symbol}. Response: {info}")
            return {}

        logger.debug(f"Raw yfinance info for {symbol}: {info}")

        return {
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "profit_margins": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsQuarterlyGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "return_on_equity": info.get("returnOnEquity"),
            "beta": info.get("beta"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            # Add other keys that might be used in calculate_fundamental_metrics
            "enterpriseValue": info.get("enterpriseValue"),
            "forwardPE": info.get("forwardPE"),
            "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
            "returnOnAssets": info.get("returnOnAssets"),
            "totalDebt": info.get("totalDebt"),
            "currentRatio": info.get("currentRatio"),
            "quickRatio": info.get("quickRatio"),
            "payoutRatio": info.get("payoutRatio"),
            "dividendRate": info.get("dividendRate"),
        }
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}", exc_info=True)
        return {}


def calculate_fundamental_metrics(symbol: str) -> Dict[str, Any]:
    """
    Calculate fundamental analysis metrics for a stock.

    Args:
        symbol: Stock symbol (e.g., 'AAPL')

    Returns:
        Dictionary containing fundamental metrics
    """
    logger.debug(f"Calculating fundamental metrics for {symbol}...")
    try:
        # Get company info
        company_info = get_company_info(symbol)

        if not company_info:
            logger.warning(f"No company info found for {symbol}, cannot calculate metrics.")
            return {}

        # Flatten the metrics into a single dictionary
        metrics = {
            # Valuation
            "pe_ratio": company_info.get("pe_ratio"),
            "pb_ratio": company_info.get("pb_ratio"),
            "market_cap": company_info.get("market_cap"),
            "enterprise_value": company_info.get("enterpriseValue"),
            "forward_pe": company_info.get("forwardPE"),
            "price_to_sales": company_info.get("priceToSalesTrailing12Months"),

            # Profitability
            "profit_margins": company_info.get("profit_margins"),
            "return_on_equity": company_info.get("return_on_equity"),
            "return_on_assets": company_info.get("returnOnAssets"),

            # Growth
            "revenue_growth": company_info.get("revenue_growth"),
            "earnings_growth": company_info.get("earnings_growth"),

            # Financial Health
            "debt_to_equity": company_info.get("debt_to_equity"),
            "total_debt": company_info.get("totalDebt"),
            "current_ratio": company_info.get("currentRatio"),
            "quick_ratio": company_info.get("quickRatio"),

            # Dividends
            "dividend_yield": company_info.get("dividend_yield"),
            "payout_ratio": company_info.get("payoutRatio"),
            "dividend_rate": company_info.get("dividendRate"),
        }

        # Filter out None values to keep the dictionary clean
        final_metrics = {k: v for k, v in metrics.items() if v is not None}
        logger.debug(f"Calculated {len(final_metrics)} fundamental metrics for {symbol}: {final_metrics}")
        return final_metrics

    except Exception as e:
        logger.error(f"Error calculating fundamental metrics for {symbol}: {e}", exc_info=True)
        return {}
