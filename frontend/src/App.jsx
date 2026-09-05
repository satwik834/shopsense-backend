import React, { useState, useEffect } from 'react';
import api from './api';
import Login from './pages/Login';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import VendorsControl from './pages/VendorsControl';
import ProductsCatalog from './pages/ProductsCatalog';
import AnalyticsEngine from './pages/AnalyticsEngine';
import InventoryControl from './pages/InventoryControl';
import CustomerInsights from './pages/CustomerInsights';
import Recommendations from './pages/Recommendations';
import BusinessIntelligence from './pages/BusinessIntelligence';
import AIAssistant from './pages/AIAssistant';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('shopsense_user');
    return saved ? JSON.parse(saved) : null;
  });

  const isAdmin = currentUser?.role === 'admin';

  const [activeTab, setActiveTab] = useState(() => {
    return currentUser?.role === 'admin' ? 'vendors' : 'products';
  });

  const [checkingAuth, setCheckingAuth] = useState(true);

  // Enforce tab safety when user role changes
  useEffect(() => {
    if (currentUser) {
      if (currentUser.role === 'vendor' && (activeTab === 'dashboard' || activeTab === 'vendors')) {
        setActiveTab('products');
      }
    }
  }, [currentUser, activeTab]);

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

          // Set appropriate default tab
          if (userData.role === 'vendor' && (activeTab === 'dashboard' || activeTab === 'vendors')) {
            setActiveTab('products');
          }
        }
      } catch (err) {
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
    setActiveTab(userData.role === 'admin' ? 'vendors' : 'products');
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
        Checking session...
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
        {/* Sidebar Navigation */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} currentUser={currentUser} />

        {/* Main Content Area */}
        <main className="flex-1 p-8 max-w-7xl mx-auto overflow-y-auto w-full">
          {isAdmin && activeTab === 'dashboard' && <Dashboard />}
          {isAdmin && activeTab === 'vendors' && <VendorsControl currentUser={currentUser} />}
          {activeTab === 'products' && <ProductsCatalog currentUser={currentUser} />}
          {activeTab === 'inventory' && <InventoryControl currentUser={currentUser} />}
          {activeTab === 'customer_insights' && <CustomerInsights currentUser={currentUser} />}
          {activeTab === 'recommendations' && <Recommendations currentUser={currentUser} />}
          {activeTab === 'bi_reporting' && <BusinessIntelligence currentUser={currentUser} />}
          {activeTab === 'ai_assistant' && <AIAssistant currentUser={currentUser} />}
          {activeTab === 'analytics' && <AnalyticsEngine currentUser={currentUser} />}
        </main>
      </div>
    </div>
  );
}
