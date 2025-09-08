import { createContext, useContext, useState, ReactNode } from 'react';
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/auth";

interface User {
  id: string;
  email: string;
  name: string;
}

export interface Conversation {
  id: string;
  conversation_name: string;
  created_at: string;
  updated_at?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  fetchConversations: () => Promise<Conversation[]>;
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

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem("token", data.access_token); // lưu JWT
      setUser({ id: data.user_id, email, name: email.split("@")[0] }); // bạn có thể fetch user info thêm
      return true;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      if (!res.ok) return false;
      // đăng ký xong, tự login
      return await login(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
  };

  const fetchConversations = async (): Promise<Conversation[]> => {
    try {
      const res = await axios.get(API_URL + "/");
      return res.data.map((conv: any) => ({
        id: conv.id,
        conversation_name: conv.conversation_name,
        created_at: conv.created_at,
        updated_at: conv.updated_at,
        latestMessage: conv.latestMessage || "",
        avatarUrl: conv.avatarUrl || ""
      }));
    } catch (error) {
      console.error("Error fetching conversations:", error);
      return [];
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading, fetchConversations }}>
      {children}
    </AuthContext.Provider>
  );
};