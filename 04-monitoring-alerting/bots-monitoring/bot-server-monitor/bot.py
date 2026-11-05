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
    SERVER_TOPIC_ID,
    CLEANUP_TOPIC_ID,
    RAM_CRITICAL,
    DISK_CRITICAL,
    CPU_CRITICAL,
    REPORT_INTERVAL_HOURS,
    ALERT_CHECK_INTERVAL_SECONDS,
    CLEANUP_INTERVAL_DAYS,
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
cpu_alert_active = False


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


async def send_to_telegram(
    bot,
    text: str,
    topic_id: int | None = None,
    chat_id: str | int = TELEGRAM_GROUP_ID,
):
    kwargs = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": ParseMode.HTML,
    }
    if topic_id is not None:
        kwargs["message_thread_id"] = topic_id

    return await bot.send_message(**kwargs)


def format_status(status):
    memory = status["memory"]
    disk = status["disk"]
    cpu = status.get("cpu")

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
        "💾 <b>SSD / DISK</b>",
        (
            f"Used: {format_bytes(disk['used'])} / "
            f"{format_bytes(disk['total'])}"
        ),
        f"Usage: {disk['percent']:.1f}%",
        f"Free: {format_bytes(disk['free'])}",
    ]

    if cpu:
        message.extend(
            [
                "",
                "⚙️ <b>CPU</b>",
                f"Usage: {cpu['percent']:.1f}%",
                (
                    f"Cores: {cpu['logical_cores']} "
                    f"({cpu['physical_cores']} physical)"
                ),
                (
                    f"Load Avg (1m, 5m, 15m): "
                    f"{cpu['load_1m']:.2f}, "
                    f"{cpu['load_5m']:.2f}, "
                    f"{cpu['load_15m']:.2f}"
                ),
            ]
        )

    message.extend(
        [
            "",
            "🔥 <b>TOP RAM PROCESSES</b>",
        ]
    )

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
        "💾 <b>SSD / DISK STATUS</b>",
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


def format_cpu(status):
    cpu = status["cpu"]
    cpu_processes = status.get("cpu_processes", [])

    message = [
        "⚙️ <b>CPU STATUS</b>",
        "",
        f"Usage: {cpu['percent']:.1f}%",
        f"Logical Cores: {cpu['logical_cores']}",
        f"Physical Cores: {cpu['physical_cores']}",
        (
            f"Load Avg (1m, 5m, 15m): "
            f"{cpu['load_1m']:.2f}, "
            f"{cpu['load_5m']:.2f}, "
            f"{cpu['load_15m']:.2f}"
        ),
    ]

    if cpu.get("freq") and cpu["freq"].get("current"):
        message.append(
            f"Frequency: {cpu['freq']['current']:.0f} MHz"
        )

    if cpu_processes:
        message.extend(
            [
                "",
                "⚡ <b>TOP CPU PROCESSES</b>",
            ]
        )
        for index, process in enumerate(cpu_processes, start=1):
            message.append(
                f"{index}. {process['name']} "
                f"(<code>{process['pid']}</code>) — "
                f"{process['cpu_percent']:.1f}%"
            )

    return "\n".join(message)


async def startup_message(
    application: Application,
):
    await send_to_telegram(
        application.bot,
        text=(
            "🚀 <b>server-monitoring bot</b> ishga tushdi.\n"
            f"Server: <code>{socket.gethostname()}</code>"
        ),
        topic_id=SERVER_TOPIC_ID,
    )


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    await update.message.reply_text(
        "🤖 <b>Server Monitor Bot</b>\n\n"
        "Mavjud buyruqlar:\n"
        "/status - Server umumiy holati (RAM, SSD, CPU)\n"
        "/ram - RAM xotira holati\n"
        "/cpu - CPU protsessor holati\n"
        "/disk - SSD / Disk holati\n"
        "/cleanup - 5 kunlik tozalashni bajarish",
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


async def cpu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    status = get_server_status()

    await update.message.reply_text(
        format_cpu(status),
        parse_mode=ParseMode.HTML,
    )


async def cleanup_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    wait_msg = await update.message.reply_text(
        "🧹 <b>Server tozalash boshlandi (5 kunlik)...</b>",
        parse_mode=ParseMode.HTML,
    )

    returncode, output = await run_cleanup()

    # Telegram xabar limiti (4096 belgi) oshib ketmasligi uchun
    safe_output = output[-3500:] if len(output) > 3500 else output

    if returncode == 0:
        header = "🧹 <b>SERVER TOZALANDI (5 KUNLIK)</b>\n\n"
    else:
        header = "⚠️ <b>TOZALASHDA XATOLIK</b>\n\n"

    message = f"{header}<pre>{safe_output}</pre>"

    await wait_msg.edit_text(
        message,
        parse_mode=ParseMode.HTML,
    )


async def send_report(
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        status = get_server_status()

        await send_to_telegram(
            context.bot,
            text=format_status(status),
            topic_id=SERVER_TOPIC_ID,
        )

        logger.info(
            "Server report sent to topic %s",
            SERVER_TOPIC_ID,
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
    global cpu_alert_active

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

        cpu_critical = any(
            alert["type"] == "CPU_CRITICAL"
            for alert in alerts
        )

        # --- RAM ALERT ---
        if ram_critical and not ram_alert_active:
            memory = status["memory"]
            detailed_status = get_server_status()

            message = (
                "🚨 <b>RAM CRITICAL</b>\n\n"
                f"Usage: {memory['percent']:.1f}%\n"
                f"Used: {format_bytes(memory['used'])}\n"
                f"Total: {format_bytes(memory['total'])}\n"
                f"Limit: {RAM_CRITICAL}%\n\n"
                "🔥 <b>TOP RAM PROCESSES</b>\n"
            )

            for process in detailed_status["processes"]:
                message += (
                    f"{process['name']} — "
                    f"{process['memory_mb']:.1f} MB\n"
                )

            await send_to_telegram(
                context.bot,
                text=message,
                topic_id=SERVER_TOPIC_ID,
            )

            ram_alert_active = True
            logger.warning("RAM critical alert sent")

        if not ram_critical and ram_alert_active:
            await send_to_telegram(
                context.bot,
                text=(
                    "✅ <b>RAM RECOVERED</b>\n\n"
                    "RAM usage critical holatdan qaytdi."
                ),
                topic_id=SERVER_TOPIC_ID,
            )

            ram_alert_active = False
            logger.info("RAM recovered")

        # --- DISK ALERT ---
        if disk_critical and not disk_alert_active:
            disk = status["disk"]
            detailed_status = get_server_status()

            message = (
                "🚨 <b>DISK CRITICAL</b>\n\n"
                f"Usage: {disk['percent']:.1f}%\n"
                f"Used: {format_bytes(disk['used'])}\n"
                f"Free: {format_bytes(disk['free'])}\n"
                f"Limit: {DISK_CRITICAL}%\n\n"
                "📁 <b>LARGEST DIRECTORIES</b>\n"
            )

            for path, size in detailed_status["largest_directories"]:
                message += (
                    f"<code>{path}</code> — "
                    f"{format_bytes(size)}\n"
                )

            await send_to_telegram(
                context.bot,
                text=message,
                topic_id=SERVER_TOPIC_ID,
            )

            disk_alert_active = True
            logger.warning("Disk critical alert sent")

        if not disk_critical and disk_alert_active:
            await send_to_telegram(
                context.bot,
                text=(
                    "✅ <b>DISK RECOVERED</b>\n\n"
                    "Disk usage critical holatdan qaytdi."
                ),
                topic_id=SERVER_TOPIC_ID,
            )

            disk_alert_active = False
            logger.info("Disk recovered")

        # --- CPU ALERT ---
        if cpu_critical and not cpu_alert_active:
            cpu = status["cpu"]
            detailed_status = get_server_status()

            message = (
                "🚨 <b>CPU CRITICAL</b>\n\n"
                f"Usage: {cpu['percent']:.1f}%\n"
                f"Limit: {CPU_CRITICAL}%\n"
                f"Load Avg: {cpu['load_1m']:.2f}, {cpu['load_5m']:.2f}, {cpu['load_15m']:.2f}\n\n"
                "⚡ <b>TOP CPU PROCESSES</b>\n"
            )

            for process in detailed_status["cpu_processes"]:
                message += (
                    f"{process['name']} (PID: {process['pid']}) — "
                    f"{process['cpu_percent']:.1f}%\n"
                )

            await send_to_telegram(
                context.bot,
                text=message,
                topic_id=SERVER_TOPIC_ID,
            )

            cpu_alert_active = True
            logger.warning("CPU critical alert sent")

        if not cpu_critical and cpu_alert_active:
            await send_to_telegram(
                context.bot,
                text=(
                    "✅ <b>CPU RECOVERED</b>\n\n"
                    "CPU usage critical holatdan qaytdi."
                ),
                topic_id=SERVER_TOPIC_ID,
            )

            cpu_alert_active = False
            logger.info("CPU recovered")

    except Exception:
        logger.exception(
            "Failed to check server alerts"
        )


async def send_cleanup_report(
    context: ContextTypes.DEFAULT_TYPE,
):
    try:
        returncode, output = await run_cleanup()

        # Telegram xabar limiti (4096 belgi) oshib ketmasligi uchun
        safe_output = output[-3500:] if len(output) > 3500 else output

        if returncode == 0:
            message = (
                "🧹 <b>SERVER CLEANUP (5 KUNLIK)</b>\n\n"
                f"<pre>{safe_output}</pre>"
            )
        else:
            message = (
                "⚠️ <b>CLEANUP FAILED</b>\n\n"
                f"<pre>{safe_output}</pre>"
            )

        await send_to_telegram(
            context.bot,
            text=message,
            topic_id=CLEANUP_TOPIC_ID,
        )

        logger.info(
            "Cleanup report sent to topic %s",
            CLEANUP_TOPIC_ID,
        )

    except Exception:
        logger.exception(
            "Failed to run cleanup"
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

    application.add_handler(
        CommandHandler(
            "ssd",
            disk_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "cpu",
            cpu_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "cleanup",
            cleanup_command_handler,
        )
    )

    application.add_handler(
        CommandHandler(
            "clean",
            cleanup_command_handler,
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
        interval=CLEANUP_INTERVAL_DAYS * 24 * 60 * 60,
        first=60,
        name="server-cleanup",
    )

    logger.info(
        "Server Monitor starting..."
    )

    application.run_polling()


if __name__ == "__main__":
    main()
