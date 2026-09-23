import logging
import socket

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_GROUP_ID,
    REPORT_INTERVAL_HOURS,
    ALERT_CHECK_INTERVAL_SECONDS,
)

from monitor import (
    get_server_status,
    get_critical_metrics,
    check_alerts,
)
from checks.cleanup import run_cleanup

logging.basicConfig(
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


ram_alert_active = False
disk_alert_active = False


def format_bytes(value):
    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ]

    size = float(value)

    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} PB"


def format_status(status):
    memory = status["memory"]
    disk = status["disk"]

    message = [
        "🖥 <b>SERVER STATUS</b>",
        "",
        f"Hostname: <code>{socket.gethostname()}</code>",
        "",
        "🧠 <b>RAM</b>",
        (
            f"Used: {format_bytes(memory['used'])} / "
            f"{format_bytes(memory['total'])}"
        ),
        f"Usage: {memory['percent']:.1f}%",
        f"Available: {format_bytes(memory['available'])}",
        "",
        "💾 <b>DISK</b>",
        (
            f"Used: {format_bytes(disk['used'])} / "
            f"{format_bytes(disk['total'])}"
        ),
        f"Usage: {disk['percent']:.1f}%",
        f"Free: {format_bytes(disk['free'])}",
        "",
        "🔥 <b>TOP RAM PROCESSES</b>",
    ]

    for index, process in enumerate(
        status["processes"],
        start=1,
    ):
        message.append(
            f"{index}. {process['name']} "
            f"(<code>{process['pid']}</code>) — "
            f"{process['memory_mb']:.1f} MB"
        )

    message.extend(
        [
            "",
            "⚡ <b>TOP CPU PROCESSES</b>",
        ]
    )

    for index, process in enumerate(
        status["cpu_processes"],
        start=1,
    ):
        message.append(
            f"{index}. {process['name']} "
            f"(<code>{process['pid']}</code>) — "
            f"{process['cpu_percent']:.1f}%"
        )

    message.extend(
        [
            "",
            "📁 <b>LARGEST DIRECTORIES</b>",
        ]
    )

    for path, size in status["largest_directories"]:
        message.append(
            f"<code>{path}</code> — "
            f"{format_bytes(size)}"
        )

    message.extend(
        [
            "",
            "🐳 <b>DOCKER</b>",
        ]
    )

    docker = status["docker"]

    if docker["installed"]:
        message.append(
            f"Containers: {docker['containers']}"
        )
        message.append(
            f"Running: {docker['running']}"
        )
    else:
        message.append(
            "Docker: not installed"
        )

    message.extend(
        [
            "",
            "📋 <b>LOGS</b>",
            (
                f"/var/log — "
                f"{format_bytes(status['logs']['size'])}"
            ),
        ]
    )

    return "\n".join(message)


def format_ram(status):
    memory = status["memory"]

    return (
        "🧠 <b>RAM STATUS</b>\n\n"
        f"Total: {format_bytes(memory['total'])}\n"
        f"Used: {format_bytes(memory['used'])}\n"
        f"Available: "
        f"{format_bytes(memory['available'])}\n"
        f"Usage: {memory['percent']:.1f}%\n\n"
        f"Swap: "
        f"{format_bytes(memory['swap_used'])} / "
        f"{format_bytes(memory['swap_total'])}\n"
        f"Swap usage: "
        f"{memory['swap_percent']:.1f}%"
    )


def format_disk(status):
    disk = status["disk"]

    message = [
        "💾 <b>DISK STATUS</b>",
        "",
        f"Total: {format_bytes(disk['total'])}",
        f"Used: {format_bytes(disk['used'])}",
        f"Free: {format_bytes(disk['free'])}",
        f"Usage: {disk['percent']:.1f}%",
        "",
        "📁 <b>LARGEST DIRECTORIES</b>",
    ]

    for path, size in status["largest_directories"]:
        message.append(
            f"<code>{path}</code> — "
            f"{format_bytes(size)}"
        )

    return "\n".join(message)


async def startup_message(
    application: Application,
):
    await application.bot.send_message(
        chat_id=TELEGRAM_GROUP_ID,
        text=(
            "🚀 <b>server-monitoring bot</b> "
            "ishga tushdi."
        ),
        parse_mode=ParseMode.HTML,
    )


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    await update.message.reply_text(
        "🤖 <b>Server Monitor</b>\n\n"
        "/status - server holati\n"
        "/ram - RAM holati\n"
        "/disk - Disk holati",
        parse_mode=ParseMode.HTML,
    )


async def status_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    status = get_server_status()

    await update.message.reply_text(
        format_status(status),
        parse_mode=ParseMode.HTML,
    )


async def ram_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    status = get_critical_metrics()

    await update.message.reply_text(
        format_ram(status),
        parse_mode=ParseMode.HTML,
    )


async def disk_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    status = get_server_status()

    await update.message.reply_text(
        format_disk(status),
        parse_mode=ParseMode.HTML,
    )


async def send_report(
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        status = get_server_status()

        await context.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID,
            text=format_status(status),
            parse_mode=ParseMode.HTML,
        )

        logger.info(
            "4-hour server report sent"
        )

    except Exception:
        logger.exception(
            "Failed to send server report"
        )


async def check_server_alerts(
    context: ContextTypes.DEFAULT_TYPE,
):
    global ram_alert_active
    global disk_alert_active

    try:
        status = get_critical_metrics()

        alerts = check_alerts(status)

        ram_critical = any(
            alert["type"] == "RAM_CRITICAL"
            for alert in alerts
        )

        disk_critical = any(
            alert["type"] == "DISK_CRITICAL"
            for alert in alerts
        )

        if ram_critical and not ram_alert_active:
            memory = status["memory"]

            message = (
                "🚨 <b>RAM CRITICAL</b>\n\n"
                f"Usage: {memory['percent']:.1f}%\n"
                f"Used: {format_bytes(memory['used'])}\n"
                f"Total: {format_bytes(memory['total'])}\n\n"
                "🔥 <b>TOP RAM PROCESSES</b>\n"
            )

            # Critical holatda processlarni ham ko'rsatish
            detailed_status = get_server_status()

            for process in detailed_status["processes"]:
                message += (
                    f"{process['name']} — "
                    f"{process['memory_mb']:.1f} MB\n"
                )

            await context.bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=message,
                parse_mode=ParseMode.HTML,
            )

            ram_alert_active = True

            logger.warning(
                "RAM critical alert sent"
            )

        if not ram_critical and ram_alert_active:
            await context.bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=(
                    "✅ <b>RAM RECOVERED</b>\n\n"
                    "RAM usage critical holatdan qaytdi."
                ),
                parse_mode=ParseMode.HTML,
            )

            ram_alert_active = False

            logger.info(
                "RAM recovered"
            )

        if disk_critical and not disk_alert_active:
            disk = status["disk"]

            detailed_status = get_server_status()

            message = (
                "🚨 <b>DISK CRITICAL</b>\n\n"
                f"Usage: {disk['percent']:.1f}%\n"
                f"Used: {format_bytes(disk['used'])}\n"
                f"Free: {format_bytes(disk['free'])}\n\n"
                "📁 <b>LARGEST DIRECTORIES</b>\n"
            )

            for path, size in (
                detailed_status[
                    "largest_directories"
                ]
            ):
                message += (
                    f"<code>{path}</code> — "
                    f"{format_bytes(size)}\n"
                )

            await context.bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=message,
                parse_mode=ParseMode.HTML,
            )

            disk_alert_active = True

            logger.warning(
                "Disk critical alert sent"
            )

        if not disk_critical and disk_alert_active:
            await context.bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=(
                    "✅ <b>DISK RECOVERED</b>\n\n"
                    "Disk usage critical holatdan qaytdi."
                ),
                parse_mode=ParseMode.HTML,
            )

            disk_alert_active = False

            logger.info(
                "Disk recovered"
            )

    except Exception:
        logger.exception(
            "Failed to check server alerts"
        )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "Telegram update caused an error",
        exc_info=context.error,
    )


def main():
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(startup_message)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "status",
            status_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "ram",
            ram_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "disk",
            disk_handler,
        )
    )

    application.add_error_handler(
        error_handler
    )

    application.job_queue.run_repeating(
        send_report,
        interval=REPORT_INTERVAL_HOURS * 60 * 60,
        first=10,
        name="server-report",
    )

    application.job_queue.run_repeating(
        check_server_alerts,
        interval=ALERT_CHECK_INTERVAL_SECONDS,
        first=30,
        name="server-alerts",
    )

    application.job_queue.run_repeating(
        send_cleanup_report,
        interval=2 * 24 * 60 * 60,
        first=60,
        name="server-cleanup",
    )

    logger.info(
        "Server Monitor starting..."
    )

    application.run_polling()

async def send_cleanup_report(
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        returncode, output = await run_cleanup()

        if returncode == 0:
            message = (
                "🧹 <b>SERVER CLEANUP</b>\n\n"
                f"<pre>{output}</pre>"
            )
        else:
            message = (
                "❌ <b>CLEANUP FAILED</b>\n\n"
                f"<pre>{output}</pre>"
            )

        await context.bot.send_message(
            chat_id=TELEGRAM_GROUP_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )

        logger.info(
            "Cleanup report sent"
        )

    except Exception:
        logger.exception(
            "Failed to run cleanup"
        )

if __name__ == "__main__":
    main()
