import React, { useState } from 'react';
import { api } from '../api';
import { ShieldCheck, Store, Lock, Mail, ArrowRight, UserPlus, LogIn, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [storeName, setStoreName] = useState('');
  const [phone, setPhone] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) return;

    try {
      setLoading(true);
      setMessage(null);
      const res = await api.login(email, password);
      localStorage.setItem('shopsense_token', res.access_token);
      localStorage.setItem('shopsense_user', JSON.stringify(res));
      onLoginSuccess(res);
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Invalid email or password.' });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) return;

    try {
      setLoading(true);
      setMessage(null);
      await api.registerVendor({
        name,
        store_name: storeName || name,
        email,
        password,
        phone,
        description
      });

      setMessage({
        type: 'success',
        text: 'Vendor registration submitted! Your account status is PENDING approval by an admin. You will be able to log in once approved.'
      });

      setMode('login');
      setPassword('');
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Registration failed.' });
    } finally {
      setLoading(false);
    }
  };

  const quickFill = (userEmail, userPassword) => {
    setEmail(userEmail);
    setPassword(userPassword);
    setMode('login');
  };

  return (
    <div className="min-h-screen bg-[#0c0d12] flex items-center justify-center p-4 selection:bg-indigo-500/30">
      <div className="w-full max-w-md bg-[#12141e] border border-zinc-800 rounded-2xl p-8 shadow-2xl space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="h-12 w-12 rounded-xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center font-mono font-bold text-indigo-400 text-2xl mx-auto shadow-inner">
            S
          </div>
          <h1 className="text-2xl font-extrabold text-zinc-100 tracking-tight">ShopSense Analytics</h1>
          <p className="text-xs text-zinc-400">Multi-Vendor E-Commerce Platform</p>
        </div>

        {/* Mode Selector */}
        <div className="grid grid-cols-2 p-1 bg-[#090a0f] border border-zinc-800 rounded-xl">
          <button
            onClick={() => { setMode('login'); setMessage(null); }}
            className={`py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === 'login'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => { setMode('register'); setMessage(null); }}
            className={`py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === 'register'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Vendor Register
          </button>
        </div>

        {/* Status Message */}
        {message && (
          <div className={`p-4 rounded-xl text-xs font-medium border flex items-start gap-2.5 ${
            message.type === 'error'
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
          }`}>
            {message.type === 'error' ? (
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="leading-relaxed">{message.text}</div>
          </div>
        )}

        {/* Form */}
        {mode === 'login' ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5">
                EMAIL ADDRESS
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-zinc-500 absolute left-3.5 top-3" />
                <input
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl pl-10 pr-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1.5">
                PASSWORD
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-zinc-500 absolute left-3.5 top-3" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl pl-10 pr-4 py-2.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-2"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="space-y-3.5">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1">
                BUSINESS LEGAL NAME *
              </label>
              <input
                type="text"
                placeholder="e.g. Apex Dynamics Ltd."
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1">
                STORE NAME
              </label>
              <input
                type="text"
                placeholder="e.g. Apex Tech Store"
                value={storeName}
                onChange={(e) => setStoreName(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1">
                CORPORATE EMAIL *
              </label>
              <input
                type="email"
                placeholder="contact@apex.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 mb-1">
                PASSWORD *
              </label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#090a0f] border border-zinc-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none transition-colors"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-2"
            >
              <span>{loading ? 'Submitting Application...' : 'Register Vendor (Requires Approval)'}</span>
            </button>
          </form>
        )}

        {/* Quick Demo Logins */}
        <div className="pt-4 border-t border-zinc-800/80">
          <div className="text-[11px] font-mono uppercase text-zinc-500 text-center mb-3">
            Quick Demo Accounts
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => quickFill('admin@shopsense.com', 'adminpassword123')}
              className="px-2 py-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-indigo-500 text-[11px] text-zinc-300 font-mono transition-colors text-center"
            >
              Admin
            </button>
            <button
              onClick={() => quickFill('contact@apex.com', 'vendorpass123')}
              className="px-2 py-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-emerald-500 text-[11px] text-emerald-400 font-mono transition-colors text-center"
            >
              Approved Vendor
            </button>
            <button
              onClick={() => quickFill('apply@freshfoods.com', 'vendorpass123')}
              className="px-2 py-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-amber-500 text-[11px] text-amber-400 font-mono transition-colors text-center"
            >
              Pending Vendor
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
