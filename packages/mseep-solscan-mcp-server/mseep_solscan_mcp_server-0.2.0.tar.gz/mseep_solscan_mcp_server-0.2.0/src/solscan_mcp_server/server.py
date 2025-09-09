"""Server implementation for the Solscan MCP server."""

import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator, List, Optional

import aiohttp
from fastmcp import Context, FastMCP

from solscan_mcp_server.api import (
    ActivityType,
    BalanceFlow,
    SortOrder,
    get_account_transactions,
    get_balance_change,
    get_defi_activities,
    get_token_accounts,
    get_token_holders,
    get_token_markets,
    get_token_meta,
    get_token_price,
    get_transaction_actions,
    get_transaction_detail,
)

logger = logging.getLogger(__name__)


class SolscanTools(str, Enum):
    """Enum of available Solscan tools."""

    TOKEN_META = "token_meta"
    TOKEN_MARKETS = "token_markets"
    TOKEN_HOLDERS = "token_holders"
    TOKEN_PRICE = "token_price"
    TOKEN_ACCOUNTS = "token_accounts"
    DEFI_ACTIVITIES = "defi_activities"
    BALANCE_CHANGE = "balance_change"
    ACCOUNT_TRANSACTIONS = "account_transactions"
    TRANSACTION_DETAIL = "transaction_detail"
    TRANSACTION_ACTIONS = "transaction_actions"


@dataclass
class SolscanContext:
    """Application context containing shared resources."""

    client: aiohttp.ClientSession
    api_key: str


@asynccontextmanager
async def solscan_lifespan(
    server: FastMCP[SolscanContext], api_key: str
) -> AsyncIterator[SolscanContext]:
    """Manage server lifecycle and resources.

    Args:
        server: The FastMCP server instance
        api_key: The Solscan API key

    Yields:
        SolscanContext: The context containing the shared HTTP client and configuration

    Raises:
        ValueError: If the Solscan API key is not provided
    """
    if not api_key:
        raise ValueError("Solscan API key is required")

    # Initialize shared HTTP client
    client = aiohttp.ClientSession(headers={"token": api_key})
    try:
        yield SolscanContext(client=client, api_key=api_key)
    finally:
        # Ensure client is properly closed on shutdown
        await client.close()


def create_mcp_server(
    api_key: str,
    host: str = "127.0.0.1",
    port: int = 8050,
) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        api_key: The Solscan API key
        host: The host to bind to (default: 127.0.0.1)
        port: The port to listen on (default: 8050)

    Returns:
        FastMCP: The configured server instance
    """
    # Initialize FastMCP server with lifespan management and server config
    server = FastMCP(
        "mcp-solscan",
        description="MCP server for interacting with Solscan Pro API",
        lifespan=lambda s: solscan_lifespan(s, api_key),
        host=host,
        port=port,
    )

    # Register tools
    @server.tool()
    async def token_meta_tool(ctx: Context, token_address: str) -> str:
        """Get token metadata from Solscan.

        Args:
            ctx: The MCP context containing shared resources
            token_address: The token address to get metadata for

        Returns:
            str: JSON string containing token metadata
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_token_meta(token_address, solscan_ctx.api_key)
        return json.dumps(result, indent=2)

    @server.tool()
    async def token_markets_tool(
        ctx: Context,
        token_address: str,
        sort_by: Optional[str] = None,
        program: Optional[list[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> str:
        """Get token market data and liquidity pools.

        Args:
            ctx: The MCP context containing shared resources
            token_address: The token address to get market data for
            sort_by: Field to sort results by
            program: List of programs to filter by
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            str: JSON string containing token market data
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_token_markets(
            token_address=token_address,
            sort_by=sort_by,
            program=program,
            page=page,
            page_size=page_size,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    async def token_holders_tool(
        ctx: Context,
        token_address: str,
        page: int = 1,
        page_size: int = 40,
        from_amount: Optional[str] = None,
        to_amount: Optional[str] = None,
    ) -> str:
        """Get token holder information.

        Args:
            ctx: The MCP context containing shared resources
            token_address: The token address to get holder information for
            page: Page number for pagination
            page_size: Number of results per page (10, 20, 30, or 40)
            from_amount: Minimum amount filter
            to_amount: Maximum amount filter

        Returns:
            str: JSON string containing token holder information
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_token_holders(
            token_address=token_address,
            page=page,
            page_size=page_size,
            from_amount=from_amount,
            to_amount=to_amount,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    async def token_price_tool(
        ctx: Context,
        token_address: str,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> str:
        """Get token price information.

        Args:
            ctx: The MCP context containing shared resources
            token_address: The token address to get price information for
            from_time: Start time in YYYYMMDD format
            to_time: End time in YYYYMMDD format

        Returns:
            str: JSON string containing token price information
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_token_price(
            token_address=token_address,
            from_time=from_time,
            to_time=to_time,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    async def token_accounts_tool(
        ctx: Context,
        wallet_address: str,
        type: str = "token",
        page: int = 1,
        page_size: int = 40,
        hide_zero: bool = True,
    ) -> str:
        """Get token accounts for a wallet.

        Args:
            ctx: The MCP context containing shared resources
            wallet_address: The wallet address to get token accounts for
            type: Type of tokens to fetch ('token' or 'nft')
            page: Page number for pagination
            page_size: Number of results per page (10, 20, 30, or 40)
            hide_zero: Whether to hide zero balance accounts

        Returns:
            str: JSON string containing token account information
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_token_accounts(
            wallet_address=wallet_address,
            type=type,
            page=page,
            page_size=page_size,
            hide_zero=hide_zero,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    async def defi_activities_tool(
        ctx: Context,
        wallet_address: str,
        activity_type: Optional[List[ActivityType]] = None,
        from_address: Optional[str] = None,
        platform: Optional[List[str]] = None,
        source: Optional[List[str]] = None,
        token: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str = "block_time",
        sort_order: SortOrder = SortOrder.DESC,
    ) -> str:
        """Get DeFi activities for a wallet.

        Args:
            ctx: The MCP context containing shared resources
            wallet_address: The wallet address to get DeFi activities for
            activity_type: List of activity types to filter by
            from_address: Address to filter activities from
            platform: List of platforms to filter by (max 5)
            source: List of sources to filter by (max 5)
            token: Token address to filter by
            from_time: Start time filter
            to_time: End time filter
            page: Page number for pagination
            page_size: Number of results per page (10, 20, 30, 40, 60, or 100)
            sort_by: Field to sort by (currently only 'block_time' supported)
            sort_order: Sort order (asc or desc)

        Returns:
            str: JSON string containing DeFi activity information
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_defi_activities(
            wallet_address=wallet_address,
            activity_type=activity_type,
            from_address=from_address,
            platform=platform,
            source=source,
            token=token,
            from_time=from_time,
            to_time=to_time,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    async def balance_change_tool(
        ctx: Context,
        wallet_address: str,
        token_account: Optional[str] = None,
        token: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        page_size: int = 100,
        page: int = 1,
        remove_spam: bool = True,
        amount: Optional[List[float]] = None,
        flow: Optional[BalanceFlow] = None,
        sort_by: str = "block_time",
        sort_order: SortOrder = SortOrder.DESC,
    ) -> str:
        """Get balance changes for a wallet.

        Args:
            ctx: The MCP context containing shared resources
            wallet_address: The wallet address to get balance changes for
            token_account: Token account address to filter by
            token: Token address to filter by
            from_time: Start time filter
            to_time: End time filter
            page_size: Number of results per page (10, 20, 30, 40, 60, or 100)
            page: Page number for pagination
            remove_spam: Whether to filter out spam transactions
            amount: Amount range filter [min, max]
            flow: Balance flow direction filter (in/out)
            sort_by: Field to sort by (currently only 'block_time' supported)
            sort_order: Sort order (asc or desc)

        Returns:
            str: JSON string containing balance change information
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_balance_change(
            wallet_address=wallet_address,
            token_account=token_account,
            token=token,
            from_time=from_time,
            to_time=to_time,
            page_size=page_size,
            page=page,
            remove_spam=remove_spam,
            amount=amount,
            flow=flow,
            sort_by=sort_by,
            sort_order=sort_order,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    @server.tool()
    async def transaction_detail_tool(ctx: Context, tx: str) -> str:
        """Get detailed transaction information.

        Args:
            ctx: The MCP context containing shared resources
            tx: Transaction signature

        Returns:
            str: JSON string containing transaction details
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_transaction_detail(tx, solscan_ctx.api_key)
        return json.dumps(result, indent=2)

    @server.tool()
    async def transaction_actions_tool(ctx: Context, tx: str) -> str:
        """Get transaction actions and token transfers.

        Args:
            ctx: The MCP context containing shared resources
            tx: Transaction signature

        Returns:
            str: JSON string containing transaction actions
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_transaction_actions(tx, solscan_ctx.api_key)
        return json.dumps(result, indent=2)

    @server.tool()
    async def account_transactions_tool(
        ctx: Context,
        wallet_address: str,
        before: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        """Get transactions for a wallet address.

        Args:
            ctx: The MCP context containing shared resources
            wallet_address: The wallet address to fetch transactions for
            before: The signature of the latest transaction of previous page
            limit: Number of transactions to return (10, 20, 30, or 40)

        Returns:
            str: JSON string containing wallet transactions
        """
        solscan_ctx = ctx.request_context.lifespan_context
        result = await get_account_transactions(
            wallet_address=wallet_address,
            before=before,
            limit=limit,
            api_key=solscan_ctx.api_key,
        )
        return json.dumps(result, indent=2)

    return server


async def serve(
    api_key: str,
    transport: str = "sse",
    host: str = "127.0.0.1",
    port: int = 8050,
    log_level: str = "INFO",
) -> None:
    """Start the MCP server with the configured transport.

    Args:
        api_key: The Solscan API key
        transport: The transport protocol to use (sse or stdio)
        host: The host to bind to when using SSE transport
        port: The port to listen on when using SSE transport
        log_level: The logging level to use
    """
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    server = create_mcp_server(api_key, host, port)

    if transport == "sse":
        logger.info(f"Starting server with SSE transport on {host}:{port}")
        await server.run_sse_async()
    else:
        logger.info("Starting server with stdio transport")
        await server.run_stdio_async()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve(os.getenv("SOLSCAN_API_KEY", "")))
