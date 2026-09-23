import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CLEANUP_SCRIPT = BASE_DIR / "server-auto-cleaning.sh"

async def run_cleanup():
    process = await asyncio.create_subprocess_exec(
	"sudo",
        "bash",
        str(CLEANUP_SCRIPT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, _ = await process.communicate()

    output = stdout.decode(
        "utf-8",
        errors="replace",
    )

    return process.returncode, output
