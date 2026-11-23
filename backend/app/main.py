
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine
from app import models

from app.api.upload import router as upload_router
from app.database import engine
from app.api.history import router as history_router

app = FastAPI(
    title="InsightIQ API",
    description="AI-powered automated data analytics platform",
    version="1.0.0"
)

@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    upload_router,
    prefix="/api",
    tags=["Data Upload"]
)

app.include_router(
    history_router,
    prefix="/api",
    tags=["Analysis History"]
)

@app.get("/")
def home():
    return {
        "message": "Welcome to InsightIQ API",
        "status": "running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "application": "InsightIQ"
    }


@app.get("/api/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": "InsightIQ",
            "message": "PostgreSQL connection successful."
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL database connection failed. Check your database configuration."
        )
