
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

# Import models so SQLAlchemy registers the table
import models

from routes import router

from exceptions import register_exception_handlers


# Application startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables for local development
    Base.metadata.create_all(bind=engine)

    try:
        yield

    finally:
        engine.dispose()


# Initialize FastAPI
app = FastAPI(
    title="Student Management API",
    description="CRUD APIs using FastAPI and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5502",
        "http://localhost:5502"
    ],

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS"
    ],

    allow_headers=["Content-Type"]
)


# Register exception handlers
register_exception_handlers(app)


# Register student routes
app.include_router(router)


# Basic application endpoint
@app.get("/")
def home():

    return {
        "message": "Student Management API is running"
    }
