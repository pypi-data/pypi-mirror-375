"""MCP tools for Robin Stocks account operations."""

from typing import Any

import robin_stocks.robinhood as rh

from open_stocks_mcp.logging_config import logger
from open_stocks_mcp.tools.error_handling import (
    create_no_data_response,
    create_success_response,
    execute_with_retry,
    handle_robin_stocks_errors,
    log_api_call,
    sanitize_api_response,
)


@handle_robin_stocks_errors
async def get_account_info() -> dict[str, Any]:
    """
    Retrieves basic information about the Robinhood account.

    Returns:
        A JSON object containing account details in the result field.
    """
    log_api_call("get_account_info")

    # Get account info with retry logic
    account_info = await execute_with_retry(rh.load_user_profile)

    if not account_info:
        return create_no_data_response("Account information not available")

    # Sanitize sensitive data
    account_info = sanitize_api_response(account_info)

    logger.info("Successfully retrieved account info.")
    return create_success_response(
        {
            "username": account_info.get("username", "N/A"),
            "created_at": account_info.get("created_at", "N/A"),
        }
    )


@handle_robin_stocks_errors
async def get_portfolio() -> dict[str, Any]:
    """
    Provides a high-level overview of the portfolio.

    Returns:
        A JSON object containing the portfolio overview in the result field.
    """
    log_api_call("get_portfolio")

    # Get portfolio data with retry logic
    portfolio = await execute_with_retry(rh.load_portfolio_profile)

    if not portfolio:
        return create_no_data_response("Portfolio data not available")

    # Sanitize sensitive data
    portfolio = sanitize_api_response(portfolio)

    logger.info("Successfully retrieved portfolio overview.")
    return create_success_response(
        {
            "market_value": portfolio.get("market_value", "N/A"),
            "equity": portfolio.get("equity", "N/A"),
            "buying_power": portfolio.get("buying_power", "N/A"),
        }
    )


@handle_robin_stocks_errors
async def get_account_details() -> dict[str, Any]:
    """
    Retrieves comprehensive account details including buying power and cash balances.

    All monetary values are returned as currency objects with amount, currency_code,
    and currency_id fields for internationalization support.

    Returns:
        A JSON object containing detailed account information in the result field:
        {
            "result": {
                "portfolio_equity": {
                    "amount": "9723.99",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "total_equity": {
                    "amount": "9723.99",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "account_buying_power": {
                    "amount": "1029.63",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "options_buying_power": {
                    "amount": "1029.63",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "crypto_buying_power": {
                    "amount": "1029.63",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "uninvested_cash": {
                    "amount": "7629.63",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "withdrawable_cash": {
                    "amount": "1029.63",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "cash_available_from_instant_deposits": {
                    "amount": "0",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "cash_held_for_orders": {
                    "amount": "0",
                    "currency_code": "USD",
                    "currency_id": "1072fc76-1862-41ab-82c2-485837590762"
                },
                "near_margin_call": false,
                "status": "success"
            }
        }
    """
    log_api_call("get_account_details")

    # Get account data with retry logic
    account_response = await execute_with_retry(rh.load_phoenix_account)

    if not account_response or not account_response.get("results"):
        return create_no_data_response("No account data found")

    # Extract account data from results (it's a list with first element containing data)
    account_data = account_response["results"][0] if account_response["results"] else {}

    # Sanitize sensitive data
    account_data = sanitize_api_response(account_data)

    # Helper function to extract amount from currency objects
    def get_currency_amount(field_data: Any) -> str:
        if isinstance(field_data, dict) and "amount" in field_data:
            return str(field_data["amount"])
        return str(field_data) if field_data is not None else "N/A"

    logger.info("Successfully retrieved account details.")
    return create_success_response(
        {
            "portfolio_equity": get_currency_amount(
                account_data.get("portfolio_equity")
            ),
            "total_equity": get_currency_amount(account_data.get("total_equity")),
            "account_buying_power": get_currency_amount(
                account_data.get("account_buying_power")
            ),
            "options_buying_power": get_currency_amount(
                account_data.get("options_buying_power")
            ),
            "crypto_buying_power": get_currency_amount(
                account_data.get("crypto_buying_power")
            ),
            "uninvested_cash": get_currency_amount(account_data.get("uninvested_cash")),
            "withdrawable_cash": get_currency_amount(
                account_data.get("withdrawable_cash")
            ),
            "cash_available_from_instant_deposits": get_currency_amount(
                account_data.get("cash_available_from_instant_deposits")
            ),
            "cash_held_for_orders": get_currency_amount(
                account_data.get("cash_held_for_orders")
            ),
            "near_margin_call": account_data.get("near_margin_call", "N/A"),
        }
    )


@handle_robin_stocks_errors
async def get_positions() -> dict[str, Any]:
    """
    Retrieves current stock positions with quantities and values.

    Returns:
        A JSON object containing current stock positions in the result field.
    """
    log_api_call("get_positions")

    # Get positions with retry logic
    positions = await execute_with_retry(rh.get_open_stock_positions)

    if not positions:
        return create_success_response(
            {"positions": [], "count": 0, "message": "No open stock positions found."}
        )

    position_list = []
    for position in positions:
        # Get symbol from instrument URL with retry logic
        instrument_url = position.get("instrument")
        symbol = "N/A"
        if instrument_url:
            try:
                symbol = await execute_with_retry(rh.get_symbol_by_url, instrument_url)
            except Exception as e:
                logger.warning(
                    f"Failed to get symbol for instrument {instrument_url}: {e}"
                )

        quantity = position.get("quantity", "0")

        # Only include positions with non-zero quantity
        if float(quantity) > 0:
            position_data = {
                "symbol": symbol,
                "quantity": quantity,
                "average_buy_price": position.get("average_buy_price", "0"),
                "updated_at": position.get("updated_at", "N/A"),
            }
            position_list.append(position_data)

    logger.info("Successfully retrieved current positions.")
    return create_success_response(
        {"positions": position_list, "count": len(position_list)}
    )
