import React, { useState } from 'react';
import { api } from '../api';
import { 
  Sparkles, 
  Search, 
  Send, 
  ShoppingBag,
  RefreshCw
} from 'lucide-react';

export default function AIAssistant({ currentUser }) {
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

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShoppingBag className="w-6 h-6 text-indigo-400" />
            AI Shopping Assistant
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Your personalized RAG-powered conversational shopping guide.
          </p>
        </div>
      </div>

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
                  {item.is_gemini_powered ? 'AI Powered' : 'Local RAG Catalog Engine'}
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
    </div>
  );
}
