import socket
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL from env: {db_url}")

try:
    hostname = db_url.split("@")[1].split(":")[0]
    print(f"Hostname parsed: {hostname}")
    
    addr = socket.gethostbyname(hostname)
    print(f"Resolved {hostname} to {addr}")
except Exception as e:
    print(f"Error resolving: {e}")

print("-" * 20)
print("Testing ddb. variant just in case:")
try:
    hostname_ddb = "ddb.zcphwwxdlbgrkagqsgzm.supabase.co"
    addr = socket.gethostbyname(hostname_ddb)
    print(f"Resolved {hostname_ddb} to {addr}")
except Exception as e:
    print(f"Error resolving {hostname_ddb}: {e}")
