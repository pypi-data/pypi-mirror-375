"""
Report generation module.

This module provides functionality to generate comprehensive
stock analysis reports in various formats.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates stock analysis reports in various formats.

    This class handles the creation of comprehensive stock analysis
    reports.
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the ReportGenerator.

        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up template environment
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def _get_template(self, template_name: str):
        """
        Get a template by name.

        Args:
            template_name: Name of the template file

        Returns:
            Jinja2 template object

        Raises:
            FileNotFoundError: If template file is not found
            Exception: For other template loading errors
        """
        try:
            # Try to load from the templates directory first
            return self.env.get_template(template_name)
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            raise

    def generate_stock_report(
        self,
        symbol: str,
        data: pd.DataFrame,
        analysis: Dict[str, Any],
        template_name: str = "stock_report.html",
        output_file: Optional[Union[str, Path]] = None,
    ) -> Tuple[str, Path]:
        """
        Generate a stock analysis report using the new template system.

        Args:
            symbol: Stock symbol
            data: Stock data with indicators
            analysis: Analysis results dictionary
            template_name: Name of the template to use
            output_file: Path to save the report

        Returns:
            Tuple of (HTML content, output file path)
        """
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"{symbol}_report_{timestamp}.html"
            else:
                output_file = Path(output_file)

            output_file.parent.mkdir(parents=True, exist_ok=True)

            context = {
                "symbol": symbol,
                "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "analysis": analysis,
                "is_index": symbol.startswith("^"),
            }

            def format_currency(value, symbol="$", places=2):
                try:
                    return f"{symbol}{value:,.{places}f}" if value is not None else "N/A"
                except (ValueError, TypeError):
                    return str(value)

            def format_percent(value, places=2):
                try:
                    return f"{value:,.{places}f}%" if value is not None else "N/A"
                except (ValueError, TypeError):
                    return str(value)

            context["helpers"] = {
                "format_currency": format_currency,
                "format_percent": format_percent,
            }

            template = self._get_template(template_name)
            html_content = template.render(**context)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Generated report: {output_file}")
            return html_content, output_file

        except Exception as e:
            logger.error(f"Error generating stock report: {e}", exc_info=True)
            raise

    def generate_sector_report(
        self,
        sector_data: Dict[str, Dict[str, Any]],
        top_stocks: Dict[str, List[Dict[str, Any]]],
        template_name: str = "sector_report.html",
        output_file: Optional[Union[str, Path]] = None,
        **additional_context: Any,
    ) -> Tuple[str, Path]:
        """
        Generate a sector performance report.

        Args:
            sector_data: Dictionary mapping sector names to performance data
            top_stocks: Dictionary mapping sector names to lists of top stocks
            template_name: Name of the template to use
            output_file: Path to save the report
            **additional_context: Additional context for the template

        Returns:
            Tuple of (HTML content, output file path)
        """
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"sector_report_{timestamp}.html"
            else:
                output_file = Path(output_file)

            output_file.parent.mkdir(parents=True, exist_ok=True)

            sector_overview = {}
            if sector_data:
                changes = [(s, d.get("change", 0)) for s, d in sector_data.items() if d.get("change") is not None]
                if changes:
                    sorted_sectors = sorted(changes, key=lambda x: x[1], reverse=True)
                    sector_overview.update({
                        "top_performer": {"name": sorted_sectors[0][0], "change": sorted_sectors[0][1]},
                        "worst_performer": {"name": sorted_sectors[-1][0], "change": sorted_sectors[-1][1]},
                        "average_change": sum(c[1] for c in changes) / len(changes) if changes else 0,
                        "trend": "up" if sum(1 for c in changes if c[1] > 0) > len(changes) / 2 else "down",
                    })

            context = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sector_data": sector_data,
                "top_stocks": top_stocks,
                "sector_overview": sector_overview,
                "sector_comparison": {s: {k: d.get(k, 0) for k in ['1D', '1W', '1M', 'YTD', '1Y']} for s, d in sector_data.items()},
                "sector_insights": additional_context.get("insights", []),
            }
            context.update(additional_context)

            def format_percent(value, places=2):
                try:
                    if value is None: return "N/A"
                    return f"{'+' if value > 0 else ''}{value:,.{places}f}%"
                except (ValueError, TypeError):
                    return str(value)

            context["helpers"] = {"format_percent": format_percent}

            template = self._get_template(template_name)
            html_content = template.render(**context)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Generated sector report: {output_file}")
            return html_content, output_file

        except Exception as e:
            logger.error(f"Error generating sector report: {e}", exc_info=True)
            raise
