"""MCP server implementation for Robin Stocks trading"""

import asyncio
import os
import sys
from typing import Any

import click
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from open_stocks_mcp.config import ServerConfig, load_config
from open_stocks_mcp.logging_config import logger, setup_logging
from open_stocks_mcp.monitoring import get_metrics_collector
from open_stocks_mcp.tools.rate_limiter import get_rate_limiter
from open_stocks_mcp.tools.robinhood_account_features_tools import (
    get_account_features,
    get_latest_notification,
    get_margin_calls,
    get_margin_interest,
    get_notifications,
    get_referrals,
    get_subscription_fees,
)
from open_stocks_mcp.tools.robinhood_account_tools import (
    get_account_details,
    get_account_info,
    get_portfolio,
    get_positions,
)
from open_stocks_mcp.tools.robinhood_advanced_portfolio_tools import (
    get_build_holdings,
    get_build_user_profile,
    get_day_trades,
)
from open_stocks_mcp.tools.robinhood_dividend_tools import (
    get_dividends,
    get_dividends_by_instrument,
    get_interest_payments,
    get_stock_loan_payments,
    get_total_dividends,
)
from open_stocks_mcp.tools.robinhood_market_data_tools import (
    get_stock_earnings,
    get_stock_events,
    get_stock_level2_data,
    get_stock_news,
    get_stock_ratings,
    get_stock_splits,
    get_stocks_by_tag,
    get_top_100,
    get_top_movers,
    get_top_movers_sp500,
)

# Phase 3 Tools
from open_stocks_mcp.tools.robinhood_options_tools import (
    find_tradable_options,
    get_aggregate_positions,
    get_all_option_positions,
    get_open_option_positions,
    get_open_option_positions_with_details,
    get_option_historicals,
    get_option_market_data,
    get_options_chains,
)
from open_stocks_mcp.tools.robinhood_order_tools import (
    get_options_orders,
    get_stock_orders,
)
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

# Phase 7: Trading Capabilities Tools
from open_stocks_mcp.tools.robinhood_trading_tools import (
    cancel_all_option_orders,
    cancel_all_stock_orders,
    cancel_option_order,
    cancel_stock_order,
    get_all_open_option_orders,
    get_all_open_stock_orders,
    # order_buy_fractional_by_price,  # DEPRECATED
    order_buy_limit,
    order_buy_market,
    order_buy_option_limit,
    # order_buy_stop_loss,  # DEPRECATED
    # order_buy_trailing_stop,  # DEPRECATED
    order_option_credit_spread,
    order_option_debit_spread,
    order_sell_limit,
    order_sell_market,
    order_sell_option_limit,
    order_sell_stop_loss,
    # order_sell_trailing_stop,  # DEPRECATED
)
from open_stocks_mcp.tools.robinhood_user_profile_tools import (
    get_account_profile,
    get_account_settings,
    get_basic_profile,
    get_complete_profile,
    get_investment_profile,
    get_security_profile,
    get_user_profile,
)
from open_stocks_mcp.tools.robinhood_watchlist_tools import (
    add_symbols_to_watchlist,
    get_all_watchlists,
    get_watchlist_by_name,
    get_watchlist_performance,
    remove_symbols_from_watchlist,
)
from open_stocks_mcp.tools.session_manager import get_session_manager

# Load environment variables from .env file
load_dotenv()

# Create global MCP server instance for Inspector
mcp = FastMCP("Open Stocks MCP")


# Register tools at module level for Inspector
@mcp.tool()
async def list_tools() -> dict[str, Any]:
    """Provides a list of available tools and their descriptions."""
    return await list_available_tools(mcp)


@mcp.tool()
async def account_info() -> dict[str, Any]:
    """Gets basic Robinhood account information."""
    return await get_account_info()  # type: ignore[no-any-return]


@mcp.tool()
async def portfolio() -> dict[str, Any]:
    """Provides a high-level overview of the portfolio."""
    return await get_portfolio()  # type: ignore[no-any-return]


@mcp.tool()
async def stock_orders() -> dict[str, Any]:
    """Retrieves a list of recent stock order history and their statuses."""
    return await get_stock_orders()  # type: ignore[no-any-return]


@mcp.tool()
async def options_orders() -> dict[str, Any]:
    """Retrieves a list of recent options order history and their statuses."""
    return await get_options_orders()  # type: ignore[no-any-return]


@mcp.tool()
async def account_details() -> dict[str, Any]:
    """Gets comprehensive account details including buying power and cash balances."""
    return await get_account_details()  # type: ignore[no-any-return]


@mcp.tool()
async def positions() -> dict[str, Any]:
    """Gets current stock positions with quantities and values."""
    return await get_positions()  # type: ignore[no-any-return]


# Advanced Portfolio Analytics Tools
@mcp.tool()
async def build_holdings() -> dict[str, Any]:
    """Builds comprehensive holdings with dividend information and performance metrics.

    Returns detailed holdings data including cost basis, equity, dividends, and performance.
    """
    return await get_build_holdings()  # type: ignore[no-any-return]


@mcp.tool()
async def build_user_profile() -> dict[str, Any]:
    """Builds comprehensive user profile with equity, cash, and dividend totals.

    Returns complete financial profile including total equity, cash balances, and dividend totals.
    """
    return await get_build_user_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def day_trades() -> dict[str, Any]:
    """Gets pattern day trading information and tracking.

    Returns day trade count, remaining day trades, PDT status, and buying power information.
    """
    return await get_day_trades()  # type: ignore[no-any-return]


# Session Management Tools
@mcp.tool()
async def session_status() -> dict[str, Any]:
    """Gets current session status and authentication information."""
    session_manager = get_session_manager()
    session_info = session_manager.get_session_info()

    return {"result": {**session_info, "status": "success"}}


@mcp.tool()
async def rate_limit_status() -> dict[str, Any]:
    """Gets current rate limit usage and statistics."""
    rate_limiter = get_rate_limiter()
    stats = rate_limiter.get_stats()

    return {"result": {**stats, "status": "success"}}


# Monitoring Tools
@mcp.tool()
async def metrics_summary() -> dict[str, Any]:
    """Gets comprehensive metrics summary for monitoring."""
    metrics_collector = get_metrics_collector()
    metrics = await metrics_collector.get_metrics()

    return {"result": {**metrics, "status": "success"}}


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """Gets health status of the MCP server."""
    metrics_collector = get_metrics_collector()
    health_status = await metrics_collector.get_health_status()

    return {"result": {**health_status, "status": "success"}}


# Market Data Tools
@mcp.tool()
async def stock_price(symbol: str) -> dict[str, Any]:
    """Gets current stock price and basic metrics.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_price(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_info(symbol: str) -> dict[str, Any]:
    """Gets detailed company information and fundamentals.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_info(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def search_stocks_tool(query: str) -> dict[str, Any]:
    """Searches for stocks by symbol or company name.

    Args:
        query: Search query (symbol or company name)
    """
    return await search_stocks(query)  # type: ignore[no-any-return]


@mcp.tool()
async def market_hours() -> dict[str, Any]:
    """Gets current market hours and status."""
    return await get_market_hours()  # type: ignore[no-any-return]


@mcp.tool()
async def price_history(symbol: str, period: str = "week") -> dict[str, Any]:
    """Gets historical price data for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        period: Time period ("day", "week", "month", "3month", "year", "5year")
    """
    return await get_price_history(symbol, period)  # type: ignore[no-any-return]


# Phase 6: Advanced Instrument Data Tools
@mcp.tool()
async def instruments_by_symbols(symbols: list[str]) -> dict[str, Any]:
    """Gets detailed instrument metadata for multiple symbols.

    Args:
        symbols: List of stock ticker symbols (e.g., ["AAPL", "GOOGL", "MSFT"])
    """
    return await get_instruments_by_symbols(symbols)  # type: ignore[no-any-return]


@mcp.tool()
async def find_instruments(query: str) -> dict[str, Any]:
    """Searches for instrument information by various criteria.

    Args:
        query: Search query string (can be symbol, company name, or other criteria)
    """
    return await find_instrument_data(query)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_quote_by_id(instrument_id: str) -> dict[str, Any]:
    """Gets stock quote using Robinhood's internal instrument ID.

    Args:
        instrument_id: Robinhood's internal instrument ID
    """
    return await get_stock_quote_by_id(instrument_id)  # type: ignore[no-any-return]


@mcp.tool()
async def pricebook_by_symbol(symbol: str) -> dict[str, Any]:
    """Gets Level II order book data for a symbol (requires Gold subscription).

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_pricebook_by_symbol(symbol)  # type: ignore[no-any-return]


# Dividend & Income Tools
@mcp.tool()
async def dividends() -> dict[str, Any]:
    """Gets all dividend payment history for the account."""
    return await get_dividends()  # type: ignore[no-any-return]


@mcp.tool()
async def total_dividends() -> dict[str, Any]:
    """Gets total dividends received across all time."""
    return await get_total_dividends()  # type: ignore[no-any-return]


@mcp.tool()
async def dividends_by_instrument(symbol: str) -> dict[str, Any]:
    """Gets dividend history for a specific stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_dividends_by_instrument(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def interest_payments() -> dict[str, Any]:
    """Gets interest payment history from cash management."""
    return await get_interest_payments()  # type: ignore[no-any-return]


@mcp.tool()
async def stock_loan_payments() -> dict[str, Any]:
    """Gets stock loan payment history from the stock lending program."""
    return await get_stock_loan_payments()  # type: ignore[no-any-return]


# Advanced Market Data Tools
@mcp.tool()
async def top_movers_sp500(direction: str = "up") -> dict[str, Any]:
    """Gets top S&P 500 movers for the day.

    Args:
        direction: Direction of movement, either 'up' or 'down' (default: 'up')
    """
    return await get_top_movers_sp500(direction)  # type: ignore[no-any-return]


@mcp.tool()
async def top_100_stocks() -> dict[str, Any]:
    """Gets top 100 most popular stocks on Robinhood."""
    return await get_top_100()  # type: ignore[no-any-return]


@mcp.tool()
async def top_movers() -> dict[str, Any]:
    """Gets top 20 movers on Robinhood."""
    return await get_top_movers()  # type: ignore[no-any-return]


@mcp.tool()
async def stocks_by_tag(tag: str) -> dict[str, Any]:
    """Gets stocks filtered by market category tag.

    Args:
        tag: Market category tag (e.g., 'technology', 'biopharmaceutical', 'upcoming-earnings')
    """
    return await get_stocks_by_tag(tag)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_ratings(symbol: str) -> dict[str, Any]:
    """Gets analyst ratings for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_ratings(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_earnings(symbol: str) -> dict[str, Any]:
    """Gets earnings reports for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_earnings(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_news(symbol: str) -> dict[str, Any]:
    """Gets news stories for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_news(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_splits(symbol: str) -> dict[str, Any]:
    """Gets stock split history for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_splits(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_events(symbol: str) -> dict[str, Any]:
    """Gets corporate events for a stock (for owned positions).

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_events(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def stock_level2_data(symbol: str) -> dict[str, Any]:
    """Gets Level II market data for a stock (Gold subscription required).

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_stock_level2_data(symbol)  # type: ignore[no-any-return]


# Phase 3: Options Trading Tools
@mcp.tool()
async def options_chains(symbol: str) -> dict[str, Any]:
    """Gets complete option chains for a stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
    """
    return await get_options_chains(symbol)  # type: ignore[no-any-return]


@mcp.tool()
async def find_options(
    symbol: str, expiration_date: str | None = None, option_type: str | None = None
) -> dict[str, Any]:
    """Finds tradable options with optional filtering.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        expiration_date: Optional expiration date in YYYY-MM-DD format
        option_type: Optional option type ("call" or "put")
    """
    return await find_tradable_options(symbol, expiration_date, option_type)  # type: ignore[no-any-return]


@mcp.tool()
async def option_market_data(option_id: str) -> dict[str, Any]:
    """Gets market data for a specific option contract.

    Args:
        option_id: Unique option contract ID
    """
    return await get_option_market_data(option_id)  # type: ignore[no-any-return]


@mcp.tool()
async def option_historicals(
    symbol: str,
    expiration_date: str,
    strike_price: str,
    option_type: str,
    interval: str = "hour",
    span: str = "week",
) -> dict[str, Any]:
    """Gets historical price data for an option contract.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        expiration_date: Expiration date in YYYY-MM-DD format
        strike_price: Strike price as string
        option_type: Option type ("call" or "put")
        interval: Time interval (default: "hour")
        span: Time span (default: "week")
    """
    result = await get_option_historicals(
        symbol, expiration_date, strike_price, option_type, interval, span
    )
    return result  # type: ignore[no-any-return]


@mcp.tool()
async def aggregate_option_positions() -> dict[str, Any]:
    """Gets aggregated option positions collapsed by underlying stock."""
    return await get_aggregate_positions()  # type: ignore[no-any-return]


@mcp.tool()
async def all_option_positions() -> dict[str, Any]:
    """Gets all option positions ever held."""
    return await get_all_option_positions()  # type: ignore[no-any-return]


@mcp.tool()
async def open_option_positions() -> dict[str, Any]:
    """Gets currently open option positions."""
    return await get_open_option_positions()  # type: ignore[no-any-return]


@mcp.tool()
async def open_option_positions_with_details() -> dict[str, Any]:
    """Gets currently open option positions with enriched details including call/put type.

    This enhanced version includes complete option instrument details for each position:
    - option_type: "call" or "put"
    - strike_price: Strike price of the option
    - option_symbol: OCC option symbol
    - tradability: Trading status
    - state: Option state (active, expired, etc.)
    - underlying_symbol: Underlying stock symbol
    - enrichment_success_rate: Percentage of positions successfully enriched

    Use this instead of open_option_positions() when you need complete option details.
    """
    return await get_open_option_positions_with_details()  # type: ignore[no-any-return]


# Phase 3: Watchlist Management Tools
@mcp.tool()
async def all_watchlists() -> dict[str, Any]:
    """Gets all user-created watchlists."""
    return await get_all_watchlists()  # type: ignore[no-any-return]


@mcp.tool()
async def watchlist_by_name(watchlist_name: str) -> dict[str, Any]:
    """Gets contents of a specific watchlist by name.

    Args:
        watchlist_name: Name of the watchlist to retrieve
    """
    return await get_watchlist_by_name(watchlist_name)  # type: ignore[no-any-return]


@mcp.tool()
async def add_to_watchlist(watchlist_name: str, symbols: list[str]) -> dict[str, Any]:
    """Adds symbols to a watchlist.

    Args:
        watchlist_name: Name of the watchlist
        symbols: List of stock symbols to add
    """
    return await add_symbols_to_watchlist(watchlist_name, symbols)  # type: ignore[no-any-return]


@mcp.tool()
async def remove_from_watchlist(
    watchlist_name: str, symbols: list[str]
) -> dict[str, Any]:
    """Removes symbols from a watchlist.

    Args:
        watchlist_name: Name of the watchlist
        symbols: List of stock symbols to remove
    """
    return await remove_symbols_from_watchlist(watchlist_name, symbols)  # type: ignore[no-any-return]


@mcp.tool()
async def watchlist_performance(watchlist_name: str) -> dict[str, Any]:
    """Gets performance metrics for a watchlist.

    Args:
        watchlist_name: Name of the watchlist to analyze
    """
    return await get_watchlist_performance(watchlist_name)  # type: ignore[no-any-return]


# Phase 3: Account Features & Notifications Tools
@mcp.tool()
async def notifications(count: int = 20) -> dict[str, Any]:
    """Gets account notifications and alerts.

    Args:
        count: Number of notifications to retrieve (default: 20)
    """
    return await get_notifications(count)  # type: ignore[no-any-return]


@mcp.tool()
async def latest_notification() -> dict[str, Any]:
    """Gets the most recent notification."""
    return await get_latest_notification()  # type: ignore[no-any-return]


@mcp.tool()
async def margin_calls() -> dict[str, Any]:
    """Gets margin call information."""
    return await get_margin_calls()  # type: ignore[no-any-return]


@mcp.tool()
async def margin_interest() -> dict[str, Any]:
    """Gets margin interest charges and rates."""
    return await get_margin_interest()  # type: ignore[no-any-return]


@mcp.tool()
async def subscription_fees() -> dict[str, Any]:
    """Gets Robinhood Gold subscription fees."""
    return await get_subscription_fees()  # type: ignore[no-any-return]


@mcp.tool()
async def referrals() -> dict[str, Any]:
    """Gets referral program information."""
    return await get_referrals()  # type: ignore[no-any-return]


@mcp.tool()
async def account_features() -> dict[str, Any]:
    """Gets comprehensive account features and settings."""
    return await get_account_features()  # type: ignore[no-any-return]


# Phase 3: User Profile Tools
@mcp.tool()
async def account_profile() -> dict[str, Any]:
    """Gets trading account profile and configuration."""
    return await get_account_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def basic_profile() -> dict[str, Any]:
    """Gets basic user profile information."""
    return await get_basic_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def investment_profile() -> dict[str, Any]:
    """Gets investment profile and risk assessment."""
    return await get_investment_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def security_profile() -> dict[str, Any]:
    """Gets security profile and settings."""
    return await get_security_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def user_profile() -> dict[str, Any]:
    """Gets comprehensive user profile information."""
    return await get_user_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def complete_profile() -> dict[str, Any]:
    """Gets complete user profile combining all profile types."""
    return await get_complete_profile()  # type: ignore[no-any-return]


@mcp.tool()
async def account_settings() -> dict[str, Any]:
    """Gets account settings and preferences."""
    return await get_account_settings()  # type: ignore[no-any-return]


# Phase 7: Trading Capabilities Tools


# Stock Order Placement Tools
@mcp.tool()
async def buy_stock_market(symbol: str, quantity: int) -> dict[str, Any]:
    """Places a market buy order for a stock.

    Args:
        symbol: The stock symbol to buy (e.g., "AAPL")
        quantity: The number of shares to buy
    """
    return await order_buy_market(symbol, quantity)  # type: ignore[no-any-return]


@mcp.tool()
async def sell_stock_market(symbol: str, quantity: int) -> dict[str, Any]:
    """Places a market sell order for a stock.

    Args:
        symbol: The stock symbol to sell (e.g., "AAPL")
        quantity: The number of shares to sell
    """
    return await order_sell_market(symbol, quantity)  # type: ignore[no-any-return]


@mcp.tool()
async def buy_stock_limit(
    symbol: str, quantity: int, limit_price: float
) -> dict[str, Any]:
    """Places a limit buy order for a stock.

    Args:
        symbol: The stock symbol to buy (e.g., "AAPL")
        quantity: The number of shares to buy
        limit_price: The maximum price per share
    """
    return await order_buy_limit(symbol, quantity, limit_price)  # type: ignore[no-any-return]


@mcp.tool()
async def sell_stock_limit(
    symbol: str, quantity: int, limit_price: float
) -> dict[str, Any]:
    """Places a limit sell order for a stock.

    Args:
        symbol: The stock symbol to sell (e.g., "AAPL")
        quantity: The number of shares to sell
        limit_price: The minimum price per share
    """
    return await order_sell_limit(symbol, quantity, limit_price)  # type: ignore[no-any-return]


# DEPRECATED: buy_stock_stop_loss removed - uncommon use case for most traders
# Buy stop-loss orders are primarily used for short covering or breakout trading
# which are advanced strategies not commonly used by typical retail investors
# @mcp.tool()
# async def buy_stock_stop_loss(
#     symbol: str, quantity: int, stop_price: float
# ) -> dict[str, Any]:
#     """Places a stop loss buy order for a stock.
#
#     Args:
#         symbol: The stock symbol to buy (e.g., "AAPL")
#         quantity: The number of shares to buy
#         stop_price: The stop price that triggers the order
#     """
#     return await order_buy_stop_loss(symbol, quantity, stop_price)  # type: ignore[no-any-return]


@mcp.tool()
async def sell_stock_stop_loss(
    symbol: str, quantity: int, stop_price: float
) -> dict[str, Any]:
    """Places a stop loss sell order for a stock.

    Args:
        symbol: The stock symbol to sell (e.g., "AAPL")
        quantity: The number of shares to sell
        stop_price: The stop price that triggers the order
    """
    return await order_sell_stop_loss(symbol, quantity, stop_price)  # type: ignore[no-any-return]


# DEPRECATED: buy_stock_trailing_stop removed - uncommon use case for most traders
# Trailing stop buy orders are advanced trading strategies primarily used for breakout trading
# which are not commonly used by typical retail investors
# @mcp.tool()
# async def buy_stock_trailing_stop(
#     symbol: str, quantity: int, trail_amount: float
# ) -> dict[str, Any]:
#     """Places a trailing stop buy order for a stock.
#
#     Args:
#         symbol: The stock symbol to buy (e.g., "AAPL")
#         quantity: The number of shares to buy
#         trail_amount: The trailing amount (percentage or dollar amount)
#     """
#     return await order_buy_trailing_stop(symbol, quantity, trail_amount)  # type: ignore[no-any-return]


# DEPRECATED: sell_stock_trailing_stop removed - uncommon use case for most traders
# Trailing stop sell orders are advanced trading strategies that require careful market timing
# and are not commonly used by typical retail investors
# @mcp.tool()
# async def sell_stock_trailing_stop(
#     symbol: str, quantity: int, trail_amount: float
# ) -> dict[str, Any]:
#     """Places a trailing stop sell order for a stock.
#
#     Args:
#         symbol: The stock symbol to sell (e.g., "AAPL")
#         quantity: The number of shares to sell
#         trail_amount: The trailing amount (percentage or dollar amount)
#     """
#     return await order_sell_trailing_stop(symbol, quantity, trail_amount)  # type: ignore[no-any-return]


# DEPRECATED: buy_fractional_stock removed - uncommon use case for most traders
# Fractional share trading is useful but represents a small subset of trading activity
# and most retail traders prefer whole share purchases for clearer position management
# @mcp.tool()
# async def buy_fractional_stock(symbol: str, amount_in_dollars: float) -> dict[str, Any]:
#     """Places a fractional share buy order using dollar amount.
#
#     Args:
#         symbol: The stock symbol to buy (e.g., "AAPL")
#         amount_in_dollars: The dollar amount to invest
#     """
#     return await order_buy_fractional_by_price(symbol, amount_in_dollars)  # type: ignore[no-any-return]


# Options Order Placement Tools
@mcp.tool()
async def buy_option_limit(
    instrument_id: str, quantity: int, limit_price: float
) -> dict[str, Any]:
    """Places a limit buy order for an option.

    Args:
        instrument_id: The option instrument ID
        quantity: The number of option contracts to buy
        limit_price: The maximum price per contract
    """
    return await order_buy_option_limit(instrument_id, quantity, limit_price)  # type: ignore[no-any-return]


@mcp.tool()
async def sell_option_limit(
    instrument_id: str, quantity: int, limit_price: float
) -> dict[str, Any]:
    """Places a limit sell order for an option.

    Args:
        instrument_id: The option instrument ID
        quantity: The number of option contracts to sell
        limit_price: The minimum price per contract
    """
    return await order_sell_option_limit(instrument_id, quantity, limit_price)  # type: ignore[no-any-return]


@mcp.tool()
async def option_credit_spread(
    short_instrument_id: str,
    long_instrument_id: str,
    quantity: int,
    credit_price: float,
) -> dict[str, Any]:
    """Places a credit spread order (sell short option, buy long option).

    Args:
        short_instrument_id: The option instrument ID to sell (short leg)
        long_instrument_id: The option instrument ID to buy (long leg)
        quantity: The number of spread contracts
        credit_price: The net credit received per spread
    """
    result: dict[str, Any] = await order_option_credit_spread(
        short_instrument_id, long_instrument_id, quantity, credit_price
    )
    return result


@mcp.tool()
async def option_debit_spread(
    short_instrument_id: str, long_instrument_id: str, quantity: int, debit_price: float
) -> dict[str, Any]:
    """Places a debit spread order (buy long option, sell short option).

    Args:
        short_instrument_id: The option instrument ID to sell (short leg)
        long_instrument_id: The option instrument ID to buy (long leg)
        quantity: The number of spread contracts
        debit_price: The net debit paid per spread
    """
    result: dict[str, Any] = await order_option_debit_spread(
        short_instrument_id, long_instrument_id, quantity, debit_price
    )
    return result


# Order Management Tools
@mcp.tool()
async def cancel_stock_order_by_id(order_id: str) -> dict[str, Any]:
    """Cancels a specific stock order.

    Args:
        order_id: The ID of the order to cancel
    """
    return await cancel_stock_order(order_id)  # type: ignore[no-any-return]


@mcp.tool()
async def cancel_option_order_by_id(order_id: str) -> dict[str, Any]:
    """Cancels a specific option order.

    Args:
        order_id: The ID of the order to cancel
    """
    return await cancel_option_order(order_id)  # type: ignore[no-any-return]


@mcp.tool()
async def cancel_all_stock_orders_tool() -> dict[str, Any]:
    """Cancels all open stock orders."""
    return await cancel_all_stock_orders()  # type: ignore[no-any-return]


@mcp.tool()
async def cancel_all_option_orders_tool() -> dict[str, Any]:
    """Cancels all open option orders."""
    return await cancel_all_option_orders()  # type: ignore[no-any-return]


@mcp.tool()
async def open_stock_orders() -> dict[str, Any]:
    """Retrieves all open stock orders."""
    return await get_all_open_stock_orders()  # type: ignore[no-any-return]


@mcp.tool()
async def open_option_orders() -> dict[str, Any]:
    """Retrieves all open option orders."""
    return await get_all_open_option_orders()  # type: ignore[no-any-return]


def create_mcp_server(config: ServerConfig | None = None) -> FastMCP:
    """Create and configure the MCP server instance"""
    if config is None:
        config = load_config()

    setup_logging(config)
    return mcp


def attempt_login(username: str, password: str) -> None:
    """
    Attempt to log in to Robinhood using the session manager.

    It verifies success by fetching the user profile.
    """
    try:
        logger.info(f"Attempting login for user: {username}")

        # Set credentials in session manager
        session_manager = get_session_manager()
        session_manager.set_credentials(username, password)

        # Use asyncio to run the async authentication
        async def do_auth() -> bool:
            return await session_manager.ensure_authenticated()

        success = asyncio.run(do_auth())

        if success:
            logger.info(f"✅ Successfully logged into Robinhood for user: {username}")
            # Verify by getting session info
            session_info = session_manager.get_session_info()
            logger.info(f"Session info: {session_info}")
        else:
            logger.error("❌ Login failed: Could not authenticate with Robinhood.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during login: {e}")
        sys.exit(1)


@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP transport")
@click.option("--host", default="localhost", help="Host to bind to")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport type (stdio or http)",
)
@click.option(
    "--username", help="Robinhood username.", default=os.getenv("ROBINHOOD_USERNAME")
)
@click.option(
    "--password", help="Robinhood password.", default=os.getenv("ROBINHOOD_PASSWORD")
)
def main(
    port: int, host: str, transport: str, username: str | None, password: str | None
) -> int:
    """Run the server with specified transport and handle authentication."""
    if not username:
        username = click.prompt("Please enter your Robinhood username")
    if not password:
        password = click.prompt("Please enter your Robinhood password", hide_input=True)

    # Perform login with stored session if available
    attempt_login(username, password)

    server = create_mcp_server()

    try:
        if transport == "stdio":
            logger.info("Starting MCP server with STDIO transport")
            asyncio.run(server.run_stdio_async())
        else:
            # Use our enhanced HTTP transport
            from open_stocks_mcp.server.http_transport import run_http_server

            asyncio.run(run_http_server(server, host, port))
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        # Use session manager for logout
        session_manager = get_session_manager()
        asyncio.run(session_manager.logout())
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
