import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Sparkles, 
  Flame, 
  Share2, 
  User, 
  RefreshCw, 
  Layers, 
  Tag, 
  TrendingUp, 
  CheckCircle2, 
  ShoppingBag,
  ArrowRight
} from 'lucide-react';

export default function Recommendations() {
  const [categories, setCategories] = useState(['All Categories', 'Electronics', 'Apparel', 'Fitness']);
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [topSellers, setTopSellers] = useState([]);
  
  // Cross Sell state
  const [productsList, setProductsList] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [crossSellData, setCrossSellData] = useState(null);

  // Personalized Recs state
  const [customersList, setCustomersList] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [personalizedData, setPersonalizedData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [crossLoading, setCrossLoading] = useState(false);
  const [custLoading, setCustLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [prods, custs, topRecs] = await Promise.all([
        api.getProducts(),
        api.getCustomers(),
        api.getTopSellingRecommendations(selectedCategory === 'All Categories' ? null : selectedCategory)
      ]);

      setProductsList(prods);
      setCustomersList(custs);
      setTopSellers(topRecs.top_sellers || []);

      if (prods.length > 0 && !selectedProductId) {
        setSelectedProductId(prods[0].id);
      }
      if (custs.length > 0 && !selectedCustomerId) {
        setSelectedCustomerId(custs[0].id);
      }
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      setError(err.message || 'Failed to load recommendation engine');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleCategoryChange = async (cat) => {
    setSelectedCategory(cat);
    try {
      const topRecs = await api.getTopSellingRecommendations(cat === 'All Categories' ? null : cat);
      setTopSellers(topRecs.top_sellers || []);
    } catch (err) {
      console.error('Failed to filter category:', err);
    }
  };

  const handleCrossSellLookup = async (pId) => {
    setSelectedProductId(pId);
    if (!pId) return;
    try {
      setCrossLoading(true);
      const res = await api.getFrequentlyBoughtTogether(pId);
      setCrossSellData(res);
    } catch (err) {
      console.error('Failed cross-sell lookup:', err);
    } finally {
      setCrossLoading(false);
    }
  };

  const handleCustomerRecLookup = async (cId) => {
    setSelectedCustomerId(cId);
    if (!cId) return;
    try {
      setCustLoading(true);
      const res = await api.getCustomerRecommendations(cId);
      setPersonalizedData(res);
    } catch (err) {
      console.error('Failed customer rec lookup:', err);
    } finally {
      setCustLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProductId) {
      handleCrossSellLookup(selectedProductId);
    }
  }, [selectedProductId]);

  useEffect(() => {
    if (selectedCustomerId) {
      handleCustomerRecLookup(selectedCustomerId);
    }
  }, [selectedCustomerId]);

  if (loading && topSellers.length === 0) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        <span className="ml-3 text-slate-400 font-medium">Loading recommendation engine models...</span>
      </div>
    );
  }

  return (
    <div className="space-y-10 animate-fadeIn">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Rule-Based Product Recommendation Engine</h1>
          <p className="text-sm text-slate-400 mt-1">
            Category sales velocity bestsellers, co-purchasing cross-sell rules, and personalized affinity matching.
          </p>
        </div>
        <button
          onClick={loadInitialData}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg text-sm transition font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Engine
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Module 1: Top Selling by Category */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <Flame className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-white">Category Bestsellers & Top Velocity Products</h2>
          </div>

          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => handleCategoryChange(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  selectedCategory === cat
                    ? 'bg-indigo-600 text-white shadow'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/60'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {topSellers.map((item, idx) => (
            <div 
              key={item.product_id}
              className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 bg-indigo-600/20 text-indigo-400 border-b border-l border-indigo-500/30 text-[10px] font-bold px-2.5 py-0.5 rounded-bl-lg font-mono">
                RANK #{idx + 1}
              </div>

              <div>
                <span className="text-[11px] font-semibold uppercase tracking-wider text-indigo-400">
                  {item.category || 'General'}
                </span>
                <h3 className="text-sm font-bold text-white mt-1 pr-12">{item.name}</h3>
                <p className="text-xs text-slate-400 mt-1">Merchant: {item.vendor_name}</p>
                <div className="mt-3 text-xs text-slate-300 bg-slate-900 p-2 rounded-lg border border-slate-800/80">
                  {item.recommendation_reason}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-500 block">Unit Price</span>
                  <span className="text-sm font-bold text-white font-mono">
                    ₹{item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 block">Units Sold</span>
                  <span className="text-xs font-bold text-emerald-400 font-mono">
                    {item.total_units_sold} Units
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Module 2 & 3: Frequently Bought Together & Customer Personalized Recs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Module 2: Frequently Bought Together */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
          <div className="flex items-center gap-2.5">
            <Share2 className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-lg font-bold text-white">Frequently Bought Together</h2>
              <p className="text-xs text-slate-400 mt-0.5">Cross-selling affinity rules for co-purchased items</p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
              Select Base Catalog Product:
            </label>
            <select
              value={selectedProductId}
              onChange={(e) => handleCrossSellLookup(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl px-3 py-2 text-sm outline-none focus:border-indigo-500 font-semibold"
            >
              {productsList.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} (₹{p.price.toFixed(2)} - {p.category})
                </option>
              ))}
            </select>
          </div>

          {crossLoading ? (
            <div className="py-12 flex justify-center items-center text-slate-400 text-xs">
              <RefreshCw className="w-5 h-5 animate-spin mr-2 text-indigo-400" />
              Calculating co-purchase affinity scores...
            </div>
          ) : crossSellData?.frequently_bought_together?.length > 0 ? (
            <div className="space-y-3">
              {crossSellData.frequently_bought_together.map((rec) => (
                <div 
                  key={rec.product_id}
                  className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-center justify-between gap-3"
                >
                  <div>
                    <h4 className="text-sm font-semibold text-white">{rec.name}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{rec.recommendation_reason}</p>
                    <span className="text-[11px] text-indigo-400 font-mono mt-1 inline-block">
                      Affinity Score: {rec.recommendation_score}
                    </span>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-sm font-bold text-white font-mono block">
                      ₹{rec.price.toFixed(2)}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      Stock: {rec.stock_quantity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 text-center text-slate-500 text-xs">
              No direct co-purchase pairings found for this catalog item.
            </div>
          )}
        </div>

        {/* Module 3: Customer Personalized Recommendations */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
          <div className="flex items-center gap-2.5">
            <User className="w-5 h-5 text-emerald-400" />
            <div>
              <h2 className="text-lg font-bold text-white">Personalized Customer Feed</h2>
              <p className="text-xs text-slate-400 mt-0.5">Recommendations weighted by historical purchase categories</p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
              Select Customer Account:
            </label>
            <select
              value={selectedCustomerId}
              onChange={(e) => handleCustomerRecLookup(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl px-3 py-2 text-sm outline-none focus:border-indigo-500 font-semibold"
            >
              {customersList.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.email})
                </option>
              ))}
            </select>
          </div>

          {custLoading ? (
            <div className="py-12 flex justify-center items-center text-slate-400 text-xs">
              <RefreshCw className="w-5 h-5 animate-spin mr-2 text-emerald-400" />
              Aggregating category affinity history...
            </div>
          ) : personalizedData?.recommended_products?.length > 0 ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span>Top Affinity Categories:</span>
                {personalizedData.favorite_categories.length > 0 ? (
                  personalizedData.favorite_categories.map((cat) => (
                    <span key={cat} className="bg-slate-800 text-slate-200 px-2 py-0.5 rounded font-semibold text-[11px]">
                      {cat}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500">No previous orders (General feed)</span>
                )}
              </div>

              {personalizedData.recommended_products.map((rec) => (
                <div 
                  key={rec.product_id}
                  className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-center justify-between gap-3"
                >
                  <div>
                    <h4 className="text-sm font-semibold text-white">{rec.name}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{rec.recommendation_reason}</p>
                    <span className="text-[11px] text-emerald-400 font-mono mt-1 inline-block">
                      Relevance Score: {rec.recommendation_score}
                    </span>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-sm font-bold text-white font-mono block">
                      ₹{rec.price.toFixed(2)}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      Sold: {rec.total_units_sold}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 text-center text-slate-500 text-xs">
              No recommendations available.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
