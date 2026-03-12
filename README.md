# Selectel Vacancies API

FastAPI-приложение для парсинга публичных вакансий Selectel, хранения в PostgreSQL и предоставления CRUD API.

## Быстрый старт

1. Клонируйте репозиторий (или распакуйте проект из архива):
  `git clone --branch with-bugs https://github.com/selectel/be-test.git`
2. Создайте `.env` на основе примера:
  `cp .env.example .env`
3. Примените переменные окружения `.env`:
  `source .env`
4. Запуск через Docker Desktop:
  `docker compose up --build`
5. Проверка работоспособности:
  в браузере откройте **http://localhost:8000/docs** (обязательно с портом `8000`, не просто localhost).
  метрики API: **http://localhost:8000/metrics**
  Prometheus UI: **http://localhost:9090**
  Grafana UI: **http://localhost:3000** (логин/пароль по умолчанию: `admin`/`admin`)
6. Остановка и очистка:
  `docker-compose down -v`

## Переменные окружения

- `DATABASE_URL` — строка подключения к PostgreSQL.
- `LOG_LEVEL` — уровень логирования (`INFO`, `DEBUG`).
- `PARSE_SCHEDULE_MINUTES` — интервал фонового парсинга в минутах.

## Основные эндпоинты

- `GET /api/v1/vacancies/` — список вакансий
- `GET /api/v1/vacancies/{id}` — детали вакансии.
- `POST /api/v1/vacancies/` — создание вакансии.
- `PUT /api/v1/vacancies/{id}` — обновление вакансии.
- `DELETE /api/v1/vacancies/{id}` — удаление вакансии.
- `POST /api/v1/parse/` — ручной запуск парсинга.

## Примечания

- При старте приложения выполняется первичный парсинг.
- Фоновый парсинг запускается планировщиком APScheduler (в рамках заданного интервала).
- В проект добавлена lightweight observability-связка Prometheus + Grafana.
- Для парсера экспортируются кастомные метрики: количество запусков, ошибок, длительность и число добавленных вакансий.

## Как смотреть метрики

1. Запустите проект: `docker compose up --build`
2. Откройте в браузере:
   - `http://localhost:8000/metrics` — сырые метрики приложения в формате Prometheus;
   - `http://localhost:9090` — UI Prometheus (можно искать метрики, например `parse_runs_total`, `parse_errors_total`, `parse_duration_seconds`);
   - `http://localhost:3000` — UI Grafana (`admin` / `admin`).
3. Источник данных Prometheus в Grafana создаётся автоматически при старте (provisioning).
4. В Grafana можно сразу строить дашборды по метрикам приложения (`parse_runs_total`, `parse_errors_total`, `parse_duration_seconds`, `parsed_vacancies_total`).

## CI/CD

- В репозитории добавлен workflow `CI/CD` (`.github/workflows/ci-cd.yml`).
- CI: на `push` и `pull_request` в `main/master` запускаются `compileall` и `pytest`.
- CD: на `push` в `main/master` собирается Docker-образ и публикуется в GHCR: `ghcr.io/<owner>/<repo>`.

