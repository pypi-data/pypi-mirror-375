import fcntl
import os
import sys
import time
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

import psutil

from ..config import config
from ..forkable import ScopedForksafeResource
from ..json import JSONDecodeError, dumps, loads
from ..logging import internal_logger
from ..process_utils import is_alive
from ..version import version

if TYPE_CHECKING:
    from typing import Literal


def get_status_file_path(unique_id: Optional[str] = None) -> str:
    if unique_id is None:
        unique_id = config.exporter_unique_id
    return "{}-{}-{}-{}".format(
        config.hud_exporter_status_file, version, sys.version_info.minor, unique_id
    )


def lock_fd(fd: int, lock_type: int, timeout: int) -> None:
    """
    Fork-safe locking using fcntl.lockf which uses POSIX record locks.
    These locks are process-specific and don't inherit across fork.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            fcntl.lockf(fd, lock_type | fcntl.LOCK_NB, 0)
            return
        except OSError:
            time.sleep(0.05)

    raise TimeoutError("Could not acquire lock within {} seconds".format(timeout))


def synchronised_write(filename: str, data: bytes, timeout: int) -> None:
    # We open with 'ab' because we only lock the file after opening it. Opening with 'wb' will truncate the file.
    with ScopedForksafeResource(open(filename, "ab", buffering=0)) as f:
        lock_fd(f.fileno(), fcntl.LOCK_EX, timeout)
        f.seek(0)
        f.truncate(0)
        f.write(data)


def synchronised_read(filename: str, timeout: int) -> bytes:
    with ScopedForksafeResource(open(filename, "rb", buffering=0)) as f:
        lock_fd(f.fileno(), fcntl.LOCK_SH, timeout)
        return f.read()


class ExporterStatus:
    def __init__(self, **kwargs: Any) -> None:
        self.status = {**kwargs}

    @property
    def pid(self) -> Optional[int]:
        return cast(Optional[int], self.status.get("pid", None))

    @pid.setter
    def pid(self, value: Optional[int]) -> None:
        self.status["pid"] = value

    @property
    def manager_port(self) -> Optional[int]:
        return cast(Optional[int], self.status.get("manager_port", None))

    @manager_port.setter
    def manager_port(self, value: Optional[int]) -> None:
        self.status["manager_port"] = value

    @property
    def creation_id(self) -> Optional[str]:
        return cast(Optional[str], self.status.get("creation_id", None))

    @creation_id.setter
    def creation_id(self, value: Optional[str]) -> None:
        self.status["creation_id"] = value

    @property
    def claimed_by(self) -> Optional[int]:
        return cast(Optional[int], self.status.get("claimed_by", None))

    @claimed_by.setter
    def claimed_by(self, value: Optional[int]) -> None:
        self.status["claimed_by"] = value

    @property
    def claimed_at(self) -> Optional[float]:
        return cast(Optional[float], self.status.get("claimed_at", None))

    @claimed_at.setter
    def claimed_at(self, value: Optional[float]) -> None:
        self.status["claimed_at"] = value

    def dump_json(self) -> bytes:
        return dumps(self.status)


def write_initial_status(filename: str, data: bytes, timeout: int) -> bool:
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    with ScopedForksafeResource(open(filename, "a+b", buffering=0)) as f:
        lock_fd(f.fileno(), fcntl.LOCK_EX, timeout)
        f.seek(0)
        content = f.read()
        try:
            status = ExporterStatus(**loads(content.decode()))
        except JSONDecodeError:
            status = ExporterStatus()

        if is_exporter_alive(status):
            return False

        f.seek(0)
        f.truncate(0)
        f.write(data)
        return True


def atomic_claim_spawn_rights(unique_id: Optional[str], worker_pid: int) -> bool:
    file_path = get_status_file_path(unique_id)

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with ScopedForksafeResource(open(file_path, "a+b", buffering=0)) as f:
            lock_fd(
                f.fileno(),
                fcntl.LOCK_EX,
                config.exporter_status_lock_acquisition_timeout,
            )
            f.seek(0)
            content = f.read()

            try:
                status = (
                    ExporterStatus(**loads(content.decode()))
                    if content
                    else ExporterStatus()
                )
            except JSONDecodeError:
                status = ExporterStatus()

            if is_exporter_alive(status):
                internal_logger.info("Exporter already running, claim failed")
                return False

            current_time = time.time()
            if (
                status.claimed_by is not None
                and status.claimed_by != worker_pid
                and status.claimed_at is not None
                and current_time - status.claimed_at < config.exporter_start_timeout
                and is_alive(status.claimed_by)
            ):
                internal_logger.info(
                    "Another worker has valid claim",
                    data={"claimed_by": status.claimed_by},
                )
                return False

            internal_logger.info(
                "No exporter running, claiming spawn rights",
                data={"worker_pid": worker_pid},
            )

            status.claimed_by = worker_pid
            status.claimed_at = current_time
            status.pid = None
            status.manager_port = None
            status.creation_id = None

            new_content = status.dump_json()
            f.seek(0)
            f.truncate(0)
            f.write(new_content)

            internal_logger.info(
                "Successfully claimed spawn rights",
                data={"worker_pid": worker_pid, "unique_id": unique_id},
            )
            return True
    except TimeoutError:
        internal_logger.warning("Timeout acquiring lock for spawn claim")
        return False
    except Exception:
        internal_logger.exception("Failed to claim spawn rights")
        return False


def release_spawn_claim(unique_id: Optional[str], worker_pid: int) -> None:
    file_path = get_status_file_path(unique_id)

    if not os.path.exists(file_path):
        return
    try:
        with ScopedForksafeResource(open(file_path, "a+b", buffering=0)) as f:
            lock_fd(
                f.fileno(),
                fcntl.LOCK_EX,
                config.exporter_status_lock_acquisition_timeout,
            )

            f.seek(0)
            content = f.read()

            if not content:
                return

            try:
                status = ExporterStatus(**loads(content.decode()))
            except JSONDecodeError:
                return

            if status.claimed_by == worker_pid:
                f.seek(0)
                f.truncate(0)
                internal_logger.info(
                    "Released spawn claim",
                    data={"worker_pid": worker_pid, "unique_id": unique_id},
                )
            else:
                internal_logger.info(
                    "Not releasing claim - not owned by this worker",
                    data={"worker_pid": worker_pid, "claimed_by": status.claimed_by},
                )
    except TimeoutError:
        internal_logger.warning("Timeout releasing spawn claim")
    except Exception:
        internal_logger.exception("Failed to release spawn claim")


def get_exporter_status(
    timeout: int = config.exporter_status_lock_acquisition_timeout,
    unique_id: Optional[str] = None,
) -> ExporterStatus:
    status_content = b"{}"
    file_path = get_status_file_path(unique_id)
    try:
        status_content = synchronised_read(file_path, timeout)
    except TimeoutError:
        raise
    except Exception:
        return ExporterStatus()

    if status_content == b"":
        return ExporterStatus()

    return ExporterStatus(**loads(status_content.decode()))


def is_exporter_alive(status: ExporterStatus) -> bool:
    if status.pid is None or status.creation_id is None:
        return False
    try:
        ps = psutil.Process(status.pid)
        hud_exporter_module_name = "{}.exporter".format(config.sdk_name)
        if not ps.is_running():
            return False
        if not any(hud_exporter_module_name in seg for seg in ps.cmdline()):
            return False
        if not any(status.creation_id in seg for seg in ps.cmdline()):
            return False
        return True

    except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
        return False


def wait_for_exporter(
    timeout: int = config.exporter_start_timeout,
    wait_condition: "Union[Literal['alive'], Literal['dead']]" = "alive",
    unique_id: Optional[str] = None,
    early_stop_predicate: Optional[Callable[[float], bool]] = None,
) -> Optional[ExporterStatus]:
    if wait_condition == "alive":
        condition = True
    elif wait_condition == "dead":
        condition = False
    current_time = start_time = time.time()
    while current_time - start_time < timeout:
        if early_stop_predicate is not None and early_stop_predicate(
            current_time - start_time
        ):
            internal_logger.warning(
                "Waiting for the exporter stopped due to early stop predicate"
            )
            return None
        status = get_exporter_status(unique_id=unique_id)
        if is_exporter_alive(status) == condition:
            return status
        time.sleep(0.4)
        current_time = time.time()
    return None
