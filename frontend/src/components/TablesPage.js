import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

export const TablesPage = () => {
  return (
    <div className="container py-8 space-y-6" data-testid="tables-page">
      <h1 className="text-3xl font-bold">Таблицы отделов</h1>
      <Card>
        <CardHeader>
          <CardTitle>Управление таблицами</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Перейдите в конкретный отдел через Фракции → Отдел для работы с таблицами.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
