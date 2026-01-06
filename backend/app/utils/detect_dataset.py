# backend/app/utils/detect_dataset.py
import pandas as pd

def detect_dataset_type(df: pd.DataFrame, sheet_name: str = "") -> str:
    """
    Identifies the dataset type based on sheet name OR content keywords.
    """
    # 1. Check Sheet Name (Fastest)
    s_name = str(sheet_name).lower()
    if "subject level metrics" in s_name: return "raw_cpid_metrics"
    if "protocol deviation" in s_name: return "raw_protocol_deviations"
    if "sae dashboard" in s_name: return "raw_sae_issues"
    
    # 2. Check Content (Scans first 20 rows for keywords)
    # Convert top 20 rows to a single lowercase string for searching
    sample_text = df.head(20).to_string().lower()

    if "projected date" in sample_text and "outstanding" in sample_text:
        return "raw_visit_projections"
    
    if "missing lab name" in sample_text or "lab category" in sample_text:
        return "raw_lab_issues"
    
    if "no. #days page missing" in sample_text:
        return "raw_missing_pages"
        
    if "audit action" in sample_text and "recordposition" in sample_text:
        return "raw_inactivated_forms"

    if "total open issue count" in sample_text:
        return "raw_edrr_issues"

    if "discrepancy id" in sample_text and "action status" in sample_text:
        return "raw_sae_issues"

    return None