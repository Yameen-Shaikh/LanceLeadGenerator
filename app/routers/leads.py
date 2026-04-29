from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import lead as models
from app.models import schemas
from app.services.osm_service import OSMService, calculate_score
from app.services.scraper_service import ScraperService

router = APIRouter(prefix="/api/leads", tags=["leads"])

def enrich_lead_in_background(lead_id: int, db: Session):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not db_lead:
        return
    
    # 1. Validate Link Status
    if db_lead.website:
        db_lead.link_status = OSMService.check_link_status(db_lead.website)
        
        # 2. Extract Mobile Number if missing or if it's a landline (starts with 020)
        current_phone = db_lead.phone or ""
        is_pune_landline = current_phone.startswith('020') or current_phone.startswith('+9120')
        
        if not current_phone or is_pune_landline:
            scraped_phone = ScraperService.extract_mobile_numbers(db_lead.website)
            if scraped_phone:
                db_lead.phone = scraped_phone
    else:
        db_lead.link_status = "missing"
    
    # 3. Recalculate score based on new info
    lead_dict = {
        "website": db_lead.website,
        "link_status": db_lead.link_status,
        "phone": db_lead.phone,
        "address": db_lead.address
    }
    db_lead.score = calculate_score(lead_dict)
    
    db.commit()

@router.get("/search")
def search_leads(keyword: str, location: str):

    osm_leads = OSMService.search_leads(keyword, location)
    scored_leads = []
    
    for lead in osm_leads:
        score = calculate_score(lead)
        lead['score'] = score
        scored_leads.append(lead)
        
    return scored_leads

@router.post("/", response_model=schemas.Lead)
def create_lead(lead: schemas.LeadCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_lead = models.Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    print(f"DEBUG: Created Lead ID {db_lead.id} for {db_lead.name}")
    
    # Trigger background enrichment
    background_tasks.add_task(enrich_lead_in_background, db_lead.id, db)
    
    return db_lead

@router.get("/", response_model=List[schemas.Lead])
def read_leads(status: str = None, min_score: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Lead)
    if status:
        query = query.filter(models.Lead.status == status)
    if min_score is not None:
        query = query.filter(models.Lead.score >= min_score)
    
    leads = query.order_by(models.Lead.created_at.desc()).all()
    print(f"DEBUG: Returning {len(leads)} leads from DB")
    return leads

@router.get("/{lead_id}", response_model=schemas.Lead)
def read_lead(lead_id: int, db: Session = Depends(get_db)):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.put("/{lead_id}", response_model=schemas.Lead)
def update_lead(lead_id: int, lead: schemas.LeadUpdate, db: Session = Depends(get_db)):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead.status:
        db_lead.status = lead.status
    if lead.notes is not None:
        db_lead.notes = lead.notes
        
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(db_lead)
    db.commit()
    return {"message": "Lead deleted"}

@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    total_leads = db.query(models.Lead).count()
    high_value_leads = db.query(models.Lead).filter(models.Lead.score >= 5).count()
    return {
        "total_leads": total_leads,
        "high_value_leads": high_value_leads
    }
