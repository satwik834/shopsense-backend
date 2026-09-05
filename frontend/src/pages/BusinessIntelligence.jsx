import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  BarChart2, 
  TrendingUp, 
  PieChart, 
  Download, 
  Award, 
  AlertTriangle, 
  CheckCircle, 
  FileSpreadsheet,
  RefreshCw,
  Zap,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

export default function BusinessIntelligence({ currentUser }) {
  const [trendDays, setTrendDays] = useState(30);
  const [salesTrend, setSalesTrend] = useState(null);
  const [categoryDist, setCategoryDist] = useState(null);
  const [benchmarking, setBenchmarking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadBIData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [trendData, catData, benchData] = await Promise.all([
        api.getSalesTrendsChart(trendDays),
        api.getCategoryDistributionChart(),
        api.getVendorBenchmarking()
      ]);
      setSalesTrend(trendData);
      setCategoryDist(catData);
      setBenchmarking(benchData);
    } catch (err) {
      console.error('Failed to load BI data:', err);
      setError(err.message || 'Failed to load Business Intelligence analytics');
    } fontFinally: {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBIData();
  }, [trendDays]);

  const handleDownloadCsv = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading && !salesTrend) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        <span className="ml-3 text-slate-400 font-medium">Loading Business Intelligence analytics...</span>
      </div>
    );
  }

  const points = salesTrend?.trend_points || [];
  const maxRevenue = Math.max(...points.map(p => p.total_revenue), 10);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Business Intelligence & Executive Reporting</h1>
          <p className="text-sm text-slate-400 mt-1">
            Frontend-formatted analytics trendlines, vendor benchmarking metrics, and CSV reporting exports.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={trendDays}
            onChange={(e) => setTrendDays(Number(e.target.value))}
            className="bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-xs font-semibold outline-none focus:border-indigo-500"
          >
            <option value={7}>Last 7 Days</option>
            <option value={14}>Last 14 Days</option>
            <option value={30}>Last 30 Days</option>
          </select>
          <button
            onClick={loadBIData}
            className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Overview Stat Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>PERIOD TOTAL REVENUE</span>
            <TrendingUp className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-2 font-mono">
            ₹{salesTrend?.total_revenue?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) || '0.00'}
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Across {salesTrend?.total_orders || 0} completed transactions
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>UNITS DELIVERED</span>
            <BarChart2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-2 font-mono">
            {salesTrend?.total_units_sold || 0} Units
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Tracked in current {salesTrend?.period || 'period'}
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>STORE BENCHMARK RATING</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 mt-2 font-mono uppercase">
            {benchmarking?.overall_performance_rating?.replace('_', ' ') || 'ACTIVE'}
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Store: <span className="text-white font-semibold">{benchmarking?.store_name}</span>
          </p>
        </div>
      </div>

      {/* Sales Volume & Revenue Trendline Chart (SVG Visualization) */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              Sales & Revenue Trajectory ({salesTrend?.period})
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Daily revenue volume and completed transaction density timeline
            </p>
          </div>
          <span className="text-xs text-indigo-400 font-mono font-semibold bg-indigo-500/10 border border-indigo-500/30 px-3 py-1 rounded-full w-max">
            {points.length} Data Points Plotted
          </span>
        </div>

        {/* Visual Line / Bar Chart Box */}
        <div className="pt-4">
          <div className="h-56 w-full flex items-end gap-1.5 pt-6 pb-2 px-2 bg-slate-950/60 rounded-xl border border-slate-800/80 relative">
            {points.map((p, idx) => {
              const heightPct = Math.max((p.total_revenue / maxRevenue) * 100, 4);
              return (
                <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group relative">
                  {/* Hover Tooltip */}
                  <div className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800 border border-slate-700 text-white text-[10px] p-2 rounded-lg whitespace-nowrap z-20 pointer-events-none shadow-lg">
                    <p className="font-bold">{p.date}</p>
                    <p className="text-indigo-300 font-mono">₹{p.total_revenue.toFixed(2)}</p>
                    <p className="text-slate-400">{p.orders_count} Orders ({p.units_sold} units)</p>
                  </div>

                  {/* Bar Visualizer */}
                  <div 
                    style={{ height: `${heightPct}%` }}
                    className="w-full bg-gradient-to-t from-indigo-600/40 to-indigo-500 rounded-t transition-all duration-300 group-hover:from-indigo-500 group-hover:to-indigo-400"
                  />
                  <span className="text-[9px] text-slate-500 font-mono mt-2 truncate w-full text-center">
                    {p.date.slice(5)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Category Market Share & Benchmarking Side-by-Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Revenue Share */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-800/80 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <PieChart className="w-4 h-4 text-emerald-400" />
              Category Revenue Market Share
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Product catalog category revenue and item volume breakdowns
            </p>
          </div>

          <div className="space-y-3">
            {categoryDist?.categories?.map((cat) => (
              <div key={cat.category} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-200">{cat.category} ({cat.products_count} Items)</span>
                  <span className="text-emerald-400 font-mono">₹{cat.total_revenue.toFixed(2)} ({cat.percentage_of_revenue}%)</span>
                </div>
                <div className="h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div 
                    style={{ width: `${cat.percentage_of_revenue}%` }}
                    className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Vendor Benchmarking Comparison */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="border-b border-slate-800/80 pb-3">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              Vendor Performance Benchmarking
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparative store KPIs vs. marketplace averages
            </p>
          </div>

          <div className="space-y-3">
            {benchmarking?.metrics?.map((m) => (
              <div key={m.metric_name} className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-xl space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">{m.metric_name}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                    m.performance_status === 'ABOVE_AVERAGE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                    m.performance_status === 'BELOW_AVERAGE' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                    'bg-slate-800 text-slate-300 border border-slate-700'
                  }`}>
                    {m.performance_status.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-baseline justify-between text-xs font-mono pt-1">
                  <span className="text-white font-bold">Store: {m.vendor_value} {m.unit}</span>
                  <span className="text-slate-500">Market Avg: {m.marketplace_avg} {m.unit}</span>
                </div>
              </div>
            ))}
          </div>

          {benchmarking?.recommendations?.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80 text-xs text-amber-400/90 font-medium">
              <p className="font-bold text-amber-400">Actionable Benchmark Advice:</p>
              <ul className="list-disc pl-4 space-y-1 mt-1 text-slate-300">
                {benchmarking.recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* CSV Data Export Control Center */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
        <div className="border-b border-slate-800/80 pb-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-indigo-400" />
            1-Click CSV Data Export Control Center
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Download verified raw reporting datasets directly for external Excel / Pandas processing
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3 flex flex-col justify-between">
            <div>
              <h3 className="font-bold text-white text-sm">Sales Transactions CSV</h3>
              <p className="text-xs text-slate-400 mt-1">
                Fulfilled order amounts, customer identifiers, item quantities, and timestamps.
              </p>
            </div>
            <button
              onClick={() => handleDownloadCsv(api.getSalesCsvUrl(), 'shopsense_sales_report.csv')}
              className="w-full flex items-center justify-center gap-2 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Sales CSV
            </button>
          </div>

          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3 flex flex-col justify-between">
            <div>
              <h3 className="font-bold text-white text-sm">Warehouse Inventory CSV</h3>
              <p className="text-xs text-slate-400 mt-1">
                Stock levels, SKU identifiers, daily sales velocity, and run-rate alert status.
              </p>
            </div>
            <button
              onClick={() => handleDownloadCsv(api.getInventoryCsvUrl(), 'shopsense_inventory_report.csv')}
              className="w-full flex items-center justify-center gap-2 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Inventory CSV
            </button>
          </div>

          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3 flex flex-col justify-between">
            <div>
              <h3 className="font-bold text-white text-sm">Customer RFM Profiles CSV</h3>
              <p className="text-xs text-slate-400 mt-1">
                Lifetime customer spend, order frequency counts, AOV, and RFM segment tiers.
              </p>
            </div>
            <button
              onClick={() => handleDownloadCsv(api.getCustomersCsvUrl(), 'shopsense_customer_rfm_report.csv')}
              className="w-full flex items-center justify-center gap-2 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold transition"
            >
              <Download className="w-3.5 h-3.5" />
              Download Customer CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
