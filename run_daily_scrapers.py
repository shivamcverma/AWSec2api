import os
import subprocess
from multiprocessing import Pool

SCRAPER_FOLDER = "scrapers/daily"

scrapers = [f for f in os.listdir(SCRAPER_FOLDER) if f.endswith(".py")][:15]

def run_scraper(scraper_file):
    scraper_path = os.path.join(SCRAPER_FOLDER, scraper_file)
    print(f"Running {scraper_file}")

    try:
        subprocess.run(
            ["python3", scraper_path],
            check=True,
            timeout=900
        )
        print(f"{scraper_file} done")
    except subprocess.TimeoutExpired:
        print(f"{scraper_file} timeout")
    except subprocess.CalledProcessError:
        print(f"{scraper_file} failed")

if __name__ == "__main__":
    workers = min(10, os.cpu_count())

    with Pool(workers) as pool:
        pool.map(run_scraper, scrapers)

    print("All scrapers finished")