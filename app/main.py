from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import init_db
from app.routes import auth_routes, calculation_routes

app = FastAPI(
    title="Calculations API",
    description="BREAD operations for calculations with user authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()

# Include routers
app.include_router(auth_routes.router)
app.include_router(calculation_routes.router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root endpoint
@app.get("/")
def read_root():
    static_index = os.path.join(static_dir, "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {
        "message": "Calculations API",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "calculations": "/calculations"
        }
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}
