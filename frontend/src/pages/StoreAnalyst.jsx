import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Bot, 
  Sparkles, 
  RefreshCw,
  Store
} from 'lucide-react';

export default function StoreAnalyst({ currentUser }) {
  const [advisorReport, setAdvisorReport] = useState(null);
  const [loadingAdvisor, setLoadingAdvisor] = useState(false);
  const [advisorError, setAdvisorError] = useState(null);
  const [selectedVendorId, setSelectedVendorId] = useState('');
  const [vendorsList, setVendorsList] = useState([]);

  const isAdmin = currentUser?.role?.toLowerCase() === 'admin';

  useEffect(() => {
    if (isAdmin) {
      api.getVendors()
        .then(data => setVendorsList(data || []))
        .catch(err => console.error('Failed to fetch vendors list for admin:', err));
    }
  }, [currentUser, isAdmin]);

  const loadAdvisorReport = async (vendorIdOverride = selectedVendorId) => {
    try {
      setLoadingAdvisor(true);
      setAdvisorError(null);
      const targetId = vendorIdOverride ? parseInt(vendorIdOverride, 10) : null;
      const res = await api.getAIStoreAdvisorReport(targetId);
      setAdvisorReport(res);
    } catch (err) {
      console.error('Failed to load AI Store Advisor report:', err);
      setAdvisorError(err.message || 'Failed to generate AI store advisor report');
    } finally {
      setLoadingAdvisor(false);
    }
  };

  useEffect(() => {
    if (!advisorReport) {
      loadAdvisorReport();
    }
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Store className="w-6 h-6 text-indigo-400" />
            Executive Store Analyst
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            AI-powered store diagnostics, inventory turnover insights, and actionable recommendations.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            Diagnostic Audit
          </h2>
          <div className="flex items-center gap-3">
            {isAdmin && (
              <select
                value={selectedVendorId}
                onChange={(e) => {
                  const newId = e.target.value;
                  setSelectedVendorId(newId);
                  loadAdvisorReport(newId);
                }}
                className="bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-1.5 text-xs font-semibold outline-none focus:border-indigo-500"
              >
                <option value="">All Platform Stores (Marketplace Overview)</option>
                {vendorsList.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.store_name || v.name}
                  </option>
                ))}
              </select>
            )}
            <button
              onClick={() => loadAdvisorReport()}
              disabled={loadingAdvisor}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingAdvisor ? 'animate-spin' : ''}`} />
              Re-Audit Store Data
            </button>
          </div>
        </div>

        {advisorError && (
          <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-rose-400 text-sm">
            {advisorError}
          </div>
        )}

        {advisorReport && (
          <div className="space-y-6">
            {/* Executive Summary Banner */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider font-mono">
                  {advisorReport.store_name} • Store Summary
                </span>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono ${
                  advisorReport.is_gemini_powered
                    ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}>
                  {advisorReport.is_gemini_powered ? 'AI Executive Advisory' : 'Standard Diagnostic Audit'}
                </span>
              </div>
              <p className="text-base font-semibold text-white">
                {advisorReport.executive_summary}
              </p>
            </div>

            {/* Diagnostic Findings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {advisorReport.diagnostics?.map((d, i) => (
                <div key={i} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{d.category}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                      d.impact_level === 'HIGH' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                      d.impact_level === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                      'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    }`}>
                      {d.impact_level} IMPACT
                    </span>
                  </div>

                  <h3 className="font-bold text-white text-base">{d.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed">{d.finding}</p>

                  <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-xs text-indigo-300 font-medium">
                    <strong>Recommendation:</strong> {d.actionable_recommendation}
                  </div>
                </div>
              ))}
            </div>

            {/* AI Generated Strategic Advice Report */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-3 shadow-sm">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                AI Executive Strategy & Action Plan
              </h3>
              <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/70 p-5 rounded-xl border border-slate-800/80 font-sans">
                {advisorReport.ai_generated_strategy}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
