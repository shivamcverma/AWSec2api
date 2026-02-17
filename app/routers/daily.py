from fastapi import APIRouter
import json
import os

router = APIRouter()

DATA_PATH = "data/daily_data"

# Scraper name -> JSON file mapping
SCRAPER_MAP = {
    "topmbacollegedetails1_40": "topmbacollegedetails1_40.json",
    "topmbacollegedetails41_80": "topmbacollegedetails41_80.json",
}

@router.get("/{scraper_name}")
def get_scraper_data(scraper_name: str):
    if scraper_name not in SCRAPER_MAP:
        return {"error": "Scraper data not found"}
    file_path = os.path.join(DATA_PATH, SCRAPER_MAP[scraper_name])
    with open(file_path) as f:
        return json.load(f)
