import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { User, Moon, Sun } from 'lucide-react';

export const SettingsPage = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const getRoleLabel = (role) => {
    const roleMap = {
      developer: 'Разработчик',
      gs: 'ГС',
      zgs: 'ЗГС',
      leader_gov: 'Лидер Правительство',
      leader_fsb: 'Лидер ФСБ',
      leader_gibdd: 'Лидер ГИБДД',
      leader_umvd: 'Лидер УМВД',
      leader_army: 'Лидер Армия',
      leader_hospital: 'Лидер Больница',
      leader_smi: 'Лидер СМИ',
      leader_fsin: 'Лидер ФСИН',
      head_of_department: 'Начальник отдела',
      deputy_head: 'Заместитель'
    };
    return roleMap[role] || role;
  };

  return (
    <div className="container py-8 space-y-6" data-testid="settings-page">
      <h1 className="text-3xl font-bold">Настройки</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Профиль
            </CardTitle>
            <CardDescription>Информация о вашем аккаунте</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm text-muted-foreground">Имя</Label>
              <p className="font-medium">{user?.full_name}</p>
            </div>
            <div>
              <Label className="text-sm text-muted-foreground">Email</Label>
              <p className="font-medium">{user?.email}</p>
            </div>
            <div>
              <Label className="text-sm text-muted-foreground">Роль</Label>
              <div className="mt-1">
                <Badge>{getRoleLabel(user?.role)}</Badge>
              </div>
            </div>
            {user?.vk_url && (
              <div>
                <Label className="text-sm text-muted-foreground">VK</Label>
                <a href={user.vk_url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  {user.vk_url}
                </a>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Внешний вид</CardTitle>
            <CardDescription>Настройте тему интерфейса</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                <div>
                  <Label>Тёмная тема</Label>
                  <p className="text-sm text-muted-foreground">
                    {theme === 'dark' ? 'Включена' : 'Выключена'}
                  </p>
                </div>
              </div>
              <Switch checked={theme === 'dark'} onCheckedChange={toggleTheme} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Двухфакторная аутентификация</CardTitle>
            <CardDescription>Дополнительная защита аккаунта</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                2FA {user?.two_fa_enabled ? 'включена' : 'отключена'} для вашего аккаунта.
              </p>
              <Button variant="outline" disabled>
                Настроить 2FA
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Уведомления</CardTitle>
            <CardDescription>Управление уведомлениями</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Настройки уведомлений будут доступны в следующей версии.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
