# BI Multi-Agent System

Набор LLM‑агентов для генерации и выполнения SQL‑запросов, выбора типов графиков и подготовки данных для визуализации.

---

##  Структура проекта

```
.
├── chart-agent/                 # Сервис генерации визуализаций
│   ├── agents/
│   │   ├── chart_data_agent.py     # Подготовка JSON‑данных ({name, value}) для Recharts
│   │   └── chart_type_agent.py     # Выбор подходящих типов графиков
│   ├── utils/
│   │   └── str_cleaner.py          # Утилита для очистки строки от форматирования LLM.
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── server.py

├── gateway/                    # API Gateway — единая точка входа для клиента
│   ├── utils/
│   │   └── str_cleaner.py          
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── server.py

├── planner-agent/             # Планировщик: классификация цели и маршрутизация запроса
│   ├── utils/
│   │   └── str_cleaner.py          
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── server.py

├── sql-agent/                 # Сервис генерации и исполнения SQL-запросов
│   ├── agents/
│   │   ├── generate_sql_agent.py   # Генерация SQL по схеме и запросу
│   │   ├── execute_sql_agent.py    # Выполнение SQL-запросов
│   │   └── manage_sql_agent.py     # Менеджер SQL: генерация → исполнение → коррекция
│   ├── utils/
│   │   └── str_cleaner.py          # Утилита для очистки строки от форматирования LLM.
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── server.py

├── initdb/                    # Инициализация базы данных
│   └── init.sql

└── .env                       # Переменные окружения (API‑ключи, DB и т.д.)
```

---

##  Установка и настройка

1. Клонируйте репозиторий:
   ```bash
   git clone <URL ПРОЕКТА>
   cd <ПУТЬ К ПРОЕКТУ>
   ```

2. Установите зависимости через Poetry (в каждом микросервисе):
   ```bash
   cd chart-agent && poetry install
   cd ../sql-agent && poetry install
   cd ../planner-agent && poetry install
   cd ../gateway && poetry install
   ```

3. Создайте `.env` в корне проекта и укажите:
   ```env
   YANDEX_API_KEY=ваш_api_key
   YANDEX_GPT_URL=<URL API>
   YANDEX_GPT_MODEL_URI=<modelUri>
   DB_CONNECTION=postgresql://user:password@host:port/dbname
   SQL_AGENT_URL=http://sql-agent:5001
   CHART_AGENT_URL=http://chart-agent:5002
   PLANNER_ROUTER_URL=http://planer-agent:5003
   POSTGRES_USER=имя_пользователя
   POSTGRES_PASSWORD=пароль_пользователя
   POSTGRES_DB=имя_базы_данных
   DB_CONNECTION=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
   ```

---

##  Запуск

Через Docker Compose или вручную:

```bash
cd chart-agent && poetry run python server.py
cd ../sql-agent && poetry run python server.py
cd ../planner-agent && poetry run python server.py
cd ../gateway && poetry run python server.py
```
или
```bash
docker-compose up --build
```
По умолчанию:
- gateway: http://localhost:5000
- planner: http://localhost:5003
- sql-agent: http://localhost:5001
- chart-agent: http://localhost:5002

---

##  Как работает

1. **Клиент** отправляет POST на `/agent`:
   ```json
   { "user_prompt": "Покажи выручку по месяцам за 2024" }
   ```

2. **Gateway** отправляет запрос в **PlannerAgent**:
   - Классифицирует цель (`goal`): `sql`, `chart`, `both`, `other`
   - Запускает соответствующие агентов:
     - SQL-агенты: `generate → execute → fix`
     - Chart-агенты: `suggest_types → generate_data`

3. **Ответ**:
   ```jsonc
   {
     "goal": "both",
     "sql": "SELECT ...",
     "results": [ {…}, {…} ],
     "charts_type": ["barchart","linechart"],
     "charts_data": {
       "barchart": [ { "name": ..., "value": ... }, ... ],
       "linechart":  ...
     }
   }
   ```