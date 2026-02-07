import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { Toaster } from './components/ui/sonner';
import { LoginPage } from './components/LoginPage';
import { Dashboard } from './components/Dashboard';
import { FactionPage } from './components/FactionPage';
import { DepartmentPage } from './components/DepartmentPage';
import { FactionsListPage } from './components/FactionsListPage';
import { DepartmentsListPage } from './components/DepartmentsListPage';
import { TablesPage } from './components/TablesPage';
import { TopicsPage } from './components/TopicsPage';
import { AuditPage } from './components/AuditPage';
import { SettingsPage } from './components/SettingsPage';
import { AdminPage } from './components/AdminPage';
import { WeekArchivePage } from './components/WeekArchivePage';
import { SeniorStaffPage } from './components/SeniorStaffPage';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const AppLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  
  return (
    <div className="min-h-screen bg-background">
      <Header onMenuClick={() => setSidebarOpen(true)} />
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 min-w-0 lg:ml-0">{children}</main>
      </div>
    </div>
  );
};

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        }
      />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/factions"
        element={
          <PrivateRoute>
            <AppLayout>
              <FactionsListPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/faction/:factionCode"
        element={
          <PrivateRoute>
            <AppLayout>
              <FactionPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/departments"
        element={
          <PrivateRoute>
            <AppLayout>
              <DepartmentsListPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/department/:departmentId"
        element={
          <PrivateRoute>
            <AppLayout>
              <DepartmentPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/department/:departmentId/archive"
        element={
          <PrivateRoute>
            <AppLayout>
              <WeekArchivePage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/department/:departmentId/week/:weekId"
        element={
          <PrivateRoute>
            <AppLayout>
              <DepartmentPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/tables"
        element={
          <PrivateRoute>
            <AppLayout>
              <TablesPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/topics"
        element={
          <PrivateRoute>
            <AppLayout>
              <TopicsPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/audit"
        element={
          <PrivateRoute>
            <AppLayout>
              <AuditPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute>
            <AppLayout>
              <SettingsPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <PrivateRoute>
            <AppLayout>
              <AdminPage />
            </AppLayout>
          </PrivateRoute>
        }
      />
      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
};

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AuthProvider>
          <WebSocketProvider>
            <AppRoutes />
            <Toaster />
          </WebSocketProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
