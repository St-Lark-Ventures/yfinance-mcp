"""
Yahoo Finance MCP Server

This MCP server provides tools to access Yahoo Finance data using the yfinance package.
Follows MCP best practices for tool naming, response formats, and error handling.
"""

from typing import Optional, List, Literal
import yfinance as yf
from datetime import datetime, timedelta
from fastmcp import FastMCP
import json

# Constants
CHARACTER_LIMIT = 25000

# Initialize the FastMCP server
mcp = FastMCP("Yahoo Finance MCP Server")


def format_response(data: dict, response_format: str = "markdown") -> str:
    """
    Format response data as either JSON or Markdown.

    Args:
        data: Dictionary containing the response data
        response_format: Either "json" or "markdown"

    Returns:
        Formatted string response
    """
    if response_format == "json":
        result = json.dumps(data, indent=2, default=str)
    else:  # markdown
        result = _format_as_markdown(data)

    # Check character limit
    if len(result) > CHARACTER_LIMIT:
        truncated_result = result[:CHARACTER_LIMIT]
        truncation_msg = f"\n\n⚠️ Response truncated at {CHARACTER_LIMIT} characters. Use filters or pagination to reduce results."
        return truncated_result + truncation_msg

    return result


def _format_as_markdown(data: dict) -> str:
    """Convert dictionary data to human-readable Markdown format."""
    if "error" in data:
        return f"❌ **Error**: {data['error']}"

    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"\n**{key.replace('_', ' ').title()}:**")
            for sub_key, sub_value in value.items():
                lines.append(f"  - {sub_key}: {sub_value}")
        elif isinstance(value, list):
            lines.append(f"\n**{key.replace('_', ' ').title()}:**")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"\n  ---")
                    for sub_key, sub_value in item.items():
                        lines.append(f"  - {sub_key}: {sub_value}")
                else:
                    lines.append(f"  - {item}")
        else:
            lines.append(f"**{key.replace('_', ' ').title()}:** {value}")

    return "\n".join(lines)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_stock_info(
    ticker: str,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get comprehensive information about a stock including price, market cap, ratios, and company details.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        response_format: Output format - 'json' for structured data, 'markdown' for human-readable (default: 'markdown')

    Returns:
        Formatted string containing stock information including:
        - Current price and currency
        - Market capitalization
        - PE ratios (trailing and forward)
        - Dividend yield
        - 52-week high/low
        - Average volume
        - Sector and industry
        - Company description

    Example:
        yfinance_get_stock_info("AAPL", "json")
        yfinance_get_stock_info("TSLA", "markdown")
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract key information
        result = {
            "ticker": ticker,
            "name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "currency": info.get("currency", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "avg_volume": info.get("averageVolume", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": info.get("longBusinessSummary", "N/A")[:500] if info.get("longBusinessSummary") else "N/A",
        }

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch stock info for {ticker}: {str(e)}. Verify the ticker symbol is correct."}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_stock_history(
    ticker: str,
    period: str = "1mo",
    interval: str = "1d",
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get historical price data for a stock with customizable time period and interval.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        period: Time period - valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: '1mo')
        interval: Data interval - valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo (default: '1d')
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string with historical price data including dates, open, high, low, close, volume.
        Large datasets may be truncated; use shorter periods or larger intervals to reduce size.

    Example:
        yfinance_get_stock_history("AAPL", "1y", "1d", "json")
        yfinance_get_stock_history("MSFT", "3mo", "1wk", "markdown")
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return format_response({"error": f"No historical data found for {ticker} with period={period}, interval={interval}"}, response_format)

        # Convert to serializable format
        result = {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "count": len(hist),
            "data": []
        }

        for index, row in hist.iterrows():
            result["data"].append({
                "date": index.strftime("%Y-%m-%d %H:%M:%S"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            })

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch history for {ticker}: {str(e)}. Check period and interval parameters."}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_stock_financials(
    ticker: str,
    statement_type: Literal["income", "balance", "cashflow"] = "income",
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get financial statements for a stock (income statement, balance sheet, or cash flow statement).

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        statement_type: Type of financial statement - 'income', 'balance', or 'cashflow' (default: 'income')
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing the requested financial statement organized by date.
        Typically includes 4 quarters of data.

    Example:
        yfinance_get_stock_financials("AAPL", "income", "json")
        yfinance_get_stock_financials("GOOGL", "balance", "markdown")
    """
    try:
        stock = yf.Ticker(ticker)

        if statement_type == "income":
            financials = stock.financials
            statement_name = "Income Statement"
        elif statement_type == "balance":
            financials = stock.balance_sheet
            statement_name = "Balance Sheet"
        elif statement_type == "cashflow":
            financials = stock.cashflow
            statement_name = "Cash Flow Statement"
        else:
            return format_response({"error": f"Invalid statement_type: {statement_type}. Use 'income', 'balance', or 'cashflow'"}, response_format)

        if financials.empty:
            return format_response({"error": f"No {statement_name.lower()} data found for {ticker}"}, response_format)

        # Convert to serializable format
        result = {
            "ticker": ticker,
            "statement_type": statement_name,
            "data": {}
        }

        for column in financials.columns:
            date_key = column.strftime("%Y-%m-%d")
            result["data"][date_key] = {}
            for index in financials.index:
                value = financials.loc[index, column]
                if not (hasattr(value, '__iter__') and not isinstance(value, str)):
                    result["data"][date_key][str(index)] = float(value) if value == value else None  # NaN check

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch financials for {ticker}: {str(e)}"}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_stock_recommendations(
    ticker: str,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get analyst recommendations and rating changes for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing analyst recommendations history including:
        - Date of recommendation
        - Firm name
        - Rating change (to grade, from grade)
        - Action taken

    Example:
        yfinance_get_stock_recommendations("AAPL", "json")
    """
    try:
        stock = yf.Ticker(ticker)
        # Use upgrades_downgrades which has firm, toGrade, fromGrade, action columns
        recommendations = stock.upgrades_downgrades

        if recommendations is None or recommendations.empty:
            return format_response({"error": f"No recommendations found for {ticker}"}, response_format)

        result = {
            "ticker": ticker,
            "recommendations": []
        }

        for index, row in recommendations.iterrows():
            # Handle index that might be datetime or other type
            if hasattr(index, 'strftime'):
                date_str = index.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = str(index)

            rec = {
                "date": date_str,
                "firm": str(row.get("firm", row.get("Firm", "N/A"))),
                "to_grade": str(row.get("toGrade", row.get("To Grade", "N/A"))),
                "from_grade": str(row.get("fromGrade", row.get("From Grade", "N/A"))),
                "action": str(row.get("action", row.get("Action", "N/A")))
            }
            result["recommendations"].append(rec)

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch recommendations for {ticker}: {str(e)}"}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_stock_news(
    ticker: str,
    max_items: int = 10,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get recent news articles related to a stock.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        max_items: Maximum number of news items to return (default: 10, max: 50)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing recent news articles with:
        - Article title
        - Publisher name
        - Publication date and time
        - Article link
        - Article type

    Example:
        yfinance_get_stock_news("TSLA", 5, "markdown")
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            return format_response({"error": f"No news found for {ticker}"}, response_format)

        result = {
            "ticker": ticker,
            "news": []
        }

        # Limit max_items to prevent overwhelming responses
        max_items = min(max_items, 50)

        for item in news[:max_items]:
            # If item is a dict, extract values normally
            if isinstance(item, dict):
                # Handle various possible timestamp fields
                published_time = item.get("providerPublishTime") or item.get("publishTime") or item.get("published")
                if published_time:
                    try:
                        if isinstance(published_time, int):
                            published_str = datetime.fromtimestamp(published_time).strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            published_str = str(published_time)
                    except:
                        published_str = "N/A"
                else:
                    published_str = "N/A"

                article = {
                    "title": item.get("title", "N/A"),
                    "publisher": item.get("publisher", "N/A"),
                    "link": item.get("link", "N/A"),
                    "published": published_str,
                    "type": item.get("type", "N/A"),
                }
            else:
                # If item is not a dict, try to convert to string representation
                article = {
                    "title": str(item) if item else "N/A",
                    "publisher": "N/A",
                    "link": "N/A",
                    "published": "N/A",
                    "type": "N/A",
                }

            result["news"].append(article)

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch news for {ticker}: {str(e)}"}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_multiple_quotes(
    tickers: List[str],
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get current quotes for multiple stocks at once in a single request.

    Args:
        tickers: List of stock ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing current quotes for all requested tickers including:
        - Company name
        - Current price
        - Currency
        - Price change and percent change
        - Trading volume

    Example:
        yfinance_get_multiple_quotes(["AAPL", "MSFT", "GOOGL"], "json")
    """
    try:
        result = {
            "quotes": {},
            "errors": []
        }

        for ticker in tickers[:20]:  # Limit to 20 tickers to prevent overwhelming responses
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                result["quotes"][ticker] = {
                    "name": info.get("longName", "N/A"),
                    "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                    "currency": info.get("currency", "N/A"),
                    "change": info.get("regularMarketChange", "N/A"),
                    "change_percent": info.get("regularMarketChangePercent", "N/A"),
                    "volume": info.get("regularMarketVolume", "N/A"),
                }
            except Exception as e:
                result["errors"].append(f"{ticker}: {str(e)}")

        if len(tickers) > 20:
            result["warning"] = f"Limited to first 20 tickers out of {len(tickers)} requested"

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch quotes: {str(e)}"}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_search_stocks(
    query: str,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Search for stocks by company name or ticker symbol to verify ticker validity.

    Args:
        query: Search query (company name or ticker symbol)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing search results with:
        - Whether stock was found
        - Ticker symbol
        - Company name
        - Exchange
        - Security type

    Example:
        yfinance_search_stocks("AAPL", "json")
        yfinance_search_stocks("Apple", "markdown")

    Note: yfinance has limited search capabilities. This tool validates if a ticker exists.
    """
    try:
        # Note: yfinance doesn't have a direct search API, so we'll use the Ticker's info
        # This is a simple implementation that checks if the query is a valid ticker
        stock = yf.Ticker(query.upper())
        info = stock.info

        if info and "symbol" in info:
            result = {
                "found": True,
                "ticker": info.get("symbol", query.upper()),
                "name": info.get("longName", "N/A"),
                "exchange": info.get("exchange", "N/A"),
                "type": info.get("quoteType", "N/A"),
            }
        else:
            result = {
                "found": False,
                "message": f"No stock found for query: {query}. Try using the exact ticker symbol."
            }

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Search failed: {str(e)}. Try using the exact ticker symbol instead."}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_earnings_dates(
    ticker: str,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get earnings calendar information including historical and upcoming earnings dates with estimates.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing earnings information including:
        - Earnings dates (historical and upcoming)
        - EPS estimates
        - Reported EPS (for historical dates)
        - Surprise percentage (actual vs estimate)

    Example:
        yfinance_get_earnings_dates("AAPL", "json")
        yfinance_get_earnings_dates("MSFT", "markdown")
    """
    try:
        stock = yf.Ticker(ticker)

        # Get earnings dates
        earnings_dates = stock.earnings_dates

        # Get next earnings date from info
        info = stock.info
        next_earnings = info.get("earningsTimestamp")

        if earnings_dates is None or earnings_dates.empty:
            return format_response({"error": f"No earnings dates found for {ticker}"}, response_format)

        result = {
            "ticker": ticker,
            "next_earnings_date": datetime.fromtimestamp(next_earnings).strftime("%Y-%m-%d %H:%M:%S") if next_earnings else "N/A",
            "earnings_history": []
        }

        for index, row in earnings_dates.iterrows():
            earnings_info = {
                "date": index.strftime("%Y-%m-%d") if hasattr(index, 'strftime') else str(index),
                "eps_estimate": float(row.get("EPS Estimate", 0)) if row.get("EPS Estimate") == row.get("EPS Estimate") else None,  # NaN check
                "eps_reported": float(row.get("Reported EPS", 0)) if row.get("Reported EPS") == row.get("Reported EPS") else None,
                "surprise_percent": float(row.get("Surprise(%)", 0)) if row.get("Surprise(%)") == row.get("Surprise(%)") else None,
            }
            result["earnings_history"].append(earnings_info)

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch earnings dates for {ticker}: {str(e)}"}, response_format)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
def yfinance_get_options_chain(
    ticker: str,
    expiration_date: Optional[str] = None,
    option_type: Literal["calls", "puts", "both"] = "both",
    in_the_money: Optional[bool] = None,
    min_volume: Optional[int] = None,
    min_open_interest: Optional[int] = None,
    strike_min: Optional[float] = None,
    strike_max: Optional[float] = None,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get options chain data (calls and/or puts) for a stock with filtering capabilities.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        expiration_date: Specific expiration date in 'YYYY-MM-DD' format. If None, uses nearest expiration (default: None)
        option_type: Type of options to return - 'calls', 'puts', or 'both' (default: 'both')
        in_the_money: Filter by ITM status - True for ITM only, False for OTM only, None for all (default: None)
        min_volume: Minimum trading volume filter (default: None)
        min_open_interest: Minimum open interest filter (default: None)
        strike_min: Minimum strike price filter (default: None)
        strike_max: Maximum strike price filter (default: None)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing options data including:
        - Available expiration dates (if no date specified)
        - Selected expiration date and filters applied
        - For each option: contract symbol, strike, last price, bid, ask, change, percent change,
          volume, open interest, implied volatility, in the money status, last trade date,
          contract size, currency

    Example:
        yfinance_get_options_chain("AAPL")  # All options, nearest expiration
        yfinance_get_options_chain("AAPL", option_type="calls")  # Calls only
        yfinance_get_options_chain("AAPL", in_the_money=True, min_volume=100)  # ITM with volume >= 100
        yfinance_get_options_chain("AAPL", "2024-12-20", "puts", strike_min=150, strike_max=200)  # Puts in strike range

    Note: To see available expiration dates, call this tool without specifying an expiration_date.
    """
    try:
        stock = yf.Ticker(ticker)

        # Get available expiration dates
        available_expirations = stock.options

        if not available_expirations:
            return format_response({"error": f"No options data available for {ticker}"}, response_format)

        # If no expiration specified, return available dates and use nearest
        if expiration_date is None:
            expiration_date = available_expirations[0]
            show_available = True
        else:
            show_available = False
            # Validate the provided expiration date
            if expiration_date not in available_expirations:
                return format_response({
                    "error": f"Expiration date {expiration_date} not available for {ticker}",
                    "available_expirations": list(available_expirations)
                }, response_format)

        # Get options chain for the specified expiration
        opt_chain = stock.option_chain(expiration_date)

        result = {
            "ticker": ticker,
            "expiration_date": expiration_date,
            "filters_applied": {
                "option_type": option_type,
                "in_the_money": in_the_money,
                "min_volume": min_volume,
                "min_open_interest": min_open_interest,
                "strike_range": f"{strike_min} to {strike_max}" if strike_min or strike_max else None
            }
        }

        if show_available:
            result["available_expirations"] = list(available_expirations)

        def process_options(df, option_label):
            """Process and filter options dataframe"""
            options_data = []
            for _, row in df.iterrows():
                # Apply filters
                if in_the_money is not None and row.get("inTheMoney", False) != in_the_money:
                    continue
                if min_volume is not None and (row["volume"] != row["volume"] or row["volume"] < min_volume):
                    continue
                if min_open_interest is not None and (row["openInterest"] != row["openInterest"] or row["openInterest"] < min_open_interest):
                    continue
                if strike_min is not None and row["strike"] < strike_min:
                    continue
                if strike_max is not None and row["strike"] > strike_max:
                    continue

                # Extract all available data
                option_data = {
                    "contract_symbol": str(row.get("contractSymbol", "N/A")),
                    "strike": float(row["strike"]),
                    "last_price": float(row["lastPrice"]),
                    "bid": float(row["bid"]),
                    "ask": float(row["ask"]),
                    "change": float(row["change"]) if row.get("change") == row.get("change") else None,  # NaN check
                    "percent_change": float(row["percentChange"]) if row.get("percentChange") == row.get("percentChange") else None,
                    "volume": int(row["volume"]) if row["volume"] == row["volume"] else 0,
                    "open_interest": int(row["openInterest"]) if row["openInterest"] == row["openInterest"] else 0,
                    "implied_volatility": float(row["impliedVolatility"]) if row["impliedVolatility"] == row["impliedVolatility"] else None,
                    "in_the_money": bool(row.get("inTheMoney", False)),
                    "last_trade_date": str(row.get("lastTradeDate", "N/A")),
                    "contract_size": str(row.get("contractSize", "REGULAR")),
                    "currency": str(row.get("currency", "USD"))
                }
                options_data.append(option_data)

            return options_data

        # Process based on option_type
        if option_type in ["calls", "both"]:
            calls_data = process_options(opt_chain.calls, "calls")
            result["calls_count"] = len(calls_data)
            result["calls"] = calls_data

        if option_type in ["puts", "both"]:
            puts_data = process_options(opt_chain.puts, "puts")
            result["puts_count"] = len(puts_data)
            result["puts"] = puts_data

        # Add summary stats
        if option_type == "both":
            result["total_options"] = result.get("calls_count", 0) + result.get("puts_count", 0)
        elif option_type == "calls":
            result["total_options"] = result.get("calls_count", 0)
        else:
            result["total_options"] = result.get("puts_count", 0)

        return format_response(result, response_format)
    except Exception as e:
        return format_response({"error": f"Failed to fetch options chain for {ticker}: {str(e)}"}, response_format)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
