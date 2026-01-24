from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Agent Load Balancer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Agent(BaseModel):
    id: str
    name: str
    max_requests: int = Field(default=2, ge=1)
    current_requests: List[str] = Field(default_factory=list)
    
    @property
    def available_capacity(self) -> int:
        return self.max_requests - len(self.current_requests)
    
    @property
    def is_available(self) -> bool:
        return len(self.current_requests) < self.max_requests


class Request(BaseModel):
    id: str
    customer_name: str
    description: str
    assigned_agent_id: Optional[str] = None
    status: str = "pending"  # pending, processing, completed
    created_at: datetime
    completed_at: Optional[datetime] = None


class CreateAgentRequest(BaseModel):
    name: str
    max_requests: int = Field(default=2, ge=1)


class CreateRequestRequest(BaseModel):
    customer_name: str
    description: str


class CompleteRequestRequest(BaseModel):
    request_id: str


# In-memory storage (use a database in production)
agents_db: dict[str, Agent] = {}
requests_db: dict[str, Request] = {}


@app.get("/")
async def root():
    return {"message": "Agent Load Balancer API", "version": "1.0"}


@app.post("/agents", response_model=Agent)
async def create_agent(agent_request: CreateAgentRequest):
    """Create a new agent with specified max request capacity"""
    agent_id = str(uuid.uuid4())
    agent = Agent(
        id=agent_id,
        name=agent_request.name,
        max_requests=agent_request.max_requests,
        current_requests=[]
    )
    agents_db[agent_id] = agent
    return agent


@app.get("/agents", response_model=List[Agent])
async def get_agents():
    """Get all agents"""
    return list(agents_db.values())


@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get a specific agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    if len(agent.current_requests) > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete agent with active requests. Agent has {len(agent.current_requests)} active request(s)"
        )
    
    del agents_db[agent_id]
    return {"message": "Agent deleted successfully"}


def find_most_available_agent() -> Optional[Agent]:
    """Find the agent with the most available capacity"""
    available_agents = [agent for agent in agents_db.values() if agent.is_available]
    
    if not available_agents:
        return None
    
    # Sort by available capacity (descending) and then by number of current requests (ascending)
    most_available = max(available_agents, key=lambda a: a.available_capacity)
    return most_available


@app.post("/requests", response_model=Request)
async def create_request(request_data: CreateRequestRequest):
    """Create a new customer request and assign to most available agent"""
    # Find the most available agent
    agent = find_most_available_agent()
    
    if not agent:
        raise HTTPException(
            status_code=503, 
            detail="No available agents. All agents are at capacity."
        )
    
    # Create the request
    request_id = str(uuid.uuid4())
    request = Request(
        id=request_id,
        customer_name=request_data.customer_name,
        description=request_data.description,
        assigned_agent_id=agent.id,
        status="processing",
        created_at=datetime.utcnow()
    )
    
    # Assign request to agent
    agent.current_requests.append(request_id)
    requests_db[request_id] = request
    
    return request


@app.get("/requests", response_model=List[Request])
async def get_requests():
    """Get all requests"""
    return list(requests_db.values())


@app.get("/requests/{request_id}", response_model=Request)
async def get_request(request_id: str):
    """Get a specific request"""
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")
    return requests_db[request_id]


@app.post("/requests/{request_id}/complete")
async def complete_request(request_id: str):
    """Mark a request as completed and remove from agent's list"""
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request = requests_db[request_id]
    
    if request.status == "completed":
        raise HTTPException(status_code=400, detail="Request already completed")
    
    # Update request status
    request.status = "completed"
    request.completed_at = datetime.utcnow()
    
    # Remove from agent's current requests
    if request.assigned_agent_id and request.assigned_agent_id in agents_db:
        agent = agents_db[request.assigned_agent_id]
        if request_id in agent.current_requests:
            agent.current_requests.remove(request_id)
    
    return request


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    total_agents = len(agents_db)
    total_requests = len(requests_db)
    active_requests = sum(1 for r in requests_db.values() if r.status == "processing")
    completed_requests = sum(1 for r in requests_db.values() if r.status == "completed")
    
    available_capacity = sum(agent.available_capacity for agent in agents_db.values())
    total_capacity = sum(agent.max_requests for agent in agents_db.values())
    
    return {
        "total_agents": total_agents,
        "total_requests": total_requests,
        "active_requests": active_requests,
        "completed_requests": completed_requests,
        "available_capacity": available_capacity,
        "total_capacity": total_capacity,
        "utilization": round((total_capacity - available_capacity) / total_capacity * 100, 2) if total_capacity > 0 else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
