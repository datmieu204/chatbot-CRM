import { User } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  avatarUrl?: string;
  latestMessage: string;
}
interface ChatHistoryPanelProps {
  conversations: Conversation[];
  selectedId: string;
  onSelect: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const ChatHistoryPanel = ({
  conversations,
  selectedId,
  onSelect,
  isOpen = true,
  onClose,
}: ChatHistoryPanelProps) => {
  return (
    <div className={`h-full flex flex-col ${isOpen ? 'block' : 'hidden'}`}>
      <div className="px-4 py-3 border-b">
        <h2 className="text-sm font-semibold">Lịch sử trò chuyện</h2>
      </div>

      <div className="flex-1 overflow-y-auto">
        <ul className="p-2 space-y-1">
          {conversations.map((c) => (
            <li key={c.id}>
              <button
                onClick={() => onSelect(c.id)}
                className={`w-full flex items-center gap-3 rounded-lg px-3 py-2 text-left transition
                ${c.id === selectedId ? 'bg-muted' : 'hover:bg-muted/70'}`}
              >
                {c.avatarUrl ? (
                  <img src={c.avatarUrl} alt={c.title} className="w-8 h-8 rounded-full border" />
                ) : (
                  <div className="w-8 h-8 rounded-full border grid place-items-center">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                )}
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{c.title}</p>
                  <p className="text-xs text-muted-foreground truncate">{c.latestMessage}</p>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {onClose && (
        <div className="md:hidden px-3 py-2 border-t">
          <button className="text-sm text-primary" onClick={onClose}>Đóng</button>
        </div>
      )}
    </div>
  );
};
