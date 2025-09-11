"""
Technical Analysis Module

This module provides functions for calculating various technical indicators
and performing technical analysis on stock data.
"""

import logging
from typing import List, Dict

import numpy as np
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("technical_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TechnicalAnalysis:
    """Class for performing technical analysis on stock data."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the TechnicalAnalysis with stock data.

        Args:
            data: DataFrame with stock data containing columns:
                'open', 'high', 'low', 'close', 'volume'
        """
        self.data = data.copy()
        self.data.columns = [col.lower() for col in self.data.columns]
        self._validate_data()

    def _validate_data(self):
        """Validate that required columns are present in the data."""
        required_columns = ["open", "high", "low", "close", "volume"]
        missing_columns = [
            col for col in required_columns if col not in self.data.columns
        ]

        if missing_columns:
            missing_cols = ", ".join(missing_columns)
            raise ValueError(f"Missing required columns: {missing_cols}")

    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).

        Args:
            window: RSI period (default: 14)

        Returns:
            Series containing RSI values
        """
        close_prices = self.data["close"]
        delta = close_prices.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_moving_averages(self, windows: List[int] = None) -> pd.DataFrame:
        """
                Calculate various moving averages.

                Args:
        windows: List of window sizes for moving averages
                        (default: [20, 50, 200])

                Returns:
                    DataFrame with moving average columns added
        """
        if windows is None:
            windows = [20, 50, 200]

        result = self.data.copy()
        close_prices = result["close"]

        for window in windows:
            col_name = f"ma_{window}"
            result[col_name] = close_prices.rolling(window=window).mean()

        return result

    def calculate_moving_average(self, window: int = 20) -> pd.Series:
        """
        Calculate a simple moving average.

        Args:
            window: Window size for the moving average (default: 20)

        Returns:
            Series containing the moving average values
        """
        return self.data["close"].rolling(window=window).mean()

    def calculate_bollinger_bands(self, window: int = 20, num_std: float = 2) -> tuple:
        """
        Calculate Bollinger Bands.

        Args:
            window: Moving average window (default: 20)
            num_std: Number of standard deviations (default: 2)

        Returns:
            Tuple containing (upper_band, middle_band, lower_band)
        """
        close_prices = self.data["close"]

        # Calculate middle band (SMA)
        middle_band = close_prices.rolling(window=window).mean()
        std = close_prices.rolling(window=window).std()

        # Calculate upper and lower bands
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)

        return upper_band, middle_band, lower_band

    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """
        Calculate Moving Average Convergence Divergence (MACD).

        Args:
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)

        Returns:
            Tuple containing (macd_line, signal_line, macd_hist)
        """
        close_prices = self.data["close"]

        # Calculate EMAs
        fast_ema = close_prices.ewm(span=fast, adjust=False).mean()
        slow_ema = close_prices.ewm(span=slow, adjust=False).mean()

        # Calculate MACD line and signal line
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Calculate histogram
        macd_hist = macd_line - signal_line

        return macd_line, signal_line, macd_hist

    def calculate_volume_indicators(self, window: int = 20) -> pd.DataFrame:
        """
        Calculate volume-based indicators.

        Args:
            window: Window for volume moving average (default: 20)

        Returns:
            DataFrame with volume indicators added
        """
        result = self.data.copy()
        volume = result["volume"]

        # Volume moving average
        result["volume_ma"] = volume.rolling(window=window).mean()

        # Volume rate of change
        result["volume_roc"] = volume.pct_change(periods=window) * 100

        # On-Balance Volume (OBV)
        close = result["close"]
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        result["obv"] = obv

        return result

    def calculate_volatility(self, window: int = 20) -> pd.DataFrame:
        """
        Calculate volatility indicators.

        Args:
            window: Window for volatility calculation (default: 20)

        Returns:
            DataFrame with volatility indicators added
        """
        result = self.data.copy()
        close = result["close"]

        # Daily returns
        returns = close.pct_change()

        # Historical volatility (annualized)
        result["volatility"] = returns.rolling(window=window).std() * np.sqrt(252) * 100

        # Average True Range (ATR)
        high = result["high"]
        low = result["low"]

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        result["atr"] = tr.rolling(window=window).mean()

        return result

    def calculate_momentum_indicators(self) -> pd.DataFrame:
        """
        Calculate momentum indicators.

        Returns:
            DataFrame with momentum indicators added
        """
        result = self.data.copy()
        close = result["close"]

        # Rate of Change (ROC)
        result["roc"] = close.pct_change(periods=14) * 100

        # Stochastic Oscillator
        high_14 = result["high"].rolling(window=14).max()
        low_14 = result["low"].rolling(window=14).min()

        k = 100 * ((close - low_14) / (high_14 - low_14))
        d = k.rolling(window=3).mean()

        result["stoch_k"] = k
        result["stoch_d"] = d

        # Williams %R
        highest_high = result["high"].rolling(window=14).max()
        lowest_low = result["low"].rolling(window=14).min()
        price_diff = highest_high - result["close"]
        range_diff = highest_high - lowest_low
        result["williams_r"] = -100 * price_diff / range_diff

        return result

    def calculate_atr(self, window: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).

        Args:
            window: Number of periods for ATR calculation (default: 14)

        Returns:
            Series containing ATR values
        """
        try:
            high = self.data["high"]
            low = self.data["low"]
            close = self.data["close"]

            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Calculate ATR
            atr = tr.rolling(window=window).mean()
            return atr

        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(index=self.data.index, dtype=float)

    def calculate_obv(self) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV).

        Returns:
            Series containing OBV values
        """
        try:
            close = self.data["close"]
            volume = self.data["volume"]

            # Calculate daily price change
            price_change = close.diff()

            # Initialize OBV with first value as 0
            obv = pd.Series(0, index=self.data.index)

            # Calculate OBV
            for i in range(1, len(obv)):
                if price_change[i] > 0:
                    obv[i] = obv[i - 1] + volume[i]
                elif price_change[i] < 0:
                    obv[i] = obv[i - 1] - volume[i]
                else:
                    obv[i] = obv[i - 1]

            return obv

        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return pd.Series(index=self.data.index, dtype=float)

    def calculate_adx(self, window: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (ADX).

        Args:
            window: Number of periods for ADX calculation (default: 14)

        Returns:
            Series containing ADX values
        """
        try:
            high = self.data["high"]
            low = self.data["low"]
            close = self.data["close"]

            # Calculate +DM and -DM
            up = high.diff()
            down = low.diff() * -1

            # Initialize DM+ and DM-
            plus_dm = up.copy()
            minus_dm = down.copy()

            # Set conditions for DM+ and DM-
            plus_dm[up <= down] = 0
            minus_dm[down <= up] = 0

            # Calculate True Range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Calculate smoothed TR, +DM, and -DM
            atr = tr.rolling(window=window).mean()
            plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)

            # Calculate DX and ADX
            dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di)).fillna(0)
            adx = dx.rolling(window=window).mean()

            return adx

        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return pd.Series(index=self.data.index, dtype=float)

    def calculate_all_indicators(self) -> pd.DataFrame:
        """
        Calculate all available technical indicators.

        Returns:
            DataFrame with all calculated indicators
        """
        try:
            # Calculate individual indicators
            self.data["rsi"] = self.calculate_rsi()
            (
                self.data["macd"],
                self.data["macd_signal"],
                self.data["macd_hist"],
            ) = self.calculate_macd()
            (
                self.data["bb_upper"],
                self.data["bb_middle"],
                self.data["bb_lower"],
            ) = self.calculate_bollinger_bands()
            self.data["ma_20"] = self.calculate_moving_average(window=20)
            self.data["ma_50"] = self.calculate_moving_average(window=50)
            self.data["ma_200"] = self.calculate_moving_average(window=200)

            # Add new indicators
            self.data["atr"] = self.calculate_atr()
            self.data["obv"] = self.calculate_obv()
            self.data["adx"] = self.calculate_adx()

            logger.info("Successfully calculated all technical indicators")
            return self.data

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return self.data


def calculate_fundamental_metrics(ticker: str) -> Dict[str, float]:
    """
    Calculate fundamental metrics for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.BO')

    Returns:
        Dictionary containing fundamental metrics
    """
    try:
        # Use yfinance to get fundamental data
        stock = yf.Ticker(ticker)
        info = stock.info

        metrics = {
            "pe_ratio": info.get("trailingPE", None),
            "forward_pe": info.get("forwardPE", None),
            "peg_ratio": info.get("pegRatio", None),
            "price_to_book": info.get("priceToBook", None),
            "price_to_sales": info.get("priceToSalesTrailing12Months", None),
            "return_on_equity": (
                info.get("returnOnEquity", None) * 100
                if "returnOnEquity" in info
                else None
            ),
            "debt_to_equity": info.get("debtToEquity", None),
            "current_ratio": info.get("currentRatio", None),
            "dividend_yield": info.get(
                "dividendYield"
            ),  # Keep as decimal (e.g., 0.02 for 2%)
            "beta": info.get("beta", None),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", None),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", None),
            "fifty_day_average": info.get("fiftyDayAverage", None),
            "two_hundred_day_average": info.get("twoHundredDayAverage", None),
            "market_cap": info.get("marketCap", None),
            "enterprise_value": info.get("enterpriseValue", None),
            "trailing_eps": info.get("trailingEps", None),
            "forward_eps": info.get("forwardEps", None),
            "profit_margins": (
                info.get("profitMargins", None) * 100
                if "profitMargins" in info
                else None
            ),
            "operating_margins": (
                info.get("operatingMargins", None) * 100
                if "operatingMargins" in info
                else None
            ),
            "ebitda": info.get("ebitda", None),
            "revenue_growth": (
                info.get("revenueGrowth", None) * 100
                if "revenueGrowth" in info
                else None
            ),
            "earnings_growth": (
                info.get("earningsGrowth", None) * 100
                if "earningsGrowth" in info
                else None
            ),
            "free_cash_flow": info.get("freeCashflow", None),
            "operating_cash_flow": info.get("operatingCashflow", None),
            "total_debt": info.get("totalDebt", None),
            "total_cash": info.get("totalCash", None),
            "shares_outstanding": info.get("sharesOutstanding", None),
            "float_shares": info.get("floatShares", None),
            "held_percent_institutions": (
                info.get("heldPercentInstitutions", None) * 100
                if "heldPercentInstitutions" in info
                else None
            ),
            "short_ratio": info.get("shortRatio", None),
            "short_percent_of_float": (
                info.get("shortPercentOfFloat", None) * 100
                if "shortPercentOfFloat" in info
                else None
            ),
            "book_value": info.get("bookValue", None),
            "enterprise_to_revenue": info.get("enterpriseToRevenue", None),
            "enterprise_to_ebitda": info.get("enterpriseToEbitda", None),
            "earnings_date": info.get("earningsDate", None),
            "ex_dividend_date": info.get("exDividendDate", None),
            "last_dividend_value": info.get("lastDividendValue", None),
            "last_dividend_date": info.get("lastDividendDate", None),
        }

        # Clean up None values
        metrics = {
            k: round(v, 4) if isinstance(v, (int, float)) else v
            for k, v in metrics.items()
        }

        return metrics

    except Exception as e:
        error_msg = (
            f"Error calculating fundamental metrics for {ticker}: " f"{str(e)[:100]}..."
        )
        logger.error(error_msg)
        return {}


if __name__ == "__main__":
    # Fetch sample data
    stock_data = yf.download("RELIANCE.BO", period="1y")

    # Initialize technical analysis
    tech_analysis = TechnicalAnalysis(stock_data)

    # Calculate all indicators
    result = tech_analysis.calculate_all_indicators()

    print("Technical indicators calculated successfully!")
    print(result[["close", "rsi", "ma_20", "ma_50", "ma_200"]].tail())
