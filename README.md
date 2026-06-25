# 📦 Order Service Project
Код проекта представлен в папке app -> db и services

---

## 🚀 Запуск проекта

Для запуска приложения с использованием Docker Compose выполните команду:

```bash
docker compose up --build
Альтернативный вариант (если уже собран образ)
docker compose up

Перед запуском убедитесь, что:
	установлен Docker
	установлен Docker Compose
	настроены переменные окружения (если используются .env)

Swagger предсталвен по адресу:
	127.0.0.1:8000/docs

Данные для тестирования:
	username | password

	admin@mail.com | admin
	user@mail.com | user
	manager@mail.com | manager
	guest@mail.com | guest

Описание проекта
	Backend-приложение, реализующее собственную систему аутентификации, авторизации и разграничения доступа (RBAC) с использованием FastAPI и SQLAlchemy.

Проект демонстрирует принципы построения безопасных backend-систем, включая:
	JWT-аутентификацию
	ролевую модель доступа
	бизнес-логику на основе действий пользователей
	Основной функционал
	Аутентификация
	Регистрация пользователей (email + пароль)
	Хеширование паролей (bcrypt)
	Login с выдачей JWT-токена
	Logout (клиентская инвалидация токена)
	Получение текущего пользователя через токен
	Управление пользователями
	Просмотр профиля пользователя
	Обновление данных профиля
	Мягкое удаление аккаунта (is_active = False)
	RBAC (Role-Based Access Control)

Доступ к действиям регулируется системой ролей и правил доступа.
	Административная часть
	Управление ролями пользователей
	Изменение правил доступа
	Контроль бизнес-правил системы
	Архитектура проекта

Проект построен по слоям:
	API layer (FastAPI routers)
	Service layer (business logic)
	Data layer (SQLAlchemy ORM)
	Security layer (JWT + RBAC)
	Проверка доступа

Проверка доступа выполняется динамически при каждом запросе.
Технологии
	Python 3.12.2
	FastAPI
	SQLAlchemy
	PostgreSQL
	JWT
	bcrypt
	Pydantic
	Принципы безопасности
	Хеширование паролей
	JWT-аутентификация
	Проверка доступа на каждом запросе
	Разделение ролей и прав
	Мягкое удаление пользователей
```
Скриншоты
<img width="1437" height="864" alt="image" src="https://github.com/user-attachments/assets/366c02bd-4d7b-4b1b-a524-0a049f67cf1d" />
<img width="1434" height="721" alt="image" src="https://github.com/user-attachments/assets/1aabcc37-1dbe-4ac2-8813-3c25a7ece21c" />
