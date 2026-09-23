# 🚀 MyPortfolio — DevOps & Infrastructure Engineering

Hush kelibsiz! Ushbu repozitoriyda mening **DevOps**, **Linux tizim ma'murchiligi** va **Infrastruktura avtomatlashtirish** bo'yicha amaliy tajribam, real loyihalarim hamda avtomatlashtirgan yechimlarim jamlangan. 

Bu yerda zamonaviy microservice arxitekturalarini konteynerlashtirishdan tortib, avtomatik deploy va serverlar monitoringigacha bo'lgan to'liq DevOps tsiklini ko'rishingiz mumkin.

---

## 🛠 Loyihalar va Avtomatlashtirilgan Yechimlar (Projects & Solutions)

### 1. 🐳 Docker & Docker Compose
DevOps faoliyatimda ilovalarni izolyatsiya qilish, konteynerlashtirish va muhitlar orasidagi muvofiqlikni ta'minlash uchun Docker texnologiyalaridan unumli foydalanaman. Ushbu bo'limda mikservis ilovalarni izolyatsiyalangan muhitda ishga tushirish, hajmlar (volumes) va tarmoqlar (networks) bilan ishlash hamda ko'p konteynerli arxitekturalarni orchestrate qilish bo'yicha yozilgan loyihalarim o'rin olgan.

* 🔗 **Kodlar va manba:** [`01-docker-and-compose`](https://github.com/user-user/MyPortfolio/tree/main/01-docker-and-compose)

---

### 2. 🚀 CI/CD Pipelines (GitHub Actions)
Manual deploy jarayonlarini nolga tushirish va kod o'zgarishlarini avtomatik ravishda sinovdan o'tkazib, production serverga xavfsiz yetkazib berish (Auto-Deploy) uchun qurilgan CI/CD konveyerlari. Pipeline'lar orqali kod tekshiruvi (linting), build va deployment bosqichlari to'liq avtomatlashtirilgan.

* 🔗 **Kodlar va manba:** [`02-ci-cd-pipelines`](https://github.com/user-user/MyPortfolio/tree/main/02-ci-cd-pipelines)

---

### 3. ☸️ Kubernetes & GitOps Orchestration
Yuqori yuklamali va keshlanadigan tizimlarni boshqarish, avtomatik masshtablashtirish (scaling) hamda resurslarni to'g'ri taqsimlash uchun tayyorlangan Production-ready Kubernetes manifestlari va Helm chartlar. Tizimning uzluksiz ishlashini (High Availability) ta'minlash bo'yicha amaliy yechimlar.

* 🔗 **Kodlar va manba:** [`03-kubernetes-gitops`](https://github.com/user-user/MyPortfolio/tree/main/03-kubernetes-gitops)

---

### 4. 🤖 Server Automation & Monitoring
Linux (Ubuntu/Hetzner) serverlaridagi muhim resurslarni (RAM, CPU, Disk) doimiy nazorat qilib turuvchi monitoring va avtomatik tozalash tizimlari. Serverda muammo yuzaga kelganda darhol Telegram bot orqali ogohlantirish beruvchi hamda tizim xotirasini avtomatik tartibga soluvchi skriptlar jamlanmasi.

* 🔗 **Kodlar va manba:** [`04-monitoring-alerting`](https://github.com/user-user/MyPortfolio/tree/main/04-monitoring-alerting)

---

## 💻 Asosiy Texnologiyalar va Vositalar (Tech Stack)

| Soha | Ishlatilgan Texnologiyalar |
|---|---|
| **OS & Administration** | Linux (Ubuntu, Hetzner), Bash Shell, SSH, Systemd |
| **Containers & Orchestration** | Docker, Docker Compose, Kubernetes |
| **CI/CD** | GitHub Actions |
| **Monitoring & Alerting** | Python (Asyncio, APScheduler), Telegram Bot API, System Logs (`journalctl`) |
| **Backend & Databases** | Python (Django), Node.js, PostgreSQL |

---

## 📌 Loyiha kodlarini ko'rish

Har bir loyihaning to'liq kodi va konfiguratsiya fayllari bilan tanishish uchun quyidagi havola orqali repozitoriyning asosiy manbasiga o'tishingiz mumkin:

👉 **[MyPortfolio barcha kodlarini ko'rish](https://github.com/user-user/MyPortfolio)**
