#!/bin/bash

# Скрипт управления приложением Flask
# Использование: ./manage.sh [команда]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Путь к проекту
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PID_FILE="$PROJECT_DIR/.flask.pid"

# Функция вывода сообщений
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка наличия команды
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "Команда '$1' не найдена. Установите её и повторите попытку."
        exit 1
    fi
}

# Активация виртуального окружения
activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Виртуальное окружение не найдено. Запустите './manage.sh install' сначала."
        exit 1
    fi
    
    #source "$VENV_DIR/bin/activate"
    ./venv/Scripts/activate
}

# Настройка базы данных
setup_database() {
    print_info "Настройка базы данных..."
    
    check_command psql
    
    # Проверка переменных окружения
    if [ -z "$DATABASE_URL" ]; then
        print_warning "Переменная DATABASE_URL не установлена. Используется значение по умолчанию."
        export DATABASE_URL="postgresql://localhost/subscriptions_db"
    fi
    
    # Извлечение имени БД из DATABASE_URL
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^\/]*\)$/\1/p')
    
    if [ -z "$DB_NAME" ]; then
        DB_NAME="subscriptions_db"
    fi
    
    print_info "Создание базы данных '$DB_NAME'..."
    
    # Попытка создать БД (может потребоваться пароль)
    if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        print_warning "База данных '$DB_NAME' уже существует."
    else
        createdb "$DB_NAME" 2>/dev/null || {
            print_error "Не удалось создать базу данных. Убедитесь, что PostgreSQL запущен и у вас есть права."
            exit 1
        }
        print_info "База данных '$DB_NAME' создана."
    fi
    
    # Создание таблиц
    print_info "Создание таблиц..."
    activate_venv
    python "$PROJECT_DIR/create_tables.py"
    
    if [ $? -eq 0 ]; then
        print_info "База данных настроена успешно!"
    else
        print_error "Ошибка при создании таблиц."
        exit 1
    fi
}

# Установка зависимостей
install_dependencies() {
    print_info "Установка зависимостей..."
    
    check_command python

    
    # Создание виртуального окружения
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Создание виртуального окружения..."
        python -m venv "$VENV_DIR"
    else
        print_warning "Виртуальное окружение уже существует."
    fi
    
    # Активация и установка зависимостей
    activate_venv
    print_info "Установка пакетов из requirements.txt..."
    python -m pip install -r "$PROJECT_DIR/requirements.txt"
    
    print_info "Зависимости установлены успешно!"
}

# Запуск приложения
start_app() {
    print_info "Запуск приложения..."
    
    activate_venv
    
    # Проверка наличия PID файла
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            print_warning "Приложение уже запущено (PID: $OLD_PID)"
            exit 1
        else
            rm "$PID_FILE"
        fi
    fi
    
    # Установка переменных окружения
    export FLASK_APP="$PROJECT_DIR/run.py"
    export FLASK_ENV="${FLASK_ENV:-development}"
    
    if [ -z "$DATABASE_URL" ]; then
        export DATABASE_URL="postgresql://localhost/subscriptions_db"
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        export SECRET_KEY="dev-secret-key-change-in-production"
        print_warning "SECRET_KEY не установлен, используется значение по умолчанию."
    fi
    
    # Запуск Flask в фоне
    nohup flask run --host=0.0.0.0 --port=8000 > "$PROJECT_DIR/flask.log" 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > "$PID_FILE"
    
    print_info "Приложение запущено (PID: $FLASK_PID)"
    print_info "Логи доступны в файле: $PROJECT_DIR/flask.log"
    print_info "Приложение доступно по адресу: http://127.0.0.1:8000"
}

# Остановка приложения
stop_app() {
    print_info "Остановка приложения..."
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "PID файл не найден. Приложение может быть не запущено."
        exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        rm "$PID_FILE"
        print_info "Приложение остановлено (PID: $PID)"
    else
        print_warning "Процесс с PID $PID не найден."
        rm "$PID_FILE"
    fi
}

# Запуск тестов
run_tests() {
    print_info "Запуск тестов..."
    
    activate_venv
    
    # Установка переменных окружения для тестов
    # export FLASK_ENV=testing
    # export TEST_DATABASE_URL="${TEST_DATABASE_URL:-postgresql://localhost/subscriptions_test_db}"
    
    pytest "$PROJECT_DIR/tests/" -v -W ignore::DeprecationWarning
    
    if [ $? -eq 0 ]; then
        print_info "Все тесты прошли успешно!"
    else
        print_error "Некоторые тесты не прошли."
        exit 1
    fi
}

# Справка
show_help() {
    echo "Использование: ./manage.sh [команда]"
    echo ""
    echo "Команды:"
    echo "  setup_db    - Настроить базу данных PostgreSQL и создать таблицы"
    echo "  install     - Создать виртуальное окружение и установить зависимости"
    echo "  start       - Запустить Flask приложение"
    echo "  stop        - Остановить Flask приложение"
    echo "  test        - Запустить unit тесты"
    echo "  --help      - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  ./manage.sh install     # Первоначальная установка"
    echo "  ./manage.sh setup_db    # Настройка БД"
    echo "  ./manage.sh start       # Запуск приложения"
}

# Основная логика
case "${1:-}" in
    setup_db)
        setup_database
        ;;
    install)
        install_dependencies
        ;;
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    test)
        run_tests
        ;;
    --help|-h|help)
        show_help
        ;;
    *)
        print_error "Неизвестная команда: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac

