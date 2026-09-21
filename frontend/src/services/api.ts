const API_BASE = "http://localhost:8000/api/v1";

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("portfolioiq_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {}),
  };

  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401 && !endpoint.includes("/auth/login/")) {
    // Session expired
    localStorage.removeItem("portfolioiq_token");
    window.location.reload();
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data?.error?.message || "An unexpected error occurred.";
    const err = new Error(errorMsg) as Error & { details?: any; code?: string };
    err.details = data?.error?.details;
    err.code = data?.error?.code;
    throw err;
  }

  return data as T;
}

export const api = {
  // Auth
  login: (credentials: { email: string; password: string }) =>
    request<{ access: string; refresh: string; user: any }>("/auth/login/", {
      method: "POST",
      body: JSON.stringify(credentials),
    }),

  register: (payload: any) =>
    request<{ user: any }>("/auth/register/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getMe: () => request<any>("/auth/me/"),

  // Portfolios
  getPortfolios: () => request<{ results?: any[]; length?: number }>("/portfolios/"),

  getPortfolioSummary: (id: string) =>
    request<any>(`/portfolios/${id}/summary/`),

  getPortfolioPositions: (id: string) =>
    request<any>(`/portfolios/${id}/positions/`),

  createPortfolio: (payload: { name: string; description?: string; base_currency?: string; cash_balance?: string }) =>
    request<any>("/portfolios/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Transactions
  getTransactions: (params?: { portfolio_id?: string; symbol?: string; type?: string }) => {
    const cleanParams: Record<string, string> = {};
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== "") {
          cleanParams[key] = String(val);
        }
      });
    }
    const query = new URLSearchParams(cleanParams).toString();
    return request<{ results: any[] }>(`/transactions/${query ? `?${query}` : ""}`);
  },

  recordTransaction: (payload: {
    portfolio: string;
    instrument: string;
    transaction_type: string;
    quantity: string;
    price: string;
    fees?: string;
    taxes?: string;
    notes?: string;
    executed_at?: string;
  }) =>
    request<any>("/transactions/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  deleteTransaction: (id: string) =>
    request<{ message: string }>(`/transactions/${id}/`, {
      method: "DELETE",
    }),

  // Analytics
  getPerformanceCurve: (portfolioId: string, timeframe: string = "3M") =>
    request<any>(`/analytics/performance/?portfolio_id=${portfolioId}&timeframe=${timeframe}`),

  getExposure: (portfolioId: string) =>
    request<any>(`/analytics/exposure/?portfolio_id=${portfolioId}`),

  getMonthlyMatrix: () => request<any>("/analytics/monthly-matrix/"),

  // Risk
  getRiskMetrics: (portfolioId: string) =>
    request<any>(`/risk/metrics/?portfolio_id=${portfolioId}`),

  runStressTest: (payload: { portfolio_id: string; market_shock_pct?: number; custom_shocks?: Record<string, number> }) =>
    request<any>("/risk/stress-test/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Options
  getOptionsPositions: (portfolioId: string) =>
    request<any>(`/options/positions/?portfolio_id=${portfolioId}`),

  getPortfolioGreeks: (portfolioId: string) =>
    request<any>(`/options/portfolio-greeks/?portfolio_id=${portfolioId}`),

  // Alerts
  getAlertRules: () => request<{ results: any[] }>("/alerts/rules/"),

  createAlertRule: (payload: { portfolio: string; metric_type: string; comparator: string; threshold_value: string }) =>
    request<any>("/alerts/rules/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getAlertEvents: () => request<{ results: any[] }>("/alerts/events/"),

  acknowledgeAlert: (id: string) =>
    request<any>(`/alerts/events/${id}/ack/`, {
      method: "POST",
    }),

  // Market Data Universe
  getInstruments: (assetClass?: string) => {
    const q = assetClass ? `?asset_class=${assetClass}` : "";
    return request<{ results: any[] }>(`/instruments/${q}`);
  },

  simulateTick: (symbol?: string) =>
    request<any>("/market-data/simulate-tick/", {
      method: "POST",
      body: JSON.stringify({ symbol }),
    }),
};
