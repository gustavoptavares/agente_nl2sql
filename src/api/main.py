from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

from src.api.routers import nl2sql_router
from src.config import settings

os.environ["LANGCHAIN_TRACING_V2"] = "true"
if settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT

app = FastAPI(
    title="NL2SQL POC API",
    version="1.0.0",
    description="API para conversão de linguagem natural para SQL"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nl2sql_router.router, prefix="/api/v1", tags=["NL2SQL"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "NL2SQL API",
        "docs": "/docs",
        "health": "/health"
    }