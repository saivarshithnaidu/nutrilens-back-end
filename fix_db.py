
from database import engine, Base
# Import all models to ensure they are registered
from models import sql_models

try:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
