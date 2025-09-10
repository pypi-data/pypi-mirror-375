import logging
from typing import Tuple

from codeboxapi.box.localbox import Path

logger = logging.getLogger(__name__)


def _read_lines(path: Path) -> Tuple[bool, Tuple[str, ...]]:
    """Read all lines from path and return (success, lines). On failure returns (False, ())."""
    try:
        with path.open("r", encoding="utf-8") as f:
            # strip newline characters but preserve internal whitespace in lines
            return True, tuple(line.strip() for line in f)
    except FileNotFoundError:
        logger.debug("File not found: %s", path)
        return False, ()
    except PermissionError:
        logger.warning("Permission denied reading %s", path)
        return False, ()
    except Exception as exc:
        logger.error("Error reading %s: %s", path, exc)
        return False, ()


def _write_file(path: Path, content: str) -> bool:
    """Try to write content to path. Return True on success, False on failure."""
    try:
        with path.open("w", encoding="utf-8") as f:
            f.write(content)
        logger.debug("Wrote %s", path)
        return True
    except PermissionError:
        logger.warning("Permission denied writing %s", path)
        return False
    except FileNotFoundError:
        logger.warning("File not found when writing %s", path)
        return False
    except Exception as exc:
        logger.error("Error writing %s: %s", path, exc)
        return False


def _ensure_mapping(map_path: Path, expected_mapping: str, desc: str) -> bool:
    exists, lines = _read_lines(map_path)
    if exists and expected_mapping in lines:
        logger.debug("%s already present: %s", desc, expected_mapping)
        return True

    # Try to write mapping (even if file didn't exist, attempt write to create it)
    content = expected_mapping + "\n"
    if _write_file(map_path, content):
        logger.debug("Wrote %s: %s", desc, expected_mapping)
        return True

    logger.warning("Could not ensure %s: %s", desc, expected_mapping)
    return False


def check_and_write_mapping(pid: int, uid: int, gid: int) -> bool:
    """
    Checks and writes the UID and GID mappings for a specified process ID (PID).
    Writes the configuration of user and group ID mappings, ensuring that permission settings are correctly applied to processes in isolated namespaces.
    """

    proc_dir = Path("/proc") / str(pid)
    if not proc_dir.exists():
        logger.warning("No such process PID %s", pid)
        return False

    # Attempt to write "deny" to setgroups if file exists
    setgroups = proc_dir / "setgroups"
    if setgroups.exists():
        if _write_file(setgroups, "deny\n"):
            logger.debug("Wrote deny to setgroups for PID %s", pid)
        else:
            logger.warning("Could not write setgroups for PID %s", pid)
    else:
        logger.debug("setgroups not present for PID %s", pid)

    uid_map = proc_dir / "uid_map"
    gid_map = proc_dir / "gid_map"
    expected_uid = f"0 {uid} 1"
    expected_gid = f"0 {gid} 1"

    uid_ok = _ensure_mapping(uid_map, expected_uid, "uid_map")
    gid_ok = _ensure_mapping(gid_map, expected_gid, "gid_map")

    return uid_ok and gid_ok
