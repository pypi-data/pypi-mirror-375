"""Solscan API client functions."""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

SOLSCAN_API_BASE_URL = "https://pro-api.solscan.io/v2.0"
WSOL_ADDRESS = "So11111111111111111111111111111111111111112"

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
    TOKEN_SWAP = "ACTIVITY_TOKEN_SWAP"
    AGG_TOKEN_SWAP = "ACTIVITY_AGG_TOKEN_SWAP"
    TOKEN_ADD_LIQ = "ACTIVITY_TOKEN_ADD_LIQ"
    TOKEN_REMOVE_LIQ = "ACTIVITY_TOKEN_REMOVE_LIQ"
    SPL_TOKEN_STAKE = "ACTIVITY_SPL_TOKEN_STAKE"
    SPL_TOKEN_UNSTAKE = "ACTIVITY_SPL_TOKEN_UNSTAKE"
    TOKEN_DEPOSIT_VAULT = "ACTIVITY_TOKEN_DEPOSIT_VAULT"
    TOKEN_WITHDRAW_VAULT = "ACTIVITY_TOKEN_WITHDRAW_VAULT"
    SPL_INIT_MINT = "ACTIVITY_SPL_INIT_MINT"
    ORDERBOOK_ORDER_PLACE = "ACTIVITY_ORDERBOOK_ORDER_PLACE"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class BalanceFlow(str, Enum):
    IN = "in"
    OUT = "out"


async def make_request(
    endpoint: str, params: Dict[str, Any], api_key: str
) -> Dict[str, Any]:
    """Make a request to the Solscan API.

    Args:
        endpoint: API endpoint path
        params: Query parameters
        api_key: Solscan API key

    Returns:
        Dict containing the API response or error
    """
    url = f"{SOLSCAN_API_BASE_URL}{endpoint}"
    headers = {"token": api_key}

    logger.debug(f"Making request to: {url}")
    logger.debug(f"With params: {params}")
    logger.debug(f"Using API key: {api_key[:4]}...")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Error from Solscan API: {error_text}")
                return {"error": f"HTTP {response.status} - {error_text}"}

            return await response.json()


async def get_token_meta(token_address: str, api_key: str) -> Dict[str, Any]:
    """Get token metadata from Solscan API."""
    logger.info(f"Fetching metadata for token {token_address}")
    return await make_request("/token/meta", {"address": token_address}, api_key)


async def get_token_markets(
    token_address: str,
    sort_by: Optional[str] = None,
    program: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 10,
    api_key: str = "",
) -> Dict[str, Any]:
    """Get token market data and liquidity pools.

    Args:
        token_address: The token's address
        sort_by: Field to sort results by
        program: List of programs to filter by (max 5)
        page: Page number for pagination
        page_size: Number of results per page (10, 20, 30, 40, 60, or 100)
        api_key: Solscan API key
    """
    logger.info(f"Fetching market data for token {token_address}")

    # Validate page_size
    if page_size not in [10, 20, 30, 40, 60, 100]:
        logger.warning(f"Invalid page_size {page_size}, defaulting to 10")
        page_size = 10

    # Build params
    params: Dict[str, Any] = {
        "token": [token_address, WSOL_ADDRESS],
        "page": page,
        "page_size": page_size,
    }

    # Add optional params if provided
    if sort_by:
        params["sort_by"] = sort_by
    if program:
        if len(program) > 5:
            logger.warning("Program list exceeds maximum of 5, truncating")
            program = program[:5]
        params["program"] = program

    return await make_request("/token/markets", params, api_key)


async def get_token_holders(
    token_address: str,
    page: int = 1,
    page_size: int = 40,
    from_amount: Optional[str] = None,
    to_amount: Optional[str] = None,
    api_key: str = "",
) -> Dict[str, Any]:
    """Get token holder distribution.

    Args:
        token_address: The token's address
        page: Page number for pagination
        page_size: Number of results per page (10, 20, 30, or 40)
        from_amount: Minimum amount filter
        to_amount: Maximum amount filter
        api_key: Solscan API key
    """
    logger.info(f"Fetching holders for token {token_address}")

    # Validate page_size
    if page_size not in [10, 20, 30, 40]:
        logger.warning(f"Invalid page_size {page_size}, defaulting to 40")
        page_size = 40

    # Build params
    params: Dict[str, Any] = {
        "address": token_address,
        "page": page,
        "page_size": page_size,
    }

    # Add optional amount filters if provided
    if from_amount:
        params["from_amount"] = from_amount
    if to_amount:
        params["to_amount"] = to_amount

    return await make_request("/token/holders", params, api_key)


async def get_token_price(
    token_address: str,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    api_key: str = "",
) -> Dict[str, Any]:
    """Get historical token price data.

    Args:
        token_address: The token's address
        from_time: Start time in YYYYMMDD format
        to_time: End time in YYYYMMDD format
        api_key: Solscan API key
    """
    logger.info(f"Fetching price history for token {token_address}")

    # Build params
    params: Dict[str, Any] = {
        "address": token_address,
    }

    # Add optional time parameters
    if from_time is not None:
        params["from_time"] = from_time
    if to_time is not None:
        params["to_time"] = to_time

    return await make_request("/token/price", params, api_key)


async def get_token_accounts(
    wallet_address: str,
    type: str = "token",
    page: int = 1,
    page_size: int = 40,
    hide_zero: bool = True,
    api_key: str = "",
) -> Dict[str, Any]:
    """Get token holdings for a wallet.

    Args:
        wallet_address: The wallet address to get token accounts for
        type: Type of tokens to fetch ('token' or 'nft')
        page: Page number for pagination
        page_size: Number of results per page (10, 20, 30, or 40)
        hide_zero: Whether to hide zero balance accounts
        api_key: Solscan API key
    """
    logger.info(f"Fetching token accounts for wallet {wallet_address}")

    # Validate type
    if type not in ["token", "nft"]:
        logger.warning(f"Invalid type {type}, defaulting to 'token'")
        type = "token"

    # Validate page_size
    if page_size not in [10, 20, 30, 40]:
        logger.warning(f"Invalid page_size {page_size}, defaulting to 40")
        page_size = 40

    params = {
        "address": wallet_address,
        "type": type,
        "page": page,
        "page_size": page_size,
        "hide_zero": "true" if hide_zero else "false",
    }

    return await make_request("/account/token-accounts", params, api_key)


async def get_defi_activities(
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
    api_key: str = "",
) -> Dict[str, Any]:
    """Get DeFi activities for a wallet.

    Args:
        wallet_address: The wallet address
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
        api_key: Solscan API key
    """
    logger.info(f"Fetching DeFi activities for wallet {wallet_address}")

    # Validate page_size
    if page_size not in [10, 20, 30, 40, 60, 100]:
        logger.warning(f"Invalid page_size {page_size}, defaulting to 100")
        page_size = 100

    # Build base params
    params: Dict[str, Any] = {
        "address": wallet_address,
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order.value.lower(),
    }

    # Add optional filters
    if activity_type:
        params["activity_type"] = [t.value for t in activity_type]
    if from_address:
        params["from"] = from_address
    if platform:
        if len(platform) > 5:
            logger.warning("Platform list exceeds maximum of 5, truncating")
            platform = platform[:5]
        params["platform"] = platform
    if source:
        if len(source) > 5:
            logger.warning("Source list exceeds maximum of 5, truncating")
            source = source[:5]
        params["source"] = source
    if token:
        params["token"] = token
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time

    return await make_request("/account/defi/activities", params, api_key)


async def get_balance_change(
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
    api_key: str = "",
) -> Dict[str, Any]:
    """Get detailed balance change activities.

    Args:
        wallet_address: The wallet address
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
        api_key: Solscan API key
    """
    logger.info(f"Fetching balance changes for wallet {wallet_address}")

    # Validate page_size
    if page_size not in [10, 20, 30, 40, 60, 100]:
        logger.warning(f"Invalid page_size {page_size}, defaulting to 100")
        page_size = 100

    # Build base params
    params: Dict[str, Any] = {
        "address": wallet_address,
        "page": page,
        "page_size": page_size,
        "remove_spam": "true" if remove_spam else "false",
        "sort_by": sort_by,
        "sort_order": sort_order.value.lower(),
    }

    # Add optional filters
    if token_account:
        params["token_account"] = token_account
    if token:
        params["token"] = token
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if amount and len(amount) == 2:
        params["amount[]"] = amount
    if flow:
        params["flow"] = flow.value

    return await make_request("/account/balance_change", params, api_key)


async def get_transaction_detail(tx: str, api_key: str) -> Dict[str, Any]:
    """Get detailed transaction information including parsed data.

    Args:
        tx: Transaction signature
        api_key: Solscan API key
    """
    logger.info(f"Fetching transaction details for {tx}")
    return await make_request("/transaction/detail", {"tx": tx}, api_key)


async def get_transaction_actions(tx: str, api_key: str) -> Dict[str, Any]:
    """Get transaction actions from Solscan API."""
    logger.info(f"Fetching actions for transaction {tx}")
    return await make_request("/transaction/actions", {"tx": tx}, api_key)


async def get_account_transactions(
    wallet_address: str,
    before: Optional[str] = None,
    limit: int = 10,
    api_key: str = "",
) -> Dict[str, Any]:
    """Get transactions for a wallet address.

    Args:
        wallet_address: The wallet address to fetch transactions for
        before: The signature of the latest transaction of previous page (for pagination)
        limit: Number of transactions to return (10, 20, 30, or 40)
        api_key: Solscan API key
    """
    logger.info(f"Fetching transactions for wallet {wallet_address}")

    # Validate limit
    if limit not in [10, 20, 30, 40]:
        logger.warning(f"Invalid limit {limit}, defaulting to 10")
        limit = 10

    # Build params
    params: Dict[str, Any] = {
        "address": wallet_address,
        "limit": limit,
    }

    # Add optional before parameter if provided
    if before:
        params["before"] = before

    return await make_request("/account/transactions", params, api_key)
