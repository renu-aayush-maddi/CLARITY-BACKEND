from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
import os
import time  # <--- Time tracking
from backend.app.core.database import get_db
from backend.app.api.analytics import log_ai_interaction  # <--- Import Logger

# SDK IMPORTS
from google import genai
from openai import OpenAI

load_dotenv()
router = APIRouter()

# --- CONFIGURATION ---
AI_PROVIDER = os.getenv("AI_PROVIDER", "google").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

gemini_client = None
openai_client = None

# Initialize Client based on Provider
if AI_PROVIDER == "google" and GOOGLE_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"⚠️ Gemini Chat Init Error: {e}")

elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"⚠️ OpenAI Chat Init Error: {e}")

class ChatRequest(BaseModel):
    message: str
    study: str

# 🚀 FINAL CORRECT SCHEMA (MATCHING YOUR DIAGNOSTIC REPORT)
SCHEMA_INFO = """
Tables & Columns:
1. subjects 
   - Columns: subject_id (text), site_id (text), status (text), study_name (text)
   - NOTE: Use this table to filter by study_name for tables that don't have it.

2. raw_missing_pages
   - Columns: subject_id (text), site_id (text), form_name (text), days_missing (int), study_name (text)
   - NOTE: Has 'study_name'. No join needed.

3. raw_inactivated_forms
   - Columns: subject_id (text), site_id (text), folder_name (text), form_name (text), audit_action (text)
   - NOTE: NO 'study_name' column. You MUST JOIN 'subjects' on subject_id to filter by study.

4. raw_lab_issues
   - Columns: subject_id (text), site_id (text), lab_category (text), test_name (text)
   - NOTE: NO 'study_name' column. You MUST JOIN 'subjects' on subject_id to filter by study.

5. raw_visit_projections
   - Columns: subject_id (text), site_id (text), visit_name (text), projected_date (text), days_outstanding (int), study_name (text)
   - NOTE: Has 'study_name'. No join needed.
"""

def generate_ai_response(prompt):
    """Helper to call the correct AI provider"""
    if AI_PROVIDER == "openai" and openai_client:
        response = openai_client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are a helpful SQL assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    elif AI_PROVIDER == "google" and gemini_client:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    else:
        raise Exception("AI Provider not configured correctly.")

@router.post("/chat/query")
def chat_with_data(req: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    # STEP 1: Generate SQL
    prompt = f"""
    You are a PostgreSQL expert. Write a SQL query to answer: "{req.message}"
    Context: Study '{req.study}'. 
    Schema: 
    {SCHEMA_INFO}
    
    CRITICAL RULES:
    1. 'site_id' is TEXT (e.g., 'Site 19'). NEVER use integers (site_id = 19 is WRONG).
       - Correct: site_id = 'Site 19' OR site_id ILIKE '%Site 19%'
    2. JOIN RULES:
       - If querying 'raw_inactivated_forms' or 'raw_lab_issues', you MUST JOIN 'subjects' s ON t.subject_id = s.subject_id 
         to filter by s.study_name = '{req.study}'.
       - If querying 'raw_missing_pages' or 'raw_visit_projections', just use WHERE study_name = '{req.study}'.
    3. Return ONLY the raw SQL string. No markdown.
    """
    
    try:
        raw_response = generate_ai_response(prompt)
        sql_query = raw_response.strip().replace("```sql", "").replace("```", "")
        
        # --- 1. LOG SUCCESSFUL GENERATION ---
        duration = round((time.time() - start_time) * 1000)
        log_ai_interaction(
            agent_name="SQL Agent",
            input_text=req.message,
            output_text=sql_query,
            latency_ms=duration,
            status="Success"
        )
        
        if not sql_query.upper().startswith("SELECT"):
            return {"response": "I can only perform read operations (SELECT)."}
            
    except Exception as e:
        # --- 2. LOG ERROR GENERATION ---
        duration = round((time.time() - start_time) * 1000)
        log_ai_interaction(
            agent_name="SQL Agent",
            input_text=req.message,
            output_text=f"Error: {str(e)}",
            latency_ms=duration,
            status="Error"
        )
        return {"response": f"Error generating query: {str(e)}"}

    # STEP 2: Execute SQL
    try:
        rows = db.execute(text(sql_query)).fetchall()
        
        if not rows:
            return {"response": f"No records found for that query in {req.study}.", "sql": sql_query}
            
        data_str = str(rows[:10]) 
    except Exception as e:
        return {"response": f"SQL Error: {str(e)}", "sql": sql_query}

    # STEP 3: Summarize Results
    summary_prompt = f"""
    User Question: {req.message}
    Data Found: {data_str}
    
    Answer the user concisely in plain English. 
    If it's a list, summarize the top 3 items.
    """
    
    try:
        final_res = generate_ai_response(summary_prompt)
        return {"response": final_res, "sql": sql_query}
    except:
        return {"response": f"Data found: {data_str}", "sql": sql_query}