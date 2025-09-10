import asyncio
import os
import shutil
import socket
import struct
import sys
import tempfile
import logging


from codemie_tools.data_management.file_system.container.jupyter import Jupyter, RuntimeOutput
from codemie_tools.data_management.file_system.container.utils.c_types_util import (
    MountFlags,
    mount,
    umount,
)

logger = logging.getLogger(__name__)

IPC_FD_FLAG = "--ipc-fd"
ROOTFS_PATH_FLAG = "--rootfs"

ROOT_FOLDER = "/root"


class ContainerConnection:
    def __init__(self, fd: int | None = None, sock: socket.socket | None = None) -> None:
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(fileno=fd)

    def send_msg(self, data_bytes: bytes):
        header = struct.pack(">I", len(data_bytes))
        self.sock.sendall(header + data_bytes)

    def recvall(self, n: int):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    def recv_msg(self):
        header = self.recvall(4)
        if not header:
            return None
        length = struct.unpack(">I", header)[0]
        return self.recvall(length)

    async def asend_msg(self, data_bytes: bytes) -> None:
        """Asynchronously send a length-prefixed message (4-byte big-endian header)."""
        try:
            self.sock.setblocking(False)
        except OSError:
            pass

        header = struct.pack(">I", len(data_bytes))
        loop = asyncio.get_running_loop()
        await loop.sock_sendall(self.sock, header + data_bytes)

    async def arecvall(self, n: int) -> bytes | None:
        try:
            self.sock.setblocking(False)
        except OSError:
            pass

        buf = b""
        loop = asyncio
        loop = asyncio.get_running_loop()
        while len(buf) < n:
            chunk = await loop.sock_recv(self.sock, n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    async def arecv_msg(self) -> bytes | None:
        """Asynchronously receive a length-prefixed message (4-byte big-endian header). Returns the message bytes or None on EOF."""
        header = await self.arecvall(4)
        if not header:
            return None
        length = struct.unpack(">I", header)[0]
        return await self.arecvall(length)

    def close(self):
        self.sock.close()


def raise_exit_code(msg: str, code: int):
    raise RuntimeError(f"{msg}. errno={code} ({os.strerror(code)})")


class ContainerRuntime:
    host_volumes_to_mount = [
        "/bin",
        "/sbin",
        "/usr",
        "/lib",
        "/lib64",
        "/venv",
    ]

    rootless_tmp_fs = [
        "/var",
        ROOT_FOLDER,
        "/etc",
    ]

    host_dev_devices = [
        "null",
        "zero",
        "full",
        "random",
        "urandom",
    ]

    def _setup_environ(self):
        os.environ.clear()
        os.environ["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin"
        os.environ["HOME"] = ROOT_FOLDER

    def _mount_dev(self, dev_folder: str):
        if err := mount("tmpfs", dev_folder, fstype="tmpfs", flags=0, data=f"mode={755}"):
            raise_exit_code("cannot mount dev folder", err)

        for dev in self.host_dev_devices:
            source = f"/dev/{dev}"
            target = os.path.join(dev_folder, dev)

            if os.path.exists(source):
                open(target, "a").close()
                if err := mount(source, target, flags=MountFlags.BIND):
                    raise_exit_code(f"cannot mount {dev} dev", err)

    def _umount_dev(self, dev_folder: str):
        for dev in self.host_dev_devices:
            target = os.path.join(dev_folder, dev)
            umount(target)
        umount(dev_folder)

    def _mount_etc(self, etc_folder: str):
        if err := mount("tmpfs", etc_folder, fstype="tmpfs"):
            raise_exit_code("Cannot mount etc folder", err)

        with open(os.path.join(etc_folder, "passwd"), "w") as f:
            f.write("root:x:0:0:root:/root:/bin/sh\n")
        with open(os.path.join(etc_folder, "group"), "w") as f:
            f.write("root:x:0:\n")
        with open(os.path.join(etc_folder, "hostname"), "w") as f:
            f.write("container\n")
        with open(os.path.join(etc_folder, "hosts"), "w") as f:
            f.write("127.0.0.1 localhost\n::1 localhost\n127.0.0.1 container\n")
        if os.path.exists("/etc/resolv.conf"):
            shutil.copy2("/etc/resolv.conf", os.path.join(etc_folder, "resolv.conf"))

    def setup_rootfs(self, rootfs_folder: str):
        if err := mount(None, "/", flags=MountFlags.REC | MountFlags.PRIVATE):
            raise_exit_code("Cannot mount read only root", err)

        for source_folder in self.host_volumes_to_mount:
            target_folder = os.path.join(rootfs_folder, source_folder.lstrip("/"))
            if err := mount(
                source_folder, target_folder, flags=MountFlags.BIND | MountFlags.PRIVATE
            ):
                raise_exit_code(f"Cannot mount {source_folder} to {target_folder}", err)

        for tmp_folder in self.rootless_tmp_fs:
            target_folder = os.path.join(rootfs_folder, tmp_folder.lstrip("/"))
            if err := mount("tmpfs", target_folder, "tmpfs", 0, "mode=755"):
                raise_exit_code(f"Cannot mount tmpfs to {target_folder}", err)

        proc_folder = os.path.join(rootfs_folder, "proc")
        if err := mount("proc", proc_folder, "proc"):
            raise_exit_code("Cannot mount proc to {proc_folder}", err)

        dev_dir = os.path.join(rootfs_folder, "dev")
        self._mount_dev(dev_dir)

        etc_dir = os.path.join(rootfs_folder, "etc")
        self._mount_etc(etc_dir)

        try:
            os.chdir(rootfs_folder)
            os.chroot(".")
            os.chdir("/")
        except Exception as e:
            raise ValueError(f"Cannot chroot user. Err: {str(e)}")

        self._setup_environ()

    def destroy_rootfs(self, rootfs_folder: str):
        for source_folder in self.host_volumes_to_mount:
            target_folder = os.path.join(rootfs_folder, source_folder.lstrip("/"))
            umount(target_folder)

        for tmp_folder in self.rootless_tmp_fs:
            target_folder = os.path.join(rootfs_folder, tmp_folder.lstrip("/"))
            umount(target_folder)

        self._umount_dev(os.path.join(rootfs_folder, "dev"))
        self._umount_dev(os.path.join(rootfs_folder, "etc"))
        umount(os.path.join(rootfs_folder, "proc"))


async def handler(ipc_fd: int, rootfs: str):
    r = ContainerRuntime()
    r.setup_rootfs(rootfs)
    ipc_sock = ContainerConnection(ipc_fd)
    try:
        with tempfile.TemporaryDirectory(prefix="jupyter_") as jupyter_dir:
            async with Jupyter(jupyter_dir) as jupyter:
                if not jupyter.kc:
                    raise RuntimeError("jupyter client could not be started")

                while True:
                    msg = await ipc_sock.arecv_msg()

                    if not msg:
                        continue

                    cmd = msg.decode("utf-8", errors="replace")

                    if cmd == "__shutdown__":
                        return

                    result = await jupyter.arun(msg.decode())

                    await ipc_sock.asend_msg(result.model_dump_json().encode())
    except Exception as e:
        ipc_sock.send_msg(
            RuntimeOutput(type="error", content=f"during execution an error occurred: {str(e)}")
            .model_dump_json()
            .encode()
        )
    finally:
        ipc_sock.close()
        os._exit(0)


if __name__ == "__main__":
    try:
        i = sys.argv.index(IPC_FD_FLAG)
        ipc_fd = int(sys.argv[i + 1])
    except Exception:
        os._exit(1)

    try:
        i = sys.argv.index(ROOTFS_PATH_FLAG)
        rootfs = sys.argv[i + 1]
    except Exception:
        os._exit(1)

    asyncio.run(handler(ipc_fd, rootfs))
