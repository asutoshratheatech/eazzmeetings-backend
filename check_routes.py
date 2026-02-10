
import requests

try:
    response = requests.get("http://localhost:8004/openapi.json", timeout=15)
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get("paths", {}).keys()
        print("Available Paths:")
        for p in paths:
            print(p)
    else:
        print(f"Failed to fetch openapi.json: {response.status_code}")
except requests.RequestException as e:
    print(f"Error: {e}")
