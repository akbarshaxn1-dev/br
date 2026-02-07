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
import { Plus, Trash2, BookOpen, Dumbbell, AlertCircle, Loader2, Building2 } from 'lucide-react';
import { toast } from 'sonner';

export const TopicsPage = () => {
  const { user } = useAuth();
  const [factions, setFactions] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [selectedFaction, setSelectedFaction] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [lectureTopics, setLectureTopics] = useState([]);
  const [trainingTopics, setTrainingTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDepts, setLoadingDepts] = useState(false);
  const [newLectureTopic, setNewLectureTopic] = useState('');
  const [newTrainingTopic, setNewTrainingTopic] = useState('');
  const [lectureDialogOpen, setLectureDialogOpen] = useState(false);
  const [trainingDialogOpen, setTrainingDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const canManage = user?.role === 'developer' || user?.role === 'gs' || user?.role === 'zgs' || user?.role?.startsWith('leader_') || user?.role === 'head_of_department';
  const canSelectFaction = ['developer', 'gs', 'zgs'].includes(user?.role);

  useEffect(() => {
    loadFactions();
  }, []);

  useEffect(() => {
    if (selectedFaction) {
      loadDepartments();
    }
  }, [selectedFaction]);

  useEffect(() => {
    if (selectedDepartment) {
      loadTopics();
    }
  }, [selectedDepartment]);

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
      toast.error('Ошибка загрузки фракций');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    setLoadingDepts(true);
    try {
      const data = await api.get(`/api/departments/faction/${selectedFaction}`);
      setDepartments(data);
      
      // Auto-select first department or user's department
      if (user?.department_id) {
        const userDept = data.find(d => d.id === user.department_id);
        if (userDept) {
          setSelectedDepartment(userDept.id);
        }
      } else if (data.length > 0) {
        setSelectedDepartment(data[0].id);
      } else {
        setSelectedDepartment('');
        setLectureTopics([]);
        setTrainingTopics([]);
      }
    } catch (error) {
      console.error('Error loading departments:', error);
      setDepartments([]);
    } finally {
      setLoadingDepts(false);
    }
  };

  const loadTopics = async () => {
    if (!selectedDepartment) return;
    
    try {
      const [lectures, trainings] = await Promise.all([
        api.get(`/api/topics/lectures/department/${selectedDepartment}`),
        api.get(`/api/topics/trainings/department/${selectedDepartment}`)
      ]);
      setLectureTopics(lectures);
      setTrainingTopics(trainings);
    } catch (error) {
      console.error('Error loading topics:', error);
      // Fallback to faction topics
      try {
        const [lectures, trainings] = await Promise.all([
          api.get(`/api/topics/lectures/faction/${selectedFaction}`),
          api.get(`/api/topics/trainings/faction/${selectedFaction}`)
        ]);
        setLectureTopics(lectures);
        setTrainingTopics(trainings);
      } catch (e) {
        toast.error('Ошибка загрузки тем');
      }
    }
  };

  const handleAddLectureTopic = async () => {
    if (!newLectureTopic.trim() || !selectedDepartment) return;
    
    setSaving(true);
    try {
      await api.post(`/api/topics/lectures/department/${selectedDepartment}`, { topic: newLectureTopic });
      toast.success('Тема лекции добавлена');
      setNewLectureTopic('');
      setLectureDialogOpen(false);
      loadTopics();
    } catch (error) {
      console.error('Error adding lecture topic:', error);
      toast.error('Ошибка добавления темы');
    } finally {
      setSaving(false);
    }
  };

  const handleAddTrainingTopic = async () => {
    if (!newTrainingTopic.trim() || !selectedDepartment) return;
    
    setSaving(true);
    try {
      await api.post(`/api/topics/trainings/department/${selectedDepartment}`, { topic: newTrainingTopic });
      toast.success('Тема тренировки добавлена');
      setNewTrainingTopic('');
      setTrainingDialogOpen(false);
      loadTopics();
    } catch (error) {
      console.error('Error adding training topic:', error);
      toast.error('Ошибка добавления темы');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteLectureTopic = async (topicId) => {
    if (!confirm('Удалить эту тему лекции?')) return;
    
    try {
      await api.delete(`/api/topics/lectures/department/${selectedDepartment}/${topicId}`);
      toast.success('Тема удалена');
      loadTopics();
    } catch (error) {
      console.error('Error deleting lecture topic:', error);
      toast.error('Ошибка удаления темы');
    }
  };

  const handleDeleteTrainingTopic = async (topicId) => {
    if (!confirm('Удалить эту тему тренировки?')) return;
    
    try {
      await api.delete(`/api/topics/trainings/department/${selectedDepartment}/${topicId}`);
      toast.success('Тема удалена');
      loadTopics();
    } catch (error) {
      console.error('Error deleting training topic:', error);
      toast.error('Ошибка удаления темы');
    }
  };

  const getFactionName = (code) => {
    const faction = factions.find(f => f.code === code);
    return faction?.name || code;
  };

  const getDepartmentName = (id) => {
    const dept = departments.find(d => d.id === id);
    return dept?.name || id;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-4 sm:py-8 px-4 space-y-4 sm:space-y-6" data-testid="topics-page">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-3xl font-bold">Лекции и Тренировки</h1>
          <p className="text-sm text-muted-foreground">Управление темами для каждого отдела</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2">
          {canSelectFaction && (
            <Select value={selectedFaction} onValueChange={(v) => { setSelectedFaction(v); setSelectedDepartment(''); }}>
              <SelectTrigger className="w-full sm:w-[180px]" data-testid="faction-selector">
                <SelectValue placeholder="Фракция" />
              </SelectTrigger>
              <SelectContent>
                {factions.map(faction => (
                  <SelectItem key={faction.code} value={faction.code}>
                    {faction.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          
          <Select value={selectedDepartment} onValueChange={setSelectedDepartment} disabled={loadingDepts || departments.length === 0}>
            <SelectTrigger className="w-full sm:w-[200px]" data-testid="department-selector">
              <SelectValue placeholder={loadingDepts ? "Загрузка..." : departments.length === 0 ? "Нет отделов" : "Выберите отдел"} />
            </SelectTrigger>
            <SelectContent>
              {departments.map(dept => (
                <SelectItem key={dept.id} value={dept.id}>
                  {dept.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {!canManage && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Управление темами доступно только лидерам фракций, начальникам отделов и администраторам.
          </AlertDescription>
        </Alert>
      )}

      {departments.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Нет отделов в выбранной фракции</p>
            <p className="text-sm text-muted-foreground mt-2">Сначала создайте отдел на странице фракции</p>
          </CardContent>
        </Card>
      ) : selectedDepartment && (
        <>
          <Alert className="bg-primary/5 border-primary/20">
            <Building2 className="h-4 w-4" />
            <AlertDescription>
              Управление темами для отдела: <strong>{getDepartmentName(selectedDepartment)}</strong> ({getFactionName(selectedFaction)})
            </AlertDescription>
          </Alert>

          <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
            {/* Lecture Topics */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                      <BookOpen className="w-5 h-5 text-blue-500" />
                    </div>
                    <div>
                      <CardTitle className="text-base sm:text-lg">Темы лекций</CardTitle>
                      <CardDescription className="text-xs">{getDepartmentName(selectedDepartment)}</CardDescription>
                    </div>
                  </div>
                  
                  {canManage && (
                    <Dialog open={lectureDialogOpen} onOpenChange={setLectureDialogOpen}>
                      <DialogTrigger asChild>
                        <Button size="sm" data-testid="add-lecture-topic">
                          <Plus className="h-4 w-4 sm:mr-1" />
                          <span className="hidden sm:inline">Добавить</span>
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Добавить тему лекции</DialogTitle>
                          <DialogDescription>
                            Для отдела: {getDepartmentName(selectedDepartment)}
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                          <div className="space-y-2">
                            <Label htmlFor="lecture-topic">Название темы</Label>
                            <Input
                              id="lecture-topic"
                              placeholder="Например: УК РФ"
                              value={newLectureTopic}
                              onChange={(e) => setNewLectureTopic(e.target.value)}
                              disabled={saving}
                            />
                          </div>
                        </div>
                        <DialogFooter>
                          <Button variant="outline" onClick={() => setLectureDialogOpen(false)} disabled={saving}>
                            Отмена
                          </Button>
                          <Button onClick={handleAddLectureTopic} disabled={saving || !newLectureTopic.trim()}>
                            {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                            Добавить
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {lectureTopics.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4 text-sm">Нет тем лекций для этого отдела</p>
                ) : (
                  <div className="space-y-2">
                    {lectureTopics.map((topic, index) => (
                      <div 
                        key={topic.id} 
                        className="flex items-center justify-between p-2 sm:p-3 bg-muted/50 rounded-lg"
                        data-testid={`lecture-topic-${index}`}
                      >
                        <span className="font-medium text-sm">{topic.topic}</span>
                        {canManage && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteLectureTopic(topic.id)}
                            className="h-8 w-8"
                            data-testid={`delete-lecture-${index}`}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Training Topics */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                      <Dumbbell className="w-5 h-5 text-purple-500" />
                    </div>
                    <div>
                      <CardTitle className="text-base sm:text-lg">Темы тренировок</CardTitle>
                      <CardDescription className="text-xs">{getDepartmentName(selectedDepartment)}</CardDescription>
                    </div>
                  </div>
                  
                  {canManage && (
                    <Dialog open={trainingDialogOpen} onOpenChange={setTrainingDialogOpen}>
                      <DialogTrigger asChild>
                        <Button size="sm" data-testid="add-training-topic">
                          <Plus className="h-4 w-4 sm:mr-1" />
                          <span className="hidden sm:inline">Добавить</span>
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Добавить тему тренировки</DialogTitle>
                          <DialogDescription>
                            Для отдела: {getDepartmentName(selectedDepartment)}
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 py-4">
                          <div className="space-y-2">
                            <Label htmlFor="training-topic">Название темы</Label>
                            <Input
                              id="training-topic"
                              placeholder="Например: Физическая подготовка"
                              value={newTrainingTopic}
                              onChange={(e) => setNewTrainingTopic(e.target.value)}
                              disabled={saving}
                            />
                          </div>
                        </div>
                        <DialogFooter>
                          <Button variant="outline" onClick={() => setTrainingDialogOpen(false)} disabled={saving}>
                            Отмена
                          </Button>
                          <Button onClick={handleAddTrainingTopic} disabled={saving || !newTrainingTopic.trim()}>
                            {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                            Добавить
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {trainingTopics.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4 text-sm">Нет тем тренировок для этого отдела</p>
                ) : (
                  <div className="space-y-2">
                    {trainingTopics.map((topic, index) => (
                      <div 
                        key={topic.id} 
                        className="flex items-center justify-between p-2 sm:p-3 bg-muted/50 rounded-lg"
                        data-testid={`training-topic-${index}`}
                      >
                        <span className="font-medium text-sm">{topic.topic}</span>
                        {canManage && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteTrainingTopic(topic.id)}
                            className="h-8 w-8"
                            data-testid={`delete-training-${index}`}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};
