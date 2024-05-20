import asyncio
import time

from examples.hsm_session import HsmSession
from examples.orderly_hsm import OrderlyHSMSession
from orderly_evm_connector.lib.utils import encode_key
from orderly_evm_connector.rest import Rest as Client
from utils.config import get_account_info
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

TESTNET_CHAIN_ID = 84532
CHAIN_ID = 8453

(
    hsm_pin,
    hsm_label,
    signer_address
) = get_account_info()

BROKER_ID = "elixir"
LIB_PATH = "/opt/cloudhsm/lib/libcloudhsm_pkcs11.so"
ROUTER_ADDRESS = "0x3b7fA734559d50867256B3d0aFDE749c2202b19D"

async def setup():
    await HsmSession.start_session(hsm_pin=hsm_pin, lib_path=LIB_PATH)

    hsm_instance = OrderlyHSMSession(
        hsm_pin=hsm_pin,
        address=signer_address,
        hsm_key_label=hsm_label,
        lib_path=LIB_PATH,
    )

    client_public = Client(
        orderly_testnet=True,
        hsm_instance=hsm_instance,
        debug=True
    )

    account_details = await client_public.get_account(ROUTER_ADDRESS, BROKER_ID)
    print(account_details)
    account_id = account_details["data"]["account_id"]
    print("account_id: ", account_id)

    orderly_priv_key = Ed25519PrivateKey.generate()
    orderly_secret = encode_key(orderly_priv_key.private_bytes_raw())
    orderly_key = encode_key(orderly_priv_key.public_key().public_bytes_raw())  
    timestamp = time.time_ns() // 1_000_000

    await client_public.delegate_add_orderly_key(
        ROUTER_ADDRESS,
        BROKER_ID,
        TESTNET_CHAIN_ID,
        orderly_key,
        "read,trading",
        timestamp,
        timestamp + 1_000 * 60 * 60 * 24 * 365,
        signer_address,
    )

    # Update the new credentials in the client instance.
    client_public.set_account_keys(account_id, orderly_secret, orderly_key)

    resp = await client_public.get_asset_history(token="USDC")
    print(resp)

    await client_public.close()

if __name__ == "__main__":
    asyncio.run(setup())
