import os

from dotenv import load_dotenv


load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

RAM_CRITICAL = int(os.getenv("RAM_CRITICAL", "90"))
DISK_CRITICAL = int(os.getenv("DISK_CRITICAL", "90"))

REPORT_INTERVAL_HOURS = int(
    os.getenv("REPORT_INTERVAL_HOURS", "4")
)

ALERT_CHECK_INTERVAL_SECONDS = int(
    os.getenv("ALERT_CHECK_INTERVAL_SECONDS", "60")
)


if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

if not TELEGRAM_GROUP_ID:
    raise ValueError("TELEGRAM_GROUP_ID is not configured")
