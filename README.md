# Lance CRM - Lead Generation Tool for Freelancers

A simple yet powerful tool to find local businesses using OpenStreetMap (Overpass API) and manage them as leads.

## Features
- **OSM Search:** Find businesses by keyword and city for free.
- **Lead Scoring:** Automatically score leads based on website presence, phone availability, and address.
- **CRM:** Save leads, update status (New, Contacted, Closed), and add internal notes.
- **WhatsApp Outreach:** Generate and copy personalized outreach messages.
- **Dashboard:** Track your lead generation progress.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite (SQLAlchemy)
- **Frontend:** HTML + TailwindCSS (Jinja2 Templates)

## Setup Instructions

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment:**
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Server:**
   ```bash
   python main.py
   ```
   Or using uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in Browser:**
   Go to [http://localhost:8000](http://localhost:8000)

## Folder Structure
- `app/`: Source code
  - `database/`: DB config
  - `models/`: DB models and schemas
  - `routers/`: API endpoints
  - `services/`: OSM and scoring logic
  - `templates/`: HTML files
- `main.py`: App entry point
- `sql_app.db`: SQLite database file (generated on first run)
