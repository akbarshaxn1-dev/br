import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { AlertCircle } from 'lucide-react';

export const TopicsPage = () => {
  const { user } = useAuth();
  const canManage = user?.role === 'developer' || user?.role === 'gs' || user?.role === 'zgs' || user?.role?.startsWith('leader_');

  return (
    <div className="container py-8 space-y-6" data-testid="topics-page">
      <h1 className="text-3xl font-bold">Лекции и Тренировки</h1>
      
      {!canManage && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Управление темами лекций и тренировок доступно только лидерам фракций и администраторам.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Управление темами</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Перейдите в свою фракцию для управления темами лекций и тренировок.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
