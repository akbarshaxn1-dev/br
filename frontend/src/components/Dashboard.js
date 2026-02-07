import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Building2, Users, FileText, BarChart3, Shield, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user } = useAuth();
  const [factions, setFactions] = useState([]);
  const [stats, setStats] = useState({ departments: 0, tables: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await api.get('/api/factions/');
      setFactions(data);
      
      // Calculate stats
      let deptCount = 0;
      for (const faction of data) {
        try {
          const depts = await api.get(`/api/departments/faction/${faction.code}`);
          deptCount += depts.length;
        } catch {}
      }
      setStats({ departments: deptCount, tables: deptCount });
    } catch (error) {
      console.error('Error loading factions:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-4 sm:py-8 px-4 space-y-6 sm:space-y-8" data-testid="dashboard">
      <div>
        <h1 className="text-xl sm:text-3xl font-bold mb-2">Добро пожаловать, {user?.full_name}!</h1>
        <p className="text-sm text-muted-foreground">
          Система управления отделами фракций
        </p>
      </div>

      <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 sm:p-6">
            <CardTitle className="text-xs sm:text-sm font-medium">Фракции</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-6 pt-0">
            <div className="text-xl sm:text-2xl font-bold">{factions.length}</div>
            <p className="text-xs text-muted-foreground hidden sm:block">Активных фракций</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 sm:p-6">
            <CardTitle className="text-xs sm:text-sm font-medium">Отделы</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-6 pt-0">
            <div className="text-xl sm:text-2xl font-bold">{stats.departments}</div>
            <p className="text-xs text-muted-foreground hidden sm:block">Всего отделов</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 sm:p-6">
            <CardTitle className="text-xs sm:text-sm font-medium">Таблицы</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-6 pt-0">
            <div className="text-xl sm:text-2xl font-bold">{stats.tables}</div>
            <p className="text-xs text-muted-foreground hidden sm:block">Активных таблиц</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 p-3 sm:p-6">
            <CardTitle className="text-xs sm:text-sm font-medium">Статус</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-6 pt-0">
            <div className="text-xl sm:text-2xl font-bold text-green-600">OK</div>
            <p className="text-xs text-muted-foreground hidden sm:block">Система работает</p>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-lg sm:text-2xl font-bold mb-4">Доступные фракции</h2>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {factions.map((faction) => (
              <Card key={faction.id} className="hover:shadow-lg transition-shadow" data-testid={`faction-card-${faction.code}`}>
                <CardHeader className="p-4 sm:p-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <CardTitle className="text-base sm:text-lg truncate">{faction.name}</CardTitle>
                      <CardDescription className="text-xs">{faction.code.toUpperCase()}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-4 sm:p-6 pt-0">
                  <Link to={`/faction/${faction.code}`}>
                    <Button className="w-full" size="sm" data-testid={`view-faction-${faction.code}`}>
                      Перейти
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
