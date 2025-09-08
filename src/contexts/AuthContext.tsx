import { createContext, useContext, useState, ReactNode } from 'react';
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

interface User {
  id: string;
  email: string;
  name: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  created_at: string;
  updated_at?: string;
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
  fetchMessages: (conversationId: string) => Promise<Message[]>;
  sendMessage: (conversationId: string, content: string) => Promise<Message | null>;
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
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem("token", data.access_token); // lưu JWT
      setUser({ id: data.payload.user_id, email:data.payload.email, name : data.payload.name }); // có thể fetch user info thêm
      return true;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
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
    localStorage.removeItem("token");
  };

  const fetchConversations = async (): Promise<Conversation[]> => {
    try {
      const res = await axios.get(API_URL + "/conversations"); // endpoint lấy conversations
      // map dữ liệu theo interface Conversation (loại bỏ latestMessage & avatarUrl)
      return res.data.map((conv: any) => ({
        id: conv.id,
        conversation_name: conv.conversation_name,
        created_at: conv.created_at,
        updated_at: conv.updated_at,
      }));
    } catch (error) {
      console.error("Error fetching conversations:", error);
      return [];
    }
  };

  const MESSAGE_API_URL = "http://127.0.0.1:8000/messages";

  const fetchMessages = async (conversationId: string): Promise<Message[]> => {
    try {
      const res = await axios.get<Message[]>(`${MESSAGE_API_URL}/conversation/${conversationId}`);
      return res.data;
    } catch (error) {
      console.error("Error fetching messages:", error);
      return [];
    }
  };

  const sendMessage = async (conversationId: string, content: string): Promise<Message | null> => {
    if (!user) return null;

    try {
      const res = await axios.post<Message>(`${MESSAGE_API_URL}/`, {
        conversation_id: conversationId,
        sender_id: user.id,
        content,
      });
      return res.data;
    } catch (error) {
      console.error("Error sending message:", error);
      return null;
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading, fetchConversations, sendMessage, fetchMessages }}>
      {children}
    </AuthContext.Provider>
  );
};
