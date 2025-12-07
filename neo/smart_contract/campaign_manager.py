
from boa3.sc import runtime, storage
from boa3.sc.compiletime import NeoMetadata, public
from boa3.sc.contracts import ContractManagement
from boa3.sc.runtime import check_witness
from boa3.sc.types import UInt160
from boa3.sc.utils import CreateNewEvent
from boa3.sc.contracts import ContractManagement, GasToken as GAS_TOKEN, NeoToken as NEO_TOKEN
# -------------------------------------------
# TOKEN SETTINGS
# -------------------------------------------

# The keys used to access the storage
OWNER_KEY = None
SUPPLY_KEY = None
USER_KEY = None
ADMIN_ADDRESS = None 

TOKEN_TOTAL_SUPPLY = None

# -------------------------------------------
# Events
# -------------------------------------------

on_transfer = CreateNewEvent(
    [
        ('from_addr', UInt160 | None),
        ('to_addr', UInt160 | None),
        ('amount', int)
    ],
    'Transfer'
)

def get_owner() -> UInt160:
    """
    Gets the script hash of the owner (the account that deployed this smart contract)
    """
    return storage.get_uint160(OWNER_KEY)

# -------------------------------------------
# Logic
# -------------------------------------------

if get_owner() != OWNER_KEY:
    quit()

if USER_KEY in storage:
    quit()

GAS_TOKEN.transfer(get_owner(), USER_KEY, 100_000_000, None)  # 1 GAS = 100_000_000

def validate_user(address: UInt160) -> bool:
    context = storage.get_context()


@public
def _deploy(data: Any, update: bool):
    """
    Initializes the storage when the smart contract is deployed.

    :return: whether the deploy was successful. This method must return True only during the smart contract's deploy.
    """
    if not update:
        container = runtime.script_container
        owner = container.sender
        storage.put_uint160(TOKEN_OWNER_KEY, owner)

        storage.put_int(TOKEN_TOTAL_SUPPLY_PREFIX, TOKEN_INITIAL_SUPPLY)
        storage.put_int(owner, TOKEN_INITIAL_SUPPLY)

        on_transfer(None, owner, TOKEN_INITIAL_SUPPLY)

@public
def transfer(from_address: UInt160, to_address: UInt160, amount: int, data: Any) -> bool:
    """
    Transfers a specified amount of NEP17 tokens from one account to another

    If the method succeeds, it must fire the `transfer` event and must return true, even if the amount is 0,
    or from and to are the same address.

    :param from_address: the address to transfer from
    :type from_address: UInt160
    :param to_address: the address to transfer to
    :type to_address: UInt160
    :param amount: the amount of NEP17 tokens to transfer
    :type amount: int
    :param data: whatever data is pertinent to the onPayment method
    :type data: Any

    :return: whether the transfer was successful
    :raise AssertionError: raised if `from_address` or `to_address` length is not 20 or if `amount` if less than zero.
    """
    # the parameters from and to should be 20-byte addresses. If not, this method should throw an exception.
    assert len(from_address) == 20 and len(to_address) == 20
    # the parameter amount must be greater than or equal to 0. If not, this method should throw an exception.
    assert amount >= 0

    # The function MUST return false if the from account balance does not have enough tokens to spend.
    from_balance = storage.get_int(from_address)
    if from_balance < amount:
        return False

    # The function should check whether the from address equals the caller contract hash.
    # If so, the transfer should be processed;
    # If not, the function should use the check_witness to verify the transfer.
    if from_address != runtime.calling_script_hash:
        if not runtime.check_witness(from_address):
            return False

    # skip balance changes if transferring to yourself or transferring 0 cryptocurrency
    if from_address != to_address and amount != 0:
        if from_balance == amount:
            storage.delete(from_address)
        else:
            storage.put_int(from_address, from_balance - amount)

        to_balance = storage.get_int(to_address)
        storage.put_int(to_address, to_balance + amount)

    # if the method succeeds, it must fire the transfer event
    on_transfer(from_address, to_address, amount)
    # if the to_address is a smart contract, it must call the contracts onPayment
    # post_transfer(from_address, to_address, amount, data)
    # and then it must return true
    return True
