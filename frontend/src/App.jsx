import React, { useState, useEffect } from 'react';
import api from './api';
import Login from './pages/Login';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import VendorsControl from './pages/VendorsControl';
import ProductsCatalog from './pages/ProductsCatalog';
import AnalyticsEngine from './pages/AnalyticsEngine';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('shopsense_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('vendors');
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Validate session via HTTP-Only cookie on mount
  useEffect(() => {
    async function checkSession() {
      try {
        const userProfile = await api.getMe();
        if (userProfile) {
          const userData = {
            user_id: userProfile.id,
            user_name: userProfile.name,
            email: userProfile.email,
            role: userProfile.role,
            approval_status: userProfile.approval_status
          };
          setCurrentUser(userData);
          localStorage.setItem('shopsense_user', JSON.stringify(userData));
        }
      } catch (err) {
        // Not logged in or session expired
        setCurrentUser(null);
        localStorage.removeItem('shopsense_user');
      } finally {
        setCheckingAuth(false);
      }
    }
    checkSession();
  }, []);

  const handleLoginSuccess = (userData) => {
    setCurrentUser(userData);
    localStorage.setItem('shopsense_user', JSON.stringify(userData));
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.warn('Logout error:', e);
    } finally {
      localStorage.removeItem('shopsense_user');
      setCurrentUser(null);
    }
  };

  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-[#0c0d12] flex items-center justify-center font-mono text-xs text-zinc-500">
        Checking HTTP-Only cookie authentication...
      </div>
    );
  }

  if (!currentUser) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-[#0c0d12] text-zinc-100 flex flex-col font-sans antialiased">
      {/* Top Header */}
      <Header user={currentUser} onLogout={handleLogout} />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Main Content Area */}
        <main className="flex-1 p-8 max-w-7xl mx-auto overflow-y-auto w-full">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'vendors' && <VendorsControl currentUser={currentUser} />}
          {activeTab === 'products' && <ProductsCatalog />}
          {activeTab === 'analytics' && <AnalyticsEngine />}
        </main>
      </div>
    </div>
  );
}
