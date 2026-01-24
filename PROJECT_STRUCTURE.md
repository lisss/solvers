# Project Structure

Complete file tree of the Agent Load Balancer system.

```
solvers/
│
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md               # Quick start guide
├── 📄 ARCHITECTURE.md             # System architecture details
├── 📄 VERCEL_DEPLOYMENT.md        # Vercel deployment guide
├── 📄 CONTRIBUTING.md             # Contribution guidelines
├── 📄 CHANGELOG.md                # Version history
├── 📄 CONTRIBUTORS.md             # List of contributors
├── 📄 LICENSE                     # MIT License
├── 📄 .gitignore                  # Git ignore rules
├── 📄 docker-compose.yml          # Multi-container orchestration
├── 📄 vercel.json                 # Vercel configuration
├── 🔧 setup.sh                    # Unix setup script
├── 🔧 setup.bat                   # Windows setup script
│
├── 📁 backend/                    # Python FastAPI backend
│   ├── 📄 main.py                 # FastAPI application
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📄 Dockerfile              # Backend container config
│   ├── 📄 .dockerignore           # Docker ignore rules
│   │
│   └── 📁 api/                    # Vercel serverless functions
│       └── 📄 index.py            # Serverless entry point
│
├── 📁 frontend/                   # React TypeScript frontend
│   ├── 📄 index.html              # HTML entry point
│   ├── 📄 package.json            # Node dependencies
│   ├── 📄 vite.config.ts          # Vite configuration
│   ├── 📄 tsconfig.json           # TypeScript config
│   ├── 📄 tsconfig.node.json      # TypeScript Node config
│   ├── 📄 Dockerfile              # Frontend container config
│   ├── 📄 nginx.conf              # Nginx web server config
│   ├── 📄 .dockerignore           # Docker ignore rules
│   │
│   └── 📁 src/                    # Source code
│       ├── 📄 main.tsx            # React entry point
│       ├── 📄 App.tsx             # Main application component
│       ├── 📄 api.ts              # API client & types
│       └── 📄 index.css           # Global styles
│
└── 📁 .github/                    # GitHub configuration
    └── 📁 workflows/
        └── 📄 deploy.yml          # CI/CD pipeline
```

## 📂 Directory Descriptions

### Root Directory
Contains all documentation, configuration files, and setup scripts.

### `/backend`
Python FastAPI backend application.
- **main.py**: Core API logic, endpoints, load balancing algorithm
- **requirements.txt**: Python package dependencies
- **Dockerfile**: Container configuration for backend
- **/api**: Vercel serverless function wrapper

### `/frontend`
React + TypeScript frontend application.
- **src/**: Source code directory
  - **main.tsx**: React DOM rendering entry point
  - **App.tsx**: Main UI component with all features
  - **api.ts**: Axios HTTP client and TypeScript interfaces
  - **index.css**: CSS styling with modern design
- **vite.config.ts**: Vite build tool configuration
- **Dockerfile**: Multi-stage build for production
- **nginx.conf**: Web server configuration for production

### `/.github/workflows`
GitHub Actions CI/CD pipeline configuration.
- **deploy.yml**: Automated deployment to Vercel

## 📊 File Statistics

| Category        | Count | Lines of Code (approx) |
|-----------------|-------|------------------------|
| Documentation   | 7     | 2,500+                 |
| Backend         | 3     | 300+                   |
| Frontend        | 6     | 500+                   |
| Configuration   | 8     | 200+                   |
| Scripts         | 2     | 150+                   |
| **Total**       | **26**| **3,650+**             |

## 🎯 Key Files by Purpose

### Getting Started
1. `QUICKSTART.md` - Start here for fastest setup
2. `README.md` - Complete documentation
3. `setup.sh` or `setup.bat` - Automated setup

### Development
1. `backend/main.py` - Backend API logic
2. `frontend/src/App.tsx` - Frontend UI
3. `frontend/src/api.ts` - API integration

### Deployment
1. `docker-compose.yml` - Local Docker deployment
2. `vercel.json` - Vercel cloud deployment
3. `.github/workflows/deploy.yml` - CI/CD pipeline

### Documentation
1. `ARCHITECTURE.md` - System design
2. `CONTRIBUTING.md` - How to contribute
3. `VERCEL_DEPLOYMENT.md` - Cloud deployment

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel deployment configuration |
| `docker-compose.yml` | Multi-container orchestration |
| `vite.config.ts` | Frontend build configuration |
| `tsconfig.json` | TypeScript compiler settings |
| `nginx.conf` | Production web server settings |
| `.gitignore` | Git version control exclusions |
| `.dockerignore` | Docker build exclusions |

## 📝 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `QUICKSTART.md` | Quick start guide |
| `ARCHITECTURE.md` | System architecture |
| `VERCEL_DEPLOYMENT.md` | Deployment guide |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CHANGELOG.md` | Version history |
| `CONTRIBUTORS.md` | List of contributors |
| `LICENSE` | MIT License |

## 🚀 Entry Points

### Running the Application

```bash
# Docker (recommended)
docker-compose up --build
Entry: docker-compose.yml

# Local Backend
python backend/main.py
Entry: backend/main.py

# Local Frontend  
npm run dev (from frontend/)
Entry: frontend/src/main.tsx

# Production Deploy
vercel --prod
Entry: vercel.json
```

## 📦 Dependencies

### Backend (Python)
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation

### Frontend (Node.js)
- React - UI library
- TypeScript - Type safety
- Vite - Build tool
- Axios - HTTP client

### DevOps
- Docker - Containerization
- Nginx - Web server
- Vercel - Hosting platform

## 🎨 Code Organization

### Backend Structure
```python
main.py
├── FastAPI app initialization
├── CORS middleware
├── Pydantic models (Agent, Request)
├── In-memory storage (dicts)
├── Load balancing logic
└── API endpoints
    ├── /agents (CRUD)
    ├── /requests (CRUD + complete)
    └── /stats (read-only)
```

### Frontend Structure
```typescript
App.tsx
├── State management (useState)
├── Data fetching (useEffect)
├── Form handlers
└── UI Components
    ├── Stats Dashboard
    ├── Agent Management
    └── Request Management

api.ts
├── Axios client setup
├── TypeScript interfaces
└── API functions
    ├── agentApi
    ├── requestApi
    └── statsApi
```

## 🔐 Security Files

- `.gitignore` - Prevents committing sensitive data
- `.dockerignore` - Excludes files from Docker images
- `.env.example` - Template for environment variables

## 📊 Lines of Code by File Type

| Type | Files | Approx Lines |
|------|-------|--------------|
| Python (.py) | 2 | 300 |
| TypeScript (.ts/.tsx) | 4 | 500 |
| CSS (.css) | 1 | 250 |
| Markdown (.md) | 7 | 2,500 |
| YAML (.yml) | 2 | 50 |
| JSON (.json) | 4 | 100 |
| Config (other) | 6 | 200 |

---

This structure is designed for:
- ✅ Easy navigation
- ✅ Clear separation of concerns
- ✅ Simple deployment
- ✅ Scalable architecture
- ✅ Comprehensive documentation
