import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User, LogOut, Menu } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { ChatHistoryPanel } from './ChatHistoryPanel';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}
interface Conversation {
  id: string;
  title: string;
  avatarUrl?: string;
  latestMessage: string;
  messages: Message[];
}

export const ChatInterface = () => {
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'AI Assistant',
      avatarUrl: '',
      latestMessage: 'Xin chào! Tôi là AI assistant. Tôi có thể giúp gì cho bạn hôm nay?',
      messages: [
        { id: '1', text: 'Xin chào! Tôi là AI assistant. Tôi có thể giúp gì cho bạn hôm nay?', isUser: false, timestamp: new Date() }
      ]
    },

  ]);

  const [selectedConvId, setSelectedConvId] = useState(conversations[0].id);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creatingConv, setCreatingConv] = useState(false);
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState<string>('');

  // Restore messages for the selected conversation from localStorage
  useEffect(() => {
    const key = `messages_${selectedConvId}`;
    try {
      const raw = localStorage.getItem(key);
      if (raw) {
        const parsed: Array<{ id: string; text: string; isUser: boolean; timestamp: string }> = JSON.parse(raw);
        const restored = parsed.map(m => ({ ...m, timestamp: new Date(m.timestamp) }));
        setConversations(prev => prev.map(c => c.id === selectedConvId ? { ...c, messages: restored } : c));
      }
    } catch {}
  }, [selectedConvId]);

  // Load conversations from API and replace mocked data
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const res = await fetch('http://localhost:8000/conversations', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        });
        if (!res.ok) return;
        const data = await res.json();
        const mapped: Conversation[] = Array.isArray(data)
        ? data.map((c: any) => ({
            id: String(c.id ?? c._id),
            title: String(c.conversation_name ?? c.title ?? c.name ?? 'Conversation'),
            avatarUrl: c.avatarUrl ?? c.avatar_url ?? '',
            latestMessage:
              typeof c.latestMessage === 'string'
                ? c.latestMessage
                : (c.latestMessage?.content ?? ''),
            messages: []
          }))
        : [];
      
        if (mapped.length) {
          setConversations(mapped);
          setSelectedConvId(mapped[0].id);
        }
      } catch (e) {
        console.error('Failed to load conversations:', e);
      }
    };
    loadConversations();
  }, []);

  const selectedConv = conversations.find(c => c.id === selectedConvId)!;
  const messages = selectedConv.messages;

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => { scrollToBottom(); }, [messages, selectedConvId]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setConversations(prev => prev.map(conv =>
      conv.id === selectedConvId
        ? { ...conv, messages: [...conv.messages, userMessage], latestMessage: userMessage.text }
        : conv
    ));
    try {
      const key = `messages_${selectedConvId}`;
      const existing = localStorage.getItem(key);
      const arr: Array<{ id: string; text: string; isUser: boolean; timestamp: string }> = existing ? JSON.parse(existing) : [];
      arr.push({ ...userMessage, timestamp: userMessage.timestamp.toISOString() });
      localStorage.setItem(key, JSON.stringify(arr));
    } catch {}

    try {
      if (user?.id) {
        await fetch('http://localhost:8000/messages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            conversation_id: selectedConvId,
            sender_id: user.id,
            content: userMessage.text
          })
        });
      }
    } catch (e) {
      console.error('Failed to save message to backend:', e);
    }

    setInputValue('');
    setIsTyping(true);

    setTimeout(() => {
      const aiResponses = [
        'Đó là một câu hỏi thú vị! Tôi đang suy nghĩ về điều này...',
        'Tôi hiểu rồi. Dựa trên thông tin bạn cung cấp...',
        'Cảm ơn bạn đã chia sẻ! Tôi có thể giúp bạn với việc này.',
        'Đây là một chủ đề hay. Hãy để tôi giải thích chi tiết...',
        'Tôi có thể đưa ra một số gợi ý cho vấn đề này.'
      ];
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: aiResponses[Math.floor(Math.random() * aiResponses.length)],
        isUser: false,
        timestamp: new Date()
      };
      setConversations(prev => prev.map(conv =>
        conv.id === selectedConvId
          ? { ...conv, messages: [...conv.messages, aiMessage], latestMessage: aiMessage.text }
          : conv
      ));
      try {
        const key = `messages_${selectedConvId}`;
        const existing = localStorage.getItem(key);
        const arr: Array<{ id: string; text: string; isUser: boolean; timestamp: string }> = existing ? JSON.parse(existing) : [];
        arr.push({ ...aiMessage, timestamp: aiMessage.timestamp.toISOString() });
        localStorage.setItem(key, JSON.stringify(arr));
      } catch {}
      setIsTyping(false);
    }, 1200);
  };

  const handleCreateNewConversation = async () => {
    if (creatingConv) return;
    setCreatingConv(true);
    try {
      const res = await fetch('http://localhost:8000/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ conversation_name: 'Cuộc trò chuyện mới' })
      });
      if (!res.ok) return;
      const data = await res.json();
      const c = Array.isArray(data) ? data[0] : data;
      if (!c) return;
      const newConv: Conversation = {
        id: String(c.id ?? c._id ?? Date.now().toString()),
        title: String(c.conversation_name ?? c.title ?? c.name ?? 'Conversation'),
        avatarUrl: c.avatarUrl ?? c.avatar_url ?? '',
        latestMessage: typeof c.latestMessage === 'string' ? c.latestMessage : (c.latestMessage?.content ?? ''),
        messages: []
      };
      setConversations(prev => [newConv, ...prev]);
      setSelectedConvId(newConv.id);
      // Enable inline rename in history panel
      setEditingConvId(newConv.id);
      setEditingName(newConv.title);
    } catch (e) {
      console.error('Failed to create conversation:', e);
    } finally {
      setCreatingConv(false);
    }
  };

  const handleSubmitRename = async (conversationId: string) => {
    const trimmed = editingName.trim();
    if (!trimmed) {
      // If cleared, keep editing without submitting
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/conversations/${encodeURIComponent(conversationId)}/rename`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ conversation_name: trimmed })
      });
      if (res.ok) {
        setConversations(prev => prev.map(conv => conv.id === conversationId ? { ...conv, title: trimmed } : conv));
        setEditingConvId(null);
      }
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ==== LAYOUT GIỐNG CHATGPT ====
  // Header cao 64px; Sidebar cố định w-72; Main đẩy ml-72 trên md+
  return (
    <div className="h-screen w-full bg-gradient-to-b from-background to-muted/30">
      {/* Header */}
      <header className="h-16 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40">
        <div className="max-w-[100rem] mx-auto h-full px-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="h-7 w-7 text-primary" />
            <div>
              <h1 className="text-lg font-semibold">AI Assistant</h1>
              <p className="text-xs text-muted-foreground">Xin chào, {user?.name ?? 'bạn'}!</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setDrawerOpen(true)}>
              <Menu className="h-6 w-6" />
            </Button>
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="h-4 w-4 mr-2" /> Đăng xuất
            </Button>
          </div>
        </div>
      </header>

      {/* Sidebar desktop (fixed) */}
      <aside className="hidden md:block fixed top-16 left-0 h-[calc(100vh-4rem)] w-72 border-r bg-background z-30">
        <ChatHistoryPanel
          conversations={conversations}
          selectedId={selectedConvId}
          onSelect={setSelectedConvId}
          isOpen
          onCreateNew={handleCreateNewConversation}
          creating={creatingConv}
          editingId={editingConvId ?? undefined}
          editingName={editingName}
          onEditingNameChange={setEditingName}
          onRenameSubmit={handleSubmitRename}
        />
      </aside>

      {/* Sidebar mobile (drawer) */}
      {drawerOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/30" onClick={() => setDrawerOpen(false)} />
          <div className="absolute left-0 top-16 h-[calc(100vh-4rem)] w-[88%] max-w-80 bg-background border-r">
            <ChatHistoryPanel
              conversations={conversations}
              selectedId={selectedConvId}
              onSelect={(id) => { setSelectedConvId(id); setDrawerOpen(false); }}
              isOpen
              onClose={() => setDrawerOpen(false)}
              onCreateNew={async () => { await handleCreateNewConversation(); setDrawerOpen(false); }}
              creating={creatingConv}
              editingId={editingConvId ?? undefined}
              editingName={editingName}
              onEditingNameChange={setEditingName}
              onRenameSubmit={async (id) => { await handleSubmitRename(id); setDrawerOpen(false); }}
            />
          </div>
        </div>
      )}

      {/* Main chat area */}
      <main className="pt-4 md:pl-72 h-[calc(100vh-4rem)]">
        <div className="h-full mx-auto max-w-3xl px-4 flex flex-col">
          {/* Messages area (scrollable) */}
          <ScrollArea className="flex-1">
            <div className="py-2 space-y-4">
              {messages.map(m => (
                <div key={m.id} className={`flex ${m.isUser ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`rounded-2xl px-4 py-3 shadow-sm max-w-[85%] ${
                      m.isUser ? 'bg-primary text-primary-foreground' : 'bg-card text-card-foreground border'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {m.isUser ? <User className="h-4 w-4 mt-0.5 opacity-80" /> : <Bot className="h-4 w-4 mt-0.5 text-primary" />}
                      <div>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{m.text}</p>
                        <p className={`text-[10px] mt-1 ${m.isUser ? 'opacity-80' : 'text-muted-foreground'}`}>
                          {m.timestamp.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-card border rounded-2xl px-4 py-3 shadow-sm">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4 text-primary" />
                      <div className="flex gap-1">
                        <span className="w-2 h-2 rounded-full bg-primary animate-bounce" />
                        <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:120ms]" />
                        <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:240ms]" />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input (sticky bottom) */}
          <div className="sticky bottom-0 bg-gradient-to-t from-background via-background to-transparent pt-3">
            <div className="border rounded-xl bg-background p-2 shadow-sm">
              <div className="flex items-center gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Nhập tin nhắn của bạn…"
                  className="flex-1"
                  disabled={isTyping}
                />
                <Button onClick={handleSend} disabled={!inputValue.trim() || isTyping}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-[11px] text-muted-foreground px-1 pt-1">Nhấn Enter để gửi • Shift+Enter để xuống dòng</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
