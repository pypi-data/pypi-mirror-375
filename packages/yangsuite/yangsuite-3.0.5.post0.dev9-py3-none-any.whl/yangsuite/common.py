from pathlib import Path
import os
import time
import hashlib
from django.conf import settings


def create_packages_snapshot(snapshots_path: str = '', snapshots_limit: int = 1) -> bool:
    """Create snapshot file with installed packages

    Args:
        snapshots_path (str): Path to main snapshots directory
        snapshots_limit (int, optional): Max number of saved snapshots. Defaults to 1.

    Returns:
        bool: _description_
    """
    if not snapshots_path:
        snapshots_path = settings.SNAPSHOTS_DIR
    SNAPSHOTS_DIR = Path(snapshots_path)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    try:
        from pip._internal.operations import freeze
    except ImportError:  # pip < 10.0
        from pip.operations import freeze
    pkgs = "\n".join(list(freeze.freeze()))
    snapshot_name = f"{time.time()}"
    snapshots = os.listdir(SNAPSHOTS_DIR)
    with open(SNAPSHOTS_DIR / snapshot_name, "w") as f:
        f.write(pkgs)
    while len(snapshots) >= snapshots_limit:
        os.remove(SNAPSHOTS_DIR / snapshots.pop(0))
    return True


def create_hash(input_string):
    # Create a hashlib object for SHA-256 hash
    hash_object = hashlib.sha256()

    # Update the hash object with the input string
    hash_object.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_value = hash_object.hexdigest()

    # Return the hash value
    return hash_value
