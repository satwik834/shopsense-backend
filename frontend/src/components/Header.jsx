import React from 'react';
import { User, LogOut, ShieldCheck, Store } from 'lucide-react';

export default function Header({ user, onLogout }) {
  if (!user) return null;

  const isAdmin = user.role === 'admin';

  return (
    <header className="border-b border-zinc-800/80 bg-[#090a0f] px-8 py-3.5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono text-zinc-400">SESSION PORTAL:</span>
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold border ${
          isAdmin
            ? 'bg-purple-500/10 text-purple-300 border-purple-500/30'
            : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
        }`}>
          {isAdmin ? <ShieldCheck className="w-3.5 h-3.5 text-purple-400" /> : <Store className="w-3.5 h-3.5 text-emerald-400" />}
          {isAdmin ? 'ADMINISTRATOR CONTROL' : 'VENDOR PORTAL'}
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right">
          <div className="text-xs font-bold text-zinc-100">{user.user_name || user.email}</div>
          <div className="text-[10px] font-mono text-zinc-400">{user.email}</div>
        </div>

        <button
          onClick={onLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 hover:border-zinc-700 bg-zinc-900 text-zinc-400 hover:text-zinc-200 text-xs font-medium transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </header>
  );
}
