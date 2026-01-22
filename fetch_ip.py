import urllib.request
import json
import sys

def resolve(name):
    url = f"https://dns.google/resolve?name={name}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_a_record(hostname):
    print(f"Resolving {hostname}...")
    data = resolve(hostname)
    if not data or "Answer" not in data:
        print("No answer")
        return None
    
    for ans in data["Answer"]:
        if ans["type"] == 1: # A record
            return ans["data"]
        if ans["type"] == 5: # CNAME
            print(f"CNAME found: {ans['data']}")
            # Recursive resolve or check next answers
            # Sometimes DoH returns the A record for the CNAME in the same response
            # scan format again
            pass
            
    # If we found CNAME but no A in this list, try to find A for the CNAME target in the same list
    # or recurse.
    # Let's simple recurse if we found a CNAME and didn't return yet.
    for ans in data["Answer"]:
        if ans["type"] == 5:
            return get_a_record(ans["data"])
            
    return None

ip = get_a_record("aws-0-ap-south-1.pooler.supabase.com")
if ip:
    print(f"FINAL_IP:{ip}")
else:
    print("Could not resolve IP")
    # debug resolve again printing full
    print(resolve("aws-0-ap-south-1.pooler.supabase.com"))
