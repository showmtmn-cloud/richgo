import axios from 'axios';

// API Base URL - 환경에 따라 변경
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API 함수들
export const apiService = {
  // 헬스 체크
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // 시스템 상태
  getRoot: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // 통계
  getStats: async () => {
    const response = await api.get('/api/stats');
    return response.data;
  },

  // 환율
  getExchangeRates: async () => {
    const response = await api.get('/api/exchange-rates');
    return response.data;
  },

  // 리그
  getLeagues: async () => {
    const response = await api.get('/api/leagues');
    return response.data;
  },

  // 커런시
  getCurrencies: async () => {
    const response = await api.get('/api/currencies');
    return response.data;
  },

  // 베이스 아이템
  getBases: async (limit = 100) => {
    const response = await api.get(`/api/bases?limit=${limit}`);
    return response.data;
  },

  // 모디파이어
  getModifiers: async (limit = 100) => {
    const response = await api.get(`/api/modifiers?limit=${limit}`);
    return response.data;
  },

  // 수익 기회
  getProfitOpportunities: async (limit = 10) => {
    const response = await api.get(`/api/profit-opportunities?limit=${limit}`);
    return response.data;
  },

  // 스케줄러 상태
  getSchedulerStatus: async () => {
    const response = await api.get('/api/scheduler/status');
    return response.data;
  },
};

export default api;
