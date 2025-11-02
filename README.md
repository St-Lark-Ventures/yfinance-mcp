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

**Historical Data:**
- "Show me Tesla's price history over the past 6 months"
- "Get AAPL historical data for the past year with weekly intervals"

**Financial Statements:**
- "Get Microsoft's income statement"
- "Show me Apple's balance sheet in JSON format"
- "What's Google's cash flow statement?"

**Earnings & Options:**
- "When is Apple's next earnings call?"
- "Show me the earnings history for MSFT"
- "Get the options chain for TSLA"
- "Show me AAPL options expiring on 2024-12-20"

**Market Intelligence:**
- "What are the latest analyst recommendations for Google?"
- "Show me recent news about Amazon stock"
- "Get the top 5 news articles for NVDA"

## Available Tools

### 1. yfinance_get_stock_info

Get comprehensive information about a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Stock name, current price, market cap, PE ratios, dividend yield, 52-week high/low, sector, industry, description

**Example:**
```python
yfinance_get_stock_info("AAPL", "json")
```

---

### 2. yfinance_get_stock_history

Get historical price data for a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `period` (string, optional): Time period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: '1mo')
- `interval` (string, optional): Data interval - 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo (default: '1d')
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Historical data with dates, open, high, low, close, and volume

**Example:**
```python
yfinance_get_stock_history("AAPL", "1y", "1d", "json")
```

---

### 3. yfinance_get_stock_financials

Get financial statements for a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `statement_type` (string, optional): 'income', 'balance', or 'cashflow' (default: 'income')
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Financial statement data organized by date (typically 4 quarters)

**Example:**
```python
yfinance_get_stock_financials("AAPL", "income", "json")
```

---

### 4. yfinance_get_stock_recommendations

Get analyst recommendations for a stock.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Analyst recommendations history with firm names, grades, and actions

**Example:**
```python
yfinance_get_stock_recommendations("AAPL", "json")
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
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Next earnings date
- Historical earnings with EPS estimates, reported EPS, and surprise percentages

**Example:**
```python
yfinance_get_earnings_dates("AAPL", "json")
```

---

### 9. yfinance_get_options_chain

Get options chain data (calls and/or puts) with advanced filtering capabilities.

**Parameters:**
- `ticker` (string): Stock ticker symbol
- `expiration_date` (string, optional): Expiration date in 'YYYY-MM-DD' format. If None, uses nearest expiration (default: None)
- `option_type` (string, optional): Type of options - 'calls', 'puts', or 'both' (default: 'both')
- `in_the_money` (boolean, optional): Filter by ITM status - True for ITM only, False for OTM only, None for all (default: None)
- `min_volume` (int, optional): Minimum trading volume filter (default: None)
- `min_open_interest` (int, optional): Minimum open interest filter (default: None)
- `strike_min` (float, optional): Minimum strike price filter (default: None)
- `strike_max` (float, optional): Maximum strike price filter (default: None)
- `response_format` (string, optional): 'json' or 'markdown' (default: 'markdown')

**Returns:**
- Available expiration dates (when no date specified)
- Filters applied
- For each option: contract symbol, strike, last price, bid, ask, change, percent change, volume, open interest, implied volatility, in the money status, last trade date, contract size, currency

**Example:**
```python
# Get all options for nearest expiration
yfinance_get_options_chain("AAPL")

# Get only calls
yfinance_get_options_chain("AAPL", option_type="calls")

# Get ITM options with volume >= 100
yfinance_get_options_chain("AAPL", in_the_money=True, min_volume=100)

# Get puts in specific strike range
yfinance_get_options_chain("AAPL", "2024-12-20", "puts", strike_min=150, strike_max=200)

# Get liquid calls (high volume and open interest)
yfinance_get_options_chain("AAPL", option_type="calls", min_volume=500, min_open_interest=1000)
```

**Filtering Tips:**
- Use `option_type` to reduce response size when only calls or puts are needed
- Use `in_the_money` to focus on ITM or OTM options
- Use `min_volume` and `min_open_interest` to filter for liquid options
- Use `strike_min` and `strike_max` to focus on specific price ranges

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
