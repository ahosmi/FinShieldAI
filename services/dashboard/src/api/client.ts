import axios from "axios";

const BASE = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE, timeout: 30_000 });

export const fetchStats        = ()        => api.get("/api/alerts/stats").then(r => r.data);
export const fetchLiveAlerts   = (n=20)    => api.get(`/api/alerts/live?limit=${n}`).then(r => r.data);
export const fetchAlerts       = (n=50)    => api.get(`/api/alerts?limit=${n}`).then(r => r.data);
export const fetchMerchants    = (n=20)    => api.get(`/api/merchants?limit=${n}`).then(r => r.data);
export const fetchRiskDist     = ()        => api.get("/api/transactions/risk-distribution").then(r => r.data);
export const fetchFraudByType  = ()        => api.get("/api/transactions/fraud-by-type").then(r => r.data);
export const fetchSuspicious   = (n=10)    => api.get(`/api/alerts/suspicious-users?limit=${n}`).then(r => r.data);

export const askAI = (question: string, context?: object) =>
  api.post("/api/ai/chat", { question, context }).then(r => r.data);

export const explainFraud = (transaction: object, risk_result?: object) =>
  api.post("/api/ai/explain", { transaction, risk_result }).then(r => r.data);
