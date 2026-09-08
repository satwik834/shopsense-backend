import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Bot, 
  Sparkles, 
  Search, 
  Send, 
  Store, 
  AlertTriangle, 
  CheckCircle2, 
  TrendingUp, 
  Cpu, 
  ShoppingBag,
  RefreshCw
} from 'lucide-react';

export default function AIAssistant({ currentUser }) {
  const [activeTab, setActiveTab] = useState('shopping'); // 'shopping' or 'advisor'

  // Shopping Assistant State
  const [queryInput, setQueryInput] = useState('');
  const [maxPriceInput, setMaxPriceInput] = useState('');
  const [categoryInput, setCategoryInput] = useState('');
  const [shoppingHistory, setShoppingHistory] = useState([
    {
      query: "Find noise-canceling headphones under 300",
      ai_response: "I recommend the Wireless Noise-Canceling Headphones in Electronics priced at INR 299.99 from Apex Electronics. It has a high relevance match score and is currently In Stock.",
      suggested_products: [
        {
          product_id: 1,
          product_name: "Wireless Noise-Canceling Headphones",
          category: "Electronics",
          price: 299.99,
          vendor_name: "Apex Electronics",
          stock_status: "IN_STOCK",
          match_score: 95,
          match_reason: "Matched search term 'headphones', Price INR 299.99 within budget"
        }
      ],
      is_gemini_powered: false
    }
  ]);
  const [searching, setSearching] = useState(false);

  // Store Advisor State
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

  const handleAskShoppingAssistant = async (e) => {
    e.preventDefault();
    if (!queryInput.trim()) return;

    try {
      setSearching(true);
      const parsedPrice = maxPriceInput ? parseFloat(maxPriceInput) : null;
      const res = await api.askAIShoppingAssistant(queryInput, parsedPrice, categoryInput);
      setShoppingHistory(prev => [res, ...prev]);
      setQueryInput('');
    } catch (err) {
      console.error('AI Shopping Assistant error:', err);
    } finally {
      setSearching(false);
    }
  };

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
    if (activeTab === 'advisor' && !advisorReport) {
      loadAdvisorReport();
    }
  }, [activeTab]);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            AI & Decision Intelligence Studio
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            RAG-powered conversational shopping assistant & Gemini AI executive store diagnostics
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 w-max">
          <button
            onClick={() => setActiveTab('shopping')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
              activeTab === 'shopping' 
                ? 'bg-indigo-600 text-white shadow-sm' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            AI Shopping Assistant
          </button>
          <button
            onClick={() => setActiveTab('advisor')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
              activeTab === 'advisor' 
                ? 'bg-indigo-600 text-white shadow-sm' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Store className="w-3.5 h-3.5" />
            AI Store Analyst
          </button>
        </div>
      </div>

      {/* TAB 1: RAG AI Shopping Assistant */}
      {activeTab === 'shopping' && (
        <div className="space-y-6">
          {/* Query Bar */}
          <form onSubmit={handleAskShoppingAssistant} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  placeholder="Ask the AI Shopping Assistant (e.g., 'Find noise-canceling headphones under 300')..."
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none focus:border-indigo-500 font-medium"
                />
              </div>

              <input
                type="number"
                placeholder="Max Price (INR)"
                value={maxPriceInput}
                onChange={(e) => setMaxPriceInput(e.target.value)}
                className="w-36 bg-slate-950 border border-slate-800 text-white rounded-xl px-3 py-2.5 text-xs outline-none focus:border-indigo-500 font-medium font-mono"
              />

              <select
                value={categoryInput}
                onChange={(e) => setCategoryInput(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-slate-300 rounded-xl px-3 py-2.5 text-xs font-semibold outline-none focus:border-indigo-500"
              >
                <option value="">All Categories</option>
                <option value="Electronics">Electronics</option>
                <option value="Apparel">Apparel</option>
                <option value="Fitness">Fitness</option>
              </select>

              <button
                type="submit"
                disabled={searching || !queryInput.trim()}
                className="flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold rounded-xl text-xs transition shadow-sm"
              >
                {searching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                Ask AI
              </button>
            </div>
          </form>

          {/* Conversation & Grounded Product Cards */}
          <div className="space-y-5">
            {shoppingHistory.map((item, idx) => (
              <div key={idx} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex items-start justify-between gap-4 border-b border-slate-800/80 pb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs">
                      AI
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Customer Query:</p>
                      <p className="text-sm font-bold text-white">"{item.query}"</p>
                    </div>
                  </div>

                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold font-mono ${
                    item.is_gemini_powered 
                      ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}>
                    {item.is_gemini_powered ? 'Gemini 2.5 Flash Powered' : 'Local RAG Catalog Engine'}
                  </span>
                </div>

                <p className="text-sm text-slate-200 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                  {item.ai_response}
                </p>

                {item.suggested_products?.length > 0 && (
                  <div className="pt-2">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                      Grounded Catalog Recommendations ({item.suggested_products.length} Matches)
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {item.suggested_products.map((p) => (
                        <div key={p.product_id} className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 font-mono">{p.category}</span>
                              <h4 className="font-bold text-white text-sm mt-0.5">{p.product_name}</h4>
                            </div>
                            <span className="text-xs font-bold text-emerald-400 font-mono">
                              ₹{p.price.toFixed(2)}
                            </span>
                          </div>

                          <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                            <span>Merchant: <strong className="text-slate-200">{p.vendor_name}</strong></span>
                            <span className="text-indigo-400 font-mono font-semibold">Match Score: {p.match_score}/100</span>
                          </div>

                          <p className="text-[11px] text-slate-500 italic bg-slate-900/60 p-2 rounded border border-slate-800/50">
                            {p.match_reason}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: AI Store Analyst */}
      {activeTab === 'advisor' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-400" />
              Executive Store Diagnostic Audit
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
                    {advisorReport.is_gemini_powered ? 'Gemini 2.5 Flash Advisory' : 'Standard Diagnostic Audit'}
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
      )}
    </div>
  );
}
