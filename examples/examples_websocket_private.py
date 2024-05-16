from utils.config import get_account_info
import time, logging
from orderly_evm_connector.websocket.websocket_api import WebsocketPrivateAPIClient

def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    logging.info(message)


wss_client = WebsocketPrivateAPIClient(
    orderly_testnet=True,
    orderly_account_id="0x5d06bf449b1a3cee4a06b27d4ef7301756780b549e4ca67adde9ac93482f429e",
    orderly_key="ed25519:5DhWbdkRypKB1UFmZPvvzkVGVCSQXzb8Bp1DXdBoVLKU",
    orderly_secret="ed25519:8QjtGyGd6jVNZcX6KnWYty7sUucouiqHjQNtnA9ff6TD",
    on_message=message_handler,
    on_close=on_close,
    debug=True
)

wss_client.get_account()
wss_client.get_balance()
wss_client.get_position()
# wss_client.get_account_liquidations()
# wss_client.get_liquidator_liquidations()
wss_client.get_wallet_transactions()
# wss_client.get_pnl_settlement()
wss_client.get_notifications()
wss_client.get_execution_report()
# wss_client.get_algo_execution_report()
# wss_client.get_execution_report_for_single_broker()
time.sleep(10000)

logging.info("closing ws connection")
wss_client.stop()
