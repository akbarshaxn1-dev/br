import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Shield } from 'lucide-react';

export const AuditPage = () => {
  const { user } = useAuth();
  const canView = ['developer', 'gs', 'zgs'].includes(user?.role);

  if (!canView) {
    return (
      <div className="container py-8">
        <Alert variant="destructive">
          <Shield className="h-4 w-4" />
          <AlertDescription>
            У вас нет доступа к журналу действий. Эта функция доступна только администраторам.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-6" data-testid="audit-page">
      <h1 className="text-3xl font-bold">Журнал действий</h1>
      <Card>
        <CardHeader>
          <CardTitle>Audit Log</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Здесь будет отображаться полный журнал всех действий пользователей в системе.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
