import { Plus, MessageSquare, Trash2, LogOut, Settings, User } from 'lucide-react';
import { useState } from 'react';

type SidebarProps = {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentChatId?: string;
    onNewChat: () => void;
};

type Memory = {
    id: number;
    category: string;
    content: string;
    created_at: string;
};

// Mock history data - in real app would come from local storage or backend
const MOCK_HISTORY = [
    { id: '1', title: 'Previous Chat 1', date: 'Today' },
    { id: '2', title: 'React Components', date: 'Yesterday' },
    { id: '3', title: 'Python Scripts', date: 'Previous 7 Days' },
];

export default function Sidebar({ isOpen, toggleSidebar, onNewChat }: SidebarProps) {
    const [history, setHistory] = useState(MOCK_HISTORY);
    const [view, setView] = useState<'chats' | 'memories'>('chats');
    const [memories, setMemories] = useState<Memory[]>([]);

    const fetchMemories = async () => {
        try {
            const res = await fetch('http://localhost:8000/memories');
            if (res.ok) {
                const data = await res.json();
                setMemories(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const toggleView = () => {
        if (view === 'chats') {
            setView('memories');
            fetchMemories();
        } else {
            setView('chats');
        }
    };

    return (
        <aside
            className={`
                fixed inset-y-0 left-0 z-50 bg-[var(--sidebar-bg)] text-[var(--foreground)] 
                transform transition-transform duration-300 ease-in-out
                ${isOpen ? 'translate-x-0' : '-translate-x-full'}
                flex flex-col w-[260px] border-r border-[var(--border-color)]
                md:relative md:translate-x-0
                ${!isOpen && 'md:!hidden'}
            `}
        >
            <div className="p-3 flex-1 overflow-y-auto">
                {/* Header Area */}
                <div className="flex items-center justify-between mb-4 px-2">
                    <button onClick={onNewChat} className="flex items-center gap-2 hover:bg-[var(--sidebar-hover)] p-2 rounded-md transition-colors text-sm font-medium">
                        <div className="w-6 h-6 bg-black dark:bg-white rounded-full flex items-center justify-center">
                            <span className="text-white dark:text-black text-xs font-bold">DS</span>
                        </div>
                        <span>New chat</span>
                    </button>
                    <button onClick={toggleSidebar} className="p-2 hover:bg-[var(--sidebar-hover)] rounded-md">
                        <LogOut size={16} className="rotate-180" />
                    </button>
                </div>

                {/* View Toggles */}

                {/* View Toggles */}
                <div className="flex gap-2 mb-4 px-1">
                    <button
                        onClick={() => setView('chats')}
                        className={`text-xs font-semibold px-2 py-1 rounded ${view === 'chats' ? 'bg-[var(--sidebar-hover)] text-[var(--foreground)]' : 'text-gray-500 hover:text-[var(--foreground)]'}`}
                    >
                        Chats
                    </button>
                    <button
                        onClick={toggleView}
                        className={`text-xs font-semibold px-2 py-1 rounded ${view === 'memories' ? 'bg-[var(--sidebar-hover)] text-[var(--foreground)]' : 'text-gray-500 hover:text-[var(--foreground)]'}`}
                    >
                        Dataset
                    </button>
                </div>

                {view === 'chats' ? (
                    /* History Groups */
                    <div className="flex flex-col gap-2">
                        <div className="px-3 py-2 text-xs font-semibold text-gray-500">Today</div>
                        {history.filter(h => h.date === 'Today').map(chat => (
                            <button key={chat.id} className="flex items-center gap-3 px-3 py-3 text-sm rounded-md hover:bg-[var(--sidebar-hover)] overflow-hidden text-ellipsis whitespace-nowrap">
                                <MessageSquare size={16} />
                                <span className="truncate">{chat.title}</span>
                            </button>
                        ))}

                        <div className="px-3 py-2 text-xs font-semibold text-gray-500 mt-4">Yesterday</div>
                        {history.filter(h => h.date === 'Yesterday').map(chat => (
                            <button key={chat.id} className="flex items-center gap-3 px-3 py-3 text-sm rounded-md hover:bg-[var(--sidebar-hover)] overflow-hidden text-ellipsis whitespace-nowrap">
                                <MessageSquare size={16} />
                                <span className="truncate">{chat.title}</span>
                            </button>
                        ))}
                    </div>
                ) : (
                    /* Memories List */
                    <div className="flex flex-col gap-2">
                        <div className="px-3 py-2 text-xs font-semibold text-gray-500">Long Term Memory</div>
                        {memories.length === 0 && <div className="px-3 text-xs text-gray-500">No memories yet. Tell me to "Remember X".</div>}
                        {memories.map(mem => (
                            <div key={mem.id} className="flex flex-col gap-1 px-3 py-2 text-sm rounded-md hover:bg-[var(--sidebar-hover)] border-b border-[var(--border-color)]">
                                <span className="text-[10px] uppercase font-bold text-gray-500">{mem.category}</span>
                                <span className="line-clamp-2 text-xs">{mem.content}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Bottom User Section */}
            <div className="p-3 border-t border-[var(--border-color)]">

                <button className="flex items-center gap-3 w-full px-3 py-3 text-sm rounded-md hover:bg-[var(--sidebar-hover)]">
                    <div className="w-6 h-6 rounded-sm bg-green-600 flex items-center justify-center text-white text-xs">
                        N
                    </div>
                    <span className="flex-1 text-left font-semibold">Neeli Krishna</span>
                    <Settings size={16} className="text-gray-500" />
                </button>
            </div>
        </aside>
    );
}
