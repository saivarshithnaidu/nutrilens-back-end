from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# load_dotenv()
# url = os.getenv("DATABASE_URL")
# Construct Pooler URL manually to bypass DNS and SNI checks
# Format: postgres://user.project_ref:password@pooler_ip:6543/postgres
# IP: 3.108.251.216
# Ref: zcphwwxdlbgrkagqsgzm
# Pass: lVEtkz0AX4L6vKSC
url = "postgresql://postgres.zcphwwxdlbgrkagqsgzm:lVEtkz0AX4L6vKSC@3.108.251.216:6543/postgres?sslmode=require"
# Hide password in print
safe_url = url.split(":")[2].split("@")[1] if url and ":" in url and "@" in url else "invalid" # Rough redaction
print(f"Connecting to host ending in: {safe_url}")

try:
    # Mimic database.py exactly
    e = create_engine(
        url,
        connect_args={"connect_timeout": 10} # Remove sslmode=require enforcement, rely on URL
    )
    with e.connect() as c:
        print("Success:", c.execute(text("SELECT 1")).scalar())
except Exception as ex:
    with open("error.txt", "w") as f:
        f.write(str(ex))
    print("Error written to error.txt")
