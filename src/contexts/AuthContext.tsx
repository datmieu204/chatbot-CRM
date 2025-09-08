import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load persisted user on first mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem('auth_user');
      if (raw) {
        const parsed = JSON.parse(raw) as User;
        if (parsed && parsed.id && parsed.email) {
          setUser(parsed);
        }
      }
    } catch {
      // ignore corrupted storage
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json().catch(() => ({} as any));

      const loggedInUser: User = {
        id: (data && (data.user?.id || data.id)) || '1',
        email: (data && (data.user?.email || data.email)) || email,
        name: (data && (data.user?.name || data.name)) || (email.includes('@') ? email.split('@')[0] : email)
      };

      setUser(loggedInUser);
      try { localStorage.setItem('auth_user', JSON.stringify(loggedInUser)); } catch {}
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ name, email, password })
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json().catch(() => ({} as any));

      const newUser: User = {
        id: (data && (data.user?.id || data.id)) || '1',
        email: (data && (data.user?.email || data.email)) || email,
        name: (data && (data.user?.name || data.name)) || name
      };

      setUser(newUser);
      try { localStorage.setItem('auth_user', JSON.stringify(newUser)); } catch {}
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    try { localStorage.removeItem('auth_user'); } catch {}
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};