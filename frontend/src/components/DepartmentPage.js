import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';
import { xhrApi } from '../utils/xhr-api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ArrowLeft, Save, Plus, Trash2, Download } from 'lucide-react';
import { toast } from 'sonner';

// Mock темы (в реальности будут загружаться из API)
const mockLectureTopics = ['УК РФ', 'КоАП', 'ФЗ', 'УПК', 'Устав'];
const mockTrainingTopics = ['Закрепление', 'Доверс', 'Писпен', 'Обыск'];

export const DepartmentPage = () => {
  const { departmentId } = useParams();
  const { user } = useAuth();
  const { joinDepartment, leaveDepartment } = useWebSocket();
  const [department] = useState({ name: 'Отдел контрразведки', faction: 'ФСБ' });
  const [currentWeek] = useState({
    week_start: '2025-02-02',
    week_end: '2025-02-08'
  });
  const [tableData, setTableData] = useState({
    rows: [
      {
        id: 1,
        nickname: 'Vadim_Smirnov',
        lectures: { 'УК РФ': 'present', 'КоАП': 'present', 'ФЗ': 'absent', 'УПК': 'present', 'Устав': 'present' },
        trainings: { 'Закрепление': 'present', 'Доверс': 'present', 'Писпен': 'absent', 'Обыск': 'present' },
        attestation: 'passed',
        days_count: 15
      },
      {
        id: 2,
        nickname: 'Ivan_Petrov',
        lectures: { 'УК РФ': 'present', 'КоАП': 'absent', 'ФЗ': 'present', 'УПК': 'absent', 'Устав': 'present' },
        trainings: { 'Закрепление': 'present', 'Доверс': 'present', 'Писпен': 'present', 'Обыск': 'absent' },
        attestation: 'not_passed',
        days_count: 12
      }
    ]
  });
  const [loading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (departmentId) {
      joinDepartment(departmentId);
    }
    return () => {
      if (departmentId) {
        leaveDepartment(departmentId);
      }
    };
  }, [departmentId, joinDepartment, leaveDepartment]);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Mock save
      await new Promise(resolve => setTimeout(resolve, 500));
      toast.success('Таблица сохранена');
    } catch (error) {
      toast.error('Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const addRow = () => {
    const newRow = {
      id: Date.now(),
      nickname: '',
      lectures: Object.fromEntries(mockLectureTopics.map(t => [t, 'absent'])),
      trainings: Object.fromEntries(mockTrainingTopics.map(t => [t, 'absent'])),
      attestation: 'not_passed',
      days_count: 0
    };
    setTableData(prev => ({
      ...prev,
      rows: [...prev.rows, newRow]
    }));
  };

  const removeRow = (rowId) => {
    setTableData(prev => ({
      ...prev,
      rows: prev.rows.filter(r => r.id !== rowId)
    }));
    toast.success('Сотрудник удален');
  };

  const updateCell = (rowId, field, subfield, value) => {
    setTableData(prev => ({
      ...prev,
      rows: prev.rows.map(row => {
        if (row.id === rowId) {
          if (subfield) {
            return { ...row, [field]: { ...row[field], [subfield]: value } };
          }
          return { ...row, [field]: value };
        }
        return row;
      })
    }));
  };

  const getStatusColor = (status) => {
    if (status === 'present') return 'bg-green-500/20 text-green-700 dark:text-green-400 border-green-500/30';
    if (status === 'absent') return 'bg-red-500/20 text-red-700 dark:text-red-400 border-red-500/30';
    return 'bg-gray-500/20 text-gray-700 dark:text-gray-400';
  };

  const getStatusText = (status) => {
    if (status === 'present') return 'Был';
    if (status === 'absent') return 'Не был';
    return '-';
  };

  const getAttestationColor = (status) => {
    if (status === 'passed') return 'bg-green-500/20 text-green-700 dark:text-green-400 border-green-500/30';
    if (status === 'excellent') return 'bg-blue-500/20 text-blue-700 dark:text-blue-400 border-blue-500/30';
    return 'bg-red-500/20 text-red-700 dark:text-red-400 border-red-500/30';
  };

  const getAttestationText = (status) => {
    if (status === 'passed') return 'Сдана';
    if (status === 'excellent') return 'Отлично';
    return 'Не сдана';
  };

  const formatWeekPeriod = () => {
    if (!currentWeek) return '';
    const start = new Date(currentWeek.week_start);
    const end = new Date(currentWeek.week_end);
    return `${start.getDate().toString().padStart(2, '0')}.${(start.getMonth() + 1).toString().padStart(2, '0')} - ${end.getDate().toString().padStart(2, '0')}.${(end.getMonth() + 1).toString().padStart(2, '0')}`;
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
          <Link to="/factions">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{department.name}</h1>
            <p className="text-muted-foreground">
              {department.faction} | Период: {formatWeekPeriod()}
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
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Excel
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="bg-yellow-500/10 border-b">
          <CardTitle className="text-yellow-600 dark:text-yellow-500 text-center text-xl">
            {department.name.toUpperCase()}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted/50 border-b-2">
                  <th className="px-3 py-3 text-left font-bold border-r min-w-[150px] sticky left-0 bg-muted/50 z-10">
                    Nick Name
                  </th>
                  <th colSpan={mockLectureTopics.length} className="px-3 py-2 text-center font-bold border-r bg-blue-500/10">
                    Лекции
                  </th>
                  <th colSpan={mockTrainingTopics.length} className="px-3 py-2 text-center font-bold border-r bg-purple-500/10">
                    Тренировки
                  </th>
                  <th className="px-3 py-2 text-center font-bold border-r bg-amber-500/10">
                    Аттестация
                  </th>
                  <th className="px-3 py-2 text-center font-bold bg-green-500/10">
                    Кол-во дней на посту
                  </th>
                  <th className="px-3 py-2 text-center font-bold w-[60px]">
                    
                  </th>
                </tr>
                <tr className="bg-muted/30 border-b">
                  <th className="px-3 py-2 border-r sticky left-0 bg-muted/30 z-10"></th>
                  {mockLectureTopics.map((topic, idx) => (
                    <th key={topic} className="px-2 py-2 text-xs font-semibold border-r min-w-[100px]">
                      {topic}
                    </th>
                  ))}
                  {mockTrainingTopics.map((topic, idx) => (
                    <th key={topic} className="px-2 py-2 text-xs font-semibold border-r min-w-[110px]">
                      {topic}
                    </th>
                  ))}
                  <th className="px-2 py-2 border-r"></th>
                  <th className="px-2 py-2"></th>
                  <th className="px-2 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {tableData.rows.map((row, rowIdx) => (
                  <tr key={row.id} className="border-b hover:bg-muted/20 transition-colors">
                    <td className="px-3 py-2 border-r sticky left-0 bg-background z-10">
                      <Input
                        value={row.nickname}
                        onChange={(e) => updateCell(row.id, 'nickname', null, e.target.value)}
                        placeholder="Введите ник"
                        className="min-w-[140px] h-8 text-sm border-none bg-transparent"
                      />
                    </td>
                    
                    {mockLectureTopics.map((topic) => (
                      <td key={topic} className="px-2 py-2 border-r">
                        <Select
                          value={row.lectures[topic]}
                          onValueChange={(value) => updateCell(row.id, 'lectures', topic, value)}
                        >
                          <SelectTrigger className={`h-8 text-xs font-medium border ${getStatusColor(row.lectures[topic])}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="present" className="text-xs">
                              <span className="text-green-600 font-medium">✓ Был</span>
                            </SelectItem>
                            <SelectItem value="absent" className="text-xs">
                              <span className="text-red-600 font-medium">✗ Не был</span>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                    ))}

                    {mockTrainingTopics.map((topic) => (
                      <td key={topic} className="px-2 py-2 border-r">
                        <Select
                          value={row.trainings[topic]}
                          onValueChange={(value) => updateCell(row.id, 'trainings', topic, value)}
                        >
                          <SelectTrigger className={`h-8 text-xs font-medium border ${getStatusColor(row.trainings[topic])}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="present" className="text-xs">
                              <span className="text-green-600 font-medium">✓ Был</span>
                            </SelectItem>
                            <SelectItem value="absent" className="text-xs">
                              <span className="text-red-600 font-medium">✗ Не был</span>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </td>
                    ))}

                    <td className="px-2 py-2 border-r">
                      <Select
                        value={row.attestation}
                        onValueChange={(value) => updateCell(row.id, 'attestation', null, value)}
                      >
                        <SelectTrigger className={`h-8 text-xs font-medium border ${getAttestationColor(row.attestation)}`}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="not_passed" className="text-xs">
                            <span className="text-red-600 font-medium">Не сдана</span>
                          </SelectItem>
                          <SelectItem value="passed" className="text-xs">
                            <span className="text-green-600 font-medium">Сдана</span>
                          </SelectItem>
                          <SelectItem value="excellent" className="text-xs">
                            <span className="text-blue-600 font-medium">Отлично</span>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </td>

                    <td className="px-3 py-2 text-center font-semibold">
                      <Input
                        type="number"
                        value={row.days_count}
                        onChange={(e) => updateCell(row.id, 'days_count', null, parseInt(e.target.value) || 0)}
                        className="w-16 h-8 text-center text-sm mx-auto"
                        min="0"
                      />
                    </td>

                    <td className="px-2 py-2 text-center">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeRow(row.id)}
                        className="h-8 w-8"
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between items-center text-sm text-muted-foreground">
        <p>Последнее сохранение: только что</p>
        <p>Real-time обновления: {saving ? 'Сохранение...' : 'Активно'}</p>
      </div>
    </div>
  );
};
