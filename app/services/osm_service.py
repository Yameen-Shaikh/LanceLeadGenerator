import requests
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor

class OSMService:
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
    REVERSE_GEOCODE_URL = "https://nominatim.openstreetmap.org/reverse"
    
    COORD_CACHE = {}

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]
    
    CATEGORY_MAPPING = {
        "gym": ["fitness_centre", "gym", "fitness", "crossfit", "sports_centre"],
        "salon": ["hairdresser", "beauty", "salon", "barber", "spa", "nail_salon"],
        "restaurant": ["restaurant", "cafe", "fast_food", "food_court", "pub", "bar", "bistro"],
        "hotel": ["hotel", "motel", "hostel", "guest_house", "apartment", "resort"],
        "dentist": ["dentist", "dental", "orthodontist"],
        "spa": ["spa", "massage", "wellness", "sauna"],
        "retail": ["shop", "boutique", "supermarket", "mall", "department_store", "clothing", "electronics"],
        "automotive": ["car_repair", "car_wash", "car_dealer", "tyres", "mechanic"],
        "education": ["school", "college", "university", "kindergarten", "language_school", "tutoring"],
        "bakery": ["bakery", "pastry", "confectionery"],
        "pharmacy": ["pharmacy", "chemist"],
    }

    @staticmethod
    def get_coords(location: str):
        """Fetch coordinates with caching and multiple fallbacks (Photon + Nominatim)."""
        location_clean = location.strip().lower()
        
        if location_clean in OSMService.COORD_CACHE:
            return OSMService.COORD_CACHE[location_clean]

        unique_ua = f"LanceLeadGenApp/1.0 (Contact: lance-app-{random.randint(100,999)}@example.com)"

        def try_services(loc):
            # Try Photon (Komoot)
            photon_url = f"https://photon.komoot.io/api/?q={loc}&limit=1"
            try:
                response = requests.get(photon_url, headers={"User-Agent": unique_ua}, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('features'):
                        coords = data['features'][0]['geometry']['coordinates']
                        return coords[1], coords[0] # [lat, lon]
            except:
                pass

            # Try Nominatim Mirrors
            endpoints = [
                "https://nominatim.openstreetmap.org/search",
                "https://nominatim.qwant.com/search",
            ]
            for url in endpoints:
                try:
                    params = {"q": loc, "format": "json", "limit": 1}
                    response = requests.get(url, params=params, headers={"User-Agent": unique_ua}, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            return data[0]["lat"], data[0]["lon"]
                except:
                    continue
            return None, None

        res = try_services(location_clean)
        if not res and " " not in location_clean and "," not in location_clean:
            res = try_services(f"{location_clean}, India")

        if res:
            OSMService.COORD_CACHE[location_clean] = res
            
        return res

    @staticmethod
    def get_exact_address(lat, lon):
        """Reverse geocoding with UA rotation."""
        params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
        ua = random.choice(OSMService.USER_AGENTS)
        try:
            response = requests.get(OSMService.REVERSE_GEOCODE_URL, params=params, headers={"User-Agent": ua}, timeout=5)
            data = response.json()
            if data and "display_name" in data:
                return ", ".join(data.get("display_name").split(",")[:4])
        except:
            pass
        return None

    @staticmethod
    def check_link_status(url: str):
        """Check link reachability."""
        if not url: return None
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        ua = random.choice(OSMService.USER_AGENTS)
        try:
            response = requests.head(url, headers={"User-Agent": ua}, timeout=5, allow_redirects=True)
            return "live" if response.status_code < 400 else "dead"
        except:
            try:
                response = requests.get(url, headers={"User-Agent": ua}, timeout=5, allow_redirects=True)
                return "live" if response.status_code < 400 else "dead"
            except:
                return "dead"

    @staticmethod
    def search_leads(keyword: str, location: str):
        """Main search logic with robust filtering and case-insensitivity."""
        keyword_clean = keyword.strip().lower()
        location_clean = location.strip().lower()
        
        lat, lon = OSMService.get_coords(location_clean)
        if not lat or not lon:
            return []
            
        mapping_matches = OSMService.CATEGORY_MAPPING.get(keyword_clean, [keyword_clean])
        search_terms = "|".join(mapping_matches)
        
        radius = 5000 # 5km
        
        query = f"""
        [out:json][timeout:120];
        (
          nwr(around:{radius}, {lat}, {lon})["leisure"~"{search_terms}", i];
          nwr(around:{radius}, {lat}, {lon})["amenity"~"{search_terms}", i];
          nwr(around:{radius}, {lat}, {lon})["shop"~"{search_terms}", i];
          nwr(around:{radius}, {lat}, {lon})["office"~"{search_terms}", i];
          nwr(around:{radius}, {lat}, {lon})["name"~"{keyword_clean}", i];
        );
        out tags center;
        """
        
        overpass_endpoints = [
            "https://overpass-api.de/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.osm.ch/api/interpreter",
            "https://overpass.openstreetmap.fr/api/interpreter"
        ]

        headers = {
            "User-Agent": f"LanceLeadGenTool/2.2 (Contact: lance-project-dev@gmail.com)",
            "Accept": "application/json",
            "Referer": "https://osm.org/"
        }

        blacklisted_place_types = ["suburb", "neighbourhood", "residential", "postcode", "district", "village", "town", "locality"]

        for url in overpass_endpoints:
            try:
                response = requests.post(url, data={'data': query}, headers=headers, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get('elements', [])
                    if not elements: continue

                    leads = []
                    seen_names = set()
                    for element in elements:
                        tags = element.get('tags', {})
                        name = tags.get('name') or tags.get('brand')
                        if not name: continue
                        
                        name_key = name.strip().lower()
                        if name_key in seen_names: continue
                        
                        place_type = tags.get('place') or tags.get('boundary') or tags.get('landuse')
                        if place_type in blacklisted_place_types: continue
                        
                        # More inclusive business check
                        has_biz_tag = any(t in tags for t in ['amenity', 'shop', 'leisure', 'office', 'craft', 'healthcare', 'tourism', 'industrial'])
                        if not has_biz_tag and keyword_clean not in name.lower(): continue

                        seen_names.add(name_key)
                        
                        addr_parts = [tags.get(f'addr:{f}', '') for f in ['housenumber', 'street', 'suburb', 'city'] if tags.get(f'addr:{f}')]
                        addr = ", ".join(addr_parts)
                        
                        lat_val = element.get('lat') or element.get('center', {}).get('lat')
                        lon_val = element.get('lon') or element.get('center', {}).get('lon')

                        leads.append({
                            "name": name,
                            "phone": tags.get('phone') or tags.get('contact:phone') or tags.get('contact:mobile'),
                            "website": tags.get('website') or tags.get('contact:website') or tags.get('url'),
                            "address": addr,
                            "lat": lat_val,
                            "lon": lon_val,
                            "osm_id": element.get('id')
                        })
                        if len(leads) >= 50: break

                    if not leads: continue

                    # Enrichment
                    def enrich_lead(lead):
                        lead['link_status'] = OSMService.check_link_status(lead['website']) if lead['website'] else "missing"
                        if (not lead['address'] or "near" in lead['address'].lower()) and lead['lat'] and lead['lon']:
                            refined = OSMService.get_exact_address(lead['lat'], lead['lon'])
                            if refined: lead['address'] = refined
                        return lead

                    with ThreadPoolExecutor(max_workers=10) as executor:
                        leads = list(executor.map(enrich_lead, leads))

                    return leads
                else:
                    continue
            except:
                continue
        
        return []

def calculate_score(lead):
    score = 0
    if not lead.get('website'): score += 4
    elif lead.get('link_status') == "dead": score += 5
    elif lead.get('link_status') == "live": score += 1
    if lead.get('phone'): score += 2
    if lead.get('address') and "near" not in lead.get('address').lower(): score += 1
    return score
