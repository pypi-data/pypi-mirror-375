"""
Stock Analysis Tool

A comprehensive tool for analyzing Indian stocks with technical and
fundamental analysis.
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback

from .analysis.mutual_fund_analyzer import MutualFundAnalyzer
from .config.settings import get_settings, get_top_bse_stocks
from .core.analyzer import StockAnalyzer as CoreAnalyzer
from .data.fetcher import DataFetcher
from .reporting.email_sender import EmailSender
from .reporting.reporter import ReportGenerator

# --- Early Setup: Logging Configuration ---
settings = get_settings()
LOGS_DIR = settings.LOGS_DIR
REPORTS_DIR = settings.REPORTS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "stock_analysis.log"),
        RichHandler(rich_tracebacks=True, markup=True),
    ],
)

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.WARNING)

install_rich_traceback(show_locals=True)
console = Console()


class StockAnalyzer:
    """Main class for stock analysis application."""

    def __init__(
        self,
        symbols: List[str] = None,
        mutual_funds: List[str] = None,
        mf_codes: List[str] = None,
        days: int = 365,
        email_recipient: Optional[str] = None,
    ):
        self.symbols = self._process_symbols(symbols)
        self.mutual_funds = mutual_funds or []
        self.mf_codes = mf_codes or []
        self.days = days
        self.email_recipient = email_recipient

        self.core_analyzer = CoreAnalyzer(symbols=self.symbols, days=self.days)
        self.mutual_fund_analyzer = MutualFundAnalyzer()
        self.reporter = ReportGenerator()
        self.email_sender = self._setup_email_sender()

    def _setup_email_sender(self) -> Optional[EmailSender]:
        if self.email_recipient and all([settings.SMTP_SERVER, settings.SMTP_PORT, settings.SENDER_EMAIL, settings.SENDER_PASSWORD]):
            return EmailSender(
                smtp_server=settings.SMTP_SERVER,
                smtp_port=settings.SMTP_PORT,
                username=settings.SENDER_EMAIL,
                password=settings.SENDER_PASSWORD,
            )
        elif self.email_recipient:
            logger.warning("Email credentials not fully configured. Cannot send email.")
        return None

    def run_analysis(self, send_email: bool = False):
        """Runs the full analysis pipeline for stocks and mutual funds."""
        stock_results = self.core_analyzer.analyze_all()
        mf_summaries = self._run_mutual_fund_analysis()

        report_path = REPORTS_DIR / "stock_analysis_report.html"
        html_content, _ = self.reporter.generate_stock_report(
            symbol="",  # Not used in the combined report
            data=pd.DataFrame(), # Not used
            analysis={'stock_results': list(stock_results.values()), 'mutual_fund_summaries': mf_summaries},
            template_name='email_template.html',
            output_file=report_path
        )
        logger.info(f"Report saved to {report_path}")

        if send_email and self.email_sender:
            recipients = [email.strip() for email in self.email_recipient.split(',')]
            logger.info(f"Sending email report to {', '.join(recipients)}")
            self.email_sender.send_email(
                to_email=recipients,
                subject=f"Stock and Mutual Fund Analysis Report - {datetime.now().strftime('%Y-%m-%d')}",
                html_content=html_content
            )

    def _run_mutual_fund_analysis(self) -> List[Dict]:
        """Runs the analysis for all configured mutual funds."""
        mf_to_analyze = self.mutual_funds or self.mf_codes
        if not mf_to_analyze:
            logger.info("No mutual funds to analyze.")
            return []

        analysis_by_name = bool(self.mutual_funds)
        summaries = []
        for identifier in mf_to_analyze:
            try:
                analysis = self.mutual_fund_analyzer.analyze_fund_by_code(identifier) if not analysis_by_name else self.mutual_fund_analyzer.analyze_fund(identifier)
                if analysis:
                    summaries.append(self.mutual_fund_analyzer.generate_fund_summary(analysis))
            except Exception as e:
                logger.error(f"Failed to analyze mutual fund {identifier}: {e}", exc_info=True)
        return summaries

    def _process_symbols(self, symbols: List[str] = None) -> List[str]:
        """Process and validate stock symbols."""
        if not symbols:
            logger.info("No symbols provided, using default top BSE stocks.")
            try:
                return get_top_bse_stocks()
            except Exception as e:
                logger.error(f"Failed to fetch default BSE stocks: {e}")
                return []
        
        # Deduplicate while preserving order
        return list(dict.fromkeys(symbols))


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Stock and Mutual Fund Analysis Tool")
    parser.add_argument("-s", "--stocks", action="append", help="Stock symbol to analyze.")
    parser.add_argument("-mf", "--mutual_funds", nargs='+', action='append', help='Mutual fund name to analyze.')
    parser.add_argument("--mf-codes", nargs='+', help='Mutual fund scheme codes to analyze.')
    parser.add_argument("-d", "--days", type=int, default=90, help="Number of days for historical data.")
    parser.add_argument("-e", "--email", type=str, help="Email address to send the report to.")
    parser.add_argument("--send-email", action="store_true", help="Flag to send the report via email.")
    return parser.parse_args()


def main():
    """Main function to run the stock analysis tool."""
    args = parse_arguments()

    mutual_funds = [item for sublist in args.mutual_funds for item in sublist] if args.mutual_funds else None

    analyzer = StockAnalyzer(
        symbols=args.stocks,
        mutual_funds=mutual_funds,
        mf_codes=args.mf_codes,
        days=args.days,
        email_recipient=args.email,
    )

    try:
        analyzer.run_analysis(send_email=args.send_email)
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
