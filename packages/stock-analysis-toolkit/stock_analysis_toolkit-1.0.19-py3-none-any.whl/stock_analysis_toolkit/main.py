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

        self.reporter = ReportGenerator()
        html_content, _ = self.reporter.generate_stock_report(
            symbol="",  # Not used in the combined report
            data=pd.DataFrame(), # Not used
            analysis={
                'stock_results': stock_analysis_results,
                'mutual_fund_summaries': original_mf_summaries
            },
            template_name='email_template.html',
            output_file=report_path
        )

        if send_email and self.email_recipient:
            if self.email_sender:
                recipients = [email.strip() for email in self.email_recipient.split(',')]
                logger.info(f"Sending email report to {', '.join(recipients)}")
                self.email_sender.send_email(
                    to_email=recipients,
                    subject=f"Stock and Mutual Fund Analysis Report - {datetime.now().strftime('%Y-%m-%d')}",
                    html_content=html_content
                )
            else:
                logger.warning("Email credentials not fully configured. Cannot send email.")

        return stock_analysis_results, original_mf_summaries, report_path

    def _run_stock_analysis(self) -> List[AnalysisResult]:
        """Runs the analysis for all configured stock symbols."""
        if not self.symbols:
            logger.info("No stock symbols to analyze.")
            return []

        logger.info(f"Running stock analysis for {len(self.symbols)} symbols...")
        analysis_results_dict = self.core_analyzer.analyze_all()
        analysis_results = list(analysis_results_dict.values())

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
