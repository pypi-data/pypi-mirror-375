# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.35] - 2025-09-10
### Added
- Mutual Fund Summary section to the email report, showing per-fund RSI, 1Y/3Y/5Y CAGR, and annualized volatility.
- Tooltip info icons for key metrics (RSI, SMA, EMA, MACD, Bollinger Bands, P/E, P/B, CAGR, Drawdown, Std Dev) across stock and mutual fund sections.

### Changed
- Kept Market Indices section at the top of the email and preserved detailed mutual fund analysis below the new summary.

## [1.0.36] - 2025-09-10
### Added
- Metrics Glossary section with anchor links and "Back to Top" links.
- Single "Metrics Legend" at the top with one set of "i" links pointing to glossary items.

### Fixed
- Removed repeated inline "i" icons from tables to avoid duplication and improve clarity.

## [1.0.37] - 2025-09-10
### Added
- Corporate Bond Analysis from CSV input: computes YTM, current yield, accrued interest, dirty/clean price, Macaulay/Modified duration, convexity, and spread vs benchmark.
- CLI flags: `--bonds-csv` (path to CSV) and `--benchmark-yield` (percent).
- Email template: Corporate Bonds Summary and Details sections; glossary extended with fixed-income metrics.

## [1.0.34] - 2025-09-10
### Added
- **Mutual Fund Analysis**: Added core functionality to fetch and analyze mutual fund data by scheme code or name.
- **Index Analysis & Provider Fallbacks**:
    - Implemented robust index data fetching with fallbacks for Yahoo Finance, Marketstack, Finnhub, and a placeholder for Indian APIs.
    - Added a `config/index_symbol_map.json` to manage provider-specific index symbols without code changes.
- **Enhanced Email Reports**:
    - Moved the Market Indices section to the top of the email for better visibility.
    - Added new columns to the index table: `1W`, `1M` returns, and `200D MA`.
    - Added visual chips for `1D Change` (Up/Down) and `SMA 20/50 Crossover` (Bullish/Bearish).
- **Email Attachments**: The HTML report is now attached to the email in addition to being in the body.

### Fixed
- Resolved email delivery issues by improving SMTP configuration loading from `.env` files and adding detailed SMTP logging.
- Corrected syntax errors in the data fetching module to ensure provider fallbacks work correctly.

## [1.0.1] - 2025-08-30
### Added
- Type checking support with mypy configuration
- Type stubs for better code quality (pandas-stubs, types-requests, types-seaborn)
- GitHub Actions workflow improvements for better CI/CD

### Changed
- Updated dependencies to latest stable versions
- Improved error handling in data fetching components
- Enhanced documentation and type hints

### Fixed
- Resolved workflow issues with unsupported command-line arguments
- Fixed type checking errors throughout the codebase
- Improved handling of optional dependencies
- Fixed issues with email reporting and chart generation

## [1.0.0] - 2025-08-27
### Added
- Initial stable release of Stock Analysis Toolkit
- Core functionality for stock data fetching and analysis
- Support for multiple data sources including yfinance and Alpha Vantage
- Technical analysis indicators and visualization tools
- Email reporting capabilities
- GitHub Actions workflow for automated testing and deployment
- Comprehensive test suite for data fetching and analysis

### Changed
- Migrated to Pydantic v2 with updated validator syntax
- Improved error handling and logging throughout the codebase
- Better documentation and type hints for all public APIs
- Enhanced data validation and error messages
- Updated dependencies to their latest stable versions
- Improved handling of missing or incomplete market data

### Fixed
- Resolved SSL/TLS handshake issues with yfinance
- Fixed NIFTY 50 PE ratio fetching with proper error handling
- Addressed various bugs and performance issues
- Fixed test functions to use proper assertions
- Resolved deprecation warnings in yfinance integration
- Improved handling of edge cases in data processing

### Security
- Secured GitHub Actions workflow to handle sensitive data
- Removed hardcoded credentials and API keys
- Added input validation for all external data sources
- Improved error handling for API rate limiting and timeouts
