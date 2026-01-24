# Quick Start Guide

Get the Agent Load Balancer running in under 5 minutes!

## 🚀 Fastest Way: Docker

### Prerequisites
- Docker and Docker Compose installed

### Steps

```bash
# 1. Clone or navigate to the project
cd /path/to/solvers

# 2. Start everything with one command
docker-compose up --build

# 3. Open your browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

That's it! 🎉

## 📋 What to Try

### 1. Create Your First Agent
1. Go to http://localhost:3000
2. Enter agent name: "Alice"
3. Set max requests: 2
4. Click "Add Agent"

### 2. Create More Agents
- Add "Bob" with max requests: 3
- Add "Charlie" with max requests: 1

### 3. Submit Requests
1. Customer: "John Doe"
2. Description: "Need help with setup"
3. Click "Submit Request"
4. Watch it auto-assign to the agent with most capacity!

### 4. Complete Requests
- Click "Complete Request" on any processing request
- Watch the agent's capacity free up

### 5. Monitor Statistics
- Check the stats cards at the top
- See real-time utilization percentage
- Watch the dashboard update every 3 seconds

## 🧪 Test the Load Balancing

Try this experiment:

```
Initial Setup:
- Agent A: capacity 2
- Agent B: capacity 3
- Agent C: capacity 1

Submit 7 requests and watch:
1. Request 1 → Agent B (has capacity 3)
2. Request 2 → Agent B (still has capacity 3)
3. Request 3 → Agent B (still has capacity 3, now full)
4. Request 4 → Agent A (has capacity 2)
5. Request 5 → Agent A (still has capacity 2, now full)
6. Request 6 → Agent C (has capacity 1, now full)
7. Request 7 → ERROR (all agents at capacity!)

Now complete one request on Agent B:
8. Request 8 → Agent B (capacity freed up)
```

## 💡 API Examples

### Using curl

```bash
# Create an agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "Agent Smith", "max_requests": 2}'

# List all agents
curl http://localhost:8000/agents

# Create a request
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "John Doe", "description": "Help needed"}'

# Get statistics
curl http://localhost:8000/stats

# Complete a request (replace {id} with actual request ID)
curl -X POST http://localhost:8000/requests/{id}/complete
```

### Using JavaScript

```javascript
// Create an agent
fetch('http://localhost:8000/agents', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Agent Smith',
    max_requests: 2
  })
})
.then(res => res.json())
.then(data => console.log(data));

// Create a request
fetch('http://localhost:8000/requests', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    customer_name: 'John Doe',
    description: 'Need help'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### Using Python

```python
import requests

# Create an agent
response = requests.post(
    'http://localhost:8000/agents',
    json={
        'name': 'Agent Smith',
        'max_requests': 2
    }
)
print(response.json())

# Create a request
response = requests.post(
    'http://localhost:8000/requests',
    json={
        'customer_name': 'John Doe',
        'description': 'Need help'
    }
)
print(response.json())

# Get stats
response = requests.get('http://localhost:8000/stats')
print(response.json())
```

## 🔍 Exploring the API

Visit http://localhost:8000/docs for interactive API documentation where you can:
- See all available endpoints
- Try API calls directly in the browser
- View request/response schemas
- Test different scenarios

## 🛠️ Local Development (Without Docker)

### Terminal 1 - Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🚨 Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or use different ports
# Backend: Change in backend/main.py
# Frontend: Change in frontend/vite.config.ts
```

### Docker Issues

```bash
# Clean everything and restart
docker-compose down -v
docker-compose up --build --force-recreate
```

### Can't Connect to API

1. Check backend is running: `curl http://localhost:8000`
2. Check Docker containers: `docker-compose ps`
3. Check logs: `docker-compose logs backend`

## 📚 Next Steps

1. Read [README.md](README.md) for complete documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for cloud deployment

## 🎯 Common Scenarios

### Scenario: No Agents Available
**Problem**: "No available agents" error when creating request
**Solution**: Create at least one agent before submitting requests

### Scenario: Can't Delete Agent
**Problem**: "Cannot delete agent with active requests" error
**Solution**: Complete or cancel all requests assigned to that agent first

### Scenario: Data Disappeared
**Problem**: All agents and requests gone after restart
**Reason**: In-memory storage (by design for demo)
**Solution**: For persistence, integrate a database (see README.md)

## 💻 Development Tips

### Auto-reload on Changes
- **Backend**: Use `uvicorn main:app --reload`
- **Frontend**: Vite automatically hot-reloads

### View Logs
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Or all together
docker-compose logs -f
```

### Clear All Data
Just restart the backend:
```bash
# Docker
docker-compose restart backend

# Local
# Stop and start the Python process
```

## 🎨 Customization Ideas

### Change Default Capacity
Edit `backend/main.py`:
```python
max_requests: int = Field(default=5, ge=1)  # Change from 2 to 5
```

### Change Refresh Interval
Edit `frontend/src/App.tsx`:
```typescript
const interval = setInterval(loadData, 5000); // Change from 3000 to 5000ms
```

### Add More Agents Automatically
Add to `backend/main.py` on startup:
```python
@app.on_event("startup")
async def startup_event():
    # Create default agents
    for i in range(1, 4):
        agent_id = str(uuid.uuid4())
        agent = Agent(
            id=agent_id,
            name=f"Agent {i}",
            max_requests=2
        )
        agents_db[agent_id] = agent
```

---

Happy load balancing! 🎯
