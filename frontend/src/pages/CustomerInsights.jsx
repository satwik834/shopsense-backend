import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Users, 
  Award, 
  TrendingUp, 
  UserCheck, 
  UserX, 
  RefreshCw, 
  Filter, 
  CreditCard,
  Calendar,
  Search
} from 'lucide-react';

export default function CustomerInsights() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [activeSegment, setActiveSegment] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [sumData, custList] = await Promise.all([
        api.getCustomerSegments(),
        api.getSegmentedCustomers(activeSegment)
      ]);
      setSummary(sumData);
      setCustomers(custList);
    } catch (err) {
      console.error('Failed to load customer analytics:', err);
      setError(err.message || 'Failed to load customer segmentation analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeSegment]);

  const filteredCustomers = customers.filter(c => 
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getSegmentBadge = (segment) => {
    switch (segment) {
      case 'VIP':
        return 'bg-purple-500/10 text-purple-400 border border-purple-500/30';
      case 'REGULAR':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30';
      case 'NEW':
        return 'bg-blue-500/10 text-blue-400 border border-blue-500/30';
      case 'INACTIVE':
      default:
        return 'bg-slate-700/30 text-slate-400 border border-slate-700/50';
    }
  };

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        <span className="ml-3 text-slate-400 font-medium">Loading customer segmentation insights...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Customer Analytics & RFM Segmentation</h1>
          <p className="text-sm text-slate-400 mt-1">
            SQL-based behavioral customer clustering, lifetime value (LTV) calculation, and order frequency distribution.
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg text-sm transition font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Insights
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Segment Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {summary?.segments?.map((seg) => (
          <div 
            key={seg.segment}
            onClick={() => setActiveSegment(activeSegment === seg.segment ? null : seg.segment)}
            className={`bg-slate-900/90 border rounded-2xl p-5 shadow-sm cursor-pointer transition ${
              activeSegment === seg.segment 
                ? 'border-indigo-500 ring-2 ring-indigo-500/30 bg-slate-800/80' 
                : 'border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between text-slate-400 text-sm font-medium">
              <span className="font-semibold">{seg.segment} Segment</span>
              {seg.segment === 'VIP' && <Award className="w-5 h-5 text-purple-400" />}
              {seg.segment === 'REGULAR' && <UserCheck className="w-5 h-5 text-emerald-400" />}
              {seg.segment === 'NEW' && <TrendingUp className="w-5 h-5 text-blue-400" />}
              {seg.segment === 'INACTIVE' && <UserX className="w-5 h-5 text-slate-500" />}
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <p className="text-3xl font-bold text-white">{seg.customer_count}</p>
              <span className="text-xs font-semibold text-slate-400 font-mono">
                {seg.percentage_of_customers}% of Total
              </span>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-400">Total Spend:</span>
              <span className="font-bold text-white font-mono">
                ₹{seg.total_revenue_contributed.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Segment Breakdown Progress Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-white">Marketplace Revenue Contribution by Customer Tier</h2>
          <span className="text-xs text-slate-400 font-mono">
            Total Revenue: ₹{summary?.total_customer_revenue?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) || '0.00'}
          </span>
        </div>
        
        <div className="h-4 bg-slate-950 rounded-full overflow-hidden flex border border-slate-800">
          {summary?.segments?.map((seg) => (
            <div
              key={seg.segment}
              style={{ width: `${seg.percentage_of_revenue}%` }}
              title={`${seg.segment}: ${seg.percentage_of_revenue}% revenue`}
              className={`h-full transition-all duration-500 ${
                seg.segment === 'VIP' ? 'bg-purple-500' :
                seg.segment === 'REGULAR' ? 'bg-emerald-500' :
                seg.segment === 'NEW' ? 'bg-blue-500' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>

        <div className="flex flex-wrap gap-4 pt-1 text-xs text-slate-400">
          {summary?.segments?.map((seg) => (
            <div key={seg.segment} className="flex items-center gap-1.5 font-medium">
              <span className={`w-2.5 h-2.5 rounded-full ${
                seg.segment === 'VIP' ? 'bg-purple-500' :
                seg.segment === 'REGULAR' ? 'bg-emerald-500' :
                seg.segment === 'NEW' ? 'bg-blue-500' : 'bg-slate-700'
              }`} />
              <span className="text-slate-300 font-semibold">{seg.segment}:</span>
              <span>{seg.percentage_of_revenue}% (₹{seg.total_revenue_contributed.toLocaleString('en-IN', { minimumFractionDigits: 2 })})</span>
            </div>
          ))}
        </div>
      </div>

      {/* Customer Spend Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white">Customer Lifetime Value (LTV) Profiles</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {activeSegment ? `Showing ${activeSegment} segment customers` : 'Showing all customer spend tiers'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-white rounded-xl pl-9 pr-4 py-1.5 text-xs outline-none focus:border-indigo-500 w-56 font-medium"
              />
            </div>
            {activeSegment && (
              <button
                onClick={() => setActiveSegment(null)}
                className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition"
              >
                Clear Filter
              </button>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-xs font-semibold tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-5">Customer Identity</th>
                <th className="py-3.5 px-4">Segment Tier</th>
                <th className="py-3.5 px-4">Total Orders</th>
                <th className="py-3.5 px-4">Lifetime Spend (₹)</th>
                <th className="py-3.5 px-4">Average Order Value</th>
                <th className="py-3.5 px-4">Last Activity</th>
                <th className="py-3.5 px-5">Profile Remarks</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {filteredCustomers.map((cust) => (
                <tr key={cust.customer_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-4 px-5">
                    <div className="font-semibold text-white">{cust.name}</div>
                    <div className="text-xs text-slate-400 font-mono mt-0.5">{cust.email}</div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${getSegmentBadge(cust.segment)}`}>
                      {cust.segment}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-white font-mono font-bold">
                    {cust.total_orders}
                  </td>
                  <td className="py-4 px-4 text-white font-mono font-bold">
                    ₹{cust.total_spent.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4 text-slate-300 font-mono text-xs">
                    ₹{cust.average_order_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4 text-xs text-slate-400">
                    {cust.last_purchase_date ? new Date(cust.last_purchase_date).toLocaleDateString() : 'No Orders'}
                  </td>
                  <td className="py-4 px-5 text-xs text-slate-400 max-w-xs truncate">
                    {cust.segment_description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
