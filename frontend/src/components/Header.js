import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Moon, Sun, Bell, LogOut, User, Menu } from 'lucide-react';
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

export const Header = ({ onMenuClick }) => {
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

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60" data-testid="main-header">
      <div className="flex h-14 lg:h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          {/* Mobile menu button */}
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenuClick} data-testid="mobile-menu-btn">
            <Menu className="h-6 w-6" />
          </Button>
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 lg:w-10 lg:h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <span className="text-lg lg:text-xl font-bold text-primary">ЕП</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-base lg:text-lg font-bold leading-tight">Единый Портал</h1>
              <p className="text-xs text-muted-foreground hidden md:block">Управление отделами</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} data-testid="theme-toggle-button">
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          <Button variant="ghost" size="icon" className="hidden sm:flex" data-testid="notifications-button">
            <Bell className="h-5 w-5" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-1 sm:gap-2 px-2 sm:px-3" data-testid="user-menu-button">
                <User className="h-4 w-4" />
                <span className="hidden md:inline max-w-[100px] truncate">{user?.full_name}</span>
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
                <Badge variant="secondary" className="text-xs">{getRoleLabel(user?.role)}</Badge>
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
