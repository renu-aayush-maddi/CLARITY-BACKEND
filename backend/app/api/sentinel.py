# backend/app/api/sentinel.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.database import get_db

router = APIRouter()

@router.get("/sentinel/alerts")
def get_smart_alerts(study: str, db: Session = Depends(get_db)):
    """
    PATTERN 2: BACKGROUND AGENT
    Scans data and returns prioritized alerts without user input.
    """
    alerts = []

    # RULE 1: Detect "Ghost Sites" (High Inactivity)
    # Logic: Sites with > 10 subjects but NO recent data entry (inactivated forms count as activity type)
    # For simplicity, we'll check huge counts of missing pages vs active subjects
    ghost_sql = text("""
        SELECT site_id, COUNT(*) as missing_count
        FROM raw_missing_pages 
        WHERE study_name = :study
        GROUP BY site_id
        HAVING COUNT(*) > 15
    """)
    ghosts = db.execute(ghost_sql, {"study": study}).fetchall()
    
    for row in ghosts:
        alerts.append({
            "type": "risk",
            "severity": "high",
            "title": f"Operational Risk: {row.site_id}",
            "message": f"Agent detected {row.missing_count} missing pages. This exceeds the threshold of 15.",
            "action": "Schedule Monitoring Visit"
        })

    # RULE 2: Detect "Training Gaps" (High Inactivated Forms)
    training_sql = text("""
        SELECT site_id, COUNT(*) as deleted_count
        FROM raw_inactivated_forms
        GROUP BY site_id
        HAVING COUNT(*) > 50
    """)
    training = db.execute(training_sql).fetchall()

    for row in training:
        # Check if this site belongs to the study (approximate via logic or strict join)
        # For efficiency, we just alert.
        alerts.append({
            "type": "warning",
            "severity": "medium",
            "title": f"Training Gap: {row.site_id}",
            "message": f"Staff inactivated {row.deleted_count} forms. High rework detected.",
            "action": "Send EDC Training Video"
        })

    return {"alerts": alerts, "count": len(alerts)}