from orderly_evm_connector.lib.utils import check_required_parameters
from orderly_evm_connector.lib.utils import check_enum_parameter
from orderly_evm_connector.lib.enums import VenueType, RebalanceStatus, MirrorXDelegationType


def venue_rebalance(
    self,
    from_venue: str,
    to_venue: str,
    amount: float,
    token: str,
):
    """[Private] Venue Rebalance

    This endpoint handles transfers between venues (orderly <-> ceffu).
    - Withdrawal to Ceffu: on-chain transfer, might take up to 20 mins
    - Deposit back to Orderly: on-chain transfer, might take up to 10 mins
    You don't need to select the chain, it will be selected automatically.

    POST /v1/venue_rebalance

    Args:
        from_venue (str): Source venue - "orderly" or "ceffu"
        to_venue (str): Destination venue - "orderly" or "ceffu"
        amount (float): Amount to transfer
        token (str): Token symbol (e.g., "USDC", "USDT", "ETH")

    https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/venue-rebalance
    """
    check_required_parameters([
        [from_venue, "from_venue"],
        [to_venue, "to_venue"],
        [amount, "amount"],
        [token, "token"]
    ])

    # Validate venue types
    valid_venues = ["orderly", "ceffu"]
    if from_venue.lower() not in valid_venues:
        raise ValueError(f"from_venue must be one of: {valid_venues}")
    if to_venue.lower() not in valid_venues:
        raise ValueError(f"to_venue must be one of: {valid_venues}")

    payload = {
        "from": from_venue.lower(),
        "to": to_venue.lower(),
        "amount": amount,
        "token": token
    }
    return self._sign_request("POST", "/v1/venue_rebalance", payload=payload)


def mirrorx_delegate(
    self,
    delegation_type: str,
    amount: float,
    token: str,
):
    """[Private] MirrorX Delegation

    This endpoint handles MirrorX delegation between Ceffu and Binance.
    This is an off-chain transfer and should be done immediately.

    POST /v1/ceffu/mirrorx_delegate

    Args:
        delegation_type (str): "DELEGATE" (fund is mirrored to binance) or "UNDELEGATE" (cancel the mirror)
        amount (float): Amount to delegate/undelegate
        token (str): Token symbol (e.g., "USDC", "USDT", "ETH")

    https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/mirrorx-delegate
    """
    check_required_parameters([
        [delegation_type, "delegation_type"],
        [amount, "amount"],
        [token, "token"]
    ])

    check_enum_parameter(delegation_type, MirrorXDelegationType)

    payload = {
        "type": delegation_type,
        "amount": amount,
        "token": token
    }
    return self._sign_request("POST", "/v1/ceffu/mirrorx_delegate", payload=payload)


def get_available_rebalance(self):
    """[Private] Get Available Rebalance

    Check available amount for rebalance.
    delegatable is the amount you can delegate or withdraw back to orderly dex.

    GET /v1/ceffu/available_rebalance

    Returns:
        dict: Response containing available rebalance amounts for each asset

    Response Example:
    {
        "success": true,
        "data": [
            {
                "asset": "USDC",
                "delegatable": 100000.25,
                "undelegatable": 50000.00
            },
            {
                "asset": "USDT",
                "delegatable": 10000.25,
                "undelegatable": 500.00
            },
            {
                "asset": "ETH",
                "delegatable": 0,
                "undelegatable": 0
            }
        ],
        "timestamp": 1711955766202
    }

    https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/available-rebalance
    """
    return self._sign_request("GET", "/v1/ceffu/available_rebalance")


def get_venue_rebalance_history(
    self,
    from_venue: str,
    to_venue: str,
    end_t: float = None,
    start_t: float = None,
    page: int = None,
    size: int = None,
    status: str = None,
    token: str = None,
):
    """[Private] Get Venue Rebalance History

    Check rebalance history between venues.

    GET /v1/venue_rebalance_history

    Args:
        from_venue (str): Source venue - "orderly" or "ceffu"
        to_venue (str): Destination venue - "orderly" or "ceffu"

    Optional Args:
        end_t (float): End time range (13-digit timestamp)
        start_t (float): Start time range (13-digit timestamp)
        page (int): Page number (default: 1)
        size (int): Page size (default: 25)
        status (str): Filter by status - "COMPLETED", "PENDING", "NEW", "FAILED"
        token (str): Filter by token symbol (return all if empty)

    Response Example:
    {
        "success": true,
        "data": {
            "meta": {
                "total": 9,
                "records_per_page": 25,
                "current_page": 1
            },
            "rows": [
                {
                    "from": "orderly",
                    "to": "ceffu",
                    "amount": 111,
                    "token": "USDC",
                    "tx_id": "0x4b0714c63cc7abae72bf68e84e25860b88ca651b7d27dad1e32bf4c027fa5326",
                    "status": "COMPLETED",
                    "created_time": 1688699193034,
                    "updated_time": 1688699193096
                }
            ]
        },
        "timestamp": 1711955766202
    }

    https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/venue-rebalance-history
    """
    check_required_parameters([
        [from_venue, "from_venue"],
        [to_venue, "to_venue"]
    ])

    # Validate venue types
    valid_venues = ["orderly", "ceffu"]
    if from_venue.lower() not in valid_venues:
        raise ValueError(f"from_venue must be one of: {valid_venues}")
    if to_venue.lower() not in valid_venues:
        raise ValueError(f"to_venue must be one of: {valid_venues}")

    if status:
        check_enum_parameter(status, RebalanceStatus)

    payload = {
        "from": from_venue.lower(),
        "to": to_venue.lower(),
        "end_t": end_t,
        "start_t": start_t,
        "page": page,
        "size": size,
        "status": status,
        "token": token
    }
    return self._sign_request("GET", "/v1/venue_rebalance_history", payload=payload)


def get_mirrorx_history(
    self,
    delegation_type: str,
    end_t: float = None,
    start_t: float = None,
    page: int = None,
    size: int = None,
    status: str = None,
    token: str = None,
):
    """[Private] Get MirrorX Delegation History

    Check delegation history for MirrorX operations.

    GET /v1/ceffu/mirrorx_history

    Args:
        delegation_type (str): "DELEGATE" (fund transferred to binance) or "UNDELEGATE" (fund transferred to ceffu)

    Optional Args:
        end_t (float): End time range (13-digit timestamp)
        start_t (float): Start time range (13-digit timestamp)
        page (int): Page number (default: 1)
        size (int): Page size (default: 25)
        status (str): Filter by status - "COMPLETED", "PENDING", "NEW", "FAILED"
        token (str): Filter by token symbol (return all if empty)

    Response Example:
    {
        "success": true,
        "data": {
            "meta": {
                "total": 9,
                "records_per_page": 25,
                "current_page": 1
            },
            "rows": [
                {
                    "type": "DELEGATE",
                    "token": "USDC",
                    "amount": 111,
                    "status": "COMPLETED",
                    "created_time": 1688699193034,
                    "updated_time": 1688699193096
                }
            ]
        },
        "timestamp": 1711955766202
    }

    https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/mirrorx-history
    """
    check_required_parameters([
        [delegation_type, "delegation_type"]
    ])

    check_enum_parameter(delegation_type, MirrorXDelegationType)

    if status:
        check_enum_parameter(status, RebalanceStatus)

    payload = {
        "type": delegation_type,
        "end_t": end_t,
        "start_t": start_t,
        "page": page,
        "size": size,
        "status": status,
        "token": token
    }
    return self._sign_request("GET", "/v1/ceffu/mirrorx_history", payload=payload)


def get_venue_balance(self):
    """[Private] Get Balances Across All Platforms

    Get balances across all platforms (Orderly, Binance, Ceffu).

    GET /v1/venue_balance

    Returns:
        dict: Response containing balances for all venues

    Response Example:
    {
        "success": true,
        "timestamp": 1711955766202,
        "data": {
            "orderly": [
                {
                    "asset": "USDC",
                    "amount": 123456789.0
                },
                {
                    "asset": "ETH",
                    "amount": 111.0
                }
            ],
            "binance": {
                "spot": [
                    {
                        "asset": "USDT",
                        "amount": 11111.0
                    },
                    {
                        "asset": "BTC",
                        "amount": 2222.0
                    }
                ],
                "futures": [
                    {
                        "asset": "USDT",
                        "amount": 11111.0
                    },
                    {
                        "asset": "BTC",
                        "amount": 2222.0
                    }
                ]
            },
            "ceffu": [
                {
                    "asset": "USDT",
                    "amount": 11111.0
                },
                {
                    "asset": "BTC",
                    "amount": 2222.0
                }
            ]
        }
    }

    https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/venue-balance
    """
    return self._sign_request("GET", "/v1/venue_balance")