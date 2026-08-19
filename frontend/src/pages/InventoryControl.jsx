import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp, 
  PlusCircle, 
  RefreshCw, 
  Calendar, 
  ShieldAlert, 
  CheckCircle2,
  XCircle,
  Clock
} from 'lucide-react';

export default function InventoryControl({ currentUser }) {
  const [inventoryData, setInventoryData] = useState(null);
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [threshold, setThreshold] = useState(10);
  
  // Restock Modal State
  const [restockModalOpen, setRestockModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [restockQty, setRestockQty] = useState(25);
  const [restockLoading, setRestockLoading] = useState(false);

  // Forecast Modal State
  const [forecastModalOpen, setForecastModalOpen] = useState(false);
  const [forecastData, setForecastData] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [inv, alerts] = await Promise.all([
        api.getInventoryLevels(threshold),
        api.getLowStockAlerts(threshold)
      ]);
      setInventoryData(inv);
      setLowStockAlerts(alerts);
    } catch (err) {
      console.error('Failed to load inventory data:', err);
      setError(err.message || 'Failed to load inventory intelligence data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [threshold]);

  const handleOpenRestock = (product) => {
    setSelectedProduct(product);
    setRestockQty(25);
    setRestockModalOpen(true);
  };

  const handleRestockSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProduct) return;
    try {
      setRestockLoading(true);
      await api.restockProduct(selectedProduct.product_id || selectedProduct.id, parseInt(restockQty, 10));
      setRestockModalOpen(false);
      await loadData();
    } catch (err) {
      alert(`Restock failed: ${err.message}`);
    } finally {
      setRestockLoading(false);
    }
  };

  const handleOpenForecast = async (product) => {
    setSelectedProduct(product);
    setForecastModalOpen(true);
    try {
      setForecastLoading(true);
      const data = await api.getInventoryForecast(product.product_id || product.id, 30);
      setForecastData(data);
    } catch (err) {
      alert(`Forecast calculation failed: ${err.message}`);
      setForecastModalOpen(false);
    } finally {
      setForecastLoading(false);
    }
  };

  if (loading && !inventoryData) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        <span className="ml-3 text-slate-400 font-medium">Loading inventory intelligence...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Inventory Intelligence & Demand Forecasting</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time stock monitoring, automated low-stock warnings, and predictive demand velocity run-rates.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300">
            <span className="text-slate-400 font-medium">Alert Threshold:</span>
            <select
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="bg-slate-800 text-white rounded px-2 py-0.5 border border-slate-700 outline-none focus:border-indigo-500 font-semibold"
            >
              <option value={5}>&le; 5 units</option>
              <option value={10}>&le; 10 units (Default)</option>
              <option value={15}>&le; 15 units</option>
              <option value={20}>&le; 20 units</option>
            </select>
          </div>
          <button
            onClick={loadData}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg text-sm transition font-medium"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-rose-400 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-sm font-medium">
            <span>Total Tracked Items</span>
            <Package className="w-5 h-5 text-indigo-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-3">
            {inventoryData?.total_products_tracked || 0}
          </p>
          <p className="text-xs text-slate-500 mt-1">Catalog items under active monitoring</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-sm font-medium">
            <span>Healthy Stock</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-3xl font-bold text-emerald-400 mt-3">
            {inventoryData?.in_stock_count || 0}
          </p>
          <p className="text-xs text-slate-500 mt-1">&gt; {threshold} units available in warehouse</p>
        </div>

        <div className="bg-slate-900/90 border border-amber-500/20 rounded-2xl p-5 shadow-sm bg-gradient-to-br from-slate-900 to-amber-950/20">
          <div className="flex items-center justify-between text-amber-300 text-sm font-medium">
            <span>Low-Stock Alerts</span>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <p className="text-3xl font-bold text-amber-400 mt-3">
            {inventoryData?.low_stock_count || 0}
          </p>
          <p className="text-xs text-amber-300/70 mt-1">Breached &le; {threshold} threshold criteria</p>
        </div>

        <div className="bg-slate-900/90 border border-rose-500/20 rounded-2xl p-5 shadow-sm bg-gradient-to-br from-slate-900 to-rose-950/20">
          <div className="flex items-center justify-between text-rose-300 text-sm font-medium">
            <span>Stockouts</span>
            <XCircle className="w-5 h-5 text-rose-400" />
          </div>
          <p className="text-3xl font-bold text-rose-400 mt-3">
            {inventoryData?.out_of_stock_count || 0}
          </p>
          <p className="text-xs text-rose-300/70 mt-1">Zero units remaining - sales blocked</p>
        </div>
      </div>

      {/* Critical Low-Stock Warning Banner */}
      {lowStockAlerts.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-amber-400 flex-shrink-0" />
            <div>
              <h2 className="text-base font-semibold text-amber-300">
                Action Required: {lowStockAlerts.length} Product(s) Below Inventory Safety Stock
              </h2>
              <p className="text-xs text-amber-200/80">
                The following catalog items are near or at exhaustion. Immediate purchase order reordering is recommended.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {lowStockAlerts.map((alert) => (
              <div 
                key={alert.product_id}
                className="bg-slate-900/90 border border-amber-500/30 rounded-xl p-3.5 flex items-center justify-between gap-3 shadow-sm"
              >
                <div>
                  <p className="text-sm font-semibold text-white truncate max-w-[180px]">{alert.product_name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                      alert.current_stock === 0 ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    }`}>
                      {alert.current_stock} Units Left
                    </span>
                    <span className="text-xs text-slate-400">SKU: {alert.sku || 'N/A'}</span>
                  </div>
                </div>
                <button
                  onClick={() => handleOpenRestock(alert)}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition shadow flex items-center gap-1.5 flex-shrink-0"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  Restock
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Stock Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">Warehouse Inventory Matrix</h2>
            <p className="text-xs text-slate-400 mt-0.5">Comprehensive real-time stock levels and estimated velocity</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            Showing {inventoryData?.items?.length || 0} tracked products
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-xs font-semibold tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-5">Product Details</th>
                <th className="py-3.5 px-4">Merchant</th>
                <th className="py-3.5 px-4">Price (₹)</th>
                <th className="py-3.5 px-4">Units in Stock</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Daily Velocity</th>
                <th className="py-3.5 px-4">Stockout Run-Rate</th>
                <th className="py-3.5 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {inventoryData?.items?.map((item) => (
                <tr key={item.product_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-4 px-5">
                    <div className="font-semibold text-white">{item.product_name}</div>
                    <div className="text-xs text-slate-400 font-mono mt-0.5">
                      SKU: {item.sku || 'N/A'} • {item.category || 'General'}
                    </div>
                  </td>
                  <td className="py-4 px-4 text-slate-300 text-xs">
                    {item.vendor_name}
                  </td>
                  <td className="py-4 px-4 text-white font-mono font-semibold">
                    ₹{item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4">
                    <span className="text-base font-bold text-white">{item.current_stock}</span>
                  </td>
                  <td className="py-4 px-4">
                    {item.stock_status === 'IN_STOCK' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        In Stock
                      </span>
                    )}
                    {item.stock_status === 'LOW_STOCK' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        Low Stock
                      </span>
                    )}
                    {item.stock_status === 'OUT_OF_STOCK' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        Out of Stock
                      </span>
                    )}
                  </td>
                  <td className="py-4 px-4 text-slate-300 font-mono text-xs">
                    {item.daily_sales_velocity} units/day
                  </td>
                  <td className="py-4 px-4">
                    {item.estimated_days_remaining !== null ? (
                      <div className="flex items-center gap-1.5 text-xs font-medium">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span className={item.estimated_days_remaining <= 7 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                          ~{item.estimated_days_remaining} Days
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">Adequate</span>
                    )}
                  </td>
                  <td className="py-4 px-5 text-right space-x-2">
                    <button
                      onClick={() => handleOpenForecast(item)}
                      className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium rounded-lg transition inline-flex items-center gap-1"
                    >
                      <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
                      Forecast
                    </button>
                    <button
                      onClick={() => handleOpenRestock(item)}
                      className="px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition inline-flex items-center gap-1 shadow"
                    >
                      <PlusCircle className="w-3.5 h-3.5" />
                      Restock
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Restock Modal */}
      {restockModalOpen && selectedProduct && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <PlusCircle className="w-5 h-5 text-indigo-400" />
                Restock Inventory
              </h3>
              <button 
                onClick={() => setRestockModalOpen(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <div>
              <p className="text-sm text-slate-300 font-semibold">{selectedProduct.product_name}</p>
              <p className="text-xs text-slate-400 mt-0.5">
                Current Stock: <span className="text-white font-bold">{selectedProduct.current_stock}</span> units
              </p>
            </div>

            <form onSubmit={handleRestockSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider mb-1.5">
                  Additional Units to Add
                </label>
                <input
                  type="number"
                  min="1"
                  max="10000"
                  required
                  value={restockQty}
                  onChange={(e) => setRestockQty(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 outline-none font-semibold text-lg"
                />
                <p className="text-xs text-slate-500 mt-1">
                  New resulting stock level will be: <span className="text-emerald-400 font-bold">{Number(selectedProduct.current_stock) + Number(restockQty || 0)}</span> units
                </p>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setRestockModalOpen(false)}
                  className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={restockLoading}
                  className="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition shadow flex items-center justify-center gap-2"
                >
                  {restockLoading ? 'Updating...' : 'Confirm Restock'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Demand Forecast Modal */}
      {forecastModalOpen && selectedProduct && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-400" />
                30-Day Demand Forecast
              </h3>
              <button 
                onClick={() => setForecastModalOpen(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            {forecastLoading ? (
              <div className="py-12 flex flex-col items-center justify-center space-y-3">
                <RefreshCw className="w-7 h-7 text-indigo-400 animate-spin" />
                <p className="text-sm text-slate-400">Computing sales velocity and run-rates...</p>
              </div>
            ) : forecastData ? (
              <div className="space-y-4">
                <div>
                  <h4 className="text-base font-semibold text-white">{forecastData.product_name}</h4>
                  <p className="text-xs text-slate-400">Run-rate demand projection across 30 days</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-xs text-slate-400 font-medium">Daily Velocity</span>
                    <p className="text-lg font-bold text-white mt-1 font-mono">{forecastData.daily_sales_velocity} units/day</p>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-xs text-slate-400 font-medium">Projected 30-Day Demand</span>
                    <p className="text-lg font-bold text-indigo-400 mt-1 font-mono">{forecastData.projected_demand} units</p>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-xs text-slate-400 font-medium">Warehouse Stock</span>
                    <p className="text-lg font-bold text-white mt-1 font-mono">{forecastData.current_stock} units</p>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-xs text-slate-400 font-medium">Reorder Urgency</span>
                    <p className={`text-sm font-bold mt-1 uppercase ${
                      forecastData.reorder_urgency === 'IMMEDIATE' ? 'text-rose-400' : forecastData.reorder_urgency === 'UPCOMING' ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      {forecastData.reorder_urgency}
                    </p>
                  </div>
                </div>

                <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/60 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-300 font-medium">Recommended Reorder Quantity:</span>
                    <span className="text-emerald-400 font-bold font-mono text-base">+{forecastData.recommended_reorder_quantity} Units</span>
                  </div>
                  {forecastData.stockout_predicted ? (
                    <p className="text-xs text-rose-400">
                      Warning: Product is predicted to experience stockout within ~{forecastData.estimated_stockout_days || 0} days at current sales velocity.
                    </p>
                  ) : (
                    <p className="text-xs text-emerald-400">
                      Inventory buffer is healthy to meet the 30-day projected customer demand.
                    </p>
                  )}
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setForecastModalOpen(false);
                      handleOpenRestock(selectedProduct);
                    }}
                    className="w-full px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition shadow flex items-center justify-center gap-2"
                  >
                    <PlusCircle className="w-4 h-4" />
                    Apply Restock Recommendation
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
