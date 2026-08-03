import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import VendorsControl from './pages/VendorsControl';
import ProductsCatalog from './pages/ProductsCatalog';
import AnalyticsEngine from './pages/AnalyticsEngine';

export default function App() {
  const [activeTab, setActiveTab] = useState('vendors'); // Default to Vendors Control as shown in screenshots

  return (
    <div className="min-h-screen bg-[#0c0d12] text-zinc-100 flex font-sans antialiased">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 p-8 max-w-7xl mx-auto overflow-y-auto">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'vendors' && <VendorsControl />}
        {activeTab === 'products' && <ProductsCatalog />}
        {activeTab === 'analytics' && <AnalyticsEngine />}
      </main>
    </div>
  );
}
