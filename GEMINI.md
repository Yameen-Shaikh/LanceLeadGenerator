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
- [x] OSM (Overpass API) Service Implementation (Enhanced with flexible filtering & retry logic)
- [x] Lead Scoring Logic
- [x] Backend API Implementation
- [x] Frontend UI (Dashboard, Search, List, Detail)
- [x] WhatsApp Message Generator
- [x] Final Testing & Documentation

## Current Status
- Project is complete and highly functional.
- OSM Search: Improved reliability using broad area fetching, Python-level keyword filtering, and fallback category mapping (e.g., matching "gym" to "fitness_centre").
- Robustness: Added retry logic and User-Agent headers to handle Overpass API limitations and 406 errors.
- CRM features (Save, Update, Delete) working.
- WhatsApp Outreach integration added.
- Setup instructions provided in README.md.
