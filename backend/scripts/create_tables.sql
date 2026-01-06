-- ================================
-- STUDY / SITE / SUBJECT BASE
-- ================================
CREATE TABLE IF NOT EXISTS study (
    id SERIAL PRIMARY KEY,
    study_name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS site (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    site_id TEXT,
    country TEXT,
    region TEXT
);

CREATE TABLE IF NOT EXISTS subject (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    site_id TEXT,
    subject_id TEXT
);

-- ================================
-- 1. CPID EDC METRICS
-- ================================
CREATE TABLE IF NOT EXISTS raw_cpid_edc_metrics (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    region TEXT,
    country TEXT,
    site_id TEXT,
    subject_id TEXT,
    subject_status TEXT,
    missing_visits INT,
    missing_pages INT,
    coded_terms INT,
    uncoded_terms INT,
    open_queries INT,
    protocol_deviations INT,
    expected_visits INT,
    pages_entered INT,
    clean_crf_percent FLOAT
);

-- ================================
-- 2. VISIT PROJECTION TRACKER
-- ================================
CREATE TABLE IF NOT EXISTS raw_visit_projection (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    country TEXT,
    site_id TEXT,
    subject_id TEXT,
    visit_name TEXT,
    projected_date DATE,
    days_outstanding INT
);

-- ================================
-- 3. MISSING PAGES REPORT
-- ================================
CREATE TABLE IF NOT EXISTS raw_missing_pages (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    site_id TEXT,
    subject_id TEXT,
    visit_date DATE,
    form_name TEXT,
    days_missing INT
);

-- ================================
-- 4. LAB ISSUES
-- ================================
CREATE TABLE IF NOT EXISTS raw_lab_issues (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    country TEXT,
    site_id TEXT,
    subject_id TEXT,
    visit_name TEXT,
    lab_category TEXT,
    issue TEXT
);

-- ================================
-- 5. SAE DASHBOARD (DM)
-- ================================
CREATE TABLE IF NOT EXISTS raw_sae_dm (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    country TEXT,
    site_id TEXT,
    subject_id TEXT,
    review_status TEXT,
    action_status TEXT
);

-- ================================
-- 6. SAE DASHBOARD (SAFETY)
-- ================================
CREATE TABLE IF NOT EXISTS raw_sae_safety (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    site_id TEXT,
    subject_id TEXT,
    case_status TEXT,
    review_status TEXT,
    action_status TEXT
);

-- ================================
-- 7. EDRR RECONCILIATION
-- ================================
CREATE TABLE IF NOT EXISTS raw_edrr (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    subject_id TEXT,
    open_issue_count INT
);

-- ================================
-- 8. MEDDRA CODING
-- ================================
CREATE TABLE IF NOT EXISTS raw_coding_meddra (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    subject_id TEXT,
    form_name TEXT,
    coding_status TEXT,
    requires_coding BOOLEAN
);

-- ================================
-- 9. WHODRUG CODING
-- ================================
CREATE TABLE IF NOT EXISTS raw_coding_whodra (
    id SERIAL PRIMARY KEY,
    study_name TEXT,
    subject_id TEXT,
    form_name TEXT,
    coding_status TEXT,
    requires_coding BOOLEAN
);
