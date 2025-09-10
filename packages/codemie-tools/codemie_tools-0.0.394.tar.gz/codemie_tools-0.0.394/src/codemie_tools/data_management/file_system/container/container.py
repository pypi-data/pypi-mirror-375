import logging
import os
import socket
import sys
import tempfile
from typing import Tuple

from codemie_tools.data_management.file_system.container.mappings import check_and_write_mapping
from codemie_tools.data_management.file_system.container.runtime import (
    IPC_FD_FLAG,
    ROOTFS_PATH_FLAG,
    ContainerConnection,
)

logger = logging.getLogger(__name__)


class Container:
    def __init__(self):
        self.rootfs: str | None = None

    def _create_ipc_socketpair(self) -> Tuple[socket.socket, socket.socket]:
        parent_sock, child_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        parent_sock.set_inheritable(True)
        child_sock.set_inheritable(True)
        return parent_sock, child_sock

    def _parent_handle_connection_and_mappings(
        self, parent_sock: socket.socket, ready_r_fd: int, child_pid: int
    ):
        try:
            ready = os.read(ready_r_fd, 5)
            if ready != b"ready":
                sys.exit(1)

        finally:
            os.close(ready_r_fd)

        uid = os.getuid()
        gid = os.getgid()

        check_and_write_mapping(child_pid, uid, gid)

        parent_sock.sendall(b"mapped")

        return ContainerConnection(sock=parent_sock)

    def _child_first_level_flow(
        self, parent_sock: socket.socket, child_sock: socket.socket, ready_w_fd: int
    ) -> None:
        parent_sock.close()

        os.unshare(os.CLONE_NEWNS | os.CLONE_NEWUSER | os.CLONE_NEWPID)

        os.write(ready_w_fd, b"ready")
        os.close(ready_w_fd)

        try:
            ack = child_sock.recv(8)
            if ack != b"mapped":
                logger.debug(f"[PID: {os.getpid()}] unexpected ack from parent, got: %s", ack)
        except Exception as e:
            logger.error(f"[PID: {os.getpid()}] failed waiting for mapping ack: %s", e)

        pid2 = os.fork()
        if pid2 == 0:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.dirname(script_path)
            script_path = os.path.join(script_dir, "runtime.py")

            new_argv = [
                sys.executable,
                script_path,
                IPC_FD_FLAG,
                str(child_sock.fileno()),
                ROOTFS_PATH_FLAG,
                self.rootfs,
            ]

            os.execve(sys.executable, new_argv, {})

        else:
            child_sock.close()

            os.waitpid(pid2, 0)
            os._exit(0)

    def run(self):
        parent_sock, child_sock = self._create_ipc_socketpair()
        r, w = os.pipe()

        self.rootfs = tempfile.mkdtemp(prefix="container_root_")

        pid = os.fork()
        if pid == 0:
            os.close(r)

            self._child_first_level_flow(
                parent_sock=parent_sock, child_sock=child_sock, ready_w_fd=w
            )
            os._exit(1)
        else:
            os.close(w)

            child_sock.close()

            return self._parent_handle_connection_and_mappings(
                parent_sock=parent_sock, ready_r_fd=r, child_pid=pid
            )
