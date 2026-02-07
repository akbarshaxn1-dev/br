import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { cn } from '../lib/utils';
import { Button } from './ui/button';
import {
  LayoutDashboard,
  Building2,
  Users,
  FileText,
  Settings,
  ClipboardList,
  History,
  UserCog,
  Menu,
  X
} from 'lucide-react';

export const Sidebar = ({ isOpen, onClose }) => {
  const { user } = useAuth();

  const canAccessAllFactions = ['developer', 'gs', 'zgs'].includes(user?.role);
  const canViewAudit = ['developer', 'gs', 'zgs'].includes(user?.role);
  const canAccessAdmin = ['developer', 'gs', 'zgs'].includes(user?.role);

  const navItems = [
    { title: 'Главная', href: '/', icon: LayoutDashboard, show: true },
    { title: 'Фракции', href: '/factions', icon: Building2, show: canAccessAllFactions },
    { title: 'Отделы', href: '/departments', icon: Users, show: true },
    { title: 'Таблицы', href: '/tables', icon: FileText, show: true },
    { title: 'Лекции', href: '/topics', icon: ClipboardList, show: user?.role?.startsWith('leader_') || canAccessAllFactions || user?.role === 'head_of_department' },
    { title: 'Логи', href: '/audit', icon: History, show: canViewAudit },
    { title: 'Админка', href: '/admin', icon: UserCog, show: canAccessAdmin },
    { title: 'Настройки', href: '/settings', icon: Settings, show: true }
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden" 
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={cn(
          "fixed lg:static inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-200 ease-in-out lg:transform-none",
          "pt-16 lg:pt-0 min-h-[calc(100vh-4rem)]",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
        data-testid="sidebar"
      >
        {/* Mobile close button */}
        <div className="lg:hidden absolute top-4 right-4">
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.filter(item => item.show).map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
              data-testid={`nav-${item.href.replace('/', '') || 'home'}`}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              <span className="truncate">{item.title}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export const MobileMenuButton = ({ onClick }) => (
  <Button variant="ghost" size="icon" className="lg:hidden" onClick={onClick}>
    <Menu className="h-6 w-6" />
  </Button>
);
