# Единый Портал Управления Отделами - Product Requirements Document

## Обзор проекта
Корпоративная платформа для управления различными государственными фракциями. Система заменяет Google/Excel таблицы и ручную отчетность.

## Архитектура
- **Backend:** FastAPI (Python) + MongoDB
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Authentication:** JWT с Refresh Tokens, RBAC

## Фракции
1. Правительство (gov)
2. ФСБ (fsb)
3. ГИБДД (gibdd)
4. УМВД (umvd)
5. Армия (army)
6. Больница (hospital)
7. СМИ (smi)
8. ФСИН (fsin)

## Роли и права доступа
- **Developer (Vadim Smirnov):** Полный root доступ, управление всем
- **GS/ZGS:** Почти полный доступ к фракциям и отделам
- **Лидеры фракций:** Управление только своей фракцией
- **Начальники отделов:** Редактирование таблиц своего отдела

## Реализованные функции

### Авторизация ✅
- JWT токены (access + refresh)
- Безопасное хранение паролей (bcrypt)
- Поддержка 2FA (TOTP) для высоких ролей

### Dashboard ✅
- Отображение всех 8 фракций
- Статистика (кол-во фракций, отделов)
- Быстрый переход к фракциям

### Фракции ✅
- Просмотр списка фракций
- Просмотр деталей фракции
- Создание отделов в фракции
- RBAC фильтрация по роли пользователя

### Отделы ✅
- Список отделов по фракции
- Создание/удаление отделов
- Управление структурой таблицы

### Динамические таблицы (Google Sheet стиль) ✅
- Колонки: Nick Name, Лекции, Тренировки, Аттестация, Дней на посту
- Дропдауны "Был" / "Не был" с цветовой кодировкой
- Inline редактирование
- Автоматическое сохранение
- Экспорт в CSV/Excel

### Темы лекций и тренировок ✅
- Управление темами по фракциям
- CRUD операции для лекций
- CRUD операции для тренировок

### Журнал действий (Audit Log) ✅
- Логирование всех действий
- Фильтрация по типу ресурса
- Отображение IP адресов
- История входов/выходов

### Недельная система ✅
- Автоматическое создание недели (Пн-Вс)
- Хранение данных таблиц по неделям
- Отображение текущего периода

### Настройки ✅
- Информация о профиле
- Переключение темы (тёмная/светлая)
- Статус 2FA

### UI/UX ✅
- Тёмная корпоративная тема
- Адаптивный дизайн
- Sidebar навигация
- Shadcn/UI компоненты

## API Endpoints
```
POST /api/auth/login - Авторизация
POST /api/auth/register - Регистрация
GET  /api/auth/me - Текущий пользователь
POST /api/auth/refresh - Обновление токена

GET  /api/factions/ - Список фракций
GET  /api/factions/{code} - Детали фракции

GET  /api/departments/{id} - Информация об отделе
GET  /api/departments/faction/{code} - Отделы фракции
POST /api/departments/faction/{code} - Создать отдел
DELETE /api/departments/{id} - Удалить отдел

GET  /api/topics/lectures/faction/{code} - Темы лекций
POST /api/topics/lectures/faction/{code} - Создать тему лекции
DELETE /api/topics/lectures/{id} - Удалить тему

GET  /api/topics/trainings/faction/{code} - Темы тренировок
POST /api/topics/trainings/faction/{code} - Создать тему тренировки
DELETE /api/topics/trainings/{id} - Удалить тему

GET  /api/weeks/department/{id}/current - Текущая неделя
GET  /api/weeks/{id}/table-data - Данные таблицы
PUT  /api/weeks/{id}/table-data - Обновить данные

GET  /api/audit/logs - Журнал действий
```

## Учётные данные для тестирования
- **Email:** vadim@emergent.dev
- **Password:** admin123
- **Роль:** Developer (Super Admin)

## Будущие задачи (P1-P2)

### P1 - Высокий приоритет
- [ ] WebSocket для real-time синхронизации
- [ ] Восстановление данных (Developer role)
- [ ] Push уведомления
- [ ] Управление пользователями

### P2 - Средний приоритет
- [ ] Redis кэширование
- [ ] Архив недель с фильтрацией
- [ ] Экспорт отчётов
- [ ] Мобильная адаптация
- [ ] Таблица "Старшего состава"

## Технический стек
- FastAPI 0.109.0
- MongoDB (motor)
- React 18
- Tailwind CSS 3
- Shadcn/UI
- JWT (PyJWT)
- bcrypt
- pyotp (2FA)

## Структура проекта
```
/app/
├── backend/
│   ├── routes/        # API endpoints
│   ├── utils/         # Helpers (security, audit, permissions)
│   ├── models.py      # Pydantic models
│   ├── database.py    # MongoDB connection
│   └── server.py      # FastAPI app
└── frontend/
    ├── src/
    │   ├── components/ # React components
    │   ├── contexts/   # Auth, Theme, WebSocket contexts
    │   └── utils/      # API helpers
    └── public/
```

---
*Последнее обновление: 06.02.2026*
