import asyncio
import contextlib
import json
import time
import websockets
from websockets.exceptions import (
    ConnectionClosedError,
    ConnectionClosedOK,
    WebSocketException,
)
from orderly_evm_connector.lib.utils import orderlyLog, parse_proxies, decode_ws_error_code
from orderly_evm_connector.lib.constants import (
    WEBSOCKET_TIMEOUT_IN_SECONDS,
    WEBSOCKET_FAILED_MAX_RETRIES,
    WEBSOCKET_RETRY_SLEEP_TIME,
)

class AsyncWebsocketManager:
    def __init__(
        self,
        websocket_url,
        on_message=None,
        on_open=None,
        on_close=None,
        on_error=None,
        on_ping=None,
        on_pong=None,
        timeout=WEBSOCKET_TIMEOUT_IN_SECONDS,
        debug=False,
        proxies=None,
        max_retries=WEBSOCKET_FAILED_MAX_RETRIES,
    ):
        self.websocket_url = websocket_url
        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.init = False
        self.on_error = on_error
        self.on_ping = on_ping
        self.on_pong = on_pong
        self.timeout = timeout
        self.logger = orderlyLog(debug=debug)
        self._proxy_params = parse_proxies(proxies) if proxies else {}
        self.subscriptions = []
        self._login = False
        self.max_retries = max_retries
        self.ws = None
        self.loop = asyncio.get_event_loop()
        self._stopping = False
        self._read_task = None
        self._last_heartbeat = 0
        self._last_message_time = time.time()

    def start(self):
        pass

    async def create_ws_connection(self):
        retries = 0
        while retries <= self.max_retries:
            try:
                self._stopping = False

                self.logger.debug(
                    f"Creating connection with WebSocket Server: {self.websocket_url}, proxies: {self._proxy_params}"
                )
                self.ws = await websockets.connect(
                    self.websocket_url,
                    timeout=self.timeout,
                    close_timeout=5,
                    ping_interval=10,
                    ping_timeout=10,
                    **self._proxy_params
                )
                self.logger.debug(
                    f"WebSocket connection has been established: {self.websocket_url}, proxies: {self._proxy_params}"
                )

                # Reset connection state
                self.init = False
                self._last_message_time = time.time()

                if self.on_open:
                    self.on_open(self)
                return
            except Exception as e:
                self.logger.error(f"Failed to create WebSocket connection: {e}")
                retries += 1
                if retries <= self.max_retries:
                    self.logger.warning(
                        f"Retrying connection... (Attempt {retries}/{self.max_retries})"
                    )
                    # Exponential backoff with jitter
                    backoff_time = min(WEBSOCKET_RETRY_SLEEP_TIME * (2 ** (retries - 1)), 60)
                    await asyncio.sleep(backoff_time)
                else:
                    raise

    async def reconnect(self):
        self.logger.warning("Reconnecting to WebSocket...")
        await self.close()
        await self.create_ws_connection()

    def send_message(self, message):
        if not self.ws or self.ws.closed or self._stopping:
            self.logger.warning("Tried to send a msg on a closed/stopping WebSocket. Dropping: %s", message)
            return
        self.logger.debug("Sending message to Orderly WebSocket Server: %s", message)
        async def _safe_send():
            try:
                await self.ws.send(message)
            except Exception as e:
                self.logger.error("Failed to send message: %s; error: %s", message, e)
        asyncio.create_task(_safe_send())

    async def run(self):
        await self.create_ws_connection()

        # run read loop in a task so we can await it during close
        self._read_task = asyncio.create_task(self.read_data())

        try:
            await self._read_task
        except asyncio.CancelledError:
            self.logger.info("WebSocket tasks cancelled")
        except Exception as e:
            self.logger.error(f"Error in WebSocket run: {e}")

    async def ensure_init(self):
        while True:
            if self.init:
                break
            await asyncio.sleep(1)

    async def _handle_heartbeat(self):
        try:
            _payload = {"event": "pong"}
            await self.ws.send(json.dumps(_payload))
            self.logger.debug(f"Sent Ping frame: {_payload}")
            self._last_heartbeat = time.time()
        except Exception as e:
            self.logger.error("Failed to send Ping: {}".format(e))

    async def read_data(self):
        try:
            while not self._stopping:
                try:
                    message = await self.ws.recv()
                    self.init = True
                    self._last_message_time = time.time()
                    _message = json.loads(message)
                except json.JSONDecodeError:
                    err_code = decode_ws_error_code(message)
                    self.logger.warning(f"Websocket error code received: {err_code}")
                    continue

                if "event" in _message and _message["event"] == "ping":
                    await self._handle_heartbeat()
                else:
                    await self._callback(self.on_message, _message)
        except (ConnectionClosedOK, ConnectionClosedError) as e:
            # If we’re stopping, a close is expected. Don’t reconnect.
            if self._stopping:
                self.logger.info("WebSocket closed intentionally (code=%s).", getattr(e, "code", None))
                return
            # If it’s a normal 1000 from the peer, also don’t call it “abnormal”.
            if getattr(e, "code", None) == 1000:
                self.logger.info("WebSocket closed normally by peer.")
                # Still attempt to reconnect unless we're stopping
                if not self._stopping:
                    await self.reconnect()
                return
            self.logger.warning("WebSocket connection closed unexpectedly (code=%s). Reconnecting...",
                                getattr(e, "code", None))
            if not self._stopping:
                await self.reconnect()
        except WebSocketException as e:
            if self._stopping:
                self.logger.info("Stopping; not reconnecting after exception.")
                return
            self.logger.error(f"WebSocket exception: {e}")
            await self.reconnect()
        except Exception as e:
            if self._stopping:
                self.logger.info("Stopping; not reconnecting after exception.")
                return
            self.logger.error(f"Exception in read_data: {e}")
            await self.reconnect()

    async def close(self):
        self._stopping = True
        if self.ws and not self.ws.closed:
            try:
                # Initiate close and WAIT for peer's close frame
                await self.ws.close(code=1000, reason="")
            finally:
                if self._read_task and not self._read_task.done():
                    try:
                        await asyncio.wait_for(self._read_task, timeout=5)
                    except asyncio.TimeoutError:
                        self.logger.warning("Read task did not finish after close timeout; cancelling.")
                        self._read_task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await self._read_task

    async def _callback(self, callback, *args):
        if callback:
            try:
                await callback(self, *args)
            except Exception as e:
                self.logger.error("Error from callback {}: {}".format(callback, e))
                if self.on_error:
                    await self.on_error(self, e)
