import asyncio
import os
import shutil
from pathlib import Path

from config import CLEANUP_MAX_DAYS

BASE_DIR = Path(__file__).resolve().parent
CLEANUP_SCRIPT = BASE_DIR / "server-auto-cleaning.sh"


async def run_cleanup():
    cmd = ["bash", str(CLEANUP_SCRIPT)]

    # Agar root bo'lmasa va sudo mavjud bo'lsa, parolsiz sudo ishlaydimi tekshiramiz
    if os.geteuid() != 0 and shutil.which("sudo"):
        try:
            check_sudo = await asyncio.create_subprocess_exec(
                "sudo",
                "-n",
                "true",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            code = await check_sudo.wait()
            if code == 0:
                cmd = ["sudo", "-n", "-E", "bash", str(CLEANUP_SCRIPT)]
        except Exception:
            pass

    env = os.environ.copy()
    env["CLEAN_DAYS"] = str(CLEANUP_MAX_DAYS)

    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, _ = await process.communicate()

    output = stdout.decode(
        "utf-8",
        errors="replace",
    )

    return process.returncode, output
