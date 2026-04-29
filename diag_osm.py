import requests
import json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "LanceDiagnostic/1.0"}

def test_query(lat, lon, keyword, search_terms):
    query = f"""
    [out:json][timeout:90];
    (
      nwr(around:10000, {lat}, {lon})["leisure"~"{search_terms}", i];
      nwr(around:10000, {lat}, {lon})["amenity"~"{search_terms}", i];
      nwr(around:10000, {lat}, {lon})["shop"~"{search_terms}", i];
      nwr(around:10000, {lat}, {lon})["name"~"{keyword}", i];
    );
    out tags center;
    """
    print(f"Testing original-style query for {keyword} near {lat}, {lon}...")
    response = requests.post(OVERPASS_URL, data={'data': query}, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Results found: {len(data.get('elements', []))}")
        if data.get('elements'):
            print("First result name:", data['elements'][0].get('tags', {}).get('name'))

def test_strict_query(lat, lon, keyword, search_terms):
    query = f"""
    [out:json][timeout:90];
    (
      nwr(around:10000, {lat}, {lon})["leisure"~"{search_terms}", i][!"area"];
      nwr(around:10000, {lat}, {lon})["amenity"~"{search_terms}", i][!"area"];
      nwr(around:10000, {lat}, {lon})["shop"~"{search_terms}", i];
      nwr(around:10000, {lat}, {lon})["name"~"{keyword}", i]["amenity"];
      nwr(around:10000, {lat}, {lon})["name"~"{keyword}", i]["shop"];
      nwr(around:10000, {lat}, {lon})["name"~"{keyword}", i]["leisure"];
      nwr(around:10000, {lat}, {lon})["name"~"{keyword}", i]["office"];
    );
    out tags center;
    """
    print(f"\nTesting strict query for {keyword} near {lat}, {lon}...")
    response = requests.post(OVERPASS_URL, data={'data': query}, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Results found: {len(data.get('elements', []))}")

# Coordinates for Pune (as an example)
lat, lon = 18.5204, 73.8567
keyword = "gym"
search_terms = "fitness_centre|gym|fitness|crossfit|sports_centre"

test_query(lat, lon, keyword, search_terms)
test_strict_query(lat, lon, keyword, search_terms)
