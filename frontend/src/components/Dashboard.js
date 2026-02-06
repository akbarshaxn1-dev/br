import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiFetch } from '../utils/api-helper';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Building2, Users, FileText, BarChart3, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard = () => {
  const { user } = useAuth();
  const [factions, setFactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFactions();
  }, []);

  const loadFactions = async () => {
    try {
      console.log('Loading factions via direct fetch...');
      const token = localStorage.getItem('access_token');
      const response = await fetch('https://dept-manager-4.preview.emergentagent.com/api/factions', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Factions loaded:', data.length);
      setFactions(data);
    } catch (error) {
      console.error('Error loading factions:', error);
    } finally {
      setLoading(false);
    }
  };

  const canAccessAllFactions = ['developer', 'gs', 'zgs'].includes(user?.role);

  return (
    <div className="container py-8 space-y-8" data-testid="dashboard">
      <div>
        <h1 className="text-3xl font-bold mb-2">Добро пожаловать, {user?.full_name}!</h1>
        <p className="text-muted-foreground">
          Система управления отделами фракций
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Фракции</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{factions.length}</div>
            <p className="text-xs text-muted-foreground">Активных фракций</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Отделы</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-</div>
            <p className="text-xs text-muted-foreground">Всего отделов</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Таблицы</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">-</div>
            <p className="text-xs text-muted-foreground">Активных таблиц</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Активность</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">100%</div>
            <p className="text-xs text-muted-foreground">Система работает</p>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-4">Доступные фракции</h2>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="spinner"></div>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {factions.map((faction) => (
              <Card key={faction.id} className="hover:shadow-lg transition-shadow" data-testid={`faction-card-${faction.code}`}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                      <Shield className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle>{faction.name}</CardTitle>
                      <CardDescription className="text-xs">Код: {faction.code.toUpperCase()}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">{faction.description}</p>
                  <Link to={`/faction/${faction.code}`}>
                    <Button className="w-full" data-testid={`view-faction-${faction.code}`}>
                      Перейти к фракции
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
