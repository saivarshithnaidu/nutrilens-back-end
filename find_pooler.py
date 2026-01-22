from sqlalchemy import create_engine, text
import sys

# Config
REF = "zcphwwxdlbgrkagqsgzm"
PASS = "DfDBEtmGKv1UvRow"
USER = "postgres"
DB = "postgres"

REGIONS = [
    "ap-south-1",     # India (Likely based on User Timezone)
    "ap-southeast-1", # Singapore
    "us-east-1",      # US East
    "eu-central-1",   # Frankfurt
    "eu-west-1",      # Ireland
    "us-west-1",      # US West
    "sa-east-1",      # Sao Paulo
    "ap-northeast-1"  # Tokyo
]

PORTS = [6543, 5432]

def test_connection(region, port):
    host = f"aws-0-{region}.pooler.supabase.com"
    # Pooler user format: postgres.ref
    pooler_user = f"{USER}.{REF}"
    
    url = f"postgresql://{pooler_user}:{PASS}@{host}:{port}/{DB}?sslmode=require"
    print(f"Testing {region} on port {port}...")
    
    try:
        # Short timeout to speed up scanning
        engine = create_engine(url, connect_args={'connect_timeout': 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print(f"SUCCESS! Found valid pooler at {region}:{port}")
            return url
    except Exception as e:
        # print(f"Failed: {e}") 
        pass
    return None

def update_env(valid_url):
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("DATABASE_URL="):
                    f.write(f"DATABASE_URL={valid_url}\n")
                    print("Updated .env with working Pooler URL.")
                else:
                    f.write(line)
    except Exception as e:
        print(f"Error updating .env: {e}")

def main():
    print("Scanning Supabase Pooler Regions...")
    for region in REGIONS:
        for port in PORTS:
            valid_url = test_connection(region, port)
            if valid_url:
                update_env(valid_url)
                print("Connection fixed! You can now run the backend.")
                sys.exit(0)
    
    print("Could not find a working pooler connection.")
    sys.exit(1)

if __name__ == "__main__":
    main()
