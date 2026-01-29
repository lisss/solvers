# 🎯 Agent Load Balancer

A full-stack application for load-balancing customer requests across multiple agents.

## 🚀 Features

- **Agent Management**: Create agents with configurable request limits
- **Smart Load Balancing**: Automatically routes requests to the most available agent
- **Real-time Updates**: UI updates instantly when creating/completing requests
- **Persistence**: Docker setup with SQLite, Vercel with in-memory storage
- **Modern Stack**: FastAPI + React + TypeScript

---

## 📦 Quick Start

### **Local Development with Docker** (Recommended)

```bash
# Clone and start
git clone https://github.com/lisss/solvers.git
cd solvers

# Run with Docker Compose
docker-compose up --build

# Access the app
# Frontend: http://localhost:3002
# Backend API: http://localhost:8000
```

✅ **Data persists** in `backend/data/data.db` (SQLite)

---

### **Local Development without Docker**

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3002
```

---

## 🌐 Vercel Deployment

### **Automatic Deployment** (like black-lodge)

1. Push to GitHub
2. Connect to Vercel
3. Deploy - **that's it!**

No database setup needed. The app works with **in-memory storage** on Vercel.

⚠️ **Note**: Data doesn't persist on Vercel (serverless = stateless). Use Docker for persistence.

### **How it works:**

- **Vercel (Production)**: In-memory SQLite (data resets between function calls)
- **Docker (Local)**: SQLite file with volume mount (data persists)

This is the same approach as [black-lodge](https://github.com/lisss/black-lodge) - simple and works out of the box!

---

## 🎮 Usage

### **Create an Agent**

```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"Agent Smith","max_requests":3}'
```

### **Create a Request**

```bash
curl -X POST http://localhost:8000/requests \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"John Doe","description":"Help with order #123"}'
```

### **Complete a Request**

```bash
curl -X POST http://localhost:8000/requests/{request_id}/complete
```

### **Get Statistics**

```bash
curl http://localhost:8000/stats
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/agents` | Create agent |
| `GET` | `/agents` | List all agents |
| `GET` | `/agents/{id}` | Get agent details |
| `DELETE` | `/agents/{id}` | Delete agent |
| `POST` | `/requests` | Create request (auto-assigns to agent) |
| `GET` | `/requests` | List all requests |
| `GET` | `/requests/{id}` | Get request details |
| `POST` | `/requests/{id}/complete` | Mark request as complete |
| `GET` | `/stats` | Get system statistics |

---

## 🛠️ Tech Stack

### **Backend**
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Simple file-based database (Docker) / In-memory (Vercel)
- **Pydantic** - Data validation

### **Frontend**
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Axios** - HTTP client

### **Deployment**
- **Docker** - Containerization for local dev
- **Vercel** - Serverless deployment (like black-lodge)
- **GitHub Actions** - CI/CD (optional)

---

## 📁 Project Structure

```
solvers/
├── api/
│   ├── index.py          # Vercel serverless function
│   └── requirements.txt  # Python dependencies
├── backend/
│   ├── main.py          # Local development server
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx      # Main React component
│   │   ├── api.ts       # API client
│   │   └── index.css    # Styles
│   ├── Dockerfile       # Frontend container
│   └── package.json     # Node dependencies
├── docker-compose.yml   # Multi-container setup
└── vercel.json         # Vercel deployment config
```

---

## 🔧 Configuration

### **Environment Variables**

**Backend (Docker):**
- `DATABASE_URL` - Default: `sqlite:////app/data/data.db`
- `HOST` - Default: `0.0.0.0`
- `PORT` - Default: `8000`

**Frontend (Docker):**
- `VITE_API_URL` - Default: `http://localhost:8000`

**Vercel:**
- No setup needed! Uses in-memory storage by default.
- (Optional) Add `DATABASE_URL` if you want to connect an external database.

---

## 🐛 Troubleshooting

### **Docker Issues**

```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

### **Port Already in Use**

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Find process using port 3002
lsof -ti:3002 | xargs kill -9
```

### **Frontend Not Connecting to Backend**

1. Check backend is running: `curl http://localhost:8000/`
2. Check CORS is enabled (already configured)
3. Check `VITE_API_URL` environment variable

---

## 🎯 Load Balancing Algorithm

The system uses a **greedy availability-based** algorithm:

1. When a request comes in, check all agents
2. Calculate available capacity for each: `max_requests - current_requests`
3. Assign to the agent with the **highest available capacity**
4. If all agents are at capacity, return error (503)

---

## 🚀 Deployment Workflow

### **Like black-lodge:**

```bash
# 1. Make changes
git add .
git commit -m "your message"

# 2. Push to GitHub
git push

# 3. Vercel auto-deploys
# Done! ✅
```

---

## 📝 License

MIT License - feel free to use this project however you want!

---

## 🤝 Contributing

PRs welcome! This is a simple project, so feel free to add features or improvements.

---

## ✨ Why This Approach?

Following the [black-lodge](https://github.com/lisss/black-lodge) deployment model:

✅ **Simple** - No database setup on Vercel  
✅ **Fast** - Deploys in seconds  
✅ **Reliable** - Fewer moving parts  
✅ **Cost-effective** - No database costs  
✅ **Docker for dev** - Persistence when you need it  

Perfect for demos, prototypes, and small apps! 🎉
