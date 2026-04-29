# Project: Lead Generation & CRM Web App (Phase 1 Complete)

## Overview
A high-performance tool for freelancers to discover local businesses using OpenStreetMap (Overpass API) and manage them through a professional CRM pipeline.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** HTML5, TailwindCSS (Premium UI), FontAwesome 6
- **Database:** SQLite (SQLAlchemy)
- **External APIs:** OSM Overpass API, Photon (Komoot), Nominatim
- **Key Libraries:** BeautifulSoup4 (Scraping), ThreadPoolExecutor (Parallelism)

## Key Features (Phase 1)
- [x] **Resilient Search Engine:** Uses 5+ global Overpass mirrors with automatic failover and 120s timeouts to bypass rate limits.
- [x] **Advanced Geocoding:** Integrated Photon + Nominatim with coordinate caching and "India-first" fallback for ultra-reliable location detection.
- [x] **Automated Mobile Scraper:** Background service that visits business websites to extract Indian mobile numbers (starting 6-9) while filtering out landlines (020).
- [x] **Dynamic Lead Scoring:** Prioritizes leads based on missing websites, broken links (dead link detection), and contact availability.
- [x] **Persistent Search UI:** Uses SessionStorage to keep search results active even after switching tabs or refreshing.
- [x] **WhatsApp Outreach Engine:** One-click WhatsApp contact with personalized pitch generation and automated number formatting (+91).
- [x] **Premium CRM Dashboard:** High-contrast, mobile-responsive UI for managing lead statuses (New, Contacted, Converted) and internal notes.
- [x] **Google Integration:** Direct "View on Google" and "Open in Maps" shortcuts for instant business verification.

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
- **PHASE 1 COMPLETE:** The tool is stable, optimized, and production-ready.
- **Data Quality:** Significantly improved via multi-source geocoding and automated web scraping.
- **User Experience:** Smooth, persistent search with real-time feedback via Toast notifications.

## Roadmap (Next Steps)
- [ ] **Phase 2:** Google Places API Integration (Premium Data Source).
- [ ] **Phase 2:** Automated Email Extraction from websites.
- [ ] **Phase 2:** Export leads to CSV/Excel.
- [ ] **Deployment:** Host on Cloud (Railway/Render) for mobile usage.
