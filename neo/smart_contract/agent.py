import asyncio
import sys

# UPDATED IMPORTS FOR NEO-MAMBA v2.x / v3.x
from neo3.wallet.wallet import Wallet  # <--- FIXED IMPORT
from neo3.core import types
from neo3.api import noderpc
from neo3.vm import ScriptBuilder
from neo3.network import payloads
from neo3.wallet.utils import address_to_script_hash

# --- CONFIGURATION ---
# Default local Neo-Express RPC port is often 50012, private nets often 20332
RPC_URL = "http://127.0.0.1:50012" 
WALLET_PATH = "/home/manuel-jardim/Documents/wallets/Spoon-Agent.neo-wallet.json"
WALLET_PASSWORD = ""
ADMIN_WALLET = address_to_script_hash('NXxMduvvfy9pmCSQtAirZX6Gge141Tqcfo')
USER_WALLET = address_to_script_hash('NXxMduvvfy9pmCSQtAirZX6Gge141Tqcfo')
PAYMENT_AMNT = 10000
CONTRACT_HASH = "0xdfcf33346dd7b8ef78940a9f856bf5efa1f853a3"  # Replace with your specific contract script hash
METHOD_NAME = "deploy" # The method you want to call
EXPERIMENT_ID = 1

# ---------------------


async def main():
    # 1. Setup the Client
    print(f"Connecting to {RPC_URL}...")
    client = noderpc.NeoRpcClient(RPC_URL)

    wallet = Wallet.from_file(WALLET_PATH)
    user_account = wallet.account_default
    print(f"Loaded wallet: {user_account.address}")

    contract_hash = types.UInt160.from_string(CONTRACT_HASH)

    args = [ADMIN_WALLET, USER_WALLET, PAYMENT_AMNT, EXPERIMENT_ID]

    sb = ScriptBuilder()
    # emit_contract_call(contract_hash, method, arguments)
    sb.emit_contract_call(contract_hash, METHOD_NAME, args) 
    contract = sb.to_array()

    # 4. Construct and Sign the Transaction
    print(f"Invoking method '{METHOD_NAME}' on {CONTRACT_HASH}...")
    
    try:
        # A. Create a transaction builder from the client
        # invoke_script returns a wrapper with the gas_consumed and script
        # We usually use `test_invoke` to get gas estimates first, or build directly if we are confident.
        
        # Proper flow in Mamba v2+:
        # 1. Get current block height for validUntilBlocks
        block_count = await client.get_block_count()
        
        print('so far its good')

        print(type(payloads.transaction))

        # 2. Create Transaction object
        tx = payloads.transaction.Transaction(
            version=0,
            nonce=123, # Random nonce, simplified for example
            system_fee=0,
            network_fee=0,
            valid_until_block=block_count + 5760,
            script=contract
        )

        print('so far its good')

        # 3. Estimate Gas (System Fee) using test invoke
        # This acts as a dry-run to see if it works and how much it costs
        invoke_result = await client.invoke_script(contract)
        
        if invoke_result.state != "HALT":
            print(f"Test invocation failed: {invoke_result.exception}")
            return

        # Apply calculated gas
        tx.system_fee = invoke_result.gas_consumed
        
        # 4. Calculate Network Fee (Signature cost)
        # This usually requires a helper or manual calculation based on witness size.
        # For simplicity in local dev, we can set a fixed fee or use a calculator helper if available.
        # A standard signature is roughly 0.003 GAS (300_000 fractions)
        tx.network_fee = 0 # 0.01 GAS (Safety margin)
        
        # 5. Sign the transaction
        # The wallet helps sign the transaction payload
        signer_witness = wallet.sign(tx)
        tx.witnesses.append(signer_witness)

        # 6. Broadcast
        # We send the raw transaction bytes
        tx_hash = await client.send_transaction(tx)
        
        print("Transaction sent successfully!")
        print(f"Tx Hash: {tx_hash.to_str()}")

    except Exception as e:
        print(f"Transaction failed: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())