# Architecture Overview

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│                     http://localhost:3000                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     REACT FRONTEND                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  App.tsx (Main Component)                                │  │
│  │  - Agent Management UI                                    │  │
│  │  - Request Creation UI                                    │  │
│  │  - Statistics Dashboard                                   │  │
│  │  - Auto-refresh (3s interval)                            │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │  api.ts (API Client)                                     │  │
│  │  - Axios HTTP Client                                     │  │
│  │  - Type-safe API calls                                   │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         │ axios.post/get/delete
                         │ http://localhost:8000
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     FASTAPI BACKEND                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (main.py)                           │  │
│  │  - CORS Middleware                                       │  │
│  │  - Request Validation (Pydantic)                         │  │
│  │  - API Endpoints                                         │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │  Load Balancer Logic                                     │  │
│  │  - find_most_available_agent()                           │  │
│  │  - Sorts by available capacity                           │  │
│  │  - Returns agent with most slots                         │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │  In-Memory Storage                                       │  │
│  │  - agents_db: dict[str, Agent]                           │  │
│  │  - requests_db: dict[str, Request]                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Models

### Agent Model
```python
{
  "id": "uuid-string",
  "name": "Agent Name",
  "max_requests": 2,  # Configurable capacity
  "current_requests": ["request-id-1", "request-id-2"]
}
```

**Properties:**
- `available_capacity`: Computed as `max_requests - len(current_requests)`
- `is_available`: Boolean, true if capacity available

### Request Model
```python
{
  "id": "uuid-string",
  "customer_name": "John Doe",
  "description": "Help with setup",
  "assigned_agent_id": "agent-uuid",
  "status": "processing",  # pending | processing | completed
  "created_at": "2026-01-24T10:30:00Z",
  "completed_at": null
}
```

### Statistics Model
```python
{
  "total_agents": 3,
  "total_requests": 15,
  "active_requests": 5,
  "completed_requests": 10,
  "available_capacity": 2,
  "total_capacity": 6,
  "utilization": 66.67  # Percentage
}
```

## Load Balancing Algorithm

### Selection Process

```python
def find_most_available_agent() -> Optional[Agent]:
    # 1. Filter agents with available capacity
    available_agents = [
        agent for agent in agents_db.values() 
        if agent.is_available
    ]
    
    # 2. If no agents available, return None
    if not available_agents:
        return None
    
    # 3. Find agent with maximum available capacity
    most_available = max(
        available_agents, 
        key=lambda a: a.available_capacity
    )
    
    return most_available
```

### Example Scenario

**Initial State:**
- Agent A: capacity 2/2 (full)
- Agent B: capacity 1/3 (2 slots free)
- Agent C: capacity 0/1 (1 slot free)

**New Request Arrives:**
1. Filter: Available agents = [B, C]
2. Compare: B has 2 slots, C has 1 slot
3. Select: Agent B (most available)
4. Assign: Request → Agent B
5. Update: Agent B now 2/3 (1 slot free)

**Next Request:**
- Available: [B (1 slot), C (1 slot)]
- Tie-breaker: First found (deterministic)
- Select: Agent B or C

## API Endpoints

### Agent Endpoints
- `POST /agents` - Create new agent
- `GET /agents` - List all agents
- `GET /agents/{id}` - Get specific agent
- `DELETE /agents/{id}` - Delete agent (if no active requests)

### Request Endpoints
- `POST /requests` - Create and auto-assign request
- `GET /requests` - List all requests
- `GET /requests/{id}` - Get specific request
- `POST /requests/{id}/complete` - Mark request complete

### Statistics Endpoint
- `GET /stats` - Get system statistics

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Deployment Architectures

### Local Development
```
┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │
│  localhost   │     │  localhost   │
│   :3000      │     │   :8000      │
└──────────────┘     └──────────────┘
```

### Docker Compose
```
┌─────────────────────────────────────┐
│        Docker Network               │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Frontend    │  │   Backend   │ │
│  │  Container   │─▶│  Container  │ │
│  │  :80 → :3000 │  │ :8000→:8000 │ │
│  └──────────────┘  └─────────────┘ │
└─────────────────────────────────────┘
```

### Vercel Deployment
```
┌─────────────────────────────────────┐
│        Vercel CDN (Global)          │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Static Frontend (React)    │  │
│  │   Served from Edge Network   │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │  Serverless Functions        │  │
│  │  (FastAPI Backend)           │  │
│  │  Auto-scaled                 │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## State Management

### Frontend State
- **Local State**: React useState hooks
- **API State**: Fetched every 3 seconds
- **Form State**: Controlled components
- **Error/Success Messages**: Component state

### Backend State
- **In-Memory**: Dictionaries for agents and requests
- **Session**: No session storage (stateless API)
- **Persistence**: None (data lost on restart)

### Production Considerations
For production, replace in-memory storage with:
- **PostgreSQL**: Relational data with ACID compliance
- **MongoDB**: Document-based flexible schema
- **Redis**: Fast caching and session storage
- **Vercel KV**: Key-value store (Vercel-native)

## Security Considerations

### Current Implementation
- ✅ CORS enabled (allows all origins)
- ✅ Input validation via Pydantic
- ✅ Type safety with TypeScript
- ❌ No authentication
- ❌ No rate limiting
- ❌ No request signing

### Production Requirements
1. **Authentication**: JWT tokens or OAuth
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Prevent API abuse
4. **Input Sanitization**: XSS prevention
5. **HTTPS**: Encrypted communication
6. **API Keys**: Secure API access
7. **CORS**: Restrict to specific domains
8. **Logging**: Security audit trail

## Performance Characteristics

### Time Complexity
- Find available agent: O(n) where n = number of agents
- Create request: O(n)
- Complete request: O(1) with agent lookup
- Get all agents/requests: O(n)

### Space Complexity
- Memory: O(a + r) where a = agents, r = requests
- Scales linearly with data

### Bottlenecks
1. **In-Memory Storage**: Limited by RAM
2. **Load Balancing**: Sequential search
3. **No Caching**: Every request hits storage

### Optimizations
1. **Database**: Persistent, indexed storage
2. **Caching**: Redis for frequently accessed data
3. **Load Balancing**: Use priority queue or heap
4. **Pagination**: Limit large result sets
5. **WebSockets**: Real-time updates without polling

## Monitoring & Observability

### Metrics to Track
- Request latency (p50, p95, p99)
- Agent utilization rate
- Request queue depth
- Error rates
- API endpoint response times

### Logging Strategy
- Request/response logs
- Error logs with stack traces
- Agent assignment decisions
- Performance metrics

### Tools
- **Sentry**: Error tracking
- **Datadog/New Relic**: APM
- **Prometheus + Grafana**: Metrics
- **ELK Stack**: Log aggregation

## Scaling Strategy

### Horizontal Scaling
```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │Backend  │      │Backend  │      │Backend  │
    │Instance │      │Instance │      │Instance │
    │   #1    │      │   #2    │      │   #3    │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Database   │
                    └──────────────┘
```

### Requirements for Scale
1. **Shared Database**: All instances access same data
2. **Load Balancer**: Nginx, HAProxy, or cloud LB
3. **Session Storage**: Redis or similar
4. **Message Queue**: RabbitMQ for async tasks
5. **Caching Layer**: Reduce database load

---

Built for scalability, maintainability, and developer experience.
