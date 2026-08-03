import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Package, Plus, Trash2, Edit3, Save, X, AlertCircle } from 'lucide-react';

export default function ProductsCatalog({ currentUser }) {
  const [products, setProducts] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [selectedVendorFilter, setSelectedVendorFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  // Stock Edit Modal State
  const [editingProduct, setEditingProduct] = useState(null);
  const [editStock, setEditStock] = useState('');
  const [editPrice, setEditPrice] = useState('');
  const [updating, setUpdating] = useState(false);

  // Add Product Form State
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('100');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Electronics');
  const [sku, setSku] = useState('');
  const [vendorId, setVendorId] = useState('');

  const isAdmin = currentUser?.role === 'admin';

  useEffect(() => {
    loadData();
  }, [selectedVendorFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      if (isAdmin) {
        const [pData, vData] = await Promise.all([
          api.getProducts(selectedVendorFilter || null),
          api.getVendors()
        ]);
        setProducts(pData);
        setVendors(vData);
      } else {
        // Vendors only fetch their own isolated products
        const pData = await api.getProducts();
        setProducts(pData);
      }
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    if (!name || !price) {
      setMessage({ type: 'error', text: 'Product Name and Price are required.' });
      return;
    }

    try {
      setSubmitting(true);
      setMessage(null);

      const payload = {
        vendor_id: isAdmin ? (parseInt(vendorId, 10) || currentUser.user_id) : currentUser.user_id,
        name,
        description: description || null,
        price: parseFloat(price),
        stock_quantity: parseInt(stock, 10) || 0,
        category: category || 'General',
        sku: sku || `SKU-${Date.now().toString().slice(-6)}`
      };

      await api.createProduct(payload);

      setMessage({ type: 'success', text: `Product '${name}' added to catalog!` });
      setName('');
      setPrice('');
      setStock('100');
      setDescription('');
      setSku('');
      await loadData();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to create product.' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    if (!editingProduct) return;

    try {
      setUpdating(true);
      await api.updateProduct(editingProduct.id, {
        stock_quantity: parseInt(editStock, 10),
        price: parseFloat(editPrice)
      });
      setEditingProduct(null);
      await loadData();
    } catch (err) {
      alert(`Failed to update product: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteProduct = async (productId, productName) => {
    if (!window.confirm(`Are you sure you want to delete product '${productName}'?`)) return;

    try {
      await api.deleteProduct(productId);
      await loadData();
    } catch (err) {
      alert(`Failed to delete product: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Product Catalog</h1>
          <p className="text-xs font-mono text-indigo-400 mt-1 uppercase tracking-wider">
            {isAdmin ? 'ALL MARKETPLACE PRODUCTS' : 'MY STORE CATALOG & INVENTORY'}
          </p>
        </div>

        {/* Admin Filter Dropdown */}
        {isAdmin && vendors.length > 0 && (
          <div className="flex items-center gap-3">
            <label className="text-xs font-bold uppercase text-zinc-400 font-mono">FILTER VENDOR:</label>
            <select
              value={selectedVendorFilter}
              onChange={(e) => setSelectedVendorFilter(e.target.value)}
              className="bg-[#12141d] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2 text-xs text-zinc-100 focus:outline-none font-medium"
            >
              <option value="">All Vendors</option>
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Add Product Form */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <Plus className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-zinc-100">Add New Product</h2>
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

        <form onSubmit={handleCreateProduct} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                PRODUCT NAME *
              </label>
              <input
                type="text"
                placeholder="e.g. Wireless Headphones"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                PRICE ($) *
              </label>
              <input
                type="number"
                step="0.01"
                placeholder="99.99"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                STOCK QUANTITY
              </label>
              <input
                type="number"
                placeholder="100"
                value={stock}
                onChange={(e) => setStock(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
              />
            </div>

            {isAdmin && (
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                  ASSIGN VENDOR *
                </label>
                <select
                  value={vendorId}
                  onChange={(e) => setVendorId(e.target.value)}
                  className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 focus:outline-none transition-colors"
                  required
                >
                  <option value="">Select Vendor</option>
                  {vendors.map((v) => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                CATEGORY
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 focus:outline-none transition-colors"
              >
                <option value="Electronics">Electronics</option>
                <option value="Apparel">Apparel</option>
                <option value="Footwear">Footwear</option>
                <option value="Home & Kitchen">Home & Kitchen</option>
                <option value="Books">Books</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                SKU (STOCK KEEPING UNIT)
              </label>
              <input
                type="text"
                placeholder="e.g. APX-WHP-01"
                value={sku}
                onChange={(e) => setSku(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
              DESCRIPTION
            </label>
            <textarea
              rows={2}
              placeholder="High quality consumer product..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition-all disabled:opacity-50"
            >
              {submitting ? 'Adding Product...' : 'Add Product'}
            </button>
          </div>
        </form>
      </div>

      {/* Product Catalog Table */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-zinc-100">Products List</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">Total Items: {products.length}</span>
        </div>

        {loading ? (
          <div className="py-8 text-center text-xs text-zinc-500 font-mono">Loading product catalog...</div>
        ) : products.length === 0 ? (
          <div className="py-8 text-center text-xs text-zinc-500">No products found in this store catalog.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-zinc-300">
              <thead className="bg-[#090a0f] border-b border-zinc-800 text-[11px] font-mono uppercase text-zinc-400">
                <tr>
                  <th className="px-4 py-3">PRODUCT</th>
                  <th className="px-4 py-3">DESCRIPTION</th>
                  <th className="px-4 py-3">CATEGORY</th>
                  <th className="px-4 py-3">PRICE</th>
                  <th className="px-4 py-3">STOCK QUANTITY</th>
                  <th className="px-4 py-3 text-right">ACTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {products.map((p) => (
                  <tr key={p.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-4">
                      <div className="font-bold text-zinc-100 text-sm">{p.name}</div>
                      <div className="text-[11px] font-mono text-zinc-500">{p.sku || `#PROD-${p.id}`}</div>
                    </td>
                    <td className="px-4 py-4 max-w-xs">
                      <p className="text-zinc-300 text-xs line-clamp-2">{p.description || 'No description provided.'}</p>
                    </td>
                    <td className="px-4 py-4 font-mono">
                      <span className="px-2.5 py-1 rounded bg-zinc-800 border border-zinc-700 text-zinc-300 text-[11px]">
                        {p.category || 'General'}
                      </span>
                    </td>
                    <td className="px-4 py-4 font-mono font-bold text-zinc-100 text-sm">
                      ${p.price?.toFixed(2)}
                    </td>
                    <td className="px-4 py-4 font-mono">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                        p.stock_quantity > 10
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {p.stock_quantity} units
                      </span>
                    </td>
                    <td className="px-4 py-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => {
                            setEditingProduct(p);
                            setEditStock(p.stock_quantity.toString());
                            setEditPrice(p.price.toString());
                          }}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors border border-zinc-700/60"
                        >
                          <Edit3 className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Edit Stock</span>
                        </button>

                        <button
                          onClick={() => handleDeleteProduct(p.id, p.name)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-rose-500/30 text-rose-400 hover:bg-rose-500/10 text-xs font-medium transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span>Delete</span>
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

      {/* Edit Stock Modal */}
      {editingProduct && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#12141e] border border-zinc-800 rounded-2xl w-full max-w-sm p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h3 className="font-bold text-sm text-zinc-100">Update Stock & Price</h3>
              <button onClick={() => setEditingProduct(null)} className="text-zinc-400 hover:text-zinc-100">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleUpdateProduct} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1">PRODUCT</label>
                <div className="text-xs font-semibold text-zinc-200">{editingProduct.name}</div>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1">PRICE ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={editPrice}
                  onChange={(e) => setEditPrice(e.target.value)}
                  className="w-full bg-[#090a0f] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-100 font-mono focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-zinc-400 mb-1">STOCK QUANTITY</label>
                <input
                  type="number"
                  value={editStock}
                  onChange={(e) => setEditStock(e.target.value)}
                  className="w-full bg-[#090a0f] border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-100 font-mono focus:outline-none"
                  required
                />
              </div>

              <div className="pt-2 flex items-center gap-2">
                <button
                  type="submit"
                  disabled={updating}
                  className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-sm transition-colors"
                >
                  {updating ? 'Saving...' : 'Save Updates'}
                </button>

                <button
                  type="button"
                  onClick={() => setEditingProduct(null)}
                  className="px-4 py-2 border border-zinc-800 text-zinc-400 text-xs rounded-xl hover:bg-zinc-800"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
