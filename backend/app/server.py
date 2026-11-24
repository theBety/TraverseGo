# Inicializes FastAPI, database and routers (APIs)

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import trails

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    
app = FastAPI(
    title="TraverseGo API",
    description="Backend API for TraverseGo app",
    version="0.1.0",
    lifespan=lifespan, 
)

app.include_router(trails.router)