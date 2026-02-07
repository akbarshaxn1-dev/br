# Единый Портал Управления Отделами - PRD

## Обзор проекта
Корпоративная платформа для централизованного управления государственными фракциями. Заменяет Google/Excel таблицы и ручную отчетность.

## Архитектура
- **Backend:** FastAPI (Python) + MongoDB + WebSocket (Socket.IO)
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Authentication:** JWT с Refresh Tokens, RBAC

## Фракции (8 штук)
Правительство | ФСБ | ГИБДД | УМВД | Армия | Больница | СМИ | ФСИН

## Роли и права доступа

| Роль | Доступ |
|------|--------|
| Developer | Полный root, имитация пользователей |
| ГС/ЗГС | Все фракции, админ-панель |
| Лидер фракции | **Создание/удаление отделов**, темы, таблицы |
| Начальник отдела | Темы отдела, таблицы |
| Заместитель | Редактирование таблиц |

## ✅ Реализованные функции

### Адаптивный дизайн (NEW)
- Полная адаптация для телефонов (375px+) и ПК
- Сворачиваемый sidebar на мобильных
- Горизонтальный скролл таблиц
- Компактные кнопки (иконки на мобильных)
- Адаптивные карточки и статистика

### Real-time синхронизация (NEW)
- WebSocket (Socket.IO) интеграция
- Live/Offline статус индикатор
- Мгновенные уведомления об изменениях

### Архив недель (NEW)
- Просмотр всех недель отдела
- Badge "Текущая" для активной недели
- Переход к таблице любой недели

### Управление отделами (NEW)
- **Создание отделов** для лидеров и админов
- **Удаление отделов** с диалогом подтверждения
- Предупреждение о потере данных

### Админ-панель
- Статистика (пользователи, фракции, отделы, входы)
- CRUD пользователей (ник, должность, VK, роль, фракция)
- Фильтры и поиск
- Блок поддержки

### Динамические таблицы
- Google Sheet стиль
- Лекции, Тренировки, Аттестация, Дни на посту
- "Был" / "Не был" дропдауны
- Экспорт в Excel/CSV

### Темы лекций/тренировок
- Управление на уровне фракции (лидеры)
- Управление на уровне отдела (начальники)

## API Endpoints

### Auth
```
POST /api/auth/login | POST /api/auth/refresh | GET /api/auth/me
```

### Admin
```
GET /api/admin/stats | GET /api/admin/users | POST /api/admin/users
PUT /api/admin/users/{id} | DELETE /api/admin/users/{id}
```

### Factions & Departments
```
GET /api/factions/ | GET /api/factions/{code}
GET /api/departments/{id} | GET /api/departments/faction/{code}
POST /api/departments/faction/{code} | DELETE /api/departments/{id}
```

### Weeks & Tables
```
GET /api/weeks/department/{id} (archive)
GET /api/weeks/department/{id}/current
GET /api/weeks/{id}/table-data | PUT /api/weeks/{id}/table-data
```

## Тестирование
- Backend: 11/11 тестов PASS (100%)
- Frontend: Все функции работают (100%)
- Mobile: Протестировано на 375x667
- Desktop: Протестировано на 1920x800

## Учётные данные
- **Email:** vadim@emergent.dev
- **Password:** admin123

## Поддержка
**Разработчик:** Vadim Smirnov  
**VK:** https://vk.com/coder2406

---
*Последнее обновление: 07.02.2026*
