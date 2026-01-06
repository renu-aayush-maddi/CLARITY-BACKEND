
# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, Form, Depends # <--- Added Form
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.utils.ingest_excel import ingest_file
from fastapi.middleware.cors import CORSMiddleware

# --- Import the new analytics router ---
from backend.app.api import analytics,agent, chat,sentinel

app = FastAPI()

# --- CORS BLOCK ---
origins = [
    "http://localhost:5173",  # React (Vite) default port
    "http://localhost:3000",  # React (Create-React-App) default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------

# --- Register Routes ---
app.include_router(analytics.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(sentinel.router, prefix="/api")

@app.post("/api/upload")
async def upload_files(
    study_name: Optional[str] = Form(None), # <--- NEW: capture study name from Form Data
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    """
    Uploads any number of Excel/CSV files.
    - If study_name is provided (Recommended), all files are tagged with it.
    - If not provided, the system tries to guess from filename/content (Fallback).
    """
    upload_results = []
    
    for file in files:
        # Pass the captured study_name to your logic
        result = ingest_file(file, db, study_name=study_name) 
        upload_results.append(result)
        
    return {"summary": upload_results}

@app.get("/")
def health_check():
    return {"status": "Clarity AI Backend is Online"}