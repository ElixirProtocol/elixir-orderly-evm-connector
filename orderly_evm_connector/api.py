import json
from json import JSONDecodeError
from typing import Callable, Coroutine
from aiohttp import ClientResponse, ClientSession

from orderly_evm_connector.lib.hsm import HSMSigner
from .__version__ import __version__
from eth_utils.curried import keccak
from eth_utils.conversions import to_bytes
from eth_account.messages import encode_structured_data
from eth_account._utils.signing import to_eth_v, to_bytes32
from orderly_evm_connector.error import ClientError, ServerError
from orderly_evm_connector.lib.constants import CHAIN_ID, TESTNET_CHAIN_ID
from orderly_evm_connector.lib.utils import (
    generate_signature,
)
from orderly_evm_connector.lib.utils import cleanNoneValue
from orderly_evm_connector.lib.utils import orderlyLog, get_endpoints

class API(object):
    def __init__(
        self,
        orderly_key=None,
        orderly_secret=None,
        wallet_secret=None,
        orderly_testnet=False,
        hsm_instance: HSMSigner =None,
        orderly_account_id=None,
        proxies=None,
        timeout=None,
        debug=False
    ):
        self.orderly_key = orderly_key
        self.orderly_secret = orderly_secret
        self.wallet_secret = wallet_secret
        self.orderly_endpoint, _, _ = get_endpoints(orderly_testnet)
        self.orderly_account_id = orderly_account_id
        self.hsm_instance = hsm_instance
        self.timeout = timeout
        self.show_header = False
        self.proxies = proxies
        self.logger = orderlyLog(debug=debug)
        self.session = ClientSession()
        self.session.headers.update(
            {
                "Content-Type": "application/json;charset=utf-8",
                "User-Agent": "orderly-connector-python/" + __version__,
            }
        )
        return
    
    def set_account_keys(self, account_id, secret, key):
        """ Set Account Keys """
        self.orderly_account_id = account_id
        self.orderly_secret = secret
        self.orderly_key = key

    async def _request(self, http_method, url_path, payload=None):
        if payload:
            _payload = cleanNoneValue(payload)
            if _payload:
                if http_method == "GET" or http_method == "DELETE":
                    url_path += "?" + "&".join(
                        [f"{k}={v}" for k, v in _payload.items()]
                    )
                    payload = ""
                else:
                    payload = _payload

        if payload is None:
            payload = ""
        url = self.orderly_endpoint + url_path
        self.logger.debug("url: " + url)
        params = cleanNoneValue(
            {
                "url": url,
                "params": payload,
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )
        response: ClientResponse = await self._dispatch_request(http_method, params)
        self.logger.debug("raw response from server:" + await response.text())
        await self._handle_rest_exception(response)

        try:
            data = await response.json()
        except ValueError:
            data = await response.text()

        return data

    async def get_wallet_signature(self, message=None):
        _message = message
        encoded_message = encode_structured_data(_message)
        joined = b"\x19" + encoded_message.version + encoded_message.header + encoded_message.body
        message_hash = keccak(joined)
        raw_signature = await self.hsm_instance.sign(message_hash)
        _, _, vrs = self.hsm_instance.adjust_and_recover_signature(message_hash, raw_signature)
        processed_v = to_eth_v(vrs[0])
        return (to_bytes32(vrs[1]) + to_bytes32(vrs[2]) + to_bytes(processed_v)).hex()

    def _sign_request(self, http_method, url_path, payload=None):
        _payload = ""
        if payload:
            _payload = cleanNoneValue(payload)
            if _payload:
                if http_method == "GET" or http_method == "DELETE":
                    url_path += "?" + "&".join(
                        [f"{k}={v}" for k, v in _payload.items()]
                    )
                    _payload = ""
        params = {}
        payload = _payload if _payload else ""
        params["url_path"] = url_path
        params["payload"] = payload
        params["http_method"] = http_method
        query_string = self._prepare_params(params)
        try:
            _timestamp, _signature = generate_signature(
                self.orderly_secret, message=query_string
            )
        except ValueError:
            _timestamp, _signature = "mock_timestamp", "mock_signature"

        self.session.headers.update(
            {
                "orderly-timestamp": _timestamp,
                "orderly-account-id": self.orderly_account_id,
                "orderly-key": self.orderly_key,
                "orderly-signature": _signature,
            }
        )
        self.logger.debug(f"Sign Request Headers: {self.session.headers}")
        return self.send_request(http_method, url_path, payload)

    async def send_request(self, http_method, url_path, payload=None):
        if payload is None:
            payload = {}
        url = self.orderly_endpoint + url_path
        self.logger.debug("url: " + url)
        params = cleanNoneValue(
            {
                "url": url,
                "params": payload,
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )
        response: ClientResponse = await self._dispatch_request(http_method, params)
        self.logger.debug("raw response from server:" + await response.text())
        await self._handle_rest_exception(response)

        try:
            data = await response.json()
        except ValueError:
            data = await response.text()
        result = {}

        if self.show_header:
            result["header"] = response.headers

        if len(result) != 0:
            result["data"] = data
            return result
        return data

    def _prepare_params(self, params: dict):
        _http_method = params["http_method"]
        _url_path = params["url_path"]
        _payload = (
            json.dumps(params["payload"]) if params["payload"] else params["payload"]
        )
        _params = "{0}{1}{2}".format(_http_method, _url_path, _payload)
        return _params

    def _dispatch_request(self, http_method, params):
        method_func: Callable[..., Coroutine[ClientResponse]] = {
            "GET": self.session.get,
            "DELETE": self.session.delete,
            "PUT": self.session.put,
            "POST": self.session.post,
        }.get(http_method, "GET")
        if http_method == "POST" or http_method == "PUT":
            self.session.headers.update({"Content-Type": "application/json"})
            return method_func(url=params["url"], json=params["params"])
        else:
            self.session.headers.update(
                {
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                }
            )
            return method_func(url=params["url"])

    async def _handle_rest_exception(self, response: ClientResponse):
        status_code = response.status
        text_response = await response.text()
        if status_code <= 400:
            return
        if 400 < status_code < 500:
            try:
                err = json.loads(text_response)
            except JSONDecodeError:
                raise ClientError(
                    status_code, None, text_response, None, response.headers
                )
            error_data = None
            if "data" in err:
                error_data = err["data"]
            raise ClientError(
                status_code, err["code"], err["message"], response.headers, error_data
            )
        raise ServerError(status_code, text_response)

    async def close(self):
        await self.session.close()
