# 📦 Лабораторная работа №2

## Проектирование и реализация RESTful API

---

## 📌 Описание проекта

Данный проект представляет собой RESTful API, разработанный с использованием **FastAPI**, **SQLAlchemy** и **PostgreSQL**.

API реализует полный набор CRUD-операций для ресурса `items`, включая:

* создание
* получение (одного и списка)
* обновление (полное и частичное)
* мягкое удаление (Soft Delete)

Также реализованы:

* пагинация
* валидация данных
* миграции базы данных (Alembic)
* контейнеризация с помощью Docker

---

## ⚙️ Используемые технологии

* Python 3.11
* FastAPI
* SQLAlchemy
* PostgreSQL 16
* Alembic (миграции)
* Docker + Docker Compose

---

## 🚀 Запуск проекта

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Создание файла `.env`

Создайте файл `.env` в корне проекта:

```env
DB_USER=student
DB_PASSWORD=student_secure_password
DB_NAME=lab2
DB_HOST=postgres
DB_PORT=5432
PORT=4200
```

---

### 3. Запуск через Docker

```bash
docker-compose up --build
```

После запуска API будет доступно по адресу:
👉 http://localhost:4200

Swagger-документация:
👉 http://localhost:4200/docs

---

## 🗄️ Миграции базы данных

Инициализация и применение миграций:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

## 📡 API эндпоинты

### 📌 Получить список элементов

```
GET /items?page=1&limit=10
```

Ответ:

```json
{
  "data": [...],
  "meta": {
    "total": 10,
    "page": 1,
    "limit": 10,
    "totalPages": 1
  }
}
```

---

### 📌 Получить элемент по ID

```
GET /items/{id}
```

---

### 📌 Создать элемент

```
POST /items
```

Тело запроса:

```json
{
  "name": "Example Item",
  "description": "Test description"
}
```

---

### 📌 Полное обновление

```
PUT /items/{id}
```

---

### 📌 Частичное обновление

```
PATCH /items/{id}
```

---

### 📌 Удаление (Soft Delete)

```
DELETE /items/{id}
```

Ответ:

```
204 No Content
```

---

## 🧠 Особенности реализации

### 🔹 Soft Delete

Удаление выполняется через установку поля `deleted_at`.
Удалённые записи:

* не возвращаются в API
* остаются в базе данных

---

### 🔹 Пагинация

Используются параметры:

* `page` — номер страницы (по умолчанию 1)
* `limit` — количество элементов (по умолчанию 10, максимум 100)

---

### 🔹 Валидация

Реализована через Pydantic:

* проверка обязательных полей
* ограничения длины строк
* проверка параметров пагинации

---

### 🔹 Архитектура

Проект построен по принципу разделения ответственности:

* `routers/` — обработка HTTP-запросов
* `services/` — бизнес-логика
* `models/` — ORM модели
* `schemas/` — DTO и валидация
* `db.py` — подключение к БД

---

## ❗ Обработка ошибок

API возвращает корректные HTTP-коды:

* `400 Bad Request` — ошибка валидации
* `404 Not Found` — ресурс не найден
* `409 Conflict` — конфликт данных
* `500 Internal Server Error` — внутренняя ошибка

---

## 🧪 Примеры запросов (cURL)

### Создание элемента

```bash
curl -X POST http://localhost:4200/items \
-H "Content-Type: application/json" \
-d '{"name":"Test","description":"Example"}'
```

### Получение списка

```bash
curl -X GET "http://localhost:4200/items?page=1&limit=2"
```

### Удаление

```bash
curl -X DELETE http://localhost:4200/items/<id>
```

---

## ✅ Соответствие требованиям

✔ RESTful API
✔ PostgreSQL + ORM
✔ Миграции через Alembic
✔ Soft Delete
✔ Пагинация
✔ DTO и валидация
✔ Docker контейнеризация
✔ Разделение слоёв (Controller / Service / Model)

---

## 📄 Лицензия

Проект создан в учебных целях.