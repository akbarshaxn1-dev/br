import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ArrowLeft, Calendar, FileText, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export const WeekArchivePage = () => {
  const { departmentId } = useParams();
  const { user } = useAuth();
  const [department, setDepartment] = useState(null);
  const [faction, setFaction] = useState(null);
  const [weeks, setWeeks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [departmentId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Get department info
      const deptResponse = await api.get(`/api/departments/${departmentId}`);
      setDepartment(deptResponse);
      
      // Get faction info
      const factionResponse = await api.get(`/api/factions/${deptResponse.faction_code || 'fsb'}`);
      setFaction(factionResponse);
      
      // Get all weeks
      const weeksResponse = await api.get(`/api/weeks/department/${departmentId}`);
      setWeeks(weeksResponse);
      
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const formatWeekPeriod = (start, end) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    return `${startDate.getDate().toString().padStart(2, '0')}.${(startDate.getMonth() + 1).toString().padStart(2, '0')} - ${endDate.getDate().toString().padStart(2, '0')}.${(endDate.getMonth() + 1).toString().padStart(2, '0')}.${endDate.getFullYear()}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-4 sm:py-8 px-4 space-y-4 sm:space-y-6" data-testid="week-archive-page">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <Link to={`/department/${departmentId}`}>
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-xl sm:text-3xl font-bold">Архив недель</h1>
          <p className="text-sm text-muted-foreground">
            {department?.name} | {faction?.name}
          </p>
        </div>
      </div>

      {weeks.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Нет сохранённых недель</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:gap-4">
          {weeks.map((week) => (
            <Card key={week.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Calendar className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm sm:text-base">
                        {formatWeekPeriod(week.week_start, week.week_end)}
                      </p>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        Создано: {formatDate(week.created_at)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 sm:gap-3">
                    {week.is_current && (
                      <Badge className="bg-green-500/10 text-green-600 border-green-500/30">
                        Текущая
                      </Badge>
                    )}
                    <Link to={`/department/${departmentId}/week/${week.id}`}>
                      <Button size="sm" variant={week.is_current ? "default" : "outline"}>
                        <FileText className="h-4 w-4 mr-1 sm:mr-2" />
                        <span className="hidden sm:inline">Открыть</span>
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
