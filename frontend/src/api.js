const API_BASE = '/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('shopsense_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function handleResponse(res) {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Auth
  login: async (email, password) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  registerVendor: async (vendorData) => {
    const res = await fetch(`${API_BASE}/auth/register-vendor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vendorData),
    });
    return handleResponse(res);
  },

  getMe: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  // Admin Controls
  getPendingVendors: async () => {
    const res = await fetch(`${API_BASE}/admin/pending-vendors`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  approveVendor: async (vendorId) => {
    const res = await fetch(`${API_BASE}/admin/vendors/${vendorId}/approve`, {
      method: 'PUT',
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  rejectVendor: async (vendorId) => {
    const res = await fetch(`${API_BASE}/admin/vendors/${vendorId}/reject`, {
      method: 'PUT',
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  // Analytics
  getMarketplaceSummary: async () => {
    const res = await fetch(`${API_BASE}/analytics/marketplace`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  getVendorAnalytics: async (vendorId) => {
    const res = await fetch(`${API_BASE}/analytics/vendors/${vendorId}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  // Vendors
  getVendors: async () => {
    const res = await fetch(`${API_BASE}/vendors/`);
    return handleResponse(res);
  },

  updateVendor: async (vendorId, data) => {
    const res = await fetch(`${API_BASE}/vendors/${vendorId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  deactivateVendor: async (vendorId) => {
    const res = await fetch(`${API_BASE}/vendors/${vendorId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return handleResponse(res);
  },

  // Products
  getProducts: async (vendorId = null) => {
    const url = vendorId ? `${API_BASE}/products/?vendor_id=${vendorId}` : `${API_BASE}/products/`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    return handleResponse(res);
  },

  createProduct: async (productData) => {
    const res = await fetch(`${API_BASE}/products/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(productData),
    });
    return handleResponse(res);
  },

  // Customers & Transactions
  getCustomers: async () => {
    const res = await fetch(`${API_BASE}/customers/`);
    return handleResponse(res);
  },

  getTransactions: async (vendorId = null) => {
    const url = vendorId ? `${API_BASE}/transactions/?vendor_id=${vendorId}` : `${API_BASE}/transactions/`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    return handleResponse(res);
  },

  recordTransaction: async (txData) => {
    const res = await fetch(`${API_BASE}/transactions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(txData),
    });
    return handleResponse(res);
  }
};
