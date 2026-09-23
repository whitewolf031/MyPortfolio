import subprocess

import psutil


def get_disk():
    disk = psutil.disk_usage("/")

    return {
        "path": "/",
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
    }


def get_largest_directories(path="/", limit=5):
    try:
        result = subprocess.run(
            [
                "du",
                "-x",
                "-d",
                "1",
                "-B1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return []

    if result.returncode not in (0, 1):
        return []

    directories = []

    for line in result.stdout.splitlines():
        line = line.strip()

        if not line:
            continue

        try:
            size_str, directory = line.split(
                "\t",
                1,
            )

            size = int(size_str)

        except (ValueError, TypeError):
            continue

        if directory.rstrip("/") == path.rstrip("/"):
            continue

        directories.append(
            (directory, size)
        )

    directories.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return directories[:limit]
