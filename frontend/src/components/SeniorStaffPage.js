import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { ArrowLeft, Save, Plus, Trash2, Loader2, RefreshCw, Users, Award, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

export const SeniorStaffPage = () => {
  const { factionCode } = useParams();
  const { user } = useAuth();
  const [faction, setFaction] = useState(null);
  const [tableData, setTableData] = useState({ rows: [] });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Check if user can edit senior staff table
  const canEdit = 
    user?.role === 'developer' || 
    user?.role === 'gs' || 
    user?.role === 'zgs' ||
    user?.role === `leader_${factionCode}`;

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Get faction info
      const factionResponse = await api.get(`/api/factions/${factionCode}`);
      setFaction(factionResponse);
      
      // Get senior staff table
      const tableResponse = await api.get(`/api/senior-staff/faction/${factionCode}`);
      setTableData(tableResponse);
      
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  }, [factionCode]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put(`/api/senior-staff/faction/${factionCode}`, {
        rows: tableData.rows
      });
      toast.success('Таблица сохранена');
      setHasChanges(false);
    } catch (error) {
      console.error('Error saving:', error);
      toast.error('Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const addRow = () => {
    const newRow = {
      employee_name: '',
      points: 0,
      norm_status: 'not_met',
      penalties: [],
      notes: ''
    };
    
    setTableData(prev => ({
      ...prev,
      rows: [...prev.rows, newRow]
    }));
    setHasChanges(true);
  };

  const removeRow = (index) => {
    setTableData(prev => ({
      ...prev,
      rows: prev.rows.filter((_, i) => i !== index)
    }));
    setHasChanges(true);
    toast.success('Сотрудник удален');
  };

  const updateRow = (index, field, value) => {
    setTableData(prev => ({
      ...prev,
      rows: prev.rows.map((row, i) => {
        if (i === index) {
          return { ...row, [field]: value };
        }
        return row;
      })
    }));
    setHasChanges(true);
  };

  const getNormStatusColor = (status) => {
    if (status === 'met') return 'bg-green-500/20 text-green-700 dark:text-green-400 border-green-500/30';
    if (status === 'exceeded') return 'bg-blue-500/20 text-blue-700 dark:text-blue-400 border-blue-500/30';
    return 'bg-red-500/20 text-red-700 dark:text-red-400 border-red-500/30';
  };

  const getPointsColor = (points) => {
    if (points >= 100) return 'text-green-500';
    if (points >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-4 sm:py-8 px-4 space-y-4 sm:space-y-6" data-testid="senior-staff-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3 sm:gap-4">
          <Link to={`/faction/${factionCode}`}>
            <Button variant="outline" size="icon" data-testid="back-button">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-xl sm:text-3xl font-bold flex items-center gap-2">
              <Users className="h-6 w-6 text-amber-500" />
              Старший состав
            </h1>
            <p className="text-sm text-muted-foreground">{faction?.name}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2">
          <Button onClick={loadData} variant="outline" size="sm" data-testid="refresh-button">
            <RefreshCw className="h-4 w-4 sm:mr-2" />
            <span className="hidden sm:inline">Обновить</span>
          </Button>
          {canEdit && (
            <>
              <Button onClick={addRow} variant="outline" size="sm" data-testid="add-row-button">
                <Plus className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Добавить</span>
              </Button>
              <Button 
                onClick={handleSave} 
                disabled={saving || !hasChanges} 
                data-testid="save-button"
                size="sm"
                className={hasChanges ? 'bg-green-600 hover:bg-green-700' : ''}
              >
                {saving ? (
                  <Loader2 className="h-4 w-4 sm:mr-2 animate-spin" />
                ) : (
                  <Save className="h-4 w-4 sm:mr-2" />
                )}
                <span className="hidden sm:inline">{saving ? 'Сохранение...' : 'Сохранить'}</span>
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Legend */}
      <Card className="bg-muted/30">
        <CardContent className="py-3">
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500/20 text-green-700 border-green-500/30">Выполнено</Badge>
              <span className="text-muted-foreground">норма выполнена</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/30">Перевыполнено</Badge>
              <span className="text-muted-foreground">норма перевыполнена</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-red-500/20 text-red-700 border-red-500/30">Не выполнено</Badge>
              <span className="text-muted-foreground">норма не выполнена</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader className="bg-amber-500/10 border-b py-3 sm:py-4">
          <CardTitle className="text-amber-600 dark:text-amber-500 text-center text-base sm:text-xl flex items-center justify-center gap-2">
            <Award className="h-5 w-5" />
            СТАРШИЙ СОСТАВ {faction?.name?.toUpperCase()}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="bg-muted/50 border-b-2">
                  <th className="px-3 py-3 text-left font-bold border-r min-w-[150px] sticky left-0 bg-muted/50 z-10">
                    Ник
                  </th>
                  <th className="px-3 py-3 text-center font-bold border-r min-w-[100px]">
                    Баллы
                  </th>
                  <th className="px-3 py-3 text-center font-bold border-r min-w-[140px]">
                    Статус нормы
                  </th>
                  <th className="px-3 py-3 text-center font-bold border-r min-w-[200px]">
                    Взыскания
                  </th>
                  <th className="px-3 py-3 text-center font-bold min-w-[200px]">
                    Заметки
                  </th>
                  {canEdit && (
                    <th className="px-2 py-3 text-center font-bold w-[60px]">
                      
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {tableData.rows.length === 0 ? (
                  <tr>
                    <td colSpan={canEdit ? 6 : 5} className="text-center py-8 text-muted-foreground">
                      <div className="flex flex-col items-center gap-2">
                        <Users className="h-8 w-8 opacity-50" />
                        <p>Нет данных о старшем составе</p>
                        {canEdit && (
                          <Button onClick={addRow} variant="outline" size="sm">
                            <Plus className="h-4 w-4 mr-2" />
                            Добавить сотрудника
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  tableData.rows.map((row, rowIdx) => (
                    <tr key={rowIdx} className="border-b hover:bg-muted/20 transition-colors">
                      <td className="px-3 py-2 border-r sticky left-0 bg-background z-10">
                        <Input
                          value={row.employee_name}
                          onChange={(e) => updateRow(rowIdx, 'employee_name', e.target.value)}
                          placeholder="Введите ник"
                          className="min-w-[140px] h-9 text-sm border-none bg-transparent"
                          disabled={!canEdit}
                          data-testid={`employee-name-${rowIdx}`}
                        />
                      </td>
                      
                      <td className="px-3 py-2 border-r text-center">
                        <Input
                          type="number"
                          value={row.points}
                          onChange={(e) => updateRow(rowIdx, 'points', parseInt(e.target.value) || 0)}
                          className={`w-20 h-9 text-center font-bold mx-auto ${getPointsColor(row.points)}`}
                          disabled={!canEdit}
                          min="0"
                          data-testid={`points-${rowIdx}`}
                        />
                      </td>

                      <td className="px-2 py-2 border-r">
                        <Select
                          value={row.norm_status}
                          onValueChange={(value) => updateRow(rowIdx, 'norm_status', value)}
                          disabled={!canEdit}
                        >
                          <SelectTrigger 
                            className={`h-9 text-xs font-medium border ${getNormStatusColor(row.norm_status)}`}
                            data-testid={`norm-status-${rowIdx}`}
                          >
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="not_met" className="text-xs">
                              <span className="text-red-600 font-medium">Не выполнено</span>
                            </SelectItem>
                            <SelectItem value="met" className="text-xs">
                              <span className="text-green-600 font-medium">Выполнено</span>
                            </SelectItem>
                            <SelectItem value="exceeded" className="text-xs">
                              <span className="text-blue-600 font-medium">Перевыполнено</span>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </td>

                      <td className="px-2 py-2 border-r">
                        <Input
                          value={row.penalties?.length > 0 ? row.penalties.map(p => p.reason || p).join(', ') : ''}
                          onChange={(e) => updateRow(rowIdx, 'penalties', e.target.value.split(',').map(s => ({ reason: s.trim() })).filter(p => p.reason))}
                          placeholder="Взыскания (через запятую)"
                          className="h-9 text-xs"
                          disabled={!canEdit}
                          data-testid={`penalties-${rowIdx}`}
                        />
                      </td>

                      <td className="px-2 py-2">
                        <Input
                          value={row.notes || ''}
                          onChange={(e) => updateRow(rowIdx, 'notes', e.target.value)}
                          placeholder="Заметки"
                          className="h-9 text-xs"
                          disabled={!canEdit}
                          data-testid={`notes-${rowIdx}`}
                        />
                      </td>

                      {canEdit && (
                        <td className="px-2 py-2 text-center">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeRow(rowIdx)}
                            className="h-8 w-8"
                            data-testid={`remove-row-${rowIdx}`}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Status bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 text-xs sm:text-sm text-muted-foreground">
        <p>{saving ? 'Сохранение...' : hasChanges ? '⚠️ Есть несохраненные изменения' : '✓ Сохранено'}</p>
        <p>Всего сотрудников: {tableData.rows.length}</p>
      </div>
    </div>
  );
};
