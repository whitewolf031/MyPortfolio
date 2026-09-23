#!/bin/bash

set -euo pipefail

#----kerakli-o'zgaruvchilar----
LOG_DIR='/var/log'
TMP_DIR='/tmp'

#---max-kun---
MAX_DAYS=7

#---disk-limit---
DISK_LIMIT=80

echo "-----------------------------"
echo "Server tozalash boshlandi"
echo " $(date)"
echo "-----------------------------"

#-------tmp file larni tozalash--------
echo "[1/5] Eski tmp file lar tozalanmoqda..."

find "$TMP_DIR" -type f -mtime +"$MAX_DAYS" -delete 2>/dev/null || true

#-------Eski log file lar tozalash-------
echo "[2/5] Eski log file lar tozalanmoqda..."

find "$LOG_DIR" \
     -type f \
     \( -name "*.log" -o -name "*.log.*" \) \
     -mtime +"$MAX_DAYS" \
     -delete 2>/dev/null || true

#-------systemd log larni tozalaymiz--------
echo "[3/5] Eski systemd log larni tozalanmoqda..."

if command -v journalctl >/dev/null 2>&1; 
then journalctl --vacuum-time=7d
fi

#-------Packet cache larni tozalash--------
echo "[4/5] Packed cache tozalanmoqda..."

if command -v apt-get >/dev/null 2>&1;
then apt-get clean
fi

#-------Server holatini tekshirish--------
echo "[5/5] Server holatini tekshirish:"

echo "Disk:"
df -h /

echo "RAM:"
free -h

echo "CPU holati:"
uptime

echo "Eng ko'p RAM ishlatyotgan jarayonlar"
ps aux --sort=-%mem | head -6

echo "CPU eng ko'p ishlatyotgan jarayonlar"
ps aux --sort=-%cpu | head -6

DISK_USAGE=$(df / | awk 'NR==2 {gsub("%", ""); print $5}')

echo ""

if [ "$DISK_USAGE" -ge "$DISK_LIMIT" ];then 
	echo "WARNING: Disk holati: ${DISK_USAGE}%!"
else
     echo "Disk holati: ${DISK_USAGE}%"
fi

echo ""
echo "Tozalash tugadi"
echo "$(date '+%Y-%m-%d %H:%M:%S')"
