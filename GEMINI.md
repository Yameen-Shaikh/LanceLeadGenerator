# Project: Lead Generation & CRM Web App (Phase 1 Complete)

## Overview
A high-performance tool for freelancers to discover local businesses using OpenStreetMap (Overpass API) and manage them through a professional CRM pipeline.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** HTML5, TailwindCSS (Premium UI), FontAwesome 6
- **Database:** SQLite (SQLAlchemy)
- **External APIs:** OSM Overpass API, Gemini API (gemini-2.0-flash), Photon, Nominatim
- **Key Libraries:** google-genai (SDK), BeautifulSoup4 (Scraping), SQLAlchemy

## Key Features (Phase 1)
- [x] **Hybrid Search Engine:** Combines 5+ OSM mirrors with **Gemini Search Grounding** for 100% coverage of local businesses.
- [x] **AI-Powered Enrichment:** Uses `gemini-2.0-flash` to autonomously research missing websites and mobile numbers.
- [x] **Advanced Geocoding:** Integrated Photon + Nominatim with coordinate caching for ultra-reliable location detection.
- [x] **Automated Mobile Scraper:** Background service that extracts Indian mobile numbers (starting 6-9) from business websites.
- [x] **Dynamic Lead Scoring:** Prioritizes leads based on missing websites, dead links, and contact availability.
- [x] **Persistent Search UI:** Uses SessionStorage to keep search results active during navigation.
- [x] **WhatsApp Outreach Engine:** One-click contact with personalized (+91) formatted numbers.
- [x] **Premium CRM Dashboard:** High-contrast, mobile-responsive UI for lead management and notes.

## Project Structure
- `app/`
    - `database/`: DB connection and SQLite management
    - `models/`: SQLAlchemy models (Leads, link_status, scoring)
    - `routers/`: API endpoints (FastAPI BackgroundTasks for enrichment)
    - `services/`: 
        - `osm_service.py`: Query logic, mirror rotation, caching
        - `scraper_service.py`: BeautifulSoup regex-based mobile extraction
    - `static/`: CSS/JS files
    - `templates/`: Premium Jinja2 templates (Sticky footer, Toast notifications)
- `main.py`: Entry point

## Current Status
- **PHASE 1 OPTIMIZED:** Upgraded to the modern `google-genai` SDK and `gemini-2.0-flash` model.
- **Improved Grounding:** Switched to the latest AI search tools for higher lead accuracy.
- **Production Ready:** Removed all debug code and implemented structured logging.

## Roadmap (Next Steps)
- [ ] **Phase 2:** Google Places API Integration (Premium Data Source).
- [ ] **Phase 2:** Automated Email Extraction from websites.
- [ ] **Phase 2:** Export leads to CSV/Excel.
- [ ] **Deployment:** Host on Cloud (Railway/Render) for mobile usage.
