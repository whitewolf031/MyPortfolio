#!/bin/bash

set -Eeuo pipefail

# Telegram sozlamalari
source /home/ubuntu/zaxrodenta_backup/.telegram-backup.env

# Docker container va db ma'lumotlari
container="zahro_dental_dev"
db_name="zahro_dental_dev"
db_user="postgres"

# Backup manzili
backup_dir="/home/ubuntu/zaxrodenta_backup"

# Backup file nomi
date=$(date +%d-%m-%Y)
backup_file="$backup_dir/zaxrodenta_backup-$date.sql"
temp_file="$backup_file.tmp"

# telegramga xabar jo'natish
telegram_send() {
	local message="$1"
	if ! curl --silent --show-error --fail \
		--connect-timeout 10 --max-time 20 \
		--request POST \
		"https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
		--data-urlencode "chat_id=${CHAT_ID}" \
                --data-urlencode "message_thread_id=${TOPIC_ID}" \
                --data-urlencode "text=${message}" \
		> /dev/null; then
		echo "XATO: Telegram xabari yuborilmadi!" >&2
	fi
	
	return 0
}

on_error() {
	local status="$1"
	local line="$2"

	trap - ERR
	rm -f -- "${temp_file:-}"
	telegram_send "❌ Error: ZaxroDental backup olishda muomo!
		📅 Sana: $(date '+%d-%m-%Y %H:%M:%S')
		🗄 Database: ${db_name}
		🖥 Container: ${container}
		⚠️ Exit code: ${status}
		📍 Script line: ${line}" || true
	
	echo "Backup xatosi: exit=$status, line=$line" >&2
	exit "$status"
}

trap 'on_error "$?" "$LINENO"' ERR

# Papka mavjud bo'lmasa yaratish
mkdir -p "$backup_dir"

# Database dan backup olish
docker exec "$container" \
	pg_dump -U "$db_user" "$db_name" > "$temp_file"

# Bo'sh file ga tekshiramiz
test -s "$temp_file"

mv -f -- "$temp_file" "$backup_file"

size=$(du -h "$backup_file" | cut -f1)

# Telegramga xush xabar
telegram_send "✅ Zaxrodental backup muvafaqiyatli yaratildi
📅 Sana: ${date}
🗄 Database: ${db_name}
📁 Fayl: $(basename "$backup_file")
💾 Hajmi: ${size}
📍 Manzil: ${backup_file}"

echo "Backup muvafaqiyatli yaratildi: $backup_file"
