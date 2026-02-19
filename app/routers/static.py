from fastapi import APIRouter
import json
import os

router = APIRouter()

DATA_PATH = "data/static_data"

# Scraper name -> JSON file mapping
STATIC_SCRAPER_MAP = {
    "mbatopcollege": "mbatopcollege.json",
    "allindiambacollege": "allindiambacollege.json",
    "engineeringtopcollege":"engineeringtopcollege.json",
    "allindiaengineeringcollege":"allindiaengineeringcollege.json",
    # add all 10 static scrapers
}

@router.get("/{scraper_name}")
def get_static_scraper(scraper_name: str):
    if scraper_name not in STATIC_SCRAPER_MAP:
        return {"error": "Static scraper data not found"}
    file_path = os.path.join(DATA_PATH, STATIC_SCRAPER_MAP[scraper_name])
    with open(file_path) as f:
        return json.load(f)
