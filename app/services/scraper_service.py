import requests
from bs4 import BeautifulSoup
import re
import random

class ScraperService:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]

    @staticmethod
    def extract_mobile_numbers(url: str):
        """Visits a URL and tries to find Indian mobile numbers, excluding landlines."""
        if not url: return None
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            headers = {"User-Agent": random.choice(ScraperService.USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15, verify=False) # verify=False to handle poor SSL
            if response.status_code != 200: return None

            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ')
            
            # Regex for Indian Mobile Numbers:
            # 1. May start with +91 or 91 or 0
            # 2. Main number must start with 6, 7, 8, or 9
            # 3. Must have exactly 10 digits in total (excluding prefix)
            phone_pattern = re.compile(r'(?:\+91|91|0)?[6-9]\d{9}')
            
            matches = phone_pattern.findall(text)
            
            # Clean and filter matches
            valid_mobiles = []
            for match in matches:
                # Remove common prefixes to get the 10-digit number
                clean = re.sub(r'^(\+91|91|0)', '', match)
                
                # Check for Pune landline '020' explicitly (just in case regex caught it)
                if match.startswith('020'): continue
                if len(clean) == 10 and clean[0] in '6789':
                    valid_mobiles.append(clean)

            # Prioritize 'tel:' links in the HTML (often more accurate)
            tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
            for link in tel_links:
                tel = re.sub(r'\D', '', link.get('href'))
                # Clean prefix
                clean_tel = re.sub(r'^(91|0)', '', tel)
                if len(clean_tel) == 10 and clean_tel[0] in '6789':
                    if clean_tel not in valid_mobiles:
                        valid_mobiles.insert(0, clean_tel) # Add tel links to front

            return valid_mobiles[0] if valid_mobiles else None

        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return None
