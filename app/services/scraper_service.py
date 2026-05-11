import requests
from bs4 import BeautifulSoup
import re
import random
import logging

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
            # Suppress insecure request warnings due to verify=False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            if response.status_code != 200: return None

            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ')
            
            # Regex for Indian Mobile Numbers
            phone_pattern = re.compile(r'(?:\+91|91|0)?[6-9]\d{9}')
            matches = phone_pattern.findall(text)
            
            valid_mobiles = []
            for match in matches:
                clean = re.sub(r'^(\+91|91|0)', '', match)
                if match.startswith('020'): continue
                if len(clean) == 10 and clean[0] in '6789':
                    valid_mobiles.append(clean)

            # Prioritize 'tel:' links
            tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
            for link in tel_links:
                tel = re.sub(r'\D', '', link.get('href'))
                clean_tel = re.sub(r'^(91|0)', '', tel)
                if len(clean_tel) == 10 and clean_tel[0] in '6789':
                    if clean_tel not in valid_mobiles:
                        valid_mobiles.insert(0, clean_tel)

            return valid_mobiles[0] if valid_mobiles else None

        except Exception as e:
            logging.error(f"Scraping error for {url}: {e}")
            return None
