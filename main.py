from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database.database import engine, Base
from app.routers import leads
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lance CRM")

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(leads.router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/search")
async def search_page(request: Request):
    return templates.TemplateResponse(request=request, name="search.html")

@app.get("/leads")
async def leads_page(request: Request):
    data = templates.TemplateResponse(request=request, name="leads.html")
    return data

@app.get("/leads/{lead_id}")
async def lead_detail_page(request: Request, lead_id: int):
    return templates.TemplateResponse(request=request, name="lead_detail.html", context={"lead_id": lead_id})

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", reload=True)
