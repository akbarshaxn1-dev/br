import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Users, Loader2, Building2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DepartmentsListPage = () => {
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
      
      // Auto-select faction for leaders or user's faction
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="departments-list-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Все отделы</h1>
          <p className="text-muted-foreground">
            {selectedFaction ? `Отделы фракции ${getFactionName(selectedFaction)}` : 'Выберите фракцию'}
          </p>
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
                  Перейти к фракции
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {departments.map((dept) => (
            <Card key={dept.id} className="hover:shadow-lg transition-shadow" data-testid={`department-card-${dept.id}`}>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Users className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{dept.name}</CardTitle>
                    <CardDescription className="text-xs">
                      {getFactionName(selectedFaction)} | ID: {dept.id.substring(0, 8)}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Link to={`/department/${dept.id}`}>
                  <Button className="w-full" data-testid={`view-department-${dept.id}`}>
                    Открыть таблицу
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
