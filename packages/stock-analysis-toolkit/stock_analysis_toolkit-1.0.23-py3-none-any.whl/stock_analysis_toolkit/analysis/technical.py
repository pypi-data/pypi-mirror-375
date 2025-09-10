"""
Technical analysis module for stock data.
"""

import logging
import pandas as pd
from typing import Dict, Any


# Configure logger
logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    """Class for performing technical analysis on stock data."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the TechnicalAnalysis with stock data.

        Args:
            data: DataFrame containing stock data with columns like 'Open', 'High', 'Low', 'Close', 'Volume'
        """
        self.data = data
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that the input data has the required columns."""
        required_columns = {"Open", "High", "Low", "Close", "Volume"}
        if not required_columns.issubset(self.data.columns):
            missing = required_columns - set(self.data.columns)
            raise ValueError(f"Input data is missing required columns: {missing}")

    def calculate_sma(self, window: int = 20) -> pd.Series:
        """Calculate Simple Moving Average."""
        return self.data["Close"].rolling(window=window).mean()

    def calculate_ema(self, window: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return self.data["Close"].ewm(span=window, adjust=False).mean()

    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = self.data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(
        self, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, pd.Series]:
        """Calculate Moving Average Convergence Divergence."""
        exp1 = self.data["Close"].ewm(span=fast, adjust=False).mean()
        exp2 = self.data["Close"].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()

        return {"macd": macd, "signal": signal_line, "histogram": macd - signal_line}

    def calculate_bollinger_bands(
        self, window: int = 20, num_std: float = 2
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = self.calculate_sma(window)
        rolling_std = self.data["Close"].rolling(window=window).std()

        return {
            "middle": sma,
            "upper": sma + (rolling_std * num_std),
            "lower": sma - (rolling_std * num_std),
        }

    def calculate_all_indicators(self) -> Dict[str, Any]:
        """Calculate all technical indicators."""
        indicators = {}
        try:
            # Add current price and daily return
            if not self.data.empty and not self.data["Close"].empty:
                # Get the last 5 data points for debugging
                last_5_dates = self.data.index[-5:].strftime('%Y-%m-%d').tolist()
                last_5_closes = self.data["Close"][-5:].tolist()
                logger.debug(f"Last 5 data points - Dates: {last_5_dates}, Closes: {last_5_closes}")
                
                current_close = float(self.data["Close"].iloc[-1])
                indicators["close"] = current_close
                
                # Calculate daily return if we have at least 2 data points
                if len(self.data) >= 2 and not self.data["Close"].isna().any():
                    # Get the last two data points with their dates
                    last_date = self.data.index[-1].strftime('%Y-%m-%d')
                    prev_date = self.data.index[-2].strftime('%Y-%m-%d')
                    prev_close = float(self.data["Close"].iloc[-2])
                    
                    logger.debug(f"Calculating daily return for {last_date}:")
                    logger.debug(f"  Previous date: {prev_date}, Close: {prev_close}")
                    logger.debug(f"  Current date: {last_date}, Close: {current_close}")
                    
                    if prev_close > 0:  # Avoid division by zero
                        daily_return = ((current_close - prev_close) / prev_close) * 100
                        logger.debug(f"  Calculated daily return: {daily_return:.2f}%")
                        
                        # Add a sanity check for extreme values
                        if abs(daily_return) > 20:  # More than 20% move is unusual for most stocks
                            logger.warning(f"  Warning: Unusually large daily return detected: {daily_return:.2f}%")
                            logger.warning(f"  Previous close: {prev_close}, Current close: {current_close}")
                            
                            # If the move is too large, try to find a more recent previous close
                            if len(self.data) > 10:  # If we have more data points
                                prev_close_alt = float(self.data["Close"].iloc[-3])  # Try two days ago
                                daily_return_alt = ((current_close - prev_close_alt) / prev_close_alt) * 100
                                logger.warning(f"  Alternative calculation using previous day: {daily_return_alt:.2f}%")
                                
                                # Use the alternative if it's more reasonable
                                if abs(daily_return_alt) < abs(daily_return) * 0.5:  # If it's significantly smaller
                                    daily_return = daily_return_alt
                                    logger.warning(f"  Using alternative daily return: {daily_return:.2f}%")
                        
                        # Round to 2 decimal places for display
                        indicators["daily_return"] = round(daily_return, 2)
                
            # Moving Averages
            indicators["sma_20"] = self.calculate_sma(20).iloc[-1]
            indicators["sma_50"] = self.calculate_sma(50).iloc[-1]
            indicators["sma_200"] = self.calculate_sma(200).iloc[-1]
            indicators["ema_20"] = self.calculate_ema(20).iloc[-1]
            indicators["ema_50"] = self.calculate_ema(50).iloc[-1]
            
            # RSI
            indicators["rsi"] = self.calculate_rsi().iloc[-1]
            
            # MACD
            macd_results = self.calculate_macd()
            indicators["macd"] = macd_results["macd"].iloc[-1]
            indicators["macd_signal"] = macd_results["signal"].iloc[-1]
            
            # Bollinger Bands
            bollinger_bands = self.calculate_bollinger_bands()
            indicators["bollinger"] = {
                "middle": bollinger_bands["middle"].iloc[-1],
                "upper": bollinger_bands["upper"].iloc[-1],
                "lower": bollinger_bands["lower"].iloc[-1],
            }
            
            # Volume
            indicators["volume"] = self.data["Volume"].iloc[-1]
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error calculating technical indicators: {e}", exc_info=True)
            # Return partial indicators if any were calculated
        return indicators
