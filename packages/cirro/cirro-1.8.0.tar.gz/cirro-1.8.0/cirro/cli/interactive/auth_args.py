import logging
from typing import Tuple, Dict

from cirro.cli.interactive.utils import ask_yes_no, ask
from cirro.config import extract_base_url

logger = logging.getLogger()


def gather_auth_config() -> Tuple[str, str, Dict, bool]:
    base_url = ask(
        'text',
        'Enter the URL of the Cirro instance you\'d like to connect to:'
    )
    # Fix user-provided base URL, if necessary
    base_url = extract_base_url(base_url)

    auth_method_config = {
        'enable_cache': ask_yes_no('Would you like to save your login? (do not use this on shared devices)')
    }

    enable_additional_checksum = ask(
        'select',
        'Upload / download file validation type (note: SHA-256 requires additional local compute)',
        choices=['CRC64 (default)', 'SHA-256']
    ) == 'SHA-256'

    return 'ClientAuth', base_url, auth_method_config, enable_additional_checksum
