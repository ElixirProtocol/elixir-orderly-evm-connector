import asyncio
import time
import argparse

from eth_keys.datatypes import PublicKey
from examples.hsm_session import HsmSession
from examples.orderly_hsm import OrderlyHSMSession
from orderly_evm_connector.lib.utils import encode_key, get_timestamp
from orderly_evm_connector.rest import Rest as Client
from utils.config import get_account_info
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from orderly_evm_connector.lib.constants import TESTNET_CHAIN_ID, CHAIN_ID

(
    hsm_pin,
    hsm_label,
    signer_address
) = get_account_info()

parser = argparse.ArgumentParser()
parser.add_argument('router_address', type=str, help='Router address')
parser.add_argument('tx_hash', type=str, help='Transaction hash to be processed')

args = parser.parse_args()

BROKER_ID = "woofi_pro"
LIB_PATH = "/opt/cloudhsm/lib/libcloudhsm_pkcs11.so"

async def setup(router_address, tx_hash):
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

    account_details = client_public.get_account(router_address, BROKER_ID)
    account_id = account_details["data"]["account_id"]
    print("account_id: ", account_id)

    orderly_priv_key = Ed25519PrivateKey.generate()
    orderly_secret = encode_key(orderly_priv_key.private_bytes_raw())
    orderly_key = encode_key(orderly_priv_key.public_key().public_bytes_raw())  

    timestamp = time.time_ns() // 1_000_000

    await client_public.delegate_add_orderly_key(
        router_address,
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

    nonce_response = client_public.get_registration_nonce()

    data = await client_public.delegate_signer(
        router_address,
        BROKER_ID,
        TESTNET_CHAIN_ID,
        int(nonce_response["data"]["registration_nonce"]),
        tx_hash,
        int(get_timestamp()),
        signer_address            
    )

    print(data)

if __name__ == "__main__":
    asyncio.run(setup(args.router_address, args.tx_hash))
