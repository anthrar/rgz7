# Система управления финансовыми подписками

Веб-приложение для управления финансовыми подписками пользователей, построенное на Flask с использованием PostgreSQL.

## Возможности

- ✅ Регистрация и авторизация пользователей
- ✅ CRUD операции для подписок (создание, просмотр, редактирование, удаление)
- ✅ Система аудита всех действий пользователей
- ✅ RESTful API для работы с подписками
- ✅ Минималистичный веб-интерфейс
- ✅ Автоматизированная настройка через bash-скрипт
- ✅ CI/CD pipeline с автоматическими тестами

## Требования

- Python 3.12
- PostgreSQL 12+
- pip

## Установка

### Автоматическая установка (рекомендуется)

Используйте скрипт `manage.sh` для автоматической настройки:

```bash
# 1. Установка зависимостей
./manage.sh install

# 2. Настройка базы данных
./manage.sh setup_db

# 3. Запуск приложения
./manage.sh start
```

### Ручная установка

1. **Создание виртуального окружения:**
```bash
python3.12 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

2. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

3. **Настройка базы данных:**
```bash
# Создайте базу данных PostgreSQL
createdb subscriptions_db

# Установите переменные окружения
export DATABASE_URL="postgresql://localhost/subscriptions_db"
export SECRET_KEY="your-secret-key-here"

# Создайте таблицы
python create_tables.py
```

4. **Запуск приложения:**
```bash
export FLASK_APP=run.py
flask run
```

Приложение будет доступно по адресу: http://localhost:5000

## Использование manage.sh

Скрипт `manage.sh` предоставляет следующие команды:

- `./manage.sh install` - Создать виртуальное окружение и установить зависимости
- `./manage.sh setup_db` - Настроить базу данных и создать таблицы
- `./manage.sh start` - Запустить Flask приложение
- `./manage.sh stop` - Остановить Flask приложение
- `./manage.sh test` - Запустить unit тесты
- `./manage.sh --help` - Показать справку

## API Эндпоинты

Все API эндпоинты требуют авторизации (кроме `/login` и `/register`).

### Аутентификация

- `POST /login` - Вход в систему
- `POST /register` - Регистрация нового пользователя
- `GET /logout` - Выход из системы

### Подписки

- `GET /api/subscriptions` - Получить список всех подписок текущего пользователя
- `GET /api/subscriptions/<id>` - Получить детали подписки
- `POST /api/subscriptions` - Создать новую подписку
- `PUT /api/subscriptions/<id>` - Обновить подписку
- `DELETE /api/subscriptions/<id>` - Удалить подписку

### Аудит

- `GET /api/audit_logs` - Получить логи аудита текущего пользователя

### Примеры запросов

**Создание подписки:**
```bash
curl -X POST http://localhost:5000/api/subscriptions \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{
    "name": "Netflix",
    "amount": 999.99,
    "interval": "monthly",
    "next_billing_date": "2024-12-01"
  }'
```

**Получение списка подписок:**
```bash
curl http://localhost:5000/api/subscriptions \
  -H "Cookie: session=..."
```

## Структура проекта

```
7rgz/
├── app/                    # Основное приложение
│   ├── __init__.py        # Фабрика приложений
│   ├── models.py          # Модели данных
│   ├── routes/            # Роуты
│   │   ├── auth.py        # Аутентификация
│   │   ├── api.py         # RESTful API
│   │   └── main.py        # Основные страницы
│   ├── services/          # Сервисы
│   │   └── audit.py       # Система аудита
│   ├── utils/             # Утилиты
│   │   └── validators.py  # Валидаторы
│   ├── static/            # Статические файлы
│   │   ├── css/
│   │   └── js/
│   └── templates/         # HTML шаблоны
├── tests/                 # Тесты
│   ├── test_models.py
│   ├── test_auth.py
│   ├── test_api.py
│   └── test_audit.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml      # GitHub Actions workflow
├── config.py              # Конфигурация
├── create_tables.py       # Скрипт создания таблиц
├── manage.sh              # Bash-скрипт управления
├── requirements.txt       # Зависимости
└── run.py                 # Точка входа
```

## Тестирование

Запуск тестов:

```bash
./manage.sh test
```

Или вручную:

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://localhost/subscriptions_db
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

## CI/CD

Проект настроен с GitHub Actions для автоматического запуска тестов и проверки безопасности при каждом push в ветку `main`.

Workflow выполняет:
- Запуск unit тестов с покрытием кода
- Проверку безопасности кода с помощью Bandit

## Безопасность

- Пароли хранятся в захешированном виде (Werkzeug)
- CSRF защита через Flask-WTF
- Авторизация через Flask-Login
- Все действия пользователей логируются в системе аудита

## Лицензия

Этот проект создан в образовательных целях.

