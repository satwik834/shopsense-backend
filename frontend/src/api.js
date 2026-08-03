const API_BASE = '/api/v1';

async function handleResponse(res) {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Health Check
  getHealth: async () => {
    const res = await fetch('/health');
    return handleResponse(res);
  },

  // Marketplace & Vendor Analytics
  getMarketplaceSummary: async () => {
    const res = await fetch(`${API_BASE}/analytics/marketplace`);
    return handleResponse(res);
  },

  getVendorAnalytics: async (vendorId) => {
    const res = await fetch(`${API_BASE}/analytics/vendors/${vendorId}`);
    return handleResponse(res);
  },

  // Vendors
  getVendors: async () => {
    const res = await fetch(`${API_BASE}/vendors/`);
    return handleResponse(res);
  },

  createVendor: async (vendorData) => {
    const res = await fetch(`${API_BASE}/vendors/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vendorData),
    });
    return handleResponse(res);
  },

  updateVendor: async (vendorId, data) => {
    const res = await fetch(`${API_BASE}/vendors/${vendorId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  deactivateVendor: async (vendorId) => {
    const res = await fetch(`${API_BASE}/vendors/${vendorId}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Products
  getProducts: async (vendorId = null) => {
    const url = vendorId ? `${API_BASE}/products/?vendor_id=${vendorId}` : `${API_BASE}/products/`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  createProduct: async (productData) => {
    const res = await fetch(`${API_BASE}/products/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(productData),
    });
    return handleResponse(res);
  },

  // Customers
  getCustomers: async () => {
    const res = await fetch(`${API_BASE}/customers/`);
    return handleResponse(res);
  },

  createCustomer: async (customerData) => {
    const res = await fetch(`${API_BASE}/customers/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customerData),
    });
    return handleResponse(res);
  },

  // Transactions
  getTransactions: async (vendorId = null) => {
    const url = vendorId ? `${API_BASE}/transactions/?vendor_id=${vendorId}` : `${API_BASE}/transactions/`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  recordTransaction: async (txData) => {
    const res = await fetch(`${API_BASE}/transactions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(txData),
    });
    return handleResponse(res);
  }
};
