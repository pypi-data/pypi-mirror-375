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

Once installed, you can use the `stock-analyzer` command from your terminal.

### Command-Line Interface

```bash
stock-analyzer --help
```

```
usage: stock-analyzer [-h] [-s STOCKS] [-mf MUTUAL_FUNDS [MUTUAL_FUNDS ...]] [--mf-codes MF_CODES [MF_CODES ...]] [-d DAYS] [-e EMAIL] [--no-cache] [-v] [--send-email]

Stock and Mutual Fund Analysis Tool

options:
  -h, --help            show this help message and exit
  -s STOCKS, --stocks STOCKS
                        Stock symbol to analyze. Can be specified multiple times (e.g., -s RELIANCE.NS -s TCS.NS)
  -mf MUTUAL_FUNDS [MUTUAL_FUNDS ...], --mutual_funds MUTUAL_FUNDS [MUTUAL_FUNDS ...]
                        Mutual fund name to analyze. Can be specified multiple times. For multi-word names, wrap in quotes.
  --mf-codes MF_CODES [MF_CODES ...]
                        Mutual fund scheme codes to analyze. Can be specified multiple times (e.g., --mf-codes 108467 120757).
  -d DAYS, --days DAYS  Number of days for historical data analysis (default: 90)
  -e EMAIL, --email EMAIL
                        Email address to send the report to.
  --no-cache            Disable caching of analysis results
  -v, --verbose         Enable verbose logging for debugging
  --send-email          Flag to send the report via email. Requires --email to be set.
```

### Sample Run Command

Here is an example command to analyze two stocks and two mutual funds, and then email the report:

```bash
stock-analyzer -s RELIANCE.NS -s TCS.NS --mf-codes 107578 120465 -e your-email@example.com --send-email
```
This command analyzes Reliance and TCS, along with the mutual funds for "Mirae Asset Large Cap Fund" (107578) and "Axis Bluechip Fund" (120465).


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
