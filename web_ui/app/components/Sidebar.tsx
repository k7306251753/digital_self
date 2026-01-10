import { Plus, MessageSquare, LogOut, Settings } from 'lucide-react';
import { useState, useEffect } from 'react';

type SidebarProps = {
    isOpen: boolean;
    toggleSidebar: () => void;
    currentChatId?: string;
    onNewChat: () => void;
    onUserChange: (user: any) => void;
    activeUser: any;
    onLogout: () => void;
    onSelectChat: (chatId: string) => void;
};

type Memory = {
    id: number;
    category: string;
    content: string;
    created_at: string;
    // ...
};

type ChatSession = {
    id: string;
    title: string;
    updated_at: string;
};

export default function Sidebar({ isOpen, toggleSidebar, onNewChat, onUserChange, activeUser, onLogout, onSelectChat }: SidebarProps) {
    const [chats, setChats] = useState<ChatSession[]>([]);
    const [view, setView] = useState<'chats' | 'memories'>('chats');
    const [memories, setMemories] = useState<Memory[]>([]);
    const [participants, setParticipants] = useState<any[]>([]);

    const fetchChats = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('http://localhost:8000/chats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setChats(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    // Poll for chats occasionally or just on mount/view switch
    useEffect(() => {
        if (view === 'chats') fetchChats();
    }, [view, isOpen]);

    const fetchMemories = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('http://localhost:8000/memories', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (res.ok) {
                const data = await res.json();
                setMemories(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    const fetchParticipants = async () => {
        try {
            console.log("[Sidebar] Fetching participants...");
            const res = await fetch('http://localhost:8089/empengagement/participants');
            if (res.ok) {
                const data = await res.json();
                console.log("[Sidebar] Data received:", data);

                // Handle different response structures
                const pList = Array.isArray(data) ? data : (data.value && Array.isArray(data.value) ? data.value : []);

                setParticipants(pList);
            } else {
                console.error("[Sidebar] Fetch failed with status:", res.status);
            }
        } catch (e) {
            console.error("[Sidebar] Fetch error:", e);
        }
    };

    useEffect(() => {
        fetchParticipants();
    }, []);

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
                        Memories
                    </button>
                </div>

                {view === 'chats' ? (
                    <div className="flex flex-col gap-2">
                        <div className="px-3 py-2 text-xs font-semibold text-gray-500">Recent Chats</div>
                        {chats.length === 0 && <div className="px-3 text-xs text-gray-500">No previous chats.</div>}
                        {chats.map(chat => (
                            <button
                                key={chat.id}
                                onClick={() => onSelectChat(chat.id)}
                                className="flex items-center gap-3 px-3 py-3 text-sm rounded-md hover:bg-[var(--sidebar-hover)] overflow-hidden text-ellipsis whitespace-nowrap text-left"
                            >
                                <MessageSquare size={16} />
                                <span className="truncate">{chat.title}</span>
                            </button>
                        ))}
                    </div>
                ) : (
                    <div className="flex flex-col gap-2">
                        <div className="px-3 py-2 text-xs font-semibold text-gray-500">Long Term Memory</div>
                        {memories.length === 0 && <div className="px-3 text-xs text-gray-500">No memories yet.</div>}
                        {memories.map(mem => (
                            <div key={mem.id} className="flex flex-col gap-1 px-3 py-2 text-sm rounded-md hover:bg-[var(--sidebar-hover)] border-b border-[var(--border-color)]">
                                <span className="text-[10px] uppercase font-bold text-gray-500">{mem.category}</span>
                                <span className="line-clamp-2 text-xs">{mem.content}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Colleagues section removed as per user request */}
            </div>

            <div className="p-4 border-t border-[var(--border-color)]">
                {activeUser ? (
                    <div className="flex flex-col gap-1 px-3">
                        <div className="text-[10px] uppercase font-bold text-gray-400">Logged in as</div>
                        <div className="text-sm font-semibold text-[var(--foreground)]">{activeUser.fullName}</div>
                        <div className="text-[11px] text-[#19c37d] font-medium">{activeUser.points} points</div>
                    </div>
                ) : (
                    <div className="px-3 text-xs text-gray-500">Not logged in</div>
                )}
                <button
                    onClick={onLogout}
                    className="mt-4 w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 rounded-md transition-colors border border-red-200 dark:border-red-900/20"
                >
                    <LogOut size={16} />
                    <span>Logout</span>
                </button>
            </div>
        </aside>
    );
}
