import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Plus, Building2, Users, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

export const FactionPage = () => {
  const { factionCode } = useParams();
  const { user } = useAuth();
  const [faction, setFaction] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newDeptName, setNewDeptName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, [factionCode]);

  const loadData = async () => {
    try {
      const [factionData, deptsData] = await Promise.all([
        api.get(`/api/factions/${factionCode}`),
        api.get(`/api/departments/faction/${factionCode}`)
      ]);
      setFaction(factionData);
      setDepartments(deptsData);
    } catch (error) {
      console.error('Error loading faction data:', error);
      toast.error('Ошибка загрузки данных фракции');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDepartment = async (e) => {
    e.preventDefault();
    if (!newDeptName.trim()) return;

    setCreating(true);
    try {
      await api.post(`/api/departments/faction/${factionCode}`, { name: newDeptName });
      toast.success('Отдел успешно создан');
      setNewDeptName('');
      setCreateDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Error creating department:', error);
      toast.error('Ошибка создания отдела');
    } finally {
      setCreating(false);
    }
  };

  const canManageDepartments = user?.role === 'developer' || user?.role === 'gs' || user?.role === 'zgs' || user?.role?.startsWith('leader_');

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!faction) {
    return (
      <div className="container py-8">
        <p className="text-center text-muted-foreground">Фракция не найдена</p>
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="faction-page">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{faction.name}</h1>
            <p className="text-muted-foreground">{faction.description}</p>
          </div>
        </div>

        {canManageDepartments && (
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="create-department-button">
                <Plus className="mr-2 h-4 w-4" />
                Создать отдел
              </Button>
            </DialogTrigger>
            <DialogContent>
              <form onSubmit={handleCreateDepartment}>
                <DialogHeader>
                  <DialogTitle>Создать новый отдел</DialogTitle>
                  <DialogDescription>
                    Создайте новый отдел в фракции {faction.name}
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="dept-name">Название отдела</Label>
                    <Input
                      id="dept-name"
                      placeholder="Например: Отдел контрразведки"
                      value={newDeptName}
                      onChange={(e) => setNewDeptName(e.target.value)}
                      disabled={creating}
                      required
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)} disabled={creating}>
                    Отмена
                  </Button>
                  <Button type="submit" disabled={creating}>
                    {creating ? 'Создание...' : 'Создать'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Статистика</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Отделов:</span>
              <span className="font-semibold">{departments.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Активных таблиц:</span>
              <span className="font-semibold">-</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Быстрые действия</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to={`/faction/${factionCode}/topics`}>
              <Button variant="outline" className="w-full justify-start">
                Управление темами лекций и тренировок
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-4">Отделы фракции</h2>
        {departments.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center space-y-3">
                <Building2 className="mx-auto h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">Пока нет отделов в этой фракции</p>
                {canManageDepartments && (
                  <Button onClick={() => setCreateDialogOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Создать первый отдел
                  </Button>
                )}
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
                      <CardDescription className="text-xs">ID: {dept.id.substring(0, 8)}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Link to={`/department/${dept.id}`}>
                    <Button className="w-full" data-testid={`view-department-${dept.id}`}>
                      Открыть отдел
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
