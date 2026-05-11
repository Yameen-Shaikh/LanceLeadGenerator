from google import genai
from google.genai import types
import logging
import os
import json
import asyncio
import re
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    API_KEY = os.getenv("GEMINI_API_KEY")
    # New SDK client
    client = genai.Client(api_key=API_KEY) if API_KEY else None
    
    MODEL_NAME = "gemini-2.0-flash"

    @staticmethod
    def extract_json(text: str):
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(text)
        except:
            return []

    @staticmethod
    async def search_leads(keyword: str, location: str):
        if not GeminiService.client:
            logging.error("Gemini API Client not initialized. Check API Key.")
            return []

        try:
            prompt = f"""
            Act as a professional lead generation researcher. 
            Find 15 ACTIVE businesses for the category '{keyword}' in '{location}'.
            Return ONLY a JSON list of objects with these keys: 'name', 'address', 'website', 'phone'.
            No markdown formatting.
            """

            # google-genai SDK has a nice async interface
            response = await GeminiService.client.aio.models.generate_content(
                model=GeminiService.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())],
                    response_mime_type="application/json"
                )
            )
            
            if response and response.text:
                leads = GeminiService.extract_json(response.text)
                for lead in leads:
                    lead['lat'] = None
                    lead['lon'] = None
                    lead['source'] = 'gemini-genai-sdk'
                return leads
            return []
        except Exception as e:
            logging.error(f"Gemini GenAI SDK Search Error: {e}")
            return []

    @staticmethod
    async def enrich_missing_data(lead_name: str, address: str):
        if not GeminiService.client:
            return None

        try:
            prompt = f"Find the official website and mobile number for the business '{lead_name}' located at '{address}'. Return only a JSON object with 'website' and 'phone' keys."
            
            response = await GeminiService.client.aio.models.generate_content(
                model=GeminiService.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())],
                    response_mime_type="application/json"
                )
            )
            
            if response and response.text:
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    return json.loads(match.group())
            return None
        except Exception as e:
            logging.error(f"Gemini GenAI SDK Enrich Error: {e}")
            return None
