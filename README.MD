# Developer Landing Backend

Проект реализован как backend для формы обратной связи на лендинге разработчика. Пользователь отправляет имя, телефон, email и комментарий, после чего сервис:

* валидирует входные данные;
* анализирует комментарий с помощью AI;
* определяет тональность обращения;
* классифицирует тип запроса;
* генерирует автоматический ответ пользователю;
* сохраняет обращение;
* отправляет email-уведомление владельцу сайта;
* отправляет копию письма пользователю;
* логирует запрос;
* обновляет статистику обращений.

Если AI-провайдер или SMTP-сервер недоступны, сервис не падает, а продолжает работать через fallback-логику.

---

## 1. Запуск проекта

### Запуск через Docker

Перед запуском нужно создать файл `.env` на основе примера:

```bash
cp .env.example .env
```

Для Windows:
```bash
copy .env.example .env
```

После этого проект можно запустить через Docker Compose:

```bash
docker compose up --build
```

После запуска сервис будет доступен по адресу:

```text
http://127.0.0.1:8000
```

Swagger/OpenAPI документация:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

---
## 2. Стек технологий

### Backend

* Python 3.9+
* FastAPI
* Uvicorn
* Pydantic v2
* pydantic-settings
* EmailStr / email-validator
* smtplib для SMTP-отправки писем
* JSON / JSONL-файлы для хранения данных

### AI

* Gemini API
* OpenAI Python SDK
* OpenAI-compatible Chat Completions API
* Fallback-логика на стороне backend

### Infrastructure

* Docker
* Docker Compose
* `.env` для конфигурации
* Логирование в файл
* Swagger/OpenAPI документация
* CORS middleware
* Глобальные error handlers

---
## 3. Архитектура проекта

Проект построен по слоистой архитектуре:

```text
Controller / Router
        ↓
Service layer
        ↓
Repository layer
        ↓
File storage
```

Структура проекта:

```text
app/
  api/
    v1/
      contact.py          
      health.py           # GET /api/health
      metrics.py          # GET /api/metrics
      router.py           # общий роутер API
  core/
    config.py             # настройки приложения из .env
    error_handlers.py     # глобальная обработка ошибок
    exceptions.py         # кастомные исключения
    logging.py            # настройка логирования
    middleware.py         # middleware для логирования запросов
  repositories/
    contact_repository.py # сохранение обращений
    metrics_repository.py # хранение статистики
    rate_limit_repository.py # хранение данных rate limit
  schemas/
    contact.py            # Pydantic-схемы для контактов
    health.py             # схемы health check
    metrics.py            # схемы метрик
  services/
    ai_service.py         # интеграция с Gemini и fallback
    contact_service.py    # бизнес-логика формы обратной связи
    email_service.py      # отправка email или сохранение в outbox
    metrics_service.py    # работа со статистикой
    rate_limit_service.py # проверка лимитов
  utils/
    json_file.py          # безопасная работа с JSON/JSONL
  main.py                 # создание FastAPI-приложения

data/
  contacts.jsonl          # сохранённые обращения
  outbox.jsonl            # письма в тестовом режиме
  ratelimit.json          # данные rate limiting
  metrics.json            # статистика обращений

logs/
  app.log                 # файл логов

tests/
  test_contact.py         # тесты API

.env.example
Dockerfile
docker-compose.yml
requirements.txt
run.py
```

---
## 4. Реализация API

### POST `/api/contact`

Основной endpoint для формы обратной связи.

#### Request body

```json
{
  "name": "Иван",
  "phone": "+7 999 123-45-67",
  "email": "client@example.com",
  "comment": "Здравствуйте, хочу обсудить разработку backend API для лендинга."
}
```

#### Curl

```bash
curl -X POST "http://127.0.0.1:8000/api/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван",
    "phone": "+7 999 123-45-67",
    "email": "client@example.com",
    "comment": "Здравствуйте, хочу обсудить разработку backend API для лендинга."
  }'
```

#### Successful response

```json
{
  "status": "accepted",
  "request_id": "21d50e46-4f63-4f14-8c22-d26fa5b725fe",
  "message": "Обращение принято. Уведомления подготовлены к отправке.",
  "created_at": "2026-06-21T15:23:18.345681Z",
  "ai": {
    "available": true,
    "sentiment": "positive",
    "category": "project_request",
    "auto_reply": "Спасибо за ваше обращение! Мы получили ваше сообщение и скоро свяжемся с вами для обсуждения деталей.",
    "provider": "gemini",
    "error": null
  },
  "email": {
    "owner_sent": true,
    "user_copy_sent": true,
    "mode": "file_outbox",
    "error": null
  }
}
```

---

### GET `/api/health`

Endpoint для проверки состояния сервиса.

#### Curl

```bash
curl "http://127.0.0.1:8000/api/health"
```

#### Response

```json
{
  "status": "ok",
  "service": "Developer Landing Backend"
}
```

---

### GET `/api/metrics`

Endpoint для получения статистики обращений.

#### Curl

```bash
curl "http://127.0.0.1:8000/api/metrics"
```

#### Example response

```json
{
  "total_contacts": 1,
  "ai_success": 1,
  "ai_failures": 0,
  "email_success": 1,
  "email_failures": 0
}
```

---


## 5. AI-интеграция

AI используется в backend для первичной обработки обращения пользователя.

AI выполняет три задачи:

1. Анализ тональности комментария.
2. Классификация типа обращения.
3. Генерация автоматического ответа пользователю.

### Используемые категории

```text
job_offer
project_request
consultation
complaint
spam
general
```

### Используемые тональности

```text
positive
neutral
negative
```

### Где реализовано

AI-интеграция находится в файле:

```text
app/services/ai_service.py
```

Сервис отправляет данные формы в Gemini и ожидает JSON-ответ:

```json
{
  "sentiment": "positive",
  "category": "project_request",
  "auto_reply": "Спасибо за обращение! Я скоро свяжусь с вами."
}
```

### Использованный prompt

System prompt:

```text
Ты backend AI-модуль для формы обратной связи на лендинге разработчика.
Верни только JSON без markdown.
Поля: sentiment, category, auto_reply.
sentiment: positive | neutral | negative.
category: job_offer | project_request | consultation | complaint | spam | general.
auto_reply: короткий вежливый ответ пользователю на русском языке.
```

User prompt формируется из данных формы:

```text
Имя: {name}
Email: {email}
Телефон: {phone}
Комментарий: {comment}
```

Параметр `temperature` установлен в `0.2`, чтобы ответы были более стабильными и предсказуемыми.

---

## 6. Что сделано с помощью AI

При разработке проекта AI использовался как помощник для проектирования и ускорения разработки.

С помощью AI были подготовлены:

* идея слоистой архитектуры `Controller → Service → Repository`;
* fallback-логика для случая недоступности AI;
* README-документация.

### Какие промпты использовались

При разработке использовались следующие промпты:

```text
Разработать backend-сервис для лендинг-презентации разработчика с полноценной API-частью и интеграцией AI-инструментов.

Продумай архитектуру проекта REST API для формы обратной связи:
POST /api/contact, валидацию имени, телефона, email и комментария,
email-уведомления владельцу сайта и пользователю, обработку ошибок,
rate limiting, логирование запросов в файл и AI-интеграцию.
```

```text
Как реализовать AI интеграцию?

AI должен выполнять минимум одну полезную функцию:
анализ тональности комментария, классификацию типа обращения
и генерацию автоматического ответа пользователю.

Нужен graceful fallback, чтобы сервис продолжал работать,
если AI-провайдер недоступен или вернул ошибку.
```

```text
Напиши README для проекта.

В README нужно описать:
как запустить проект в Docker, как настроить .env,
какой стек используется, архитектуру проекта,
описание API-эндпоинтов, AI-интеграцию,
fallback-логику, хранение данных, rate limiting и логирование.
```

### Что пришлось исправлять вручную

После использования AI вручную были исправлены и доработаны следующие части:

* выбор модели `gemini-2.5-flash`;
* обработка ошибок от AI-провайдера;
* обработка ситуации, когда AI недоступен или возвращает некорректный ответ;
* fallback-ответы для анализа тональности, категории и автоответа;
* формат успешного ответа `POST /api/contact`;
* тестовый режим отправки email через `data/outbox.jsonl`;
* структура проекта и разделение логики по слоям;
* описание запуска проекта в Docker;
* примеры запросов и ответов в README.

---
## 7. Хранение данных

В проекте используется файловое хранение. Это сделано для простоты запуска и демонстрации backend-логики без необходимости поднимать отдельную базу данных.

### Обращения пользователей

Файл:

```text
data/contacts.jsonl
```

Каждое обращение сохраняется отдельной строкой в JSONL-формате.

### Email outbox

Файл:

```text
data/outbox.jsonl
```

Если `MAIL_ENABLED=false`, письма не отправляются через SMTP, а сохраняются в этот файл.

Это позволяет проверить, какие письма были бы отправлены владельцу сайта и пользователю.

### Rate limiting

Файл:

```text
data/ratelimit.json
```

В нём хранится информация о количестве запросов с конкретного IP-адреса за указанный временной период.

Настройки:

```env
CONTACT_RATE_LIMIT=5
CONTACT_RATE_WINDOW_SECONDS=60
```

Это означает, что один клиент может отправить не более 5 обращений за 60 секунд.

### Статистика

Файл:

```text
data/metrics.json
```

В статистике хранятся:

* общее количество обращений;
* количество успешных AI-обработок;
* количество fallback-срабатываний;
* количество успешных email-операций;
* количество email-ошибок.

### Логи

Файл:

```text
logs/app.log
```

В логах фиксируются:

* входящие HTTP-запросы;
* request id;
* метод запроса;
* путь;
* статус ответа;
* время обработки;
* ошибки валидации;
* ошибки приложения;
* неожиданные ошибки;
* ошибки AI-провайдера.

---
