import asyncio
from neo3.api.wrappers import ChainFacade, NeoToken, NEP17Contract
from neo3.api.helpers.signing import sign_with_account
from neo3.network.payloads.verification import Signer
from neo3.core import types
from neo3.wallet import account, wallet

async def main():
    # This example shows how to transfer NEP-17 tokens for a contract that does not
    # have a dedicated wrapper like Neo and Gas have.
    # Most of the setup is the same as the first example
    ADMIN_WALLET_APTH = '/home/manuel-jardim/Documents/wallets/Spoon-Agent.neo-wallet.json'
    host_adress = 'HTTP://127.0.0.1:50012'

    admin_wallet = wallet.Wallet.from_file(ADMIN_WALLET_APTH)
    admin_account = admin_wallet.account_default

    # This is your interface for talking to the blockchain
    facade = ChainFacade(rpc_host=host_adress)
    facade.add_signer(
        sign_with_account(admin_account),
        Signer(admin_account.script_hash),  # default scope is te/CALLED_BY_ENTRY
    )

    source = admin_account.address
    destination = "NUVaphUShQPD82yoXcbvFkedjHX6rUF7QQ"

    # Use the generic NEP17 class to wrap the token and create a similar interface as before
    # The contract hash is that of our sample Nep17 token which is deployed in our neoxpress setup
    contract_hash = types.UInt160.from_string(
        "0xc640d9b6a7e402a094bda255fa54d551fd010f15"
    )
    token = NEP17Contract(contract_hash)
    # Now call it in the same fashion as before with the NEoToken
    print("Calling transfer and waiting for receipt...")
    print(await facade.invoke(token.transfer(source, destination, 10)))


if __name__ == "__main__":
    asyncio.run(main())