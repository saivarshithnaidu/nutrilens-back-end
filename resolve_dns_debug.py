import urllib.request
import json
import sys

def check_host(hostname):
    print(f"\nChecking {hostname}...")
    url = f"https://dns.google/resolve?name={hostname}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {data.get('Status')} (0=Success, 3=NXDOMAIN)")
            if "Answer" in data:
                for answer in data["Answer"]:
                    line = f" - Type: {answer['type']}, Data: {answer['data']}\n"
                    print(line.strip())
                    with open("dns_result.txt", "a") as f:
                        f.write(line)
            else:
                print(" - No Answer section.")
    except Exception as e:
        print(f"Error: {e}")

check_host("db.zcphwwxdlbgrkagqsgzm.supabase.co")
check_host("aws-0-ap-south-1.pooler.supabase.com")
check_host("google.com")
