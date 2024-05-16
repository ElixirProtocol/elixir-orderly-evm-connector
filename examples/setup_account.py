import asyncio

from eth_keys.datatypes import PublicKey
from examples.hsm_session import HsmSession
from examples.orderly_hsm import OrderlyHSMSession
from orderly_evm_connector.rest import Rest as Client
from utils.config import get_account_info

TESTNET_CHAIN_ID = 84532
CHAIN_ID = 8453

(
    hsm_pin,
    hsm_label,
    signer_address
) = get_account_info()

BROKER_ID = "elixir"
LIB_PATH = "/opt/cloudhsm/lib/libcloudhsm_pkcs11.so"

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

    account_details = await client_public.get_account(signer_address, BROKER_ID)
    print(account_details)

    if not account_details["success"]:
        nonce_response = await client_public.get_registration_nonce()

        data = await client_public.register_account(
            BROKER_ID,
            TESTNET_CHAIN_ID,
            int(nonce_response["data"]["registration_nonce"]),
            signer_address
        )

        print(data)

if __name__ == "__main__":
    asyncio.run(setup())
