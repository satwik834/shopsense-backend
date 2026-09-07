import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Radio, 
  Sparkles, 
  DollarSign, 
  Wand2, 
  TrendingUp, 
  Tag, 
  CheckCircle2, 
  Copy, 
  RefreshCw,
  Zap,
  Activity,
  Layers
} from 'lucide-react';

export default function MerchantStudio({ currentUser }) {
  // Real-Time WebSocket State
  const [wsStatus, setWsStatus] = useState('CONNECTING');
  const [eventsStream, setEventsStream] = useState([
    {
      event_type: "CONNECTED",
      timestamp: new Date().toLocaleTimeString(),
      data: { message: "Real-time ShopSense event stream active" }
    },
    {
      event_type: "ORDER_CREATED",
      timestamp: new Date().toLocaleTimeString(),
      data: { transaction_id: 104, amount: 299.99, product_name: "Wireless Headphones", status: "completed" }
    }
  ]);

  // AI Copywriter State
  const [rawNotes, setRawNotes] = useState('ultra HD 4K noise canceling headphones, 40 hour battery life, foldability, ergonomic cushions');
  const [copyCategory, setCopyCategory] = useState('Electronics');
  const [targetPrice, setTargetPrice] = useState('299.99');
  const [listingOutput, setListingOutput] = useState(null);
  const [generatingCopy, setGeneratingCopy] = useState(false);

  // Price Optimizer State
  const [productsList, setProductsList] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [priceOptimization, setPriceOptimization] = useState(null);
  const [optimizingPrice, setOptimizingPrice] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const wsUrl = `ws://${window.location.hostname}:8000/ws/events`;
    let ws = null;
    try {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => setWsStatus('CONNECTED');
      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setEventsStream(prev => [{
            ...parsed,
            timestamp: new Date().toLocaleTimeString()
          }, ...prev.slice(0, 19)]);
        } catch (e) {
          console.warn("WebSocket parse error:", e);
        }
      };
      ws.onerror = () => setWsStatus('DISCONNECTED');
      ws.onclose = () => setWsStatus('DISCONNECTED');
    } catch (e) {
      setWsStatus('DISCONNECTED');
    }

    // Load product list for price optimizer
    api.getProducts().then(prods => {
      setProductsList(prods);
      if (prods.length > 0) {
        setSelectedProductId(prods[0].id);
      }
    }).catch(err => console.error("Failed to load products:", err));

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const handleGenerateListing = async (e) => {
    e.preventDefault();
    if (!rawNotes.trim()) return;

    try {
      setGeneratingCopy(true);
      const parsedPrice = targetPrice ? parseFloat(targetPrice) : null;
      const res = await api.generateProductListing(rawNotes, copyCategory, parsedPrice);
      setListingOutput(res);
    } catch (err) {
      console.error("AI Listing generation failed:", err);
    } finally {
      setGeneratingCopy(false);
    }
  };

  const handleOptimizePrice = async () => {
    if (!selectedProductId) return;

    try {
      setOptimizingPrice(true);
      const res = await api.optimizeProductPrice(Number(selectedProductId));
      setPriceOptimization(res);
    } catch (err) {
      console.error("Price optimization failed:", err);
    } finally {
      setOptimizingPrice(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Zap className="w-6 h-6 text-amber-400" />
            AI Merchant Studio & Real-Time Event Hub
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time WebSocket event ticker, AI product copywriter & smart price elasticity optimizer
          </p>
        </div>

        {/* WebSocket Connection Status Pill */}
        <div className="flex items-center gap-2 bg-slate-950 px-3.5 py-1.5 rounded-full border border-slate-800 text-xs font-mono">
          <span className={`w-2.5 h-2.5 rounded-full ${
            wsStatus === 'CONNECTED' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
          }`} />
          <span className="text-slate-300 font-bold">WEBSOCKET STREAM: {wsStatus}</span>
        </div>
      </div>

      {/* SECTION 1: Real-Time Event Ticker */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            Real-Time Marketplace Event Stream
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">
            {eventsStream.length} Active Events Logged
          </span>
        </div>

        <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-4 max-h-44 overflow-y-auto space-y-2.5 font-mono text-xs">
          {eventsStream.map((evt, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 bg-slate-900/60 rounded border border-slate-800/50">
              <div className="flex items-center gap-3">
                <span className="text-slate-500 text-[10px]">{evt.timestamp}</span>
                <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-bold text-[10px] border border-indigo-500/20">
                  {evt.event_type}
                </span>
                <span className="text-slate-300 truncate max-w-md">
                  {JSON.stringify(evt.data)}
                </span>
              </div>
              <span className="text-emerald-400 font-bold text-[10px]">LIVE</span>
            </div>
          ))}
        </div>
      </div>

      {/* SECTION 2 & 3: Side-by-Side Copywriter & Price Optimizer */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* AI Product Copywriter */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-800/80 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Wand2 className="w-4 h-4 text-purple-400" />
              AI Automated Product Copywriter
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Draft SEO-optimized product titles, descriptions, and feature tags from raw notes
            </p>
          </div>

          <form onSubmit={handleGenerateListing} className="space-y-3">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Raw Product Notes / Features</label>
              <textarea
                rows={3}
                value={rawNotes}
                onChange={(e) => setRawNotes(e.target.value)}
                placeholder="Enter raw features or bullet points..."
                className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl p-3 text-xs outline-none focus:border-indigo-500 font-sans"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Category</label>
                <select
                  value={copyCategory}
                  onChange={(e) => setCopyCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl p-2.5 text-xs outline-none focus:border-indigo-500 font-semibold"
                >
                  <option value="Electronics">Electronics</option>
                  <option value="Apparel">Apparel</option>
                  <option value="Fitness">Fitness</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">Target Price (INR)</label>
                <input
                  type="number"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  placeholder="299.99"
                  className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl p-2.5 text-xs outline-none focus:border-indigo-500 font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={generatingCopy || !rawNotes.trim()}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold rounded-xl text-xs transition shadow-sm"
            >
              {generatingCopy ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Generate AI Listing Copy
            </button>
          </form>

          {listingOutput && (
            <div className="pt-3 border-t border-slate-800/80 space-y-3">
              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider font-mono">
                    SUGGESTED TITLE
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold font-mono ${
                    listingOutput.is_gemini_powered ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {listingOutput.is_gemini_powered ? 'Gemini 2.5 Flash' : 'Standard Copywriter'}
                  </span>
                </div>
                <h4 className="font-bold text-white text-sm">{listingOutput.suggested_title}</h4>
                <p className="text-xs text-slate-300 leading-relaxed pt-1">{listingOutput.detailed_description}</p>
              </div>

              {listingOutput.seo_tags?.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {listingOutput.seo_tags.map((tag, i) => (
                    <span key={i} className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px] font-mono border border-slate-700">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* AI Smart Price Optimizer */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-800/80 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              AI Smart Price Optimizer
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Analyze product sales velocity, category averages, and margin elasticity
            </p>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">Select Catalog Product</label>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl p-2.5 text-xs outline-none focus:border-indigo-500 font-semibold"
              >
                {productsList.map((p) => (
                  <option key={p.id} value={p.id}>
                    #{p.id} - {p.name} (INR {p.price.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleOptimizePrice}
              disabled={optimizingPrice || !selectedProductId}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold rounded-xl text-xs transition shadow-sm"
            >
              {optimizingPrice ? <RefreshCw className="w-4 h-4 animate-spin" /> : <DollarSign className="w-4 h-4" />}
              Run AI Price Optimization
            </button>
          </div>

          {priceOptimization && (
            <div className="pt-3 border-t border-slate-800/80 space-y-3">
              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white">{priceOptimization.product_name}</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px] border border-emerald-500/30 font-mono">
                    {priceOptimization.elasticity_rating} ELASTICITY
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/60 font-mono text-xs">
                  <div>
                    <span className="text-slate-400 text-[10px] block">CURRENT PRICE</span>
                    <span className="text-slate-200 font-bold">INR {priceOptimization.current_price.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-emerald-400 text-[10px] block font-bold">RECOMMENDED PRICE</span>
                    <span className="text-emerald-400 font-bold text-sm">INR {priceOptimization.recommended_price.toFixed(2)}</span>
                  </div>
                </div>

                <div className="pt-2 text-xs text-slate-300 leading-relaxed">
                  <p className="font-semibold text-indigo-300">Strategy Rationale:</p>
                  <p className="mt-0.5">{priceOptimization.pricing_strategy_rationale}</p>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
