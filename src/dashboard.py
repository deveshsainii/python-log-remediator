from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from state_manager import StateManager
import uvicorn
import os

app = FastAPI(title="Log Analysis & Auto-Remediation Dashboard")
state = StateManager()

# Setup templates
templates = Jinja2Templates(directory="src/templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stats")
async def get_stats():
    return state.get_snapshot()

def run_dashboard(port: int = 8080):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
