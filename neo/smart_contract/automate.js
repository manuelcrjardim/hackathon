const Neon = require("@cityofzion/neon-js");

// CONFIGURATION
const RPC_URL = "http://127.0.0.1:50012";
const CONTRACT_HASH = "0xdfcf33346dd7b8ef78940a9f856bf5efa1f853a3"; // <--- PASTE YOUR HASH
const WIF = "L1...";           // <--- See note below on how to get this WIF

// Setup the client
const rpcClient = new Neon.rpc.RPCClient(RPC_URL);
const account = new Neon.wallet.Account(WIF);

async function triggerContract() {
    console.log(`Agent ${account.address} is triggering contract...`);

    // 1. Build the Script (What method to call)
    const script = Neon.sc.createScript({
        scriptHash: CONTRACT_HASH,
        operation: "myMethodName",
        args: [
            Neon.sc.ContractParam.string("someArgument"),
            Neon.sc.ContractParam.integer(10)
        ]
    });

    // 2. Build and Sign Transaction
    // The 'invoke' method handles fetching current block data, gas calculation, and signing.
    try {
        const result = await Neon.api.doInvoke({
            api: new Neon.api.NeoRPCProvider({ url: RPC_URL }),
            account: account,
            script: script,
            gas: 0, // System fee is calculated automatically, this is extra priority fee
        });

        console.log("Transaction ID:", result.response.txid);
        console.log("Success!");
    } catch (e) {
        console.error("Error invoking contract:", e);
    }
}

triggerContract();