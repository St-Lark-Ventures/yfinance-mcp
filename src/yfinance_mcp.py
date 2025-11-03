"""
Yahoo Finance MCP Server

This MCP server provides tools to access Yahoo Finance data using the yfinance package.
Follows MCP best practices for tool naming, response formats, and error handling.
"""

from typing import Optional, List, Literal, Union
import yfinance as yf
from datetime import datetime, timedelta
from fastmcp import FastMCP
import json
import pandas as pd

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
    fields: Optional[Union[List[str], str]] = None,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get comprehensive information about a stock including price, market cap, ratios, and company details.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        fields: Optional list of field names to include (case-insensitive partial matching).
                Available fields: name, price, currency, market_cap, pe_ratio, forward_pe,
                dividend_yield, 52_week_high, 52_week_low, avg_volume, sector, industry, description
                (default: None, returns all fields)
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
        yfinance_get_stock_info("TSLA", ["price", "market_cap", "pe_ratio"], "markdown")
        yfinance_get_stock_info("MSFT", fields=["sector", "industry"])
    """
    try:
        # Handle fields parameter if passed as JSON string
        if fields is not None and isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as a single field
                fields = [fields]

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

        # Filter fields if specified
        if fields is not None and len(fields) > 0:
            filtered_result = {"ticker": ticker}  # Always include ticker
            available_fields = list(result.keys())

            for field in fields:
                field_lower = field.lower()
                # Find matching field using case-insensitive partial matching
                for available_field in available_fields:
                    if field_lower in available_field.lower():
                        filtered_result[available_field] = result[available_field]
                        break

            result = filtered_result

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
    limit: Optional[int] = None,
    summary_only: bool = False,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get historical price data for a stock with customizable time period and interval.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        period: Time period - valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: '1mo')
        interval: Data interval - valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo (default: '1d')
        limit: Maximum number of most recent data points to return (default: None, returns all)
        summary_only: If True, return summary statistics instead of all data points (default: False)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string with historical price data or summary statistics.
        When summary_only=True, returns: high, low, avg close, total volume, start/end dates.
        When limit is set, returns only the N most recent data points.

    Example:
        yfinance_get_stock_history("AAPL", "1y", "1d", "json")
        yfinance_get_stock_history("AAPL", "1y", "1d", limit=30)  # Last 30 days
        yfinance_get_stock_history("AAPL", "1y", "1d", summary_only=True)  # Just summary
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return format_response({"error": f"No historical data found for {ticker} with period={period}, interval={interval}"}, response_format)

        # If summary_only, return summary statistics
        if summary_only:
            result = {
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "summary": {
                    "total_data_points": len(hist),
                    "start_date": hist.index[0].strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": hist.index[-1].strftime("%Y-%m-%d %H:%M:%S"),
                    "highest_price": float(hist["High"].max()),
                    "lowest_price": float(hist["Low"].min()),
                    "average_close": float(hist["Close"].mean()),
                    "total_volume": int(hist["Volume"].sum()),
                    "latest_close": float(hist["Close"].iloc[-1]),
                }
            }
            return format_response(result, response_format)

        # Apply limit if specified (get most recent N records)
        if limit is not None and limit > 0:
            hist = hist.tail(limit)

        # Convert to serializable format
        result = {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "count": len(hist),
            "data": []
        }

        if limit is not None:
            result["limit_applied"] = limit

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
    period: Literal["quarterly", "annual"] = "quarterly",
    limit: int = 4,
    fields: Optional[Union[List[str], str]] = None,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get financial statements for a stock (income statement, balance sheet, or cash flow statement).

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        statement_type: Type of financial statement - 'income', 'balance', or 'cashflow' (default: 'income')
        period: Period type - 'quarterly' for quarterly reports, 'annual' for yearly reports (default: 'quarterly')
        limit: Maximum number of periods to return (default: 4)
        fields: List of specific line items to include. If None, returns all fields (default: None)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing the requested financial statement organized by date.
        Returns quarterly data by default (most recent 4 quarters).
        Use period='annual' to get annual/yearly financial statements instead.
        When fields is specified, only those line items are included.

    Example:
        yfinance_get_stock_financials("AAPL", "income", "json")
        yfinance_get_stock_financials("AAPL", "income", period="annual", limit=3)  # Last 3 years
        yfinance_get_stock_financials("AAPL", "income", limit=2, fields=["Total Revenue", "Net Income"])
    """
    try:
        # Handle fields parameter if passed as JSON string
        if fields is not None and isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as a single field
                fields = [fields]

        stock = yf.Ticker(ticker)

        # Select the appropriate financial statement based on type and period
        if statement_type == "income":
            financials = stock.quarterly_financials if period == "quarterly" else stock.financials
            statement_name = "Income Statement"
        elif statement_type == "balance":
            financials = stock.quarterly_balance_sheet if period == "quarterly" else stock.balance_sheet
            statement_name = "Balance Sheet"
        elif statement_type == "cashflow":
            financials = stock.quarterly_cashflow if period == "quarterly" else stock.cashflow
            statement_name = "Cash Flow Statement"
        else:
            return format_response({"error": f"Invalid statement_type: {statement_type}. Use 'income', 'balance', or 'cashflow'"}, response_format)

        if financials.empty:
            return format_response({"error": f"No {statement_name.lower()} data found for {ticker}"}, response_format)

        # Apply limit (get most recent N periods)
        if limit > 0:
            financials = financials.iloc[:, :limit]

        # Filter fields if specified
        if fields is not None and len(fields) > 0:
            # Find matching fields (case-insensitive partial match)
            available_fields = financials.index.tolist()
            matched_fields = []
            for field in fields:
                for available_field in available_fields:
                    if field.lower() in available_field.lower():
                        matched_fields.append(available_field)
                        break

            if matched_fields:
                financials = financials.loc[matched_fields]
            else:
                return format_response({
                    "error": f"None of the specified fields found in {statement_name}",
                    "available_fields": available_fields[:20]  # Show first 20 available fields
                }, response_format)

        # Convert to serializable format
        result = {
            "ticker": ticker,
            "statement_type": statement_name,
            "period_type": period,
            "periods_count": len(financials.columns),
            "fields_count": len(financials.index),
            "limit_applied": limit,
            "data": {}
        }

        if fields is not None:
            result["fields_requested"] = fields

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
    limit: int = 20,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get analyst recommendations and rating changes for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        limit: Maximum number of most recent recommendations to return (default: 20)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing analyst recommendations history including:
        - Date of recommendation
        - Firm name
        - Rating change (to grade, from grade)
        - Action taken

    Example:
        yfinance_get_stock_recommendations("AAPL", "json")
        yfinance_get_stock_recommendations("AAPL", limit=10)  # Only 10 most recent
    """
    try:
        stock = yf.Ticker(ticker)
        # Use upgrades_downgrades which has firm, toGrade, fromGrade, action columns
        recommendations = stock.upgrades_downgrades

        if recommendations is None or recommendations.empty:
            return format_response({"error": f"No recommendations found for {ticker}"}, response_format)

        # Sort by date descending (newest first) and apply limit
        recommendations = recommendations.sort_index(ascending=False)
        if limit > 0:
            recommendations = recommendations.head(limit)

        result = {
            "ticker": ticker,
            "count": len(recommendations),
            "limit_applied": limit,
            "recommendations": []
        }

        for index, row in recommendations.iterrows():
            # Handle index that might be datetime or other type
            if hasattr(index, 'strftime'):
                date_str = index.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = str(index)

            # Try multiple possible column name variations
            firm = row.get("Firm", row.get("firm", "N/A"))
            to_grade = row.get("ToGrade", row.get("To Grade", row.get("toGrade", "N/A")))
            from_grade = row.get("FromGrade", row.get("From Grade", row.get("fromGrade", "N/A")))
            action = row.get("Action", row.get("action", "N/A"))

            # Optional price target information
            current_target = row.get("currentPriceTarget")
            prior_target = row.get("priorPriceTarget")
            target_action = row.get("priceTargetAction")

            rec = {
                "date": date_str,
                "firm": str(firm) if firm != "N/A" else "N/A",
                "to_grade": str(to_grade) if to_grade != "N/A" and pd.notna(to_grade) else "N/A",
                "from_grade": str(from_grade) if from_grade != "N/A" and pd.notna(from_grade) else "N/A",
                "action": str(action) if action != "N/A" else "N/A"
            }

            # Add price target info if available
            if pd.notna(current_target):
                rec["price_target"] = float(current_target)
            if pd.notna(prior_target):
                rec["prior_price_target"] = float(prior_target)
            if pd.notna(target_action) and target_action != "N/A":
                rec["price_target_action"] = str(target_action)

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
        - Article description/summary
        - Publisher name
        - Publication date and time
        - Article link
        - Content type
        - Thumbnail image URL

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
            # If item is a dict, extract values from the nested 'content' field
            if isinstance(item, dict):
                # News data is nested in the 'content' field
                content = item.get("content", {})

                # Handle various possible timestamp fields
                published_time = content.get("pubDate") or content.get("displayTime")
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
                    "title": content.get("title", "N/A"),
                    "description": content.get("summary", content.get("description", "N/A")),
                    "publisher": content.get("provider", {}).get("displayName", "N/A") if isinstance(content.get("provider"), dict) else str(content.get("provider", "N/A")),
                    "link": content.get("clickThroughUrl", {}).get("url", content.get("clickThroughUrl", "N/A")) if isinstance(content.get("clickThroughUrl"), dict) else str(content.get("clickThroughUrl", "N/A")),
                    "published": published_str,
                    "type": content.get("contentType", "N/A"),
                    "thumbnail": content.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "N/A") if content.get("thumbnail") else "N/A"
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
    tickers: Union[List[str], str],
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
        # Handle tickers parameter if passed as JSON string
        if isinstance(tickers, str):
            try:
                tickers = json.loads(tickers)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as a single ticker
                tickers = [tickers]

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
    limit: int = 12,
    future_only: bool = False,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get earnings calendar information including historical and upcoming earnings dates with estimates.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        limit: Maximum number of earnings dates to return (default: 12)
        future_only: If True, return only upcoming earnings dates (default: False)
        response_format: Output format - 'json' or 'markdown' (default: 'markdown')

    Returns:
        Formatted string containing earnings information including:
        - Earnings dates (historical and/or upcoming)
        - EPS estimates
        - Reported EPS (for historical dates)
        - Surprise percentage (actual vs estimate)

    Example:
        yfinance_get_earnings_dates("AAPL", "json")
        yfinance_get_earnings_dates("AAPL", limit=4)  # Last 4 quarters
        yfinance_get_earnings_dates("AAPL", future_only=True)  # Only upcoming
    """
    try:
        stock = yf.Ticker(ticker)

        # Get earnings dates
        earnings_dates = stock.earnings_dates

        if earnings_dates is None or earnings_dates.empty:
            return format_response({"error": f"No earnings dates found for {ticker}"}, response_format)

        # Filter for future only if requested
        if future_only:
            # Make now timezone-aware to match earnings_dates index timezone
            import pandas as pd
            if earnings_dates.index.tz is not None:
                now = pd.Timestamp.now(tz=earnings_dates.index.tz)
            else:
                now = pd.Timestamp.now()
            earnings_dates = earnings_dates[earnings_dates.index > now]

        # Check if we have any earnings dates after filtering
        if earnings_dates.empty:
            return format_response({
                "error": f"No {'future ' if future_only else ''}earnings dates found for {ticker}",
                "note": "yfinance may have limited future earnings data available"
            }, response_format)

        # Apply limit (get most recent N earnings dates)
        if limit > 0:
            earnings_dates = earnings_dates.head(limit)

        # Get next earnings date from actual filtered data (more reliable than info)
        next_earnings_from_data = earnings_dates.index[0] if not earnings_dates.empty else None

        result = {
            "ticker": ticker,
            "next_earnings_date": next_earnings_from_data.strftime("%Y-%m-%d") if next_earnings_from_data else "N/A",
            "count": len(earnings_dates),
            "limit_applied": limit,
            "future_only": future_only,
            "earnings_history": []
        }

        # Add note if fewer results than requested
        if future_only and len(earnings_dates) < limit:
            result["note"] = f"Only {len(earnings_dates)} future earnings date(s) available. yfinance typically provides 1-2 quarters of future data."

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
    dte: Optional[int] = None,
    option_type: Literal["calls", "puts", "both"] = "calls",
    strikes_near_price: Optional[int] = 10,
    in_the_money: Optional[bool] = None,
    min_volume: Optional[int] = None,
    min_open_interest: Optional[int] = None,
    strike_min: Optional[float] = None,
    strike_max: Optional[float] = None,
    dates_only: bool = False,
    response_format: Literal["json", "markdown"] = "markdown"
) -> str:
    """
    Get options chain data for a stock. Returns call options near current price for the nearest expiration by default.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        expiration_date: Optional expiration date in 'YYYY-MM-DD' format (default: nearest)
        dte: Optional days to expiration - USE THIS for time-based queries:
             - 7 for "weekly options"
             - 30 for "monthly options"
             - 90 for "quarterly options"
             - 365 for "LEAPS" or "long-term options"
             (default: None, uses nearest expiration)
        option_type: 'calls', 'puts', or 'both'
             - Use 'both' when query mentions "what's available" or exploratory requests
             - Default: 'calls'
        strikes_near_price: Number of strikes above/below current price, or None for all (default: 10)
        in_the_money: True for ITM, False for OTM, None for both (default: None)
        min_volume: Minimum volume filter - ONLY use if query mentions "liquid" or "active" (default: None)
        min_open_interest: Minimum open interest filter - ONLY use if query mentions "liquid" or "active" (default: None)
        strike_min: Minimum strike price (default: None)
        strike_max: Maximum strike price (default: None)
        dates_only: If True, return only the list of available expiration dates without contract data.
                    Use for queries like "what expiration dates does [ticker] have?" (default: False)
        response_format: 'json' or 'markdown' (default: 'markdown')

    Query interpretation:
        - "weekly options" → dte=7
        - "monthly options" → dte=30
        - "what options are available" → option_type="both"
        - "what expiration dates" or "what dates are available" → dates_only=True
        - "liquid/active options" → add min_volume and min_open_interest
        - Don't add filters unless specifically requested

    Returns:
        Options chain data with contract details, prices, volume, open interest, and implied volatility.
        If dates_only=True, returns only the list of available expiration dates.

    Examples:
        yfinance_get_options_chain("SPY", dates_only=True)  # Just get available expiration dates
        yfinance_get_options_chain("SPY", dte=7)  # Weekly options
        yfinance_get_options_chain("AAPL", dte=30, option_type="both")  # Monthly calls and puts
        yfinance_get_options_chain("TSLA", dte=7, min_volume=1000)  # Liquid weekly options
    """
    try:
        stock = yf.Ticker(ticker)

        # Get current stock price for strikes_near_price filtering
        info = stock.info
        current_price = info.get("currentPrice", info.get("regularMarketPrice"))
        if current_price is None:
            # Try fast_info as fallback
            try:
                current_price = stock.fast_info.last_price
            except:
                current_price = None

        # Get available expiration dates
        available_expirations = stock.options

        if not available_expirations:
            return format_response({"error": f"No options data available for {ticker}"}, response_format)

        # If only dates requested, return early without fetching contract data
        if dates_only:
            result = {
                "ticker": ticker,
                "available_expirations": list(available_expirations),
                "total_expirations": len(available_expirations)
            }
            return format_response(result, response_format)

        # Handle DTE (days to expiration) if specified
        if dte is not None:
            from datetime import datetime, timedelta
            target_date = datetime.now() + timedelta(days=dte)

            # Find the expiration closest to the target DTE
            closest_exp = None
            min_diff = float('inf')

            for exp_str in available_expirations:
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                diff = abs((exp_date - target_date).days)
                if diff < min_diff:
                    min_diff = diff
                    closest_exp = exp_str

            expiration_date = closest_exp
            show_available = True
        # If no expiration specified, return available dates and use nearest
        elif expiration_date is None:
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
                "strikes_near_price": strikes_near_price,
                "in_the_money": in_the_money,
                "min_volume": min_volume,
                "min_open_interest": min_open_interest,
                "strike_range": f"{strike_min} to {strike_max}" if strike_min or strike_max else None
            }
        }

        if current_price is not None:
            result["current_price"] = float(current_price)

        if show_available:
            result["available_expirations"] = list(available_expirations)

        def process_options(df, option_label):
            """Process and filter options dataframe"""
            # First, apply strikes_near_price filter if applicable
            if strikes_near_price is not None and current_price is not None and not df.empty:
                # Calculate distance from current price for each strike
                df = df.copy()
                df['distance_from_price'] = abs(df['strike'] - current_price)

                # Separate into ITM and OTM
                if option_label == "calls":
                    itm_df = df[df['strike'] <= current_price].nsmallest(strikes_near_price, 'distance_from_price')
                    otm_df = df[df['strike'] > current_price].nsmallest(strikes_near_price, 'distance_from_price')
                else:  # puts
                    itm_df = df[df['strike'] >= current_price].nsmallest(strikes_near_price, 'distance_from_price')
                    otm_df = df[df['strike'] < current_price].nsmallest(strikes_near_price, 'distance_from_price')

                # Combine and sort by strike
                df = pd.concat([itm_df, otm_df]).sort_values('strike')

            options_data = []
            for _, row in df.iterrows():
                # Apply other filters
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
