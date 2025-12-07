
from boa3.sc import runtime, storage
from boa3.sc.compiletime import NeoMetadata, public
from boa3.sc.contracts import ContractManagement
from boa3.sc.runtime import check_witness
from boa3.sc.types import UInt160
from boa3.sc.utils import CreateNewEvent
from boa3.sc.contracts import ContractManagement, GasToken as GAS_TOKEN, NeoToken as NEO_TOKEN
from boa3.sc.storage import try_get_uint160, try_get_list, put_list

# -------------------------------------------
# TOKEN SETTINGS
# -------------------------------------------

# The keys used to access the storage
#s
#ADMIN_KEY = UInt160(NfM2evxNufpuJndQX2SYh4m2x9s3Uqknfr)
SUPPLY_KEY = None
ADMIN_ADDRESS = None 

# -------------------------------------------
# Events
# -------------------------------------------

@public
def deploy(owner_key: UInt160, user_key: UInt160, amount: int, experiment_id: int, transcript_id: int) -> bool:

    #if owner_key != ADMIN_KEY:
    #    return False

    # list is formatted as such [[experiment_list], [transcrpit_id]]

    info = try_get_list(user_key)
    experiments = info[0]

    if experiment_id in experiments:
        return False

    GAS_TOKEN.transfer(owner_key, user_key, amount, None)  # 1 GAS = 100_000_000
    put_list(user_key, [experiment_id], [transcript_id])
    return True

def manifest() -> NeoMetadata:
    meta = NeoMetadata()

    meta.author = "COZ in partnership with Simpli"
    meta.email = "contact@coz.io"
    meta.description = 'This is a contract example'
    return meta