import os
import platform
from dataclasses import dataclass
from typing import List, Optional

import psutil

from ..logging import internal_logger
from ..schemas.events import KubernetesWorkloadData


def get_cpu_limit() -> Optional[str]:
    try:
        cpu_quota = read_file_safe("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
        cpu_period = read_file_safe("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
        if cpu_quota:
            if cpu_quota == "-1":
                return "unlimited"
            if not cpu_period:
                return None
            try:
                return str(int(cpu_quota) / int(cpu_period))
            except Exception as err:
                internal_logger.debug(
                    "Failed to calculate CPU limit with error: {}".format(err)
                )
                return None
        # cgroup v2
        cpu_max = read_file_safe("/sys/fs/cgroup/cpu.max")
        if not cpu_max:
            return None
        _max, period = cpu_max.split(" ")
        if _max == "max":
            return "unlimited"
        return str(float(_max) / float(period))
    except Exception as err:
        internal_logger.debug("Failed to get CPU limit with error: {}".format(err))
        return None


@dataclass
class MemoryInfo:
    pod_memory_limit_bytes: int
    source: str


def get_system_memory_limit() -> MemoryInfo:
    total_memory = psutil.virtual_memory().total
    return MemoryInfo(
        pod_memory_limit_bytes=total_memory,
        source="system-memory",
    )


def parse_memory_limit_string(content: str) -> Optional[int]:
    memory_bytes = int(content)
    if (
        memory_bytes <= 0 or memory_bytes > 128 * 1024 * 1024 * 1024
    ):  # We assume that a memory limit of 128GB or more is unlimited
        return None

    return memory_bytes


def check_cgroup_v2_memory(cgroup_files: List[str]) -> Optional[MemoryInfo]:
    for file_path in cgroup_files:
        content = read_file_safe(file_path)
        if content is None:
            continue

        if content.strip() == "max":
            continue

        try:
            memory_limit_bytes = parse_memory_limit_string(content)
            if memory_limit_bytes is not None:
                return MemoryInfo(
                    pod_memory_limit_bytes=memory_limit_bytes, source=file_path
                )
        except ValueError:
            internal_logger.debug(f"Failed to parse memory limit from {file_path}")
            continue

    return None


def check_cgroup_v1_memory(cgroup_files: List[str]) -> Optional[MemoryInfo]:
    for file_path in cgroup_files:
        content = read_file_safe(file_path)
        if not content:
            continue

        if file_path.endswith("memory.stat"):
            limit_indicators = [
                "hierarchical_memory_limit",
                "memory.limit_in_bytes",
                "limit_in_bytes",
            ]
            lines = content.split("\n")

            for indicator in limit_indicators:
                limit_line = None
                for line in lines:
                    if line.startswith(indicator):
                        limit_line = line
                        break

                if limit_line is None:
                    continue

                try:
                    memory_limit_bytes = parse_memory_limit_string(
                        limit_line.split()[1]
                    )
                    if memory_limit_bytes is not None:
                        return MemoryInfo(
                            pod_memory_limit_bytes=memory_limit_bytes,
                            source=f"{file_path}:{indicator}",
                        )
                except Exception:
                    continue
        else:
            try:
                memory_bytes = parse_memory_limit_string(content.strip())
                if memory_bytes is not None:
                    return MemoryInfo(
                        pod_memory_limit_bytes=memory_bytes,
                        source=file_path,
                    )
            except Exception:
                continue

    return None


def _get_memory_limit_without_cache() -> MemoryInfo:
    if platform.system() != "Linux":
        return get_system_memory_limit()

    cgroup_v2_files = ["/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory.high"]

    result = check_cgroup_v2_memory(cgroup_v2_files)
    if result is not None:
        internal_logger.info(
            f"Found pod memory limit: {result.pod_memory_limit_bytes}MB from {result.source}"
        )
        return result

    cgroup_v1_files = [
        "/sys/fs/cgroup/memory/memory.stat",
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",
    ]

    result = check_cgroup_v1_memory(cgroup_v1_files)
    if result is not None:
        internal_logger.info(
            f"Found pod memory limit: {result.pod_memory_limit_bytes}MB from {result.source}"
        )
        return result

    result = get_system_memory_limit()
    result.source = "system-memory-fallback"
    internal_logger.info(
        f"No container memory limit found, using system memory: {result.pod_memory_limit_bytes}MB"
    )

    return result


_cached_memory_info: Optional[MemoryInfo] = None


def get_memory_limit() -> MemoryInfo:
    global _cached_memory_info

    if _cached_memory_info is not None:
        return _cached_memory_info

    _cached_memory_info = _get_memory_limit_without_cache()
    return _cached_memory_info


def read_file_safe(file_path: str) -> Optional[str]:
    try:
        if not os.path.exists(file_path):
            internal_logger.debug("File {} not found".format(file_path))
            return None
        with open(
            file_path,
            "r",
            opener=lambda file, flags: os.open(file, flags | os.O_NONBLOCK),
        ) as file:
            return file.read()
    except FileNotFoundError:
        internal_logger.debug("File {} not found ERR".format(file_path))
        return None
    except Exception as err:
        internal_logger.debug(
            "Failed to read file {} with error: {}".format(file_path, err)
        )
        return None


def is_running_in_docker() -> bool:
    # Check for the existence of the .dockerenv file
    return os.path.exists("/.dockerenv")


def get_kubernetes_workload_data(
    pod_cpu_limit: Optional[str] = None,
) -> Optional[KubernetesWorkloadData]:
    if platform.system() != "Linux":
        internal_logger.info(
            "Kubernetes workload data is only available on Linux",
            data=dict(os=platform.system()),
        )
        return None
    if not is_running_in_docker():
        internal_logger.info(
            "Not running in a container, skipping Kubernetes workload data"
        )
        return None
    hostname = platform.node()
    namespace = read_file_safe(
        "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    )
    product_uuid = read_file_safe("/sys/class/dmi/id/product_uuid")
    memory = get_memory_limit()
    return KubernetesWorkloadData(
        pod_name=hostname,
        pod_cpu_limit=str(pod_cpu_limit),
        pod_memory_limit=memory.pod_memory_limit_bytes,
        pod_namespace=namespace,
        product_uuid=product_uuid,
    )
