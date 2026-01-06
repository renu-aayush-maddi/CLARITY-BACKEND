from backend.app.core.database import SessionLocal
from sqlalchemy import text, inspect

def debug_database():
    db = SessionLocal()
    inspector = inspect(db.get_bind())
    
    print("\n" + "="*50)
    print("🔎 DATABASE DIAGNOSTIC REPORT")
    print("="*50)

    # 1. LIST ALL TABLES AND ROW COUNTS
    tables = inspector.get_table_names()
    print(f"\nFound {len(tables)} tables: {tables}")

    for table in tables:
        print(f"\n--- Table: {table} ---")
        
        # Get Columns
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"   Columns: {columns}")
        
        # Get Row Count
        try:
            count = db.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
            print(f"   Row Count: {count}")
            
            # If table has data, print the first row to check values (especially Study Name)
            if count > 0:
                sample = db.execute(text(f'SELECT * FROM "{table}" LIMIT 1')).fetchone()
                print(f"   Sample Row: {sample}")
        except Exception as e:
            print(f"   Error reading table: {e}")

    print("\n" + "="*50)

if __name__ == "__main__":
    debug_database()