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
import { Plus, Trash2, GripVertical, BookOpen, Dumbbell, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export const TopicsPage = () => {
  const { user } = useAuth();
  const [factions, setFactions] = useState([]);
  const [selectedFaction, setSelectedFaction] = useState('');
  const [lectureTopics, setLectureTopics] = useState([]);
  const [trainingTopics, setTrainingTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newLectureTopic, setNewLectureTopic] = useState('');
  const [newTrainingTopic, setNewTrainingTopic] = useState('');
  const [lectureDialogOpen, setLectureDialogOpen] = useState(false);
  const [trainingDialogOpen, setTrainingDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const canManage = user?.role === 'developer' || user?.role === 'gs' || user?.role === 'zgs' || user?.role?.startsWith('leader_');
  const canSelectFaction = ['developer', 'gs', 'zgs'].includes(user?.role);

  useEffect(() => {
    loadFactions();
  }, []);

  useEffect(() => {
    if (selectedFaction) {
      loadTopics();
    }
  }, [selectedFaction]);

  const loadFactions = async () => {
    try {
      const data = await api.get('/api/factions/');
      setFactions(data);
      
      // Auto-select faction for leaders
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

  const loadTopics = async () => {
    try {
      const [lectures, trainings] = await Promise.all([
        api.get(`/api/topics/lectures/faction/${selectedFaction}`),
        api.get(`/api/topics/trainings/faction/${selectedFaction}`)
      ]);
      setLectureTopics(lectures);
      setTrainingTopics(trainings);
    } catch (error) {
      console.error('Error loading topics:', error);
      toast.error('Ошибка загрузки тем');
    }
  };

  const handleAddLectureTopic = async () => {
    if (!newLectureTopic.trim()) return;
    
    setSaving(true);
    try {
      await api.post(`/api/topics/lectures/faction/${selectedFaction}`, { topic: newLectureTopic });
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
    if (!newTrainingTopic.trim()) return;
    
    setSaving(true);
    try {
      await api.post(`/api/topics/trainings/faction/${selectedFaction}`, { topic: newTrainingTopic });
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
      await api.delete(`/api/topics/lectures/${topicId}`);
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
      await api.delete(`/api/topics/trainings/${topicId}`);
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="topics-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Лекции и Тренировки</h1>
          <p className="text-muted-foreground">Управление темами для таблиц отделов</p>
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

      {!canManage && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Управление темами доступно только лидерам фракций и администраторам.
          </AlertDescription>
        </Alert>
      )}

      {selectedFaction && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Lecture Topics */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <CardTitle>Темы лекций</CardTitle>
                    <CardDescription>{getFactionName(selectedFaction)}</CardDescription>
                  </div>
                </div>
                
                {canManage && (
                  <Dialog open={lectureDialogOpen} onOpenChange={setLectureDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm" data-testid="add-lecture-topic">
                        <Plus className="h-4 w-4 mr-1" />
                        Добавить
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Добавить тему лекции</DialogTitle>
                        <DialogDescription>
                          Добавьте новую тему для фракции {getFactionName(selectedFaction)}
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="lecture-topic">Название темы</Label>
                          <Input
                            id="lecture-topic"
                            placeholder="Например: Конституция РФ"
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
                <p className="text-muted-foreground text-center py-4">Нет тем лекций</p>
              ) : (
                <div className="space-y-2">
                  {lectureTopics.map((topic, index) => (
                    <div 
                      key={topic.id} 
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                      data-testid={`lecture-topic-${index}`}
                    >
                      <div className="flex items-center gap-3">
                        <GripVertical className="h-4 w-4 text-muted-foreground cursor-move" />
                        <span className="font-medium">{topic.topic}</span>
                      </div>
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
                    <CardTitle>Темы тренировок</CardTitle>
                    <CardDescription>{getFactionName(selectedFaction)}</CardDescription>
                  </div>
                </div>
                
                {canManage && (
                  <Dialog open={trainingDialogOpen} onOpenChange={setTrainingDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm" data-testid="add-training-topic">
                        <Plus className="h-4 w-4 mr-1" />
                        Добавить
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Добавить тему тренировки</DialogTitle>
                        <DialogDescription>
                          Добавьте новую тему для фракции {getFactionName(selectedFaction)}
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
                <p className="text-muted-foreground text-center py-4">Нет тем тренировок</p>
              ) : (
                <div className="space-y-2">
                  {trainingTopics.map((topic, index) => (
                    <div 
                      key={topic.id} 
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                      data-testid={`training-topic-${index}`}
                    >
                      <div className="flex items-center gap-3">
                        <GripVertical className="h-4 w-4 text-muted-foreground cursor-move" />
                        <span className="font-medium">{topic.topic}</span>
                      </div>
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
      )}
    </div>
  );
};
