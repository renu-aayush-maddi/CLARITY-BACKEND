

# backend/app/utils/dataset_registry.py
DATASET_SPECS = {
    "raw_cpid_metrics": {
        # Note: 'missing_visits' must match TARGET_SCHEMA key above
        "required_columns": ["subject_id", "missing_visits"], 
        "table": "raw_cpid_metrics"
    },
    "raw_protocol_deviations": {
        "required_columns": ["pd_status", "visit_date"],
        "table": "raw_protocol_deviations"
    },
    "raw_visit_projections": {
        "required_columns": ["projected_date", "days_outstanding"],
        "table": "raw_visit_projections"
    },
    "raw_lab_issues": {
        "required_columns": ["lab_category", "test_name"],
        "table": "raw_lab_issues"
    },
    "raw_sae_safety": {
        "required_columns": ["case_status", "review_status"],
        "table": "raw_sae_safety"
    },
    "raw_sae_dm": {
        "required_columns": ["discrepancy_id", "action_status"],
        "table": "raw_sae_dm"
    },
    "raw_coding_meddra": {
        "required_columns": ["coding_status", "term"],
        "table": "raw_coding_meddra"
    },
    "raw_coding_whodra": {
        "required_columns": ["coding_status", "trade_name"],
        "table": "raw_coding_whodra"
    },
    "raw_missing_pages": {
        "required_columns": ["days_missing", "form_name", "visit_date"], 
        "table": "raw_missing_pages"
    },
    "raw_inactivated_forms": {
        "required_columns": ["audit_action", "folder_name"],
        "table": "raw_inactivated_forms"
    },
    "raw_edrr_issues": {
        "required_columns": ["issue_count"], 
        "table": "raw_edrr_issues"
    }
}