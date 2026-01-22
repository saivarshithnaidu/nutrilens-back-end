from passlib.context import CryptContext
import sys

print(f"Python version: {sys.version}")

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("Context created.")
    
    hash_ = pwd_context.hash("password123")
    print(f"Hash: {hash_}")
    
    verify = pwd_context.verify("password123", hash_)
    print(f"Verify: {verify}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
