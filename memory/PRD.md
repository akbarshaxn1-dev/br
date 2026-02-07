# Единый Портал Управления Отделами - PRD

## Обзор проекта
Корпоративная платформа для централизованного управления государственными фракциями. Заменяет Google/Excel таблицы и ручную отчетность.

## Архитектура
- **Backend:** FastAPI (Python) + MongoDB
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Authentication:** JWT с Refresh Tokens, RBAC

## Фракции (8 штук)
1. Правительство (gov)
2. ФСБ (fsb)
3. ГИБДД (gibdd)
4. УМВД (umvd)
5. Армия (army)
6. Больница (hospital)
7. СМИ (smi)
8. ФСИН (fsin)

## Роли и права доступа

| Роль | Доступ | Возможности |
|------|--------|-------------|
| Developer (Vadim Smirnov) | Полный root | Всё + имитация пользователей, восстановление данных |
| ГС/ЗГС | Почти полный | Все фракции, админ-панель, логи |
| Лидеры фракций | Своя фракция | CRUD отделов, темы, таблицы |
| Начальник отдела | Свой отдел | Таблицы, темы отдела |
| Заместитель | Свой отдел | Редактирование таблиц |

## Реализованные функции ✅

### Авторизация
- JWT токены (access + refresh)
- bcrypt хеширование паролей
- Поддержка 2FA (TOTP)

### Админ-панель (NEW)
- Статистика (пользователи, фракции, отделы, входы за 24ч)
- Создание пользователей (ник, имя, email, пароль, должность, VK, роль, фракция, отдел)
- Редактирование пользователей
- Деактивация/активация
- Фильтры по фракции и роли
- Поиск по нику/имени/email
- Блок поддержки разработчика

### Dashboard
- 8 фракций с быстрым переходом
- Статистика системы

### Фракции
- Список с RBAC фильтрацией
- Детали фракции
- Создание/удаление отделов

### Отделы
- Список по фракции
- Управление структурой

### Динамические таблицы (Google Sheet стиль)
- Nick Name, Лекции, Тренировки, Аттестация, Дней на посту
- Дропдауны "Был" / "Не был" с цветовой кодировкой
- Inline редактирование
- Автосохранение
- Экспорт в CSV/Excel
- **Управление темами прямо из таблицы (NEW)**

### Темы лекций и тренировок
- CRUD для фракций (лидеры)
- **CRUD для отделов (начальники отделов)** (NEW)
- Наследование от фракции к отделу

### Журнал действий
- Полное логирование (кто, когда, что, IP)
- Фильтрация по типу ресурса
- История входов

### Недельная система
- Автоматическое создание (Пн-Вс)
- Хранение по неделям

### UI/UX
- Тёмная корпоративная тема
- Светлая тема
- Адаптивный дизайн
- Sidebar навигация (8 пунктов)

## API Endpoints

### Auth
```
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/me
POST /api/auth/refresh
```

### Admin (NEW)
```
GET  /api/admin/stats
GET  /api/admin/users
GET  /api/admin/users/{id}
POST /api/admin/users
PUT  /api/admin/users/{id}
DELETE /api/admin/users/{id}
POST /api/admin/users/{id}/activate
GET  /api/admin/roles
GET  /api/admin/factions-list
GET  /api/admin/departments-list
POST /api/admin/impersonate/{id}
```

### Factions & Departments
```
GET  /api/factions/
GET  /api/factions/{code}
GET  /api/departments/{id}
GET  /api/departments/faction/{code}
POST /api/departments/faction/{code}
DELETE /api/departments/{id}
```

### Topics
```
GET  /api/topics/lectures/faction/{code}
POST /api/topics/lectures/faction/{code}
DELETE /api/topics/lectures/{id}
GET  /api/topics/lectures/department/{id}    (NEW)
POST /api/topics/lectures/department/{id}    (NEW)
DELETE /api/topics/lectures/department/{id}/{topic_id}  (NEW)
```

### Weeks & Tables
```
GET  /api/weeks/department/{id}/current
GET  /api/weeks/{id}/table-data
PUT  /api/weeks/{id}/table-data
```

### Audit
```
GET  /api/audit/logs
```

## Учётные данные
- **Email:** vadim@emergent.dev
- **Password:** admin123
- **Роль:** Developer (Super Admin)

## Тестирование
- Backend: 22/22 тестов PASS
- Frontend: 100% функций работают
- Test files: `/app/test_reports/iteration_2.json`

## Будущие задачи

### P1 - Высокий приоритет
- [ ] WebSocket для real-time синхронизации
- [ ] Восстановление данных (откат удалений)
- [ ] Push уведомления
- [ ] Таблица старшего состава

### P2 - Средний приоритет
- [ ] Redis кэширование
- [ ] Архив недель с историей
- [ ] Мобильная адаптация (карточки)
- [ ] Undo/Redo для таблиц

## Структура проекта
```
/app/
├── backend/
│   ├── routes/
│   │   ├── admin.py      # NEW
│   │   ├── auth.py
│   │   ├── audit.py
│   │   ├── departments.py
│   │   ├── factions.py
│   │   ├── topics.py     # Updated
│   │   └── weeks.py
│   ├── utils/
│   ├── models.py
│   └── server.py
└── frontend/
    └── src/
        ├── components/
        │   ├── AdminPage.js    # NEW
        │   ├── DepartmentPage.js  # Updated
        │   └── ...
        └── ...
```

## Поддержка
**Разработчик:** Vadim Smirnov  
**Связь:** https://vk.com/coder2406

---
*Последнее обновление: 07.02.2026*
