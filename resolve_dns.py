import urllib.request
import json
import sys

host = "db.zcphwwxdlbgrkagqsgzm.supabase.co"
url = f"https://dns.google/resolve?name={host}"
print(f"Querying {url}...")

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        print(f"DEBUG DATA: {data}")
        if "Answer" in data:
            for answer in data["Answer"]:
                if answer["type"] == 1: # A record
                    print(f"IP:{answer['data']}") # Format for easy parsing
                    sys.exit(0)
        
        print("No A record found.")
        sys.exit(1)

except Exception as e:
    print(f"Error resolving DNS: {e}")
    sys.exit(1)
