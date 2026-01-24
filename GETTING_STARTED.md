# 🚀 Getting Started in 3 Steps

## Step 1: Start the Application

### Option A: Docker (Recommended) 🐳

```bash
cd solvers
docker-compose up --build
```

**That's it!** The application is now running.

### Option B: Local Development 💻

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Step 2: Open in Browser

### Frontend Application
**URL**: http://localhost:3000

You'll see:
- 📊 Statistics dashboard at the top
- ➕ Agent creation form
- 👥 List of agents (initially empty)
- 📝 Request creation form
- 📋 List of requests (initially empty)

### API Documentation
**URL**: http://localhost:8000/docs

Interactive API documentation where you can:
- View all endpoints
- Test API calls
- See request/response schemas

---

## Step 3: Create Your First Agent & Request

### 3.1 Create an Agent

In the browser at http://localhost:3000:

1. Find the "Create Agent" section
2. Enter:
   - **Agent Name**: `Sarah`
   - **Max Concurrent Requests**: `2`
3. Click **"Add Agent"**

✅ You'll see Sarah appear in the agents list!

### 3.2 Create Another Agent

1. **Agent Name**: `Mike`
2. **Max Concurrent Requests**: `3`
3. Click **"Add Agent"**

✅ Now you have two agents!

### 3.3 Submit a Request

1. Find the "Create Customer Request" section
2. Enter:
   - **Customer Name**: `John Doe`
   - **Description**: `Need help with password reset`
3. Click **"Submit Request"**

✅ Watch it automatically assign to Mike (he has the highest capacity: 3)!

### 3.4 Submit More Requests

Try submitting 5 more requests and watch the load balancing in action:

- Request 1 → Mike (capacity: 3)
- Request 2 → Mike (capacity: 3)
- Request 3 → Mike (capacity: 3, now full!)
- Request 4 → Sarah (capacity: 2)
- Request 5 → Sarah (capacity: 2, now full!)
- Request 6 → ❌ Error: No available agents!

### 3.5 Complete a Request

1. Find any request with status **"PROCESSING"**
2. Click **"Complete Request"**
3. Watch the agent's capacity bar update!
4. Try submitting another request - it will now work!

---

## 🎉 Congratulations!

You've successfully:
- ✅ Started the application
- ✅ Created agents
- ✅ Submitted requests
- ✅ Watched load balancing in action
- ✅ Completed requests

---

## 🔍 What to Explore Next

### 1. Check the Statistics
Look at the stats cards at the top:
- Total Agents
- Active Requests
- Completed Requests
- System Utilization %

These update automatically every 3 seconds!

### 2. Try the API
Open http://localhost:8000/docs and try:

**Create an agent:**
```json
POST /agents
{
  "name": "Agent 007",
  "max_requests": 5
}
```

**Get all agents:**
```
GET /agents
```

**Get system stats:**
```
GET /stats
```

### 3. Test Edge Cases

**What happens if you:**
- Delete an agent with active requests? (It won't let you!)
- Fill all agents to capacity? (New requests will fail)
- Create an agent with capacity 10? (It works!)
- Complete a request twice? (It will fail)

### 4. Read the Documentation

- **QUICKSTART.md** - Quick reference guide
- **README.md** - Complete documentation
- **EXAMPLES.md** - Real-world scenarios
- **ARCHITECTURE.md** - How it works under the hood

---

## 🛠️ Using with cURL

If you prefer command line:

```bash
# Create agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "CLI Agent", "max_requests": 2}'

# Create request
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Jane", "description": "Help needed"}'

# Get stats
curl http://localhost:8000/stats | jq
```

---

## 🐛 Troubleshooting

### "Port already in use"
```bash
# Check what's using the port
lsof -i :8000  # or :3000

# Kill the process or stop it properly
```

### "Cannot connect to backend"
1. Make sure backend is running
2. Check http://localhost:8000 in browser
3. Look at backend logs for errors

### "Docker issues"
```bash
# Clean everything
docker-compose down -v
docker-compose up --build --force-recreate
```

---

## 📚 Next Steps

### For Users
- Read **EXAMPLES.md** for real-world scenarios
- Check **README.md** for complete features

### For Developers
- Read **ARCHITECTURE.md** to understand the system
- Check **CONTRIBUTING.md** to contribute

### For DevOps
- See **VERCEL_DEPLOYMENT.md** for cloud deployment
- Review Docker files for containerization

---

## 🎯 Quick Commands Reference

| Action | Command |
|--------|---------|
| Start (Docker) | `docker-compose up --build` |
| Stop (Docker) | `docker-compose down` |
| Start Backend | `cd backend && python main.py` |
| Start Frontend | `cd frontend && npm run dev` |
| View API Docs | http://localhost:8000/docs |
| View Frontend | http://localhost:3000 |
| Check Stats | `curl http://localhost:8000/stats` |

---

## 💡 Tips

1. **Auto-refresh**: The dashboard updates every 3 seconds automatically
2. **Mobile Friendly**: Try it on your phone!
3. **Dark Mode**: Uses your system theme preference
4. **API First**: All UI actions use the API - you can build your own UI!
5. **Type Safe**: Full TypeScript and Python type hints

---

**Happy Load Balancing!** 🎯

Need help? Check the documentation or open an issue on GitHub.
