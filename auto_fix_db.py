import urllib.request
import json
import sys
from sqlalchemy import create_engine, text

# Config
HOST = "db.zcphwwxdlbgrkagqsgzm.supabase.co"
PASS = "DfDBEtmGKv1UvRow" # From user's first prompt/env
USER = "postgres"
DB = "postgres"

def get_ip_from_google_dns(hostname):
    print(f"Resolving {hostname} via Google DNS...")
    url = f"https://dns.google/resolve?name={hostname}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if "Answer" in data:
                # Get the last A record (IP)
                msg = [a['data'] for a in data["Answer"] if a['type'] == 1]
                if msg:
                    return msg[-1] # Return the IP
    except Exception as e:
        print(f"DNS Error: {e}")
    return None

def test_connection_and_update(ip_address):
    print(f"Testing connection to IP: {ip_address}...")
    # SQL Alchemy URL with IP
    # NOTE: Supabase requires SSL. verification might fail with IP, so we might need simple sslmode
    # For now, let's try standard SSL behavior or sslmode='require' with no host check (if possible)
    # With libpq, sslmode='require' usually works even if host mismatches?
    
    db_url = f"postgresql://{USER}:{PASS}@{ip_address}:5432/{DB}"
    
    try:
        engine = create_engine(db_url, connect_args={'sslmode':'require'})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("SUCCESS: Connection established!")
            
            # Read .env
            with open(".env", "r") as f:
                lines = f.readlines()
            
            # Write .env
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("DATABASE_URL="):
                        f.write(f"DATABASE_URL={db_url}\n")
                        print("Updated .env with IP address.")
                    else:
                        f.write(line)
            return True
    except Exception as e:
        print(f"Connection Failed: {e}")
        return False

def main():
    ip = get_ip_from_google_dns(HOST)
    if ip:
        print(f"Found IP: {ip}")
        success = test_connection_and_update(ip)
        if success:
            sys.exit(0)
    else:
        print("Could not resolve IP from Google DNS.")
    
    sys.exit(1)

if __name__ == "__main__":
    main()
