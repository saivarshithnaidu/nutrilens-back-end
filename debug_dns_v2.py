import socket
import os
from dotenv import load_dotenv

print("--- DEBUG DNS START ---")
load_dotenv(override=True)

db_url = os.getenv("DATABASE_URL")
# redacted print to be safe
print(f"DATABASE_URL length: {len(db_url) if db_url else 0}")
if db_url:
    print(f"DATABASE_URL prefix: {db_url.split('@')[-1] if '@' in db_url else 'Invalid Format'}")

try:
    if not db_url or "@" not in db_url:
        print("DATABASE_URL is missing or invalid.")
    else:
        hostname = db_url.split("@")[1].split(":")[0]
        print(f"Target Hostname: {hostname}")
        
        try:
            addr = socket.gethostbyname(hostname)
            print(f"SUCCESS: Resolved {hostname} to {addr}")
        except Exception as e:
            print(f"FAILURE: Could not resolve {hostname}: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")

print("--- DEBUG DNS END ---")
