# Yahoo Finance MCP Server

An MCP (Model Context Protocol) server that provides access to Yahoo Finance data using the yfinance Python package. This server enables AI assistants to fetch real-time stock quotes, historical data, financial statements, analyst recommendations, earnings information, options chains, and news.

**Built following MCP best practices** with proper tool naming, response format options, character limits, and comprehensive error handling.

## Features

This MCP server provides **10 comprehensive tools**:

### Stock Information
- **yfinance_get_stock_info**: Get comprehensive stock information (price, market cap, PE ratio, sector, etc.)
- **yfinance_get_stock_history**: Retrieve historical price data with customizable periods and intervals
- **yfinance_get_multiple_quotes**: Get current quotes for multiple stocks simultaneously
- **yfinance_search_stocks**: Search and validate stock tickers

### Financial Analysis
- **yfinance_get_stock_financials**: Access financial statements (income statement, balance sheet, cash flow)
- **yfinance_get_earnings_dates**: Get earnings calendar with historical and upcoming dates, EPS estimates
- **yfinance_get_options_chain**: Retrieve options data (calls/puts) with choice of expiration dates

### Market Intelligence
- **yfinance_get_stock_recommendations**: Get analyst recommendations and rating changes
- **yfinance_get_stock_news**: Fetch recent news articles related to stocks

### Key Features
- ✅ **Dual response formats**: JSON (structured) and Markdown (human-readable)
- ✅ **Character limits**: Automatic truncation at 25,000 characters with clear guidance
- ✅ **Tool annotations**: All tools properly annotated with `readOnlyHint` and `openWorldHint`
- ✅ **Comprehensive error handling**: Actionable error messages that guide next steps
- ✅ **MCP naming conventions**: All tools prefixed with `yfinance_` to prevent conflicts

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Setup

1. Clone or navigate to this directory:
```bash
cd yfinance-mcp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

To use this MCP server with Claude Desktop or other MCP clients, add it to your MCP settings configuration file.

### Claude Desktop Configuration

**Step 1: Edit your Claude Desktop configuration file:**

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

**Step 2: Add the server configuration:**

**Windows Configuration (Recommended):**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "cmd",
      "args": ["/c", "cd /d C:\\yfinance-mcp && C:\\yfinance-mcp\\venv\\Scripts\\python.exe -m src.yfinance_mcp"]
    }
  }
}
```

**macOS/Linux Configuration:**
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "/bin/bash",
      "args": ["-c", "cd /path/to/yfinance-mcp && ./venv/bin/python -m src.yfinance_mcp"]
    }
  }
}
```

**Important Notes:**
- Replace `C:\\yfinance-mcp` (Windows) or `/path/to/yfinance-mcp` (macOS/Linux) with your actual installation path
- The configuration uses the virtual environment's Python interpreter to ensure all dependencies are available
- Make sure you've created the venv and installed requirements before using this configuration

## Usage

### Running the Server Standalone

You can test the server by running it directly:

```bash
python src/yfinance_mcp.py
```

### Example Queries (via Claude Desktop)

Once configured with Claude Desktop, you can ask questions like:

**Stock Information:**
- "What's the current stock price of Apple?"
- "Show me comprehensive info for TSLA in JSON format"
- "Compare quotes for AAPL, MSFT, and GOOGL"
- "What sector and industry is Microsoft in?" *(uses fields parameter)*
- "Just show me the price and PE ratio for NVDA" *(uses fields parameter)*
- "Get just the basic valuation metrics for AAPL" *(uses fields parameter)*

**Historical Data:**
- "Show me Tesla's price history over the past 6 months"
- "Get AAPL historical data for the past year with weekly intervals"
- "Show me just the last week of trading data for GOOGL"
- "What were the last 30 days of price data for MSFT?" *(uses limit parameter)*
- "Give me a summary of AAPL's price performance over the last year" *(uses summary_only parameter)*
- "What's the high, low, and average price for TSLA this year?" *(uses summary_only parameter)*

**Financial Statements:**
- "Get Microsoft's income statement"
- "Show me Apple's balance sheet in JSON format"
- "What's Google's cash flow statement?"
- "What's Tesla's total revenue for the most recent quarter?" *(quarterly by default, uses fields and limit parameters)*
- "Show me just the revenue and net income for AAPL over the last 2 quarters" *(uses fields and limit parameters)*
- "Get the key profitability metrics from MSFT's latest income statement" *(uses fields and limit parameters)*
- "Show me AAPL's annual revenue for the past 3 years" *(uses period='annual' parameter)*

**Earnings & Options:**
- "When is Apple's next earnings call?"
- "Show me the earnings history for MSFT"
- "What expiration dates does SPY have for options?" *(uses dates_only=True)*
- "What are the 3 closest option expiration dates around December 15 for AAPL?" *(uses target_date="2024-12-15", max_dates=3, dates_only=True)*
- "Show me options expiring around 30 days from now for SPY" *(uses dte=30)*
- "Get 3 monthly expiration dates near 30 days out for TSLA" *(uses dte=30, max_dates=3, dates_only=True)*
- "Get the options chain for TSLA"
- "Show me the SPY options chain for weekly expiration" *(uses dte=7, shows actual option contracts)*
- "Get AAPL call options expiring in about 30 days" *(uses dte=30, option_type="calls")*
- "Show me options for the 2 closest expirations around January 15" *(uses target_date="2025-01-15", max_dates=2)*
- "Get highly liquid call options for SPY expiring next week" *(uses dte=7, min_volume, min_open_interest)*
- "Show me protective put options for AAPL with monthly expiration" *(uses dte=30, option_type="puts", in_the_money=True)*
- "What are the next 3 upcoming earnings dates for GOOGL?" *(uses future_only and limit parameters)*
- "Show me just the last 4 earnings reports for NVDA" *(uses limit parameter)*
- "When are the next earnings calls for TSLA?" *(uses future_only parameter)*

**Market Intelligence:**
- "What are the latest analyst recommendations for Google?"
- "Show me recent news about Amazon stock"
- "Get the top 5 news articles for NVDA"
- "What are the 5 most recent analyst ratings for AAPL?" *(uses limit parameter)*
- "Show me the last 10 analyst recommendations for MSFT" *(uses limit parameter)*

## Available Tools

### 1. yfinance_get_stock_info

Get comprehensive information about a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
- `fields` (list of strings, optional): Specific fields to return. Available fields: name, price, currency, market_cap, pe_ratio, forward_pe, dividend_yield, 52_week_high, 52_week_low, avg_volume, sector, industry, description. Uses case-insensitive partial matching (default: None, returns all fields)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Stock name, current price, market cap, PE ratios, dividend yield, 52-week high/low, sector, industry, description (all fields or filtered subset)

**Example:**
```python
yfinance_get_stock_info("AAPL", "json")
yfinance_get_stock_info("TSLA", fields=["price", "market_cap", "pe_ratio"])
yfinance_get_stock_info("MSFT", fields=["sector", "industry"])
```

---

### 2. yfinance_get_stock_history

Get historical price data for a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `period` (string, optional): Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: '1mo')
- `interval` (string, optional): Data interval - 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo (default: '1d')
- `limit` (int, optional): Maximum number of most recent data points to return (default: None, returns all)
- `summary_only` (bool, optional): If True, return summary statistics instead of all data points - includes high, low, avg close, total volume, start/end dates (default: False)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Historical data with dates, open, high, low, close, and volume (or summary statistics if summary_only=True)

**Example:**
```python
yfinance_get_stock_history("AAPL", "1y", "1d", "json")
yfinance_get_stock_history("AAPL", "1y", "1d", limit=30)  # Last 30 days only
yfinance_get_stock_history("AAPL", "1y", "1d", summary_only=True)  # Just summary
```

---

### 3. yfinance_get_stock_financials

Get financial statements for a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `statement_type` (string, optional): 'income', 'balance', or 'cashflow' (default: 'income')
- `period` (string, optional): 'quarterly' for quarterly reports, 'annual' for yearly reports (default: 'quarterly')
- `limit` (int, optional): Maximum number of most recent periods to return (default: 4)
- `fields` (list of strings, optional): Specific financial fields to return. Uses case-insensitive partial matching. Example fields: 'revenue', 'net income', 'total assets', 'cash', etc. (default: None, returns all fields)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Financial statement data organized by date (quarterly or annual, all fields or filtered subset)
- **Note:** Returns quarterly data by default. Most recent 4 quarters unless limit is changed.

**Example:**
```python
yfinance_get_stock_financials("AAPL", "income", "json")
yfinance_get_stock_financials("AAPL", "income", period="quarterly", limit=2)  # Last 2 quarters
yfinance_get_stock_financials("AAPL", "income", period="annual", limit=3)  # Last 3 years
yfinance_get_stock_financials("AAPL", "income", fields=["revenue", "net income"])
```

---

### 4. yfinance_get_stock_recommendations

Get analyst recommendations for a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `limit` (int, optional): Maximum number of most recent recommendations to return (default: 20)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Analyst recommendations history with firm names, grades, and actions

**Example:**
```python
yfinance_get_stock_recommendations("AAPL", "json")
yfinance_get_stock_recommendations("AAPL", limit=10)  # Last 10 recommendations only
```

---

### 5. yfinance_get_stock_news

Get recent news articles related to a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `max_items` (int, optional): Maximum number of news items (default: 10, max: 50)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Recent news articles with title, publisher, link, and publication date

**Example:**
```python
yfinance_get_stock_news("TSLA", 5, "markdown")
```

---

### 6. yfinance_get_multiple_quotes

Get current quotes for multiple stocks at once.

**Parameters:**
- `tickers` (list of strings): List of stock ticker symbols (max 20)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Current quotes for all requested tickers including price, change, and volume

**Example:**
```python
yfinance_get_multiple_quotes(["AAPL", "MSFT", "GOOGL"], "json")
```

---

### 7. yfinance_search_stocks

Search for stocks by company name or ticker symbol.

**Parameters:**
- `query` (string): Search query (company name or ticker)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Stock information if found, including ticker, name, exchange, and type

**Example:**
```python
yfinance_search_stocks("AAPL", "json")
```

---

### 8. yfinance_get_earnings_dates

Get earnings calendar information with historical and upcoming dates.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `limit` (int, optional): Maximum number of earnings dates to return (default: 12)
- `future_only` (bool, optional): If True, return only future/upcoming earnings dates (default: False)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Next earnings date
- Historical earnings with EPS estimates, reported EPS, and surprise percentages (or future only if future_only=True)

**Example:**
```python
yfinance_get_earnings_dates("AAPL", "json")
yfinance_get_earnings_dates("AAPL", limit=4)  # Last 4 earnings dates only
yfinance_get_earnings_dates("AAPL", future_only=True)  # Only upcoming earnings
```

---

### 9. yfinance_get_options_chain

Get options chain data (calls and/or puts) with advanced filtering capabilities.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `expiration_date` (string, optional): Expiration date in 'YYYY-MM-DD' format. If None, uses nearest expiration (default: None)
- `dte` (int, optional): Days to expiration - finds expiration closest to N days out. **Mutually exclusive with target_date** (default: None)
- `target_date` (string, optional): Target date in 'YYYY-MM-DD' format to find closest expiration(s) to. **Mutually exclusive with dte** (default: None)
- `max_dates` (int, optional): Number of closest expirations to return (works with dte or target_date). 1=single closest, 2=two closest, 3+=N closest (default: 1)
- `option_type` (string, optional): Type of options - 'calls', 'puts', or 'both' (default: 'calls')
- `strikes_near_price` (int, optional): Number of strikes to show above and below current price. None = all strikes (default: 10)
- `in_the_money` (boolean, optional): Filter by ITM status - True for ITM only, False for OTM only, None for all (default: None)
- `min_volume` (int, optional): Minimum trading volume filter (default: None)
- `min_open_interest` (int, optional): Minimum open interest filter (default: None)
- `strike_min` (float, optional): Minimum strike price filter (default: None)
- `strike_max` (float, optional): Maximum strike price filter (default: None)
- `dates_only` (boolean, optional): If True, return only available expiration dates without fetching contract data. Fast and efficient for exploratory queries (default: False)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- If `dates_only=True`: List of selected expiration dates (filtered by dte/target_date/max_dates if specified)
- If `max_dates=1`: Single expiration with contract data (backward compatible format)
- If `max_dates>1`: Array of expirations, each with contract data
- Otherwise: Current stock price, filters applied, and for each option: contract symbol, strike, last price, bid, ask, change, percent change, volume, open interest, implied volatility, in the money status, last trade date, contract size, currency

**Examples:**

**Getting Expiration Dates Only:**
```python
# Fast query: just get available expiration dates without contract data
yfinance_get_options_chain("SPY", dates_only=True)

# Get 3 closest expirations to 30 days from now (dates only)
yfinance_get_options_chain("SPY", dte=30, max_dates=3, dates_only=True)

# Get 2 closest expirations around December 15 (dates only)
yfinance_get_options_chain("AAPL", target_date="2024-12-15", max_dates=2, dates_only=True)
```

**Basic Usage:**
```python
# Quick check: calls near current price for nearest expiration
yfinance_get_options_chain("TSLA")

# Get nearest expiration, but show more strikes (20 above and below current price)
yfinance_get_options_chain("TSLA", strikes_near_price=20)

# See all available strikes for nearest expiration
yfinance_get_options_chain("AAPL", strikes_near_price=None)
```

**Using DTE (Days to Expiration):**
```python
# Weekly options (~7 days out)
yfinance_get_options_chain("SPY", dte=7)

# Monthly options (~30 days out)
yfinance_get_options_chain("AAPL", dte=30)

# Quarterly options (~90 days out)
yfinance_get_options_chain("MSFT", dte=90)

# LEAPS (~365 days out, longer-term options)
yfinance_get_options_chain("GOOGL", dte=365)
```

**Using Target Date and Multiple Expirations:**
```python
# Get options for expiration closest to December 15, 2024
yfinance_get_options_chain("AAPL", target_date="2024-12-15")

# Get 3 closest expirations around December 15 (full contract data for all 3)
yfinance_get_options_chain("AAPL", target_date="2024-12-15", max_dates=3)

# Get 3 monthly expirations around 30 days out
yfinance_get_options_chain("SPY", dte=30, max_dates=3)

# Get 2 closest expirations to 60 days out, calls and puts
yfinance_get_options_chain("TSLA", dte=60, max_dates=2, option_type="both")
```

**Common Trading Scenarios:**
```python
# Near-the-money calls and puts (5 strikes each side) for 30-day expiration
yfinance_get_options_chain("NVDA", dte=30, option_type="both", strikes_near_price=5)

# Out-of-the-money calls only (above current price) for weekly expiration
yfinance_get_options_chain("TSLA", dte=7, in_the_money=False, strikes_near_price=10)

# In-the-money puts (protective puts) for monthly expiration
yfinance_get_options_chain("AAPL", dte=30, option_type="puts", in_the_money=True, strikes_near_price=10)

# Near-the-money calls with tight spread (very liquid only)
yfinance_get_options_chain("SPY", dte=7, strikes_near_price=5, min_volume=1000, min_open_interest=5000)
```

**Filtering by Liquidity:**
```python
# Only show highly liquid calls (high volume and open interest)
yfinance_get_options_chain("SPY", min_volume=500, min_open_interest=1000)

# Active calls for weekly expiration
yfinance_get_options_chain("QQQ", dte=7, min_volume=100)

# Liquid monthly puts
yfinance_get_options_chain("AAPL", dte=30, option_type="puts", min_volume=50, min_open_interest=500)
```

**Specific Date and Strike Range:**
```python
# Specific expiration date with strike range
yfinance_get_options_chain("AAPL", expiration_date="2024-12-20", strike_min=150, strike_max=200)

# Puts in specific range for earnings play
yfinance_get_options_chain("TSLA", expiration_date="2024-01-19", option_type="puts", strike_min=200, strike_max=250)

# Both calls and puts for specific date, near the money
yfinance_get_options_chain("MSFT", expiration_date="2024-12-20", option_type="both", strikes_near_price=8)
```

**Filtering Tips:**
- **Default changed to 'calls'** to reduce response size and match common usage
- Use `strikes_near_price=10` (default) to get ~20 contracts centered around current price
- Use `strikes_near_price=None` to see all available strikes (may hit character limit for large chains)
- Use `dte` for more intuitive expiration selection (e.g., dte=30 for monthly options)
- `strikes_near_price` and `in_the_money` work together:
  - `strikes_near_price=10, in_the_money=False` → 10 nearest OTM strikes
  - `strikes_near_price=10, in_the_money=True` → 10 nearest ITM strikes
  - `strikes_near_price=5` → Very near-the-money options (5 ITM + 5 OTM)
- Use `min_volume` and `min_open_interest` to filter for liquid options
- Use `strike_min` and `strike_max` for custom price ranges (overrides strikes_near_price)

**Query Interpretation Guidelines:**
- **"Show me [ticker] options chain"** → Use default parameters (calls, 10 strikes, nearest expiration)
- **"Show me weekly/monthly options"** → Add `dte=7` or `dte=30` to specify expiration timeframe
- **"What options are available?"** → Exploratory query; use `option_type="both"` to show calls and puts
- **"Get highly liquid options"** → Add `min_volume` and `min_open_interest` filters
- **Don't add unsolicited filters** unless the query specifically mentions liquidity, volume, or specific strikes

---

## Response Formats

All tools support two response formats:

### JSON Format (`response_format="json"`)
- Machine-readable structured data
- Includes all available fields and metadata
- Suitable for programmatic processing
- Use when LLMs need to process data further

### Markdown Format (`response_format="markdown"`)
- Human-readable formatted text
- Uses headers, lists, and formatting for clarity
- Converts timestamps to readable format
- Default format for most queries

## Data Limits and Truncation

- **Character limit**: 25,000 characters per response
- **Automatic truncation**: Responses exceeding the limit are truncated with a clear warning
- **Guidance provided**: Truncation messages suggest using filters or pagination
- **Tool-specific limits**:
  - News: Max 50 items
  - Multiple quotes: Max 20 tickers

## Data Source

This server uses the [yfinance](https://github.com/ranaroussi/yfinance) Python library, which fetches data from Yahoo Finance. Please note:

- Data is provided for informational purposes only
- Real-time quotes may be delayed
- Historical data availability varies by ticker and exchange
- Yahoo Finance terms of service apply

## Troubleshooting

### Common Issues

1. **No data returned**: Some tickers may not be available or may be delisted. Verify the ticker symbol is correct.

2. **Rate limiting**: Yahoo Finance may rate-limit requests. If you encounter errors, try reducing the frequency of requests.

3. **Connection errors**: Ensure you have an active internet connection and that Yahoo Finance is accessible.

4. **Truncated responses**: If responses are truncated:
   - Use shorter time periods for historical data
   - Reduce `max_items` for news queries
   - Use larger intervals for historical data (e.g., '1wk' instead of '1d')

5. **Options data not available**: Not all stocks have options. Verify the ticker supports options trading.

## Development

### Testing the Server

```bash
# Verify Python syntax
python -m py_compile src/yfinance_mcp.py

# Run the server (will wait for stdio input)
python src/yfinance_mcp.py
```

### Code Formatting

This project uses Black for code formatting:

```bash
black src/
```

### Project Structure

```
yfinance-mcp/
├── src/
│   ├── __init__.py
│   └── yfinance_mcp.py          # Main server implementation
├── .gitignore
├── pyproject.toml                # Project configuration
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## MCP Best Practices Implemented

This server follows official MCP best practices:

1. ✅ **Tool naming**: All tools prefixed with `yfinance_` to prevent conflicts
2. ✅ **Response formats**: Dual format support (JSON and Markdown)
3. ✅ **Character limits**: 25,000 character limit with truncation
4. ✅ **Tool annotations**: All tools annotated with behavior hints
5. ✅ **Error handling**: Actionable error messages with guidance
6. ✅ **Comprehensive documentation**: Detailed docstrings and examples
7. ✅ **Type safety**: Full type hints throughout

## License

This project is provided as-is for educational and informational purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Disclaimer

This software is for informational purposes only. It is not financial advice. The authors and contributors are not responsible for any financial decisions made based on data provided by this tool.
