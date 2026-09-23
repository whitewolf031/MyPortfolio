import psutil


def get_top_memory_processes(limit=5):
    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "memory_percent", "memory_info"]
    ):
        try:
            info = process.info

            memory_mb = (
                info["memory_info"].rss / 1024 / 1024
            )

            processes.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "unknown",
                    "memory_percent": info["memory_percent"] or 0,
                    "memory_mb": memory_mb,
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda x: x["memory_mb"],
        reverse=True,
    )

    return processes[:limit]


def get_top_cpu_processes(limit=5):
    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent"]
    ):
        try:
            info = process.info

            processes.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "unknown",
                    "cpu_percent": info["cpu_percent"] or 0,
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda x: x["cpu_percent"],
        reverse=True,
    )

    return processes[:limit]
