# BookSpace — электронная библиотека

Полноценный учебный проект: FastAPI + SQLAlchemy + Pydantic + JWT, PostgreSQL 15, Vanilla JS SPA, Nginx, Docker Compose (3 контейнера).

## Запуск
```bash
docker compose up --build
```
Открыть: `http://localhost:8080`  
Swagger: `http://localhost:8080/docs`  
Health: `http://localhost:8080/api/health`

## Демо-доступ
- Читатель: `client` / `client123`
- Администратор: `admin` / `admin123`

Первый запуск автоматически создаёт демо-пользователей, категории и 7 книг. В демонстрационной версии меняйте секреты перед публичным развёртыванием.

## Возможности
- Регистрация и вход, JWT и роли `Client` / `Admin`.
- Каталог книг с поиском по названию, автору и ISBN, фильтром категории и наличия.
- Выдача и возврат книг, даты возврата, список личных выдач.
- Администрирование книг, проверка доступного остатка, статистика и журнал аудита.
- Валидация API, проверки доступа, health endpoint.
- Документация архитектуры и 60 пользовательских историй (ровно 20 MVP).

## GitHub Issues
1. Создайте пустой GitHub-репозиторий и загрузите в него проект.
2. Создайте Personal Access Token с разрешением на создание Issues в репозитории.
3. Создайте labels `MVP` и `backlog` (или запустите скрипт без labels, если GitHub ответит ошибкой).
4. В терминале задайте переменные и запустите скрипт:
```bash
export GITHUB_TOKEN="ваш_токен"
export GITHUB_REPOSITORY="ваш_логин/BookSpace"
python docs/upload_issues.py
```
Скрипт проверяет, что найдено ровно 60 историй, затем создаёт issue для каждой.

## Структура
```text
BookSpace/
├── backend/              # FastAPI, модели, схемы, auth и маршруты
├── frontend/             # SPA, стили, Nginx
├── docs/
│   ├── 60_USE_CASES.md   # 60 user stories, ровно 20 MVP
│   ├── upload_issues.py  # загрузка историй в GitHub Issues
│   └── ОПИСАНИЕ_ПРОЕКТА.md
├── docker-compose.yml
└── README.md
```

Смотрите `docs/ОПИСАНИЕ_ПРОЕКТА.md` для схемы архитектуры и объяснения компонентов. Подробная интерактивная документация API доступна по `/docs`.
