# Agent Load Balancer System

A full-stack application for managing customer support requests with intelligent agent load balancing. The system automatically routes incoming requests to the most available agent based on their current workload.

## 🚀 Features

- **Agent Management**: Create and manage agents with configurable request capacity
- **Intelligent Load Balancing**: Automatically routes requests to the agent with the most available capacity
- **Real-time Dashboard**: Monitor system statistics, agent workloads, and request status
- **Request Tracking**: Track requests from creation through completion
- **Auto-refresh**: Dashboard updates every 3 seconds for real-time monitoring
- **RESTful API**: Full-featured backend API with FastAPI
- **Modern UI**: Beautiful, responsive React frontend with TypeScript

## 📋 System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend  │ ───> │   Backend    │ ───> │   Agents     │
│  (React)    │      │  (FastAPI)   │      │ Load Balancer│
└─────────────┘      └──────────────┘      └──────────────┘
```

### How Load Balancing Works

1. **Agent Creation**: Each agent has a configurable max request capacity (default: 2)
2. **Request Submission**: When a new request arrives, the system finds the agent with the most available slots
3. **Assignment**: Request is assigned to the selected agent and added to their queue
4. **Completion**: When an agent completes a request, it's removed from their queue, freeing capacity

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Python 3.11+**

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **CSS3**: Modern styling

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Vercel**: Cloud deployment platform
- **GitHub Actions**: CI/CD pipeline

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 20 or higher
- Docker and Docker Compose (optional, for containerized deployment)

### Option 1: Local Development

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Option 2: Docker Deployment

```bash
# From project root directory
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop containers
docker-compose down
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 🌐 Vercel Deployment

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed deployment instructions.

### Quick Setup

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Login and Link Project**
```bash
vercel login
vercel link
```

3. **Configure GitHub Secrets**
   - `VERCEL_TOKEN`: Your Vercel API token
   - `VERCEL_ORG_ID`: From `.vercel/project.json`
   - `VERCEL_PROJECT_ID`: From `.vercel/project.json`

4. **Deploy**
```bash
# Production deployment
vercel --prod

# Preview deployment
vercel
```

## 📚 API Documentation

### Agents

#### Create Agent
```http
POST /agents
Content-Type: application/json

{
  "name": "Agent Smith",
  "max_requests": 2
}
```

#### Get All Agents
```http
GET /agents
```

#### Get Single Agent
```http
GET /agents/{agent_id}
```

#### Delete Agent
```http
DELETE /agents/{agent_id}
```

### Requests

#### Create Request
```http
POST /requests
Content-Type: application/json

{
  "customer_name": "John Doe",
  "description": "Need help with account setup"
}
```

#### Get All Requests
```http
GET /requests
```

#### Get Single Request
```http
GET /requests/{request_id}
```

#### Complete Request
```http
POST /requests/{request_id}/complete
```

### Statistics

#### Get System Stats
```http
GET /stats
```

Returns:
```json
{
  "total_agents": 3,
  "total_requests": 10,
  "active_requests": 4,
  "completed_requests": 6,
  "available_capacity": 2,
  "total_capacity": 6,
  "utilization": 66.67
}
```

## 🎯 Usage Examples

### Creating Agents

1. Open the frontend at `http://localhost:3000`
2. Fill in the "Create Agent" form:
   - Agent Name: e.g., "Agent Alice"
   - Max Concurrent Requests: e.g., 3
3. Click "Add Agent"

### Submitting Requests

1. Fill in the "Create Customer Request" form:
   - Customer Name: e.g., "John Doe"
   - Description: e.g., "Need help with billing"
2. Click "Submit Request"
3. The system automatically assigns it to the most available agent

### Completing Requests

1. Find a request with "PROCESSING" status
2. Click the "Complete Request" button
3. The request is marked as completed and removed from the agent's queue

## 🏗️ Project Structure

```
solvers/
├── backend/
│   ├── api/
│   │   └── index.py          # Vercel serverless entry point
│   ├── main.py               # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Backend container config
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── api.ts           # API client
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile           # Frontend container config
│   ├── nginx.conf           # Nginx configuration
│   └── .dockerignore
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions CI/CD
├── docker-compose.yml       # Multi-container setup
├── vercel.json             # Vercel configuration
├── .gitignore
├── README.md               # This file
└── VERCEL_DEPLOYMENT.md    # Deployment guide
```

## 🔧 Configuration

### Environment Variables

#### Backend
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

#### Frontend
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## 🧪 Testing the System

### Manual Testing

1. **Start the application** (using Docker or locally)

2. **Create multiple agents**:
   - Agent 1: Max requests = 2
   - Agent 2: Max requests = 3
   - Agent 3: Max requests = 1

3. **Submit requests** and observe load balancing:
   - First request → Goes to Agent 2 (highest capacity: 3)
   - Second request → Goes to Agent 2 (capacity: 3)
   - Third request → Goes to Agent 2 (capacity: 3, now full)
   - Fourth request → Goes to Agent 1 (highest remaining: 2)
   - Continue until all agents are full

4. **Complete requests** and watch capacity free up

5. **Monitor stats** to see real-time utilization

## 🚨 Important Notes

### Data Persistence

The current implementation uses **in-memory storage** for simplicity. This means:
- ⚠️ Data is lost when the server restarts
- ⚠️ Not suitable for production without modification
- ⚠️ For production, integrate a database:
  - Vercel Postgres
  - MongoDB Atlas
  - PostgreSQL
  - Redis

### Production Considerations

1. **Database**: Add persistent storage
2. **Authentication**: Implement user authentication
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Logging**: Implement proper logging
5. **Monitoring**: Add error tracking (e.g., Sentry)
6. **CORS**: Update CORS settings to specific domains
7. **Security**: Add security headers and input validation
8. **Testing**: Add unit and integration tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check port 8000 is available: `lsof -i :8000`

### Frontend won't start
- Check Node version: `node --version` (should be 20+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check port 3000 is available: `lsof -i :3000`

### Docker issues
- Ensure Docker is running: `docker --version`
- Clean up containers: `docker-compose down -v`
- Rebuild: `docker-compose up --build --force-recreate`

### API connection issues
- Verify backend is running: `curl http://localhost:8000`
- Check CORS settings in `backend/main.py`
- Verify `VITE_API_URL` in frontend `.env` file

## 📞 Support

For issues and questions:
1. Check the [API Documentation](http://localhost:8000/docs) when running locally
2. Review the troubleshooting section above
3. Open an issue on GitHub

## 🎉 Features to Add

Potential enhancements:
- [ ] Agent priority levels
- [ ] Request categorization and routing rules
- [ ] Agent skills and request matching
- [ ] Historical analytics and reporting
- [ ] WebSocket for real-time updates
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Dark/light theme toggle
- [ ] Export data to CSV/JSON
- [ ] Agent performance metrics

---

Built with ❤️ using FastAPI, React, and TypeScript
