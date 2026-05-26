docker-compose exec postgres_db psql -U postgres -d lab3db -c "SELECT email, hashed_password FROM users;"
# 🔐 Лабораторная работа №3

## Авторизация и аутентификация (JWT, OAuth2, Cookies)

---

## 📌 Описание проекта

Данный проект является продолжением **Лабораторной работы №3** и расширяет RESTful API механизмами аутентификации и авторизации. Реализованы:

- Регистрация и вход по email/паролю
- Аутентификация через Яндекс (OAuth 2.0) вручную, без готовых библиотек
- Выдача Access и Refresh JWT-токенов, передаваемых исключительно через `HttpOnly` cookies
- Хеширование паролей (bcrypt с уникальной солью) и токенов в базе данных
- Механизм обновления токенов (refresh) и отзыва (logout, logout-all)
- Защита CRUD-эндпоинтов `items` – доступ только авторизованным пользователям, каждый видит/редактирует только свои записи
- Проверка `state` для защиты от CSRF в OAuth-потоке
- Полное соответствие техническим требованиям: разделение слоёв, DTO, валидация, конфигурация через `.env`

---

## ⚙️ Используемые технологии

- Python 3.11
- FastAPI
- SQLAlchemy + PostgreSQL 16
- Alembic (миграции)
- PyJWT, bcrypt
- HTTPX (для OAuth-запросов)
- Docker + Docker Compose
- Яндекс ID (в качестве OAuth-провайдера)

---

## 🚀 Запуск проекта

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd <project-folder>
2. Создание файла .env
Скопируйте .env.example и заполните актуальными значениями:


cp .env.example .env
Пример .env.example (все секреты только для локальной разработки):

env
# База данных
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=lab3db
DB_HOST=postgres_db
DB_PORT=5432

# JWT
JWT_ACCESS_SECRET=simple_access_secret_key
JWT_REFRESH_SECRET=simple_refresh_secret_key
JWT_ACCESS_EXPIRATION=15
JWT_REFRESH_EXPIRATION=10080
TOKEN_HASH_SALT=simple_salt_for_token_hashing

# OAuth Яндекс
YANDEX_CLIENT_ID=your_client_id
YANDEX_CLIENT_SECRET=your_client_secret
YANDEX_REDIRECT_URI=http://localhost:4200/auth/oauth/yandex/callback
Для работы OAuth необходимо зарегистрировать приложение на Яндекс ID и указать полученные YANDEX_CLIENT_ID и YANDEX_CLIENT_SECRET.

3. Запуск через Docker

docker-compose up --build
API будет доступно по адресу:
👉 http://localhost:4200

Swagger-документация:
👉 http://localhost:4200/docs

Ссылка для Яндекс:
http://localhost:4200/auth/oauth/yandex

🗄️ Миграции базы данных
В проекте используется Alembic. Для создания и применения миграций:


docker-compose exec fastapi_app alembic revision --autogenerate -m "init"
docker-compose exec fastapi_app alembic upgrade head
Таблицы создаются автоматически при старте приложения, но миграции рекомендуются для продакшена.

📡 API эндпоинты
🔹 Аутентификация и пользователи
Метод	URI	Описание	Доступ
POST	/auth/register	Регистрация нового пользователя	Public
POST	/auth/login	Вход (установка HttpOnly cookies)	Public
POST	/auth/refresh	Обновление Access и Refresh токенов	Public (требуется валидная Refresh Cookie)
GET	/auth/whoami	Информация о текущем пользователе	Private
POST	/auth/logout	Завершение текущей сессии (отзыв токенов)	Private
POST	/auth/logout-all	Завершение всех сессий пользователя	Private
GET	/auth/oauth/yandex	Инициация входа через Яндекс	Public
GET	/auth/oauth/yandex/callback	Обработка ответа от Яндекса	Public
POST	/auth/forgot-password	Заглушка восстановления пароля	Public
POST	/auth/reset-password	Заглушка сброса пароля	Public
🔹 CRUD для ресурса items (защищены)
Все эндпоинты требуют авторизации. Пользователь видит и изменяет только свои записи.

Метод	URI	Описание
GET	/items?page=1&limit=10	Получить список своих элементов
GET	/items/{id}	Получить элемент по ID (только свой)
POST	/items	Создать новый элемент
PUT	/items/{id}	Полное обновление элемента
PATCH	/items/{id}	Частичное обновление
DELETE	/items/{id}	Мягкое удаление (Soft Delete)

🧠 Особенности реализации
🔹 JWT и Cookies
Access Token (15 мин) и Refresh Token (7 дней) генерируются вручную при помощи библиотеки PyJWT.
Токены передаются исключительно через Set-Cookie с флагами HttpOnly, SameSite.
Клиент (JavaScript) не имеет доступа к токенам, что предотвращает XSS-атаки.
🔹 Хранение токенов и паролей
Пароли хешируются алгоритмом bcrypt с автоматической генерацией уникальной соли.
Токены в БД хранятся в виде детерминированных хешей (SHA-256 + соль), что позволяет выполнять поиск токена для отзыва.
Отозванные и истекшие токены помечаются в БД.
🔹 OAuth 2.0 (Яндекс)
Реализован Authorization Code Grant вручную: формирование ссылки с параметром state, обмен кода на токен, запрос данных пользователя.
Пользователь ищется или создаётся в локальной БД по yandex_id. После входа генерируются собственные JWT.
🔹 Защита ресурсов
Добавлен middleware (зависимость get_current_user), который извлекает Access Token из куки, проверяет подпись и срок действия, а также факт отзыва токена в БД.
CRUD-операции с items используют владельца (user_id), гарантируя изоляцию данных.
🔹 Архитектура
Проект сохраняет модульную структуру, заложенную в ЛР2, с разделением на слои:
routers/ – обработка HTTP-запросов
services/ – бизнес-логика
models/ – ORM-модели
schemas/ – DTO и валидация
dependencies.py – общие зависимости FastAPI
utils/security.py – криптографические функции

❗ Безопасность и обработка ошибок
Пароли и токены в БД никогда не хранятся в открытом виде.
Чувствительные данные (хеши, соль, токены) исключены из ответов API.
OAuth-поток защищён проверкой state от CSRF.
Ошибки аутентификации и авторизации возвращают 401 Unauthorized или 403 Forbidden.
Неиспользуемые или невалидные токены отзываются.

🧪 Тестирование
Для тестирования рекомендуется использовать Postman или curl. Примеры запросов:
Регистрация

curl -X POST http://localhost:4200/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'
Логин (сохранение куки в файл)

curl -c cookies.txt -X POST http://localhost:4200/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"test@example.com","password":"secret123"}'
Проверка whoami

curl -b cookies.txt http://localhost:4200/auth/whoami
Создание элемента

curl -b cookies.txt -X POST http://localhost:4200/items/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Моя запись","description":"Тест"}'
Выход

curl -b cookies.txt -X POST http://localhost:4200/auth/logout
Проверка уникальности хешей паролей
Зарегистрируйте двух пользователей с одинаковым паролем.

Выполните:


docker-compose exec postgres_db psql -U postgres -d lab3db -c "SELECT email, hashed_password FROM users;"
Убедитесь, что значения hashed_password различаются.

✅ Соответствие требованиям
✔ JWT Access и Refresh токены, передаваемые только через HttpOnly cookies
✔ Хеширование паролей (bcrypt + соль) и токенов (SHA-256 + соль)
✔ Ручная реализация OAuth 2.0 (Яндекс) без готовых библиотек
✔ Механизмы отзыва токенов, refresh, logout-all
✔ Защита существующих CRUD-эндпоинтов с проверкой владельца
✔ Проверка state для защиты OAuth от CSRF
✔ Модульная архитектура с разделением ответственности
✔ DTO, валидация входящих данных
✔ Конфигурация через .env
✔ Запуск через docker-compose up --build

📄 Лицензия
Проект создан в учебных целях.