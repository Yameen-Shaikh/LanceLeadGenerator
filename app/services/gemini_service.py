import httpx
import logging
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    API_KEY = os.getenv("GEMINI_API_KEY")
    # Using the full model path for v1beta stability
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    @staticmethod
    async def search_leads(keyword: str, location: str):
        """
        Use Gemini with Search Grounding to find businesses.
        This is used as a high-quality fallback or alternative to OSM.
        """
        if not GeminiService.API_KEY or GeminiService.API_KEY == "AIzaSyBTFmE54WYYJMti4qPCrjNfxUy5uSyPa2Y":
            # The key is present, we should not block it with a hardcoded check
            pass
        
        if not GeminiService.API_KEY:
            logging.error("Gemini API Key not configured.")
            return []

        prompt = f"""
        Find 15 active businesses for the category '{keyword}' in '{location}'.
        For each business, provide:
        - Name
        - Full Address
        - Website (if available)
        - Mobile/Phone number (Indian format starting with 6-9 preferred)
        
        Format the response as a JSON list of objects with keys: 'name', 'address', 'website', 'phone'.
        Only return the JSON list, no other text.
        """

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "tools": [
                {"google_search_retrieval": {}} # This enables Search Grounding
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{GeminiService.BASE_URL}?key={GeminiService.API_KEY}",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Extract text content from Gemini response
                    content_text = result['candidates'][0]['content']['parts'][0]['text']
                    leads = json.loads(content_text)
                    
                    # Normalize leads to match project schema
                    for lead in leads:
                        lead['lat'] = None # Gemini doesn't always give precise GPS easily
                        lead['lon'] = None
                        lead['source'] = 'gemini'
                    
                    return leads
                else:
                    logging.error(f"Gemini API Error: {response.status_code} - {response.text}")
                    return []
            except Exception as e:
                logging.error(f"Error calling Gemini: {e}")
                return []

    @staticmethod
    async def enrich_missing_data(lead_name: str, address: str):
        """
        Specific tool to find missing website/phone for a known business.
        """
        if not GeminiService.API_KEY or GeminiService.API_KEY == "your_key_here":
            return None

        prompt = f"Find the official website and mobile number for the business '{lead_name}' located at '{address}'. Return only a JSON object with 'website' and 'phone' keys."

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "tools": [{"google_search_retrieval": {}}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(
                    f"{GeminiService.BASE_URL}?key={GeminiService.API_KEY}",
                    headers=headers,
                    json=payload
                )
                if response.status_code == 200:
                    result = response.json()
                    content_text = result['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(content_text)
            except:
                pass
        return None
