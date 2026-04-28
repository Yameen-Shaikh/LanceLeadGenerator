import requests
import logging
import time

class OSMService:
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
    
    # Standard Browser Headers
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    CATEGORY_MAPPING = {
        "gym": ["fitness_centre", "gym", "fitness", "crossfit", "sports_centre"],
        "salon": ["hairdresser", "beauty", "salon", "barber", "spa"],
        "restaurant": ["restaurant", "cafe", "fast_food", "food_court", "pub", "bar"],
        "hotel": ["hotel", "motel", "hostel", "guest_house", "apartment"],
        "dentist": ["dentist", "dental", "orthodontist", "doctors"],
        "spa": ["spa", "massage", "wellness", "sauna"],
        "retail": ["shop", "boutique", "supermarket", "mall", "department_store"],
        "automotive": ["car_repair", "car_wash", "car_dealer", "tyres"],
        "education": ["school", "college", "university", "kindergarten", "language_school"],
        "bakery": ["bakery", "pastry", "confectionery"],
        "pharmacy": ["pharmacy", "chemist"],
    }

    @staticmethod
    def get_coords(location: str):
        params = {"q": location, "format": "json", "limit": 1}
        try:
            # Nominatim also requires a User-Agent
            response = requests.get(OSMService.GEOCODE_URL, params=params, headers=OSMService.HEADERS, timeout=10)
            data = response.json()
            if data:
                return data[0]["lat"], data[0]["lon"]
        except Exception as e:
            logging.error(f"Geocoding error: {e}")
        return None, None

    @staticmethod
    def search_leads(keyword: str, location: str):
        lat, lon = OSMService.get_coords(location)
        if not lat or not lon:
            return []

        keyword_lower = keyword.lower()
        mapping_matches = OSMService.CATEGORY_MAPPING.get(keyword_lower, [keyword_lower])
        
        # Optimized query using regex in a single nwr call to be faster and cleaner
        search_terms = "|".join(mapping_matches)
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
        
        # Retry with different User-Agents if we get 406
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "LanceLeadGenBot/1.0 (+http://example.com)"
        ]

        for ua in user_agents:
            try:
                logging.info(f"Querying Overpass with UA: {ua[:30]}...")
                response = requests.post(
                    OSMService.OVERPASS_URL, 
                    data={'data': query}, 
                    headers={"User-Agent": ua}, 
                    timeout=100
                )
                
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get('elements', [])
                    
                    leads = []
                    seen_names = set()
                    for element in elements:
                        tags = element.get('tags', {})
                        name = tags.get('name') or tags.get('brand')
                        if not name or name in seen_names: continue
                        seen_names.add(name)
                        
                        addr = ", ".join([tags.get(f'addr:{f}', '') for f in ['housenumber', 'street', 'suburb', 'city'] if tags.get(f'addr:{f}')])
                        if not addr: addr = tags.get('addr:full') or f"Near {location}"
                        
                        leads.append({
                            "name": name,
                            "phone": tags.get('phone') or tags.get('contact:phone') or tags.get('contact:mobile'),
                            "website": tags.get('website') or tags.get('contact:website') or tags.get('url'),
                            "address": addr,
                            "osm_id": element.get('id')
                        })
                        if len(leads) >= 100: break
                    return leads
                
                elif response.status_code == 406:
                    logging.warning("Received 406, retrying with different UA...")
                    continue
                else:
                    logging.error(f"Overpass Error {response.status_code}: {response.text[:200]}")
                    break
                    
            except Exception as e:
                logging.error(f"Request error: {e}")
                time.sleep(1)
        
        return []

def calculate_score(lead):
    score = 0
    if not lead.get('website'): score += 3
    if lead.get('phone'): score += 2
    if lead.get('address') and "Near" not in lead.get('address'): score += 1
    return score
