const API_BASE = '/api/v1';

async function request(url, options = {}) {
  // Always include credentials so browser sends and receives HTTP-Only cookies
  const fetchOptions = {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
    },
  };

  let res = await fetch(url, fetchOptions);

  // If 401 Unauthorized, attempt token refresh via /auth/refresh cookie once
  if (res.status === 401 && !url.includes('/auth/login') && !url.includes('/auth/refresh')) {
    try {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      if (refreshRes.ok) {
        // Retry original request with fresh cookie
        res = await fetch(url, fetchOptions);
      }
    } catch (e) {
      console.warn('Token refresh attempt failed:', e);
    }
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Auth
  login: async (email, password) => {
    return request(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
  },

  registerVendor: async (vendorData) => {
    return request(`${API_BASE}/auth/register-vendor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vendorData),
    });
  },

  logout: async () => {
    return request(`${API_BASE}/auth/logout`, {
      method: 'POST',
    });
  },

  getMe: async () => {
    return request(`${API_BASE}/auth/me`);
  },

  // Admin Controls
  getPendingVendors: async () => {
    return request(`${API_BASE}/admin/pending-vendors`);
  },

  approveVendor: async (vendorId) => {
    return request(`${API_BASE}/admin/vendors/${vendorId}/approve`, {
      method: 'PUT',
    });
  },

  rejectVendor: async (vendorId) => {
    return request(`${API_BASE}/admin/vendors/${vendorId}/reject`, {
      method: 'PUT',
    });
  },

  // Analytics
  getMarketplaceSummary: async () => {
    return request(`${API_BASE}/analytics/marketplace`);
  },

  getVendorAnalytics: async (vendorId) => {
    return request(`${API_BASE}/analytics/vendors/${vendorId}`);
  },

  // Vendors
  getVendors: async () => {
    return request(`${API_BASE}/vendors/`);
  },

  updateVendor: async (vendorId, data) => {
    return request(`${API_BASE}/vendors/${vendorId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  deactivateVendor: async (vendorId) => {
    return request(`${API_BASE}/vendors/${vendorId}`, {
      method: 'DELETE',
    });
  },

  // Products
  getProducts: async (vendorId = null) => {
    const url = vendorId ? `${API_BASE}/products/?vendor_id=${vendorId}` : `${API_BASE}/products/`;
    return request(url);
  },

  createProduct: async (productData) => {
    return request(`${API_BASE}/products/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(productData),
    });
  },

  // Customers & Transactions
  getCustomers: async () => {
    return request(`${API_BASE}/customers/`);
  },

  getTransactions: async (vendorId = null) => {
    const url = vendorId ? `${API_BASE}/transactions/?vendor_id=${vendorId}` : `${API_BASE}/transactions/`;
    return request(url);
  },

  recordTransaction: async (txData) => {
    return request(`${API_BASE}/transactions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(txData),
    });
  }
};

export default api;
