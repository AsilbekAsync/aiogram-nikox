# Aiogram Start Template

Async Telegram bot starter with aiogram 3.x + MySQL + Alembic.

## Features

- **aiogram 3.x** — async Telegram Bot API
- **SQLAlchemy 2.0 + asyncmy** — async MySQL
- **Alembic** — database migrations
- **Custom FSM storage** — MySQL-backed
- **YAML texts** — localization ready
- **VSCode** — pre-configured

## Quick Start

```bash
# 1. Clone and setup venv
python3 -m venv .venv
source .venv/bin/activate
pip install aiogram sqlalchemy asyncmy python-dotenv pyyaml alembic

# 2. Configure
cp .env.example .env
# Edit .env: set BOT_TOKEN and MySQL credentials

# 3. Create database
mysql -u root -e "CREATE DATABASE IF NOT EXISTS aiogram_start CHARACTER SET utf8mb4"

# 4. Run
python main.py
```

## Project Structure

```
├── main.py                 # Entry point — migrations, tables, polling
├── config.py               # .env loader (BOT_TOKEN, DATABASE_URL)
├── handlers/               # Message handlers
│   ├── start.py            # /start command
│   └── unknown.py          # Unknown messages
├── keyboards/              # Reply/Inline keyboards
│   └── default.py          # Main menu builder
├── states/                 # FSM states
│   ├── storage.py          # MySQL-backed FSM storage
│   └── registration.py     # Example registration flow
├── models/                 # SQLAlchemy ORM models
│   ├── user.py             # Telegram user
│   └── fsm.py              # FSM states table
├── database/               # DB layer
│   ├── engine.py           # Async engine + session factory
│   └── base.py             # DeclarativeBase
├── texts/                  # Localization (YAML)
│   ├── loader.py           # Text loader: load("uz", "messages")
│   └── uz/
│       ├── messages.yaml   # Bot messages
│       └── labels.yaml     # Button labels
├── alembic/                # Database migrations
│   ├── env.py              # Async engine config
│   └── versions/           # Migration files
├── alembic.ini
├── .env.example
├── pyproject.toml
└── .vscode/                # Python path, debug config
```

## Adding a New Handler

```python
# handlers/help.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from texts.loader import load

t = load("uz")
router = Router()

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(t["help"])
```

Then register in `main.py`:

```python
from handlers.help import router as help_router
dp.include_router(help_router)
```

## Adding a New Language

```bash
mkdir texts/en
cp texts/uz/messages.yaml texts/en/messages.yaml
# Translate texts/en/messages.yaml
```

Then use: `t = load("en")`

## Creating Migrations

```bash
# After changing models
alembic revision --autogenerate -m "add new column"
alembic upgrade head
```

## License

MIT
