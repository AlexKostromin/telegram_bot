# Docker Compose и Makefile - Полное руководство

## 📋 Обзор

Проект содержит два основных файла для управления приложением:

1. **docker-compose.yml** - Единый конфиг для всех сервисов (220 строк)
2. **Makefile** - 30+ удобных команд для разработки и деплоя (320 строк)

---

## 🐳 Docker Compose (docker-compose.yml)

### Особенности

✅ **Единый файл для всех окружений**
- Поддерживает SQLite (разработка)
- Поддерживает PostgreSQL (продакшен)
- Django Admin Panel (опционально)

✅ **Профили (Profiles)**
```yaml
profiles:
  - bot        # Основной бот
  - db         # PostgreSQL
  - admin      # Django админ-панель
  - all        # Все сервисы
  - postgres   # Только PostgreSQL
```

✅ **4 сервиса**
1. **bot** - Telegram бот (основной)
2. **postgres** - PostgreSQL база данных
3. **admin** - Django админ-панель (8000 порт)
4. **network_check** - Проверка сети

### Использование

#### Development (SQLite по умолчанию):
```bash
docker compose up -d bot
```

#### Production (PostgreSQL):
```bash
docker compose --profile all up -d
```

#### Только админ-панель:
```bash
docker compose --profile admin up -d
```

#### Только БД:
```bash
docker compose --profile db up -d postgres
```

### Конфигурация через переменные окружения

```bash
# .env файл
BOT_TOKEN=your_token_here
DATABASE_URL=sqlite+aiosqlite:///./bot_database.db
DEBUG=False
ADMIN_IDS=123456789

# PostgreSQL (если используется)
POSTGRES_USER=usn_bot
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=usn_bot_db
POSTGRES_PORT=5432

# Admin Panel
ADMIN_PORT=8000
```

### Volumes и хранение данных

```yaml
bot_data           # SQLite БД и состояние бота
postgres_data      # PostgreSQL данные
bot_logs          # Логи приложения
admin_static      # Статические файлы Django
admin_media       # Медиа-файлы Django
```

### Networks

Все сервисы подключены к сети `bot_network`:
- Сервисы видят друг друга по имени
- Изолированы от остальной системы
- Безопасная inter-service коммуникация

### Health Checks

PostgreSQL имеет встроенную проверку здоровья:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U usn_bot"]
  interval: 10s
  timeout: 5s
  retries: 5
```

Бот дождется, пока PostgreSQL будет готов:
```yaml
depends_on:
  postgres:
    condition: service_healthy
```

---

## 🔧 Makefile - 30+ команд

### Структура Makefile

```
📁 Makefile
├── Основные команды (help, info, version)
├── Docker операции (up, down, build, clean)
├── Development режимы (dev, sqlite, postgres)
├── Логирование (logs, logs-tail, stats)
├── Административные команды (shell, status, health)
├── Admin Panel (admin-up, admin-down)
├── БД управление (db-shell, db-backup, db-restore)
└── Тестирование (test, lint, format)
```

### Основные команды

#### 📖 Справка
```bash
make help          # Полная справка (это сообщение)
make info          # Информация о проекте
make version       # Версии инструментов
```

#### 🎯 Быстрый старт
```bash
make dev           # Запустить разработку (SQLite)
make up            # Запустить в фоне
make down          # Остановить все
make restart       # Перезапустить бот
```

#### 📊 Мониторинг
```bash
make logs          # Живой логи (Ctrl+C выход)
make logs-tail     # Последние 50 строк
make status        # Статус контейнеров (ps)
make stats         # Использование ресурсов
make health        # Проверка здоровья бота
```

#### 🏗️ Docker
```bash
make build         # Собрать/пересобрать образ
make clean         # Удалить контейнеры и volumes (с подтверждением)
make prune         # Очистить неиспользуемые ресурсы Docker
```

#### 💻 Interactive
```bash
make shell         # Bash в контейнере бота
```

#### 🔧 PostgreSQL
```bash
make postgres      # Запустить с PostgreSQL
make migrate       # Миграция SQLite → PostgreSQL
make db-init       # Инициализировать PostgreSQL
make db-shell      # Открыть psql консоль
make db-backup     # Бэкап базы (backups/usn_bot_YYYYMMDD_HHMMSS.sql)
make db-restore BACKUP_FILE=backups/...  # Восстановление
make db-clean      # Удалить все данные (с подтверждением)
```

#### 🎛️ Admin Panel
```bash
make admin-up      # Запустить админ-панель (http://localhost:8000)
make admin-down    # Остановить админ-панель
make admin-logs    # Логи админ-панели
make admin-shell   # Bash в контейнере админ-панели
```

#### ✅ Качество кода
```bash
make test          # Запустить тесты (pytest)
make lint          # Проверка стиля (flake8)
make format        # Форматирование (black)
```

---

## 💡 Сценарии использования

### Scenario 1: Разработка с SQLite

```bash
# Запуск
make dev

# Просмотр логов
make logs

# Если нужно перезапустить
make restart

# Открыть консоль в контейнере
make shell

# Остановить
make down
```

### Scenario 2: Миграция на PostgreSQL

```bash
# 1. Автоматическая миграция
make migrate

# 2. ИЛИ запуск PostgreSQL вручную
make postgres

# 3. Проверить БД
make db-shell
```

### Scenario 3: Production deployment

```bash
# 1. Запустить все сервисы
docker compose --profile all up -d

# 2. Проверить здоровье
make health

# 3. Посмотреть логи
make logs

# 4. Сделать бэкап
make db-backup

# 5. Мониторить
make stats
```

### Scenario 4: Admin Panel

```bash
# 1. Запустить админ-панель
make admin-up

# 2. Открыть браузер на http://localhost:8000/admin
# 3. Логин: admin / пароль: admin

# 4. Посмотреть логи админ-панели
make admin-logs

# 5. Открыть консоль (для отладки)
make admin-shell
```

### Scenario 5: Резервное копирование и восстановление

```bash
# Создать бэкап
make db-backup
# Создаст файл: backups/usn_bot_20260210_101530.sql

# Восстановить из бэкапа
make db-restore BACKUP_FILE=backups/usn_bot_20260210_101530.sql
```

---

## 📝 Конфигурация

### Environment Variables

Создайте `.env` файл в корне проекта:

```bash
# Telegram Bot
BOT_TOKEN=your_bot_token_here
DEBUG=False
LOGGING_LEVEL=INFO
ADMIN_IDS=123456789,987654321

# Database (выберите один)
# SQLite (разработка)
DATABASE_URL=sqlite+aiosqlite:///./bot_database.db

# PostgreSQL (продакшен)
DATABASE_URL=postgresql+asyncpg://usn_bot:secure_password@postgres:5432/usn_bot_db

# PostgreSQL credentials
POSTGRES_USER=usn_bot
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=usn_bot_db
POSTGRES_PORT=5432

# Django
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_PORT=8000

# Connection Pooling
PG_POOL_SIZE=10
PG_MAX_OVERFLOW=20
```

### .env.example

Файл `.env.example` содержит все доступные переменные:

```bash
cp .env.example .env
# Отредактировать значения
```

---

## 🐛 Troubleshooting

### Проблема: "Container not running"

```bash
# Проверить статус
make status

# Посмотреть ошибки
make logs

# Пересоздать контейнер
make down
make build
make up
```

### Проблема: "Port already in use"

```bash
# Найти процесс на порту 8000
lsof -i :8000

# Убить процесс
kill -9 <PID>

# Или использовать другой порт
ADMIN_PORT=8001 docker compose up -d
```

### Проблема: "Database connection refused"

```bash
# Проверить PostgreSQL
make db-shell

# Если не подключается, пересоздать
make db-clean
make db-init
```

### Проблема: "Out of disk space"

```bash
# Очистить неиспользуемые образы и контейнеры
make prune

# Более агрессивная очистка
docker system prune -a --volumes -f
```

---

## 📊 Мониторинг и логирование

### Просмотр логов в реальном времени

```bash
# Бот
make logs

# Admin Panel
make admin-logs

# PostgreSQL
docker compose logs -f postgres
```

### Ограничение логов

По умолчанию логи ограничены:
- **max-size**: 10MB на файл
- **max-file**: 3 файла ротации

Отредактируйте в `docker-compose.yml`:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "20m"  # Размер файла
    max-file: "5"    # Кол-во файлов
```

### Проверка ресурсов

```bash
# Реальное время использование
make stats

# Или native Docker команда
docker stats usn-telegram-bot

# Информация о контейнере
docker inspect usn-telegram-bot
```

---

## 🔐 Security Best Practices

### Passwords и Secrets

❌ **Плохо:**
```bash
DATABASE_URL=postgresql://user:password@host/db
```

✅ **Хорошо:**
```bash
# .env файл (не коммитить!)
DATABASE_URL=postgresql://user:${POSTGRES_PASSWORD}@host/db

# .env.example (для примера)
POSTGRES_PASSWORD=change_this_in_production
```

### Docker Security

```bash
# Запуск с ограничениями (в compose.yml)
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
```

### Networking

- Все сервисы в изолированной сети `bot_network`
- PostgreSQL не expose в host по умолчанию (только через bot сервис)
- Для доступа извне, раскомментируйте `ports` в postgres сервисе

---

## 📈 Performance Tuning

### PostgreSQL Connection Pooling

```bash
# .env
PG_POOL_SIZE=20        # Размер пула (default: 10)
PG_MAX_OVERFLOW=40     # Max overflow (default: 20)
```

### Memory Limits

```bash
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G         # Максимум памяти
    reservations:
      memory: 512M       # Зарезервировано
```

### CPU Limits

```bash
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'          # Максимум CPU
    reservations:
      cpus: '1'          # Зарезервировано
```

---

## 🚀 Deployment Checklist

- [ ] Создать `.env` с production значениями
- [ ] Установить сильный пароль PostgreSQL
- [ ] Запустить `make postgres` (или `--profile all`)
- [ ] Проверить `make health` (бот здоров?)
- [ ] Сделать первый `make db-backup`
- [ ] Настроить мониторинг логов
- [ ] Настроить автоматические бэкапы (крон)
- [ ] Протестировать восстановление из бэкапа
- [ ] Настроить SSL/TLS (если нужно)
- [ ] Документировать ваши переменные окружения

---

## 📚 Дополнительные команды

### Advanced Docker Compose

```bash
# Просмотреть конфиг
docker compose config

# Валидировать конфиг
docker compose config --quiet

# Список сервисов
docker compose config --services

# Dry-run (не запускать)
docker compose up --dry-run
```

### Manual Docker Commands

```bash
# Если не хотите использовать make...

# Запустить все
docker compose up -d

# Остановить
docker compose down

# Перестроить
docker compose build --no-cache

# Логи
docker compose logs -f bot

# Shell
docker compose exec bot /bin/bash
```

---

## 📞 Support

Если что-то не работает:

1. Проверьте логи: `make logs`
2. Проверьте статус: `make status`
3. Проверьте здоровье: `make health`
4. Посмотрите документацию: `POSTGRESQL_MIGRATION.md`
5. Откройте issue на GitHub

---

## 📋 Summar

| Файл | Строк | Назначение |
|------|-------|-----------|
| docker-compose.yml | 220 | Конфиг всех сервисов |
| Makefile | 320 | 30+ команд управления |
| .env | - | Переменные окружения |
| .env.example | - | Примеры конфига |

**Основная идея:**
- `docker-compose.yml` описывает **что**
- `Makefile` описывает **как** это использовать

---

**Последнее обновление:** 2026-02-10
**Версия:** 1.0
