"""Unit tests for stock market and core tools."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from open_stocks_mcp.tools.robinhood_stock_tools import (
    find_instrument_data,
    get_instruments_by_symbols,
    get_market_hours,
    get_price_history,
    get_pricebook_by_symbol,
    get_stock_info,
    get_stock_price,
    get_stock_quote_by_id,
    search_stocks,
)
from open_stocks_mcp.tools.robinhood_tools import list_available_tools


class TestStockMarketTools:
    """Test stock market data tools with mocked responses."""

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_quotes")
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_latest_price")
    @pytest.mark.asyncio
    async def test_get_stock_price_success(
        self, mock_latest_price: Any, mock_quotes: Any
    ) -> None:
        """Test successful stock price retrieval."""
        mock_latest_price.return_value = ["150.25"]
        mock_quotes.return_value = [
            {
                "previous_close": "148.50",
                "volume": "1000000",
                "ask_price": "150.30",
                "bid_price": "150.20",
                "last_trade_price": "150.25",
            }
        ]

        result = await get_stock_price("AAPL")

        assert "result" in result
        assert result["result"]["symbol"] == "AAPL"
        assert result["result"]["price"] == 150.25
        assert result["result"]["change"] == 1.75  # 150.25 - 148.50
        assert result["result"]["change_percent"] == 1.18  # rounded
        assert result["result"]["previous_close"] == 148.50
        assert result["result"]["volume"] == 1000000
        assert result["result"]["status"] == "success"

    @pytest.mark.exception_test
    @pytest.mark.skip(reason="Slow exception test - run with pytest -m exception_test")
    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_quotes")
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_latest_price")
    @pytest.mark.asyncio
    async def test_get_stock_price_no_data(
        self, mock_latest_price: Any, mock_quotes: Any
    ) -> None:
        """Test stock price when no data is available."""
        mock_latest_price.return_value = None
        mock_quotes.return_value = None

        result = await get_stock_price("AAPL")  # Use valid symbol format

        assert "result" in result
        assert result["result"]["status"] == "no_data"
        assert "No price data found" in result["result"]["message"]

    @pytest.mark.exception_test
    @pytest.mark.skip(reason="Slow exception test - run with pytest -m exception_test")
    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_stock_price_invalid_symbol(self) -> None:
        """Test stock price with invalid symbol format."""
        result = await get_stock_price("123INVALID")

        assert "result" in result
        assert "error" in result["result"]
        assert result["result"]["status"] == "error"

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_name_by_symbol")
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_instruments_by_symbols")
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_fundamentals")
    @pytest.mark.asyncio
    async def test_get_stock_info_success(
        self, mock_fundamentals: Any, mock_instruments: Any, mock_name: Any
    ) -> None:
        """Test successful stock info retrieval."""
        mock_fundamentals.return_value = [
            {
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "description": "Apple Inc. designs and manufactures smartphones",
                "market_cap": "3000000000000",
                "pe_ratio": "25.5",
                "dividend_yield": "0.50",
                "high_52_weeks": "182.94",
                "low_52_weeks": "124.17",
                "average_volume": "50000000",
            }
        ]
        mock_instruments.return_value = [{"simple_name": "Apple", "tradeable": True}]
        mock_name.return_value = "Apple Inc."

        result = await get_stock_info("AAPL")

        assert "result" in result
        assert result["result"]["symbol"] == "AAPL"
        assert result["result"]["company_name"] == "Apple Inc."
        assert result["result"]["sector"] == "Technology"
        assert result["result"]["industry"] == "Consumer Electronics"
        assert result["result"]["market_cap"] == "3000000000000"
        assert result["result"]["pe_ratio"] == "25.5"
        assert result["result"]["tradeable"] is True
        assert result["result"]["status"] == "success"

    @pytest.mark.exception_test
    @pytest.mark.skip(reason="Slow exception test - run with pytest -m exception_test")
    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_instruments_by_symbols")
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_fundamentals")
    @pytest.mark.asyncio
    async def test_get_stock_info_no_data(
        self, mock_fundamentals: Any, mock_instruments: Any
    ) -> None:
        """Test stock info when no data is available."""
        mock_fundamentals.return_value = None
        mock_instruments.return_value = None

        result = await get_stock_info("AAPL")  # Use valid symbol format

        assert "result" in result
        assert result["result"]["status"] == "no_data"
        assert "No company information found" in result["result"]["message"]

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.find_instrument_data")
    @pytest.mark.asyncio
    async def test_search_stocks_success(self, mock_find_instrument: Any) -> None:
        """Test successful stock search."""
        mock_find_instrument.return_value = [
            {
                "symbol": "AAPL",
                "simple_name": "Apple Inc.",
                "tradeable": True,
                "country": "US",
                "type": "stock",
            },
            {
                "symbol": "GOOGL",
                "simple_name": "Alphabet Inc.",
                "tradeable": True,
                "country": "US",
                "type": "stock",
            },
        ]

        result = await search_stocks("Apple")

        assert "result" in result
        assert result["result"]["query"] == "Apple"
        assert result["result"]["count"] == 2
        assert len(result["result"]["results"]) == 2
        assert result["result"]["results"][0]["symbol"] == "AAPL"
        assert result["result"]["results"][0]["name"] == "Apple Inc."
        assert result["result"]["results"][1]["symbol"] == "GOOGL"
        assert result["result"]["status"] == "success"

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.find_instrument_data")
    @pytest.mark.asyncio
    async def test_search_stocks_no_results(self, mock_find_instrument: Any) -> None:
        """Test stock search with no results."""
        mock_find_instrument.return_value = None

        result = await search_stocks("NONEXISTENT")

        assert "result" in result
        assert result["result"]["query"] == "NONEXISTENT"
        assert result["result"]["count"] == 0
        assert result["result"]["results"] == []
        assert "No stocks found" in result["result"]["message"]
        assert result["result"]["status"] == "success"

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_stocks_empty_query(self) -> None:
        """Test stock search with empty query."""
        result = await search_stocks("")

        assert "result" in result
        assert "error" in result["result"]
        assert result["result"]["status"] == "error"

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_markets")
    @pytest.mark.asyncio
    async def test_get_market_hours_success(self, mock_markets: Any) -> None:
        """Test successful market hours retrieval."""
        mock_markets.return_value = [
            {
                "name": "NASDAQ Global Select Market",
                "mic": "XNAS",
                "operating_mic": "XNAS",
                "timezone": "US/Eastern",
                "website": "https://www.nasdaq.com/",
            },
            {
                "name": "New York Stock Exchange",
                "mic": "XNYS",
                "operating_mic": "XNYS",
                "timezone": "US/Eastern",
                "website": "https://www.nyse.com/",
            },
        ]

        result = await get_market_hours()

        assert "result" in result
        assert result["result"]["count"] == 2
        assert len(result["result"]["markets"]) == 2
        assert result["result"]["markets"][0]["name"] == "NASDAQ Global Select Market"
        assert result["result"]["markets"][0]["mic"] == "XNAS"
        assert result["result"]["markets"][1]["name"] == "New York Stock Exchange"
        assert result["result"]["status"] == "success"

    @pytest.mark.exception_test
    @pytest.mark.skip(reason="Slow exception test - run with pytest -m exception_test")
    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_markets")
    @pytest.mark.asyncio
    async def test_get_market_hours_no_data(self, mock_markets: Any) -> None:
        """Test market hours when no data is available."""
        mock_markets.return_value = None

        result = await get_market_hours()

        assert "result" in result
        assert result["result"]["status"] == "no_data"
        assert "No market data available" in result["result"]["message"]

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_stock_historicals")
    @pytest.mark.asyncio
    async def test_get_price_history_success(self, mock_historicals: Any) -> None:
        """Test successful price history retrieval."""
        mock_historicals.return_value = [
            {
                "begins_at": "2023-01-01T00:00:00Z",
                "open_price": "148.00",
                "high_price": "150.50",
                "low_price": "147.50",
                "close_price": "149.75",
                "volume": "1000000",
            },
            {
                "begins_at": "2023-01-02T00:00:00Z",
                "open_price": "149.80",
                "high_price": "151.20",
                "low_price": "149.00",
                "close_price": "150.25",
                "volume": "1200000",
            },
        ]

        result = await get_price_history("AAPL", "week")

        assert "result" in result
        assert result["result"]["symbol"] == "AAPL"
        assert result["result"]["period"] == "week"
        assert result["result"]["interval"] == "hour"
        assert result["result"]["count"] == 2
        assert len(result["result"]["data_points"]) == 2
        assert result["result"]["data_points"][0]["close"] == 149.75
        assert result["result"]["data_points"][1]["close"] == 150.25
        assert result["result"]["status"] == "success"

    @pytest.mark.exception_test
    @pytest.mark.skip(reason="Slow exception test - run with pytest -m exception_test")
    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_stock_historicals")
    @pytest.mark.asyncio
    async def test_get_price_history_no_data(self, mock_historicals: Any) -> None:
        """Test price history when no data is available."""
        mock_historicals.return_value = None

        result = await get_price_history("AAPL", "week")  # Use valid symbol format

        assert "result" in result
        assert result["result"]["status"] == "no_data"
        assert "No historical data found" in result["result"]["message"]

    @pytest.mark.exception_test
    @pytest.mark.skip(reason="Slow exception test - run with pytest -m exception_test")
    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_price_history_invalid_period(self) -> None:
        """Test price history with invalid period."""
        result = await get_price_history("AAPL", "invalid")

        assert "result" in result
        assert "error" in result["result"]
        assert result["result"]["status"] == "error"
        assert "Invalid period" in result["result"]["error"]

    @pytest.mark.journey_system
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_available_tools_success(self) -> None:
        """Test successful tools listing."""
        # Create a mock FastMCP instance
        mock_mcp = AsyncMock()

        # Create mock tool objects
        mock_tool1 = MagicMock()
        mock_tool1.name = "stock_price"
        mock_tool1.description = "Get current stock price and basic metrics"

        mock_tool2 = MagicMock()
        mock_tool2.name = "portfolio"
        mock_tool2.description = "Provides a high-level overview of the portfolio"

        mock_mcp.list_tools.return_value = [mock_tool1, mock_tool2]

        result = await list_available_tools(mock_mcp)

        assert "result" in result
        assert result["result"]["count"] == 2
        assert len(result["result"]["tools"]) == 2
        assert result["result"]["tools"][0]["name"] == "stock_price"
        assert (
            result["result"]["tools"][0]["description"]
            == "Get current stock price and basic metrics"
        )
        assert result["result"]["tools"][1]["name"] == "portfolio"


class TestServerTools:
    """Test server monitoring and session tools."""

    @pytest.mark.journey_system
    @pytest.mark.unit
    @patch("open_stocks_mcp.server.app.get_session_manager")
    @pytest.mark.asyncio
    async def test_session_status_success(self, mock_get_session_manager: Any) -> None:
        """Test successful session status retrieval."""
        # We need to import these from the server app where they're defined
        from open_stocks_mcp.server.app import session_status

        mock_session_manager = MagicMock()
        mock_session_manager.get_session_info.return_value = {
            "is_authenticated": True,
            "is_valid": True,
            "username": "testuser",
            "login_time": "2023-01-01T10:00:00",
            "session_timeout_hours": 23,
        }
        mock_get_session_manager.return_value = mock_session_manager

        result = await session_status()

        assert "result" in result
        assert result["result"]["is_authenticated"] is True
        assert result["result"]["is_valid"] is True
        assert result["result"]["username"] == "testuser"
        assert result["result"]["status"] == "success"

    @pytest.mark.journey_system
    @pytest.mark.unit
    @patch("open_stocks_mcp.server.app.get_rate_limiter")
    @pytest.mark.asyncio
    async def test_rate_limit_status_success(self, mock_get_rate_limiter: Any) -> None:
        """Test successful rate limit status retrieval."""
        from open_stocks_mcp.server.app import rate_limit_status

        mock_rate_limiter = MagicMock()
        mock_rate_limiter.get_stats.return_value = {
            "calls_last_minute": 5,
            "calls_last_hour": 150,
            "limit_per_minute": 30,
            "limit_per_hour": 1000,
            "minute_usage_percent": 16.67,
            "hour_usage_percent": 15.0,
        }
        mock_get_rate_limiter.return_value = mock_rate_limiter

        result = await rate_limit_status()

        assert "result" in result
        assert result["result"]["calls_last_minute"] == 5
        assert result["result"]["calls_last_hour"] == 150
        assert result["result"]["limit_per_minute"] == 30
        assert result["result"]["minute_usage_percent"] == 16.67
        assert result["result"]["status"] == "success"

    @pytest.mark.journey_system
    @pytest.mark.unit
    @patch("open_stocks_mcp.server.app.get_metrics_collector")
    @pytest.mark.asyncio
    async def test_metrics_summary_success(
        self, mock_get_metrics_collector: Any
    ) -> None:
        """Test successful metrics summary retrieval."""
        from open_stocks_mcp.server.app import metrics_summary

        mock_metrics_collector = AsyncMock()
        mock_metrics_collector.get_metrics.return_value = {
            "total_calls": 500,
            "total_errors": 10,
            "error_rate_percent": 2.0,
            "avg_response_time_ms": 250.5,
            "session_refreshes": 1,
            "timestamp": "2023-01-01T12:00:00",
        }
        mock_get_metrics_collector.return_value = mock_metrics_collector

        result = await metrics_summary()

        assert "result" in result
        assert result["result"]["total_calls"] == 500
        assert result["result"]["total_errors"] == 10
        assert result["result"]["error_rate_percent"] == 2.0
        assert result["result"]["avg_response_time_ms"] == 250.5
        assert result["result"]["status"] == "success"

    @pytest.mark.journey_system
    @pytest.mark.unit
    @patch("open_stocks_mcp.server.app.get_metrics_collector")
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_get_metrics_collector: Any) -> None:
        """Test successful health check."""
        from open_stocks_mcp.server.app import health_check

        mock_metrics_collector = AsyncMock()
        mock_metrics_collector.get_health_status.return_value = {
            "health_status": "healthy",  # Different key to avoid status override
            "issues": [],
            "metrics_summary": {
                "error_rate_percent": 1.5,
                "avg_response_time_ms": 200.0,
                "calls_last_hour": 100,
            },
        }
        mock_get_metrics_collector.return_value = mock_metrics_collector

        result = await health_check()

        assert "result" in result
        assert result["result"]["status"] == "success"  # Server adds this status
        assert result["result"]["health_status"] == "healthy"
        assert result["result"]["issues"] == []
        assert result["result"]["metrics_summary"]["error_rate_percent"] == 1.5
        assert result["result"]["metrics_summary"]["avg_response_time_ms"] == 200.0

    @pytest.mark.journey_system
    @pytest.mark.unit
    @patch("open_stocks_mcp.server.app.get_metrics_collector")
    @pytest.mark.asyncio
    async def test_health_check_degraded(self, mock_get_metrics_collector: Any) -> None:
        """Test health check with degraded status."""
        from open_stocks_mcp.server.app import health_check

        mock_metrics_collector = AsyncMock()
        mock_metrics_collector.get_health_status.return_value = {
            "health_status": "degraded",  # Different key to avoid status override
            "issues": ["High error rate: 15.0%"],
            "metrics_summary": {
                "error_rate_percent": 15.0,
                "avg_response_time_ms": 6000.0,
                "calls_last_hour": 50,
            },
        }
        mock_get_metrics_collector.return_value = mock_metrics_collector

        result = await health_check()

        assert "result" in result
        assert result["result"]["status"] == "success"  # Server adds this status
        assert result["result"]["health_status"] == "degraded"
        assert "High error rate: 15.0%" in result["result"]["issues"]
        assert result["result"]["metrics_summary"]["error_rate_percent"] == 15.0


class TestAdvancedInstrumentTools:
    """Test advanced instrument data tools with mocked responses."""

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_instruments_by_symbols")
    @pytest.mark.asyncio
    async def test_get_instruments_by_symbols_success(
        self, mock_get_instruments: Any
    ) -> None:
        """Test successful instrument retrieval for multiple symbols."""
        mock_get_instruments.return_value = [
            {
                "id": "450dfc6d-5510-4d40-abfb-f633b7d9be3e",
                "url": "https://robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/",
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "tradeable": True,
                "market": "NASDAQ",
                "list_date": "1980-12-12",
                "state": "active",
                "type": "stock",
                "tradability": "tradable",
                "splits": "https://robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/splits/",
                "fundamentals": "https://robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/fundamentals/",
                "quote": "https://robinhood.com/quotes/AAPL/",
                "simple_name": "Apple",
                "min_tick_size": None,
                "maintenance_ratio": "0.2500",
                "day_trade_ratio": "0.2500",
                "margin_initial_ratio": "0.5000",
                "bloomberg_unique": "EQ0010169500001000",
                "rhs_tradability": "tradable",
                "tradable_chain_id": "1df78b0f-8362-4c73-9c41-6e8c5f7dc4a4",
                "default_collar_fraction": "0.0500",
                "fractional_tradability": "tradable",
                "terminal_currencies": ["USD"],
                "country": "US",
                "day_trade_buying_power_ratio": "0.2500",
                "symbol_description": "Apple Inc. - Common Stock",
                "instrument_id": "450dfc6d-5510-4d40-abfb-f633b7d9be3e",
            },
            {
                "id": "943c5009-a0bb-4665-8cf4-a95dab5874e4",
                "url": "https://robinhood.com/instruments/943c5009-a0bb-4665-8cf4-a95dab5874e4/",
                "symbol": "GOOGL",
                "name": "Alphabet Inc. - Class A",
                "tradeable": True,
                "market": "NASDAQ",
                "list_date": "2004-08-19",
                "state": "active",
                "type": "stock",
                "tradability": "tradable",
                "splits": "https://robinhood.com/instruments/943c5009-a0bb-4665-8cf4-a95dab5874e4/splits/",
                "fundamentals": "https://robinhood.com/instruments/943c5009-a0bb-4665-8cf4-a95dab5874e4/fundamentals/",
                "quote": "https://robinhood.com/quotes/GOOGL/",
                "simple_name": "Alphabet",
                "min_tick_size": None,
                "maintenance_ratio": "0.2500",
                "day_trade_ratio": "0.2500",
                "margin_initial_ratio": "0.5000",
                "bloomberg_unique": "EQ0010080100001000",
                "rhs_tradability": "tradable",
                "tradable_chain_id": "6df56bd0-0bf2-44ab-8875-f94fd8526942",
                "default_collar_fraction": "0.0500",
                "fractional_tradability": "tradable",
                "terminal_currencies": ["USD"],
                "country": "US",
                "day_trade_buying_power_ratio": "0.2500",
                "symbol_description": "Alphabet Inc. - Class A - Common Stock",
                "instrument_id": "943c5009-a0bb-4665-8cf4-a95dab5874e4",
            },
        ]

        result = await get_instruments_by_symbols(["AAPL", "GOOGL"])

        assert "result" in result
        assert result["result"]["status"] == "success"
        assert len(result["result"]["instruments"]) == 2
        assert result["result"]["instruments"][0]["symbol"] == "AAPL"
        assert result["result"]["instruments"][0]["name"] == "Apple Inc."
        assert result["result"]["instruments"][1]["symbol"] == "GOOGL"
        assert result["result"]["instruments"][1]["name"] == "Alphabet Inc. - Class A"

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_instruments_by_symbols_empty_list(self) -> None:
        """Test get_instruments_by_symbols with empty symbol list."""
        result = await get_instruments_by_symbols([])

        assert "result" in result
        assert result["result"]["status"] == "error"
        assert "empty" in result["result"]["error"].lower()

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_instruments_by_symbols_invalid_symbols(self) -> None:
        """Test get_instruments_by_symbols with invalid symbol formats."""
        result = await get_instruments_by_symbols(["", "INVALID$SYMBOL", "123"])

        assert "result" in result
        assert result["result"]["status"] == "error"
        assert "invalid" in result["result"]["error"].lower()

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.find_instrument_data")
    @pytest.mark.asyncio
    async def test_find_instrument_data_success(
        self, mock_find_instrument: Any
    ) -> None:
        """Test successful instrument data search."""
        mock_find_instrument.return_value = [
            {
                "id": "450dfc6d-5510-4d40-abfb-f633b7d9be3e",
                "url": "https://robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/",
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "tradeable": True,
                "market": "NASDAQ",
                "list_date": "1980-12-12",
                "state": "active",
                "type": "stock",
                "simple_name": "Apple",
                "country": "US",
                "symbol_description": "Apple Inc. - Common Stock",
            }
        ]

        result = await find_instrument_data("Apple")

        assert "result" in result
        assert result["result"]["status"] == "success"
        assert len(result["result"]["instruments"]) == 1
        assert result["result"]["instruments"][0]["symbol"] == "AAPL"
        assert result["result"]["instruments"][0]["name"] == "Apple Inc."

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_instrument_data_empty_query(self) -> None:
        """Test find_instrument_data with empty query."""
        result = await find_instrument_data("")

        assert "result" in result
        assert result["result"]["status"] == "error"
        assert "empty" in result["result"]["error"].lower()

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_stock_quote_by_id")
    @pytest.mark.asyncio
    async def test_get_stock_quote_by_id_success(
        self, mock_get_stock_quote_by_id: Any
    ) -> None:
        """Test successful stock quote retrieval by ID."""
        mock_get_stock_quote_by_id.return_value = {
            "ask_price": "150.30",
            "ask_size": "100",
            "bid_price": "150.20",
            "bid_size": "200",
            "last_trade_price": "150.25",
            "last_extended_hours_trade_price": "150.00",
            "previous_close": "148.50",
            "adjusted_previous_close": "148.50",
            "previous_close_date": "2024-01-12",
            "symbol": "AAPL",
            "trading_halted": False,
            "has_traded": True,
            "last_trade_price_source": "consolidated",
            "updated_at": "2024-01-13T21:00:00Z",
            "instrument": "https://robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/",
            "instrument_id": "450dfc6d-5510-4d40-abfb-f633b7d9be3e",
        }

        result = await get_stock_quote_by_id("450dfc6d-5510-4d40-abfb-f633b7d9be3e")

        assert "result" in result
        assert result["result"]["status"] == "success"
        assert (
            result["result"]["instrument_id"] == "450dfc6d-5510-4d40-abfb-f633b7d9be3e"
        )
        assert result["result"]["symbol"] == "AAPL"
        assert result["result"]["price"] == 150.25

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_stock_quote_by_id_empty_id(self) -> None:
        """Test get_stock_quote_by_id with empty ID."""
        result = await get_stock_quote_by_id("")

        assert "result" in result
        assert result["result"]["status"] == "error"
        assert "empty" in result["result"]["error"].lower()

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @patch("open_stocks_mcp.tools.robinhood_stock_tools.rh.get_pricebook_by_symbol")
    @pytest.mark.asyncio
    async def test_get_pricebook_by_symbol_success(
        self, mock_get_pricebook: Any
    ) -> None:
        """Test successful pricebook retrieval."""
        mock_get_pricebook.return_value = {
            "asks": [
                {"price": "150.30", "quantity": "100"},
                {"price": "150.32", "quantity": "200"},
                {"price": "150.35", "quantity": "150"},
            ],
            "bids": [
                {"price": "150.20", "quantity": "200"},
                {"price": "150.18", "quantity": "100"},
                {"price": "150.15", "quantity": "300"},
            ],
            "symbol": "AAPL",
            "updated_at": "2024-01-13T21:00:00Z",
        }

        result = await get_pricebook_by_symbol("AAPL")

        assert "result" in result
        assert result["result"]["status"] == "success"
        assert result["result"]["symbol"] == "AAPL"
        assert len(result["result"]["asks"]) == 3
        assert len(result["result"]["bids"]) == 3
        assert result["result"]["asks"][0]["price"] == 150.30
        assert result["result"]["bids"][0]["price"] == 150.20

    @pytest.mark.journey_market_data
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_pricebook_by_symbol_invalid_symbol(self) -> None:
        """Test get_pricebook_by_symbol with invalid symbol."""
        result = await get_pricebook_by_symbol("INVALID$SYMBOL")

        assert "result" in result
        assert result["result"]["status"] == "error"
        assert "invalid" in result["result"]["error"].lower()
