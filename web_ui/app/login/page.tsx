'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Monitor } from 'lucide-react';

export default function LoginPage() {
    const [userName, setUserName] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const res = await fetch('http://localhost:8089/empengagement/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userName, password }),
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('token', data.token);
                router.push('/');
            } else {
                setError('Invalid username or password');
            }
        } catch (err) {
            setError('Failed to connect to authentication server');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-[var(--background)] text-[var(--foreground)] p-4">
            <div className="w-full max-w-md bg-[var(--bot-msg-bg)] p-8 rounded-2xl shadow-xl border border-[var(--border-color)]">
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 bg-[#19c37d] rounded-xl flex items-center justify-center mb-4">
                        <Monitor size={32} className="text-white" />
                    </div>
                    <h1 className="text-2xl font-bold">Welcome Back</h1>
                    <p className="text-gray-500 text-sm mt-2">Login to your Digital Self</p>
                </div>

                <form onSubmit={handleLogin} className="flex flex-col gap-4">
                    <div className="flex flex-col gap-1">
                        <label className="text-xs font-semibold text-gray-500 uppercase">Username</label>
                        <input
                            type="text"
                            value={userName}
                            onChange={(e) => setUserName(e.target.value)}
                            className="bg-[var(--input-bg)] border border-[var(--border-color)] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-[#19c37d]/50 transition-all text-sm"
                            placeholder="krishna01"
                            required
                        />
                    </div>

                    <div className="flex flex-col gap-1">
                        <label className="text-xs font-semibold text-gray-500 uppercase">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="bg-[var(--input-bg)] border border-[var(--border-color)] rounded-lg px-4 py-3 outline-none focus:ring-2 ring-[#19c37d]/50 transition-all text-sm"
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    {error && <p className="text-red-500 text-xs mt-1">{error}</p>}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="bg-[#19c37d] hover:bg-[#1aab70] text-white font-bold py-3 rounded-lg transition-all shadow-md mt-4 disabled:opacity-50"
                    >
                        {isLoading ? 'Logging in...' : 'Log In'}
                    </button>
                </form>

                <div className="mt-8 text-center text-xs text-gray-500">
                    <p>Default Admin: krishna01 / securepass</p>
                </div>
            </div>
        </div>
    );
}
