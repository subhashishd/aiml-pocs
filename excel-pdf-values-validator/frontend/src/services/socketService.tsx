import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';
import toast from 'react-hot-toast';

// Socket events interface
interface SocketEvents {
  // Task events
  'task:created': (data: { taskId: string; filename: string; status: string }) => void;
  'task:updated': (data: { taskId: string; status: string; progress?: number }) => void;
  'task:completed': (data: { taskId: string; status: string; result?: any }) => void;
  'task:failed': (data: { taskId: string; status: string; error: string }) => void;
  
  // System events
  'system:status': (data: { component: string; status: string; message?: string }) => void;
  'system:metrics': (data: { cpu: number; memory: number; disk: number }) => void;
  
  // File events
  'file:uploaded': (data: { fileId: string; filename: string; size: number }) => void;
  'file:processed': (data: { fileId: string; taskId: string; status: string }) => void;
  
  // Connection events
  connect: () => void;
  disconnect: () => void;
  connect_error: (error: Error) => void;
}

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  subscribe: <K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]) => void;
  unsubscribe: <K extends keyof SocketEvents>(event: K, callback?: SocketEvents[K]) => void;
  emit: (event: string, data?: any) => void;
}

const SocketContext = createContext<SocketContextType>({
  socket: null,
  isConnected: false,
  subscribe: () => {},
  unsubscribe: () => {},
  emit: () => {},
});

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize socket connection
    const socketUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:8000';
    
    const newSocket = io(socketUrl, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      auth: {
        token: localStorage.getItem('auth_token'),
      },
    });

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('Socket connected:', newSocket.id);
      setIsConnected(true);
      toast.success('Connected to server', { id: 'socket-connection' });
    });

    newSocket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      setIsConnected(false);
      
      if (reason === 'io server disconnect') {
        // Server disconnected - try to reconnect
        newSocket.connect();
      }
      
      toast.error('Disconnected from server', { id: 'socket-connection' });
    });

    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      setIsConnected(false);
      toast.error('Connection failed', { id: 'socket-connection' });
    });

    newSocket.on('reconnect', (attemptNumber) => {
      console.log('Socket reconnected after', attemptNumber, 'attempts');
      toast.success('Reconnected to server', { id: 'socket-connection' });
    });

    newSocket.on('reconnect_error', (error) => {
      console.error('Socket reconnection error:', error);
    });

    newSocket.on('reconnect_failed', () => {
      console.error('Socket reconnection failed');
      toast.error('Failed to reconnect to server', { id: 'socket-connection' });
    });

    // Global event handlers for notifications
    newSocket.on('task:created', (data) => {
      toast.success(`Task created: ${data.filename}`, {
        duration: 3000,
        icon: '📁',
      });
    });

    newSocket.on('task:completed', (data) => {
      toast.success(`Task completed: ${data.taskId}`, {
        duration: 5000,
        icon: '✅',
      });
    });

    newSocket.on('task:failed', (data) => {
      toast.error(`Task failed: ${data.error}`, {
        duration: 5000,
        icon: '❌',
      });
    });

    newSocket.on('system:status', (data) => {
      if (data.status === 'error') {
        toast.error(`System issue: ${data.component} - ${data.message}`, {
          duration: 10000,
          icon: '⚠️',
        });
      }
    });

    setSocket(newSocket);

    // Cleanup on unmount
    return () => {
      newSocket.close();
    };
  }, []);

  const subscribe = <K extends keyof SocketEvents>(
    event: K,
    callback: SocketEvents[K]
  ) => {
    if (socket) {
      socket.on(event as string, callback as any);
    }
  };

  const unsubscribe = <K extends keyof SocketEvents>(
    event: K,
    callback?: SocketEvents[K]
  ) => {
    if (socket) {
      if (callback) {
        socket.off(event as string, callback as any);
      } else {
        socket.removeAllListeners(event as string);
      }
    }
  };

  const emit = (event: string, data?: any) => {
    if (socket && isConnected) {
      socket.emit(event, data);
    } else {
      console.warn('Socket not connected, cannot emit event:', event);
    }
  };

  const value: SocketContextType = {
    socket,
    isConnected,
    subscribe,
    unsubscribe,
    emit,
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

// Custom hook to use socket
export const useSocket = () => {
  const context = useContext(SocketContext);
  
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  
  return context;
};

// Custom hook for task updates
export const useTaskUpdates = (taskId?: string) => {
  const { subscribe, unsubscribe } = useSocket();
  const [taskStatus, setTaskStatus] = useState<{
    status: string;
    progress?: number;
    error?: string;
  } | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const handleTaskUpdate = (data: { taskId: string; status: string; progress?: number }) => {
      if (data.taskId === taskId) {
        setTaskStatus({
          status: data.status,
          progress: data.progress,
        });
      }
    };

    const handleTaskCompleted = (data: { taskId: string; status: string; result?: any }) => {
      if (data.taskId === taskId) {
        setTaskStatus({
          status: data.status,
          progress: 100,
        });
      }
    };

    const handleTaskFailed = (data: { taskId: string; status: string; error: string }) => {
      if (data.taskId === taskId) {
        setTaskStatus({
          status: data.status,
          error: data.error,
        });
      }
    };

    subscribe('task:updated', handleTaskUpdate);
    subscribe('task:completed', handleTaskCompleted);
    subscribe('task:failed', handleTaskFailed);

    return () => {
      unsubscribe('task:updated', handleTaskUpdate);
      unsubscribe('task:completed', handleTaskCompleted);
      unsubscribe('task:failed', handleTaskFailed);
    };
  }, [taskId, subscribe, unsubscribe]);

  return taskStatus;
};

// Custom hook for system status
export const useSystemStatus = () => {
  const { subscribe, unsubscribe } = useSocket();
  const [systemStatus, setSystemStatus] = useState<{
    components: Record<string, { status: string; message?: string }>;
    metrics?: { cpu: number; memory: number; disk: number };
  }>({
    components: {},
  });

  useEffect(() => {
    const handleSystemStatus = (data: { component: string; status: string; message?: string }) => {
      setSystemStatus(prev => ({
        ...prev,
        components: {
          ...prev.components,
          [data.component]: {
            status: data.status,
            message: data.message,
          },
        },
      }));
    };

    const handleSystemMetrics = (data: { cpu: number; memory: number; disk: number }) => {
      setSystemStatus(prev => ({
        ...prev,
        metrics: data,
      }));
    };

    subscribe('system:status', handleSystemStatus);
    subscribe('system:metrics', handleSystemMetrics);

    return () => {
      unsubscribe('system:status', handleSystemStatus);
      unsubscribe('system:metrics', handleSystemMetrics);
    };
  }, [subscribe, unsubscribe]);

  return systemStatus;
};

export default SocketContext;
