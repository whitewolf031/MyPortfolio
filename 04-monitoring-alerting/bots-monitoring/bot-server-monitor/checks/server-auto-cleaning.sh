#!/bin/bash

# Xatolar butun scriptni to'xtatib qo'ymasligi uchun pipefail saqlanadi
set -uo pipefail

#----Kerakli o'zgaruvchilar----
LOG_DIR='/var/log'
TMP_DIR='/tmp'

#---Tozalash kunlari (standart 5 kunlik)---
MAX_DAYS="${CLEAN_DAYS:-5}"

#---Disk limit foizi---
DISK_LIMIT="${DISK_LIMIT:-80}"

echo "=========================================="
echo "🧹 SERVERNI TOZALASH (${MAX_DAYS} KUNLIK)"
echo "Vaqt: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

DISK_BEFORE=$(df -h / | awk 'NR==2 {print $3 " / " $2 " (" $5 ")"}')
echo "💾 Disk bandligi (tozalashdan oldin): $DISK_BEFORE"
echo ""

#-------1. tmp fayllarni tozalash--------
echo "[1/4] Eski /tmp fayllar (>${MAX_DAYS} kunlik) tozalanmoqda..."
TMP_COUNT=$(find "$TMP_DIR" -type f -mtime +"$MAX_DAYS" 2>/dev/null | wc -l)
if [ "$TMP_COUNT" -gt 0 ]; then
    TMP_SIZE=$(find "$TMP_DIR" -type f -mtime +"$MAX_DAYS" -exec du -ch {} + 2>/dev/null | tail -n 1 | awk '{print $1}')
else
    TMP_SIZE="0B"
fi

find "$TMP_DIR" -type f -mtime +"$MAX_DAYS" -delete 2>/dev/null || true
echo "  -> Natija: $TMP_COUNT ta fayl tozalandi (hajmi: ${TMP_SIZE:-0B})"

#-------2. Eski log fayllarni tozalash-------
echo "[2/4] Eski /var/log fayllar (>${MAX_DAYS} kunlik) tozalanmoqda..."
LOG_COUNT=$(find "$LOG_DIR" -type f \( -name "*.log" -o -name "*.log.*" -o -name "*.gz" \) -mtime +"$MAX_DAYS" 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    LOG_SIZE=$(find "$LOG_DIR" -type f \( -name "*.log" -o -name "*.log.*" -o -name "*.gz" \) -mtime +"$MAX_DAYS" -exec du -ch {} + 2>/dev/null | tail -n 1 | awk '{print $1}')
else
    LOG_SIZE="0B"
fi

find "$LOG_DIR" \
     -type f \
     \( -name "*.log" -o -name "*.log.*" -o -name "*.gz" \) \
     -mtime +"$MAX_DAYS" \
     -delete 2>/dev/null || true
echo "  -> Natija: $LOG_COUNT ta log fayl tozalandi (hajmi: ${LOG_SIZE:-0B})"

#-------3. systemd journal loglarini tozalash--------
echo "[3/4] Systemd journal loglari (${MAX_DAYS} kunlik vakuum)..."
if command -v journalctl >/dev/null 2>&1; then
    JOURNAL_RES=$(journalctl --vacuum-time="${MAX_DAYS}d" 2>&1 | tail -n 2 || true)
    echo "  -> $JOURNAL_RES"
else
    echo "  -> journalctl topilmadi, o'tkazib yuborildi."
fi

#-------4. Paket keshlarini tozalash--------
echo "[4/4] Paket keshlar tozalanmoqda (apt-get clean)..."
if command -v apt-get >/dev/null 2>&1; then
    apt-get clean 2>/dev/null || true
    echo "  -> apt-get clean bajarildi."
else
    echo "  -> apt-get mavjud emas."
fi

echo ""
echo "=========================================="
echo "📊 SERVER HOLATI (TOZALASHDAN SO'NG)"
echo "=========================================="

DISK_AFTER=$(df -h / | awk 'NR==2 {print $3 " / " $2 " (" $5 ")"}')
echo "💾 Disk: $DISK_AFTER"

echo "🧠 RAM:"
free -h | awk 'NR<=2 {print $0}'

echo "⚙️ CPU va Uptime:"
uptime

DISK_USAGE=$(df / | awk 'NR==2 {gsub("%", ""); print $5}')

echo ""
if [ "$DISK_USAGE" -ge "$DISK_LIMIT" ]; then 
    echo "⚠️ OGOHLANTIRISH: Disk bandligi kritik darajada: ${DISK_USAGE}%!"
else
    echo "✅ Disk holati me'yorda: ${DISK_USAGE}%"
fi

echo ""
echo "✅ ${MAX_DAYS} kunlik tozalash yakunlandi: $(date '+%Y-%m-%d %H:%M:%S')"
