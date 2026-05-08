import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def test_gemini_search():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    print(f"Testing Gemini Search Grounding...")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    
    prompt = "Find 3 cafes in Pune with their websites and mobile numbers. Return as a JSON list of objects with keys: name, website, phone."
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "tools": [
            {"google_search_retrieval": {}}
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
        }
    }

    try:
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            print("Gemini Response:")
            print(json.dumps(json.loads(content), indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_gemini_search()
