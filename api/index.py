from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any
import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Storage layer - uses Vercel KV, Upstash Redis, or in-memory
class Storage:
    def __init__(self):
        # Try Vercel KV first
        self.kv_url = os.getenv("KV_REST_API_URL")
        self.kv_token = os.getenv("KV_REST_API_TOKEN")
        
        # Fallback to Upstash Redis
        if not self.kv_url:
            self.kv_url = os.getenv("UPSTASH_REDIS_REST_URL")
            self.kv_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        self.memory_agents = {}
        self.memory_requests = {}

    async def get_agents(self) -> Dict[str, Any]:
        if self.kv_url and self.kv_token:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.kv_url}/get/agents",
                        headers={"Authorization": f"Bearer {self.kv_token}"},
                    )
                    if response.status_code == 200:
                        result = response.json().get("result")
                        return json.loads(result) if result else {}
            except Exception as e:
                print(f"KV error: {e}")
        return self.memory_agents

    async def set_agents(self, agents: Dict[str, Any]):
        if self.kv_url and self.kv_token:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.kv_url}/set/agents",
                        headers={"Authorization": f"Bearer {self.kv_token}"},
                        json={"value": json.dumps(agents)},
                    )
            except Exception as e:
                print(f"KV error: {e}")
        self.memory_agents = agents

    async def get_requests(self) -> Dict[str, Any]:
        if self.kv_url and self.kv_token:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.kv_url}/get/requests",
                        headers={"Authorization": f"Bearer {self.kv_token}"},
                    )
                    if response.status_code == 200:
                        result = response.json().get("result")
                        return json.loads(result) if result else {}
            except Exception as e:
                print(f"KV error: {e}")
        return self.memory_requests

    async def set_requests(self, requests: Dict[str, Any]):
        if self.kv_url and self.kv_token:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.kv_url}/set/requests",
                        headers={"Authorization": f"Bearer {self.kv_token}"},
                        json={"value": json.dumps(requests)},
                    )
            except Exception as e:
                print(f"KV error: {e}")
        self.memory_requests = requests


storage = Storage()


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


app = FastAPI(title="Agent Load Balancer API", root_path="/api")

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
    agents_db = await storage.get_agents()
    return list(agents_db.values())


@app.post("/agents", response_model=Agent)
async def create_agent(agent_data: CreateAgent):
    agents_db = await storage.get_agents()
    agent = Agent(name=agent_data.name, max_requests=agent_data.max_requests)
    agents_db[agent.id] = agent.dict()
    await storage.set_agents(agents_db)
    return agent


@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    agents_db = await storage.get_agents()
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    agents_db = await storage.get_agents()
    requests_db = await storage.get_requests()

    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Remove all requests assigned to this agent
    for req_id, req in requests_db.items():
        if req.get("agent_id") == agent_id:
            req["agent_id"] = None
            req["status"] = "pending"

    del agents_db[agent_id]
    await storage.set_agents(agents_db)
    await storage.set_requests(requests_db)
    return {"message": "Agent deleted successfully"}


@app.get("/requests", response_model=List[Request])
async def list_requests():
    requests_db = await storage.get_requests()
    return list(requests_db.values())


@app.post("/requests", response_model=Request)
async def create_request(request_data: CreateRequest):
    agents_db = await storage.get_agents()
    requests_db = await storage.get_requests()

    request = Request(
        customer_name=request_data.customer_name,
        description=request_data.description,
        status="pending",
    )

    # Find the most available agent
    best_agent_id = None
    min_load = float("inf")

    for agent_id, agent_data in agents_db.items():
        current_count = len(agent_data.get("current_requests", []))

        if current_count >= agent_data.get("max_requests", 2):
            continue

        if current_count < min_load:
            min_load = current_count
            best_agent_id = agent_id

    # Assign to best agent if found
    if best_agent_id:
        request.agent_id = best_agent_id
        request.status = "assigned"
        agents_db[best_agent_id]["current_requests"].append(request.id)

    requests_db[request.id] = request.dict()
    await storage.set_agents(agents_db)
    await storage.set_requests(requests_db)
    return request


@app.get("/requests/{request_id}", response_model=Request)
async def get_request(request_id: str):
    requests_db = await storage.get_requests()
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")
    return requests_db[request_id]


@app.post("/requests/{request_id}/complete")
async def complete_request(request_id: str):
    agents_db = await storage.get_agents()
    requests_db = await storage.get_requests()

    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")

    request = requests_db[request_id]
    request["status"] = "completed"
    request["completed_at"] = datetime.utcnow().isoformat()

    # Remove from agent's current_requests
    agent_id = request.get("agent_id")
    if agent_id and agent_id in agents_db:
        agent = agents_db[agent_id]
        if request_id in agent.get("current_requests", []):
            agent["current_requests"].remove(request_id)

    await storage.set_agents(agents_db)
    await storage.set_requests(requests_db)
    return request


@app.delete("/requests/{request_id}")
async def delete_request(request_id: str):
    agents_db = await storage.get_agents()
    requests_db = await storage.get_requests()

    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="Request not found")

    request = requests_db[request_id]

    # Remove from agent's current_requests
    agent_id = request.get("agent_id")
    if agent_id and agent_id in agents_db:
        agent = agents_db[agent_id]
        if request_id in agent.get("current_requests", []):
            agent["current_requests"].remove(request_id)

    del requests_db[request_id]
    await storage.set_agents(agents_db)
    await storage.set_requests(requests_db)
    return {"message": "Request deleted successfully"}


@app.get("/stats")
async def get_stats():
    agents_db = await storage.get_agents()
    requests_db = await storage.get_requests()

    total_capacity = sum(a.get("max_requests", 2) for a in agents_db.values())
    total_assigned = sum(len(a.get("current_requests", [])) for a in agents_db.values())

    return {
        "total_agents": len(agents_db),
        "total_requests": len(requests_db),
        "total_capacity": total_capacity,
        "total_assigned": total_assigned,
        "available_capacity": total_capacity - total_assigned,
    }
