import requests

BASE_URL = "http://127.0.0.1:8000/auth"

def test_signup():
    print("Testing Signup...")
    payload = {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json().get("access_token")
    except Exception as e:
        print(f"Signup exception: {e}")
        return None

def test_login(token):
    print("\nTesting Login...")
    payload = {
        "username": "test@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Login exception: {e}")

if __name__ == "__main__":
    token = test_signup()
    if token:
        test_login(token)
