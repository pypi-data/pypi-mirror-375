# Stock Analysis Toolkit

[![PyPI version](https://img.shields.io/pypi/v/stock-analysis-toolkit.svg)](https://pypi.org/project/stock-analysis-toolkit/)
[![Python Version](https://img.shields.io/pypi/pyversions/stock-analysis-toolkit.svg)](https://pypi.org/project/stock-analysis-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python toolkit for analyzing stocks using technical and fundamental analysis. This package provides tools to fetch stock data, perform in-depth analysis, generate visualizations, and create detailed reports.

## ✨ Features

- **Multi-source Data Collection**
  - BSE stocks (e.g., `500325.BO` for RELIANCE)
  - NSE stocks (e.g., `RELIANCE.NS` or `NSE:RELIANCE`)
  - Market indices (e.g., `^NSEI` for NIFTY 50)
  - Mutual funds (by name or code)

- **Technical Analysis**
  - RSI, MACD, Bollinger Bands
  - Moving Averages (SMA, EMA)
  - Volume indicators
  - Custom technical indicators

- **Fundamental Analysis**
  - P/E, P/B, P/S ratios
  - ROE, ROA, and other profitability metrics
  - Debt/Equity and other leverage ratios
  - Dividend yield and history

- **Reporting & Visualization**
  - Interactive charts with Plotly
  - Detailed HTML reports
  - Email notifications with reports
  - Custom report templates

## 🚀 Installation

### Basic Installation
```bash
pip install stock-analysis-toolkit
```

### With Optional Dependencies
```bash
pip install "stock-analysis-toolkit[full]"
```

### For Development
```bash
git clone https://github.com/pranav87/stock_analysis.git
cd stock_analysis
pip install -e ".[dev]"
```

### TA-Lib Installation (Required for Technical Analysis)
- **macOS**: `brew install ta-lib`
- **Linux**: `sudo apt-get install -y python3-ta-lib`
- **Windows**: Download the appropriate wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)

## 📝 Configuration

Create a `.env` file in your project root with the following variables:
```
# Required for Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Optional: Email settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_specific_password
```
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_specific_password
   ```

## Usage

### Basic Usage

Analyze the top 10 BSE stocks:
```bash
python src/main.py
```

### Command Line Options

```
usage: main.py [-h] [--stocks [STOCKS ...]] [--days DAYS] [--email EMAIL]
              [--report-dir REPORT_DIR] [--top TOP] [--all]

Stock Analysis Tool

optional arguments:
  -h, --help            show this help message and exit
  --stocks [STOCKS ...] List of stock symbols to analyze (e.g., RELIANCE.BO TCS.BO)
  --days DAYS           Number of days of historical data to fetch (default: 365)
  --email EMAIL         Email address to send the report to
  --report-dir REPORT_DIR
                        Directory to save the report (default: reports)
  --top TOP             Analyze top N BSE stocks by market cap
  --all                 Analyze all top BSE stocks
```

### Examples

1. Analyze specific stocks:
   ```bash
   python3 src/main.py --stocks RELIANCE.BO TCS.BO HDFCBANK.BO
   ```

2. Analyze top 5 BSE stocks and email the report:
   ```bash
   python3 src/main.py --top 5 --email your-email@example.com
   ```

3. Analyze all top BSE stocks with 2 years of data:
   ```bash
   python3 src/main.py --all --days 730
   ```

4. Analyze NIFTY50 index:
   ```bash
   python3 src/main.py --stocks ^NSEI --days 365
   python3 src/main.py --stocks ^NSEI --days 365 --email your-email@example.com
   ```

5. Analyze top 10 BSE stocks and email the report:
   ```bash
   python3 src/main.py --top 10 --email your-email@example.com
   ```

6. Analyze top 10 BSE stocks and email the report:
   ```bash
   cd HOME_PATH/stock_analysis && PYTHONPATH=HOME_PATH/stock_analysis python3 -m src.main --email your-email@example.com
   ```

7. Analyze specific mutual funds:
   ```bash
   python3 src/main.py --stocks RELIANCE.NS --mutual_funds "ICICI Prudential Equity & Debt Fund - Monthly IDCW" --email your-email@anywhere.com
   ```


## Project Structure

```
stock-analysis/
├── config/                 # Configuration files
│   └── config.py           # Application configuration
├── data/                   # Data storage
│   └── cache/              # Cached stock data
├── logs/                   # Log files
├── reports/                # Generated reports
│   └── charts/             # Chart visualizations
├── src/                    # Source code
│   ├── data_fetcher.py     # Data collection from APIs
│   ├── technical_analysis.py # Technical indicators and analysis
│   ├── visualization.py    # Data visualization
│   └── main.py             # Main application and CLI
├── .env.example            # Example environment variables
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Supported Stock Exchanges

- **BSE (Bombay Stock Exchange)**: Use `.BO` suffix (e.g., `RELIANCE.BO`)
- **NSE (National Stock Exchange)**: Use `.NS` suffix (e.g., `RELIANCE.NS`)

## Data Sources

- Primary: Google Finance
- Fallback: Yahoo Finance
- Additional: Alpha Vantage (for fundamental data, requires API key)

## Email Configuration

To enable email notifications:

1. Enable "Less secure app access" in your Gmail account settings or generate an App Password
2. Set the following environment variables in your `.env` file:
   ```
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_specific_password
   ```

## Limitations

- Free API tiers may have rate limits
- Some fundamental data may not be available for all stocks
- Analysis should be used for informational purposes only

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with a licensed financial advisor before making investment decisions.
