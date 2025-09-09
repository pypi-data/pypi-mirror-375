"""Tests for the Solscan API client functions."""

from typing import Any, Dict

import pytest
from aiohttp import ClientSession
from pytest_mock import MockerFixture

from solscan_mcp_server.api import (
    WSOL_ADDRESS,
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

# Test data
TEST_API_KEY = "test_api_key"
TEST_TOKEN_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
TEST_WALLET_ADDRESS = "test_wallet_address"
TEST_TX_SIGNATURE = "test_tx_signature"


@pytest.fixture
def mock_session(mocker: MockerFixture) -> ClientSession:
    """Create a mock aiohttp ClientSession."""
    return mocker.Mock(spec=ClientSession)


@pytest.fixture
def mock_response() -> Dict[str, Any]:
    """Mock API response data."""
    return {"success": True, "data": {"test": "data"}}


@pytest.fixture
def mock_error_response() -> Dict[str, Any]:
    """Mock API error response data."""
    return {"error": "Test error message"}


@pytest.mark.asyncio
async def test_get_token_meta(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_token_meta function."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    result = await get_token_meta(TEST_TOKEN_ADDRESS, TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/meta",
        {"address": TEST_TOKEN_ADDRESS},
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_token_markets(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_token_markets function with various parameters."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with all parameters
    result = await get_token_markets(
        token_address=TEST_TOKEN_ADDRESS,
        sort_by="liquidity",
        program=["raydium"],
        page=1,
        page_size=10,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/markets",
        {
            "token": [TEST_TOKEN_ADDRESS, WSOL_ADDRESS],
            "sort_by": "liquidity",
            "program": ["raydium"],
            "page": 1,
            "page_size": 10,
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_token_markets(
        token_address=TEST_TOKEN_ADDRESS,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/markets",
        {
            "token": [TEST_TOKEN_ADDRESS, WSOL_ADDRESS],
            "page": 1,
            "page_size": 10,
        },
        TEST_API_KEY,
    )

    # Test with program list exceeding max length
    mock_make_request.reset_mock()
    result = await get_token_markets(
        token_address=TEST_TOKEN_ADDRESS,
        program=["prog1", "prog2", "prog3", "prog4", "prog5", "prog6"],
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/markets",
        {
            "token": [TEST_TOKEN_ADDRESS, WSOL_ADDRESS],
            "program": ["prog1", "prog2", "prog3", "prog4", "prog5"],
            "page": 1,
            "page_size": 10,
        },
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_token_holders(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_token_holders function with pagination."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with all parameters
    result = await get_token_holders(
        token_address=TEST_TOKEN_ADDRESS,
        page=2,
        page_size=30,
        from_amount="100",
        to_amount="1000",
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/holders",
        {
            "address": TEST_TOKEN_ADDRESS,
            "page": 2,
            "page_size": 30,
            "from_amount": "100",
            "to_amount": "1000",
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_token_holders(TEST_TOKEN_ADDRESS, api_key=TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/holders",
        {
            "address": TEST_TOKEN_ADDRESS,
            "page": 1,
            "page_size": 40,
        },
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_token_price(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_token_price function with time range."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with time range
    result = await get_token_price(
        token_address=TEST_TOKEN_ADDRESS,
        from_time=20240101,
        to_time=20240131,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/price",
        {
            "address": TEST_TOKEN_ADDRESS,
            "from_time": 20240101,
            "to_time": 20240131,
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_token_price(TEST_TOKEN_ADDRESS, api_key=TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/token/price",
        {"address": TEST_TOKEN_ADDRESS},
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_token_accounts(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_token_accounts function with all parameters."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with all parameters
    result = await get_token_accounts(
        wallet_address=TEST_WALLET_ADDRESS,
        type="nft",
        page=2,
        page_size=30,
        hide_zero=False,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/token-accounts",
        {
            "address": TEST_WALLET_ADDRESS,
            "type": "nft",
            "page": 2,
            "page_size": 30,
            "hide_zero": "false",
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_token_accounts(TEST_WALLET_ADDRESS, api_key=TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/token-accounts",
        {
            "address": TEST_WALLET_ADDRESS,
            "type": "token",
            "page": 1,
            "page_size": 40,
            "hide_zero": "true",
        },
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_defi_activities(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_defi_activities function with all parameters."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with all parameters
    result = await get_defi_activities(
        wallet_address=TEST_WALLET_ADDRESS,
        activity_type=[ActivityType.TOKEN_SWAP, ActivityType.TOKEN_ADD_LIQ],
        from_address="test_from",
        platform=["raydium", "orca"],
        source=["source1", "source2"],
        token=TEST_TOKEN_ADDRESS,
        from_time=20240101,
        to_time=20240131,
        page=2,
        page_size=60,
        sort_by="block_time",
        sort_order=SortOrder.ASC,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/defi/activities",
        {
            "address": TEST_WALLET_ADDRESS,
            "activity_type": ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_TOKEN_ADD_LIQ"],
            "from": "test_from",
            "platform": ["raydium", "orca"],
            "source": ["source1", "source2"],
            "token": TEST_TOKEN_ADDRESS,
            "from_time": 20240101,
            "to_time": 20240131,
            "page": 2,
            "page_size": 60,
            "sort_by": "block_time",
            "sort_order": "asc",
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_defi_activities(TEST_WALLET_ADDRESS, api_key=TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/defi/activities",
        {
            "address": TEST_WALLET_ADDRESS,
            "page": 1,
            "page_size": 100,
            "sort_by": "block_time",
            "sort_order": "desc",
        },
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_balance_change(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_balance_change function with all parameters."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with all parameters
    result = await get_balance_change(
        wallet_address=TEST_WALLET_ADDRESS,
        token_account="test_token_account",
        token=TEST_TOKEN_ADDRESS,
        from_time=20240101,
        to_time=20240131,
        page_size=60,
        page=2,
        remove_spam=False,
        amount=[100.0, 1000.0],
        flow=BalanceFlow.IN,
        sort_by="block_time",
        sort_order=SortOrder.ASC,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/balance_change",
        {
            "address": TEST_WALLET_ADDRESS,
            "token_account": "test_token_account",
            "token": TEST_TOKEN_ADDRESS,
            "from_time": 20240101,
            "to_time": 20240131,
            "page": 2,
            "page_size": 60,
            "remove_spam": "false",
            "amount[]": [100.0, 1000.0],
            "flow": "in",
            "sort_by": "block_time",
            "sort_order": "asc",
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_balance_change(TEST_WALLET_ADDRESS, api_key=TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/balance_change",
        {
            "address": TEST_WALLET_ADDRESS,
            "page": 1,
            "page_size": 100,
            "remove_spam": "true",
            "sort_by": "block_time",
            "sort_order": "desc",
        },
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_transaction_detail(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_transaction_detail function."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    result = await get_transaction_detail(TEST_TX_SIGNATURE, TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/transaction/detail",
        {"tx": TEST_TX_SIGNATURE},
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_transaction_actions(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_transaction_actions function."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    result = await get_transaction_actions(TEST_TX_SIGNATURE, TEST_API_KEY)

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/transaction/actions",
        {"tx": TEST_TX_SIGNATURE},
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_get_account_transactions(
    mock_session: ClientSession,
    mock_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test get_account_transactions function with pagination."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_response

    # Test with all parameters
    result = await get_account_transactions(
        wallet_address=TEST_WALLET_ADDRESS,
        before="test_tx_signature",
        limit=30,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/transactions",
        {
            "address": TEST_WALLET_ADDRESS,
            "before": "test_tx_signature",
            "limit": 30,
        },
        TEST_API_KEY,
    )

    # Test with default parameters
    mock_make_request.reset_mock()
    result = await get_account_transactions(
        wallet_address=TEST_WALLET_ADDRESS,
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/transactions",
        {
            "address": TEST_WALLET_ADDRESS,
            "limit": 10,
        },
        TEST_API_KEY,
    )

    # Test with invalid limit
    mock_make_request.reset_mock()
    result = await get_account_transactions(
        wallet_address=TEST_WALLET_ADDRESS,
        limit=50,  # Invalid limit
        api_key=TEST_API_KEY,
    )

    assert result == mock_response
    mock_make_request.assert_called_once_with(
        "/account/transactions",
        {
            "address": TEST_WALLET_ADDRESS,
            "limit": 10,  # Should default to 10
        },
        TEST_API_KEY,
    )


@pytest.mark.asyncio
async def test_api_error_handling(
    mock_session: ClientSession,
    mock_error_response: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """Test API error handling."""
    mock_make_request = mocker.patch("solscan_mcp_server.api.make_request")
    mock_make_request.return_value = mock_error_response

    # Test error handling for each API function
    result = await get_token_meta(TEST_TOKEN_ADDRESS, TEST_API_KEY)
    assert result == mock_error_response

    result = await get_token_markets(TEST_TOKEN_ADDRESS, api_key=TEST_API_KEY)
    assert result == mock_error_response

    result = await get_token_holders(TEST_TOKEN_ADDRESS, api_key=TEST_API_KEY)
    assert result == mock_error_response

    result = await get_token_price(TEST_TOKEN_ADDRESS, api_key=TEST_API_KEY)
    assert result == mock_error_response

    result = await get_token_accounts(TEST_WALLET_ADDRESS, api_key=TEST_API_KEY)
    assert result == mock_error_response

    result = await get_defi_activities(TEST_WALLET_ADDRESS, api_key=TEST_API_KEY)
    assert result == mock_error_response

    result = await get_balance_change(TEST_WALLET_ADDRESS, api_key=TEST_API_KEY)
    assert result == mock_error_response

    result = await get_transaction_detail(TEST_TX_SIGNATURE, TEST_API_KEY)
    assert result == mock_error_response

    result = await get_transaction_actions(TEST_TX_SIGNATURE, TEST_API_KEY)
    assert result == mock_error_response
