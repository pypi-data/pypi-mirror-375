import ctypes
import ctypes.util
import os
from enum import IntEnum
from functools import lru_cache


def _c_char_p_or_null(s):
    if s is None:
        return ctypes.c_char_p(None)
    if isinstance(s, bytes):
        return ctypes.c_char_p(s)
    return ctypes.c_char_p(s.encode() if isinstance(s, str) else str(s).encode())


@lru_cache
def get_libc():
    libc_path = ctypes.util.find_library("c")
    if not libc_path:
        raise RuntimeError("Could not find libc")

    libc = ctypes.CDLL(libc_path, use_errno=True)
    libc.mount.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_void_p,
    ]
    libc.mount.restype = ctypes.c_int

    libc.umount.argtypes = [ctypes.c_char_p]
    libc.umount.restype = ctypes.c_int
    return libc


def mount_ctypes(source, target, fstype=None, flags=0, data=None):
    src_p = _c_char_p_or_null(source)
    tgt_p = _c_char_p_or_null(target)
    fs_p = _c_char_p_or_null(fstype)
    data_p = _c_char_p_or_null(data)

    ret = get_libc().mount(
        src_p, tgt_p, fs_p, ctypes.c_ulong(flags), ctypes.cast(data_p, ctypes.c_void_p)
    )
    if ret == 0:
        return 0
    return ctypes.get_errno() or 1


class MountFlags(IntEnum):
    RDONLY = 1
    BIND = 4096
    REC = 16384
    PRIVATE = 1 << 18


def mount(source, target, fstype=None, flags=0, data=None):
    """
    Returns:
        0 on success, non-zero on failure.
    """
    if not os.path.exists(target):
        os.makedirs(target, exist_ok=True)

    return mount_ctypes(source, target, fstype, flags, data)


def umount(target: str):
    """Unmount the filesystem mounted at target."""
    ret = get_libc().umount(ctypes.c_char_p(target.encode("utf-8")))
    if ret == 0:
        return 0
    return ctypes.get_errno() or 1
