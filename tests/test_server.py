"""Tests for yfinance_mcp server functions."""

import pytest
from unittest.mock import MagicMock, patch
import json
import pandas as pd
from datetime import datetime

from yfinance_mcp.server import (
    format_response,
    _format_as_markdown,
    CHARACTER_LIMIT,
)


class TestFormatResponse:
    """Tests for format_response function."""

    def test_json_format(self):
        """Test JSON output format."""
        data = {"ticker": "AAPL", "price": 175.50}
        result = format_response(data, "json")
        parsed = json.loads(result)
        assert parsed["ticker"] == "AAPL"
        assert parsed["price"] == 175.50

    def test_markdown_format(self):
        """Test markdown output format."""
        data = {"ticker": "AAPL", "price": 175.50}
        result = format_response(data, "markdown")
        assert "Ticker" in result
        assert "AAPL" in result

    def test_truncation(self):
        """Test response truncation at character limit."""
        large_data = {"data": "x" * (CHARACTER_LIMIT + 1000)}
        result = format_response(large_data, "json")
        assert len(result) <= CHARACTER_LIMIT + 200
        assert "truncated" in result.lower()

    def test_default_format_is_markdown(self):
        """Test that default format is markdown."""
        data = {"ticker": "AAPL"}
        result = format_response(data)
        # Markdown format has title-cased keys
        assert "Ticker" in result


class TestFormatAsMarkdown:
    """Tests for _format_as_markdown function."""

    def test_error_format(self):
        """Test error message formatting."""
        data = {"error": "Something went wrong"}
        result = _format_as_markdown(data)
        assert "Error" in result
        assert "Something went wrong" in result

    def test_dict_values(self):
        """Test nested dictionary formatting."""
        data = {"summary": {"high": 100, "low": 90}}
        result = _format_as_markdown(data)
        assert "Summary" in result
        assert "high" in result

    def test_list_values(self):
        """Test list formatting."""
        data = {"items": ["item1", "item2", "item3"]}
        result = _format_as_markdown(data)
        assert "Items" in result
        assert "item1" in result

    def test_nested_list_of_dicts(self):
        """Test list of dictionaries formatting."""
        data = {"recommendations": [{"firm": "Goldman", "rating": "Buy"}]}
        result = _format_as_markdown(data)
        assert "Recommendations" in result
        assert "firm" in result

    def test_simple_values(self):
        """Test simple key-value formatting."""
        data = {"name": "Apple Inc.", "price": 175.50}
        result = _format_as_markdown(data)
        assert "Name" in result
        assert "Apple Inc." in result
        assert "Price" in result


class TestIntegrationWithYfinance:
    """Integration tests that call yfinance (may be slow/network dependent)."""

    @pytest.mark.slow
    @pytest.mark.skipif(True, reason="Requires network and may be rate-limited")
    def test_real_stock_info(self):
        """Test with real yfinance data - skipped by default."""
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        assert "symbol" in info or "shortName" in info


class TestDataFormatting:
    """Tests for data formatting edge cases."""

    def test_empty_dict(self):
        """Test formatting empty dictionary."""
        result = format_response({}, "json")
        assert result == "{}"

    def test_none_values(self):
        """Test handling of None values."""
        data = {"ticker": "AAPL", "dividend": None}
        result = format_response(data, "json")
        parsed = json.loads(result)
        assert parsed["dividend"] is None

    def test_numeric_values(self):
        """Test handling of various numeric values."""
        data = {
            "integer": 100,
            "float": 175.50,
            "negative": -10.5,
            "large": 2800000000000
        }
        result = format_response(data, "json")
        parsed = json.loads(result)
        assert parsed["integer"] == 100
        assert parsed["float"] == 175.50
        assert parsed["negative"] == -10.5
        assert parsed["large"] == 2800000000000

    def test_special_characters_in_values(self):
        """Test handling of special characters."""
        data = {"description": "Apple & Co. <tech> company"}
        result = format_response(data, "json")
        parsed = json.loads(result)
        assert parsed["description"] == "Apple & Co. <tech> company"

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        data = {"currency": "USD", "symbol": "$"}
        result = format_response(data, "json")
        parsed = json.loads(result)
        assert parsed["symbol"] == "$"


class TestMarkdownEdgeCases:
    """Tests for markdown formatting edge cases."""

    def test_underscore_replacement_in_keys(self):
        """Test that underscores in keys are replaced with spaces."""
        data = {"market_cap": 1000000}
        result = _format_as_markdown(data)
        assert "Market Cap" in result

    def test_deeply_nested_dict(self):
        """Test handling of nested dictionaries in markdown."""
        data = {
            "outer": {
                "inner_key": "inner_value"
            }
        }
        result = _format_as_markdown(data)
        assert "Outer" in result
        assert "inner_key" in result
