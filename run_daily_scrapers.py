import os
import subprocess
from multiprocessing import Pool

# Path to daily scrapers folder
SCRAPER_FOLDER = "scrapers/daily"

# List all scraper scripts (assuming .py extension)
scrapers = [
    "topmbacollegedetails1_40.py",
    "topmbacollegedetails41_80.py",
    # add all 190 scraper filenames
]

def run_scraper(scraper_file):
    """
    Run individual scraper safely.
    Output JSON should be written to data/daily_data inside scraper itself
    """
    scraper_path = os.path.join(SCRAPER_FOLDER, scraper_file)
    print(f"Running {scraper_file} ...")
    try:
        # Python3 command to run scraper
        subprocess.run(["python3", scraper_path], check=True)
        print(f"{scraper_file} completed ✅")
    except subprocess.CalledProcessError:
        print(f"Error running {scraper_file} ❌")

if __name__ == "__main__":
    # Optional: run in parallel (adjust number of workers)
    num_workers = 4  # or os.cpu_count()
    with Pool(num_workers) as pool:
        pool.map(run_scraper, scrapers)
    
    # Or if you prefer sequential run:
    # for scraper in scrapers:
    #     run_scraper(scraper)
    
    print("All daily scrapers finished!")
