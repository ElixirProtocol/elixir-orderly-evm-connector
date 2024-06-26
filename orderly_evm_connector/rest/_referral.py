from orderly_evm_connector.lib.utils import check_required_parameters


def create_referral_code(self, account_id: str, referral_code: str, max_rebate_rate: float,
                         referrer_rebate_rate: float, referee_rebate_rate: float):
    """
    Create Referral Code

    Limit: 1 requests per 1 second

    POST /v1/referral/create

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/create-referral-code
    """
    check_required_parameters(
        [[account_id, "account_id"],
         [referral_code, "referral_code"],
         [max_rebate_rate, "max_rebate_rate"],
         [referrer_rebate_rate, "referrer_rebate_rate"],
         [referee_rebate_rate, "referee_rebate_rate"]]
    )
    payload = {
        "account_id": account_id,
        "referral_code": referral_code,
        "max_rebate_rate": max_rebate_rate,
        "referrer_rebate_rate": referrer_rebate_rate,
        "referee_rebate_rate": referee_rebate_rate
    }
    return self._sign_request("POST", "/v1/referral/create", payload=payload)


def update_referral_code(self, account_id: str, referral_code: str, max_rebate_rate: float,
                         referrer_rebate_rate: float, referee_rebate_rate: float):
    """
    Update Referral Code

    Limit: 1 requests per 1 second

    POST /v1/referral/ypdate

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/update-referral-code
    """
    check_required_parameters(
        [[account_id, "account_id"],
         [referral_code, "referral_code"],
         [max_rebate_rate, "max_rebate_rate"],
         [referrer_rebate_rate, "referrer_rebate_rate"],
         [referee_rebate_rate, "referee_rebate_rate"]]
    )
    payload = {
        "account_id": account_id,
        "referral_code": referral_code,
        "max_rebate_rate": max_rebate_rate,
        "referrer_rebate_rate": referrer_rebate_rate,
        "referee_rebate_rate": referee_rebate_rate
    }
    return self._sign_request("POST", "/v1/referral/update", payload=payload)


def bind_referral_code(self, referral_code: str):
    """
    Bind Referral Code

    Limit: 1 requests per 1 second

    POST /v1/referral/bind

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/bind-referral-code
    """
    check_required_parameters(
        [[referral_code, "referral_code"]]
    )
    payload = {
        "referral_code": referral_code
    }
    return self._sign_request("POST", "/v1/referral/bind", payload=payload)


def get_referral_code_info(self, page: int = None, size: int = None, user_address: str = None, account_id : str = None):
    """
    [Private]Get Referral Code Info
    
    Scope: Only each broker_id’s admin wallet can call this endpoint.


    Limit: 10 requests per 1 second

    GET /v1/referral/admin_info

    https://staging-docs.orderly.network/build-on-evm/evm-api/restful-api/private/get-referral-code-info
    """
    payload = {
        "page": page,
        "size": size,
    }
    return self._sign_request("GET", "/v1/referral/admin_info", payload=payload)


def get_referral_info(self):
    """
    Get Referral Info

    Limit: 10 requests per 1 second

    GET /v1/referral/info

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/get-referral-info
    """
    return self._sign_request("GET", "/v1/referral/info")


def get_referral_history(self, start_date: str = None, end_date: str = None, page: int = None, size: int = None):
    """
    Get Referral History

    Limit: 10 requests per 1 second

    GET /v1/referral/history

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/get-referral-history
    """
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "size": size,
    }
    return self._sign_request("GET", "/v1/referral/referral_history", payload=payload)


def get_referral_rebate_summary(self, start_date: str = None, end_date: str = None, page: int = None, size: int = None):
    """
    Get Referral Rebate Summary

    Limit: 10 requests per 1 second

    GET /v1/referral/rebate_summary

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/get-referral-rebate-summary
    """
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "size": size,
    }
    return self._sign_request("GET", "/v1/referral/rebate_summary", payload=payload)


def get_referee_history(self, start_date: str = None, end_date: str = None, page: int = None, size: int = None):
    """
    Get Referee History

    Limit: 10 requests per 1 second

    GET /v1/referral/referee_history

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/referee_history
    """
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "size": size,
    }
    return self._sign_request("GET", "/v1/referral/referee_history", payload=payload)


def get_referee_info(self, page: int = None, size: int = None):
    """
    Get Referee Info

    Limit: 10 requests per 1 second

    GET /v1/referral/referee_info

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/get-referee-info
    """
    payload = {
        "page": page,
        "size": size,
    }
    return self._sign_request("GET", "/v1/referral/referee_info", payload=payload)


def get_distribution_history(self, start_date: str = None, end_date: str = None, page: int = None, size: int = None):
    """
    Get Referral Info

    Limit: 1 requests per 1 second

    GET /v1/client/distribution_history

    https://docs.orderly.network/build-on-evm/evm-api/restful-api/private/get-distribution-history
    """
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "size": size,
    }
    return self._sign_request("GET", "/v1/client/distribution_history", payload=payload)
