import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Moon, Sun, Bell, LogOut, User } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Badge } from './ui/badge';

export const Header = () => {
  const { user, logout } = useAuth();
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

  const getFactionLabel = (faction) => {
    const factionMap = {
      gov: 'Правительство',
      fsb: 'ФСБ',
      gibdd: 'ГИБДД',
      umvd: 'УМВД',
      army: 'Армия',
      hospital: 'Больница',
      smi: 'СМИ',
      fsin: 'ФСИН'
    };
    return factionMap[faction] || faction;
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60" data-testid="main-header">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-primary">ЕП</span>
            </div>
            <div>
              <h1 className="text-lg font-bold">Единый Портал</h1>
              <p className="text-xs text-muted-foreground">Управление отделами</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            data-testid="theme-toggle-button"
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          <Button variant="ghost" size="icon" data-testid="notifications-button">
            <Bell className="h-5 w-5" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2" data-testid="user-menu-button">
                <User className="h-4 w-4" />
                <span className="hidden sm:inline">{user?.full_name}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{user?.full_name}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem disabled>
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs">Роль:</span>
                    <Badge variant="secondary" className="text-xs">{getRoleLabel(user?.role)}</Badge>
                  </div>
                  {user?.faction && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs">Фракция:</span>
                      <Badge variant="outline" className="text-xs">{getFactionLabel(user?.faction)}</Badge>
                    </div>
                  )}
                </div>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-destructive" data-testid="logout-button">
                <LogOut className="mr-2 h-4 w-4" />
                Выход
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
