import shutil
import subprocess


def get_docker():
    if not shutil.which("docker"):
        return {
            "installed": False,
            "containers": 0,
            "running": 0,
            "disk_usage": None,
        }

    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "-q"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        containers = [
            line
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        result = subprocess.run(
            ["docker", "ps", "-q"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        running = [
            line
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        return {
            "installed": True,
            "containers": len(containers),
            "running": len(running),
            "disk_usage": get_docker_disk_usage(),
        }

    except (
        subprocess.SubprocessError,
        FileNotFoundError,
    ):
        return {
            "installed": True,
            "containers": 0,
            "running": 0,
            "disk_usage": None,
        }


def get_docker_disk_usage():
    try:
        result = subprocess.run(
            ["docker", "system", "df"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        return result.stdout.strip()

    except subprocess.SubprocessError:
        return None
