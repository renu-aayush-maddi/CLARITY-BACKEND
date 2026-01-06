# import pandas as pd
# import numpy as np
# import re
# import logging
# from sqlalchemy.orm import Session
# from sqlalchemy import text, inspect
# from backend.app.utils.dataset_registry import DATASET_SPECS
# from backend.app.utils.smart_mapper import normalize_dataframe_columns, TARGET_SCHEMA

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def extract_study_from_filename(filename: str):
#     """ Extracts 'Study 1' from filename. """
#     match = re.search(r"(Study\s?\d+)", filename, re.IGNORECASE)
#     if match:
#         raw = match.group(1)
#         if " " not in raw: raw = raw.replace("Study", "Study ")
#         return raw.title()
#     return None

# def extract_study_from_content(dfs: dict):
#     """ 
#     Fallback: Looks inside the data for a 'Project Name' or 'Study' column.
#     """
#     for sheet_name, df in dfs.items():
#         # Quick normalize to see if we find a study column
#         temp_df = df.copy()
#         # Clean headers
#         if len(temp_df) > 0:
#             # Try row 0 header
#             temp_df.columns = [str(c).strip() for c in temp_df.columns]
#             temp_df = normalize_dataframe_columns(temp_df)
            
#             if 'study_name' in temp_df.columns:
#                 # Get the first non-empty value
#                 unique_vals = temp_df['study_name'].dropna().unique()
#                 for val in unique_vals:
#                     val_str = str(val)
#                     if "Study" in val_str:
#                         return val_str.strip()
            
#             # Try row 1 header (common in Metrics reports)
#             if len(df) > 1:
#                 df_skip = df.iloc[1:].copy()
#                 df_skip.columns = df.iloc[0]
#                 df_skip = normalize_dataframe_columns(df_skip)
#                 if 'study_name' in df_skip.columns:
#                     unique_vals = df_skip['study_name'].dropna().unique()
#                     for val in unique_vals:
#                          val_str = str(val)
#                          if "Study" in val_str:
#                             return val_str.strip()
#     return None

# def find_header_row(df, max_scan=20):
#     """ Scans top 20 rows to find the real header row """
#     best_idx = 0
#     max_matches = 0
#     all_keywords = [item for sublist in TARGET_SCHEMA.values() for item in sublist]
    
#     for i in range(min(len(df), max_scan)):
#         row_vals = [str(x).lower().strip() for x in df.iloc[i].values]
#         matches = sum(1 for val in row_vals if val in all_keywords)
#         if matches > max_matches:
#             max_matches = matches
#             best_idx = i
#     return best_idx if max_matches >= 2 else 0

# def ensure_subjects_exist(db: Session, df: pd.DataFrame, study_name: str):
#     if 'subject_id' not in df.columns:
#         return

#     cols_to_keep = ['subject_id']
#     if 'site_id' in df.columns:
#         cols_to_keep.append('site_id')
        
#     subjects = df[cols_to_keep].drop_duplicates(subset=['subject_id'])
    
#     sql = text("""
#         INSERT INTO subjects (subject_id, site_id, study_name, status)
#         VALUES (:uid, :site, :study, 'Active')
#         ON CONFLICT (subject_id) 
#         DO UPDATE SET site_id = EXCLUDED.site_id 
#         WHERE subjects.site_id IS NULL OR subjects.site_id = 'Unknown Site';
#     """)

#     for _, row in subjects.iterrows():
#         unique_id = str(row['subject_id']).strip() 
        
#         site_val = "Unknown Site"
#         if 'site_id' in subjects.columns and pd.notna(row['site_id']):
#             site_val = str(row['site_id'])

#         try:
#             db.execute(sql, {"uid": unique_id, "site": site_val, "study": study_name})
#         except Exception as e:
#             logger.error(f"Subject Insert Error: {e}")
    
#     try:
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Subject Commit Failed: {e}")

# def ingest_file(file, db: Session):
#     filename = file.filename
#     results = []
    
#     # 1. Try filename detection
#     study_name = extract_study_from_filename(filename)
    
#     try:
#         # Load File
#         dfs = {}
#         if filename.endswith('.csv'):
#             try:
#                 dfs["Sheet1"] = pd.read_csv(file.file, header=None, low_memory=False)
#             except:
#                 file.file.seek(0)
#                 dfs["Sheet1"] = pd.read_csv(file.file, sep=';', header=None, low_memory=False)
#         else:
#             xl = pd.ExcelFile(file.file.read())
#             for sheet in xl.sheet_names:
#                 dfs[sheet] = xl.parse(sheet, header=None)

#         # 2. Fallback: Deep Search in Content
#         if not study_name:
#             study_name = extract_study_from_content(dfs)
            
#         # 3. Last Resort: Fail
#         if not study_name:
#             return {
#                 "status": "error", 
#                 "reason": f"No Study Name detected in {filename}. Please rename file to start with 'Study X_'."
#             }

#         # Priority Sort: Metrics first
#         sorted_sheets = sorted(dfs.items(), key=lambda x: 0 if "metrics" in x[0].lower() or "subject" in x[0].lower() else 1)

#         for sheet_name, df_raw in sorted_sheets:
#             if df_raw.empty: continue

#             # 1. Header & Normalize
#             header_idx = find_header_row(df_raw)
#             new_header = df_raw.iloc[header_idx]
#             df_content = df_raw[header_idx + 1:].copy()
#             df_content.columns = new_header
            
#             df_clean = normalize_dataframe_columns(df_content)
#             df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]

#             # 2. Detect Dataset
#             dataset_key = None
#             for key, rules in DATASET_SPECS.items():
#                 if all(col in df_clean.columns for col in rules['required_columns']):
#                     dataset_key = key
#                     break
            
#             if not dataset_key: continue 

#             # 3. Transform IDs
#             df_clean['study_name'] = study_name
#             if 'subject_id' in df_clean.columns:
#                 df_clean['subject_id'] = df_clean['subject_id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
#                 # Create Composite ID ONCE
#                 df_clean['subject_id'] = study_name + "_" + df_clean['subject_id']

#             # 4. Create Subjects
#             ensure_subjects_exist(db, df_clean, study_name)
            
#             # SANITIZE INTEGER COLUMNS
#             if 'days_missing' in df_clean.columns:
#                 # Force non-numeric values (like #ERROR) to NaN, then fill with 0
#                 df_clean['days_missing'] = pd.to_numeric(df_clean['days_missing'], errors='coerce').fillna(0)
            
#             if 'days_outstanding' in df_clean.columns:
#                 df_clean['days_outstanding'] = pd.to_numeric(df_clean['days_outstanding'], errors='coerce').fillna(0)

#             # 5. Insert Data
#             target_table = DATASET_SPECS[dataset_key]["table"]
#             try:
#                 inspector = inspect(db.bind)
#                 valid_db_cols = [c['name'] for c in inspector.get_columns(target_table)]
#                 columns_to_keep = [c for c in df_clean.columns if c in valid_db_cols]
#                 df_final = df_clean[columns_to_keep]
                
#                 df_final.to_sql(target_table, db.bind, if_exists='append', index=False, method='multi')
#                 results.append(f"✅ {dataset_key}: Loaded {len(df_final)} rows")
#             except Exception as e:
#                 if "Duplicate" not in str(e):
#                     results.append(f"❌ {sheet_name}: {str(e)}")

#         return {"status": "processed", "details": results, "study": study_name}

#     except Exception as e:
#         return {"status": "error", "reason": str(e)}



import pandas as pd
import numpy as np
import re
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from backend.app.utils.dataset_registry import DATASET_SPECS
from backend.app.utils.smart_mapper import normalize_dataframe_columns, TARGET_SCHEMA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. FILENAME DETECTION (The Fast Way) ---
def extract_study_from_filename(filename: str):
    """ Extracts 'Study 1' from 'Study 1_Visit_Tracker.csv' """
    match = re.search(r"(Study\s?\d+)", filename, re.IGNORECASE)
    if match:
        raw = match.group(1)
        if " " not in raw: raw = raw.replace("Study", "Study ")
        return raw.title()
    return None

# --- 2. CONTENT DETECTION (The Smart Fallback) ---
def extract_study_from_content(dfs: dict):
    """ 
    Looks inside the Excel/CSV data for a 'Project Name' or 'Study' column.
    Useful when the filename is generic like 'Inactivated_Rows.xlsx'.
    """
    for sheet_name, df in dfs.items():
        # Make a copy and normalize to find hidden 'study_name' columns
        try:
            temp_df = df.copy()
            # Try finding header in first few rows
            header_idx = find_header_row(temp_df)
            new_header = temp_df.iloc[header_idx]
            temp_df = temp_df[header_idx + 1:]
            temp_df.columns = new_header
            
            # Normalize to see if we have 'study_name'
            temp_df = normalize_dataframe_columns(temp_df)
            
            if 'study_name' in temp_df.columns:
                # Get the first value (e.g., "Study 2")
                unique_vals = temp_df['study_name'].dropna().unique()
                for val in unique_vals:
                    val_str = str(val).strip()
                    # Validate it looks like "Study X"
                    if re.match(r"Study\s?\d+", val_str, re.IGNORECASE):
                        # Standardize format to "Study X"
                        match = re.search(r"(Study\s?\d+)", val_str, re.IGNORECASE)
                        raw = match.group(1)
                        if " " not in raw: raw = raw.replace("Study", "Study ")
                        return raw.title()
        except Exception:
            continue # If this sheet fails, try the next one

    return None

def find_header_row(df, max_scan=20):
    """ Scans top 20 rows to find the real header row """
    best_idx = 0
    max_matches = 0
    all_keywords = [item for sublist in TARGET_SCHEMA.values() for item in sublist]
    
    for i in range(min(len(df), max_scan)):
        row_vals = [str(x).lower().strip() for x in df.iloc[i].values]
        matches = sum(1 for val in row_vals if val in all_keywords)
        if matches > max_matches:
            max_matches = matches
            best_idx = i
    return best_idx if max_matches >= 2 else 0

def ensure_subjects_exist(db: Session, df: pd.DataFrame, study_name: str):
    """
    Creates subjects in the database.
    """
    if 'subject_id' not in df.columns:
        return

    # Keep Site ID if exists
    cols_to_keep = ['subject_id']
    if 'site_id' in df.columns:
        cols_to_keep.append('site_id')
        
    subjects = df[cols_to_keep].drop_duplicates(subset=['subject_id'])
    
    sql = text("""
        INSERT INTO subjects (subject_id, site_id, study_name, status)
        VALUES (:uid, :site, :study, 'Active')
        ON CONFLICT (subject_id) 
        DO UPDATE SET site_id = EXCLUDED.site_id 
        WHERE subjects.site_id IS NULL OR subjects.site_id = 'Unknown Site';
    """)

    for _, row in subjects.iterrows():
        unique_id = str(row['subject_id']).strip() 
        
        site_val = "Unknown Site"
        if 'site_id' in subjects.columns and pd.notna(row['site_id']):
            site_val = str(row['site_id'])

        try:
            db.execute(sql, {"uid": unique_id, "site": site_val, "study": study_name})
        except Exception as e:
            logger.error(f"Subject Insert Error: {e}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Subject Commit Failed: {e}")

# --- UPDATE THIS FUNCTION ---
def ingest_file(file, db: Session, study_name: str = None):
    filename = file.filename
    results = []
    
    # CASE A: User selected a study in the UI (The "Batch Context" approach)
    if study_name:
        # We trust the user's selection. No need to search the file.
        pass 
        
    # CASE B: No study selected? Try to auto-detect (Fallback)
    else:
        # 1. Try Filename
        study_name = extract_study_from_filename(filename)
        
        # 2. Try Content
        if not study_name:
             # We need to load the file early to check content for the name
            try:
                if filename.endswith('.csv'):
                    # ... (csv loading logic) ...
                    pass 
                else:
                    # ... (excel loading logic) ...
                    pass 
                # (This part gets tricky because we usually load the file later. 
                #  If using Batch Context, you rarely reach this fallback.)
                pass
            except:
                pass

    # FINAL CHECK: Do we have a study name now?
    if not study_name:
         return {
            "status": "error", 
            "reason": f"Study Name is missing. Please select a Study from the dropdown."
        }

    try:
        # Load File (If not already loaded in fallback)
        dfs = {}
        file.file.seek(0) # RESET POINTER in case we read it during detection
        
        if filename.endswith('.csv'):
            try:
                dfs["Sheet1"] = pd.read_csv(file.file, header=None, low_memory=False)
            except:
                file.file.seek(0)
                dfs["Sheet1"] = pd.read_csv(file.file, sep=';', header=None, low_memory=False)
        else:
            xl = pd.ExcelFile(file.file.read())
            for sheet in xl.sheet_names:
                dfs[sheet] = xl.parse(sheet, header=None)

        # Priority Sort: Metrics first
        sorted_sheets = sorted(dfs.items(), key=lambda x: 0 if "metrics" in x[0].lower() or "subject" in x[0].lower() else 1)

        for sheet_name, df_raw in sorted_sheets:
            if df_raw.empty: continue

            # 1. Header & Normalize
            header_idx = find_header_row(df_raw)
            new_header = df_raw.iloc[header_idx]
            df_content = df_raw[header_idx + 1:].copy()
            df_content.columns = new_header
            
            df_clean = normalize_dataframe_columns(df_content)
            df_clean = df_clean.loc[:, ~df_clean.columns.duplicated()]

            # 2. Detect Dataset
            dataset_key = None
            for key, rules in DATASET_SPECS.items():
                if all(col in df_clean.columns for col in rules['required_columns']):
                    dataset_key = key
                    break
            
            if not dataset_key: continue 

            # 3. Transform IDs (Uses the study_name we passed in!)
            df_clean['study_name'] = study_name
            
            if 'subject_id' in df_clean.columns:
                df_clean['subject_id'] = df_clean['subject_id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                # Enforce unique ID format: Study2_1001
                df_clean['subject_id'] = study_name + "_" + df_clean['subject_id']
            
            # SANITIZE INTEGER COLUMNS
            if 'days_missing' in df_clean.columns:
                df_clean['days_missing'] = pd.to_numeric(df_clean['days_missing'], errors='coerce').fillna(0)
            if 'days_outstanding' in df_clean.columns:
                df_clean['days_outstanding'] = pd.to_numeric(df_clean['days_outstanding'], errors='coerce').fillna(0)

            # 4. Create Subjects
            ensure_subjects_exist(db, df_clean, study_name)

            # 5. Insert Data
            target_table = DATASET_SPECS[dataset_key]["table"]
            try:
                inspector = inspect(db.bind)
                valid_db_cols = [c['name'] for c in inspector.get_columns(target_table)]
                columns_to_keep = [c for c in df_clean.columns if c in valid_db_cols]
                df_final = df_clean[columns_to_keep]
                
                df_final.to_sql(target_table, db.bind, if_exists='append', index=False, method='multi')
                results.append(f"✅ {dataset_key}: Loaded {len(df_final)} rows")
            except Exception as e:
                if "Duplicate" not in str(e):
                    results.append(f"❌ {sheet_name}: {str(e)}")

        return {"status": "processed", "details": results, "study": study_name}

    except Exception as e:
        return {"status": "error", "reason": str(e)}