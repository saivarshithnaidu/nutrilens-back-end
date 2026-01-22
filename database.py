from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
APP_ENV = os.getenv("APP_ENV", "development")
SUPABASE_URL = os.getenv("DATABASE_URL", "")
SQLITE_URL = "sqlite:///./local.db"

# Monkeypatch removed - relying on system DNS or fallback
# import socket
# ... (removed)

# Helper to fix postgres protocol
if SUPABASE_URL.startswith("postgres://"):
    SUPABASE_URL = SUPABASE_URL.replace("postgres://", "postgresql://", 1)

# Global Engine & Session
engine = None
SessionLocal = None
Base = declarative_base()

def init_db():
    global engine, SessionLocal
    
    # 1. Attempt Supabase Connection
    try:
        print("🌐 Connecting to Supabase (Cloud DB)...")
        logger.info("Attempting to connect to Supabase...")
        temp_engine = create_engine(
            SUPABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3, "sslmode": "require"} # Reduced timeout
        )
        # Test Connection
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Connected to Supabase!")
        engine = temp_engine
        
    except Exception as e:
        print(f"⚠️ Supabase unavailable ({str(e)[:50]}...).")
        # logger.warning(f"⚠️ Supabase unreachable: {e}")
        
        # 2. Fallback to SQLite (Development Only)
        if APP_ENV == "development":
            print("🔄 FALLING BACK TO LOCAL SQLITE DATABASE (Offline Mode)")
            logger.info("🔄 Falling back to Local SQLite...")
            engine = create_engine(
                SQLITE_URL, 
                connect_args={"check_same_thread": False} 
            )
            print("✅ Connected to Local SQLite")
        else:
            logger.error("❌ Database connection failed in Production. No fallback allowed.")
            engine = None

    # 3. Create Session Factory
    if engine:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize on module load
init_db()

def get_db():
    if SessionLocal is None:
        # DB is completely offline (Production + Supabase Down)
        raise Exception("Database unavailable")
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
