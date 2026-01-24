import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Agent {
  id: string;
  name: string;
  max_requests: number;
  current_requests: string[];
}

export interface Request {
  id: string;
  customer_name: string;
  description: string;
  assigned_agent_id: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
}

export interface Stats {
  total_agents: number;
  total_requests: number;
  active_requests: number;
  completed_requests: number;
  available_capacity: number;
  total_capacity: number;
  utilization: number;
}

export const agentApi = {
  createAgent: (name: string, max_requests: number = 2) =>
    api.post<Agent>('/agents', { name, max_requests }),
  
  getAgents: () => api.get<Agent[]>('/agents'),
  
  getAgent: (id: string) => api.get<Agent>(`/agents/${id}`),
  
  deleteAgent: (id: string) => api.delete(`/agents/${id}`),
};

export const requestApi = {
  createRequest: (customer_name: string, description: string) =>
    api.post<Request>('/requests', { customer_name, description }),
  
  getRequests: () => api.get<Request[]>('/requests'),
  
  getRequest: (id: string) => api.get<Request>(`/requests/${id}`),
  
  completeRequest: (id: string) => api.post<Request>(`/requests/${id}/complete`),
};

export const statsApi = {
  getStats: () => api.get<Stats>('/stats'),
};

export default api;
