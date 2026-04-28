# Project: Lead Generation & CRM Web App

## Overview
A tool for freelancers to find local businesses using OpenStreetMap (Overpass API) and manage them as leads.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** HTML + TailwindCSS
- **Database:** SQLite (SQLAlchemy)
- **External API:** OpenStreetMap Overpass API (FREE)

## Project Structure
- `app/`
    - `database/`: DB connection and session management
    - `models/`: SQLAlchemy models and Pydantic schemas
    - `routers/`: API endpoints (Leads CRUD, Search)
    - `services/`: Business logic (OSM search, lead scoring)
    - `static/`: CSS/JS files
    - `templates/`: HTML templates (Dashboard, Search, List, Detail)
- `venv/`: Virtual environment
- `main.py`: Application entry point

## Roadmap
- [x] Initial Project Setup
- [x] Database Schema & Models
- [x] OSM (Overpass API) Service Implementation (Enhanced with Geocoding & Radius Search)
- [x] Resilient API logic (User-Agent rotation to bypass 406 errors)
- [x] Lead Scoring Logic (Prioritizing businesses without websites)
- [x] Backend API Implementation
- [x] Frontend UI (Responsive tables with horizontal scroll)
- [x] WhatsApp Message Generator
- [x] Final Testing & Documentation

## Current Status
- Project is complete and highly functional.
- **Search System:** Replaced broad area fetching with a high-reliability Geocoding + 10km Radius Search. Any location (suburbs, cities, states) can now be searched.
- **Robustness:** Implemented a resilient request handler with User-Agent rotation to handle Overpass API "406 Not Acceptable" errors and rate limiting.
- **UI Improvements:** Enhanced the results tables with dedicated columns for Address, Contact, and Website, including horizontal scrolling for mobile responsiveness.
- **CRM Features:** Full Save, Update, and Delete functionality for leads is working.
- **WhatsApp Outreach:** Integrated outreach generator is functional.
