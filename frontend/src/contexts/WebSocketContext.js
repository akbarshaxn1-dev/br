import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import io from 'socket.io-client';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const listenersRef = useRef({});

  useEffect(() => {
    if (!isAuthenticated || !user) {
      if (socket) {
        socket.disconnect();
        setSocket(null);
        setConnected(false);
      }
      return;
    }

    // Use the backend URL from environment
    const wsUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
    
    const newSocket = io(wsUrl, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
      timeout: 20000
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected, socket id:', newSocket.id);
      setConnected(true);
      
      // Authenticate
      newSocket.emit('authenticate', {
        user_id: user.id,
        faction: user.faction
      });
    });

    newSocket.on('connect_error', (error) => {
      console.log('WebSocket connection error:', error.message);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      setConnected(false);
    });

    newSocket.on('authenticated', (data) => {
      console.log('WebSocket authenticated:', data);
    });

    newSocket.on('error', (error) => {
      console.log('WebSocket error:', error);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, [isAuthenticated, user]);

  const on = useCallback((event, callback) => {
    if (socket) {
      socket.on(event, callback);
      if (!listenersRef.current[event]) {
        listenersRef.current[event] = [];
      }
      listenersRef.current[event].push(callback);
    }
  }, [socket]);

  const off = useCallback((event, callback) => {
    if (socket) {
      socket.off(event, callback);
      if (listenersRef.current[event]) {
        listenersRef.current[event] = listenersRef.current[event].filter(cb => cb !== callback);
      }
    }
  }, [socket]);

  const emit = useCallback((event, data) => {
    if (socket && connected) {
      socket.emit(event, data);
    }
  }, [socket, connected]);

  const joinDepartment = useCallback((departmentId) => {
    emit('join_department', { department_id: departmentId });
  }, [emit]);

  const leaveDepartment = useCallback((departmentId) => {
    emit('leave_department', { department_id: departmentId });
  }, [emit]);

  const value = {
    socket,
    connected,
    on,
    off,
    emit,
    joinDepartment,
    leaveDepartment
  };

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>;
};
