import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

export const DepartmentsListPage = () => {
  return (
    <div className="container py-8 space-y-6" data-testid="departments-list-page">
      <h1 className="text-3xl font-bold">Все отделы</h1>
      <Card>
        <CardHeader>
          <CardTitle>Список отделов</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Выберите фракцию в меню "Фракции" чтобы увидеть отделы конкретной фракции.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
