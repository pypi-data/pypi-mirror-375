"""
Mutual Fund Analysis Module

This module provides comprehensive analysis for mutual funds including
performance metrics, risk analysis, and portfolio composition.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..data.mutual_fund_fetcher import MutualFundFetcher

logger = logging.getLogger(__name__)


class MutualFundAnalyzer:
    """Comprehensive mutual fund analysis and reporting."""

    def __init__(self, cache_dir: str = "cache/mutual_funds"):
        self.fetcher = MutualFundFetcher(cache_dir)
        self.chart_dir = Path("temp_charts")
        self.chart_dir.mkdir(exist_ok=True)

    def analyze_fund(self, fund_name: str) -> Optional[Dict[str, Any]]:
        """Analyzes a mutual fund by its name."""
        fund_info = self.fetcher.find_fund_by_name(fund_name)
        if not fund_info:
            logger.error(f"Mutual fund '{fund_name}' not found.")
            return None
        
        scheme_code = fund_info.get('schemeCode')
        if not scheme_code:
            logger.error(f"'schemeCode' not found for fund: {fund_name}")
            return None
            
        return self.analyze_fund_by_code(scheme_code)

    def analyze_fund_by_code(self, scheme_code: str) -> Optional[Dict[str, Any]]:
        """Analyzes a mutual fund by its scheme code."""
        logger.info(f"Analyzing fund with code: {scheme_code}")
        fund_details = self.fetcher.get_fund_details(scheme_code)
        if not fund_details or 'meta' not in fund_details:
            logger.error(f"Failed to fetch details for fund {scheme_code}.")
            return None
        
        fund_info = {
            'scheme_code': scheme_code,
            'name': fund_details['meta'].get('scheme_name', f"Fund {scheme_code}")
        }

        nav_df = self._prepare_nav_dataframe(fund_details.get('data', []))
        if nav_df.empty:
            logger.warning(f"Could not prepare NAV DataFrame for {scheme_code}.")
            return None

        # --- Comprehensive Analysis --- #
        performance = self._calculate_performance_metrics(nav_df)
        risk = self._calculate_risk_metrics(nav_df)
        technicals, nav_df_with_technicals = self._calculate_technical_indicators(nav_df)
        analysis_results = {
            'fund_info': fund_info,
            'fund_details': fund_details,
            'nav_data': nav_df_with_technicals,
            'performance_metrics': performance,
            'risk_metrics': risk,
            'technical_indicators': technicals,
            'portfolio_composition': {},
            'chart_paths': self._generate_all_charts(fund_info, nav_df_with_technicals, {})
        }
        return analysis_results

    def _prepare_nav_dataframe(self, nav_history: List[Dict[str, Any]]) -> pd.DataFrame:
        if not nav_history: return pd.DataFrame()
        df = pd.DataFrame(nav_history)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        
        # Log rows where 'nav' is not a valid number before coercing
        invalid_navs = df[~df['nav'].str.match(r'^-?\d*\.?\d+$', na=True)]
        for index, row in invalid_navs.iterrows():
            logger.warning(f"Invalid NAV value '{row['nav']}' on date {row['date'].strftime('%Y-%m-%d')}")

        df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
        return df.dropna(subset=['nav']).sort_values('date').reset_index(drop=True)

    def _calculate_performance_metrics(self, nav_df: pd.DataFrame) -> Dict[str, Any]:
        if nav_df.empty or len(nav_df) < 2: return {}
        calculated_metrics = {}
        end_nav, end_date = nav_df.iloc[-1]['nav'], nav_df.iloc[-1]['date']
        for name, days in {'1Y': 365, '3Y': 1095, '5Y': 1825, '10Y': 3652}.items():
            start_date = end_date - pd.Timedelta(days=days)
            past_nav_df = nav_df[nav_df['date'] <= start_date]
            if not past_nav_df.empty:
                start_nav = past_nav_df.iloc[-1]['nav']
                actual_start_date = past_nav_df.iloc[-1]['date']
                if start_nav > 0:
                    years = (end_date - actual_start_date).days / 365.25
                    if years > 0:
                        cagr = (((end_nav / start_nav) ** (1 / years)) - 1) * 100
                        calculated_metrics[f'cagr_{name.lower()}'] = round(cagr, 2)
        return calculated_metrics

    def _calculate_risk_metrics(self, nav_df: pd.DataFrame) -> Dict[str, Any]:
        if len(nav_df) < 30: return {}
        nav_df['daily_return'] = nav_df['nav'].pct_change()
        daily_returns = nav_df['daily_return'].dropna()
        if daily_returns.empty: return {}

        # Downside returns for Sortino
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if not downside_returns.empty else 0

        # Max Drawdown
        cumulative_returns = (1 + daily_returns).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak

        # Metrics calculation
        annual_volatility = daily_returns.std() * np.sqrt(252)
        annual_return = daily_returns.mean() * 252
        risk_free_rate = 0.06  # Assumption

        return {
            'annual_volatility': round(annual_volatility * 100, 2),
            'sharpe_ratio': round((annual_return - risk_free_rate) / annual_volatility, 2) if annual_volatility > 0 else 0,
            'sortino_ratio': round((annual_return - risk_free_rate) / downside_std, 2) if downside_std > 0 else 0,
            'max_drawdown': round(drawdown.min() * 100, 2) if not drawdown.empty else 0
        }

    def _calculate_technical_indicators(self, nav_df: pd.DataFrame) -> Tuple[Dict[str, Any], pd.DataFrame]:
        if nav_df.empty: return {}, nav_df
        indicators = {}
        df = nav_df.copy()

        # RSI
        if len(df) > 14:
            delta = df['nav'].diff()
            gain = (delta.where(delta > 0, 0)).ewm(com=13, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(com=13, adjust=False).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            indicators['rsi'] = round(df['rsi'].iloc[-1], 2) if not pd.isna(df['rsi'].iloc[-1]) else None

        # Standard Deviation (20-day rolling)
        if len(df) >= 20:
            df['20d_std'] = df['nav'].rolling(window=20).std()
            indicators['20d_std'] = round(df['20d_std'].iloc[-1], 2) if not pd.isna(df['20d_std'].iloc[-1]) else None
            
            # Bollinger Bands for Support/Resistance
            df['20d_ma'] = df['nav'].rolling(window=20).mean()
            df['upper_band'] = df['20d_ma'] + (df['20d_std'] * 2)
            df['lower_band'] = df['20d_ma'] - (df['20d_std'] * 2)
            
            # Add to indicators
            indicators['20d_ma'] = round(df['20d_ma'].iloc[-1], 2) if not pd.isna(df['20d_ma'].iloc[-1]) else None
            indicators['upper_band'] = round(df['upper_band'].iloc[-1], 2) if not pd.isna(df['upper_band'].iloc[-1]) else None
            indicators['lower_band'] = round(df['lower_band'].iloc[-1], 2) if not pd.isna(df['lower_band'].iloc[-1]) else None

        # Moving Averages & Crosses
        if len(df) >= 50:
            df['ma_50'] = df['nav'].rolling(window=50).mean()
            indicators['ma_50'] = df['ma_50'].iloc[-1]
        if len(df) >= 200:
            df['ma_200'] = df['nav'].rolling(window=200).mean()
            indicators['ma_200'] = df['ma_200'].iloc[-1]
            indicators['golden_cross'] = df['ma_50'].iloc[-2] < df['ma_200'].iloc[-2] and df['ma_50'].iloc[-1] > df['ma_200'].iloc[-1]
            indicators['death_cross'] = df['ma_50'].iloc[-2] > df['ma_200'].iloc[-2] and df['ma_50'].iloc[-1] < df['ma_200'].iloc[-1]

        # Support and Resistance (using recent pivot points)
        if len(df) >= 30:
            # Simple support/resistance using recent lows/highs
            lookback = min(30, len(df) // 3)  # Adjust lookback based on data length
            df['high'] = df['nav'].rolling(window=lookback).max()
            df['low'] = df['nav'].rolling(window=lookback).min()
            
            # Recent support and resistance levels
            resistance = df['high'].iloc[-lookback:].max()
            support = df['low'].iloc[-lookback:].min()
            
            indicators['resistance'] = round(resistance, 2)
            indicators['support'] = round(support, 2)
            indicators['distance_to_resistance_pct'] = round(((resistance - df['nav'].iloc[-1]) / df['nav'].iloc[-1]) * 100, 2) if resistance > 0 else None
            indicators['distance_to_support_pct'] = round(((df['nav'].iloc[-1] - support) / support) * 100, 2) if support > 0 else None

        return indicators, df

    def _analyze_portfolio_composition(self, fund_details: Dict[str, Any]) -> Dict[str, Any]:
        # This data is not available from the current API, so return an empty dict.
        return {}

    def _generate_all_charts(self, fund_info: Dict, nav_df: pd.DataFrame, portfolio: Dict) -> Dict[str, str]:
        fund_name, scheme_code = fund_info.get('name', 'Unknown'), fund_info.get('scheme_code', 'NA')
        paths = {}

        # NAV Performance Chart
        if len(nav_df) > 30:
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(go.Scatter(x=nav_df['date'], y=nav_df['nav'], mode='lines', name='NAV'))
            if 'ma_50' in nav_df: fig.add_trace(go.Scatter(x=nav_df['date'], y=nav_df['ma_50'], mode='lines', name='50-Day MA'))
            if 'ma_200' in nav_df: fig.add_trace(go.Scatter(x=nav_df['date'], y=nav_df['ma_200'], mode='lines', name='200-Day MA'))
            fig.update_layout(title=f"{fund_name} - NAV Performance", height=500)

            # Always generate PNG for consistency
            png_path = self.chart_dir / f"mf_nav_performance_{scheme_code}.png"
            try:
                fig.write_image(png_path, engine="kaleido")
                logger.info(f"Saved PNG chart to {png_path}")
                paths['nav_performance_chart'] = str(png_path)
            except Exception as e:
                logger.error(f"Failed to save PNG chart: {e}", exc_info=True)

        # Portfolio allocation charts are disabled as the data is not available from the API.
        return paths

    def generate_fund_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        if not analysis: return {}

        fund_info = analysis.get('fund_info', {})
        fund_details = analysis.get('fund_details', {})
        meta = fund_details.get('meta', {})
        nav_df = analysis.get('nav_data', pd.DataFrame())

        summary = {
            'name': meta.get('scheme_name', fund_info.get('name', 'N/A')),
            'scheme_code': fund_info.get('scheme_code', 'N/A'),
            'fund_house': meta.get('fund_house', 'N/A'),
            'scheme_category': meta.get('scheme_category', 'N/A'),
            'aum': meta.get('aum', 'N/A'),
            'expense_ratio': meta.get('expense_ratio', 'N/A'),
            'latest_nav': nav_df.iloc[-1]['nav'] if not nav_df.empty else 'N/A',
            'nav_date': nav_df.iloc[-1]['date'].strftime('%d-%b-%Y') if not nav_df.empty else 'N/A',
            **analysis.get('performance_metrics', {}),
            **analysis.get('risk_metrics', {}),
            **analysis.get('technical_indicators', {}),
            'portfolio_composition': analysis.get('portfolio_composition', {}),
            'chart_paths': analysis.get('chart_paths', {})
        }
        return summary

    def validate_fund_name(self, fund_name: str) -> Tuple[bool, Optional[str]]:
        if self.fetcher.find_fund_by_name(fund_name):
            return True, None
        return False, f"Mutual fund '{fund_name}' not found. Please verify the name at stock.indianapi.in."
