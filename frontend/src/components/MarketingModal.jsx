import React, { useState } from 'react';
import { X, Copy, Check, Sparkles } from 'lucide-react';

export default function MarketingModal({ product, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!product) return null;

  const emailSubject = `Special Offer: Discover the all-new ${product.name}!`;
  const emailBody = `Subject: ${emailSubject}

Dear Customer,

We are excited to highlight our top-rated product: ${product.name}!

${product.description || 'Elevate your experience with cutting-edge quality and craftsmanship designed for optimal performance.'}

Price: $${product.price?.toFixed(2)}
Category: ${product.category || 'General'}
SKU: ${product.sku || 'N/A'}

Order now while stock lasts!

Best regards,
ShopSense Partner Store`;

  const handleCopy = () => {
    navigator.clipboard.writeText(emailBody);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#12141e] border border-zinc-800 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-5 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/40">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-zinc-100">AI Marketing Studio</h3>
              <p className="text-xs text-zinc-400">Customized promotional copy for {product.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4">
          <p className="text-xs text-zinc-400">
            Here is a customized promotional email generated specifically for this product. Copy and send it to your customer list!
          </p>

          <div className="bg-[#090a0f] border border-zinc-800 rounded-xl p-4 font-mono text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto">
            {emailBody}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900/40 flex items-center justify-between">
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors shadow-sm"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy Email Copy'}</span>
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-zinc-700 hover:bg-zinc-800 text-zinc-300 font-medium text-xs transition-colors"
          >
            Close Studio
          </button>
        </div>
      </div>
    </div>
  );
}
