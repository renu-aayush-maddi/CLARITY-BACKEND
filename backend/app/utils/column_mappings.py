COLUMN_MAPPINGS = {
    # 1. SUBJECT METRICS (Master List)
    "raw_cpid_metrics": {
        "study_name": ["Project Name", "Study", "Protocol"],
        "site_id": ["Site ID", "Site", "Site Number", "SiteNumber"],
        "subject_id": ["Subject ID", "Subject", "Patient ID", "SubjectName", "Subject Name"],
        "subject_status": ["Subject Status (Source: PRIMARY Form)", "Subject Status", "Status"],
        "missing_visits": ["Missing Visits", "# Missing Visits", "Number of Missing Visits"],
        "missing_pages": ["Missing Page", "Missing Pages", "# Missing Pages"],
        "open_queries": ["#Total Queries", "Total Queries", "# Total Queries", "Open Queries"],
        "clean_crf_percent": ["% Clean Entered CRF", "Clean CRF %"],
        "protocol_deviations": ["Protocol Deviations (Source:(Rave EDC : BO4))", "Protocol Deviations", "# PDs"],
        "pages_entered": ["# Pages Entered", "Pages Entered"]
    },

    # 2. PROTOCOL DEVIATIONS
    "raw_protocol_deviations": {
        "study_name": ["Study", "Project Name"],
        "site_id": ["Site ID", "Site"],
        "subject_id": ["Subject Name", "Subject", "Subject ID"],
        "pd_status": ["PD Status", "Deviation Status", "Status"],
        "visit_date": ["Visit date", "Visit Date", "Date of Visit"]
    },

    # 3. SDV (Source Data Verification)
    "raw_sdv_metrics": {
        "site_id": ["Site", "Site ID"],
        "subject_id": ["Subject Name", "Subject", "Subject ID"],
        "visit_date": ["Visit Date", "Visit date"],
        "form_name": ["Data Page Name", "Form Name", "Form"],
        "verification_status": ["Verification Status", "SDV Status"]
    },

    # 4. MISSING PAGES (The most variable one)
    "raw_missing_pages": {
        "study_name": ["Study Name", "Study", "Project Name"], # <--- ADD THIS LINE
        "subject_id": ["Subject Name", "SubjectName", "Subject", "Subject ID"],
        "site_id": ["Site Number", "SiteNumber", "Site", "Site ID"],
        "form_name": ["FormName", "Page Name", "Form Name", "Form"],
        "days_missing": ["No. #Days Page Missing", "# of Days Missing", "Days Outstanding", "Days Missing", "# Days"]
    },

    # 5. WHODRUG (Coding)
    "raw_coding_whodra": {
        "subject_id": ["Subject", "Subject Name", "Subject ID"],
        "coding_status": ["Coding Status"],
        # If "Trade Name" is missing, we fall back to "Field OID" or "Verbatim"
        "trade_name": ["Trade Name", "Trade name", "Field OID", "Verbatim Term", "Reported Term"]
    },

    # 6. MEDDRA (Coding)
    "raw_coding_meddra": {
        "subject_id": ["Subject", "Subject Name", "Subject ID"],
        "coding_status": ["Coding Status"],
        # If "Term" is missing, fall back to "Field OID"
        "term": ["Field OID", "Reported Term", "Term", "Verbatim Term"]
    },

    # 7. SAE / SAFETY
    "raw_sae_safety": {
        "subject_id": ["Patient ID", "Subject", "Subject ID", "Subject Name"],
        "site_id": ["Site", "Site ID"],
        "discrepancy_id": ["Discrepancy ID", "ID"],
        "case_status": ["Case Status", "Status"],
        "review_status": ["Review Status"]
    },
    
    # 8. SAE / DM
    "raw_sae_dm": {
        "subject_id": ["Patient ID", "Subject", "Subject ID"],
        "site_id": ["Site", "Site ID"],
        "discrepancy_id": ["Discrepancy ID", "ID"],
        "action_status": ["Action Status"]
    },

    # 9. LAB ISSUES
    "raw_lab_issues": {
        "site_id": ["Site number", "Site", "Site ID"],
        "subject_id": ["Subject", "Subject ID", "Subject Name"],
        "visit": ["Visit", "Visit Name"],
        "lab_category": ["Lab category", "Category"],
        "test_name": ["Test Name", "Test description", "Lab Test"],
        "issue_type": ["Issue", "Issue Description"]
    },

    # 10. VISIT PROJECTIONS
    "raw_visit_projections": {
        "study_name": ["Project Name", "Study"],
        "site_id": ["Site", "Site ID"],
        "subject_id": ["Subject", "Subject ID"],
        "visit_name": ["Visit", "Visit Name"],
        "projected_date": ["Projected Date", "Date"],
        "days_outstanding": ["# Days Outstanding", "# Days Outstanding (TODAY - PROJECTED DATE)", "Days Overdue"]
    },

    # 11. EDRR
    "raw_edrr_issues": {
        "subject_id": ["Subject", "Subject ID"],
        "site_id": ["Site", "Site ID"],
        "issue_count": ["Total Open issue Count per subject", "Total Open issue Count", "Open Issues"]
    },

    # 12. INACTIVATED FORMS
    "raw_inactivated_forms": {
        "subject_id": ["Subject", "Subject ID"],
        "site_id": ["Study Site Number", "Site", "Site ID", "Site Number"],
        "folder_name": ["Folder", "Folder Name"],
        "form_name": ["Form", "Form Name"],
        "audit_action": ["Audit Action", "Action"]
    }
}