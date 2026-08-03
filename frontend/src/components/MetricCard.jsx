import React from 'react';

export default function MetricCard({ title, value, subtitle, highlightColor = 'text-emerald-400' }) {
  return (
    <div className="bg-[#12141d] border border-zinc-800/80 rounded-xl p-5 shadow-sm hover:border-zinc-700/80 transition-colors">
      <div className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
        {title}
      </div>
      <div className={`text-3xl font-extrabold tracking-tight font-mono ${highlightColor}`}>
        {value}
      </div>
      {subtitle && (
        <div className="text-[11px] text-zinc-500 mt-2 font-medium">
          {subtitle}
        </div>
      )}
    </div>
  );
}
