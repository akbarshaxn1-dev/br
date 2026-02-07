import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { 
  Users, UserPlus, Shield, Building2, BarChart3, Loader2, 
  Pencil, Trash2, Power, PowerOff, Search, Eye, ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';

const ROLE_LABELS = {
  'developer': 'Разработчик',
  'gs': 'Главный Следящий (ГС)',
  'zgs': 'Заместитель ГС (ЗГС)',
  'leader_gov': 'Лидер Правительства',
  'leader_fsb': 'Лидер ФСБ',
  'leader_gibdd': 'Лидер ГИБДД',
  'leader_umvd': 'Лидер УМВД',
  'leader_army': 'Лидер Армии',
  'leader_hospital': 'Лидер Больницы',
  'leader_smi': 'Лидер СМИ',
  'leader_fsin': 'Лидер ФСИН',
  'head_of_department': 'Начальник отдела',
  'deputy_head': 'Заместитель начальника'
};

const FACTION_LABELS = {
  'gov': 'Правительство',
  'fsb': 'ФСБ',
  'gibdd': 'ГИБДД',
  'umvd': 'УМВД',
  'army': 'Армия',
  'hospital': 'Больница',
  'smi': 'СМИ',
  'fsin': 'ФСИН'
};

export const AdminPage = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [roles, setRoles] = useState([]);
  const [factions, setFactions] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFaction, setFilterFaction] = useState('all');
  const [filterRole, setFilterRole] = useState('all');
  
  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [saving, setSaving] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    nickname: '',
    position: '',
    vk_url: '',
    role: '',
    faction: '',
    department_id: ''
  });

  const canAccess = ['developer', 'gs', 'zgs'].includes(user?.role);

  useEffect(() => {
    if (canAccess) {
      loadData();
    }
  }, [canAccess]);

  useEffect(() => {
    if (formData.faction) {
      loadDepartments(formData.faction);
    }
  }, [formData.faction]);

  const loadData = async () => {
    try {
      const [usersData, statsData, rolesData, factionsData] = await Promise.all([
        api.get('/api/admin/users'),
        api.get('/api/admin/stats'),
        api.get('/api/admin/roles'),
        api.get('/api/admin/factions-list')
      ]);
      
      setUsers(usersData);
      setStats(statsData);
      setRoles(rolesData);
      setFactions(factionsData);
    } catch (error) {
      console.error('Error loading admin data:', error);
      toast.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async (factionCode) => {
    try {
      const data = await api.get(`/api/admin/departments-list?faction=${factionCode}`);
      setDepartments(data);
    } catch (error) {
      console.error('Error loading departments:', error);
    }
  };

  const handleCreateUser = async () => {
    if (!formData.email || !formData.password || !formData.full_name || !formData.nickname || !formData.role) {
      toast.error('Заполните все обязательные поля');
      return;
    }

    setSaving(true);
    try {
      await api.post('/api/admin/users', formData);
      toast.success('Пользователь создан');
      setCreateDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Error creating user:', error);
      toast.error(error.message || 'Ошибка создания пользователя');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    setSaving(true);
    try {
      const updateData = { ...formData };
      delete updateData.password; // Don't update password if empty
      delete updateData.email; // Email usually shouldn't change
      
      await api.put(`/api/admin/users/${selectedUser.id}`, updateData);
      toast.success('Пользователь обновлён');
      setEditDialogOpen(false);
      setSelectedUser(null);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Error updating user:', error);
      toast.error(error.message || 'Ошибка обновления');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Деактивировать этого пользователя?')) return;

    try {
      await api.delete(`/api/admin/users/${userId}`);
      toast.success('Пользователь деактивирован');
      loadData();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error(error.message || 'Ошибка');
    }
  };

  const handleActivateUser = async (userId) => {
    try {
      await api.post(`/api/admin/users/${userId}/activate`);
      toast.success('Пользователь активирован');
      loadData();
    } catch (error) {
      console.error('Error activating user:', error);
      toast.error(error.message || 'Ошибка');
    }
  };

  const openEditDialog = (userData) => {
    setSelectedUser(userData);
    setFormData({
      email: userData.email,
      password: '',
      full_name: userData.full_name,
      nickname: userData.nickname || '',
      position: userData.position || '',
      vk_url: userData.vk_url || '',
      role: userData.role,
      faction: userData.faction || '',
      department_id: userData.department_id || ''
    });
    if (userData.faction) {
      loadDepartments(userData.faction);
    }
    setEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      full_name: '',
      nickname: '',
      position: '',
      vk_url: '',
      role: '',
      faction: '',
      department_id: ''
    });
  };

  const filteredUsers = users.filter(u => {
    const matchesSearch = 
      (u.full_name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (u.nickname?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (u.email?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    
    const matchesFaction = filterFaction === 'all' || u.faction === filterFaction;
    const matchesRole = filterRole === 'all' || u.role === filterRole;
    
    return matchesSearch && matchesFaction && matchesRole;
  });

  if (!canAccess) {
    return (
      <div className="container py-8">
        <Alert variant="destructive">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            Доступ запрещён. Админ-панель доступна только администраторам.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="admin-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Админ-панель</h1>
          <p className="text-muted-foreground">Управление пользователями и доступами</p>
        </div>
        
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="create-user-btn">
              <UserPlus className="mr-2 h-4 w-4" />
              Создать пользователя
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-xl">
            <DialogHeader>
              <DialogTitle>Создание пользователя</DialogTitle>
              <DialogDescription>
                Заполните данные нового пользователя
              </DialogDescription>
            </DialogHeader>
            
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nickname">Ник (игровой) *</Label>
                  <Input
                    id="nickname"
                    placeholder="Vadim_Smirnov"
                    value={formData.nickname}
                    onChange={(e) => setFormData({...formData, nickname: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="full_name">Полное имя *</Label>
                  <Input
                    id="full_name"
                    placeholder="Вадим Смирнов"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="user@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Пароль *</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="position">Должность</Label>
                  <Input
                    id="position"
                    placeholder="Майор"
                    value={formData.position}
                    onChange={(e) => setFormData({...formData, position: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="vk_url">Ссылка VK</Label>
                  <Input
                    id="vk_url"
                    placeholder="https://vk.com/..."
                    value={formData.vk_url}
                    onChange={(e) => setFormData({...formData, vk_url: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>Роль *</Label>
                <Select value={formData.role} onValueChange={(v) => setFormData({...formData, role: v})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите роль" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.value} value={role.value}>
                        {role.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Фракция</Label>
                  <Select value={formData.faction || "none"} onValueChange={(v) => setFormData({...formData, faction: v === "none" ? "" : v, department_id: ''})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Выберите фракцию" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Без фракции</SelectItem>
                      {factions.map(faction => (
                        <SelectItem key={faction.value} value={faction.value}>
                          {faction.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                {formData.faction && (
                  <div className="space-y-2">
                    <Label>Отдел</Label>
                    <Select value={formData.department_id || "none"} onValueChange={(v) => setFormData({...formData, department_id: v === "none" ? "" : v})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите отдел" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Без отдела</SelectItem>
                        {departments.map(dept => (
                          <SelectItem key={dept.id} value={dept.id}>
                            {dept.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>
            
            <DialogFooter>
              <Button variant="outline" onClick={() => { setCreateDialogOpen(false); resetForm(); }}>
                Отмена
              </Button>
              <Button onClick={handleCreateUser} disabled={saving}>
                {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Создать
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Всего пользователей</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_users}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Фракций</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_factions}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Отделов</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_departments}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Входов за 24ч</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.recent_logins_24h}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Пользователи</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Поиск по нику, имени, email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                  data-testid="search-users"
                />
              </div>
            </div>
            <Select value={filterFaction} onValueChange={setFilterFaction}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Фракция" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все фракции</SelectItem>
                {factions.map(f => (
                  <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterRole} onValueChange={setFilterRole}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Роль" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все роли</SelectItem>
                {roles.map(r => (
                  <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Users Table */}
          <div className="rounded-md border">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="p-3 text-left font-semibold">Ник</th>
                  <th className="p-3 text-left font-semibold">Имя</th>
                  <th className="p-3 text-left font-semibold">Роль</th>
                  <th className="p-3 text-left font-semibold">Фракция</th>
                  <th className="p-3 text-left font-semibold">Статус</th>
                  <th className="p-3 text-left font-semibold">VK</th>
                  <th className="p-3 text-right font-semibold">Действия</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-8 text-muted-foreground">
                      Пользователи не найдены
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((u) => (
                    <tr key={u.id} className="border-b hover:bg-muted/20" data-testid={`user-row-${u.id}`}>
                      <td className="p-3">
                        <span className="font-medium">{u.nickname || '-'}</span>
                      </td>
                      <td className="p-3">
                        <div>
                          <p className="font-medium">{u.full_name}</p>
                          <p className="text-xs text-muted-foreground">{u.email}</p>
                        </div>
                      </td>
                      <td className="p-3">
                        <Badge variant="outline" className={
                          u.role === 'developer' ? 'bg-red-500/10 text-red-600 border-red-500/30' :
                          u.role === 'gs' || u.role === 'zgs' ? 'bg-amber-500/10 text-amber-600 border-amber-500/30' :
                          u.role.startsWith('leader_') ? 'bg-purple-500/10 text-purple-600 border-purple-500/30' :
                          'bg-blue-500/10 text-blue-600 border-blue-500/30'
                        }>
                          {ROLE_LABELS[u.role] || u.role}
                        </Badge>
                      </td>
                      <td className="p-3">
                        {u.faction ? FACTION_LABELS[u.faction] || u.faction : '-'}
                      </td>
                      <td className="p-3">
                        {u.is_active ? (
                          <Badge className="bg-green-500/10 text-green-600 border-green-500/30">Активен</Badge>
                        ) : (
                          <Badge variant="destructive">Неактивен</Badge>
                        )}
                      </td>
                      <td className="p-3">
                        {u.vk_url ? (
                          <a href={u.vk_url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline flex items-center gap-1">
                            <ExternalLink className="h-3 w-3" />
                            VK
                          </a>
                        ) : '-'}
                      </td>
                      <td className="p-3">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => openEditDialog(u)}
                            data-testid={`edit-user-${u.id}`}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          {u.role !== 'developer' && (
                            <>
                              {u.is_active ? (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleDeleteUser(u.id)}
                                  data-testid={`deactivate-user-${u.id}`}
                                >
                                  <PowerOff className="h-4 w-4 text-destructive" />
                                </Button>
                              ) : (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleActivateUser(u.id)}
                                  data-testid={`activate-user-${u.id}`}
                                >
                                  <Power className="h-4 w-4 text-green-600" />
                                </Button>
                              )}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          <p className="text-sm text-muted-foreground mt-4">
            Показано {filteredUsers.length} из {users.length} пользователей
          </p>
        </CardContent>
      </Card>

      {/* Edit User Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Редактирование пользователя</DialogTitle>
            <DialogDescription>
              {selectedUser?.nickname} ({selectedUser?.email})
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Ник</Label>
                <Input
                  value={formData.nickname}
                  onChange={(e) => setFormData({...formData, nickname: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>Полное имя</Label>
                <Input
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Должность</Label>
                <Input
                  value={formData.position}
                  onChange={(e) => setFormData({...formData, position: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>VK</Label>
                <Input
                  value={formData.vk_url}
                  onChange={(e) => setFormData({...formData, vk_url: e.target.value})}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Роль</Label>
              <Select value={formData.role} onValueChange={(v) => setFormData({...formData, role: v})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {roles.map(role => (
                    <SelectItem key={role.value} value={role.value}>
                      {role.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Фракция</Label>
                <Select value={formData.faction || "none"} onValueChange={(v) => setFormData({...formData, faction: v === "none" ? "" : v, department_id: ''})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Без фракции</SelectItem>
                    {factions.map(faction => (
                      <SelectItem key={faction.value} value={faction.value}>
                        {faction.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              {formData.faction && (
                <div className="space-y-2">
                  <Label>Отдел</Label>
                  <Select value={formData.department_id || "none"} onValueChange={(v) => setFormData({...formData, department_id: v === "none" ? "" : v})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Без отдела</SelectItem>
                      {departments.map(dept => (
                        <SelectItem key={dept.id} value={dept.id}>
                          {dept.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => { setEditDialogOpen(false); setSelectedUser(null); resetForm(); }}>
              Отмена
            </Button>
            <Button onClick={handleUpdateUser} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Сохранить
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Support Block */}
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold">Разработчик: Vadim Smirnov</p>
              <p className="text-sm text-muted-foreground">Связь: https://vk.com/coder2406</p>
            </div>
            <a href="https://vk.com/coder2406" target="_blank" rel="noopener noreferrer">
              <Button variant="outline">
                <ExternalLink className="mr-2 h-4 w-4" />
                Связаться
              </Button>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
