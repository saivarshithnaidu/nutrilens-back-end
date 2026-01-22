
from sqlalchemy import create_engine, inspect
import os

SQLITE_URL = "sqlite:///./local.db"
engine = create_engine(SQLITE_URL)

try:
    insp = inspect(engine)
    tables = insp.get_table_names()
    print("Tables found:", tables)
    if "users" in tables:
        print("✅ users table exists.")
    else:
        print("❌ users table MISSING.")
except Exception as e:
    print(f"Error inspecting DB: {e}")
