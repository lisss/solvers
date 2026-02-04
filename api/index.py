from datetime import datetime
import os
import uuid
import json
import urllib.request
import urllib.error
import base64
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Use GitHub repo as storage - commit data.json on every change
# This requires a GitHub token with repo access
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "lisss/solvers"
DATA_FILE = "data/storage.json"

class GitHubStorage:
    """Storage backend using GitHub repo"""
    
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.repo = REPO
        self.file_path = DATA_FILE
        self.cache = {"agents": {}, "requests": {}}
        self.sha = None
        
    def _api_call(self, method: str, url: str, data: dict = None):
        """Make GitHub API call"""
        if not self.token:
            return None
            
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        try:
            req_data = json.dumps(data).encode('utf-8') if data else None
            request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"GitHub API error: {e.code}")
            return None
        except Exception as e:
            print(f"GitHub API error: {e}")
            return None
    
    def load(self) -> dict:
        """Load data from GitHub"""
        if not self.token:
            return self.cache
            
        url = f"https://api.github.com/repos/{self.repo}/contents/{self.file_path}"
        result = self._api_call("GET", url)
        
        if result and "content" in result:
            self.sha = result["sha"]
            content = base64.b64decode(result["content"]).decode('utf-8')
            try:
                self.cache = json.loads(content)
                return self.cache
            except:
                return self.cache
        return self.cache
    
    def save(self, data: dict):
        """Save data to GitHub"""
        if not self.token:
            self.cache = data
            return
            
        self.cache = data
        
        # Get current SHA if we don't have it
        if not self.sha:
            url = f"https://api.github.com/repos/{self.repo}/contents/{self.file_path}"
            result = self._api_call("GET", url)
            if result and "sha" in result:
                self.sha = result["sha"]
        
        # Commit the file
        url = f"https://api.github.com/repos/{self.repo}/contents/{self.file_path}"
        content = base64.b64encode(json.dumps(data, indent=2).encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": "Update storage",
            "content": content
        }
        
        if self.sha:
            payload["sha"] = self.sha
        
        result = self._api_call("PUT", url, payload)
        if result and "content" in result:
            self.sha = result["content"]["sha"]

# Initialize storage
storage = GitHubStorage()

# Models
class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    max_requests: int = 2
    current_requests: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Request(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    description: str
    agent_id: Optional[str] = None
    status: str = "pending"  # pending, assigned, completed
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

class CreateAgent(BaseModel):
    name: str
    max_requests: int = 2

class CreateRequest(BaseModel):
    customer_name: str
    description: str

app = FastAPI(title="Agent Load Balancer API", root_path="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup initialization removed - not compatible with serverless

@app.get("/")
async def root():
    return {"message": "Agent Load Balancer API", "version": "1.0", "storage": "github" if GITHUB_TOKEN else "memory"}

@app.get("/agents", response_model=List[Agent])
async def list_agents():
    """Get all agents"""
    data = storage.load()
    agents = list(data.get("agents", {}).values())
    return agents

@app.post("/agents", response_model=Agent)
async def create_agent(agent_data: CreateAgent):
    """Create a new agent"""
    data = storage.load()
    
    agent = Agent(
        name=agent_data.name,
        max_requests=agent_data.max_requests,
        current_requests=[]
    )
    
    if "agents" not in data:
        data["agents"] = {}
    data["agents"][agent.id] = agent.model_dump()
    storage.save(data)
    
    return agent

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get a specific agent"""
    data = storage.load()
    agents = data.get("agents", {})
    
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return Agent(**agents[agent_id])

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    data = storage.load()
    agents = data.get("agents", {})
    
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Also remove all requests assigned to this agent
    requests = data.get("requests", {})
    for req_id in list(requests.keys()):
        if requests[req_id].get("agent_id") == agent_id:
            requests[req_id]["agent_id"] = None
            requests[req_id]["status"] = "pending"
    
    del agents[agent_id]
    storage.save(data)
    
    return {"message": "Agent deleted successfully"}

@app.get("/requests", response_model=List[Request])
async def list_requests():
    """Get all requests"""
    data = storage.load()
    requests = list(data.get("requests", {}).values())
    return requests

@app.post("/requests", response_model=Request)
async def create_request(request_data: CreateRequest):
    """Create a new customer request and assign to most available agent"""
    data = storage.load()
    agents = data.get("agents", {})
    
    # Create the request
    request = Request(
        customer_name=request_data.customer_name,
        description=request_data.description,
        status="pending"
    )
    
    # Find the most available agent (with least current requests and capacity)
    best_agent_id = None
    min_load = float('inf')
    
    for agent_id, agent_data in agents.items():
        current_count = len(agent_data.get("current_requests", []))
        max_requests = agent_data.get("max_requests", 2)
        
        # Skip agents that are at capacity
        if current_count >= max_requests:
            continue
        
        # Choose agent with lowest current load
        if current_count < min_load:
            min_load = current_count
            best_agent_id = agent_id
    
    # Assign to best agent if found
    if best_agent_id:
        request.agent_id = best_agent_id
        request.status = "assigned"
        
        # Add request to agent's current_requests
        if "current_requests" not in agents[best_agent_id]:
            agents[best_agent_id]["current_requests"] = []
        agents[best_agent_id]["current_requests"].append(request.id)
    
    # Save the request
    if "requests" not in data:
        data["requests"] = {}
    data["requests"][request.id] = request.model_dump()
    
    storage.save(data)
    
    return request

@app.get("/requests/{request_id}", response_model=Request)
async def get_request(request_id: str):
    """Get a specific request"""
    data = storage.load()
    requests = data.get("requests", {})
    
    if request_id not in requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return Request(**requests[request_id])

@app.post("/requests/{request_id}/complete")
async def complete_request(request_id: str):
    """Mark a request as completed and remove from agent's list"""
    data = storage.load()
    requests = data.get("requests", {})
    agents = data.get("agents", {})
    
    if request_id not in requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = requests[request_id]
    agent_id = request.get("agent_id")
    
    # Update request status
    request["status"] = "completed"
    request["completed_at"] = datetime.utcnow().isoformat()
    
    # Remove from agent's current_requests
    if agent_id and agent_id in agents:
        current_requests = agents[agent_id].get("current_requests", [])
        if request_id in current_requests:
            current_requests.remove(request_id)
            agents[agent_id]["current_requests"] = current_requests
    
    storage.save(data)
    
    return Request(**request)

@app.delete("/requests/{request_id}")
async def delete_request(request_id: str):
    """Delete a request"""
    data = storage.load()
    requests = data.get("requests", {})
    agents = data.get("agents", {})
    
    if request_id not in requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = requests[request_id]
    agent_id = request.get("agent_id")
    
    # Remove from agent's current_requests
    if agent_id and agent_id in agents:
        current_requests = agents[agent_id].get("current_requests", [])
        if request_id in current_requests:
            current_requests.remove(request_id)
            agents[agent_id]["current_requests"] = current_requests
    
    del requests[request_id]
    storage.save(data)
    
    return {"message": "Request deleted successfully"}

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    data = storage.load()
    agents = data.get("agents", {})
    requests = data.get("requests", {})
    
    total_capacity = sum(a.get("max_requests", 2) for a in agents.values())
    total_assigned = sum(len(a.get("current_requests", [])) for a in agents.values())
    
    return {
        "total_agents": len(agents),
        "total_requests": len(requests),
        "total_capacity": total_capacity,
        "total_assigned": total_assigned,
        "available_capacity": total_capacity - total_assigned
    }

# For Vercel serverless
from mangum import Mangum
handler = Mangum(app)
