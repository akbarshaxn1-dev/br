import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';
import { api } from '../utils/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { ArrowLeft, Save, Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

export const DepartmentPage = () => {
  const { departmentId } = useParams();
  const { user } = useAuth();
  const { joinDepartment, leaveDepartment, on, off } = useWebSocket();
  const [department, setDepartment] = useState(null);
  const [currentWeek, setCurrentWeek] = useState(null);
  const [tableData, setTableData] = useState({ rows: [] });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
    joinDepartment(departmentId);

    // Listen for real-time updates
    const handleTableUpdate = (data) => {
      if (data.department_id === departmentId) {
        toast.info('Таблица обновлена другим пользователем');
        loadTableData();
      }
    };

    on('table_updated', handleTableUpdate);

    return () => {
      leaveDepartment(departmentId);
      off('table_updated', handleTableUpdate);
    };
  }, [departmentId]);

  const loadData = async () => {
    try {
      const weekRes = await weeksService.getCurrent(departmentId);
      setCurrentWeek(weekRes.data);
      await loadTableData(weekRes.data.id);
    } catch (error) {
      console.error('Error loading department data:', error);
      toast.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async (weekId = currentWeek?.id) => {
    if (!weekId) return;
    try {
      const res = await weeksService.getTableData(weekId);
      setTableData(res.data);
    } catch (error) {
      console.error('Error loading table data:', error);
    }
  };

  const handleSave = async () => {
    if (!currentWeek) return;
    
    setSaving(true);
    try {
      await weeksService.updateTableData(currentWeek.id, tableData);
      toast.success('Таблица сохранена');
    } catch (error) {
      console.error('Error saving table:', error);
      toast.error('Ошибка сохранения таблицы');
    } finally {
      setSaving(false);
    }
  };

  const addRow = () => {
    setTableData(prev => ({
      ...prev,
      rows: [...prev.rows, {
        employee_name: '',
        cells: {
          monday: false,
          tuesday: false,
          wednesday: false,
          thursday: false,
          friday: false,
          saturday: false,
          sunday: false
        }
      }]
    }));
  };

  const removeRow = (index) => {
    setTableData(prev => ({
      ...prev,
      rows: prev.rows.filter((_, i) => i !== index)
    }));
  };

  const updateRow = (index, field, value) => {
    setTableData(prev => {
      const newRows = [...prev.rows];
      if (field === 'employee_name') {
        newRows[index].employee_name = value;
      } else {
        newRows[index].cells[field] = value;
      }
      return { ...prev, rows: newRows };
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="department-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Таблица отдела</h1>
            <p className="text-muted-foreground">
              Неделя {currentWeek ? new Date(currentWeek.week_start).toLocaleDateString('ru') : ''}
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={addRow} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Добавить сотрудника
          </Button>
          <Button onClick={handleSave} disabled={saving} data-testid="save-table-button">
            <Save className="mr-2 h-4 w-4" />
            {saving ? 'Сохранение...' : 'Сохранить'}
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left font-semibold min-w-[200px]">Сотрудник</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Пн</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Вт</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Ср</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Чт</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Пт</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Сб</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Вс</th>
                  <th className="px-4 py-3 text-center font-semibold w-[80px]">Действия</th>
                </tr>
              </thead>
              <tbody>
                {tableData.rows.length === 0 ? (
                  <tr>
                    <td colSpan="9" className="px-4 py-12 text-center text-muted-foreground">
                      Нет данных. Добавьте сотрудников.
                    </td>
                  </tr>
                ) : (
                  tableData.rows.map((row, index) => (
                    <tr key={index} className="border-b hover:bg-muted/30 transition-colors" data-testid={`table-row-${index}`}>
                      <td className="px-4 py-3">
                        <Input
                          value={row.employee_name}
                          onChange={(e) => updateRow(index, 'employee_name', e.target.value)}
                          placeholder="Имя сотрудника"
                          className="border-none bg-transparent"
                        />
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.monday || false}
                            onCheckedChange={(checked) => updateRow(index, 'monday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.tuesday || false}
                            onCheckedChange={(checked) => updateRow(index, 'tuesday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.wednesday || false}
                            onCheckedChange={(checked) => updateRow(index, 'wednesday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.thursday || false}
                            onCheckedChange={(checked) => updateRow(index, 'thursday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.friday || false}
                            onCheckedChange={(checked) => updateRow(index, 'friday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.saturday || false}
                            onCheckedChange={(checked) => updateRow(index, 'saturday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex justify-center">
                          <Checkbox
                            checked={row.cells.sunday || false}
                            onCheckedChange={(checked) => updateRow(index, 'sunday', checked)}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeRow(index)}
                          data-testid={`delete-row-${index}`}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
