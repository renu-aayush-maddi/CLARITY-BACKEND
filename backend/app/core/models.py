from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base

# ==========================================
# 1. CORE DIMENSION: SUBJECT (The Anchor)
# ==========================================
class Subject(Base):
    """
    The central entity. All other files link to this.
    We normalize Study/Site/Country here to avoid repetition.
    """
    __tablename__ = "subjects"

    subject_id = Column(String, primary_key=True, index=True) # e.g. "101-001"
    site_id = Column(String, index=True)
    study_id = Column(String, index=True)
    country = Column(String)
    region = Column(String)
    status = Column(String) # e.g. "Screening", "Enrolled"
    
    # Relationships (Link to satellite tables)
    metrics = relationship("RawCPID", back_populates="subject")
    visits = relationship("RawVisit", back_populates="subject")
    labs = relationship("RawLab", back_populates="subject")
    saes = relationship("RawSAE", back_populates="subject")
    analytics = relationship("SubjectAnalytics", back_populates="subject", uselist=False)

# ==========================================
# 2. RAW DATA TABLES (Ingestion Targets)
# ==========================================

class RawCPID(Base):
    """Source: CPID_EDC_Metrics (Subject Level)"""
    __tablename__ = "raw_cpid_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subjects.subject_id"))
    
    # Operational Metrics
    missing_visits = Column(Integer, default=0)
    missing_pages = Column(Integer, default=0)
    open_queries = Column(Integer, default=0)
    coded_terms = Column(Integer, default=0)
    uncoded_terms = Column(Integer, default=0)
    protocol_deviations = Column(Integer, default=0)
    
    # Verification
    pages_entered = Column(Integer, default=0)
    clean_crf_percent = Column(Float, default=0.0)
    forms_verified = Column(Integer, default=0)
    forms_locked = Column(Integer, default=0)
    
    subject = relationship("Subject", back_populates="metrics")

class RawVisit(Base):
    """Source: Visit Projection Tracker"""
    __tablename__ = "raw_visit_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subjects.subject_id"))
    visit_name = Column(String)
    projected_date = Column(String) # String to handle messy Excel formats safely
    days_outstanding = Column(Integer)
    
    subject = relationship("Subject", back_populates="visits")

class RawLab(Base):
    """Source: Missing_Lab_Name_and_Ranges"""
    __tablename__ = "raw_lab_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subjects.subject_id"))
    visit = Column(String)
    lab_category = Column(String) # Chemistry, Hematology
    test_name = Column(String)
    issue_type = Column(String) # "Missing Range" or "Missing Lab Name"
    
    subject = relationship("Subject", back_populates="labs")

class RawSAE(Base):
    """Source: SAE Dashboard (Combined DM and Safety)"""
    __tablename__ = "raw_sae_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subjects.subject_id"))
    discrepancy_id = Column(String)
    case_status = Column(String) # Open, Closed
    review_status = Column(String)
    action_status = Column(String)
    source_system = Column(String) # "DM" or "Safety"
    
    subject = relationship("Subject", back_populates="saes")

class RawProtocolDeviation(Base):
    """Source: Protocol Deviation Report"""
    __tablename__ = "raw_protocol_deviations"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subjects.subject_id"))
    category = Column(String)
    status = Column(String) # Confirmed, Proposed
    visit_date = Column(String)

# ==========================================
# 3. INTELLIGENCE LAYER (Derived Metrics)
# ==========================================

class SubjectAnalytics(Base):
    """
    The 'Data Quality Index' required by the Hackathon.
    We calculate this in Phase 2 using Python.
    """
    __tablename__ = "subject_analytics"
    
    subject_id = Column(String, ForeignKey("subjects.subject_id"), primary_key=True)
    
    # The "Clean Patient" Flag (Rule: 0 missing visits + 0 queries + 0 missing pages)
    is_clean_patient = Column(Boolean, default=False)
    
    # The "Data Quality Index" (0 to 100 Score)
    risk_score = Column(Float, default=0.0) 
    
    # Aggregates for easy dashboarding
    total_open_issues = Column(Integer, default=0)
    days_since_last_activity = Column(Integer, default=0)
    
    last_calculated = Column(DateTime(timezone=True), server_default=func.now())
    
    subject = relationship("Subject", back_populates="analytics")