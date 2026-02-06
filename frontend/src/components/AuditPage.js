import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Shield, RefreshCw, Search, Loader2, User, FileText, Clock } from 'lucide-react';

export const AuditPage = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    user_id: '',
    resource_type: '',
    action: ''
  });

  const canView = ['developer', 'gs', 'zgs'].includes(user?.role);

  useEffect(() => {
    if (canView) {
      loadLogs();
    }
  }, [canView]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter.user_id) params.append('user_id', filter.user_id);
      if (filter.resource_type) params.append('resource_type', filter.resource_type);
      if (filter.action) params.append('action', filter.action);
      
      const queryString = params.toString();
      const url = `/api/audit/logs${queryString ? `?${queryString}` : ''}`;
      const data = await api.get(url);
      setLogs(data);
    } catch (error) {
      console.error('Error loading audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActionLabel = (action) => {
    const labels = {
      'user_login': 'Вход в систему',
      'user_logout': 'Выход из системы',
      'user_registered': 'Регистрация',
      '2fa_enabled': '2FA включена',
      'department_created': 'Создан отдел',
      'department_updated': 'Обновлен отдел',
      'department_deleted': 'Удален отдел',
      'week_created': 'Создана неделя',
      'table_data_updated': 'Обновлены данные таблицы',
      'lecture_topic_created': 'Создана тема лекции',
      'lecture_topic_deleted': 'Удалена тема лекции',
      'training_topic_created': 'Создана тема тренировки',
      'training_topic_deleted': 'Удалена тема тренировки',
      'factions_initialized': 'Инициализированы фракции'
    };
    return labels[action] || action;
  };

  const getResourceTypeLabel = (type) => {
    const labels = {
      'auth': 'Авторизация',
      'user': 'Пользователь',
      'department': 'Отдел',
      'faction': 'Фракция',
      'week': 'Неделя',
      'table_data': 'Данные таблицы',
      'lecture_topic': 'Тема лекции',
      'training_topic': 'Тема тренировки'
    };
    return labels[type] || type;
  };

  const getActionColor = (action) => {
    if (action.includes('created') || action.includes('registered')) return 'bg-green-500/20 text-green-700 dark:text-green-400';
    if (action.includes('deleted')) return 'bg-red-500/20 text-red-700 dark:text-red-400';
    if (action.includes('updated')) return 'bg-blue-500/20 text-blue-700 dark:text-blue-400';
    if (action.includes('login')) return 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-400';
    if (action.includes('logout')) return 'bg-orange-500/20 text-orange-700 dark:text-orange-400';
    return 'bg-gray-500/20 text-gray-700 dark:text-gray-400';
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (!canView) {
    return (
      <div className="container py-8">
        <Alert variant="destructive">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            У вас нет доступа к журналу действий. Эта функция доступна только администраторам.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="audit-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Журнал действий</h1>
          <p className="text-muted-foreground">История всех действий в системе</p>
        </div>
        <Button onClick={loadLogs} disabled={loading} data-testid="refresh-logs">
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Обновить
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="h-5 w-5" />
            Фильтры
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <Select value={filter.resource_type} onValueChange={(v) => setFilter(f => ({...f, resource_type: v}))}>
                <SelectTrigger data-testid="filter-resource-type">
                  <SelectValue placeholder="Тип ресурса" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Все типы</SelectItem>
                  <SelectItem value="auth">Авторизация</SelectItem>
                  <SelectItem value="user">Пользователь</SelectItem>
                  <SelectItem value="department">Отдел</SelectItem>
                  <SelectItem value="faction">Фракция</SelectItem>
                  <SelectItem value="week">Неделя</SelectItem>
                  <SelectItem value="table_data">Данные таблицы</SelectItem>
                  <SelectItem value="lecture_topic">Тема лекции</SelectItem>
                  <SelectItem value="training_topic">Тема тренировки</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Input
                placeholder="ID пользователя"
                value={filter.user_id}
                onChange={(e) => setFilter(f => ({...f, user_id: e.target.value}))}
                data-testid="filter-user-id"
              />
            </div>
            <div>
              <Button onClick={loadLogs} className="w-full">
                <Search className="mr-2 h-4 w-4" />
                Поиск
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="mx-auto h-12 w-12 mb-4" />
              <p>Нет записей в журнале</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left p-4 font-semibold">Время</th>
                    <th className="text-left p-4 font-semibold">Пользователь</th>
                    <th className="text-left p-4 font-semibold">Действие</th>
                    <th className="text-left p-4 font-semibold">Ресурс</th>
                    <th className="text-left p-4 font-semibold">IP</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, index) => (
                    <tr key={log.id} className="border-b hover:bg-muted/20" data-testid={`audit-log-${index}`}>
                      <td className="p-4">
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          {formatDate(log.timestamp)}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">{log.user_email}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge className={getActionColor(log.action)}>
                          {getActionLabel(log.action)}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex flex-col gap-1">
                          <span className="text-sm font-medium">{getResourceTypeLabel(log.resource_type)}</span>
                          <span className="text-xs text-muted-foreground">{log.resource_id.substring(0, 8)}...</span>
                        </div>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {log.ip_address || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <p className="text-sm text-muted-foreground text-center">
        Показано {logs.length} записей
      </p>
    </div>
  );
};
