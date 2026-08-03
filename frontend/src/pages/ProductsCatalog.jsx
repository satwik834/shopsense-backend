import React, { useState, useEffect } from 'react';
import { api } from '../api';
import MarketingModal from '../components/MarketingModal';
import { Package, Eye, Mail, Sparkles, Tag, Layers } from 'lucide-react';

export default function ProductsCatalog() {
  const [products, setProducts] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);
  const [selectedProductForMarketing, setSelectedProductForMarketing] = useState(null);

  // Form State
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('100');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Footwear');
  const [sku, setSku] = useState('');
  const [vendorId, setVendorId] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pData, vData] = await Promise.all([
        api.getProducts(),
        api.getVendors()
      ]);
      setProducts(pData);
      setVendors(vData);
      if (vData.length > 0 && !vendorId) {
        setVendorId(vData[0].id.toString());
      }
    } catch (err) {
      console.error('Failed to load products/vendors:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateAiTags = (productName, categoryName) => {
    const baseTags = [categoryName.toLowerCase(), 'quality', 'popular'];
    const words = productName.toLowerCase().split(' ').filter(w => w.length > 3);
    const combined = Array.from(new Set([...words, ...baseTags]));
    return combined.slice(0, 5).join(', ');
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    if (!name || !price || !vendorId) {
      setMessage({ type: 'error', text: 'Product Name, Price, and Vendor are required.' });
      return;
    }

    try {
      setSubmitting(true);
      setMessage(null);

      const generatedTags = generateAiTags(name, category);
      const fullDescription = description
        ? `${description} [AI TAGS: ${generatedTags}]`
        : `Elevate your experience with ${name}. [AI TAGS: ${generatedTags}]`;

      await api.createProduct({
        vendor_id: parseInt(vendorId, 10),
        name,
        description: fullDescription,
        price: parseFloat(price),
        stock_quantity: parseInt(stock, 10) || 0,
        category,
        sku: sku || `SKU-${Date.now().toString().slice(-6)}`,
        image_url: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200&auto=format&fit=crop&q=60'
      });

      setMessage({ type: 'success', text: `Product '${name}' created with AI tags successfully!` });
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

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">Catalog & Inventory Control</h1>
        <p className="text-xs font-mono text-indigo-400 mt-1 uppercase tracking-wider">
          PRODUCT MANAGEMENT MODULE
        </p>
      </div>

      {/* Add Product (with AI Auto-Optimization) Form (Matching Screenshot 78/79) */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-zinc-100">Add Product (with AI Auto-Optimization)</h2>
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
                placeholder="e.g. Sports shoe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                BASE PRICE ($) *
              </label>
              <input
                type="number"
                step="0.01"
                placeholder="20.00"
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
                {vendors.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.store_name || `ID ${v.id}`})
                  </option>
                ))}
              </select>
            </div>

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
                <option value="Footwear">Footwear</option>
                <option value="Apparel">Apparel</option>
                <option value="Accessories">Accessories</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
                SKU (STOCK KEEPING UNIT)
              </label>
              <input
                type="text"
                placeholder="e.g. SHOE-01"
                value={sku}
                onChange={(e) => setSku(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-2">
              BASIC DESCRIPTION
            </label>
            <textarea
              rows={2}
              placeholder="Elevate your experience with our cutting-edge product designed for optimal performance..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting || vendors.length === 0}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition-all disabled:opacity-50"
            >
              {submitting ? 'Generating AI Tags...' : 'Generate AI Tags & Save Product'}
            </button>
          </div>
        </form>
      </div>

      {/* My Catalog Table (Matching Screenshot 79) */}
      <div className="bg-[#12141d] border border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-zinc-100">My Catalog</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">Total Items: {products.length}</span>
        </div>

        {loading ? (
          <div className="py-8 text-center text-xs text-zinc-500 font-mono">Loading product catalog...</div>
        ) : products.length === 0 ? (
          <div className="py-8 text-center text-xs text-zinc-500">No products in catalog yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-zinc-300">
              <thead className="bg-[#090a0f] border-b border-zinc-800 text-[11px] font-mono uppercase text-zinc-400">
                <tr>
                  <th className="px-4 py-3">PRODUCT NAME</th>
                  <th className="px-4 py-3">DESCRIPTION & TAGS</th>
                  <th className="px-4 py-3">CATEGORY</th>
                  <th className="px-4 py-3">PRICE / STOCK</th>
                  <th className="px-4 py-3 text-right">MARKETING</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {products.map((p) => {
                  // Extract tags if present
                  const tagMatch = p.description?.match(/\[AI TAGS: (.*?)\]/);
                  const cleanDesc = p.description ? p.description.replace(/\[AI TAGS: .*?\]/, '').trim() : '';
                  const tagsString = tagMatch ? tagMatch[1] : 'sports, quality, performance';

                  return (
                    <tr key={p.id} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-zinc-800/80 border border-zinc-700/60 overflow-hidden flex-shrink-0 flex items-center justify-center">
                            {p.image_url ? (
                              <img src={p.image_url} alt={p.name} className="w-full h-full object-cover" />
                            ) : (
                              <Package className="w-5 h-5 text-zinc-500" />
                            )}
                          </div>
                          <div>
                            <div className="font-bold text-zinc-100 text-sm">{p.name}</div>
                            <div className="text-[11px] font-mono text-zinc-500">{p.sku || `#PROD-${p.id}`}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 max-w-sm">
                        <p className="text-zinc-300 text-xs line-clamp-2 leading-relaxed">
                          {cleanDesc || 'Elevate your experience with optimal performance and premium quality.'}
                        </p>
                        <div className="mt-2 flex items-center gap-1 flex-wrap">
                          <span className="text-[10px] font-mono text-indigo-400 font-semibold uppercase">AI TAGS:</span>
                          {tagsString.split(',').map((t, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/40 text-indigo-300 text-[10px] font-mono"
                            >
                              {t.trim()}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-800/40 text-emerald-400 text-[11px] font-mono font-medium">
                          VISION: {p.category || 'General'}
                        </span>
                      </td>
                      <td className="px-4 py-4 font-mono">
                        <div className="font-bold text-zinc-100 text-sm">${p.price?.toFixed(2)}</div>
                        <div className="text-[11px] text-zinc-400">Stock: {p.stock_quantity}</div>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <button
                            onClick={() => alert(`Product Details:\nID: ${p.id}\nName: ${p.name}\nPrice: $${p.price}\nStock: ${p.stock_quantity}`)}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition-colors border border-zinc-700/60"
                          >
                            <Eye className="w-3.5 h-3.5 text-zinc-400" />
                            <span>View</span>
                          </button>

                          <button
                            onClick={() => setSelectedProductForMarketing(p)}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 text-xs font-medium transition-colors border border-indigo-500/30"
                          >
                            <Mail className="w-3.5 h-3.5 text-indigo-400" />
                            <span>Email</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Marketing Studio Modal */}
      {selectedProductForMarketing && (
        <MarketingModal
          product={selectedProductForMarketing}
          onClose={() => setSelectedProductForMarketing(null)}
        />
      )}
    </div>
  );
}
