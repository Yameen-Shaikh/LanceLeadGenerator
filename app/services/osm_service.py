import requests
import logging
import time

class OSMService:
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    # Headers to avoid 406 or blockages
    HEADERS = {
        "User-Agent": "LanceLeadGenApp/1.0 (https://github.com/yourusername/lance)",
        "Accept": "application/json"
    }
    
    # Fallback Category Mapping for common keywords
    CATEGORY_MAPPING = {
        "gym": ["fitness_centre", "gym", "fitness", "crossfit"],
        "salon": ["hairdresser", "beauty", "salon", "barber"],
        "restaurant": ["restaurant", "cafe", "fast_food", "food_court"],
        "hotel": ["hotel", "motel", "hostel", "guest_house"],
        "dentist": ["dentist", "dental", "orthodontist"],
        "spa": ["spa", "massage", "wellness"],
    }

    @staticmethod
    def search_leads(keyword: str, city: str):
        # Clean inputs
        keyword = keyword.strip()
        city = city.strip().split(',')[0].strip() # Take only city name if "City, Country" is provided
        
        # 1. BROAD DATA FETCHING
        # Use case-insensitive search for area name to be more flexible
        query = f"""
        [out:json][timeout:60];
        area["name"~"^{city}$", i]->.a;
        (
          nwr["name"](area.a);
        );
        out tags center;
        """
        
        keyword_lower = keyword.lower()
        mapping_matches = OSMService.CATEGORY_MAPPING.get(keyword_lower, [])
        
        # 6. ERROR HANDLING & RETRY LOGIC
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    OSMService.OVERPASS_URL, 
                    data={'data': query}, 
                    headers=OSMService.HEADERS,
                    timeout=70
                )
                
                response.raise_for_status()
                data = response.json()
                
                elements = data.get('elements', [])
                logging.info(f"Total elements fetched from OSM for city '{city}': {len(elements)}")
                
                leads = []
                for element in elements:
                    tags = element.get('tags', {})
                    name = tags.get('name', '')
                    name_lower = name.lower()
                    
                    amenity = tags.get('amenity', '').lower()
                    shop = tags.get('shop', '').lower()
                    leisure = tags.get('leisure', '').lower()
                    
                    # 2. PYTHON-LEVEL FILTERING & 4. FALLBACK CATEGORY MATCHING
                    match_found = False
                    if keyword_lower in name_lower or \
                       keyword_lower in amenity or \
                       keyword_lower in shop or \
                       keyword_lower in leisure:
                        match_found = True
                    else:
                        for val in mapping_matches:
                            if val in amenity or val in shop or val in leisure:
                                match_found = True
                                break
                    
                    if not match_found:
                        continue

                    # 3. SAFE TAG EXTRACTION
                    address_parts = [
                        tags.get('addr:street'),
                        tags.get('addr:housenumber'),
                        tags.get('addr:city'),
                        tags.get('addr:postcode')
                    ]
                    address = ", ".join([p for p in address_parts if p])
                    if not address:
                        address = tags.get('addr:full') or 'N/A'
                    
                    phone = tags.get('phone') or tags.get('contact:phone') or tags.get('contact:mobile') or tags.get('contact:phone:office')
                    website = tags.get('website') or tags.get('contact:website') or tags.get('contact:url') or tags.get('url')
                    
                    lead_data = {
                        "name": name,
                        "phone": phone,
                        "website": website,
                        "address": address,
                        "osm_id": element.get('id')
                    }
                    leads.append(lead_data)
                    
                    if len(leads) >= 200:
                        break
                
                logging.info(f"Elements after filtering for keyword '{keyword}': {len(leads)}")
                return leads

            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTP error fetching data from OSM: {e}")
                if response.status_code in [429, 504]:
                    time.sleep(5)
                    continue
                break
            except requests.exceptions.Timeout:
                logging.warning(f"OSM request timeout (attempt {attempt+1}/{max_retries+1})")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break
        
        return []

def calculate_score(lead):
    score = 0
    if not lead.get('website'):
        score += 3
    if lead.get('phone'):
        score += 2
    if lead.get('address') and lead.get('address') != 'N/A':
        score += 1
    return score

def get_label(score):
    if score >= 5:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"
