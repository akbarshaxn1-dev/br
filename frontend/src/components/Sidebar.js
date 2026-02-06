import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { cn } from '../lib/utils';
import {
  LayoutDashboard,
  Building2,
  Shield,
  Users,
  FileText,
  Settings,
  ClipboardList,
  History
} from 'lucide-react';

export const Sidebar = () => {
  const { user } = useAuth();

  const canAccessAllFactions = ['developer', 'gs', 'zgs'].includes(user?.role);
  const canViewAudit = ['developer', 'gs', 'zgs'].includes(user?.role);

  const navItems = [
    {
      title: 'Главная',
      href: '/',
      icon: LayoutDashboard,
      show: true
    },
    {
      title: 'Фракции',
      href: '/factions',
      icon: Building2,
      show: canAccessAllFactions
    },
    {
      title: 'Отделы',
      href: '/departments',
      icon: Users,
      show: true
    },
    {
      title: 'Таблицы',
      href: '/tables',
      icon: FileText,
      show: true
    },
    {
      title: 'Лекции и Тренировки',
      href: '/topics',
      icon: ClipboardList,
      show: user?.role?.startsWith('leader_') || canAccessAllFactions
    },
    {
      title: 'Журнал действий',
      href: '/audit',
      icon: History,
      show: canViewAudit
    },
    {
      title: 'Настройки',
      href: '/settings',
      icon: Settings,
      show: true
    }
  ];

  return (
    <aside className="w-64 border-r border-border bg-card min-h-[calc(100vh-4rem)] p-4" data-testid="sidebar">
      <nav className="space-y-1">
        {navItems
          .filter(item => item.show)
          .map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
              data-testid={`nav-${item.href.replace('/', '')}`}
            >
              <item.icon className="h-5 w-5" />
              {item.title}
            </NavLink>
          ))}
      </nav>
    </aside>
  );
};
