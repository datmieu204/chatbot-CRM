import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User, LogOut, Menu } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { ChatHistoryPanel } from './ChatHistoryPanel';
import type { Conversation, Message } from '@/contexts/AuthContext';

export const ChatInterface = () => {
  const { user, logout, fetchConversations, fetchMessages, sendMessage } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations khi mount
  useEffect(() => {
    const loadConversations = async () => {
      const convs = await fetchConversations();
      setConversations(convs);
      if (convs.length > 0) setSelectedConvId(convs[0].id);
    };
    loadConversations();
  }, [fetchConversations]);

  // Load messages khi conversation thay đổi
  useEffect(() => {
    if (!selectedConvId) return;
    const loadMessages = async () => {
      const msgs = await fetchMessages(selectedConvId);
      setMessages(msgs);
    };
    loadMessages();
  }, [selectedConvId, fetchMessages]);
  console.log(user);
  
  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => { scrollToBottom(); }, [messages, selectedConvId]);

  const handleSend = async () => {
    if (!inputValue.trim() || !user || !selectedConvId) return;

    const userMessage: Message = await sendMessage(selectedConvId, inputValue) as Message;
    if (!userMessage) return;

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Giả lập trả lời bot nếu muốn (hoặc lấy từ backend nếu có)
    setTimeout(() => {
      const botMessage: Message = {
        id: Date.now().toString(),
        conversation_id: selectedConvId,
        sender_id: 'bot',
        content: 'Bot đang trả lời bạn...',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1200);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const selectedConv = conversations.find(c => c.id === selectedConvId);

  return (
    <div className="h-screen w-full bg-gradient-to-b from-background to-muted/30">
      {/* Header */}
      <header className="h-16 border-b bg-background/80 backdrop-blur sticky top-0 z-40">
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

      {/* Sidebar */}
      <aside className="hidden md:block fixed top-16 left-0 h-[calc(100vh-4rem)] w-72 border-r bg-background z-30">
        <ChatHistoryPanel
          conversations={conversations}
          selectedId={selectedConvId}
          onSelect={setSelectedConvId}
          isOpen
        />
      </aside>

      {/* Sidebar mobile */}
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
            />
          </div>
        </div>
      )}

      {/* Main chat area */}
      <main className="pt-4 md:pl-72 h-[calc(100vh-4rem)]">
        <div className="h-full mx-auto max-w-3xl px-4 flex flex-col">
          <ScrollArea className="flex-1">
            <div className="py-2 space-y-4">
              {messages.map(m => (
                <div key={m.id} className={`flex ${m.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}>
                  <div className={`rounded-2xl px-4 py-3 shadow-sm max-w-[85%] ${
                    m.sender_id === user?.id ? 'bg-primary text-primary-foreground' : 'bg-card text-card-foreground border'
                  }`}>
                    <div className="flex items-start gap-2">
                      {m.sender_id === user?.id ? <User className="h-4 w-4 mt-0.5 opacity-80" /> : <Bot className="h-4 w-4 mt-0.5 text-primary" />}
                      <div>
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{m.content}</p>
                        <p className={`text-[10px] mt-1 ${m.sender_id === user?.id ? 'opacity-80' : 'text-muted-foreground'}`}>
                          {new Date(m.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
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
