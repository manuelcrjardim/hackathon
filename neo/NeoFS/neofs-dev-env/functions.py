"""
File Name: functions.py

Purpose: Holds all functions for developer B, who is responsible for storing a transcript in the Neo blockchain and
         verifying the transaction.
"""


# =====================
# LIBRARY IMPORTS
# =====================
import hashlib
import tempfile
import subprocess
from typing import Optional, Dict, Any
import os
import re
from pathlib import Path


# =====================
# DEFINE CONSTANTS
# =====================


# =====================
# FUNCTIONS/METHODS
# =====================
def upload_transcript_to_neofs_cli(
    transcript: str,
    container_id: str,
    neofs_endpoint: str,
    wif: str,
    *,
    attributes: Optional[Dict[str, str]] = None,
    hash_plaintext: bool = True,
    verify_download: bool = True,
) -> Dict[str, Any]:
    """
    Purpose:
        Upload a transcript string to NeoFS using neofs-cli. This function serializes `transcript` to a file-like payload (typically JSON),
        uploads it to the specified NeoFS container, and optionally computes a hash
        for on-chain receipt verification.

    Args:
        transcript: The transcript text to upload.
        container_id: Target NeoFS container ID.
        neofs_endpoint: NeoFS node endpoint used by the CLI.
        wif: Wallet private key in WIF format for signing.
        filename: Logical filename to associate with the uploaded object.
        attributes: Optional NeoFS object attributes (key-value metadata).
        hash_plaintext: If True, compute and return a hash of the plaintext
            transcript for use as an on-chain receipt.

    Returns:
        A dictionary with:
            - object_id: The created NeoFS object ID (or None on failure).
            - stdout: Raw stdout from the CLI invocation.
            - stderr: Raw stderr from the CLI invocation.
            - transcript_hash: Hash of the plaintext transcript if enabled.

    Security:
        Avoid hardcoding or logging WIF. Prefer passing WIF via environment
        variables or a secure secret manager.
    """

    # -------------------------------------------------------------------------
    # 0) Basic input validation.
    #    Fail early with clear errors instead of mysterious CLI failures later.
    # -------------------------------------------------------------------------
    if not transcript or not isinstance(transcript, str):
        raise ValueError("transcript must be a non-empty string")
    if not container_id:
        raise ValueError("container_id is required")
    if not neofs_endpoint:
        raise ValueError("neofs_endpoint is required")
    if not wif:
        raise ValueError("wif is required (use an env var)")
    
    # -------------------------------------------------------------------------
    # 1) Compute transcript hash (optional).
    #    This is the "proof-of-integrity" you will put into Neo N3.
    #    You are hashing PLAINTEXT here because the scientist may want
    #    to verify that the decrypted transcript matches the on-chain hash later.
    # -------------------------------------------------------------------------
    transcript_hash = None
    if hash_plaintext:
        # Encode to bytes using UTF-8, then hash with SHA-256, then hex string.
        transcript_hash = hashlib.sha256(transcript.encode("utf-8")).hexdigest()

    # -------------------------------------------------------------------------
    # 2) Write transcript to a temporary file.
    #    The CLI expects a file path for `object put`.
    #    delete=False is needed because the CLI is a separate process that
    #    must be able to read the file after this `with` block ends.
    # -------------------------------------------------------------------------
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(transcript)   # Write the transcript into the temp file.
        tmp_path = tmp.name     # Record the saved file path.

    # -------------------------------------------------------------------------
    # 3) Build the NeoFS upload command.
    #    - "neofs-cli"         : the CLI executable
    #    - "-r endpoint"       : RPC / NeoFS network endpoint
    #    - "-k wif"            : wallet key used to sign the operation
    #    - "object put"        : upload an object
    #    - "--file tmp_path"   : the file to upload
    #    - "--cid container_id": target container
    # -------------------------------------------------------------------------
    cmd = [
        "/home/bin/neofs-cli",
        "-r", neofs_endpoint,
        "-k", wif,
        "object", "put",
        "--file", tmp_path,
        "--cid", container_id,
    ]

    # -------------------------------------------------------------------------
    # 4) Add optional attributes (metadata).
    #    Some CLI versions accept repeated "--attr key=value".
    #    If your CLI errors here, remove attributes.
    # -------------------------------------------------------------------------
    # if attributes:
    #     for k, v in attributes.items():
    #         cmd.extend(["--attr", f"{k}={v}"])

    # -------------------------------------------------------------------------
    # 5) Execute upload.
    #    capture_output=True collects stdout/stderr so we can:
    #      - parse the object ID
    #      - return helpful diagnostics if something fails
    # -------------------------------------------------------------------------
    proc = subprocess.run(cmd, capture_output=True, text=True)

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    # -------------------------------------------------------------------------
    # 6) Check OS-level success first.
    #    A non-zero return code almost always means the upload failed.
    # -------------------------------------------------------------------------
    if proc.returncode != 0:
        raise RuntimeError(
            "NeoFS upload failed (non-zero return code).\n"
            f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        )

    # -------------------------------------------------------------------------
    # 7) Parse object ID from CLI output.
    #    Different versions print slightly different formats.
    #    We search line-by-line for something that looks like:
    #      "Object ID: <id>"
    # -------------------------------------------------------------------------
    object_id = None
    for line in stdout.splitlines():
        if "Object ID" in line:
            object_id = line.split(":", 1)[-1].strip()
            break

    # If we couldn't find the object_id, treat as a failure for your use case,
    # because you need this ID as part of your on-chain receipt.
    if not object_id:
        raise RuntimeError(
            "NeoFS upload may have succeeded, but object_id was not found in output.\n"
            f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        )
    
    # -------------------------------------------------------------------------
    # 8) Optional verification step (strongly recommended).
    #    We try to download the object into a temp file.
    #    If this fails, we assume the upload isn't reliably retrievable,
    #    and we abort so you don't store a bad receipt on Neo N3.
    # -------------------------------------------------------------------------
    verify_stdout = ""
    verify_stderr = ""

    if verify_download:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".verify.txt",
            delete=False,
            encoding="utf-8",
        ) as verify_tmp:
            verify_path = verify_tmp.name

        # `object get` is the most universal verification approach:
        # if the CLI can fetch it back, it exists and is addressable.
        verify_cmd = [
            "neofs-cli",
            "-r", neofs_endpoint,
            "-k", wif,
            "object", "get",
            "--cid", container_id,
            "--oid", object_id,
            "--out", verify_path,
        ]

        verify_proc = subprocess.run(verify_cmd, capture_output=True, text=True)
        verify_stdout = (verify_proc.stdout or "").strip()
        verify_stderr = (verify_proc.stderr or "").strip()

        if verify_proc.returncode != 0:
            raise RuntimeError(
                "NeoFS verification download failed.\n"
                "Upload returned an object_id but retrieval failed.\n"
                f"UPLOAD STDOUT:\n{stdout}\n\nUPLOAD STDERR:\n{stderr}\n\n"
                f"VERIFY STDOUT:\n{verify_stdout}\n\nVERIFY STDERR:\n{verify_stderr}"
            )
        
    # -------------------------------------------------------------------------
    # 9) Build the Neo N3 "receipt".
    #    This is the minimal payload you want to pass to Dev A’s contract.
    # -------------------------------------------------------------------------
    receipt = {
        "hash_alg": "SHA-256",
        "transcript_hash": transcript_hash,      # may be None if hash_plaintext=False
        "neofs_container_id": container_id,
        "neofs_object_id": object_id,
    }

    # -------------------------------------------------------------------------
    # 10) Return everything useful.
    #     receipt is what you store on-chain.
    #     stdout/stderr are helpful for debugging during the hackathon demo.
    # -------------------------------------------------------------------------
    return {
        "receipt": receipt,
        "upload_stdout": stdout,
        "upload_stderr": stderr,
        "verify_stdout": verify_stdout,
        "verify_stderr": verify_stderr,
    }



def upload_text_and_capture_oid(UPLOAD_SH, text: str) -> str:
    """
    Calls upload_transcript.sh and parses OID from stdout/stderr.
    Uses env vars for endpoint/wallet/container/cli path.
    """

    if not UPLOAD_SH.exists():
        raise FileNotFoundError(f"Missing script: {UPLOAD_SH}")

    env = os.environ.copy()

    # Run with capture_output so we can parse OID,
    # but still in a normal shell invocation.
    result = subprocess.run(
        ["bash", str(UPLOAD_SH), "--text", text],
        text=True,
        capture_output=True,
        env=env
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Upload script failed.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    combined = result.stdout + "\n" + result.stderr
    match = re.search(r"\bOID:\s*([A-Za-z0-9]+)", combined)

    if not match:
        raise RuntimeError(
            "Upload succeeded but could not parse OID.\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    return match.group(1)
def get_text_interactive(GET_SH, oid: str) -> None:
    """
    Calls get_transcript.sh. This script will print content
    if no output file is provided.
    """
    if not GET_SH.exists():
        raise FileNotFoundError(f"Missing script: {GET_SH}")

    env = os.environ.copy()

    with tempfile.NamedTemporaryFile(prefix="neofs_get_", suffix=".txt", delete=False) as tmp:
        out_path = tmp.name

    try:
        result = subprocess.run(
            ["bash", str(GET_SH), oid, out_path],
            env=env,
            text=True,
            capture_output=True
        )

        out_file = Path(out_path)

        # Trust the file over the exit code if content exists
        if out_file.exists() and out_file.stat().st_size > 0:
            return out_file.read_text(encoding="utf-8", errors="replace")

        # Otherwise, surface the real failure info
        raise RuntimeError(
            "NeoFS get failed and no content was written.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}\n"
        )

    finally:
        try:
            os.remove(out_path)
        except OSError:
            pass  
def prompt_user_text() -> str:
    """
    Simple single-line prompt.
    (If you want multi-line, I can give you that version too.)
    """
    text = input("\nEnter the transcript text you want to upload to NeoFS:\n> ").strip()
    if not text:
        # Fallback so you don't upload an empty object by accident
        text = "Default transcript: user provided empty input."
    return text



# =====================
# MAIN PROCESS FOR DEBUGGING
# =====================
if __name__ == "__main__":
    print("----------- DEBUGGING -----------")



   
