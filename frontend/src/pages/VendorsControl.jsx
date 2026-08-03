import React, { useState, useEffect } from 'react';
import { api } from '../api';
import MetricCard from '../components/MetricCard';
import { Building2, Mail, Phone, ShieldCheck, UserCheck, UserX } from 'lucide-react';

export default function VendorsControl({ onVendorAdded }) {
  const [vendors, setVendors] = useState([]);
  const [marketplaceSummary, setMarketplaceSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  // Vendor Form State
  const [name, setName] = useState('');
  const [storeName, setStoreName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [commissionTier, setCommissionTier] = useState('Standard 15%');
  const [taxVerification, setTaxVerification] = useState('Auto-Verify via Stripe Identity');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [vData, mData] = await Promise.all([
        api.getVendors(),
        api.getMarketplaceSummary()
      ]);
      setVendors(vData);
      setMarketplaceSummary(mData);
    } catch (err) {
      console.error('Failed to load vendor data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateVendor = async (e) => {
    e.preventDefault();
    if (!name || !email) {
      setMessage({ type: 'error', text: 'Business Name and Email are required.' });
      return;
    }

    try {
      setSubmitting(true);
      setMessage(null);
      await api.createVendor({
        name,
        store_name: storeName || name,
        email,
        phone: phone || null,
        description: `Commission: ${commissionTier} | Tax: ${taxVerification}`
      });

      setMessage({ type: 'success', text: `Vendor profile '${name}' initialized successfully!` });
      setName('');
      setStoreName('');
      setEmail('');
      setPhone('');
      await loadData();
      if (onVendorAdded) onVendorAdded();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to initialize vendor.' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleStatus = async (vendor) => {
    try {
      if (vendor.is_active) {
        await api.deactivateVendor(vendor.id);
      } else {
        await api.updateVendor(vendor.id, { is_active: true });
      }
      await loadData();
    } catch (err) {
      alert(`Error updating vendor status: ${err.message}`);
    }
  };

  const activeVendorCount = vendors.filter(v => v.is_active).length;
  const totalRevenueGMV = marketplaceSummary?.total_marketplace_revenue || 0.0;
  const catalogProductsCount = marketplaceSummary?.total_products || 0;

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Vendor Management</h1>
        <p className="text-xs font-mono text-indigo-400 mt-1 uppercase tracking-wider">
          FOUNDATION MODULE • SECURE ACCESS
        </p>
      </div>

      {/* Top Metrics Cards Row (Matching Screenshot 74/75/76) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <MetricCard
          title="TOTAL REVENUE (GMV)"
          value={`$${totalRevenueGMV.toFixed(2)}`}
          subtitle="Aggregate gross merchandise volume"
          highlightColor="text-emerald-400"
        />
        <MetricCard
          title="ACTIVE VENDORS"
          value={activeVendorCount.toString()}
          subtitle={`Total Registered: ${vendors.length}`}
          highlightColor="text-indigo-400"
        />
        <MetricCard
          title="CATALOG PRODUCTS"
          value={catalogProductsCount.toString()}
          subtitle="Active items across marketplace"
          highlightColor="text-sky-400"
        />
      </div>

      {/* Register New Vendor Form (Matching Screenshot 73 & 77) */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <Building2 className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-zinc-100">Register New Vendor (Advanced Options)</h2>
        </div>

        {message && (
          <div className={`p-3 rounded-lg text-xs font-medium mb-5 border ${
            message.type === 'error'
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
          }`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleCreateVendor} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                BUSINESS LEGAL NAME *
              </label>
              <input
                type="text"
                placeholder="e.g. Apex Dynamics Ltd."
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                CORPORATE EMAIL *
              </label>
              <input
                type="email"
                placeholder="contact@apex.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                STORE / DISPLAY NAME
              </label>
              <input
                type="text"
                placeholder="e.g. Apex Store"
                value={storeName}
                onChange={(e) => setStoreName(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                COMMISSION RATE TIER
              </label>
              <select
                value={commissionTier}
                onChange={(e) => setCommissionTier(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 focus:outline-none transition-colors"
              >
                <option value="Standard 15%">Standard 15%</option>
                <option value="Premium 10%">Premium 10%</option>
                <option value="Enterprise 8%">Enterprise 8%</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                TAX VERIFICATION API
              </label>
              <select
                value={taxVerification}
                onChange={(e) => setTaxVerification(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 focus:outline-none transition-colors"
              >
                <option value="Auto-Verify via Stripe Identity">Auto-Verify via Stripe Identity</option>
                <option value="Manual Document Review">Manual Document Review</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                CONTACT PHONE
              </label>
              <input
                type="text"
                placeholder="e.g. +1 555-0192"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition-all disabled:opacity-50"
            >
              {submitting ? 'Initializing...' : 'Initialize Vendor Profile'}
            </button>
          </div>
        </form>
      </div>

      {/* Marketplace Vendor Directory Table (Matching Screenshot 73 & 77) */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-zinc-100 mb-5">Marketplace Vendor Directory</h2>

        {loading ? (
          <div className="py-8 text-center text-xs text-zinc-500 font-mono">Loading vendor directory...</div>
        ) : vendors.length === 0 ? (
          <div className="py-8 text-center text-xs text-zinc-500">No vendors registered yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-zinc-300">
              <thead className="bg-[#090a0f] border-b border-zinc-800 text-[11px] font-mono uppercase text-zinc-400">
                <tr>
                  <th className="px-4 py-3">UUID / ID</th>
                  <th className="px-4 py-3">VENDOR IDENTITY</th>
                  <th className="px-4 py-3">COMMUNICATIONS</th>
                  <th className="px-4 py-3">STATUS MATRIX</th>
                  <th className="px-4 py-3 text-right">ACTIONS (CHANGE STATUS)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {vendors.map((v) => (
                  <tr key={v.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-zinc-400">#VD-{v.id.toString().padStart(4, '0')}</td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-zinc-100">{v.name}</div>
                      {v.store_name && <div className="text-[11px] text-zinc-400">{v.store_name}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5 text-zinc-300">
                        <Mail className="w-3.5 h-3.5 text-zinc-500" />
                        <span>{v.email}</span>
                      </div>
                      {v.phone && (
                        <div className="flex items-center gap-1.5 text-zinc-500 text-[11px] mt-0.5">
                          <Phone className="w-3 h-3" />
                          <span>{v.phone}</span>
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {v.is_active ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                          Deactivated
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleToggleStatus(v)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
                          v.is_active
                            ? 'border-rose-500/30 text-rose-400 hover:bg-rose-500/10'
                            : 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10'
                        }`}
                      >
                        {v.is_active ? (
                          <>
                            <UserX className="w-3.5 h-3.5" />
                            <span>Deactivate</span>
                          </>
                        ) : (
                          <>
                            <UserCheck className="w-3.5 h-3.5" />
                            <span>Activate</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
