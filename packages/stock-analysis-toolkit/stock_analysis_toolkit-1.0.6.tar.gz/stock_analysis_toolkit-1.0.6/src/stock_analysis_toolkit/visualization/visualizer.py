"""
Visualization Module

This module provides functions for visualizing stock data and technical indicators.
"""

import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import plotly
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("visualization.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Set style
sns.set_theme(style="whitegrid")


class StockVisualizer:
    """Class for creating visualizations of stock data and technical indicators."""

    def __init__(self, data: pd.DataFrame, symbol: str):
        """
        Initialize the StockVisualizer.

        Args:
            data: DataFrame containing stock data and indicators
            symbol: Stock symbol (e.g., 'RELIANCE.BO')
        """
        self.data = data.copy()
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = [col[0].lower() for col in self.data.columns.values]
        else:
            self.data.columns = [str(col).lower() for col in self.data.columns]
        self.symbol = symbol
        self.company_name = self._get_company_name(symbol)
        self.output_dir = Path("reports") / "charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol."""
        # Simple mapping, can be expanded or fetched from an API
        company_map = {
            "RELIANCE.BO": "Reliance Industries",
            "TCS.BO": "Tata Consultancy Services",
            "HDFCBANK.BO": "HDFC Bank",
            "INFY.BO": "Infosys",
            "ICICIBANK.BO": "ICICI Bank",
            "HINDUNILVR.BO": "Hindustan Unilever",
            "ITC.BO": "ITC Limited",
            "BHARTIARTL.BO": "Bharti Airtel",
            "SBIN.BO": "State Bank of India",
            "KOTAKBANK.BO": "Kotak Mahindra Bank",
            "HCLTECH.BO": "HCL Technologies",
            "BAJFINANCE.BO": "Bajaj Finance",
            "LT.BO": "Larsen & Toubro",
            "ASIANPAINT.BO": "Asian Paints",
            "AXISBANK.BO": "Axis Bank",
            "MARUTI.BO": "Maruti Suzuki",
            "SUNPHARMA.BO": "Sun Pharma",
            "TITAN.BO": "Titan Company",
            "ULTRACEMCO.BO": "UltraTech Cement",
            "NESTLEIND.BO": "Nestle India",
        }
        return company_map.get(symbol, symbol.split(".")[0])

    def _figure_to_base64(self, fig, width: int = 1200, height: int = 800) -> str:
        """
        Convert a Plotly figure to a base64 encoded PNG string.
        """
        try:
            fig.update_layout(
                width=width,
                height=height,
                margin=dict(l=50, r=50, t=80, b=50),
                paper_bgcolor="white",
                plot_bgcolor="white",
            )
            img_bytes = fig.to_image(format="png", scale=2, engine="kaleido")
            base64_string = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_string}"
        except Exception as e:
            logger.warning(f"Kaleido failed: {e}. Falling back to BytesIO.")
            img_buffer = BytesIO()
            fig.write_image(img_buffer, format="png", width=width, height=height, scale=2)
            img_buffer.seek(0)
            base64_string = base64.b64encode(img_buffer.read()).decode('utf-8')
            return f"data:image/png;base64,{base64_string}"

    def _save_plot(
        self, fig, filename: str, width: int = 1200, height: int = 800, for_html_report: bool = False
    ) -> str:
        """
        Save plot as an image file or return a base64 string.

        Args:
            fig: Plotly figure object
            filename: Base filename (without extension)
            width: Image width in pixels
            height: Image height in pixels
            for_html_report: If True, return a base64 string for HTML embedding.

        Returns:
            str: Path to the saved PNG file or a base64 string.
        """
        if for_html_report:
            return self._figure_to_base64(fig, width, height)

        clean_symbol = self.symbol.replace(".", "_").lower()
        filepath = self.output_dir / f"{clean_symbol}_{filename}.png"
        try:
            fig.write_image(filepath, width=width, height=height, scale=2, engine="kaleido")
            logger.info(f"Saved plot to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save plot {filepath} with kaleido: {e}. Trying different engine.")
            fig.write_image(filepath, width=width, height=height, scale=2)
            logger.info(f"Saved plot to {filepath} with default engine.")
        return str(filepath)

    def plot_candlestick(self, days: int = 90, for_html_report: bool = False) -> str:
        """
        Create an interactive candlestick chart with volume.

        Args:
            days: Number of days to display (default: 90)
            for_html_report: If True, return a base64 string for HTML embedding.

        Returns:
            Path to the saved file or a base64 string.
        """
        logger.info(f"Creating candlestick chart for {self.symbol}")
        df = self.data.tail(days).copy()
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"{self.company_name} ({self.symbol}) - Price", "Volume"),
        )
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price",
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
            ),
            row=1,
            col=1,
        )
        colors = ["#26a69a" if close >= open_ else "#ef5350" for close, open_ in zip(df["close"], df["open"])]
        fig.add_trace(
            go.Bar(x=df.index, y=df["volume"], name="Volume", marker_color=colors, opacity=0.7),
            row=2,
            col=1,
        )
        fig.update_layout(
            title=f"{self.company_name} ({self.symbol}) - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            showlegend=False,
            template="plotly_white",
            hovermode="x unified",
            height=800,
            margin=dict(l=50, r=50, t=80, b=50),
            xaxis2_title="Date",
            yaxis2_title="Volume",
        )
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        for ma in ["ma_20", "ma_50", "ma_200"]:
            if ma in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[ma], name=ma.upper(), line=dict(width=1.5), opacity=0.7),
                    row=1,
                    col=1,
                )
        return self._save_plot(fig, f"candlestick_{days}d", for_html_report=for_html_report)

    def plot_technical_indicators(self, days: int = 180, for_html_report: bool = False) -> str:
        """
        Create a dashboard of technical indicators.

        Args:
            days: Number of days to display (default: 180)
            for_html_report: If True, return a base64 string for HTML embedding.

        Returns:
            Path to the saved file or a base64 string.
        """
        logger.info(f"Creating technical indicators dashboard for {self.symbol}")
        df = self.data.tail(days).copy()
        fig = make_subplots(
            rows=4,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.2, 0.2, 0.2],
            subplot_titles=(
                f"{self.company_name} ({self.symbol}) - Price",
                "Relative Strength Index (RSI)",
                "Moving Average Convergence Divergence (MACD)",
                "Bollinger Bands %B",
            ),
        )
        fig.add_trace(
            go.Candlestick(
                x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Price"
            ),
            row=1,
            col=1,
        )
        if all(col in df.columns for col in ["bb_upper", "bb_middle", "bb_lower"]):
            fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"], name="BB Upper", line=dict(color="rgba(200, 200, 200, 0.7)", width=1), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["bb_middle"], name="BB Middle", line=dict(color="rgba(100, 100, 100, 0.7)", width=1, dash="dash"), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"], name="BB Lower", line=dict(color="rgba(200, 200, 200, 0.7)", width=1), fill="tonexty", fillcolor="rgba(200, 200, 200, 0.1)", showlegend=False), row=1, col=1)
        if "rsi" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI", line=dict(color="#2196F3", width=2)), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
            fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, layer="below", row=2, col=1)
            fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, layer="below", row=2, col=1)
        if all(col in df.columns for col in ["macd_line", "macd_signal"]):
            fig.add_trace(go.Scatter(x=df.index, y=df["macd_line"], name="MACD", line=dict(color="#2196F3", width=2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], name="Signal", line=dict(color="#FF9800", width=1.5)), row=3, col=1)
            colors = ["#26a69a" if val >= 0 else "#ef5350" for val in df["macd_hist"]]
            fig.add_trace(go.Bar(x=df.index, y=df["macd_hist"], name="Histogram", marker_color=colors, opacity=0.7), row=3, col=1)
            fig.add_hline(y=0, line_color="black", opacity=0.5, row=3, col=1)
        if "bb_%b" in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df["bb_%b"], name="%B", line=dict(color="#9C27B0", width=2)), row=4, col=1)
            for level, color, y in [("Upper", "red", 100), ("Middle", "black", 50), ("Lower", "green", 0)]:
                fig.add_hline(y=y, line_dash="dash", line_color=color, opacity=0.5, row=4, col=1, annotation_text=level if y != 50 else "Middle", annotation_position="right")
        fig.update_layout(title=f"{self.company_name} ({self.symbol}) - Technical Indicators", showlegend=False, template="plotly_white", height=1200, margin=dict(l=50, r=50, t=100, b=50), hovermode="x unified")
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="BB %B", row=4, col=1)
        for i in range(1, 5):
            fig.update_xaxes(showgrid=True, row=i, col=1)
        return self._save_plot(fig, "technical_indicators", height=1200, for_html_report=for_html_report)

    def plot_fundamentals(self, fundamentals: Dict, for_html_report: bool = False) -> str:
        """
        Create a dashboard of fundamental metrics.

        Args:
            fundamentals: Dictionary of fundamental metrics
            for_html_report: If True, return a base64 string for HTML embedding.

        Returns:
            Path to the saved file or a base64 string.
        """
        logger.info(f"Creating fundamentals dashboard for {self.symbol}")
        metrics = [
            ("Valuation", "P/E Ratio", "pe_ratio"), ("Valuation", "Forward P/E", "forward_pe"), ("Valuation", "PEG Ratio", "peg_ratio"),
            ("Valuation", "Price/Book", "price_to_book"), ("Valuation", "Price/Sales", "price_to_sales"), ("Valuation", "Enterprise Value/Revenue", "enterprise_to_revenue"),
            ("Valuation", "Enterprise Value/EBITDA", "enterprise_to_ebitda"), ("Profitability", "Return on Equity", "return_on_equity"),
            ("Profitability", "Profit Margin", "profit_margins"), ("Profitability", "Operating Margin", "operating_margins"),
            ("Financial Health", "Debt/Equity", "debt_to_equity"), ("Financial Health", "Current Ratio", "current_ratio"),
            ("Financial Health", "Total Debt", "total_debt"), ("Financial Health", "Total Cash", "total_cash"),
            ("Dividend", "Dividend Yield", "dividend_yield"), ("Dividend", "Last Dividend Value", "last_dividend_value"),
            ("Market", "Beta", "beta"), ("Market", "52-Week High", "fifty_two_week_high"), ("Market", "52-Week Low", "fifty_two_week_low"),
            ("Market", "50-Day MA", "fifty_day_average"), ("Market", "200-Day MA", "two_hundred_day_average"),
            ("Market", "Market Cap (Cr)", "market_cap"), ("Market", "Enterprise Value (Cr)", "enterprise_value"),
        ]
        data = []
        for category, name, key in metrics:
            value = fundamentals.get(key)
            if value is not None:
                if key in ["market_cap", "enterprise_value"] and value is not None:
                    value = value / 10**7
                data.append({"Category": category, "Metric": name, "Value": value})
        if not data:
            logger.warning("No fundamental data available for visualization")
            return ""
        fig = make_subplots(
            rows=2, cols=2, subplot_titles=("Valuation Metrics", "Profitability & Growth", "Financial Health", "Dividend & Market Data"),
            vertical_spacing=0.12, horizontal_spacing=0.1, specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]],
        )
        categories = {}
        for item in data:
            if item["Category"] not in categories:
                categories[item["Category"]] = []
            categories[item["Category"]].append(item)
        category_positions = {"Valuation": (1, 1), "Profitability": (1, 2), "Financial Health": (2, 1), "Dividend": (2, 2), "Market": (2, 2)}
        for category, items in categories.items():
            row, col = category_positions.get(category, (1, 1))
            items = sorted(items, key=lambda x: abs(x["Value"]) if x["Value"] is not None else 0, reverse=True)
            x = [item["Metric"] for item in items]
            y = [item["Value"] for item in items]
            colors = []
            for item in items:
                metric = item["Metric"].lower()
                value = item["Value"]
                if value is None:
                    colors.append("lightgray")
                elif "ratio" in metric or "margin" in metric or "return" in metric:
                    colors.append("rgba(76, 175, 80, 0.7)")
                elif "debt" in metric or "beta" in metric:
                    colors.append("rgba(244, 67, 54, 0.7)" if (value or 0) > 0 else "rgba(76, 175, 80, 0.7)")
                else:
                    colors.append("rgba(33, 150, 243, 0.7)")
            fig.add_trace(
                go.Bar(
                    x=x, y=y, name=category, marker_color=colors,
                    text=[f"{v:.2f}" if isinstance(v, (int, float)) else str(v) for v in y],
                    textposition="auto", hoverinfo="text",
                    hovertext=[f"{k}: {v:.2f}" if isinstance(v, (int, float)) else f"{k}: {v}" for k, v in zip(x, y)],
                ),
                row=row, col=col,
            )
            if category == "Valuation":
                fig.add_hline(y=20, line_dash="dash", line_color="red", opacity=0.5, row=row, col=col, annotation_text="Market Avg P/E=20", annotation_position="top right")
            if category == "Financial Health":
                fig.add_hline(y=1, line_dash="dash", line_color="red", opacity=0.5, row=row, col=col, annotation_text="D/E=1", annotation_position="top right")
        fig.update_layout(title=f"{self.company_name} ({self.symbol}) - Fundamental Analysis", showlegend=False, template="plotly_white", height=1200, margin=dict(l=50, r=50, t=100, b=50), hovermode="closest")
        fig.update_yaxes(title_text="Value", row=1, col=1)
        fig.update_yaxes(title_text="Value", row=1, col=2)
        fig.update_yaxes(title_text="Value", row=2, col=1)
        fig.update_yaxes(title_text="Value", row=2, col=2)
        fig.update_xaxes(tickangle=45)
        return self._save_plot(fig, "fundamentals", height=1200, for_html_report=for_html_report)

    def generate_all_visualizations(
        self, fundamentals: Optional[Dict] = None, for_html_report: bool = False, for_email: bool = False
    ) -> Dict[str, str]:
        """
        Generate all visualizations for the stock.

        Args:
            fundamentals: Dictionary of fundamental metrics
            for_html_report: If True, generate charts as base64 strings for HTML reports
            for_email: If True, generate charts as PNG files for email attachments

        Returns:
            Dictionary of chart paths or base64 strings
        """
        logger.info(f"Generating all visualizations for {self.symbol}...")
        charts = {}
        try:
            if for_email:
                charts["candlestick_chart"] = self.plot_candlestick(days=90)
                charts["technical_indicators_chart"] = self.plot_technical_indicators(days=180)
                if fundamentals:
                    charts["fundamentals_chart"] = self.plot_fundamentals(fundamentals)
            else:
                charts["candlestick_chart"] = self.plot_candlestick(days=90, for_html_report=for_html_report)
                charts["technical_indicators_chart"] = self.plot_technical_indicators(days=180, for_html_report=for_html_report)
                if fundamentals:
                    charts["fundamentals_chart"] = self.plot_fundamentals(fundamentals, for_html_report=for_html_report)
        except Exception as e:
            logger.error(f"Error generating visualizations for {self.symbol}: {e}", exc_info=True)
        logger.info(f"Finished generating visualizations for {self.symbol}.")
        return charts

    def plot_sector_performance(
        self, sector_performance: Dict[str, float], for_html_report: bool = False
    ) -> str:
        """
        Create a bar chart of sector performance.

        Args:
            sector_performance: Dictionary with sector performance data
            for_html_report: If True, return base64 encoded image

        Returns:
            Path to the saved file or base64 encoded image, or empty string if failed.
        """
        try:
            if not sector_performance:
                logger.warning("No sector performance data provided")
                return ""

            df = pd.DataFrame.from_dict(sector_performance, orient="index").reset_index()
            df.columns = ["Sector", "Performance"]
            df = df.sort_values("Performance", ascending=False)

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=df["Sector"],
                    y=df["Performance"],
                    text=[f"{p:.2f}%" for p in df["Performance"]],
                    textposition="auto",
                    marker_color=[
                        "rgba(76, 175, 80, 0.7)" if p > 0 else "rgba(244, 67, 54, 0.7)"
                        for p in df["Performance"]
                    ],
                    name="Performance",
                )
            )

            fig.update_layout(
                title={
                    "text": "Sector Performance (1M Return %)",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 20},
                },
                xaxis={"title": "Sector", "tickangle": -45, "tickfont": {"size": 10}},
                yaxis={"title": "1M Return (%)"},
                plot_bgcolor="rgba(240, 240, 240, 0.95)",
                paper_bgcolor="white",
                margin=dict(l=50, r=50, t=80, b=120),
                height=600,
                hovermode="x unified",
                showlegend=False,
            )

            return self._save_plot(fig, "sector_performance", for_html_report=for_html_report)

        except Exception as e:
            logger.error(f"Error creating sector performance chart: {e}", exc_info=True)
            return ""


if __name__ == "__main__":
    # Example usage
    import yfinance as yf

    # Fetch sample data
    symbol = "RELIANCE.BO"
    data = yf.download(symbol, period="1y")

    # Initialize visualizer
    visualizer = StockVisualizer(data, symbol)

    # Generate visualizations
    visualizations = visualizer.generate_all_visualizations()

    print("Generated visualizations:")
    for name, path in visualizations.items():
        print(f"- {name}: {path}")
