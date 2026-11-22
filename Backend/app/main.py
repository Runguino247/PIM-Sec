from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.fim.scheduler import start_scheduler

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://tudominio.com",
    "http://localhost:5173"
]

app = FastAPI(
    title="PIM-Sec API",
    description="Sistema de monitoreo de integridad de archivos mediante SHA-256",
    version="1.0.0"
)

# Configurar CORS para permitir el Frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:8000"], # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "PIM-Sec API is running"}

@app.on_event("startup")
def startup_event():
    start_scheduler()