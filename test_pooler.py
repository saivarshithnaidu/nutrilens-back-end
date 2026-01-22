from sqlalchemy import create_engine, text
import sys

# Construct the pooler URL
# user: postgres.REF
# pass: PASSWORD (from env)
# host: aws-0-ap-south-1.pooler.supabase.com
# port: 6543
# db: postgres

# Original: postgres://postgres:DfDBEtmGKv1UvRow@db.zcphwwxdlbgrkagqsgzm.supabase.co:5432/postgres
REF = "zcphwwxdlbgrkagqsgzm"
PASS = "DfDBEtmGKv1UvRow"
HOST = "aws-0-ap-south-1.pooler.supabase.com"

# Try Transaction Pooler (port 6543, user=postgres.ref)
POOLER_URL = f"postgresql://postgres.{REF}:{PASS}@{HOST}:6543/postgres"

print(f"Testing connection to: {HOST}...")

try:
    engine = create_engine(POOLER_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("\nSUCCESS! Connection established via Pooler.")
except Exception as e:
    print(f"\nFAILED via Pooler: {e}")
