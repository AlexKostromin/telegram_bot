# API Specification — USN Competitions Bot

Базовый URL: `https://your-domain.com`
Все ответы в формате **JSON**.
Все эндпоинты требуют заголовок авторизации (при необходимости согласовать).

---

## Оглавление

1. [GET /api/v1/competitions](#1-get-apiv1competitions)
2. [GET /api/v1/users/by-telegram/{telegram_id}](#2-get-apiv1usersby-telegramtelegram_id)
3. [POST /api/v1/users](#3-post-apiv1users)
4. [PUT /api/v1/users/{user_id}](#4-put-apiv1usersuser_id)
5. [GET /api/v1/time-slots](#5-get-apiv1time-slots)

---

## 1. GET /api/v1/competitions

Список активных соревнований, доступных для регистрации.

**Query-параметры:**

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `active_only` | boolean | `true` | Если `true` — возвращать только активные |

**Пример запроса:**
```
GET /api/v1/competitions?active_only=true
```

**Пример ответа `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "«Гранд финал 2025» КУБ",
    "description": "Основной чемпионат сезона 2025",
    "competition_type": "classic_game",
    "competition_category": "Standard",
    "competition_language": "Russian",
    "ratings_updated": true,
    "available_roles": ["player", "adviser", "viewer", "voter"],
    "player_entry_open": true,
    "voter_entry_open": true,
    "viewer_entry_open": true,
    "adviser_entry_open": true,
    "requires_time_slots": false,
    "requires_jury_panel": false,
    "is_active": true,
    "chief_arbitrator": "Константин Селянин",
    "arbitrators": ["Ольга Сероглазова-Селянина", "Константин Селянин"],
    "start_date": null,
    "end_date": null,
    "days": [
      {
        "day_number": 1,
        "date": "2025-12-13",
        "start_time_utc": "08:50:00"
      }
    ],
    "players": [
      {
        "player_name": "Ярослав Якубовский",
        "group": "A",
        "player_category": null
      }
    ]
  }
]
```

**Поле `competition_type` — возможные значения:**

| Значение | Описание |
|---|---|
| `classic_game` | Классическая игра |
| `tournament` | Турнир |
| `online` | Онлайн-формат |
| `team_competition` | Командное соревнование |

**Поле `available_roles` — возможные значения:** `player`, `voter`, `viewer`, `adviser`

> **Важно для бота:**
> - Роль `adviser` (Секундант) показывается пользователю **только** для соревнований типа `classic_game`.
> - Флаги `*_entry_open` определяют, открыта ли регистрация для конкретной роли.

---

## 2. GET /api/v1/users/by-telegram/{telegram_id}

Поиск пользователя по Telegram ID.

**Path-параметры:**

| Параметр | Тип | Описание |
|---|---|---|
| `telegram_id` | integer | Числовой Telegram ID пользователя |

**Пример запроса:**
```
GET /api/v1/users/by-telegram/123456789
```

**Пример ответа `200 OK`:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "telegram_username": "ivan_petrov",
  "first_name": "Иван",
  "last_name": "Петров",
  "phone": "+79001234567",
  "email": "ivan@example.com",
  "country": "Россия",
  "city": "Москва",
  "club": "Клуб Знатоков",
  "company": "ООО Тест",
  "position": "Инженер",
  "certificate_name": "Ivan Petrov",
  "presentation": "Иван Петров, КВЧ «Знатоки»",
  "seconded_player": null,
  "bio": "Опытный игрок",
  "date_of_birth": "1990-05-15",
  "channel_name": "@ivan_channel",
  "classic_rating": 1500,
  "quick_rating": 1400,
  "team_rating": 1450,
  "is_active": true,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

**Ответ `404 Not Found`:**
```json
{
  "detail": "User not found"
}
```

---

## 3. POST /api/v1/users

Создание нового пользователя.

**Тело запроса (`Content-Type: application/json`):**

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `telegram_id` | integer | **да** | Числовой Telegram ID |
| `telegram_username` | string\|null | нет | Username без `@` |
| `first_name` | string | **да** | Имя |
| `last_name` | string | **да** | Фамилия |
| `phone` | string | **да** | Телефон в формате `+7...` |
| `email` | string | **да** | Email |
| `country` | string\|null | нет | Страна |
| `city` | string | **да** | Город |
| `club` | string | **да** | Клуб/школа |
| `company` | string\|null | нет | Компания |
| `position` | string\|null | нет | Должность |
| `certificate_name` | string\|null | нет | Имя и фамилия латиницей для сертификата (для player/voter) |
| `presentation` | string\|null | нет | Как представить на соревновании |
| `seconded_player` | string\|null | нет | Игрок, которому секундирует (только для adviser) |
| `bio` | string\|null | нет | Краткое описание |
| `date_of_birth` | string\|null | нет | Дата рождения в формате `YYYY-MM-DD` |
| `channel_name` | string\|null | нет | Телеграм-канал пользователя |

**Пример запроса:**
```json
{
  "telegram_id": 123456789,
  "telegram_username": "ivan_petrov",
  "first_name": "Иван",
  "last_name": "Петров",
  "phone": "+79001234567",
  "email": "ivan@example.com",
  "country": "Россия",
  "city": "Москва",
  "club": "Клуб Знатоков",
  "certificate_name": "Ivan Petrov",
  "presentation": "Иван Петров, КВЧ «Знатоки»"
}
```

**Ответ `201 Created`:** возвращает созданного пользователя (тот же формат, что в GET by-telegram, плюс `id`, `created_at`, `updated_at`).

**Ответ `409 Conflict`** — если пользователь с таким `telegram_id`, `phone` или `email` уже существует:
```json
{
  "detail": "User with this telegram_id already exists"
}
```

---

## 4. PUT /api/v1/users/{user_id}

Обновление данных существующего пользователя (частичное — передаются только изменяемые поля).

**Path-параметры:**

| Параметр | Тип | Описание |
|---|---|---|
| `user_id` | integer | Внутренний ID пользователя |

**Тело запроса** — любое подмножество полей из таблицы [POST /api/v1/users](#3-post-apiv1users) (кроме `telegram_id`). Поля, не переданные в запросе, не изменяются.

**Пример запроса:**
```json
{
  "presentation": "Иван Петров (обновлено)",
  "city": "Санкт-Петербург"
}
```

**Ответ `200 OK`:** возвращает обновлённого пользователя целиком.

**Ответ `404 Not Found`:**
```json
{
  "detail": "User not found"
}
```

**Ответ `409 Conflict`** — если новый `phone` или `email` уже занят другим пользователем.

---

## 5. GET /api/v1/time-slots

Список временных слотов для судей по соревнованию.

**Query-параметры:**

| Параметр | Тип | Обязательный | Описание |
|---|---|---|---|
| `competition_id` | integer | **да** | ID соревнования |

**Пример запроса:**
```
GET /api/v1/time-slots?competition_id=4
```

**Пример ответа `200 OK`:**
```json
[
  {
    "id": 1,
    "competition_id": 4,
    "slot_day": "2026-03-01",
    "start_time": "09:00",
    "end_time": "10:00",
    "max_voters": 5,
    "is_active": true,
    "assigned": 2,
    "available": 3
  },
  {
    "id": 2,
    "competition_id": 4,
    "slot_day": "2026-03-01",
    "start_time": "10:30",
    "end_time": "11:30",
    "max_voters": 5,
    "is_active": true,
    "assigned": 0,
    "available": 5
  }
]
```

**Описание полей:**

| Поле | Описание |
|---|---|
| `slot_day` | Дата слота (`YYYY-MM-DD`) |
| `start_time` | Время начала (`HH:MM`) |
| `end_time` | Время окончания (`HH:MM`) |
| `max_voters` | Максимальное количество судей в слоте |
| `assigned` | Уже записано судей |
| `available` | Доступно мест (`max_voters - assigned`) |

Слоты в ответе отсортированы по `(slot_day, start_time)`.
Если у соревнования нет слотов — возвращается пустой массив `[]`.

---

## Коды ответов

| Код | Описание |
|---|---|
| `200` | Успех |
| `201` | Ресурс создан |
| `404` | Не найдено |
| `409` | Конфликт (дублирование уникального поля) |
| `422` | Ошибка валидации (некорректное тело запроса) |