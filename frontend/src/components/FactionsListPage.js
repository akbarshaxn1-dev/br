import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiFetch } from '../utils/api-helper';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Shield } from 'lucide-react';
import { Link } from 'react-router-dom';

export const FactionsListPage = () => {
  const { user } = useAuth();
  const [factions, setFactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFactions();
  }, []);

  const loadFactions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      // Use relative URL
      const response = await fetch('/api/factions', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load');
      }
      
      const data = await response.json();
      setFactions(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-[400px]"><div className="spinner"></div></div>;
  }

  return (
    <div className="container py-8 space-y-6" data-testid="factions-list-page">
      <h1 className="text-3xl font-bold">Все фракции</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {factions.map((faction) => (
          <Link key={faction.id} to={`/faction/${faction.code}`}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Shield className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <CardTitle>{faction.name}</CardTitle>
                    <CardDescription>{faction.code.toUpperCase()}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{faction.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
};
