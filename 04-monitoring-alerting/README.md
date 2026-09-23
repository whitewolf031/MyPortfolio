# ⚡ Server Automation & Monitoring Tools

Ushbu bo'limda mening Linux infrastrukturasini avtomatlashtirish, Hetzner serverlarini Infrastructure as Code (IaC) orqali boshqarish, Prometheus monitoring tizimini sozlash hamda avtomatik Telegram-bot xabarnomalarini yo'lga qo'yish bo'yicha amaliy va qo'shimcha skriptlarim jamlangan.

---

## 🛠 Avtomatlashtirish Bo'limlari va Skriptlar

### 1. 📜 Bash Automation Scripts
Linux serverlarida kunlik va takrorlanuvchi operatsiyalarni avtomatlashtirish, foydalanuvchilarni boshqarish, zaxira (backup) nusxalarini olish va tizim jurnallarini (logs) tozalash uchun yozilgan samarali Bash skriptlar to'plami.

* 🔗 **Kodlar va manba:** [`bash-scripts`](https://github.com/whitewolf031/MyPortfolio/tree/main/04-monitoring-alerting/bash-scripts)

---

### 2. 🤖 Bot Monitoring & Alerting
Serverdagi jarayonlarni, disk xotirasi holatini hamda RAM yuklamasini real vaqt rejimida nazorat qilib turuvchi va favqulodda holatlar (critical alerts) haqida Telegram orqali xabar beruvchi avtomatik Python/Bot xizmatlari.

* 🔗 **Kodlar va manba:** [`bots-monitoring`](https://github.com/whitewolf031/MyPortfolio/tree/main/04-monitoring-alerting/bots-monitoring)

---

### 3. 🏗️ Hetzner Infrastructure as Code (Terraform)
Hetzner Cloud server resurslarini (VPS/Cloud instances, SSH kalitlar, tarmoq va xavfsizlik devorlari) kod orqali avtomatik yaratish va boshqarish imkonini beruvchi Terraform konfiguratsiya fayllari.

* 🔗 **Kodlar va manba:** [`hetzner-terraform`](https://github.com/whitewolf031/MyPortfolio/tree/main/04-monitoring-alerting/hetzner-terraform)

---

### 4. 📊 Prometheus & Metrics Monitoring
Serverlar va konteynerlarning metritsalarini yig'ish, tizim yuklamasini tahlil qilish hamda monitoring vizualizatsiyasi uchun sozlangan Prometheus konfiguratsiyalari.

* 🔗 **Kodlar va manba:** [`monitoring/prometheus`](https://github.com/whitewolf031/MyPortfolio/tree/main/04-monitoring-alerting/monitoring)

---

## 💻 Qo'llanilgan Texnologiyalar

| Yo'nalish | Asosiy Vositalar |
|---|---|
| **Scripting & Shell** | Bash Shell, Python |
| **Infrastructure as Code** | Terraform (Hetzner Cloud Provider) |
| **Monitoring & Metrics** | Prometheus, System Metrics, Journalctl Logs |
| **Notifications** | Telegram Bot API (Asyncio, APScheduler) |

---

## 📌 Barcha skriptlarni ko'rish

Bo'limdagi barcha avtomatlashtirish manba kodlarini quyidagi havola orqali ko'rishingiz mumkin:

👉 **[Avtomatlashtirilgan jarayonlar kodlarini ko'rish](https://github.com/whitewolf031/MyPortfolio)**
