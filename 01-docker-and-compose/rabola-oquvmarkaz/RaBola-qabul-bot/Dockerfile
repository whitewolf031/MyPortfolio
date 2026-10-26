FROM python:3.11-slim

# Muhit o'zgaruvchilari: Python bufferini o'chirish (loglar darhol ko'rinishi uchun)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Tizim paketlarini yangilash
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ishchi katalogni o'rnatish
WORKDIR /app

# Avval requirements faylni nusxalash (Docker layer keshidan unumli foydalanish)
COPY requirements.txt .

# Kutubxonalarni o'rnatish
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Loyiha kodlarini nusxalash
COPY . .

# Botni ishga tushirish
CMD ["python", "bot.py"]