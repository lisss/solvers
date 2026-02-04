from datetime import datetime
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mangum import Mangum

# In-memory storage
agents_db = {}
requests_db = {}

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
    status: str = "pending"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

class CreateAgent(BaseModel):
    name: str
    max_requests: int = 2

class CreateRequest(BaseModel):
    customer_name: str
    description: str

app = FastAPI(title="Agent Load Balancer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Agent Load Balancer API", "version": "1.0"}

@app.get("/agents", response_model=List[Agent])
async def list_agents():
    return list(agents_db.values())

@app.post("/agents", response_model=Agent)
async def create_agent(agent_data: CreateAgent):
    agent = Agent(name=agent_data.name, max_requests=agent_data.max_requests)
    agents_db[agent.id] = agent
    return agent

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Remove all requests assigned to this agent
    for req in requests_db.values():
        if req.agent_id == agent_id:
            req.agent_id = None
            req.status = "pending"
    
    del agents_db[agent_id]
    return {"message": "Agent deleted successfully"}

@app.get("/requests", response_model=List[Request])
async def list_requests():
    return list(requests_db.values())

@app.post("/requests", response_model=Request)
async def create_request(request_data: CreateRequest):
    request = Request(
        customer_name=request_data.customer_name,
        description=request_data.description,
        status="pending"
    )
    
    # Find the most available agent
    best_agent_id = None
    min_load = float('inf')
    
    for agent_id, agent in agents_db.items():
        current_count = len(agent.current_requests)
        
        if current_count >= agent.max_requests:
            continue
        
        if current_count < min_load:
            min_load = current_count
            best_agent_id = agent_id
    
    # Assign to best agent if found
    if best_agent_id:
        request.agent_id = best_agent_id
        request.status = "assigned"
        agents_db[best_agent_id].current_requests.append(request.id)
    
    requests_db[request.id] = request
    return request

@app.get("/requests/{request_id}", response_model=Request)
async def get_request(request_id: str):
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")
    return requests_db[request_id]

@app.post("/requests/{request_id}/complete")
async def complete_request(request_id: str):
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = requests_db[request_id]
    request.status = "completed"
    request.completed_at = datetime.utcnow().isoformat()
    
    # Remove from agent's current_requests
    if request.agent_id and request.agent_id in agents_db:
        agent = agents_db[request.agent_id]
        if request_id in agent.current_requests:
            agent.current_requests.remove(request_id)
    
    return request

@app.delete("/requests/{request_id}")
async def delete_request(request_id: str):
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = requests_db[request_id]
    
    # Remove from agent's current_requests
    if request.agent_id and request.agent_id in agents_db:
        agent = agents_db[request.agent_id]
        if request_id in agent.current_requests:
            agent.current_requests.remove(request_id)
    
    del requests_db[request_id]
    return {"message": "Request deleted successfully"}

@app.get("/stats")
async def get_stats():
    total_capacity = sum(a.max_requests for a in agents_db.values())
    total_assigned = sum(len(a.current_requests) for a in agents_db.values())
    
    return {
        "total_agents": len(agents_db),
        "total_requests": len(requests_db),
        "total_capacity": total_capacity,
        "total_assigned": total_assigned,
        "available_capacity": total_capacity - total_assigned
    }

# For Vercel serverless
handler = Mangum(app, lifespan="off")
