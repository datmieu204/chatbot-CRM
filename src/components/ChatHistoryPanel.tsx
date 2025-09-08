import { User, MessageSquarePlus } from 'lucide-react';

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
  onCreateNew?: () => void;   
  creating?: boolean;         
  editingId?: string;
  editingName?: string;
  onEditingNameChange?: (value: string) => void;
  onRenameSubmit?: (id: string) => void;
}

export const ChatHistoryPanel = ({
  conversations,
  selectedId,
  onSelect,
  isOpen = true,
  onClose,
  onCreateNew,
  creating = false,
  editingId,
  editingName = '',
  onEditingNameChange,
  onRenameSubmit,
}: ChatHistoryPanelProps) => {
  return (
    <div className={`h-full flex flex-col ${isOpen ? 'block' : 'hidden'}`}>

 {/* Ô tạo cuộc trò chuyện mới — neutral như item trong lịch sử */}
{onCreateNew && (
  <div className="px-2 pt-2">
    <button
    onClick={onCreateNew}
    disabled={creating}
    className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-left
              border bg-background hover:bg-muted/70 active:bg-muted
              transition-colors duration-300 ease-out disabled:opacity-60">
      <div className="w-8 h-8 rounded-full border grid place-items-center">
        <MessageSquarePlus className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="min-w-0">
        <p className="text-sm font-medium truncate">Cuộc trò chuyện mới</p>
        <p className="text-xs text-muted-foreground truncate">
          {creating ? 'Đang tạo…' : 'Bấm để bắt đầu một đoạn chat'}
        </p>
      </div>
    </button>
  </div>
)}


    {/* Tiêu đề 'Lịch sử trò chuyện' */}
    <div className="px-4 py-3 border-b">
      <h2 className="text-sm font-semibold">Lịch sử trò chuyện</h2>
    </div>

    {/* Danh sách */}
    <div className="flex-1 overflow-y-auto">
      <ul className="p-2 space-y-1">
        {conversations.map((c) => (
          <li key={c.id}>
            <div
              className={`w-full flex items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors cursor-pointer
              ${c.id === selectedId
                ? 'bg-primary/15 hover:bg-primary/20 border border-primary/40 shadow-sm'
                : 'hover:bg-muted/70'}`}
              onClick={() => onSelect(c.id)}
            >
              {c.avatarUrl ? (
                <img src={c.avatarUrl} alt={c.title} className="w-8 h-8 rounded-full border" />
              ) : (
                <div className="w-8 h-8 rounded-full border grid place-items-center">
                  <User className="w-4 h-4 text-muted-foreground" />
                </div>
              )}
              <div className="min-w-0 flex-1">
                {editingId === c.id ? (
                  <input
                    autoFocus
                    value={editingName}
                    onChange={(e) => onEditingNameChange?.(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') onRenameSubmit?.(c.id);
                      if (e.key === 'Escape') onEditingNameChange?.(c.title);
                    }}
                    onBlur={() => onRenameSubmit?.(c.id)}
                    className="w-full text-sm font-medium bg-transparent border-none focus:outline-none focus:ring-0"
                  />
                ) : (
                  <>
                    <p className={`text-sm truncate ${c.id === selectedId ? 'font-semibold text-primary' : 'font-medium'}`}>
                      {c.title}
                    </p>
                    <p className={`text-xs truncate ${c.id === selectedId ? 'text-primary/70' : 'text-muted-foreground'}`}>
                      {c.latestMessage}
                    </p>
                  </>
                )}
              </div>
            </div>
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
