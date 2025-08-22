import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import analysis, email, firstAI

app = FastAPI(
    title="Python AI Tutoriles",
    description="Project to learn AI using python & FastAPI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(firstAI.router, prefix=settings.API_PREFIX)
app.include_router(email.router, prefix=settings.API_PREFIX)
app.include_router(analysis.route, prefix=settings.API_PREFIX)

# Get keys for your project from the project settings page: https://cloud.langfuse.com
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-cda6714d-37ac-499f-8c4a-782016b1eba8"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-c29bb63b-6571-4087-b1d5-a0fa5247a5fb"
os.environ["LANGFUSE_HOST"] = "http://localhost:5000"

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
