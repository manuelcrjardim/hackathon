import asyncio
from neo3.api.wrappers import ChainFacade, NeoToken, NEP17Contract
from neo3.network.payloads.verification import Signer
from neo3.core import types
from neo3.wallet import account, wallet

# ------------------------------------------------------------
# 1. HELPER FUNCTION
# ------------------------------------------------------------
def sign_with_account(account, password: str = None):
    async def sign(msg: bytes):
        return account.sign(msg, password)
    return sign

async def main():
    # --------------------------------------------------------
    # 2. CONFIGURATION
    # --------------------------------------------------------
    ADMIN_WALLET_PATH = '/home/manuel-jardim/Documents/wallets/Spoon-Agent.neo-wallet.json'
    HOST_ADDRESS = 'http://127.0.0.1:50012'

    admin_wallet = wallet.Wallet.from_file(ADMIN_WALLET_PATH)
    admin_account = admin_wallet.account_default
    print(f"Loaded Admin Account: {admin_account.address}")

    # Connect to the blockchain
    facade = ChainFacade(rpc_host=HOST_ADDRESS)
    
    # --------------------------------------------------------
    # 3. FIX: SWAP ARGUMENTS (Signer, Witness)
    # --------------------------------------------------------
    facade.add_signer(
        Signer(admin_account.script_hash),  # Arg 1: The Signer definition
        sign_with_account(admin_account)    # Arg 2: The Witness callback
    )

    # --------------------------------------------------------
    # 4. TEST CONNECTIVITY
    # --------------------------------------------------------
    print("\nAttempting to transfer 1 NEO to self (Connectivity Test)...")
    
    neo_token = NeoToken()
    
    # This invokes a real transaction on your local chain
    tx_hash = await facade.invoke(
        neo_token.transfer(admin_account.address, admin_account.address, 1)
    )
    
    print(f"Success! Transaction Hash: {tx_hash}")

if __name__ == "__main__":
    asyncio.run(main())