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
from .analysis.bond import BondInput, compute_bond_metrics
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
        indices: List[str] = None,
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
        self.indices = indices or []

        self.core_analyzer = CoreAnalyzer(symbols=self.symbols, indices=self.indices, days=self.days)
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

        return stock_results, mf_summaries, report_path

    def _run_mutual_fund_analysis(self) -> List[Dict]:
        """Runs the analysis for all configured mutual funds."""
        summaries = []
        if self.mutual_funds:
            logger.info(f"Analyzing {len(self.mutual_funds)} mutual funds by name.")
            for fund_name in self.mutual_funds:
                try:
                    analysis = self.mutual_fund_analyzer.analyze_fund(fund_name)
                    if analysis:
                        summaries.append(self.mutual_fund_analyzer.generate_fund_summary(analysis))
                except Exception as e:
                    logger.error(f"Failed to analyze mutual fund by name '{fund_name}': {e}", exc_info=True)

        if self.mf_codes:
            logger.info(f"Analyzing {len(self.mf_codes)} mutual funds by code.")
            for scheme_code in self.mf_codes:
                try:
                    analysis = self.mutual_fund_analyzer.analyze_fund_by_code(scheme_code)
                    if analysis:
                        summaries.append(self.mutual_fund_analyzer.generate_fund_summary(analysis))
                except Exception as e:
                    logger.error(f"Failed to analyze mutual fund by code '{scheme_code}': {e}", exc_info=True)

        if not self.mutual_funds and not self.mf_codes:
            logger.info("No mutual funds to analyze.")

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


def _load_and_analyze_bonds(csv_path: str, benchmark_yield: Optional[float]) -> List[Dict[str, Any]]:
    """Load corporate bonds from a CSV and compute metrics.

    Expected CSV columns (headers case-insensitive):
    - isin (str)
    - issuer (str)
    - coupon (percent, e.g., 7.5)
    - frequency (int payments per year, default 2)
    - maturity_date (YYYY-MM-DD)
    - clean_price (per 100 face)
    - face_value (optional, default 100)
    - settlement_date (optional YYYY-MM-DD; defaults to run date)
    - day_count (optional, one of ACT/365, ACT/360, 30/360)
    - rating (optional)
    - benchmark_yield (optional percent; overrides global if present)
    """
    df = pd.read_csv(csv_path)
    results: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        try:
            def pick(col, default=None):
                for name in [col, col.upper(), col.lower(), col.title()]:
                    if name in row and not (pd.isna(row[name])):
                        return row[name]
                return default

            maturity_raw = pick('maturity_date')
            maturity_date = pd.to_datetime(maturity_raw).date() if pd.notna(maturity_raw) else None
            if maturity_date is None:
                raise ValueError("maturity_date is required")

            settlement_raw = pick('settlement_date')
            settlement_date = pd.to_datetime(settlement_raw).date() if pd.notna(settlement_raw) else None

            # Optional quantity
            qty_raw = pick('quantity', 1.0)
            quantity = float(qty_raw) if qty_raw is not None and qty_raw != '' else 1.0

            # Optional call/put schedules: parse semicolon-separated dates/prices
            def parse_schedule(dates_str, prices_str):
                if dates_str is None or prices_str is None:
                    return None
                dates = [pd.to_datetime(x.strip()).date() for x in str(dates_str).split(';') if x.strip()]
                prices = [float(x.strip()) for x in str(prices_str).split(';') if x.strip()]
                if not dates or not prices or len(dates) != len(prices):
                    return None
                return list(zip(dates, prices))

            call_sched = parse_schedule(pick('call_dates'), pick('call_prices'))
            put_sched = parse_schedule(pick('put_dates'), pick('put_prices'))

            bi = BondInput(
                isin=str(pick('isin', '')),
                issuer=str(pick('issuer', '')),
                coupon=float(pick('coupon', 0.0)),
                frequency=int(pick('frequency', 2)),
                maturity_date=maturity_date,
                clean_price=float(pick('clean_price', 0.0)),
                face_value=float(pick('face_value', 100.0)),
                settlement_date=settlement_date,
                day_count=str(pick('day_count', 'ACT/365')),
                rating=str(pick('rating', '')) if pick('rating') is not None else None,
                benchmark_yield=float(pick('benchmark_yield')) if pick('benchmark_yield') is not None else None,
                quantity=quantity,
                call_schedule=call_sched,
                put_schedule=put_sched,
            )
            metrics = compute_bond_metrics(bi, benchmark_yield_pct=benchmark_yield)
            results.append({
                'isin': bi.isin,
                'issuer': bi.issuer,
                'coupon': bi.coupon,
                'frequency': bi.frequency,
                'maturity_date': bi.maturity_date.isoformat(),
                'clean_price': bi.clean_price,
                'face_value': bi.face_value,
                'settlement_date': bi.settlement_date.isoformat() if bi.settlement_date else None,
                'day_count': bi.day_count,
                'rating': bi.rating,
                'quantity': bi.quantity,
                'ytm': metrics.ytm,
                'current_yield': metrics.current_yield,
                'accrued_interest': metrics.accrued_interest,
                'dirty_price': metrics.dirty_price,
                'macaulay_duration': metrics.macaulay_duration,
                'modified_duration': metrics.modified_duration,
                'convexity': metrics.convexity,
                'spread': metrics.spread,
                'ytc': metrics.ytc,
                'ytw': metrics.ytw,
                'market_value': metrics.market_value,
                'next_call_date': (sorted([d for d, _ in (bi.call_schedule or []) if d >= (bi.settlement_date or pd.Timestamp.today().date())])[0].isoformat() if bi.call_schedule else None),
            })
        except Exception as e:
            logger.error(f"Failed to compute bond metrics for row {_}: {e}")
    return results


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Stock and Mutual Fund Analysis Tool", allow_abbrev=False)
    parser.add_argument("-s", "--stocks", action="append", help="Stock symbol to analyze.")
    parser.add_argument("-mf", "--mutual_funds", nargs='+', action='append', help='Mutual fund name to analyze.')
    parser.add_argument("--mf-codes", nargs='+', help='Mutual fund scheme codes to analyze.')
    parser.add_argument("-d", "--days", type=int, default=90, help="Number of days for historical data.")
    parser.add_argument("-e", "--email", type=str, help="Email address to send the report to.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging for debugging.")
    parser.add_argument('--send-email', action='store_true', help='Send the report via email.')
    parser.add_argument('--indices', nargs='*', help='A list of index symbols to analyze (e.g., ^NSEI ^CRSMID).')
    parser.add_argument('--bonds-csv', type=str, help='Path to a CSV containing corporate bonds to analyze.')
    parser.add_argument('--benchmark-yield', type=float, help='Benchmark government yield (percent) for spread calc.')
    return parser.parse_args()


def main():
    """Main function to run the stock analysis tool."""
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    logger.info(f"Parsed arguments: {args}")

    mutual_funds = [' '.join(sublist) for sublist in args.mutual_funds] if args.mutual_funds else None
    logger.info(f"Processed mutual funds by name: {mutual_funds}")
    logger.info(f"Mutual funds by code from args: {args.mf_codes}")

    # Provide sensible default indices if none are supplied
    default_indices = ['^NSEI', '^CNXBL', '^CRSMID', '^CRSSML']
    resolved_indices = args.indices or default_indices

    analyzer = StockAnalyzer(
        symbols=args.stocks,
        indices=resolved_indices,
        mutual_funds=mutual_funds,
        mf_codes=args.mf_codes,
        days=args.days,
        email_recipient=args.email,
    )

    try:
        should_send_email = args.send_email and bool(args.email)

        stock_results = analyzer.core_analyzer.analyze_all()
        index_results = analyzer.core_analyzer.analyze_indices()

        # Mutual Fund Analysis
        mf_codes_from_args = args.mf_codes or []
        mf_names_from_args = mutual_funds or []
        mf_analyzer = MutualFundAnalyzer()
        mf_summaries = mf_analyzer.run_analysis(fund_names=mf_names_from_args, scheme_codes=mf_codes_from_args)

        # Corporate Bond Analysis (optional via CSV)
        bond_results = []
        if args.bonds_csv:
            try:
                bond_results = _load_and_analyze_bonds(args.bonds_csv, args.benchmark_yield)
                logger.info(f"Analyzed {len(bond_results)} corporate bonds from CSV")
            except Exception as e:
                logger.error(f"Failed to analyze bonds from CSV '{args.bonds_csv}': {e}", exc_info=True)

        # Generate Report
        report_generator = ReportGenerator()
        # Portfolio aggregates for bonds
        portfolio = None
        if bond_results:
            try:
                total_mv = sum(b.get('market_value') or 0.0 for b in bond_results)
                # Weight by market value when available
                def wavg(key):
                    num = sum((b.get(key) or 0.0) * (b.get('market_value') or 0.0) for b in bond_results if b.get(key) is not None)
                    den = total_mv if total_mv else 0.0
                    return (num / den) if den else None
                portfolio = {
                    'count': len(bond_results),
                    'total_market_value': total_mv,
                    'weighted_modified_duration': wavg('modified_duration'),
                    'weighted_convexity': wavg('convexity'),
                }
            except Exception:
                portfolio = None
        analysis_data = {
            'stock_results': list(stock_results.values()),
            'mutual_fund_summaries': mf_summaries,
            'index_results': index_results,
            'bond_results': bond_results,
            'bond_portfolio': portfolio,
        }
        html_content, report_path = report_generator.generate_stock_report(
            symbol="",
            data=pd.DataFrame(),
            analysis=analysis_data,
            template_name='email_template.html',
            output_file=REPORTS_DIR / "stock_analysis_report.html"
        )

        if should_send_email and report_path and analyzer.email_sender:
            recipients = [email.strip() for email in analyzer.email_recipient.split(',')]
            analyzer.email_sender.send_email(
                to_email=recipients,
                subject=f"Stock and Mutual Fund Analysis Report - {datetime.now().strftime('%Y-%m-%d')}",
                html_content=html_content,
                attachments=[report_path]
            )

        if report_path:
            logger.info(f"Analysis complete. Report available at: {report_path}")
        else:
            logger.info("Analysis complete. No data to generate a report.")

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
