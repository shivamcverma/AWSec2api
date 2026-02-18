from fastapi import APIRouter
import json
import os

router = APIRouter()

DATA_PATH = "data/daily_data"

# Scraper name -> JSON file mapping
SCRAPER_MAP = {
    "topmbacollegedetails1_40": "topmbacollegedetails1_40.json",
    "topmbacollegedetails41_80": "topmbacollegedetails41_80.json",
    "topmbacollegedetails81_all":"topmbacollegedetails81_all.json",
    "allindiambacollegedetails1_40":"allindiambacollegedetails1_40.json",
    "allindiambacollegedetails41_100":"allindiambacollegedetails41_100.json",
    "allindiambacollegedetails101_140":"allindiambacollegedetails101_140.json",
    "allindiambacollegedetails141_180":"allindiambacollegedetails141_180.json",
    "allindiambacollegedetails181_220":"allindiambacollegedetails181_220.json",
    "allindiambacollegedetails221_260":"allindiambacollegedetails221_260.json",
    "allindiambacollegedetails261_300":"allindiambacollegedetails261_300.json",
    "allindiambacollegedetails301_340":"allindiambacollegedetails301_340.json",
    "allindiambacollegedetails341_370":"allindiambacollegedetails341_370.json",
    "allindiambacollegedetails371_380":"allindiambacollegedetails371_380.json",
    "allindiambacollegedetails381_420":"allindiambacollegedetails381_420.json",
    "distancemba":"distancemba.json",
    "executivemba":"executivemba.json",
    "mba":"mba.json",
    "parttimemba":"parttimemba.json",
    "mbageneralmanagement": "mbageneralmanagement.json",
    "mbainagriculture":"mbainagriculture.json",
    "mbaindataanalytics":"mbaindataanalytics.json",
    "mbaindatascience":"mbaindatascience.json",
    "mbaindigitalmarketing":"mbaindigitalmarketing.json",
    "mbainentrepreneurship":"mbainentrepreneurship.json",
    "onlinemba":"onlinemba.json",
    "allindiaengineeringcollege":"allindiaengineeringcollege.json",
    "atma":"atma.json",
    "cat":"cat.json",
    "cmat":"cmat.json",
    "engineeringcollegedetails1_40":"engineeringcollegedetails1_40.json",
    "engineeringcollegedetails41_80":"engineeringcollegedetails41_80.json",
    "engineeringcollegedetails81_120":"engineeringcollegedetails81_120.json",
    "engineeringcollegedetails121_160":"engineeringcollegedetails121_160.json",
    "engineeringtopcollege":"engineeringtopcollege.json",
    "ibsat":"ibsat.json",
    "kiitee":"kiitee.json",
    "mat":"mat.json",
    "mbainfamilybusiness":"mbainfamilybusiness.json",
    "mbainfinance":"mbainfinance.json",
    "mbainhealthcaremanagement":"mbainhealthcaremanagement.json",
    "mbainhrhumanresource":"mbainhrhumanresource.json",
    "mbaininternationalbusiness":"mbaininternationalbusiness.json",
    "mbainitsystems":"mbainitsystems.json",
    "mbainoperations":"mbainoperations.json",
    "mbainpharmaceuticalmanagement":"mbainpharmaceuticalmanagement.json",
    "mbainsalesmarketing":"mbainsalesmarketing.json",
    "nmat":"nmat.json",
    "productmanagement":"productmanagement.json",
    "snap":"snap.json",
    "upcat":"upcat.json",
    "xat":"xat.json",
    
}

@router.get("/{scraper_name}")
def get_scraper_data(scraper_name: str):
    if scraper_name not in SCRAPER_MAP:
        return {"error": "Scraper data not found"}
    file_path = os.path.join(DATA_PATH, SCRAPER_MAP[scraper_name])
    with open(file_path) as f:
        return json.load(f)
