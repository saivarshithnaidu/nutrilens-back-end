import subprocess
import re
import sys

def get_pooler_ip():
    try:
        # Ping just once
        output = subprocess.check_output("ping -n 1 aws-0-ap-south-1.pooler.supabase.com", shell=True).decode()
        # Look for [1.2.3.4]
        match = re.search(r'\[([\d\.]+)\]', output)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error scraping IP: {e}")
    return None

ip = get_pooler_ip()
if ip:
    print(f"POOLER_IP={ip}")
else:
    print("NO_IP_FOUND")
