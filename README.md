# 🦅 TrumpBot - Advanced Telegram Battle Bot

> ⚡ A modern Telegram bot for group-based PvP missile combat
> 🚀 Built with async Python, PostgreSQL, and bilingual (FA/EN) support


<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11-blue?logo=python"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/Postgres-12+-blue?logo=postgresql"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green"></a>
  <img src="https://img.shields.io/github/stars/bettercallninja/TrumpBot?style=social">
</p>

---

## ✨ Features

### 🎮 Core Gameplay
- **PvP Combat System**: Reply-based attacks with advanced damage calculations
- **Weapons Arsenal**: Multiple types with unique damage & effects
- **Defense Systems**: Shields and interceptors with cooldowns
- **Level-based Progression**: Dynamic XP, levels, and scaling
- **Real-time Status**: HP tracking, defenses, and cooldown management

### 💎 Premium Features
- **Telegram Stars Shop**: Buy premium items with TG Stars
- **Medal Economy**: Earn rewards via gameplay & activity
- **Inventory System**: Store & use items with logging
- **Daily Bonuses**: Keep engagement alive

### ⚙️ Technical Excellence
- **Async-first**: Full async/await implementation
- **Connection Pooling**: `psycopg-pool` for PostgreSQL
- **Bilingual**: English + فارسی with per-user settings
- **Type Hints**: Static safety across the codebase
- **Error Handling**: Robust exception management & user feedback
- **Modular Design**: Commands, DB, utils, handlers separated

---

## 🏗 Architecture

<details>
<summary>View Code Structure</summary>

```tree
TrumpBot/
 ├── main.py
 ├── src/
 │   ├── app.py
 │   ├── commands/       # attack, general, status, ...
 │   ├── config/         # BotConfig, items
 │   ├── database/       # DBManager with pooling
 │   ├── handlers/       # event handlers
 │   ├── utils/          # helpers, translations
 │   └── __init__.py
 ├── pyproject.toml
 └── README.md
```
</details>

- Manager pattern for clean game logic
- Dependency injection for flexibility
- Factory pattern for bot creation
- Full type-hints & structured logging

---

## 🚀 Quick Start

### Prerequisites
- Python **3.8+**
- PostgreSQL **12+**
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Installation
```bash
git clone <repository-url>
cd TrumpBot
pip install -r requirements.txt
```

### Configuration
Create `.env` file:
```env
BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:pass@localhost:5432/trumpbot
UNLIMITED_MISSILES=false
LOG_LEVEL=INFO
```

### Run
```bash
python main.py
```

For production:
```bash
python main.py > bot.log 2>&1 &
```

---

## 🎮 Commands

| Command      | Action                          |
|--------------|---------------------------------|
| `/start`     | Welcome & main menu             |
| `/help`      | Show full help                  |
| `/language`  | Switch EN/FA                    |
| `/status`    | Show player HP & defenses       |
| `/shield`    | Quick shield activation         |
| `/attack`    | Attack (reply or weapon select) |
| `/shop`      | Buy items                       |
| `/inventory` | Show & manage items             |
| `/stars`     | Premium shop (TG Stars)         |
| `/stats`     | Combat statistics               |

---

## 🔒 Security & Performance

- Parameterized SQL → **safe from injection**
- Connection pooling → **efficient DB usage**
- Rate-limiting → **fair gameplay**
- Graceful degradation → **bot never crashes**

---

## 🛡 Deployment

<details>
<summary>Dockerfile</summary>

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```
</details>

---

## 🤝 Contributing

1. Fork repo & create branch
2. Add feature with type hints + docs
3. Open PR with description

---

## 📞 Support

Telegram: [@bettercallninja](https://t.me/bettercallninja)

---

## 📜 License

MIT © [bettercallninja](https://github.com/bettercallninja)