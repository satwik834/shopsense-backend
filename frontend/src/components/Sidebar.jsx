import React from 'react';
import { LayoutDashboard, Users, Package, BarChart3 } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'vendors', label: 'Vendors Control', icon: Users },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'analytics', label: 'Analytics Engine', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 border-r border-zinc-800/80 bg-[#090a0f] min-h-screen flex flex-col justify-between p-4 selection:bg-indigo-500/20">
      <div>
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-3 py-4 mb-6">
          <div className="h-9 w-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center font-mono font-bold text-indigo-400 text-lg shadow-inner">
            S
          </div>
          <div>
            <h1 className="font-bold text-base text-zinc-100 tracking-tight">ShopSense OS</h1>
            <p className="text-[11px] text-zinc-500 font-medium">Enterprise Analytics v0.1</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-sm'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-zinc-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer info */}
      <div className="p-3 bg-zinc-900/40 border border-zinc-800/60 rounded-xl">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs text-zinc-300 font-medium">Backend Live</span>
        </div>
        <p className="text-[11px] text-zinc-500 mt-1">SQLite • SQLAlchemy ORM</p>
      </div>
    </aside>
  );
}
