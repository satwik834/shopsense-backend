import React, { useState, useEffect } from 'react';
import { api } from '../api';
import MetricCard from '../components/MetricCard';
import { LayoutDashboard, ShoppingCart, DollarSign, Users, Package, CreditCard } from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  // New Sale Form
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [selectedVendorId, setSelectedVendorId] = useState('');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [recording, setRecording] = useState(false);
  const [saleMsg, setSaleMsg] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [sum, vList, cList, pList, tList] = await Promise.all([
        api.getMarketplaceSummary(),
        api.getVendors(),
        api.getCustomers(),
        api.getProducts(),
        api.getTransactions()
      ]);
      setSummary(sum);
      setVendors(vList);
      setCustomers(cList);
      setProducts(pList);
      setTransactions(tList);

      if (cList.length > 0) setSelectedCustomerId(cList[0].id.toString());
      if (vList.length > 0) setSelectedVendorId(vList[0].id.toString());
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter products by selected vendor for sale recorder
  const availableProducts = products.filter(
    (p) => p.vendor_id === parseInt(selectedVendorId, 10)
  );

  useEffect(() => {
    if (availableProducts.length > 0) {
      setSelectedProductId(availableProducts[0].id.toString());
    } else {
      setSelectedProductId('');
    }
  }, [selectedVendorId, products]);

  const handleRecordSale = async (e) => {
    e.preventDefault();
    if (!selectedCustomerId || !selectedVendorId || !selectedProductId) {
      setSaleMsg({ type: 'error', text: 'Please select a customer, vendor, and valid product.' });
      return;
    }

    try {
      setRecording(true);
      setSaleMsg(null);
      await api.recordTransaction({
        customer_id: parseInt(selectedCustomerId, 10),
        vendor_id: parseInt(selectedVendorId, 10),
        product_id: parseInt(selectedProductId, 10),
        quantity: parseInt(quantity, 10) || 1
      });

      setSaleMsg({ type: 'success', text: 'Transaction recorded successfully! Analytics updated.' });
      await loadDashboardData();
    } catch (err) {
      setSaleMsg({ type: 'error', text: err.message || 'Failed to record transaction.' });
    } finally {
      setRecording(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Marketplace Overview</h1>
        <p className="text-xs font-mono text-indigo-400 mt-1 uppercase tracking-wider">
          SHOPSENSE CENTRAL DASHBOARD
        </p>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="MARKETPLACE REVENUE"
          value={`₹${(summary?.total_marketplace_revenue || 0).toFixed(2)}`}
          subtitle="Total platform gross revenue"
          highlightColor="text-emerald-400"
        />
        <MetricCard
          title="TOTAL VENDORS"
          value={(summary?.total_vendors || 0).toString()}
          subtitle="Registered merchant accounts"
          highlightColor="text-indigo-400"
        />
        <MetricCard
          title="REGISTERED CUSTOMERS"
          value={(summary?.total_customers || 0).toString()}
          subtitle="Active buyer profiles"
          highlightColor="text-amber-400"
        />
        <MetricCard
          title="TOTAL TRANSACTIONS"
          value={(summary?.total_transactions || 0).toString()}
          subtitle="Fulfilled platform orders"
          highlightColor="text-sky-400"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Record Live Transaction Panel */}
        <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-5">
            <CreditCard className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-zinc-100">Record Live Sale</h2>
          </div>

          {saleMsg && (
            <div className={`p-3 rounded-lg text-xs font-medium mb-4 border ${
              saleMsg.type === 'error'
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            }`}>
              {saleMsg.text}
            </div>
          )}

          <form onSubmit={handleRecordSale} className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1.5">
                CUSTOMER
              </label>
              <select
                value={selectedCustomerId}
                onChange={(e) => setSelectedCustomerId(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
              >
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>{c.name} ({c.email})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1.5">
                VENDOR
              </label>
              <select
                value={selectedVendorId}
                onChange={(e) => setSelectedVendorId(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
              >
                {vendors.map((v) => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1.5">
                PRODUCT
              </label>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                disabled={availableProducts.length === 0}
              >
                {availableProducts.length === 0 ? (
                  <option value="">No products for this vendor</option>
                ) : (
                  availableProducts.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} (₹{p.price?.toFixed(2)})</option>
                  ))
                )}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1.5">
                QUANTITY
              </label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={recording || availableProducts.length === 0}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50 mt-2"
            >
              {recording ? 'Processing...' : 'Record Transaction'}
            </button>
          </form>
        </div>

        {/* Recent Transactions Stream */}
        <div className="lg:col-span-2 bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
          <h2 className="text-base font-bold text-zinc-100 mb-5">Recent Marketplace Transactions</h2>

          {loading ? (
            <div className="py-8 text-center text-xs font-mono text-zinc-500">Loading transactions...</div>
          ) : transactions.length === 0 ? (
            <div className="py-8 text-center text-xs text-zinc-500">No transactions recorded yet.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-zinc-300">
                <thead className="bg-[#090a0f] border-b border-zinc-800 text-[11px] font-mono uppercase text-zinc-400">
                  <tr>
                    <th className="px-4 py-3">TX ID</th>
                    <th className="px-4 py-3">QTY</th>
                    <th className="px-4 py-3">UNIT PRICE</th>
                    <th className="px-4 py-3">TOTAL AMOUNT</th>
                    <th className="px-4 py-3">STATUS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {transactions.slice(0, 8).map((tx) => (
                    <tr key={tx.id} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="px-4 py-3 font-mono text-zinc-400">#TX-{tx.id.toString().padStart(4, '0')}</td>
                      <td className="px-4 py-3 font-mono text-zinc-300">{tx.quantity}</td>
                      <td className="px-4 py-3 font-mono text-zinc-300">₹{tx.unit_price?.toFixed(2)}</td>
                      <td className="px-4 py-3 font-mono font-bold text-emerald-400">₹{tx.total_amount?.toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {tx.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
