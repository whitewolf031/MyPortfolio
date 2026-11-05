import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def parse_optional_int(value):
    if value is not None and str(value).strip():
        try:
            return int(str(value).strip())
        except ValueError:
            return None
    return None


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# Telegram Supergroup Forum Topic IDs (message_thread_id)
# Server monitoring (RAM, SSD, CPU, hisobotlar, alertlar) uchun topic:
SERVER_TOPIC_ID = parse_optional_int(os.getenv("SERVER_TOPIC_ID"))

# 5 kunlik tozalanganlar haqidagi ma'lumotlar uchun alohida topic:
CLEANUP_TOPIC_ID = parse_optional_int(os.getenv("CLEANUP_TOPIC_ID"))

# Kritik foiz chegaralari (alertlar uchun)
RAM_CRITICAL = int(os.getenv("RAM_CRITICAL", "90"))
DISK_CRITICAL = int(os.getenv("DISK_CRITICAL", "90"))
CPU_CRITICAL = int(os.getenv("CPU_CRITICAL", "90"))

# Hisobotlar va tekshirish intervallari
REPORT_INTERVAL_HOURS = int(os.getenv("REPORT_INTERVAL_HOURS", "4"))
ALERT_CHECK_INTERVAL_SECONDS = int(os.getenv("ALERT_CHECK_INTERVAL_SECONDS", "60"))

# Tozalash sozlamalari
CLEANUP_INTERVAL_DAYS = int(os.getenv("CLEANUP_INTERVAL_DAYS", "1"))
CLEANUP_MAX_DAYS = int(os.getenv("CLEANUP_MAX_DAYS", "5"))


if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

if not TELEGRAM_GROUP_ID:
    raise ValueError("TELEGRAM_GROUP_ID is not configured")
