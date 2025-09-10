import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import requests

from strideutils import stride_requests
from strideutils.stride_config import config

WALLET_SETUP_COMMAND = "echo {mnemonic} | {binary} keys add {account_name} --recover --keyring-backend=test"


@dataclass
class TxResponse:
    stdout: dict
    stderr: str
    tx_hash: str = ""
    success: bool = False
    code: Optional[int] = None
    tx_response: Optional[dict] = None
    raw_log: Optional[str] = None


def restore_wallet(account_name: str = "wallet", mnemonic_var: str = "MNEMONIC", binary: str = "strided"):
    """
    Restores a wallet in the keyring, using the mnemonic under the specified environment variable
    """
    mnemonic = os.getenv(mnemonic_var)
    if not mnemonic:
        raise EnvironmentError(f"{mnemonic_var} must be set")

    os.system(WALLET_SETUP_COMMAND.format(mnemonic=mnemonic, binary=binary, account_name=account_name))


def execute_tx(command: str, api_endpoint: str = config.stride.api_endpoint) -> TxResponse:
    """
    Execute a tx and query the tx hash
    """
    # Tack on the auto-confirm if it's not already in the command and capture the output as JSON
    if "-y" not in command:
        command += " -y"
    command += " --output json"

    # Run the command in the shell and store the response
    output = subprocess.run(command, shell=True, capture_output=True, text=True)

    # If there was stderr, return the response as failed
    if not output.stdout or output.stderr:
        return TxResponse(stdout={}, stderr=output.stderr, raw_log=output.stderr)

    # Cast the stdout and build the response
    response = TxResponse(stdout=json.loads(output.stdout), stderr=output.stderr)

    # Get the tx hash or return an error if one was not generated
    response.tx_hash = response.stdout.get("txhash", "")
    if response.tx_hash == "":
        response.raw_log = "Tx hash not found after running tx"
        return response

    # Confirm the code ID was 0 in the stdout logs
    # Note: This is not the final code ID - just the one thrown after validate basic
    # Just because it's 0 doesn't mean it actually succeeded, but if it's non-zero
    # in the immediate logs then it means it failed validate basic
    if "code" in response.stdout and response.stdout["code"] != 0:
        response.raw_log = response.stdout["raw_log"]
        response.code = response.stdout["code"]
        return response

    # Poll the tx hash for the codeID and raw log
    for _ in range(30):
        # We intentionally search with requests directly instead of using stride_requests
        # so we can handle retries explicitly
        tx_search_response = requests.get(f"{api_endpoint}/{stride_requests.TXS_QUERY}/{response.tx_hash}")

        if tx_search_response.status_code != 200:
            time.sleep(2)
            continue

        response_data = tx_search_response.json()
        if not response_data.get("tx_response"):
            time.sleep(2)
            continue

        response.code = int(response_data["tx_response"]["code"])
        response.raw_log = response_data["tx_response"]["raw_log"]
        response.success = response.code == 0
        return response

    # If the tx was never found on chain, return an error
    response.raw_log = "Transaction not found on chain after one minute"
    return response
