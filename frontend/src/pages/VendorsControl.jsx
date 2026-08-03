import React, { useState, useEffect } from 'react';
import { api } from '../api';
import MetricCard from '../components/MetricCard';
import { Building2, Mail, Phone, UserCheck, UserX, Clock, CheckCircle2, XCircle } from 'lucide-react';

export default function VendorsControl({ currentUser }) {
  const [vendors, setVendors] = useState([]);
  const [pendingVendors, setPendingVendors] = useState([]);
  const [marketplaceSummary, setMarketplaceSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState(null);

  const isAdmin = currentUser?.role === 'admin';

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

      if (isAdmin) {
        const pData = await api.getPendingVendors();
        setPendingVendors(pData);
      }
    } catch (err) {
      console.error('Failed to load vendor data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (vendorId) => {
    try {
      setActionMsg(null);
      await api.approveVendor(vendorId);
      setActionMsg({ type: 'success', text: `Vendor #${vendorId} has been APPROVED!` });
      await loadData();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Failed to approve vendor.' });
    }
  };

  const handleReject = async (vendorId) => {
    try {
      setActionMsg(null);
      await api.rejectVendor(vendorId);
      setActionMsg({ type: 'success', text: `Vendor #${vendorId} application was REJECTED.` });
      await loadData();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.message || 'Failed to reject vendor.' });
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

  const activeVendorCount = vendors.filter(v => v.approval_status === 'approved' && v.is_active).length;
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

      {/* Action Notification Message */}
      {actionMsg && (
        <div className={`p-4 rounded-xl text-xs font-medium border ${
          actionMsg.type === 'error'
            ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}>
          {actionMsg.text}
        </div>
      )}

      {/* Top Metrics Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <MetricCard
          title="TOTAL REVENUE (GMV)"
          value={`₹${totalRevenueGMV.toFixed(2)}`}
          subtitle="Aggregate marketplace volume"
          highlightColor="text-emerald-400"
        />
        <MetricCard
          title="ACTIVE VENDORS"
          value={activeVendorCount.toString()}
          subtitle={`Pending Applications: ${pendingVendors.length}`}
          highlightColor="text-indigo-400"
        />
        <MetricCard
          title="CATALOG PRODUCTS"
          value={catalogProductsCount.toString()}
          subtitle="Active items across marketplace"
          highlightColor="text-sky-400"
        />
      </div>

      {/* ADMIN CONTROL: Pending Approvals Section */}
      {isAdmin && (
        <div className="bg-[#12141d] border border-amber-500/30 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-400" />
              <h2 className="text-base font-bold text-zinc-100">Pending Vendor Applications</h2>
            </div>
            <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {pendingVendors.length} Waiting Approval
            </span>
          </div>

          {pendingVendors.length === 0 ? (
            <div className="py-6 text-center text-xs text-zinc-400">
              No pending vendor applications waiting for review.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-zinc-300">
                <thead className="bg-[#090a0f] border-b border-zinc-800 text-[11px] font-mono uppercase text-zinc-400">
                  <tr>
                    <th className="px-4 py-3">ID</th>
                    <th className="px-4 py-3">BUSINESS & STORE</th>
                    <th className="px-4 py-3">EMAIL</th>
                    <th className="px-4 py-3">APPLICATION STATUS</th>
                    <th className="px-4 py-3 text-right">ADMIN ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {pendingVendors.map((v) => (
                    <tr key={v.id} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="px-4 py-3.5 font-mono text-zinc-400">#VD-{v.id.toString().padStart(4, '0')}</td>
                      <td className="px-4 py-3.5">
                        <div className="font-bold text-zinc-100">{v.name}</div>
                        <div className="text-[11px] text-zinc-400">{v.store_name || 'N/A'}</div>
                      </td>
                      <td className="px-4 py-3.5 font-mono text-zinc-300">{v.email}</td>
                      <td className="px-4 py-3.5">
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          PENDING APPROVAL
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <div className="inline-flex items-center gap-2">
                          <button
                            onClick={() => handleApprove(v.id)}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs transition-colors shadow-sm"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve</span>
                          </button>

                          <button
                            onClick={() => handleReject(v.id)}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-rose-500/40 text-rose-400 hover:bg-rose-500/10 font-medium text-xs transition-colors"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            <span>Reject</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Marketplace Vendor Directory Table */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-zinc-100 mb-5">Marketplace Vendor Directory</h2>

        {loading ? (
          <div className="py-8 text-center text-xs text-zinc-500 font-mono">Loading directory...</div>
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
                  <th className="px-4 py-3">APPROVAL STATUS</th>
                  {isAdmin && <th className="px-4 py-3 text-right">ACTIONS</th>}
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
                    </td>
                    <td className="px-4 py-3">
                      {v.approval_status === 'approved' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          Approved
                        </span>
                      ) : v.approval_status === 'pending' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                          Pending Approval
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          Rejected
                        </span>
                      )}
                    </td>
                    {isAdmin && (
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleToggleStatus(v)}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
                            v.is_active
                              ? 'border-rose-500/30 text-rose-400 hover:bg-rose-500/10'
                              : 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10'
                          }`}
                        >
                          {v.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    )}
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
