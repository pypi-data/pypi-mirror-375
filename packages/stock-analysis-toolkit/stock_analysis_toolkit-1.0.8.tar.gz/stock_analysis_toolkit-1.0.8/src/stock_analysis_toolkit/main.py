"""
Stock Analysis Tool

A comprehensive tool for analyzing Indian stocks with technical and
fundamental analysis.
"""

# --- Standard Library Imports ---
import argparse
import base64
import json
import logging
import math
import webbrowser
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# --- Third-Party Imports ---
import numpy as np
import pandas as pd
import pytz
from jinja2 import Environment, PackageLoader, select_autoescape
from rich import print as rprint
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
from rich.traceback import install as install_rich_traceback

# --- Local Application Imports ---
from .analysis.mutual_fund_analyzer import MutualFundAnalyzer
from .config.settings import get_settings
from .core.analyzer import AnalysisResult
from .core.analyzer import StockAnalyzer as CoreAnalyzer
from .data.fetcher import DataFetcher
from .config.settings import get_top_bse_stocks
from .reporting.email_sender import EmailSender
from .visualization.visualizer import StockVisualizer

# --- Early Setup: Logging Configuration ---
settings = get_settings()
LOGS_DIR = settings.LOGS_DIR
REPORTS_DIR = settings.REPORTS_DIR

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "stock_analysis.log"),
        RichHandler(rich_tracebacks=True, markup=True),
    ],
)

logger = logging.getLogger(__name__)

# Set higher log level for other libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.WARNING)

# Install rich traceback for better error messages
install_rich_traceback(show_locals=True)

# Initialize console for rich output
console = Console()

logger.info("Logging configured successfully.")


def ensure_scalar(value, default=None):
    """Ensure the value is a scalar (not a pandas Series or DataFrame)."""
    if isinstance(value, (pd.Series, pd.DataFrame)) and not value.empty:
        return value.iloc[0] if len(value) > 0 else default
    return value if value is not None else default

def safe_format(value, format_str=".2f", default="N/A"):
    """Safely format a value with error handling.

    Args:
        value: The value to format
        format_str: Format string (default: ".2f")
        default: Default value if formatting fails (default: "N/A")

    Returns:
        Formatted string or default value
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return default
    try:
        return format(float(value), format_str)
    except (ValueError, TypeError):
        return str(value)

def get_change_class(change_pct: float) -> Tuple[str, str]:
    """Get CSS class and icon for price change."""
    if change_pct > 0:
        return "positive-change", "↑"
    elif change_pct < 0:
        return "negative-change", "↓"
    return "neutral-change", "→"

# Ensure reports directory exists
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class StockAnalyzer:
    """Main class for stock analysis application."""

    def __init__(
        self,
        symbols: List[str] = None,
        bse_codes: List[str] = None,
        nse_symbols: List[str] = None,
        mutual_funds: List[str] = None,
        mf_codes: List[str] = None,
        days: int = 365,
        email_recipient: Optional[str] = None,
        use_cache: bool = True,
    ):
        """
        Initialize the StockAnalyzer.

        Args:
            symbols: List of stock symbols to analyze
                    (e.g., ['RELIANCE.NS', 'TCS.BO', '^NSEI'])
            bse_codes: List of BSE stock codes
                      (e.g., ['500325', '532540'])
            nse_symbols: List of NSE stock symbols
                        (e.g., ['RELIANCE', 'TCS'])
            mutual_funds: List of exact mutual fund names to analyze
            days: Number of days of historical data to fetch
                 (default: 365)
            email_recipient: Email address to send the report to.
        """
        logger.debug(
            "Initializing StockAnalyzer with "
            f"symbols={symbols}, bse_codes={bse_codes}, "
            f"nse_symbols={nse_symbols}, email_recipient={email_recipient}"
        )

        # Log the types of inputs for debugging
        if symbols is not None:
            logger.debug(
                f"Symbols type: {type(symbols)}, length: {len(symbols) if hasattr(symbols, '__len__') else 'N/A'}"
            )
        if bse_codes is not None:
            logger.debug(
                f"BSE codes type: {type(bse_codes)}, length: {len(bse_codes) if hasattr(bse_codes, '__len__') else 'N/A'}"
            )
        if nse_symbols is not None:
            logger.debug(
                f"NSE symbols type: {type(nse_symbols)}, length: {len(nse_symbols) if hasattr(nse_symbols, '__len__') else 'N/A'}"
            )

        # Process the symbols
        logger.debug("=== Before _process_symbols ===")
        logger.debug("Symbols: %s (type: %s)", symbols, type(symbols))
        logger.debug("BSE codes: %s (type: %s)", bse_codes, type(bse_codes))
        logger.debug("NSE symbols: %s (type: %s)", nse_symbols, type(nse_symbols))

        self.mutual_funds = mutual_funds or []
        self.mf_codes = mf_codes or []
        processed_symbols = self._process_symbols(symbols, bse_codes, nse_symbols)
        logger.debug("=== After _process_symbols ===")
        logger.debug(
            "Processed symbols: %s (type: %s)",
            processed_symbols,
            type(processed_symbols),
        )

        # Ensure we have a list, not a set or other iterable
        if not isinstance(processed_symbols, list):
            logger.warning(
                "Converting symbols from %s to list", type(processed_symbols)
            )
            try:
                if isinstance(processed_symbols, set):
                    processed_symbols = list(processed_symbols)
                elif hasattr(processed_symbols, "__iter__") and not isinstance(
                    processed_symbols, str
                ):
                    logger.debug(
                        "Converting symbols from %s to list", type(processed_symbols)
                    )
                    processed_symbols = list(processed_symbols)
                else:
                    processed_symbols = [processed_symbols]
                logger.debug("Converted to list: %s", processed_symbols)
            except Exception as e:
                logger.error(
                    "Error normalizing symbols (type: %s): %s",
                    type(processed_symbols).__name__,
                    e,
                    exc_info=True,
                )
                processed_symbols = []

        self.symbols = processed_symbols
        self.days = days
        self.data_fetcher = DataFetcher()
        self.core_analyzer = CoreAnalyzer(
            symbols=self.symbols, days=self.days
        )
        self.mutual_fund_analyzer = MutualFundAnalyzer()
        self.report_data = {}
        self.visualizations = {}
        self.mutual_fund_results = {}
        self.output_dir = REPORTS_DIR
        self.email_recipient = email_recipient
        self.email_sender = None  # Initialize to None

        # Check if email sending should be attempted
        email_requested = bool(email_recipient)
        if settings.EMAIL_ENABLED or email_requested:
            # Check for complete email configuration
            if all([settings.SMTP_SERVER, settings.SMTP_PORT, settings.SENDER_EMAIL, settings.SENDER_PASSWORD]):
                self.email_sender = EmailSender(
                    smtp_server=settings.SMTP_SERVER,
                    smtp_port=settings.SMTP_PORT,
                    username=settings.SENDER_EMAIL,
                    password=settings.SENDER_PASSWORD
                )
            elif email_requested:
                # Log a warning only if the user explicitly asked for an email
                logger.warning("Email credentials not fully configured in .env file. Cannot send email.")

        logger.debug(
            f"StockAnalyzer initialized with {len(self.symbols)} symbols: {self.symbols}"
        )

    def run_analysis(self, send_email: bool = False) -> Tuple[List[Dict], List[Dict], Optional[Path]]:
        """Runs the full analysis pipeline for stocks and mutual funds."""
        logger.debug("Main StockAnalyzer's run_analysis method called.")
        stock_analysis_results = self._run_stock_analysis()
        original_mf_summaries = self._run_mutual_fund_analysis()

        # Define output path
        report_path = self.output_dir / "stock_analysis_report.html"

        # 1. Generate the file-based report (with base64 images)
        self.generate_report(
            stock_results=stock_analysis_results,
            mutual_fund_summaries=original_mf_summaries,
            output_path=report_path,
            for_email=False,
        )

        # 2. If sending an email, generate the email-specific content
        # If sending an email, generate the email-specific content
        if send_email and self.email_recipient:
            logger.info("Preparing email content...")
            # Generate HTML content and attachments for the email
            email_content_data = self.generate_report(
                stock_results=stock_analysis_results,
                mutual_fund_summaries=original_mf_summaries,
                output_path=report_path, # Not written, but used for context
                for_email=True,
            )

            if email_content_data:
                html_content, attachments, email_stock_results, email_mf_summaries = email_content_data
                logger.info(f"Sending email report to {self.email_recipient}")

                # Save email HTML for debugging
                try:
                    with open("test_output/email_preview.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    logger.info("Saved email preview to test_output/email_preview.html")
                except IOError as e:
                    logger.error(f"Could not save email preview: {e}")

                email_sent = self.send_email_report(
                    recipients=[self.email_recipient],
                    subject=f"Stock and Mutual Fund Analysis Report - {datetime.now().strftime('%Y-%m-%d')}",
                    html_content=html_content,
                    attachments=attachments,
                    stock_results=email_stock_results,  # Pass stock results to email sender
                    mutual_fund_summaries=email_mf_summaries
                )
                if email_sent:
                    logger.info(f"Email report sent successfully to {self.email_recipient}.")
                else:
                    logger.warning(f"Email report to {self.email_recipient} was not sent due to configuration issues.")
                return email_stock_results, email_mf_summaries, report_path

        return stock_analysis_results, original_mf_summaries, report_path

    def _run_stock_analysis(self) -> List[AnalysisResult]:
        """Runs the analysis for all configured stock symbols."""
        if not self.symbols:
            logger.info("No stock symbols to analyze.")
            return []

        logger.info(f"Running stock analysis for {len(self.symbols)} symbols...")
        analysis_results_dict = self.core_analyzer.analyze_all()
        analysis_results = list(analysis_results_dict.values())

        # After analysis, generate visualizations for each result
        for result in analysis_results:
            if result and result.technical_indicators:
                stock_data_df = self.core_analyzer.stock_data.get(result.symbol)
                if stock_data_df is None or stock_data_df.empty:
                    logger.warning(f"Skipping visualization for {result.symbol} due to missing data.")
                    continue
                visualizer = StockVisualizer(stock_data_df, result.symbol)
                # Generate charts and attach their paths to the result object
                result.visualization_paths = visualizer.generate_all_visualizations(
                    result.fundamental_metrics, for_email=True
                )
        return analysis_results

    def _run_mutual_fund_analysis(self) -> List[Dict]:
        """Runs the analysis for all configured mutual funds."""
        if not self.mutual_funds and not self.mf_codes:
            logger.info("No mutual funds to analyze.")
            return []

        mf_to_analyze = self.mutual_funds or self.mf_codes
        analysis_by_name = bool(self.mutual_funds)

        logger.info(f"Running mutual fund analysis for {len(mf_to_analyze)} funds...")
        summaries = []
        for fund_identifier in mf_to_analyze:
            try:
                if analysis_by_name:
                    analysis = self.mutual_fund_analyzer.analyze_fund(fund_identifier)
                else:
                    analysis = self.mutual_fund_analyzer.analyze_fund_by_code(fund_identifier)
                
                if analysis:
                    summary = self.mutual_fund_analyzer.generate_fund_summary(analysis)
                    summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to analyze mutual fund {fund_identifier}: {e}", exc_info=True)
        return summaries

    def _generate_charts_html(self, charts: Dict[str, str], for_email: bool, report_path: Path) -> str:
        """Generate HTML for charts."""
        if not charts:
            return ""

        html = '''<div class="analysis-section"><h3>Charts</h3>'''

        for chart_name, chart_data in charts.items():
            chart_title = chart_name.replace('_', ' ').title()
            html += f"<h4>{chart_title}</h4>"

            if for_email:
                # For emails, chart_data is a file path
                chart_path = Path(chart_data)
                if not chart_path.exists():
                    logger.warning(f"Chart file not found: {chart_path}")
                    continue
                chart_id = chart_path.stem.replace(" ", "_").lower()
                html += f'''
                <div class="chart-container" style="margin: 20px 0; text-align: center;">
                    <img src="cid:{chart_id}" alt="{chart_title}"
                         style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;" />
                </div>'''
            else:
                # For HTML reports, chart_data is a base64 string
                html += f'''
                <div class="chart-container" style="margin: 20px 0; text-align: center;">
                    <img src="data:image/png;base64,{chart_data}" alt="{chart_title}"
                         style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px;" />
                </div>'''

        html += "</div>"
        return html

    def _process_symbols(
        self,
        symbols: List[str] = None,
        bse_codes: List[str] = None,
        nse_symbols: List[str] = None,
    ) -> List[str]:
        """Process and validate stock symbols from different sources."""

        def safe_log_input(name, value):
            """Safely log input values with their types."""
            if value is None:
                logger.debug("%s: None", name)
            elif isinstance(value, (list, tuple, set)):
                logger.debug(
                    "%s: %s (type: %s, len: %d)",
                    name, value, type(value).__name__, len(value)
                )
            else:
                logger.debug("%s: %s (type: %s)", name, value, type(value).__name__)

        logger.debug("=== _process_symbols called with: ===")
        safe_log_input("symbols", symbols)
        safe_log_input("bse_codes", bse_codes)
        safe_log_input("nse_symbols", nse_symbols)

        processed_symbols = []

        def normalize_symbols(symbols_input, input_name="symbols") -> List[str]:
            """Helper to safely convert various inputs to a list of strings."""
            if not symbols_input:
                return []
            if isinstance(symbols_input, str):
                return [s.strip() for s in symbols_input.split(',') if s.strip()]
            if isinstance(symbols_input, (list, set, tuple)):
                return [str(s).strip() for s in symbols_input if str(s).strip()]
            logger.warning("Cannot normalize symbols of type %s", type(symbols_input).__name__)
            return []

        if symbols:
            processed_symbols.extend(normalize_symbols(symbols, "symbols"))
        if bse_codes:
            processed_symbols.extend([f"{code}.BO" for code in normalize_symbols(bse_codes, "bse_codes")])
        if nse_symbols:
            processed_symbols.extend([f"{sym}.NS" for sym in normalize_symbols(nse_symbols, "nse_symbols")])

        if not processed_symbols and not self.mutual_funds:
            logger.info("No symbols provided, using default top BSE stocks.")
            try:
                processed_symbols = get_top_bse_stocks()
            except Exception as e:
                logger.error(f"Failed to fetch default BSE stocks: {e}")
                processed_symbols = []

        # Deduplicate while preserving order
        seen = set()
        unique_symbols = [s for s in processed_symbols if not (s in seen or seen.add(s))]

        logger.info(f"Processed {len(unique_symbols)} unique symbols.")
        logger.debug(f"Final symbol list: {unique_symbols}")
        return unique_symbols

    def validate_symbols(self, symbols: List[str]) -> Tuple[List[str], List[str]]:
        """Validate stock symbols and separate them into valid and invalid.

        Args:
            symbols: List of stock symbols to validate

        Returns:
            Tuple of (valid_symbols, invalid_symbols)
        """
        if not symbols:
            return [], []

        valid = []
        invalid = []

        # Ensure we have a list and not some other iterable
        try:
            symbols_list = list(symbols)
        except TypeError:
            logger.error("Cannot convert symbols to list: %s", symbols)
            return [], []

        for symbol in symbols_list:
            try:
                # Ensure symbol is a string
                symbol_str = str(symbol).strip()
                if not symbol_str:
                    invalid.append(str(symbol))
                    continue

                # Check if symbol follows known patterns
                if (
                    symbol_str.endswith((".NS", ".BO"))
                    or symbol_str.startswith("^")
                    or symbol_str.upper() in ["^NSEI", "^BSESN", "^NSEBANK"]
                ):
                    valid.append(symbol_str)
                else:
                    invalid.append(symbol_str)

            except Exception as e:
                logger.error("Error validating symbol %s: %s", symbol, e)
                invalid.append(str(symbol))

        logger.info("Validated symbols: %d valid, %d invalid", len(valid), len(invalid))
        if invalid:
            logger.debug("Invalid symbols: %s", invalid)

        return valid, invalid

    def fetch_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all symbols.

        Returns:
            Dictionary mapping symbols to DataFrames with stock data
        """
        logger.info("Fetching data for %d stocks...", len(self.symbols))
        return self.data_fetcher.fetch_multiple_stocks(self.symbols, self.days)

    def prepare_analysis_summary(self, symbol: str, data: pd.DataFrame, analysis_result: AnalysisResult, recommendation) -> Dict:
        """
        Perform technical and fundamental analysis on a stock or index.

        Args:
            symbol: Stock or index symbol
            data: DataFrame with stock/index data
            analysis_result: The core analysis result.
            recommendation: The generated recommendation.

        Returns:
            Dictionary with analysis results
        """
        logger.info("Preparing analysis summary for %s...", symbol)

        is_index = symbol.startswith("^")

        # For indices, we'll do a simpler analysis
        if is_index:
            latest = data.iloc[-1].to_dict()
            prev_close = data.iloc[-2].to_dict() if len(data) > 1 else latest

            analysis = {
                "symbol": symbol,
                "name": f"{symbol.replace('^', '')} Index",
                "company_name": f"{symbol.replace('^', '')} Index",
                "latest_price": latest.get("close"),
                "price": latest.get("close"),
                "change_pct": (
                    (
                        latest.get("close", 0)
                        / prev_close.get("close", latest.get("close", 1))
                        - 1
                    )
                    * 100
                    if "close" in latest
                    and "close" in prev_close
                    and prev_close["close"] > 0
                    else 0
                ),
                "volume": latest.get("volume"),
                "is_index": True,
                "fundamentals": {},
                "charts": [],
                "rsi": None,
                "bb_upper": None,
                "bb_middle": None,
                "bb_lower": None,
                "macd": None,
                "macd_signal": None,
                "pe_ratio": None,
                "52_week_high": data["high"].max() if not data.empty else None,
                "52_week_low": data["low"].min() if not data.empty else None,
                "data": data,
            }

            # Add simple moving averages if we have enough data
            if len(data) >= 20:
                analysis.update(
                    {
                        "ma_20": data["close"].rolling(window=20).mean().iloc[-1],
                        "ma_50": (
                            data["close"].rolling(window=50).mean().iloc[-1]
                            if len(data) >= 50
                            else None
                        ),
                        "ma_200": (
                            data["close"].rolling(window=200).mean().iloc[-1]
                            if len(data) >= 200
                            else None
                        ),
                    }
                )

            return analysis

        # For regular stocks, do full technical analysis
        ta = TechnicalAnalysis(data)
        data_with_indicators = ta.calculate_all_indicators()

        fundamentals = analysis_result.fundamental_metrics

        # Generate visualizations for HTML report (base64)
        visualizer = StockVisualizer(data_with_indicators, symbol)
        charts = visualizer.generate_all_visualizations(
            fundamentals,
            for_html_report=True,  # Generate base64 images for HTML report
            for_email=False
        )

        # Store results
        self.visualizations[symbol] = charts
        # Store the original data for potential regeneration
        if not hasattr(self, "original_data"):
            self.original_data = {}
        self.original_data[symbol] = data_with_indicators

        # Prepare analysis summary
        latest = data_with_indicators.iloc[-1].to_dict()

        analysis = {
            "recommendation": recommendation.to_dict(),
            "symbol": symbol,
            "company_name": getattr(visualizer, "formatted_company_name", symbol),
            "latest_price": latest.get("close"),
            "change_pct": (
                (latest.get("close", 0) / data_with_indicators["close"].iloc[-2] - 1)
                * 100
                if len(data_with_indicators) > 1
                else 0
            ),
            "volume": latest.get("volume"),
            "rsi": latest.get("rsi"),
            "ma_20": latest.get("ma_20"),
            "ma_50": latest.get("ma_50"),
            "ma_200": latest.get("ma_200"),
            "bb_upper": latest.get("bb_upper"),
            "bb_middle": latest.get("bb_middle"),
            "bb_lower": latest.get("bb_lower"),
            "macd": latest.get("macd_line"),
            "macd_signal": latest.get("macd_signal"),
            "fundamentals": fundamentals or {},
            "charts": list(charts.values()) if charts else [],
            "is_index": False,
        }

        return analysis

    def _generate_stock_comparison_table(self, analysis_results: List[Dict]) -> str:
        """Generate a concise HTML table for stock comparison."""
        if not analysis_results:
            return ""

        # Define metrics to display in the table
        metrics = [
            ('Price', 'latest_price', {'is_currency': True}),
            ('RSI', 'rsi', {}),
            ('20-day MA', 'ma_20', {'is_currency': True}),
            ('50-day MA', 'ma_50', {'is_currency': True}),
            ('200-day MA', 'ma_200', {'is_currency': True}),
            ('P/E Ratio', 'pe_ratio', {}),
            ('Debt/Equity', 'debt_to_equity', {}),
            ('Revenue Growth', 'revenue_growth', {'is_percent': True}),
            ('Dividend Yield', 'dividend_yield', {'is_percent': True}),
        ]

        # Start table structure
        html = '''
        <div style="overflow-x: auto; margin-bottom: 25px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; min-width: 800px;">
                <thead>
                    <tr style="background-color: #f0f7ff;">
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">Stock</th>
        '''
        for metric_name, _, _ in metrics:
            html += f'<th style="padding: 8px; border: 1px solid #dee2e6; text-align: right;">{metric_name}</th>'
        html += '</tr></thead><tbody>'

        # Populate table rows
        for i, analysis in enumerate(analysis_results):
            bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            html += f'<tr style="background-color: {bg_color};">'
            html += f'<td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">{analysis.get("symbol", "N/A")}</td>'

            for _, key, opts in metrics:
                is_currency = opts.get('is_currency', False)
                is_percent = opts.get('is_percent', False)

                if key in ['pe_ratio', 'debt_to_equity', 'revenue_growth', 'dividend_yield']:
                    value = analysis.get('fundamentals', {}).get(key)
                else:
                    value = analysis.get(key)

                # Formatting logic
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    formatted_value = "N/A"
                elif is_currency:
                    formatted_value = f"₹{value:.2f}"
                elif is_percent:
                    # Value is already a percentage, just format it
                    formatted_value = f"{value:.2f}%"
                else:
                    try:
                        formatted_value = f"{float(value):.2f}"
                    except (ValueError, TypeError):
                        formatted_value = str(value)

                html += f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: right;">{formatted_value}</td>'
            html += '</tr>'

        html += '</tbody></table></div>'
        return html

    def _generate_mf_comparison_table(self, mf_summaries: List[Dict]) -> str:
        """Generate a concise HTML table for mutual fund comparison."""
        if not mf_summaries:
            return ""

        metrics = [
            ('Latest NAV', 'latest_nav', {'is_currency': True}),
            ('1Y CAGR', 'cagr_1y', {'is_percent': True}),
            ('3Y CAGR', 'cagr_3y', {'is_percent': True}),
            ('5Y CAGR', 'cagr_5y', {'is_percent': True}),
            ('Expense Ratio', 'expense_ratio', {'is_percent': True}),
            ('AUM (Cr)', 'aum', {'is_currency': True}),
            ('NAV Date', 'nav_date', {}),
        ]

        html = '''
        <div style="overflow-x: auto; margin-bottom: 25px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; min-width: 800px;">
                <thead>
                    <tr style="background-color: #e8f5e9;">
                        <th style="padding: 8px; border: 1px solid #dee2e6; text-align: left;">Fund Name</th>
        '''
        for metric_name, _, _ in metrics:
            html += f'<th style="padding: 8px; border: 1px solid #dee2e6; text-align: right;">{metric_name}</th>'
        html += '</tr></thead><tbody>'

        for i, summary in enumerate(mf_summaries):
            bg_color = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            html += f'<tr style="background-color: {bg_color};">'
            html += f'<td style="padding: 8px; border: 1px solid #dee2e6; font-weight: bold;">{summary.get("name", "N/A")}</td>'

            for _, key, opts in metrics:
                value = summary.get(key)
                is_currency = opts.get('is_currency', False)
                is_percent = opts.get('is_percent', False)

                if value is None or value == 'N/A' or (isinstance(value, float) and math.isnan(value)):
                    formatted_value = "N/A"
                elif is_currency:
                    try:
                        formatted_value = f"₹{float(value):.2f}"
                    except (ValueError, TypeError):
                        formatted_value = str(value)
                elif is_percent:
                    try:
                        # Here, we assume the value is already a percentage number (e.g., 1.5 for 1.5%)
                        formatted_value = f"{float(value):.2f}%"
                    except (ValueError, TypeError):
                        formatted_value = str(value)
                else:
                    formatted_value = str(value)

                html += f'<td style="padding: 8px; border: 1px solid #dee2e6; text-align: right;">{formatted_value}</td>'
            html += '</tr>'

        html += '</tbody></table></div>'
        return html

    def generate_report(
        self,
        stock_results: List[AnalysisResult],
        mutual_fund_summaries: List[Dict],
        output_path: Path,
        for_email: bool = False,
    ) -> Optional[Tuple[str, List[Dict[str, str]], List[AnalysisResult], List[Dict]]]:
        """Generate an HTML report from analysis results."""
        logger.info(
            f"Generating report (for_email={for_email}) for "
            f"{len(stock_results)} stocks and {len(mutual_fund_summaries)} mutual funds."
        )

        env = Environment(
            loader=PackageLoader("stock_analysis_toolkit", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        env.filters["safe_format"] = safe_format
        env.filters["get_change_class"] = get_change_class

        report_stock_results = deepcopy(stock_results)
        report_mf_summaries = deepcopy(mutual_fund_summaries)
        attachments = []

        # Process visualization paths for the report
        for result in report_stock_results:
            if hasattr(result, 'visualization_paths') and result.visualization_paths:
                for key, path in result.visualization_paths.items():
                    if for_email:
                        cid = f"image_{result.symbol}_{key}"
                        result.visualization_paths[key] = f"cid:{cid}"
                        attachments.append({"path": path, "cid": cid, "type": "image/png"})
                    else:
                        try:
                            with open(path, "rb") as f:
                                encoded_string = base64.b64encode(f.read()).decode("utf-8")
                            result.visualization_paths[key] = f"data:image/png;base64,{encoded_string}"
                        except FileNotFoundError:
                            logger.warning(f"Image file not found: {path}")
                            result.visualization_paths[key] = ""
        
        # Process mutual fund charts if they exist
        if for_email and report_mf_summaries:
            for mf_summary in report_mf_summaries:
                if 'charts' in mf_summary and mf_summary['charts']:
                    for chart_path in mf_summary['charts']:
                        if isinstance(chart_path, str) and os.path.exists(chart_path):
                            cid = f"mf_{os.path.basename(chart_path).split('.')[0]}"
                            attachments.append({
                                "path": chart_path, 
                                "cid": cid, 
                                "type": "image/png"
                            })

        context = {
            "stock_results": report_stock_results,
            "mutual_fund_summaries": report_mf_summaries,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        template = env.get_template("email_template_clean.html")
        html_content = template.render(context)

        if for_email:
            return html_content, attachments, report_stock_results, report_mf_summaries
        else:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Report saved to {output_path}")
            except IOError as e:
                logger.error(f"Error saving report to {output_path}: {e}")
            return None

    def send_email_report(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        attachments: List[Dict[str, str]],
        stock_results: List[AnalysisResult],
        mutual_fund_summaries: List[Dict[str, Any]]
    ) -> bool:
        """Send the analysis report via email."""
        if not self.email_sender:
            logger.warning("Email sending is disabled or not configured.")
            return False

        try:
            self.email_sender.send_email(
                recipients=recipients,
                subject=subject,
                html_content=html_content,
                attachments=attachments,
                stock_results=stock_results,
                mutual_fund_summaries=mutual_fund_summaries
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Stock and Mutual Fund Analysis Tool")
    parser.add_argument(
        "-s",
        "--stocks",
        action="append",
        help="Stock symbol to analyze. Can be specified multiple times (e.g., -s RELIANCE.NS -s TCS.NS)",
    )
    parser.add_argument(
        "-mf",
        "--mutual_funds",
        nargs='+',
        action='append',
        help='Mutual fund name to analyze. Can be specified multiple times. For multi-word names, wrap in quotes or pass as separate words. (e.g., -mf "Mirae Asset Large Cap Fund" -mf "Axis Bluechip Fund")',
    )
    parser.add_argument(
        "--mf-codes",
        nargs='+',
        help='Mutual fund scheme codes to analyze. Can be specified multiple times (e.g., --mf-codes 108467 120757).'
    )
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        default=90,
        help="Number of days for historical data analysis (default: 90)",
    )
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        help="Email address to send the report to. If provided, the report will be sent as an email.",
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Disable caching of analysis results"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging for debugging",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Flag to send the report via email. Requires --email to be set.",
    )
    return parser.parse_args()

def main():
    """Main function to run the analysis."""
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Verbose logging enabled.")

    stock_symbols = args.stocks if args.stocks else []
    raw_mutual_funds = args.mutual_funds or []
    mutual_funds = [' '.join(fund_words) for fund_words in raw_mutual_funds]
    mf_codes = args.mf_codes or []

    if not stock_symbols and not mutual_funds and not mf_codes:
        logger.error("No stocks or mutual funds provided. Use -s or -mf to specify.")
        return

    try:
        analyzer = StockAnalyzer(
            symbols=stock_symbols,
            mutual_funds=mutual_funds,
            mf_codes=mf_codes,
            days=args.days,
            email_recipient=args.email,
            use_cache=not args.no_cache,
        )

        should_send_email = args.send_email and bool(args.email)

        _, _, report_path = analyzer.run_analysis(send_email=should_send_email)

        if report_path:
            logger.info(f"Analysis complete. Report available at: {report_path}")
        elif not should_send_email:
             logger.info("Analysis complete. No data to generate a report.")

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
