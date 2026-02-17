from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json, time, os
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://www.shiksha.com"

def create_driver():
    options = Options()
    # options.add_argument("--headless=new")  # Uncomment for headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
       "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Important for Ubuntu runner
    # options.binary_location = "/usr/bin/chromium"

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_all_mba_colleges(driver, total_pages=202):
    all_colleges = []
    c_count = 1  # Counter for actual (non-featured) colleges

    for page in range(1, total_pages + 1):

        if page == 1:
            url = "https://www.shiksha.com/mba/colleges/mba-colleges-india"
        else:
            url = f"https://www.shiksha.com/mba/colleges/mba-colleges-india-{page}"

        try:
            driver.get(url)
            time.sleep(5)

            # 🔑 wait till main container loads
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.ID, "tuplewrapper")
                )
            )

        except TimeoutException:
            print(f"⚠️ Page {page} load timeout — retrying with fresh driver")
            driver.quit()
            driver = create_driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.ID, "tuplewrapper")
                )
            )

        # scroll_to_bottom(driver, pause_time=5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find the main container
        tuple_wrapper = soup.find("div", id="tuplewrapper")
        if not tuple_wrapper:
            continue
        
        # Find all college containers - BOTH featured and regular
        all_tuples = tuple_wrapper.find_all("div", class_="fb6321")
   

        for tuple_div in all_tuples:
            # Check if this is a featured/promoted college
            # Featured colleges usually have different class patterns or "Sponsored" text
            is_featured = False
            
            # Method 1: Check for sponsored/featured indicators
            sponsored_div = tuple_div.find("div", class_="eb4a9b")  # Common class for sponsored label
            if sponsored_div:
                is_featured = True
            
            # Method 2: Check for "Sponsored" text
            if not is_featured:
                sponsored_text = tuple_div.find(string=lambda text: text and "Sponsored" in text)
                if sponsored_text:
                    is_featured = True
            
            # Method 3: Check for different layout patterns
            if not is_featured:
                # Featured colleges often have different structure
                featured_check = tuple_div.find("div", class_="fdb64c")
                if featured_check:
                    # Check if it has the structure of featured colleges
                    fees_label = featured_check.find("label", string="Total Fees")  # Featured use "Total Fees"
                    if fees_label:
                        is_featured = True
     
            
            # Now process only actual (non-featured) colleges
          
            college = {
                "id":f"college_{c_count:03d}",
                "name": None,
                "college_img":None,
                "url": None,
                "location": None,
                "ownership": None,
                "nirf_rank": None,
                "courses_count": None,
                "rating": None,
                "exams": [],
                "fees": None,
                "median_salary": None,
                "is_featured": False  # Always false since we're filtering featured out
            }
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.b47f1d img"))
                )
            except TimeoutException:
                pass  # Image might not exist

            img_div = tuple_div.find("div", class_="b47f1d")
            college_img = None  # Default to None if no image

            if img_div:
                image = img_div.find("img")
                if image:
                    # Check for both src and data-src attributes
                    college_img = image.get("src") or image.get("data-src")

            college["college_img"] = college_img


            content_div = tuple_div.find("div", class_="fdb64c")

            if not content_div:
                continue  # Skip if no content div found

            # Extract name and URL
            h3 = content_div.find("h3")
            if h3:
                college["name"] = h3.get_text(strip=True)
                # Find the parent <a> tag
                a_tag = h3.find_parent("a")
                if a_tag and a_tag.get("href"):
                    college["url"] = BASE_URL + a_tag.get("href")

            # Extract location and ownership info
            location_div = content_div.find("div", class_="ae8f7e")
            if location_div:
                spans = location_div.find_all("span")
                if spans:
                    # First span usually contains location
                    college["location"] = spans[0].get_text(strip=True)
                # Check for ownership (usually second span if present)
                if len(spans) > 1:
                    college["ownership"] = spans[1].get_text(strip=True)
                
                # Check for NIRF ranking
                rank_span = location_div.find("span", class_="dd5f3f")
                if rank_span:
                    college["nirf_rank"] = rank_span.get_text(strip=True)

            # Extract courses count and rating
            courses_block = content_div.find("label", string="Courses Offered")
            if courses_block:
                parent = courses_block.find_next("div", class_="c8c9ee")
                if parent:
                    a = parent.find("a", class_="a7957a")
                    if a:
                        college["courses_count"] = a.get_text(strip=True)
                    rating_a = parent.find("a", class_="a0296e")
                    if rating_a:
                        college["rating"] = rating_a.get_text(strip=True)

            # Extract exams
            exams_block = content_div.find("label", string="Exams Accepted")
            if exams_block:
                ul = exams_block.find_next("ul", class_="e6079e")
                if ul:
                    for li in ul.find_all("li"):
                        exam = li.get_text(strip=True)
                        if exam and "+" not in exam:
                            college["exams"].append(exam)

            # Extract fees - FOCUS ON "Total Tuition Fees" for actual colleges
            fees_block = content_div.find("label", string="Total Tuition Fees")
            if fees_block:
                div = fees_block.find_next("div", class_="c8c9ee")
                if div:
                    college["fees"] = div.get_text(" ", strip=True)
            
            # Also check for "Total Fees" if "Total Tuition Fees" not found (some variations)
            if not college["fees"]:
                fees_block = content_div.find("label", string="Total Fees")
                if fees_block:
                    div = fees_block.find_next("div", class_="c8c9ee")
                    if div:
                        college["fees"] = div.get_text(" ", strip=True)

            # Extract median salary
            salary_block = content_div.find("label", string="Median Salary")
            if not salary_block:  # Some might use "Placement Rating"
                salary_block = content_div.find("label", string="Placement Rating")
            
            if salary_block:
                a = salary_block.find_next("a")
                if a:
                    college["median_salary"] = a.get_text(" ", strip=True)

            all_colleges.append(college)
            c_count += 1
    return all_colleges


if __name__ == "__main__":
    driver = create_driver()
    try:
        data = scrape_all_mba_colleges(driver, total_pages=202)

        TEMP_FILE = "mba_data.tmp.json"
        FINAL_FILE = "mba_data.json"

        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        os.replace(TEMP_FILE, FINAL_FILE)
        print("✅ Data scraped & saved successfully (atomic write)")

    finally:
        driver.quit()