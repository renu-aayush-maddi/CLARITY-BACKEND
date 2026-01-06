import pandas as pd
from thefuzz import process

TARGET_SCHEMA = {
    "site_id": ["site id", "site number", "site no", "investigator site", "site", "study site number", "site_id"],
    "subject_id": ["subject id", "subject name", "patient id", "subject no", "subject", "participant id", "patient_id"],
    "study_name": ["project name", "study", "protocol id", "protocol", "study id"],
    "visit_date": ["visit date", "date of visit", "collection date", "visit dt", "assessment date"],
    "projected_date": ["projected date", "due date", "expected date"],
    "form_name": ["form name", "form", "crf name", "ecrf name", "page name", "folder name", "data page name"],
    "folder_name": ["folder", "visit name", "visit"],
    "days_outstanding": ["# days outstanding", "days outstanding", "# days outstanding (today - projected date)", "days overdue"],
    "days_missing": ["no. #days page missing", "# of days missing", "# days page missing", "missing pages", "days missing", "# days"],
    "test_name": ["test name", "analyte", "lab test", "test description"],
    "lab_category": ["lab category", "category", "panel"],
    "status": ["status", "state", "overall subject status", "subject status", "case status"],
    "query_text": ["query text", "marking group", "query string", "description"],
    "audit_action": ["audit action", "action", "reason"],
    # Added to fix 'CPID Metrics' detection
    "missing_visits": ["missing visits", "# missing visits", "number of missing visits"] 
}

def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    rename_map = {}
    original_cols = df.columns.tolist()

    for col in original_cols:
        col_lower = col.lower()
        best_match_score = 0
        best_target = None

        for target_key, keywords in TARGET_SCHEMA.items():
            match, score = process.extractOne(col_lower, keywords)
            if score > 88: 
                if score > best_match_score:
                    best_match_score = score
                    best_target = target_key

        if best_target:
            rename_map[col] = best_target

    if rename_map:
        df = df.rename(columns=rename_map)
    return df