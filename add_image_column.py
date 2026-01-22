from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure we use postgresql:// for SQLAlchemy
original_url = os.getenv("DATABASE_URL", "")
if original_url.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = original_url.replace("postgres://", "postgresql://", 1)
else:
    SQLALCHEMY_DATABASE_URL = original_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def add_column():
    try:
        with engine.connect() as conn:
            # Check if column exists
            check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='profile_image'")
            result = conn.execute(check_sql).fetchone()
            
            if not result:
                print("Adding profile_image column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_image VARCHAR"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column profile_image already exists.")
    except Exception as e:
        print(f"Error migrating database: {e}")

if __name__ == "__main__":
    add_column()
