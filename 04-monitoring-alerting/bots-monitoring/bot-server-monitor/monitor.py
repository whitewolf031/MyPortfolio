from checks.memory import get_memory
from checks.disk import (
    get_disk,
    get_largest_directories,
)
from checks.cpu import get_cpu
from checks.process import (
    get_top_memory_processes,
    get_top_cpu_processes,
)
from checks.docker import get_docker
from checks.logs import get_logs

from config import (
    RAM_CRITICAL,
    DISK_CRITICAL,
    CPU_CRITICAL,
)


def get_critical_metrics():
    return {
        "memory": get_memory(),
        "disk": get_disk(),
        "cpu": get_cpu(),
    }


def get_server_status():
    memory = get_memory()
    disk = get_disk()
    cpu = get_cpu()

    processes = get_top_memory_processes()
    cpu_processes = get_top_cpu_processes()

    docker = get_docker()
    logs = get_logs()

    largest_directories = get_largest_directories(
        "/",
        limit=5,
    )

    return {
        "memory": memory,
        "disk": disk,
        "cpu": cpu,
        "processes": processes,
        "cpu_processes": cpu_processes,
        "docker": docker,
        "logs": logs,
        "largest_directories": largest_directories,
    }


def check_alerts(status):
    alerts = []

    memory_percent = status["memory"]["percent"]
    disk_percent = status["disk"]["percent"]
    cpu_percent = status["cpu"]["percent"]

    if memory_percent >= RAM_CRITICAL:
        alerts.append(
            {
                "type": "RAM_CRITICAL",
                "value": memory_percent,
                "threshold": RAM_CRITICAL,
            }
        )

    if disk_percent >= DISK_CRITICAL:
        alerts.append(
            {
                "type": "DISK_CRITICAL",
                "value": disk_percent,
                "threshold": DISK_CRITICAL,
            }
        )

    if cpu_percent >= CPU_CRITICAL:
        alerts.append(
            {
                "type": "CPU_CRITICAL",
                "value": cpu_percent,
                "threshold": CPU_CRITICAL,
            }
        )

    return alerts
