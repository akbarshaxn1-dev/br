import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Alert, AlertDescription } from './ui/alert';
import { Plus, Building2, Users, ArrowLeft, Trash2, Loader2, AlertTriangle, Award } from 'lucide-react';
import { toast } from 'sonner';

export const FactionPage = () => {
  const { factionCode } = useParams();
  const { user } = useAuth();
  const [faction, setFaction] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState(null);
  const [newDeptName, setNewDeptName] = useState('');
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadData();
  }, [factionCode]);

  const loadData = async () => {
    try {
      setLoading(true);
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
      toast.error(error.message || 'Ошибка создания отдела');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteDepartment = async () => {
    if (!selectedDept) return;

    setDeleting(true);
    try {
      await api.delete(`/api/departments/${selectedDept.id}`);
      toast.success(`Отдел "${selectedDept.name}" удалён`);
      setDeleteDialogOpen(false);
      setSelectedDept(null);
      loadData();
    } catch (error) {
      console.error('Error deleting department:', error);
      toast.error(error.message || 'Ошибка удаления отдела');
    } finally {
      setDeleting(false);
    }
  };

  const openDeleteDialog = (dept) => {
    setSelectedDept(dept);
    setDeleteDialogOpen(true);
  };

  // Check permissions - leader of this specific faction or admin
  const canManageDepartments = 
    user?.role === 'developer' || 
    user?.role === 'gs' || 
    user?.role === 'zgs' || 
    user?.role === `leader_${factionCode}`;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
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
    <div className="container py-4 sm:py-8 px-4 space-y-4 sm:space-y-6" data-testid="faction-page">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3 sm:gap-4">
          <Link to="/">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-xl sm:text-3xl font-bold">{faction.name}</h1>
            <p className="text-sm text-muted-foreground">{faction.description}</p>
          </div>
        </div>

        {canManageDepartments && (
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="create-department-button" className="w-full sm:w-auto">
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
                  <Button type="submit" disabled={creating || !newDeptName.trim()}>
                    {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
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
              <span className="font-semibold">{departments.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Быстрые действия</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {canManageDepartments && (
              <Link to={`/faction/${factionCode}/senior-staff`}>
                <Button variant="outline" className="w-full justify-start" data-testid="senior-staff-button">
                  <Award className="mr-2 h-4 w-4 text-amber-500" />
                  Старший состав
                </Button>
              </Link>
            )}
            <Link to="/topics">
              <Button variant="outline" className="w-full justify-start">
                Управление темами лекций и тренировок
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-xl sm:text-2xl font-bold mb-4">Отделы фракции</h2>
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
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {departments.map((dept) => (
              <Card key={dept.id} className="hover:shadow-lg transition-shadow" data-testid={`department-card-${dept.id}`}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Users className="w-5 h-5 text-primary" />
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="text-base sm:text-lg truncate">{dept.name}</CardTitle>
                        <CardDescription className="text-xs">ID: {dept.id.substring(0, 8)}</CardDescription>
                      </div>
                    </div>
                    {canManageDepartments && (
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="text-destructive hover:bg-destructive/10"
                        onClick={() => openDeleteDialog(dept)}
                        data-testid={`delete-department-${dept.id}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Удаление отдела
            </DialogTitle>
            <DialogDescription>
              Вы уверены, что хотите удалить отдел "{selectedDept?.name}"?
            </DialogDescription>
          </DialogHeader>
          
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Это действие удалит все таблицы и данные отдела. Восстановление возможно только через разработчика.
            </AlertDescription>
          </Alert>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)} disabled={deleting}>
              Отмена
            </Button>
            <Button variant="destructive" onClick={handleDeleteDepartment} disabled={deleting}>
              {deleting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
              {deleting ? 'Удаление...' : 'Удалить'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
