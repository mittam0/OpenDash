# OpenDash

Веб-сервис дашбордов на Streamlit с авторизацией, гибкими блоками и подключением к базам данных через SQLAlchemy.

## Возможности

- **Авторизация** — вход по логину/паролю, админ создаёт пользователей
- **Дашборд** — до 4 блоков на пользователя, каждый блок сворачивается/разворачивается
- **Типы блоков:** график (Plotly), таблица, сводная таблица, карточка значения
- **Источники данных:** SQL-запрос к любому коннектору (SQLAlchemy) или загрузка CSV/XLSX
- **Коннекторы** — администратор добавляет подключения к PostgreSQL, MySQL, MSSQL, SQLite и др.
- **Обновление** — кнопка "Обновить" + настраиваемый интервал автообновления (в секундах)
- **Каждому пользователю** — своя конфигурация блоков

## Быстрый старт

```powershell
git clone <repo>
cd OpenDash
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\streamlit run main.py
```

Открыть в браузере: http://localhost:8501

**Логин по умолчанию:** `adm` / `adm`

## Структура проекта

```
OpenDash/
├── main.py                     # Точка входа
├── requirements.txt            # Зависимости
├── app/
│   ├── config.py               # Конфигурация
│   ├── database.py             # SQLite, создание таблиц
│   ├── models.py               # CRUD для users, connectors, blocks
│   ├── auth.py                 # Хеширование паролей, login/logout
│   ├── seed.py                 # Первичное заполнение (admin, main connector)
│   ├── pages/
│   │   ├── login.py            # Страница входа
│   │   ├── dashboard.py        # Основная панель с блоками
│   │   └── admin.py            # Админка (пользователи + коннекторы)
│   ├── components/
│   │   ├── chart_block.py      # График (Plotly)
│   │   ├── table_block.py      # Таблица
│   │   ├── pivot_block.py      # Сводная таблица
│   │   └── value_card.py       # Карточка значения
│   └── utils/
│       ├── data_source.py      # Загрузка данных (SQL / файл)
│       ├── query_executor.py   # Безопасное выполнение SQL
│       └── upsert_data.py      # Загрузка DataFrame в БД с дедупликацией
└── uploads/                    # Папка для загруженных файлов
```

## База данных

Системная БД — SQLite (`opendash.db`), создаётся автоматически при первом запуске.

### Таблицы

- **users** — пользователи (username, password_hash, role)
- **connectors** — подключения к БД (name, engine, connection_string)
- **blocks** — блоки дашборда (user_id, block_type, config, position и др.)

## Upsert данных

Скрипт для загрузки DataFrame в любую таблицу через SQLAlchemy:

```python
from app.utils.upsert_data import upsert_table

upsert_table(df, "table_name", dup_columns=["id", "date"])
```

CLI:

```powershell
python -m app.utils.upsert_data --table sales --file data.csv --dup_columns date product
```
