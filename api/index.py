from datetime import datetime
import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Dict, List, Optional

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database models
class AgentModel(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    max_requests = Column(Integer, nullable=False, default=2)


class RequestModel(Base):
    __tablename__ = "requests"
    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    assigned_agent_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)


# Initialize app
app = FastAPI(title="Agent Load Balancer API", root_path="/api", )

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


# Startup event
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# Helper functions
def agent_current_requests(db, agent_id: str) -> List[str]:
    return [
        r.id
        for r in db.query(RequestModel)
        .filter(
            RequestModel.assigned_agent_id == agent_id,
            RequestModel.status == "processing",
        )
        .all()
    ]


def serialize_agent(db, agent: AgentModel) -> Agent:
    current = agent_current_requests(db, agent.id)
    return Agent(
        id=agent.id,
        name=agent.name,
        max_requests=agent.max_requests,
        current_requests=current,
    )


def find_most_available_agent(db) -> Optional[AgentModel]:
    agents = db.query(AgentModel).all()
    if not agents:
        return None

    availability: Dict[str, int] = {}
    for agent in agents:
        active_count = (
            db.query(RequestModel)
            .filter(
                RequestModel.assigned_agent_id == agent.id,
                RequestModel.status == "processing",
            )
            .count()
        )
        availability[agent.id] = agent.max_requests - active_count

    available_agents = [a for a in agents if availability.get(a.id, 0) > 0]
    if not available_agents:
        return None

    return max(available_agents, key=lambda a: availability.get(a.id, 0))


# Routes
@app.get("/")
async def root():
    return {"message": "Agent Load Balancer API", "version": "1.0"}


@app.post("/agents", response_model=Agent)
async def create_agent(agent_request: CreateAgentRequest):
    agent_id = str(uuid.uuid4())
    with SessionLocal() as db:
        agent = AgentModel(
            id=agent_id,
            name=agent_request.name,
            max_requests=agent_request.max_requests,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return serialize_agent(db, agent)


@app.get("/agents", response_model=List[Agent])
async def get_agents():
    with SessionLocal() as db:
        agents = db.query(AgentModel).all()
        return [serialize_agent(db, agent) for agent in agents]


@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    with SessionLocal() as db:
        agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return serialize_agent(db, agent)


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    with SessionLocal() as db:
        agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        active_count = (
            db.query(RequestModel)
            .filter(
                RequestModel.assigned_agent_id == agent_id,
                RequestModel.status == "processing",
            )
            .count()
        )
        if active_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete agent with active requests. Agent has {active_count} active request(s)",
            )

        db.delete(agent)
        db.commit()
        return {"message": "Agent deleted successfully"}


@app.post("/requests", response_model=Request)
async def create_request(request_data: CreateRequestRequest):
    with SessionLocal() as db:
        agent = find_most_available_agent(db)
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="No available agents. All agents are at capacity.",
            )

        request_id = str(uuid.uuid4())
        request = RequestModel(
            id=request_id,
            customer_name=request_data.customer_name,
            description=request_data.description,
            assigned_agent_id=agent.id,
            status="processing",
            created_at=datetime.utcnow(),
        )
        db.add(request)
        db.commit()
        db.refresh(request)

        return Request(
            id=request.id,
            customer_name=request.customer_name,
            description=request.description,
            assigned_agent_id=request.assigned_agent_id,
            status=request.status,
            created_at=request.created_at,
            completed_at=request.completed_at,
        )


@app.get("/requests", response_model=List[Request])
async def get_requests():
    with SessionLocal() as db:
        requests = db.query(RequestModel).all()
        return [
            Request(
                id=r.id,
                customer_name=r.customer_name,
                description=r.description,
                assigned_agent_id=r.assigned_agent_id,
                status=r.status,
                created_at=r.created_at,
                completed_at=r.completed_at,
            )
            for r in requests
        ]


@app.get("/requests/{request_id}", response_model=Request)
async def get_request(request_id: str):
    with SessionLocal() as db:
        request = db.query(RequestModel).filter(RequestModel.id == request_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        return Request(
            id=request.id,
            customer_name=request.customer_name,
            description=request.description,
            assigned_agent_id=request.assigned_agent_id,
            status=request.status,
            created_at=request.created_at,
            completed_at=request.completed_at,
        )


@app.post("/requests/{request_id}/complete")
async def complete_request(request_id: str):
    with SessionLocal() as db:
        request = db.query(RequestModel).filter(RequestModel.id == request_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        if request.status == "completed":
            raise HTTPException(status_code=400, detail="Request already completed")

        request.status = "completed"
        request.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(request)

        return Request(
            id=request.id,
            customer_name=request.customer_name,
            description=request.description,
            assigned_agent_id=request.assigned_agent_id,
            status=request.status,
            created_at=request.created_at,
            completed_at=request.completed_at,
        )


@app.get("/stats")
async def get_stats():
    with SessionLocal() as db:
        total_agents = db.query(AgentModel).count()
        total_requests = db.query(RequestModel).count()
        active_requests = db.query(RequestModel).filter(RequestModel.status == "processing").count()
        completed_requests = (
            db.query(RequestModel).filter(RequestModel.status == "completed").count()
        )

        agents = db.query(AgentModel).all()
        available_capacity = 0
        total_capacity = 0
        for agent in agents:
            total_capacity += agent.max_requests
            active_count = (
                db.query(RequestModel)
                .filter(
                    RequestModel.assigned_agent_id == agent.id,
                    RequestModel.status == "processing",
                )
                .count()
            )
            available_capacity += max(agent.max_requests - active_count, 0)

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
