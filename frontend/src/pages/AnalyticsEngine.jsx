import React, { useState, useEffect } from 'react';
import { api } from '../api';
import MetricCard from '../components/MetricCard';
import { TrendingUp } from 'lucide-react';

export default function AnalyticsEngine({ currentUser }) {
  const isAdmin = currentUser?.role === 'admin';
  const vendorSelfId = currentUser?.user_id?.toString();

  const [vendors, setVendors] = useState([]);
  const [selectedVendorId, setSelectedVendorId] = useState(isAdmin ? '' : vendorSelfId);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAdmin) {
      loadVendors();
    } else if (vendorSelfId) {
      setSelectedVendorId(vendorSelfId);
      loadVendorAnalytics(vendorSelfId);
    }
  }, [currentUser]);

  useEffect(() => {
    if (selectedVendorId) {
      loadVendorAnalytics(selectedVendorId);
    }
  }, [selectedVendorId]);

  const loadVendors = async () => {
    try {
      setLoading(true);
      const data = await api.getVendors();
      setVendors(data);
      if (data.length > 0 && !selectedVendorId) {
        setSelectedVendorId(data[0].id.toString());
      }
    } catch (err) {
      console.error('Failed to load vendors:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadVendorAnalytics = async (vId) => {
    try {
      setLoading(true);
      const data = await api.getVendorAnalytics(vId);
      setAnalytics(data);
    } catch (err) {
      console.error(`Failed to load analytics for vendor ${vId}:`, err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
            {isAdmin ? 'Analytics Engine' : 'My Sales & Performance'}
          </h1>
          <p className="text-xs font-mono text-indigo-400 mt-1 uppercase tracking-wider">
            {isAdmin ? 'BUSINESS INTELLIGENCE & VENDOR DECISIONS' : 'STORE SALES & REVENUE PERFORMANCE'}
          </p>
        </div>

        {/* Vendor Selector Dropdown (Admin Only) */}
        {isAdmin && (
          <div className="flex items-center gap-3">
            <label className="text-xs font-bold uppercase text-zinc-400 font-mono">SELECT VENDOR:</label>
            <select
              value={selectedVendorId}
              onChange={(e) => setSelectedVendorId(e.target.value)}
              className="bg-[#12141d] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-xs text-zinc-100 focus:outline-none font-medium"
            >
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.store_name || `ID ${v.id}`})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading || !analytics ? (
        <div className="py-12 text-center text-xs font-mono text-zinc-500">Loading sales analytics...</div>
      ) : (
        <>
          {/* Vendor Metrics Overview Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
            <MetricCard
              title="TOTAL REVENUE"
              value={`₹${analytics.total_revenue.toFixed(2)}`}
              subtitle="Completed transaction earnings"
              highlightColor="text-emerald-400"
            />
            <MetricCard
              title="TOTAL ORDERS"
              value={analytics.total_orders.toString()}
              subtitle="Completed purchases"
              highlightColor="text-indigo-400"
            />
            <MetricCard
              title="UNITS SOLD"
              value={analytics.total_units_sold.toString()}
              subtitle="Items fulfilled to buyers"
              highlightColor="text-amber-400"
            />
            <MetricCard
              title="AVG ORDER VALUE"
              value={`₹${analytics.average_order_value.toFixed(2)}`}
              subtitle="Revenue per transaction"
              highlightColor="text-sky-400"
            />
          </div>

          {/* Top Selling Products Performance Table */}
          <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-5">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-zinc-100">Product Performance Breakdown</h2>
            </div>

            {analytics.top_selling_products.length === 0 ? (
              <div className="py-8 text-center text-xs text-zinc-500">No product sales recorded yet.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-zinc-300">
                  <thead className="bg-[#090a0f] border-b border-zinc-800 text-[11px] font-mono uppercase text-zinc-400">
                    <tr>
                      <th className="px-4 py-3">PRODUCT NAME</th>
                      <th className="px-4 py-3">PRICE (₹)</th>
                      <th className="px-4 py-3">CURRENT STOCK</th>
                      <th className="px-4 py-3">UNITS SOLD</th>
                      <th className="px-4 py-3 text-right">REVENUE GENERATED</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {analytics.top_selling_products.map((p) => (
                      <tr key={p.id} className="hover:bg-zinc-800/30 transition-colors">
                        <td className="px-4 py-3.5 font-semibold text-zinc-100">{p.name}</td>
                        <td className="px-4 py-3.5 font-mono text-zinc-300">₹{p.price.toFixed(2)}</td>
                        <td className="px-4 py-3.5 font-mono text-zinc-400">{p.stock_quantity} units</td>
                        <td className="px-4 py-3.5 font-mono text-indigo-400 font-bold">{p.units_sold}</td>
                        <td className="px-4 py-3.5 text-right font-mono font-bold text-emerald-400 text-sm">
                          ₹{p.revenue_generated.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
