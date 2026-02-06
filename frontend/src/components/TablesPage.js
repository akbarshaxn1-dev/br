import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { FileText, Loader2, Calendar, Building2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const TablesPage = () => {
  const { user } = useAuth();
  const [factions, setFactions] = useState([]);
  const [selectedFaction, setSelectedFaction] = useState('');
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDepts, setLoadingDepts] = useState(false);

  const canSelectFaction = ['developer', 'gs', 'zgs'].includes(user?.role);

  useEffect(() => {
    loadFactions();
  }, []);

  useEffect(() => {
    if (selectedFaction) {
      loadDepartments();
    }
  }, [selectedFaction]);

  const loadFactions = async () => {
    try {
      const data = await api.get('/api/factions/');
      setFactions(data);
      
      if (user?.faction) {
        setSelectedFaction(user.faction);
      } else if (data.length > 0) {
        setSelectedFaction(data[0].code);
      }
    } catch (error) {
      console.error('Error loading factions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    setLoadingDepts(true);
    try {
      const data = await api.get(`/api/departments/faction/${selectedFaction}`);
      setDepartments(data);
    } catch (error) {
      console.error('Error loading departments:', error);
      setDepartments([]);
    } finally {
      setLoadingDepts(false);
    }
  };

  const getFactionName = (code) => {
    const faction = factions.find(f => f.code === code);
    return faction?.name || code;
  };

  const getCurrentWeekLabel = () => {
    const now = new Date();
    const monday = new Date(now);
    monday.setDate(monday.getDate() - monday.getDay() + 1);
    const sunday = new Date(monday);
    sunday.setDate(sunday.getDate() + 6);
    
    return `${monday.getDate().toString().padStart(2, '0')}.${(monday.getMonth() + 1).toString().padStart(2, '0')} - ${sunday.getDate().toString().padStart(2, '0')}.${(sunday.getMonth() + 1).toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="tables-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Таблицы отделов</h1>
          <p className="text-muted-foreground">Быстрый доступ к таблицам всех отделов</p>
        </div>
        
        {canSelectFaction && (
          <div className="w-64">
            <Select value={selectedFaction} onValueChange={setSelectedFaction}>
              <SelectTrigger data-testid="faction-selector">
                <SelectValue placeholder="Выберите фракцию" />
              </SelectTrigger>
              <SelectContent>
                {factions.map(faction => (
                  <SelectItem key={faction.code} value={faction.code}>
                    {faction.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* Current Week Info */}
      <Card className="bg-primary/5 border-primary/20">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-primary" />
              <div>
                <p className="font-medium">Текущая неделя</p>
                <p className="text-sm text-muted-foreground">{getCurrentWeekLabel()}</p>
              </div>
            </div>
            <Badge variant="outline" className="bg-green-500/10 text-green-600 border-green-500/30">
              Активна
            </Badge>
          </div>
        </CardContent>
      </Card>

      {loadingDepts ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : departments.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center space-y-3">
              <Building2 className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="text-muted-foreground">
                Нет отделов в выбранной фракции
              </p>
              <Link to={`/faction/${selectedFaction}`}>
                <Button>
                  Создать отдел
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {departments.map((dept) => (
            <Card key={dept.id} className="hover:shadow-lg transition-shadow" data-testid={`table-card-${dept.id}`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{dept.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {getFactionName(selectedFaction)}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Период:</span>
                  <span className="font-medium">{getCurrentWeekLabel()}</span>
                </div>
                <Link to={`/department/${dept.id}`}>
                  <Button className="w-full" data-testid={`open-table-${dept.id}`}>
                    Открыть таблицу
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Архив таблиц</CardTitle>
          <CardDescription>
            История таблиц за прошлые недели будет доступна в следующей версии
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
};
