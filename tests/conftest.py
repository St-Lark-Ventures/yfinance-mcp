"""Pytest fixtures for yfinance-mcp tests."""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime


@pytest.fixture
def mock_stock_info():
    """Mock stock info data."""
    return {
        "symbol": "AAPL",
        "longName": "Apple Inc.",
        "currentPrice": 175.50,
        "currency": "USD",
        "marketCap": 2800000000000,
        "trailingPE": 28.5,
        "forwardPE": 26.2,
        "dividendYield": 0.005,
        "fiftyTwoWeekHigh": 199.62,
        "fiftyTwoWeekLow": 124.17,
        "averageVolume": 55000000,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
    }


@pytest.fixture
def mock_history_data():
    """Mock historical price data."""
    dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "Open": [170.0, 171.0, 172.0, 173.0, 174.0],
            "High": [172.0, 173.0, 174.0, 175.0, 176.0],
            "Low": [169.0, 170.0, 171.0, 172.0, 173.0],
            "Close": [171.0, 172.0, 173.0, 174.0, 175.0],
            "Volume": [50000000, 51000000, 52000000, 53000000, 54000000],
        },
        index=dates,
    )


@pytest.fixture
def mock_ticker(mock_stock_info, mock_history_data):
    """Mock yfinance Ticker object."""
    ticker = MagicMock()
    ticker.info = mock_stock_info
    ticker.history.return_value = mock_history_data
    ticker.options = ["2024-01-19", "2024-01-26", "2024-02-02"]
    return ticker
