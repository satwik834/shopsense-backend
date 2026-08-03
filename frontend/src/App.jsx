import React, { useState, useEffect } from 'react';
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

  const handleLoginSuccess = (userData) => {
    setCurrentUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('shopsense_token');
    localStorage.removeItem('shopsense_user');
    setCurrentUser(null);
  };

  if (!currentUser) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-[#0c0d12] text-zinc-100 flex flex-col font-sans antialiased">
      {/* Top Header with User Info & Logout */}
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
