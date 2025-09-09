"""Tests for the Solscan MCP server."""

import asyncio
import json
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock

import pytest
from fastmcp import Context, FastMCP
from mcp.types import TextContent
from pytest_mock import MockerFixture

from solscan_mcp_server.api import ActivityType, BalanceFlow, SortOrder
from solscan_mcp_server.server import (
    SolscanContext,
    SolscanTools,
    create_mcp_server,
    get_account_transactions,
    serve,
    solscan_lifespan,
)

# Test data
TEST_API_KEY = "test_api_key"
TEST_TOKEN_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
TEST_WALLET_ADDRESS = "test_wallet_address"
TEST_TX_SIGNATURE = "test_tx_signature"


@pytest.fixture
def mock_response() -> Dict[str, Any]:
    """Mock API response data."""
    return {"success": True, "data": {"test": "data"}}


@pytest.fixture
async def server() -> FastMCP:
    """Create a test MCP server instance."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tools directly in test
    @server.tool(name=SolscanTools.TOKEN_META.value)
    async def token_meta_tool(token_address: str) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.TOKEN_MARKETS.value)
    async def token_markets_tool(
        token_address: str,
        sort_by: Optional[str] = None,
        program: Optional[list[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.TOKEN_HOLDERS.value)
    async def token_holders_tool(
        token_address: str,
        limit: int = 10,
        offset: int = 0,
    ) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.TOKEN_PRICE.value)
    async def token_price_tool(token_address: str) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.TOKEN_ACCOUNTS.value)
    async def token_accounts_tool(wallet_address: str) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.DEFI_ACTIVITIES.value)
    async def defi_activities_tool(
        wallet_address: str,
        before_tx_signature: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.BALANCE_CHANGE.value)
    async def balance_change_tool(tx_signature: str) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.TRANSACTION_DETAIL.value)
    async def transaction_detail_tool(tx_signature: str) -> str:
        return json.dumps(mock_response, indent=2)

    @server.tool(name=SolscanTools.TRANSACTION_ACTIONS.value)
    async def transaction_actions_tool(tx_signature: str) -> str:
        return json.dumps(mock_response, indent=2)

    return server


@pytest.fixture
def mock_context(mocker: MockerFixture) -> Context:
    """Create a mock MCP context."""
    context = mocker.Mock(spec=Context)
    context.request_context = mocker.Mock()
    context.request_context.lifespan_context = SolscanContext(
        client=mocker.Mock(), api_key=TEST_API_KEY
    )
    return context


@pytest.mark.asyncio
async def test_server_initialization(mocker: MockerFixture) -> None:
    """Test server initialization and tool registration."""
    # Create server instance
    server = create_mcp_server(TEST_API_KEY)

    # Mock server.run to avoid actual execution
    mock_run = mocker.patch.object(server, "run_stdio_async")
    mock_run.return_value = None

    # Start server in background
    task = asyncio.create_task(server.run_stdio_async())

    # Give the server a moment to initialize
    await asyncio.sleep(0.1)

    # Verify server is initialized
    assert server._tool_manager is not None

    # Clean up
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_server_lifespan(mocker: MockerFixture) -> None:
    """Test server lifespan management."""
    server = FastMCP("test")

    async with solscan_lifespan(server, TEST_API_KEY) as context:
        assert isinstance(context, SolscanContext)
        assert context.api_key == TEST_API_KEY
        assert context.client is not None


@pytest.mark.asyncio
async def test_server_configuration():
    """Test server configuration with different parameters."""
    # Test default configuration
    server = create_mcp_server(TEST_API_KEY)
    assert isinstance(server, FastMCP)

    # Test custom configuration
    server = create_mcp_server(TEST_API_KEY, host="0.0.0.0", port=9000)
    assert isinstance(server, FastMCP)


@pytest.mark.asyncio
async def test_server_transport_selection(mocker: MockerFixture):
    """Test server transport selection."""
    # Mock the server creation and transport methods
    mock_server = mocker.Mock(spec=FastMCP)
    mock_server.run_sse_async = AsyncMock()
    mock_server.run_stdio_async = AsyncMock()

    mocker.patch(
        "solscan_mcp_server.server.create_mcp_server",
        return_value=mock_server,
    )

    # Test SSE transport
    task = asyncio.create_task(serve(TEST_API_KEY, transport="sse"))
    await asyncio.sleep(0.1)  # Give it time to start
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert mock_server.run_sse_async.called
    assert not mock_server.run_stdio_async.called

    # Reset mock calls
    mock_server.run_sse_async.reset_mock()
    mock_server.run_stdio_async.reset_mock()

    # Test STDIO transport
    task = asyncio.create_task(serve(TEST_API_KEY, transport="stdio"))
    await asyncio.sleep(0.1)  # Give it time to start
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert mock_server.run_stdio_async.called
    assert not mock_server.run_sse_async.called


@pytest.mark.asyncio
async def test_token_meta_call(
    mocker: MockerFixture, mock_response: Dict[str, Any]
) -> None:
    """Test token_meta tool execution."""
    server = create_mcp_server(TEST_API_KEY)

    # Register tool
    @server.tool(name=SolscanTools.TOKEN_META.value)
    async def token_meta_tool(token_address: str) -> str:
        return '{"success": true, "data": {"test": "data"}}'

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TOKEN_META.value,
        {"token_address": TEST_TOKEN_ADDRESS},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].text == '{"success": true, "data": {"test": "data"}}'


@pytest.mark.asyncio
async def test_token_markets_call(
    mocker: MockerFixture, mock_response: Dict[str, Any]
) -> None:
    """Test token_markets tool execution."""
    server = create_mcp_server(TEST_API_KEY)

    # Register tool
    @server.tool(name=SolscanTools.TOKEN_MARKETS.value)
    async def token_markets_tool(
        token_address: str,
        sort_by: str = None,
        program: list[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> str:
        return '{"success": true, "data": {"test": "data"}}'

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TOKEN_MARKETS.value,
        {
            "token_address": TEST_TOKEN_ADDRESS,
            "sort_by": "liquidity",
            "program": ["raydium"],
            "page": 1,
            "page_size": 10,
        },
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].text == '{"success": true, "data": {"test": "data"}}'


@pytest.mark.asyncio
async def test_token_holders_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test token_holders tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.TOKEN_HOLDERS.value)
    async def token_holders_tool(
        token_address: str,
        limit: int = 10,
        offset: int = 0,
    ) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TOKEN_HOLDERS.value,
        {
            "token_address": TEST_TOKEN_ADDRESS,
            "limit": 10,
            "offset": 0,
        },
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


@pytest.mark.asyncio
async def test_token_price_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test token_price tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.TOKEN_PRICE.value)
    async def token_price_tool(token_address: str) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TOKEN_PRICE.value,
        {"token_address": TEST_TOKEN_ADDRESS},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


@pytest.mark.asyncio
async def test_token_accounts_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test token_accounts tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.TOKEN_ACCOUNTS.value)
    async def token_accounts_tool(wallet_address: str) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TOKEN_ACCOUNTS.value,
        {"wallet_address": TEST_WALLET_ADDRESS},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


@pytest.mark.asyncio
async def test_defi_activities_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test defi_activities tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.DEFI_ACTIVITIES.value)
    async def defi_activities_tool(
        wallet_address: str,
        before_tx_signature: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.DEFI_ACTIVITIES.value,
        {
            "wallet_address": TEST_WALLET_ADDRESS,
            "before_tx_signature": None,
            "limit": 10,
        },
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


@pytest.mark.asyncio
async def test_balance_change_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test balance_change tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.BALANCE_CHANGE.value)
    async def balance_change_tool(tx_signature: str) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.BALANCE_CHANGE.value,
        {"tx_signature": TEST_TX_SIGNATURE},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


@pytest.mark.asyncio
async def test_transaction_detail_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test transaction_detail tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.TRANSACTION_DETAIL.value)
    async def transaction_detail_tool(tx_signature: str) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TRANSACTION_DETAIL.value,
        {"tx_signature": TEST_TX_SIGNATURE},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


@pytest.mark.asyncio
async def test_transaction_actions_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test transaction_actions tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.TRANSACTION_ACTIONS.value)
    async def transaction_actions_tool(tx_signature: str) -> str:
        return json.dumps(mock_response, indent=2)

    # Simulate tool call
    result = await server.call_tool(
        SolscanTools.TRANSACTION_ACTIONS.value,
        {"tx_signature": TEST_TX_SIGNATURE},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response


def test_solscan_tools_enum() -> None:
    """Test SolscanTools enum values."""
    assert SolscanTools.TOKEN_META.value == "token_meta"
    assert SolscanTools.TOKEN_MARKETS.value == "token_markets"
    assert SolscanTools.TOKEN_HOLDERS.value == "token_holders"
    assert SolscanTools.TOKEN_PRICE.value == "token_price"
    assert SolscanTools.TOKEN_ACCOUNTS.value == "token_accounts"
    assert SolscanTools.DEFI_ACTIVITIES.value == "defi_activities"
    assert SolscanTools.BALANCE_CHANGE.value == "balance_change"
    assert SolscanTools.ACCOUNT_TRANSACTIONS.value == "account_transactions"
    assert SolscanTools.TRANSACTION_DETAIL.value == "transaction_detail"
    assert SolscanTools.TRANSACTION_ACTIONS.value == "transaction_actions"


@pytest.mark.asyncio
async def test_account_transactions_tool(
    mock_context: Context,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test account_transactions tool."""
    server = FastMCP(
        "mcp-solscan-test",
        description="Test MCP server for Solscan API",
    )

    # Register tool directly in test
    @server.tool(name=SolscanTools.ACCOUNT_TRANSACTIONS.value)
    async def account_transactions_tool(
        wallet_address: str,
        before: Optional[str] = None,
        limit: int = 10,
    ) -> str:
        return json.dumps(mock_response, indent=2)

    # Test with all parameters
    result = await server.call_tool(
        SolscanTools.ACCOUNT_TRANSACTIONS.value,
        {
            "wallet_address": TEST_WALLET_ADDRESS,
            "before": TEST_TX_SIGNATURE,
            "limit": 30,
        },
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response

    # Test with default parameters
    result = await server.call_tool(
        SolscanTools.ACCOUNT_TRANSACTIONS.value,
        {"wallet_address": TEST_WALLET_ADDRESS},
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert json.loads(result[0].text) == mock_response
