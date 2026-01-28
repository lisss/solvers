import React, { useState, useEffect, useRef } from 'react';
import { agentApi, requestApi, statsApi, Agent, Request, Stats } from './api';
import './index.css';

const DEFAULT_MAX_REQUESTS = 2

const App: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [requests, setRequests] = useState<Request[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const lastAgentsJson = useRef<string>('');
  const lastRequestsJson = useRef<string>('');
  const lastStatsJson = useRef<string>('');

  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentMaxRequests, setNewAgentMaxRequests] = useState(DEFAULT_MAX_REQUESTS);

  const [newRequestCustomer, setNewRequestCustomer] = useState('');
  const [newRequestDescription, setNewRequestDescription] = useState('');

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  const loadData = async () => {
    try {
      const [agentsRes, requestsRes, statsRes] = await Promise.all([
        agentApi.getAgents(),
        requestApi.getRequests(),
        statsApi.getStats(),
      ]);
      const agentsJson = JSON.stringify(agentsRes.data);
      if (agentsJson !== lastAgentsJson.current) {
        lastAgentsJson.current = agentsJson;
        setAgents(agentsRes.data);
      }
      const requestsJson = JSON.stringify(requestsRes.data);
      if (requestsJson !== lastRequestsJson.current) {
        lastRequestsJson.current = requestsJson;
        setRequests(requestsRes.data);
      }
      const statsJson = JSON.stringify(statsRes.data);
      if (statsJson !== lastStatsJson.current) {
        lastStatsJson.current = statsJson;
        setStats(statsRes.data);
      }
    } catch (err: any) {
      setError(`Failed to load data: ${err.response?.data?.detail || err.message}`);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000); // Auto-refresh every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();
    
    if (!newAgentName.trim()) {
      setError('Agent name is required');
      return;
    }

    try {
      await agentApi.createAgent(newAgentName, newAgentMaxRequests);
      setSuccess('Agent created successfully');
      setNewAgentName('');
      setNewAgentMaxRequests(2);
      await loadData();
    } catch (err: any) {
      setError(`Failed to create agent: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleDeleteAgent = async (id: string) => {
    clearMessages();
    
    if (!confirm('Are you sure you want to delete this agent?')) {
      return;
    }

    try {
      await agentApi.deleteAgent(id);
      setSuccess('Agent deleted successfully');
      await loadData();
    } catch (err: any) {
      setError(`Failed to delete agent: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();
    
    if (!newRequestCustomer.trim() || !newRequestDescription.trim()) {
      setError('Customer name and description are required');
      return;
    }

    try {
      await requestApi.createRequest(newRequestCustomer, newRequestDescription);
      setSuccess('Request created and assigned to agent');
      setNewRequestCustomer('');
      setNewRequestDescription('');
      await loadData();
    } catch (err: any) {
      setError(`Failed to create request: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleCompleteRequest = async (id: string) => {
    clearMessages();
    
    try {
      await requestApi.completeRequest(id);
      setSuccess('Request completed');
      await loadData();
    } catch (err: any) {
      setError(`Failed to complete request: ${err.response?.data?.detail || err.message}`);
    }
  };

  const getAgentName = (agentId: string | null) => {
    if (!agentId) return 'Unassigned';
    const agent = agents.find((a) => a.id === agentId);
    return agent ? agent.name : 'Unknown';
  };

  const getProgressClass = (percentage: number) => {
    if (percentage >= 80) return 'danger';
    if (percentage >= 50) return 'warning';
    return '';
  };

  return (
    <div className="container">
      <h1>🎯 Any-problem-solver</h1>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_agents}</div>
            <div className="stat-label">Total Agents</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.active_requests}</div>
            <div className="stat-label">Active Requests</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.completed_requests}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.utilization}%</div>
            <div className="stat-label">Utilization</div>
          </div>
        </div>
      )}

      <div className="section">
        <h2>Create Agent</h2>
        <form onSubmit={handleCreateAgent} className="form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="agentName">Agent Name</label>
              <input
                id="agentName"
                type="text"
                value={newAgentName}
                onChange={(e) => setNewAgentName(e.target.value)}
                placeholder="Enter agent name"
              />
            </div>
            <div className="form-group">
              <label htmlFor="maxRequests">Max Concurrent Requests</label>
              <input
                id="maxRequests"
                type="number"
                min="1"
                max="10"
                value={newAgentMaxRequests}
                onChange={(e) => setNewAgentMaxRequests(parseInt(e.target.value))}
              />
            </div>
            <button type="submit" className="primary">
              Add Agent
            </button>
          </div>
        </form>

        <h2>Agents</h2>
        {agents.length === 0 ? (
          <div className="empty-state">No agents created yet. Create your first agent above!</div>
        ) : (
          <div className="grid">
            {agents.map((agent) => {
              const utilization = (agent.current_requests.length / agent.max_requests) * 100;
              return (
                <div key={agent.id} className="card">
                  <div className="card-header">
                    <div className="card-title">{agent.name}</div>
                    <button onClick={() => handleDeleteAgent(agent.id)} className="danger">
                      Delete
                    </button>
                  </div>
                  <div className="card-content">
                    <div>
                      <strong>Capacity:</strong> {agent.current_requests.length} / {agent.max_requests}
                    </div>
                    <div className="progress-bar">
                      <div
                        className={`progress-fill ${getProgressClass(utilization)}`}
                        style={{ width: `${utilization}%` }}
                      />
                    </div>
                    <div>
                      <strong>Available Slots:</strong> {agent.max_requests - agent.current_requests.length}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="section">
        <h2>Create Customer Request</h2>
        <form onSubmit={handleCreateRequest} className="form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="customerName">Customer Name</label>
              <input
                id="customerName"
                type="text"
                value={newRequestCustomer}
                onChange={(e) => setNewRequestCustomer(e.target.value)}
                placeholder="Enter customer name"
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Description</label>
              <input
                id="description"
                type="text"
                value={newRequestDescription}
                onChange={(e) => setNewRequestDescription(e.target.value)}
                placeholder="Enter request description"
              />
            </div>
            <button type="submit" className="primary">
              Submit Request
            </button>
          </div>
        </form>

        <h2>Requests</h2>
        {requests.length === 0 ? (
          <div className="empty-state">No requests yet. Submit your first request above!</div>
        ) : (
          <div className="grid">
            {requests.map((request) => (
              <div key={request.id} className="card">
                <div className="card-header">
                  <div className="card-title">{request.customer_name}</div>
                  <span className={`badge ${request.status}`}>{request.status}</span>
                </div>
                <div className="card-content">
                  <div>
                    <strong>Description:</strong> {request.description}
                  </div>
                  <div>
                    <strong>Assigned to:</strong> {getAgentName(request.assigned_agent_id)}
                  </div>
                  <div>
                    <strong>Created:</strong> {new Date(request.created_at).toLocaleString()}
                  </div>
                  {request.status === 'processing' && (
                    <button onClick={() => handleCompleteRequest(request.id)} className="success">
                      Complete Request
                    </button>
                  )}
                  {request.completed_at && (
                    <div>
                      <strong>Completed:</strong> {new Date(request.completed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
