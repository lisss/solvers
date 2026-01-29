from datetime import datetime
import os
import uuid
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

# Storage layer - inline to avoid import issues on Vercel
KV_URL = os.environ.get("KV_REST_API_URL") or os.environ.get("KV_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN")
USE_KV = KV_URL and KV_TOKEN

if USE_KV:
    try:
        from upstash_redis import Redis

        kv = Redis(url=KV_URL, token=KV_TOKEN)
        print("✅ Using Vercel KV - data will persist!")
    except Exception as e:
        print(f"⚠️  KV connection failed: {e}, falling back to in-memory")
        USE_KV = False
        kv = None
else:
    kv = None
    print("⚠️  No KV configured - data will be inconsistent on Vercel")


class Storage:
    """Simple key-value storage"""

    def __init__(self):
        if not USE_KV:
            self._memory = {}

    def set(self, key: str, value: str) -> None:
        if USE_KV:
            kv.set(key, value)
        else:
            self._memory[key] = value

    def get(self, key: str) -> Optional[str]:
        if USE_KV:
            result = kv.get(key)
            return result.decode() if isinstance(result, bytes) else result
        else:
            return self._memory.get(key)

    def delete(self, key: str) -> None:
        if USE_KV:
            kv.delete(key)
        else:
            self._memory.pop(key, None)

    def keys(self, pattern: str = "*") -> List[str]:
        if USE_KV:
            keys = kv.keys(pattern)
            return [k.decode() if isinstance(k, bytes) else k for k in keys]
        else:
            if pattern == "*":
                return list(self._memory.keys())
            prefix = pattern.replace("*", "")
            return [k for k in self._memory.keys() if k.startswith(prefix)]


storage = Storage()


# Initialize app
app = FastAPI(
    title="Agent Load Balancer API",
    root_path="/api",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class Agent(BaseModel):
    id: str
    name: str
    max_requests: int = Field(default=2, ge=1)
    current_requests: List[str] = Field(default_factory=list)


class Request(BaseModel):
    id: str
    customer_name: str
    description: str
    assigned_agent_id: Optional[str] = None
    status: str = "pending"
    created_at: datetime
    completed_at: Optional[datetime] = None


class CreateAgentRequest(BaseModel):
    name: str
    max_requests: int = Field(default=2, ge=1)


class CreateRequestRequest(BaseModel):
    customer_name: str
    description: str


# No startup needed - storage is ready to use!


# Helper functions
def get_agent(agent_id: str) -> Optional[Agent]:
    """Get agent by ID from storage"""
    data = storage.get(f"agent:{agent_id}")
    if not data:
        return None
    agent_dict = json.loads(data)
    # Get current requests
    current_requests = []
    for req_key in storage.keys(f"request:*"):
        req_data = storage.get(req_key)
        if req_data:
            req = json.loads(req_data)
            if req.get("assigned_agent_id") == agent_id and req.get("status") == "processing":
                current_requests.append(req["id"])
    agent_dict["current_requests"] = current_requests
    return Agent(**agent_dict)


def list_agents() -> List[Agent]:
    """List all agents from storage"""
    agents = []
    for key in storage.keys("agent:*"):
        agent_id = key.replace("agent:", "")
        agent = get_agent(agent_id)
        if agent:
            agents.append(agent)
    return agents


def find_most_available_agent() -> Optional[Agent]:
    """Find agent with most available capacity"""
    agents = list_agents()
    if not agents:
        return None

    available_agents = [a for a in agents if len(a.current_requests) < a.max_requests]
    if not available_agents:
        return None

    return max(available_agents, key=lambda a: a.max_requests - len(a.current_requests))


# Routes
@app.get("/")
async def root():
    return {"message": "Agent Load Balancer API", "version": "1.0"}


@app.post("/agents", response_model=Agent)
async def create_agent(agent_request: CreateAgentRequest):
    agent_id = str(uuid.uuid4())
    agent_data = {
        "id": agent_id,
        "name": agent_request.name,
        "max_requests": agent_request.max_requests,
        "current_requests": [],
    }
    storage.set(f"agent:{agent_id}", json.dumps(agent_data))
    return Agent(**agent_data)


@app.get("/agents", response_model=List[Agent])
async def get_agents():
    return list_agents()


@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent_by_id(agent_id: str):
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if len(agent.current_requests) > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete agent with active requests. Agent has {len(agent.current_requests)} active request(s)",
        )

    storage.delete(f"agent:{agent_id}")
    return {"message": "Agent deleted successfully"}


@app.post("/requests", response_model=Request)
async def create_request(request_data: CreateRequestRequest):
    agent = find_most_available_agent()
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="No available agents. All agents are at capacity.",
        )

    request_id = str(uuid.uuid4())
    request_obj = {
        "id": request_id,
        "customer_name": request_data.customer_name,
        "description": request_data.description,
        "assigned_agent_id": agent.id,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
    }
    storage.set(f"request:{request_id}", json.dumps(request_obj))
    return Request(**request_obj)


@app.get("/requests", response_model=List[Request])
async def get_requests():
    requests = []
    for key in storage.keys("request:*"):
        data = storage.get(key)
        if data:
            req_dict = json.loads(data)
            requests.append(Request(**req_dict))
    return requests


@app.get("/requests/{request_id}", response_model=Request)
async def get_request(request_id: str):
    data = storage.get(f"request:{request_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Request not found")
    return Request(**json.loads(data))


@app.post("/requests/{request_id}/complete")
async def complete_request(request_id: str):
    data = storage.get(f"request:{request_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Request not found")

    req_dict = json.loads(data)
    if req_dict["status"] == "completed":
        raise HTTPException(status_code=400, detail="Request already completed")

    req_dict["status"] = "completed"
    req_dict["completed_at"] = datetime.utcnow().isoformat()
    storage.set(f"request:{request_id}", json.dumps(req_dict))

    return Request(**req_dict)


@app.get("/stats")
async def get_stats():
    agents = list_agents()
    total_agents = len(agents)

    requests = []
    for key in storage.keys("request:*"):
        data = storage.get(key)
        if data:
            requests.append(json.loads(data))

    total_requests = len(requests)
    active_requests = len([r for r in requests if r["status"] == "processing"])
    completed_requests = len([r for r in requests if r["status"] == "completed"])

    total_capacity = sum(a.max_requests for a in agents)
    available_capacity = sum(a.max_requests - len(a.current_requests) for a in agents)

    return {
        "total_agents": total_agents,
        "total_requests": total_requests,
        "active_requests": active_requests,
        "completed_requests": completed_requests,
        "available_capacity": available_capacity,
        "total_capacity": total_capacity,
        "utilization": (
            round((total_capacity - available_capacity) / total_capacity * 100, 2)
            if total_capacity > 0
            else 0
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
