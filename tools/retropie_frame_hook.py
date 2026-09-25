"""Receive exact FCEUmm video-frame colors from the local RetroArch proxy core."""

import os
import pwd
import socket
import struct
import threading
from collections import deque
from pathlib import Path
from time import monotonic

from controller.optical import ExactFrameDecoder
from tools.identify_game import identify

PROXY_CORE = b"/home/pi/rob-vision/build/rob_vision_fceumm_libretro.so"
SOCKET_PATH = Path("/run/rob-vision/frames.sock")


def sender_game(pid, registry, proc_root=Path("/proc")):
    """Trust only the active RetroPie process running our proxy for a known ROM."""
    if type(pid) is not int or pid < 1:
        return None
    try:
        args = (proc_root / str(pid) / "cmdline").read_bytes().split(b"\0")
    except OSError:
        return None
    if not args or Path(os.fsdecode(args[0])).name != "retroarch":
        return None
    if b"/dev/shm/retroarch.cfg" not in args:
        return None
    if not any(args[i] == b"-L" and args[i + 1] == PROXY_CORE
               for i in range(len(args) - 1)):
        return None
    for arg in args[1:]:
        rom = os.fsdecode(arg)
        if rom.casefold().startswith("/home/pi/retropie/roms/nes/"):
            return identify("nes", rom, registry)
    return None


class FrameHookServer:
    def __init__(self, registry, path=SOCKET_PATH):
        self.registry = registry
        self.path = Path(path)
        self.lock = threading.RLock()
        self.running = False
        self.thread = None
        self.sock = None
        self.sender_pid = None
        self.game = None
        self.last_frame_at = 0.0
        self.last_process_check = 0.0
        self.decoder = ExactFrameDecoder()
        self.pending = deque(maxlen=32)
        self.trace = os.getenv("ROB_FRAME_TRACE") == "1"
        self.trace_last_level = None

    def start(self):
        self.path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        self._unlink_socket()
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            sock.bind(str(self.path))
            os.chown(self.path, -1, pwd.getpwnam("pi").pw_gid)
            os.chmod(self.path, 0o660)
            sock.settimeout(.3)
        except Exception:
            sock.close()
            self._unlink_socket()
            raise
        self.sock = sock
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.sock:
            self.sock.close()
        self._unlink_socket()

    def _unlink_socket(self):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    def _loop(self):
        while self.running:
            try:
                packet, ancdata, _flags, _address = self.sock.recvmsg(5, socket.CMSG_SPACE(12))
            except socket.timeout:
                continue
            except OSError:
                break
            credentials = next((data for level, kind, data in ancdata
                                if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS), None)
            if len(packet) != 5 or credentials is None or len(credentials) < 12:
                continue
            pid, _uid, _gid = struct.unpack("3i", credentials[:12])
            index = struct.unpack("=I", packet[:4])[0]
            level = chr(packet[4])
            self.feed(pid, index, level)

    def feed(self, pid, index, level):
        now = monotonic()
        with self.lock:
            if pid != self.sender_pid or now - self.last_process_check >= .5:
                game = sender_game(pid, self.registry)
                self.last_process_check = now
                if pid != self.sender_pid or game != self.game:
                    self.decoder.reset()
                    print('R.O.B. frame hook: sender {} game {}.'.format(pid, game or 'ignored'), flush=True)
                self.sender_pid, self.game = pid, game
            if not self.game:
                return
            self.last_frame_at = now
            if self.trace and (level != self.trace_last_level or level != "N"):
                print('R.O.B. frame trace: {} {}'.format(index, level), flush=True)
            self.trace_last_level = level
            match = self.decoder.feed(index, level, self.game)
            if match:
                command, pattern = match
                print('R.O.B. frame hook: {} at frame {}.'.format(command, index), flush=True)
                self.pending.append({"game": self.game, "command": command,
                                     "pattern": pattern, "sender_pid": pid,
                                     "frame_index": index, "created_at": now})

    def recent_game(self):
        with self.lock:
            if self.game and monotonic() - self.last_frame_at < .5:
                return self.game
            return None

    def take_pending(self):
        with self.lock:
            items = list(self.pending)
            self.pending.clear()
            return items
