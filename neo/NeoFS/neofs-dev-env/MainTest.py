"""
File Name: MainTest.py

Purpose: Quick test of SpoonOS NeoFS tools without cloning spoon-core.
"""
# =====================
# IMPORT LIBRARIES
# =====================
import os
import subprocess
from pathlib import Path
import functions


# =====================
# PATHS
# =====================
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_SH = BASE_DIR / "upload_transcript.sh"
GET_SH = BASE_DIR / "get_transcript.sh"


# =====================
# NEOFS ENV DEFAULTS
# =====================
os.environ.setdefault("NEOFS_ENDPOINT", "s01.neofs.devenv:8080")
os.environ.setdefault("NEOFS_WALLET", "./wallets/wallet.json")
os.environ.setdefault("NEOFS_CONTAINER_ID", "E3U1vNvbdfKBoSUtp47oZcCrspxMvTbnw2h1B9QjZFVK")

# 🔥 The key fix for your 127 error:
# Force the exact CLI binary you already confirmed exists.
os.environ.setdefault("NEOFS_CLI_PATH", "/usr/local/bin/neofs-cli")


if __name__ == "__main__":
    print("--------- MAIN PROCESS: RUNNING ---------")

    # 0) Propt user for a string input
    transcript_text = functions.prompt_user_text()

    # 1) Upload text using bash
    oid = functions.upload_text_and_capture_oid(UPLOAD_SH, transcript_text)
    print(f"✅ Parsed OID: {oid}")

    # 2) Retrieve and print the stored text
    returned_transcript_text = functions.get_text_interactive(GET_SH, oid)
    print(returned_transcript_text)

    print("\n--------- MAIN PROCESS: DONE ---------")


























































# import os
# import functions


# # =====================
# # DEFINE CONSTANTS
# # =====================

# # Your dev-env endpoint
# NEOFS_ENDPOINT = "s01.neofs.devenv:8080"

# # Your container ID
# NEOFS_CONTAINER_ID = "2xsGgxv9GMTFpbXwRDPaZrywzKzoe1he2W7PyptY7Ejk"

# # IMPORTANT:
# # Prefer keeping your WIF in an env var even if you don't want exports.
# # You can set it once inside VSCode's Run/Debug env settings,
# # or as a temporary local edit here.
# # NEOFS_WIF = os.getenv("NEOFS_WIF", "").strip()
# # If you really want to hardcode locally (DON'T COMMIT):
# NEOFS_WIF = "6PYP7YrwGnLuu4WYQbEe3WJiC44aKmqwqawLsp7H3oh5vocS9xTv2ZfTp3"


# def main():
#     print("----------- MAIN PROCESS: RUNNING -----------")

#     if not NEOFS_WIF:
#         raise RuntimeError(
#             "NEOFS_WIF is missing.\n"
#             "Set it in VSCode run environment or temporarily hardcode it in this file.\n"
#             "This function signs with WIF (-k), not wallet.key."
#         )

#     transcript_text = "Hello NeoFS! This is a quick MainTest upload using functions.py."

#     result = functions.upload_transcript_to_neofs_cli(
#         transcript=transcript_text,
#         container_id=NEOFS_CONTAINER_ID,
#         neofs_endpoint=NEOFS_ENDPOINT,
#         wif=NEOFS_WIF,
#         attributes={
#             "FileName": "transcript_quick_test.txt",
#             "Type": "Transcript",
#             "Source": "MainTest.py",
#         },
#         hash_plaintext=True,
#         verify_download=True,
#     )

#     print("✅ Upload complete.")
#     print("Receipt:")
#     print(result["receipt"])
#     print("\nUpload stdout:")
#     print(result.get("upload_stdout", ""))
#     print("\nUpload stderr:")
#     print(result.get("upload_stderr", ""))
#     print("\nVerify stdout:")
#     print(result.get("verify_stdout", ""))
#     print("\nVerify stderr:")
#     print(result.get("verify_stderr", ""))


# if __name__ == "__main__":
#     main()



























# import os
# import json
# import asyncio



# # ---- Hardcoded NeoFS config for quick local testing ----
# # Do NOT commit real keys to git.

# # REST/HTTP gateway base URL (your dev-env host mapping)
# os.environ["NEOFS_BASE_URL"] = "http://rest.neofs.devenv:8090"

# # Your Neo N3 address (owner)
# os.environ["NEOFS_OWNER_ADDRESS"] = "NbUgTSFvPmsRxmGeWpuuGeJUoRoi6PErcM"

# # Your PRIVATE KEY in WIF format
# os.environ["NEOFS_PRIVATE_KEY_WIF"] = "6PYP7YrwGnLuu4WYQbEe3WJiC44aKmqwqawLsp7H3oh5vocS9xTv2ZfTp3"

# # Your container
# os.environ["NEOFS_CONTAINER_ID"] = "2xsGgxv9GMTFpbXwRDPaZrywzKzoe1he2W7PyptY7Ejk"

# # Optional: ensure you aren't using an old bearer token for this quick test
# os.environ.pop("NEOFS_BEARER_TOKEN", None)














# async def test_spoon_neofs_upload():
#     # Import SpoonOS tool (from installed package)
#     from spoon_ai.tools.neofs_tools import UploadObjectTool

#     # ---- DEFAULTS YOU ALREADY PROVIDED ----
#     DEFAULT_CONTAINER_ID = "2xsGgxv9GMTFpbXwRDPaZrywzKzoe1he2W7PyptY7Ejk"

#     # Prefer env var if set, otherwise use default
#     container_id = os.getenv("NEOFS_CONTAINER_ID", DEFAULT_CONTAINER_ID).strip()

#     # Bearer token may be required if your container is private/eACL
#     # You said you likely don't need one for this container
#     bearer_token = os.getenv("NEOFS_BEARER_TOKEN")

#     # Example transcript payload
#     transcript_obj = {
#         "type": "transcript",
#         "session_id": "quick-test-001",
#         "text": "Hello NeoFS from SpoonOS tools!",
#     }

#     tool = UploadObjectTool()

#     result = await tool.execute(
#         container_id=container_id,
#         content=json.dumps(transcript_obj, ensure_ascii=False),
#         bearer_token=bearer_token,  # None is fine for public/permissive containers
#         attributes={
#             "FileName": "transcript_quick_test.json",
#             "Type": "Transcript",
#             "Source": "MainTest.py",
#         },
#         wallet_connect=False,
#     )

#     print(result)


# if __name__ == "__main__":
#     print("----------- MAIN PROCESS: RUNNING -----------")

#     try:
#         asyncio.run(test_spoon_neofs_upload())
#         print("✅ SpoonOS NeoFS upload test completed.")
#     except Exception as e:
#         print(f"❌ Test failed: {e}")
#         raise












