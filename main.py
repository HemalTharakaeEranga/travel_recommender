from pathlib import Path
import importlib, pkgutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env", override=True)

app = FastAPI(title="Travel-Recommender API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


for m in pkgutil.iter_modules(["backend"]):
    mod = importlib.import_module(f"backend.{m.name}")
    if hasattr(mod, "router"):
        app.include_router(mod.router, prefix="/api")
