import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

def diag():
    lat, lon = 18.5204, 73.8567 # Pune
    query = f"""
    [out:json][timeout:90];
    (
      nwr(around:10000, {lat}, {lon})["leisure"~"fitness_centre|gym", i];
      nwr(around:10000, {lat}, {lon})["amenity"~"fitness_centre|gym", i];
      nwr(around:10000, {lat}, {lon})["name"~"gym", i];
    );
    out tags center;
    """
    print(f"Querying Overpass for Pune ({lat}, {lon})...")
    r = requests.post("https://overpass-api.de/api/interpreter", data={'data': query}, headers=HEADERS)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        elements = data.get("elements", [])
        print(f"Found {len(elements)} elements")
        for el in elements[:5]:
            print(f" - {el.get('tags', {}).get('name')}")
    else:
        print(r.text)

if __name__ == "__main__":
    diag()
