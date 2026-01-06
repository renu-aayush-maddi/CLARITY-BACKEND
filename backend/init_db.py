from backend.app.core.database import engine, Base
from backend.app.core.models import * # Import all models

print("Creating tables in Neon...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")