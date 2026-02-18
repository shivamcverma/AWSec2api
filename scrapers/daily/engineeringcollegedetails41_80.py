from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# ---------------- URLS ----------------
BASE_URL =[
    "https://www.shiksha.com/university/institute-of-chemical-technology-mumbai-36791",
    "https://www.shiksha.com/college/mnit-jaipur-malaviya-national-institute-of-technology-24372",
    "https://www.shiksha.com/university/upes-dehradun-30663",
    "https://www.shiksha.com/college/vnit-nagpur-visvesvaraya-national-institute-of-technology-24399",
    "https://www.shiksha.com/university/saveetha-institute-of-medical-and-technical-sciences-poonamallee-chennai-34281",
    "https://www.shiksha.com/college/symbiosis-institute-of-technology-symbiosis-international-pune-lavale-village-29564",
    "https://www.shiksha.com/college/ssn-college-of-engineering-old-mahabalipuram-road-chennai-23008",
    "https://www.shiksha.com/university/lpu-lovely-professional-university-jalandhar-28499",
    "https://www.shiksha.com/university/nit-durgapur-national-institute-of-technology-54019",
    "https://www.shiksha.com/university/nit-silchar-national-institute-of-technology-28583",
    "https://www.shiksha.com/university/birla-institute-of-technology-mesra-ranchi-24087",
    "https://www.shiksha.com/university/graphic-era-deemed-to-be-university-dehradun-22612",
    "https://www.shiksha.com/college/nit-patna-national-institute-of-technology-23147",
    "https://www.shiksha.com/college/iiest-shibpur-indian-institute-of-engineering-science-and-technology-howrah-24176",
    "https://www.shiksha.com/college/national-institute-of-technology-jalandhar-24247",
    "https://www.shiksha.com/college/iit-jammu-indian-institute-of-technology-53791",
    "https://www.shiksha.com/college/iit-tirupati-indian-institute-of-technology-chittoor-53834",
    "https://www.shiksha.com/university/manipal-university-jaipur-38039",
    "https://www.shiksha.com/college/manipal-institute-of-technology-mahe-3225",
    "https://www.shiksha.com/university/madan-mohan-malviya-university-of-technology-gorakhpur-42983",
    "https://www.shiksha.com/university/iist-indian-institute-of-space-science-and-technology-thiruvananthapuram-25141",
    "https://www.shiksha.com/university/mnnit-allahabad-motilal-nehru-national-institute-of-technology-24357",
    "https://www.shiksha.com/university/iiit-delhi-indraprastha-institute-of-information-technology-32722",
    "https://www.shiksha.com/college/iit-palakkad-indian-institute-of-technology-53829",
    "https://www.shiksha.com/college/nit-delhi-national-institute-of-technology-narela-38584",
    "https://www.shiksha.com/college/sardar-vallabhbhai-national-institute-of-technology-surat-24414",
    "https://www.shiksha.com/college/psgct-coimbatore-19398",
    "https://www.shiksha.com/university/sathyabama-institute-of-science-and-technology-chennai-23588",
    "https://www.shiksha.com/university/international-institute-of-information-technology-bangalore-26396",
    "https://www.shiksha.com/college/netaji-subhas-university-of-technology-dwarka-delhi-28573",
    "https://www.shiksha.com/university/banasthali-vidyapith-jaipur-3155",
    "https://www.shiksha.com/college/iit-bhilai-indian-institute-of-technology-53794",
    "https://www.shiksha.com/college/nit-srinagar-national-institute-of-technology-24264",
    "https://www.shiksha.com/university/uoh-university-of-hyderabad-23069",
    "https://www.shiksha.com/college/ramaiah-institute-of-technology-bangalore-474",
    "https://www.shiksha.com/college/christ-kengeri-campus-kengeri-bangalore-60485",
    "https://www.shiksha.com/college/iit-dharwad-indian-institute-of-technology-53833",
    "https://www.shiksha.com/college/rajiv-gandhi-institute-of-petroleum-technology-amethi-46857",
    "https://www.shiksha.com/college/sant-longowal-institute-of-engineering-and-technology-sangrur-25241",
    "https://www.shiksha.com/university/vignan-s-foundation-for-science-technology-and-research-guntur-21507",
] 

def build_urls(BASE_URL):
    return {
        "college_info":BASE_URL,
        "courses": BASE_URL + "/courses",
        "fees": BASE_URL + "/fees",
        "reviews": BASE_URL + "/reviews",
        "admission": BASE_URL + "/admission",
        "placement": BASE_URL + "/placement",
        "cutoff": BASE_URL + "/cutoff",
        "ranking": BASE_URL + "/ranking",
        "gallery": BASE_URL + "/gallery",
        "infrastructure": BASE_URL + "/infrastructure",
        "faculty": BASE_URL + "/faculty",
        "compare": BASE_URL + "/compare",
        "scholarships": BASE_URL + "/scholarships",
        # "qna": "https://ask.shiksha.com/which-is-better-for-mba-iim-ahmedabad-or-jbims-qna-5114413"
    }
# ---------------- DRIVER ----------------
def create_driver():
    options = Options()

    # Mandatory for GitHub Actions
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Optional but good
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Important for Ubuntu runner
    options.binary_location = "/usr/bin/chromium"

    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(
        service=service,
        options=options
    )

# ---------------- UTILITIES ----------------
def scroll_to_bottom(driver, scroll_times=3, pause=1.5):
    for _ in range(scroll_times):
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(pause)

def scrape_college_info(driver,URLS):
    driver.get(URLS["college_info"])
    wait = WebDriverWait(driver, 30)
    data = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
        "highlights": {
            "summary": None,
            "table": [],
            
        }
    }


        # ================= COVER IMAGE =================
    try:
        section = wait.until(
           (EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")
            )
        )
        )
    except TimeoutException:
        print("⚠️ top header not found, using page source fallback")
        section = driver.find_element(By.TAG_NAME, "body")
    
    img = section.find_element(By.ID, "topHeaderCard-gallery-image")
    
    data["cover_image"] = img.get_attribute("src")

    badges = section.find_elements(By.CLASS_NAME, "b8cb")
    for badge in badges:
        text = badge.text.lower()
        if "video" in text:
            data["videos_count"] = int(re.search(r"\d+", text).group())
        elif "photo" in text:
            data["photos_count"] = int(re.search(r"\d+", text).group())

    # ================= HEADER CARD =================
    header = wait.until(
        EC.presence_of_element_located((By.ID, "top-header-card-heading"))
    )

    try:
        data["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
    except:
        pass
    try:
        data["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    try:
        loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
        if "," in loc:
            data["location"], data["city"] = [x.strip() for x in loc.split(",", 1)]
        else:
            data["location"] = loc
    except:
        pass

    try:
        rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
        match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
        if match:
            data["rating"] = match.group(1)
    except:
        pass

    try:
        reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
        data["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
    except:
        pass

    try:
        qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
        num = re.search(r"[\d.]+", qa_text).group()
        data["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
    except:
        pass

    try:
        items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
        for item in items:
            txt = item.text.lower()
            if "institute" in txt:
                data["institute_type"] = item.text.strip()
            elif "estd" in txt:
                year = re.search(r"\d{4}", item.text)
                if year:
                    data["established_year"] = year.group()
    except:
        pass


        # 🔹 Highlights Table
# ================= HIGHLIGHTS SECTION (JS SAFE) =================
    try:
        highlights = wait.until(
            EC.presence_of_element_located((By.ID, "ovp_section_highlights"))
        )
    
        # 🔹 SUMMARY (already OK, JS se bhi safe)
        summary = driver.execute_script("""
            let el = document.querySelector('#EdContent__ovp_section_highlights');
            if (!el) return null;
            let ps = el.querySelectorAll('p');
            let out = [];
            ps.forEach(p => {
                let t = p.innerText.trim();
                if (t.length > 30) out.push(t);
            });
            return out.join("\\n");
        """)
        data["highlights"]["summary"] = summary
    
    
        # 🔹 TABLE (MAIN FIX)
        table_data = driver.execute_script("""
            let table = document.querySelector('#EdContent__ovp_section_highlights table');
            if (!table) return [];
    
            let rows = table.querySelectorAll('tr');
            let result = [];
    
            rows.forEach((row, idx) => {
                if (idx === 0) return; // skip header
                let cols = row.querySelectorAll('td');
                if (cols.length >= 2) {
                    let key = cols[0].innerText.trim();
                    let val = cols[1].innerText.trim();
                    if (key || val) {
                        result.push({
                            particular: key,
                            details: val
                        });
                    }
                }
            });
            return result;
        """)
        data["highlights"]["table"] = table_data
    
    except Exception as e:
        print("Highlights error:", e)
    
    

    return data

def scrape_college_infopro(driver,URLS):
    driver.get(URLS["college_info"])
    wait = WebDriverWait(driver, 30)

    popular = {
        "intro": None,
        "courses": [],
        "faqs": []
    }

    # ================= SECTION WAIT =================
    wait.until(
        EC.presence_of_element_located(
            (By.ID, "ovp_section_popular_courses")
        )
    )

    # ================= INTRO / SUMMARY =================
    popular["intro"] = driver.execute_script("""
       let el = document.querySelector('#EdContent__ovp_section_popular_courses');
       if (!el) return null;
   
       let ps = el.querySelectorAll('p');
       let out = [];
   
       ps.forEach(p => {
           let t = p.textContent.replace(/\\s+/g, ' ').trim();
           if (t.length > 20) out.push(t);
       });
   
       return out.join("\\n");
       """)

    # ================= COURSES (FIXED) =================
    courses = driver.execute_script("""
        let result = [];

        document.querySelectorAll('div.base_course_tuple > div[id^="tuple_"]').forEach(tuple => {

            let course = {};

            // name + url
            let h3 = tuple.querySelector('h3');
            course.course_name = h3 ? h3.innerText.trim() : null;
            course.course_url = h3 ? h3.closest('a')?.href : null;

            // duration
            let spans = tuple.querySelectorAll('.edfa span');
            course.duration = spans.length > 1 ? spans[1].innerText.trim() : null;

            // rating + reviews
            let ratingBlock = tuple.querySelector('a[href*="reviews"]');
            if (ratingBlock) {
                course.rating = ratingBlock.querySelector('span')?.innerText.trim() || null;
                let r = ratingBlock.querySelector('.e040');
                course.reviews = r ? r.innerText.replace(/[()]/g, '') : null;
            }

            // ranking
            course.ranking =
                tuple.querySelector('.ba04')?.innerText.trim() || null;

            // ===== EXAMS ACCEPTED (SAFE) =====
            course.exams = [];
            tuple.querySelectorAll('label').forEach(label => {
                if (label.innerText.includes('Exams Accepted')) {
                    let ul = label.parentElement.querySelector('ul');
                    if (ul) {
                        ul.querySelectorAll('a').forEach(a => {
                            course.exams.push(a.innerText.trim());
                        });
                    }
                }
            });

            // ===== FEES =====
            course.fees = null;
            tuple.querySelectorAll('label').forEach(label => {
                if (label.innerText.includes('Total Tuition Fees')) {
                    let div = label.parentElement.querySelector('div');
                    if (div) {
                        course.fees = div.innerText.replace('Get Fee Details', '').trim();
                    }
                }
            });

            // ===== SALARY / PLACEMENT =====
            course.median_salary = null;
            tuple.querySelectorAll('label').forEach(label => {
                if (
                    label.innerText.includes('Median Salary') ||
                    label.innerText.includes('Placement Rating')
                ) {
                    let span = label.parentElement.querySelector('span');
                    if (span) {
                        course.median_salary = span.innerText.trim();
                    }
                }
            });

            result.push(course);
        });

        return result;
    """)
    popular["courses"] = courses

    # ================= FAQs =================
    faqs = driver.execute_script("""
        let faqs = [];
        document.querySelectorAll('#sectional-faqs-0 strong').forEach(q => {
            let question = q.innerText.replace('Q:', '').trim();
            let ansBox = q.parentElement.nextElementSibling;
            let answer = ansBox ? ansBox.innerText.replace('A:', '').trim() : "";
            if (question) {
                faqs.push({ question, answer });
            }
        });
        return faqs;
    """)
    popular["faqs"] = faqs

    return popular

def scrape_courses(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    
    driver.get(URLS["courses"])
    wait = WebDriverWait(driver, 20)
    # ---------- COVER IMAGE ----------
    section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
    img = section.find_element(By.ID, "topHeaderCard-gallery-image")
    college_info["college_name"] = img.get_attribute("alt")
    college_info["cover_image"] = img.get_attribute("src")

    badges = section.find_elements(By.CLASS_NAME, "b8cb")
    for badge in badges:
        text = badge.text.lower()
        if "video" in text:
            college_info["videos_count"] = int(re.search(r"\d+", text).group())
        elif "photo" in text:
            college_info["photos_count"] = int(re.search(r"\d+", text).group())

    # ---------- HEADER CARD ----------
    header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

    try:
        college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
    except:
        pass

    try:
        college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    try:
        loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
        if "," in loc:
            college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
        else:
            college_info["location"] = loc
    except:
        pass

    try:
        rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
        match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
        if match:
            college_info["rating"] = match.group(1)
    except:
        pass

    try:
        reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
        college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
    except:
        pass

    try:
        qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
        num = re.search(r"[\d.]+", qa_text).group()
        college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
    except:
        pass

    try:
        items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
        for item in items:
            txt = item.text.lower()
            if "institute" in txt:
                college_info["institute_type"] = item.text.strip()
            elif "estd" in txt:
                year = re.search(r"\d{4}", item.text)
                if year:
                    college_info["established_year"] = year.group()
    except:
        pass


    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table._1708")))

    def scroll_to_bottom(driver, scroll_times=3, pause=1.5):
 
       for _ in range(scroll_times):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(pause)
    driver.get(URLS["courses"])
    scroll_to_bottom(driver, scroll_times=3, pause=2)  # Courses page ke liye scroll


    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("table._1708 tbody tr")
    courses = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        course_name = cols[0].get_text(" ", strip=True)
        fees = cols[1].get_text(" ", strip=True).replace("Get Fee Details", "").strip()

        eligibility = {}
        exams = []

        if len(cols) > 2:
            grad = cols[2].find("span", string=lambda x: x and "Graduation" in x)
            if grad:
                eligibility["graduation"] = grad.find_next("span").get_text(strip=True)

            exams = [a.get_text(strip=True) for a in cols[2].select("a")]
            if exams:
                eligibility["exams"] = exams

        courses.append({
            "course_name": course_name,
            "fees": fees,
            "eligibility": eligibility
        })

    return {"college_info": college_info, "courses": courses}


# ---------------- FEES ----------------
def scrape_fees(driver,URLS):
    driver.get(URLS["fees"])
    wait = WebDriverWait(driver, 20)
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ Top header section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ fees card not found")
    fees_data = []

    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "table.table._26d3"))
    )

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("table.table._26d3 tbody tr")

    for row in rows:
        course_a = row.select_one("td:nth-child(1) a")
        fee_div = row.select_one("td:nth-child(2) div.getFeeDetailsCTA__text")

        if not course_a or not fee_div:
            continue

        fees = fee_div.get_text(" ", strip=True).replace("Get Fee Details", "").strip()

        fees_data.append({
            "course": course_a.get_text(strip=True),
            "total_tuition_fees": fees
        })
    return {"college_info": college_info, "fees_data": fees_data}


# ---------------- REVIEW SUMMARY ----------------
def scrape_review_summary(driver,URLS):
    driver.get(URLS["reviews"])
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    wait = WebDriverWait(driver, 15)

    # ---------- COVER IMAGE ----------
    section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
    img = section.find_element(By.ID, "topHeaderCard-gallery-image")
    college_info["college_name"] = img.get_attribute("alt")
    college_info["cover_image"] = img.get_attribute("src")

    badges = section.find_elements(By.CLASS_NAME, "b8cb")
    for badge in badges:
        text = badge.text.lower()
        if "video" in text:
            college_info["videos_count"] = int(re.search(r"\d+", text).group())
        elif "photo" in text:
            college_info["photos_count"] = int(re.search(r"\d+", text).group())

    # ---------- HEADER CARD ----------
    header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

    try:
        college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
    except:
        pass

    try:
        college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    try:
        loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
        if "," in loc:
            college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
        else:
            college_info["location"] = loc
    except:
        pass

    try:
        rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
        match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
        if match:
            college_info["rating"] = match.group(1)
    except:
        pass

    try:
        reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
        college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
    except:
        pass

    try:
        qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
        num = re.search(r"[\d.]+", qa_text).group()
        college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
    except:
        pass

    try:
        items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
        for item in items:
            txt = item.text.lower()
            if "institute" in txt:
                college_info["institute_type"] = item.text.strip()
            elif "estd" in txt:
                year = re.search(r"\d{4}", item.text)
                if year:
                    college_info["established_year"] = year.group()
    except:
        pass
    summary = {
        "college_name": "",
        "overall_rating": "",
        "total_verified_reviews": "",
        "rating_distribution": {},
        "category_ratings": {}
    }

    # Page thoda scroll karo taki summary load ho jaye
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 🔥 MAIN SUMMARY CARD (paper-card bfe9)
    main_card = soup.select_one("div.paper-card.bfe9")
    if not main_card:
        print("❌ Review summary main card not found")
        return summary

    # -------- COLLEGE NAME --------
    college = main_card.select_one("div.fe79")
    if college:
        summary["college_name"] = college.get_text(strip=True)

    # -------- OVERALL RATING --------
    overall = main_card.select_one("span._6ac2")
    if overall:
        summary["overall_rating"] = overall.get_text(strip=True).replace("/5", "")

    # -------- TOTAL VERIFIED REVIEWS --------
    total = main_card.select_one("span._03a5")
    if total:
        summary["total_verified_reviews"] = total.get_text(strip=True)\
            .replace("Verified Reviews", "").strip()

    # -------- RATING DISTRIBUTION (4-5, 3-4, 2-3) --------
    for li in main_card.select("ul._8c4d li"):
        label = li.select_one("span._4826")
        count = li.select_one("span.c230")
        if label and count:
            summary["rating_distribution"][label.get_text(strip=True)] = count.get_text(strip=True)

    # -------- CATEGORY RATINGS (Placements, Infra, Faculty...) --------
    for card in main_card.select("div.paper-card.boxShadow._4b5c"):
        category = card.select_one("span._7542")
        rating = card.select_one("span._1b94 span")
        if category and rating:
            summary["category_ratings"][category.get_text(strip=True)] = rating.get_text(strip=True)

    return {"college_info":college_info,"summary":summary,}



# ---------------- REVIEWS ----------------
def scrape_reviews(driver,URLS):
    reviews = []

    driver.get(URLS["reviews"])
    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.paper-card"))
    )

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.select("div.paper-card")

    for card in cards:
        title = card.select_one("div._1298")
        detail_block = card.select_one("div.cf9e.false")

        if not title or not detail_block:
            continue

        review = {
            "reviewer_name": (card.select_one("span._1bfc") or "").get_text(strip=True) if card.select_one("span._1bfc") else "",
            "course": (card.select_one("div._4efe a") or "").get_text(strip=True) if card.select_one("div._4efe a") else "",
            "overall_rating": (card.select_one("div._304d span") or "").get_text(strip=True) if card.select_one("div._304d span") else "",
            "review_title": title.get_text(strip=True),
            "review_date": (card.select_one("span._4dae") or "").get_text(strip=True) if card.select_one("span._4dae") else "",
            "detailed_review": {}
        }

        for sec in detail_block.find_all("div", recursive=False):
            key = sec.find("strong")
            val = sec.find("span")
            if key and val:
                review["detailed_review"][key.get_text(strip=True).replace(":", "")] = val.get_text(strip=True)

        reviews.append(review)

    return reviews

def scrape_admission_overview(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["admission"])
    wait = WebDriverWait(driver, 15)

    # ---------- COVER IMAGE ----------
    section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
    img = section.find_element(By.ID, "topHeaderCard-gallery-image")
    college_info["college_name"] = img.get_attribute("alt")
    college_info["cover_image"] = img.get_attribute("src")

    badges = section.find_elements(By.CLASS_NAME, "b8cb")
    for badge in badges:
        text = badge.text.lower()
        if "video" in text:
            college_info["videos_count"] = int(re.search(r"\d+", text).group())
        elif "photo" in text:
            college_info["photos_count"] = int(re.search(r"\d+", text).group())

    # ---------- HEADER CARD ----------
    header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

    try:
        college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
    except:
        pass

    try:
        college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    try:
        loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
        if "," in loc:
            college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
        else:
            college_info["location"] = loc
    except:
        pass

    try:
        rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
        match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
        if match:
            college_info["rating"] = match.group(1)
    except:
        pass

    try:
        reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
        college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
    except:
        pass

    try:
        qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
        num = re.search(r"[\d.]+", qa_text).group()
        college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
    except:
        pass

    try:
        items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
        for item in items:
            txt = item.text.lower()
            if "institute" in txt:
                college_info["institute_type"] = item.text.strip()
            elif "estd" in txt:
                year = re.search(r"\d{4}", item.text)
                if year:
                    college_info["established_year"] = year.group()
    except:
        pass
    admission = {
        "title": "",
        "overview_text": "",
        "faqs": []
    }

    driver.get(URLS["admission"])
    wait = WebDriverWait(driver, 15)

    # Page ko thoda scroll karao (accordion + wiki load ke liye)
    for _ in range(4):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # -------- TITLE --------
    title = soup.select_one("div#admission_section_admission_overview h2 div._6a22")
    if title:
        admission["title"] = title.get_text(strip=True)

    # -------- OVERVIEW TEXT --------
    overview_block = soup.select_one(
        "div#EdContent__admission_section_admission_overview"
    )

    if overview_block:
        paragraphs = overview_block.find_all("p")
        admission["overview_text"] = "\n\n".join(
            p.get_text(" ", strip=True) for p in paragraphs
        )

    # -------- FAQs (Questions & Answers) --------
    faq_blocks = soup.select("div.sectional-faqs > div.listener")

    for q_block in faq_blocks:
        question = q_block.get_text(" ", strip=True).replace("Q:", "").strip()

        answer_block = q_block.find_next("div", class_="_16f53f")
        answer = ""

        if answer_block:
            p_tags = answer_block.select("div._843b17 p")
            answer = " ".join(p.get_text(" ", strip=True) for p in p_tags)

        if question and answer:
            admission["faqs"].append({
                "question": question,
                "answer": answer
            })

    return {"college_info":college_info,"admission":admission}

def scrape_admission_eligibility_selection(driver,URLS):
    data = {
        "title": "",
        "intro_text": "",
        "eligibility_table": [],
        "faqs": []
    }

    driver.get(URLS["admission"])
    wait = WebDriverWait(driver, 15)

    # Scroll so accordion content loads
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 900);")
        time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # ================= TITLE =================
    title = soup.select_one(
        "#admission_section_eligibility_selection h2 div._6a22"
    )
    if title:
        data["title"] = title.get_text(strip=True)

    # ================= INTRO PARAGRAPH =================
    intro = soup.select_one(
        "#EdContent__admission_section_eligibility_selection p"
    )
    if intro:
        data["intro_text"] = intro.get_text(" ", strip=True)

    # ================= TABLE =================
    table = soup.select_one(
        "#EdContent__admission_section_eligibility_selection table._895c"
    )

    if table:
        rows = table.select("tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            course = cols[0].get_text(" ", strip=True)
            eligibility = cols[1].get_text(" ", strip=True)
            selection = cols[2].get_text(" ", strip=True)

            data["eligibility_table"].append({
                "course": course,
                "eligibility": eligibility,
                "selection_criteria": selection
            })

    # ================= FAQs =================
    faq_blocks = soup.select("div.sectional-faqs > div.listener")

    for q in faq_blocks:
        question = q.get_text(" ", strip=True)
        question = question.replace("Q:", "").strip()

        ans_block = q.find_next("div", class_="_16f53f")
        answer = ""

        if ans_block:
            answer = ans_block.get_text(" ", strip=True)
            answer = answer.replace("A:", "").strip()

        if question and answer:
            data["faqs"].append({
                "question": question,
                "answer": answer
            })

    return data

def scrape_placement_report(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["placement"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ placement section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ placement college info card not found")
    data = {
        "title": "",
        "summary": [],
        "faqs": []
    }

    driver.get(URLS["placement"])
    wait = WebDriverWait(driver, 15)

    # Scroll to load placement section
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.select_one("section#placement_section_report")
    if not section:
        return data

    # ================= TITLE =================
    title = section.select_one("h2 div._6a22")
    if title:
        data["title"] = title.get_text(strip=True)

    # ================= SUMMARY PARAGRAPHS =================
    paragraphs = section.select(
        "#EdContent__placement_section_report p"
    )
    for p in paragraphs:
        text = p.get_text(" ", strip=True)
        if text:
            data["summary"].append(text)

    # ================= FAQs =================
    faq_questions = section.select("div.sectional-faqs > div.listener")

    for q in faq_questions:
        question = q.get_text(" ", strip=True)
        question = question.replace("Q:", "").strip()

        ans_block = q.find_next("div", class_="_16f53f")
        answer_text = ""
        tables = []

        if ans_block:
            # Answer text
            answer_text = ans_block.get_text(" ", strip=True)
            answer_text = answer_text.replace("A:", "").strip()

            # Tables inside answer
            for table in ans_block.select("table"):
                headers = [th.get_text(strip=True) for th in table.select("tr th")]
                rows = []

                for tr in table.select("tr")[1:]:
                    cols = [td.get_text(" ", strip=True) for td in tr.select("td")]
                    if cols:
                        rows.append(cols)

                tables.append({
                    "headers": headers,
                    "rows": rows
                })

        if question:
            data["faqs"].append({
                "question": question,
                "answer": answer_text,
                "tables": tables
            })

    return {"college_info":college_info,"data":data}

def scrape_average_package_section(driver,URLS):
    driver.get(URLS["placement"])
    data = {
        "title": "",
        "intro": "",
        "average_package_table": [],
        "top_recruiters": [],
        "insights": [],
        "faqs": []
    }

    
    wait = WebDriverWait(driver, 15)

    # Scroll to load section
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 900);")
        time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.select_one("section#placement_section_average_package")
    if not section:
        return data

    # ---------------- TITLE ----------------
    title = section.select_one("h2 div._6a22")
    if title:
        data["title"] = title.get_text(strip=True)

    # ---------------- INTRO TEXT ----------------
    intro = section.select_one("#EdContent__placement_section_average_package p")
    if intro:
        data["intro"] = intro.get_text(" ", strip=True)

    # ---------------- MAIN TABLE ----------------
    table = section.select_one("#EdContent__placement_section_average_package table")
    if table:
        headers = [th.get_text(strip=True) for th in table.select("tr th")]
        for row in table.select("tr")[1:]:
            cols = [td.get_text(" ", strip=True) for td in row.select("td")]
            if cols:
                data["average_package_table"].append(dict(zip(headers, cols)))

    # ---------------- TOP RECRUITERS ----------------
    recruiters = section.select("div._140ef9 span._58be47")
    data["top_recruiters"] = [r.get_text(strip=True) for r in recruiters]

    # ---------------- INSIGHTS ----------------
    insight_cards = section.select("div._58c8")
    for card in insight_cards:
        heading = card.select_one("h6")
        text = card.select_one("p")

        if heading and text:
            data["insights"].append({
                "title": heading.get_text(strip=True),
                "description": text.get_text(strip=True)
            })

    # ---------------- FAQs ----------------
    faq_questions = section.select("div.sectional-faqs > div.listener")

    for q in faq_questions:
        question = q.get_text(" ", strip=True).replace("Q:", "").strip()
        ans_block = q.find_next("div", class_="_16f53f")

        answer_text = ""
        tables = []

        if ans_block:
            answer_text = ans_block.get_text(" ", strip=True).replace("A:", "").strip()

            for t in ans_block.select("table"):
                headers = [th.get_text(strip=True) for th in t.select("tr th")]
                rows = []

                for tr in t.select("tr")[1:]:
                    cols = [td.get_text(" ", strip=True) for td in tr.select("td")]
                    if cols:
                        rows.append(cols)

                tables.append({
                    "headers": headers,
                    "rows": rows
                })

        data["faqs"].append({
            "question": question,
            "answer": answer_text,
            "tables": tables
        })

    return data

def scrape_placement_faqs(driver,URLS):
    faqs = []

    

    driver.get(URLS["placement"])
    time.sleep(5)

    # lazy load ke liye scroll
    for _ in range(8):
        driver.execute_script("window.scrollBy(0, 1200)")
        time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 👉 Question blocks
    questions = soup.select("div.html-0.c5db62.listener")

    for q in questions:
        question_text = q.get_text(" ", strip=True)
        question_text = question_text.replace("Q:", "").strip()

        answer_div = q.find_next_sibling("div", class_="_16f53f")
        if not answer_div:
            continue

        answer_paragraphs = []
        tables = []

        # ---- text ----
        for p in answer_div.select("p"):
            txt = p.get_text(" ", strip=True)
            if txt and "Ask Shiksha GPT" not in txt:
                answer_paragraphs.append(txt)

        # ---- tables ----
        for table in answer_div.select("table"):
            headers = [th.get_text(" ", strip=True) for th in table.select("tr th")]
            rows = []

            for tr in table.select("tr")[1:]:
                cols = [td.get_text(" ", strip=True) for td in tr.select("td")]
                if cols:
                    rows.append(cols)

            tables.append({
                "headers": headers,
                "rows": rows
            })

        faqs.append({
            "question": question_text,
            "answer": " ".join(answer_paragraphs),
            "tables": tables
        })

    return faqs

# ---------------- CUTOFF ----------------

def scrape_cutoff(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["cutoff"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ cutoff img section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ cutoff info not found")
    result = []

    driver.get(URLS["cutoff"])
    wait = WebDriverWait(driver, 15)

    try:
        cutoff_section = wait.until(
            EC.presence_of_element_located(
                (By.ID, "icop_section_latest_round_cutoff_327")
            )
        )
    except:
        print("⚠️ scrape_cutoff not available, skipping")
        return None

    # --- Expand qualifying cutoff accordion using JS click ---
    try:
        accordion_icon = cutoff_section.find_element(By.CSS_SELECTOR, "img._377d._7ef0")
        driver.execute_script("arguments[0].scrollIntoView(true);", accordion_icon)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", accordion_icon)  # JS click avoids interception
        time.sleep(2)  # wait for table to render
    except Exception as e:
        print("Accordion click error:", e)

    # --- Extract qualifying cutoff table using JS + BeautifulSoup ---
    qualifying_cutoff = []
    try:
        # Wait until table rows are present
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "#icop_section_latest_round_cutoff_327 div.wikiContents table tbody tr")
            )
        )
    
        # Get table HTML directly within the cutoff section
        table_html = driver.execute_script(
            "return document.querySelector('#icop_section_latest_round_cutoff_327 div.wikiContents table').outerHTML;"
        )
        soup = BeautifulSoup(table_html, "html.parser")
    
        headers = [th.get_text(strip=True) for th in soup.select("thead th")]
        rows = soup.select("tbody tr")
        for row in rows:
            cols = row.find_all("td")
            row_dict = {headers[i]: cols[i].get_text(strip=True) if i < len(cols) else "" for i in range(len(headers))}
            qualifying_cutoff.append(row_dict)
    except Exception as e:
        print("Qualifying table parse error:", e)
    
    result.append({"type": "qualifying_cutoff", "table": qualifying_cutoff})

    # --- Extract course-wise cutoffs ---
    try:
        course_divs = cutoff_section.find_elements(By.CSS_SELECTOR, "div.multipleTableContainer > div")
        for div in course_divs:
            try:
                course_name = div.find_element(By.CSS_SELECTOR, "h5 span").text.strip()
                
                # Get course table HTML via JS within this div
                table_html = driver.execute_script(
                    "return arguments[0].querySelector('table').outerHTML;", div
                )
                soup = BeautifulSoup(table_html, "html.parser")
                headers = [th.get_text(strip=True) for th in soup.select("thead th")]
                rows = soup.select("tbody tr")
                rows_data = []
                for row in rows:
                    cols = row.find_all("td")
                    row_dict = {headers[i]: cols[i].get_text(strip=True) if i < len(cols) else "" for i in range(len(headers))}
                    rows_data.append(row_dict)

                result.append({
                    "type": "course_cutoff",
                    "course_name": course_name,
                    "cutoff_table": rows_data
                })
            except Exception as e:
                print("Course parse error:", e)
                continue
    except Exception as e:
        print("Course container error:", e)

    return {"college_info":college_info,"result":result}

def scrape_ranking(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }


    driver.get(URLS["ranking"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ Top header section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ Header card not found")
    result = []

    driver.get(URLS["ranking"])
    wait = WebDriverWait(driver, 15)

    # --- wait for ranking section ---
    
    try:
        ranking_section = wait.until(
            EC.presence_of_element_located(
                (By.ID, "rp_section_international_ranking")
            )
        )
    except:
        print("⚠️scrape_ranking not available, skipping")
        return None

    # --- expand accordion ---
    try:
        icon = ranking_section.find_element(By.CSS_SELECTOR, "img._377d._7ef0")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", icon)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", icon)
        time.sleep(0.5)
    except:
        pass

    # --- wait for content block ---
    content_div = wait.until(
        EC.presence_of_element_located(
            (By.ID, "EdContent__rp_section_international_ranking")
        )
    )

    # --- get FULL HTML of content ---
    html = driver.execute_script(
        "return arguments[0].innerHTML;", content_div
    )

    soup = BeautifulSoup(html, "html.parser")

    # ================= HEADING =================
    try:
        title = ranking_section.find_element(By.CSS_SELECTOR, "h2 div").text.strip()
    except:
        title = ""

    # ================= PARAGRAPHS =================
    description = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            description.append(text)

    # ================= TABLE =================
    tables = []
    for table in soup.find_all("table"):
        table_rows = []
        for row in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
            if cells:
                table_rows.append(cells)
        if table_rows:
            tables.append(table_rows)

    result.append({
        "type": "international_ranking",
        "title": title,
        "description": description,
        "tables": tables
    })

    return {"college_info":college_info,"result":result}

def scrape_ranking_section(driver,URLS):
    driver.get(URLS["ranking"])
    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.find("section", id="rp_section_publishers_8")
    if not section:
        return {}

    result = {
        "title": "",
        "description": "",
        "tables": []
    }

    # ---- TITLE ----
    h2 = section.find("h2")
    if h2:
        result["title"] = h2.get_text(strip=True)

    # ---- DESCRIPTION (paragraph text) ----
    paragraphs = section.find_all("p")
    result["description"] = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

    # ---- ALL TABLES ----
    for table in section.find_all("table"):
        table_data = []

        # headers
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        for row in table.find_all("tr"):
            cols = [td.get_text(" ", strip=True) for td in row.find_all("td")]

            if not cols:
                continue

            if headers and len(headers) == len(cols):
                table_data.append(dict(zip(headers, cols)))
            else:
                table_data.append(cols)

        if table_data:
            result["tables"].append(table_data)

    return result



def parse_ranking_criteria_html(driver,URLS):
    driver.get(URLS["ranking"])
    wait = WebDriverWait(driver, 15)

    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.ID, "EdContent__rp_section_publisher_ranking_criteria")
            )
        )
    except:
        print("⚠️ parse_ranking_criteria_html not available, skipping")
        return None

    # 🔥 scroll so lazy images load
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", section)
    time.sleep(2)

    html = driver.execute_script(
        "return arguments[0].innerHTML;", section
    )

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "description": "",
        "table": [],
        "images": []
    }

    # ✅ description
    p = soup.find("p")
    if p:
        data["description"] = p.get_text(strip=True)

    # ✅ table
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]

        for row in rows[1:]:
            values = [td.get_text(strip=True) for td in row.find_all("td")]
            if values:
                data["table"].append(dict(zip(headers, values)))

    # ✅ images (lazy-load safe)
    images = set()
    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-original")
        )
        if src and src.startswith("http"):
            images.add(src)

    data["images"] = list(images)

    return data

def scrape_mini_clips(driver, URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["gallery"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ gallary section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ gallary info not found")
    driver.get(URLS["gallery"])
    wait = WebDriverWait(driver, 15)

    data = {
        "section_title": "Mini Clips",
        "clips": []
    }

    try:
        # ✅ wait for widget
        widget = wait.until(
            EC.presence_of_element_located((By.ID, "reelsWidget"))
        )

        # ✅ force scroll (VERY IMPORTANT)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", widget
        )
        time.sleep(3)

        # ✅ wait until clips appear
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "#reelsWidget li._7c2b")
            )
        )

        clips = driver.find_elements(By.CSS_SELECTOR, "#reelsWidget li._7c2b")

        for clip in clips:
            clip_data = {
                "title": "",
                "thumbnail": "",
            }

            # 🖼️ thumbnail
            try:
                img = clip.find_element(By.TAG_NAME, "img")
                clip_data["thumbnail"] = img.get_attribute("src")
            except:
                pass

            # 📝 title
            try:
                title = clip.find_element(By.CSS_SELECTOR, "._4a7330")
                clip_data["title"] = title.text.strip()
            except:
                pass

            if any(clip_data.values()):
                data["clips"].append(clip_data)

    except:
        print("⚠️ Mini clips section not available, skipping")

    return {"college_info":college_info,"data":data}


def scrape_hostel_campus_structured(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["infrastructure"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ Top header section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ Header card not found")
    driver.get(URLS["infrastructure"])
    wait = WebDriverWait(driver, 30)


    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,"div.wikkiContents")
            )
        )
    except:
        print("⚠️ scrape_hostel_campus_structured not available, skipping")
        return None

    html = driver.execute_script("return arguments[0].innerHTML;", section)
    soup = BeautifulSoup(html, "html.parser")

    result = {
        "author": "",
        "updated_on": "",
        "sections": []
    }

    # ✅ Author
    author = soup.select_one(".adp_usr_dtls a")
    if author:
        result["author"] = author.get_text(strip=True)

    # ✅ Updated date
    updated = soup.select_one(".post-date")
    if updated:
        result["updated_on"] = updated.get_text(strip=True)

    content_root = soup.select_one(".abtSection")
    if not content_root:
        return result

    current_section = {
        "heading": "Introduction",
        "text": [],
        "list": [],
        "images": [],
        "videos": [],
        "tables": []
    }

    def push_section():
        if (
            current_section["text"]
            or current_section["list"]
            or current_section["images"]
            or current_section["videos"]
            or current_section["tables"]
        ):
            result["sections"].append(current_section.copy())

    # ✅ Traverse content in order
    for tag in content_root.find_all(
        ["h2", "h3", "p", "ul", "img", "iframe", "table"],
        recursive=True
    ):

        # 🔹 New section starts
        if tag.name in ["h2", "h3"]:
            push_section()
            current_section = {
                "heading": tag.get_text(strip=True),
                "text": [],
                "list": [],
                "images": [],
                "videos": [],
                "tables": []
            }

        elif tag.name == "p":
            # Skip paragraphs inside table
            if tag.find_parent("table"):
                continue
            text = tag.get_text(" ", strip=True)
            if text:
                current_section["text"].append(text)

        elif tag.name == "ul":
            for li in tag.find_all("li"):
                li_text = li.get_text(strip=True)
                if li_text:
                    current_section["list"].append(li_text)

        elif tag.name == "img":
            src = (
                tag.get("data-src")
                or tag.get("data-original")
                or tag.get("src")
            )
            if src and src.startswith("http"):
                current_section["images"].append(src)

        elif tag.name == "iframe":
            src = tag.get("src")
            if not src:
                continue
            video = {
                "video_url": src,
                "video_id": "",
                "title": tag.get("title", "")
            }
            if "embed/" in src:
                video["video_id"] = src.split("embed/")[1].split("?")[0]
            current_section["videos"].append(video)

        elif tag.name == "table":
            table_data = []
            rows = tag.find_all("tr")
            if rows:
                headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
                for row in rows[1:]:
                    values = [td.get_text(strip=True) for td in row.find_all("td")]
                    if values:
                        if headers and len(headers) == len(values):
                            table_data.append(dict(zip(headers, values)))
                        else:
                            table_data.append(values)
            if table_data:
                current_section["tables"].append(table_data)

    push_section()
    return {"college_info":college_info,"result":result}

def scrape_infrastructure_structured(driver, URLS):
    driver.get(URLS["infrastructure"])
    wait = WebDriverWait(driver, 15)

    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "infrastructureSection")))
        html = driver.execute_script("return arguments[0].innerHTML;", section)
    except:
        print("⚠️ Infrastructure section not found. Skipping...")
        return {
            "section": "",
            "facilities": [],
            "other_facilities": []
        }

    soup = BeautifulSoup(html, "html.parser")

    result = {
        "section": "",
        "facilities": [],
        "other_facilities": []
    }

    # Section title
    title_tag = soup.find("h2", class_="tbSec2")
    if title_tag:
        result["section"] = title_tag.get_text(strip=True)

    # Main facilities
    for li in soup.select("ul.infraDataList > li"):
        # Handle other major facilities without dtl
        if li.find_all("div", class_="icn") and not li.find("div", class_="dtl"):
            other_list = [i.get_text(strip=True) for i in li.find_all("strong")]
            result["facilities"].append({
                "name": "Other Major Facilities",
                "list": other_list
            })
            continue

        name_tag = li.find("strong")
        name = name_tag.get_text(strip=True) if name_tag else None
        description_tag = li.find("div", class_="dtl")
        description = ""
        available_facilities = []

        if description_tag:
            p_tag = description_tag.find("p")
            if p_tag:
                description = p_tag.get_text(" ", strip=True)

            child_facility = description_tag.find("div", class_="childFaciltyBox")
            if child_facility:
                spans = [s.get_text(strip=True) for s in child_facility.find_all("span") if s.get_text(strip=True)]
                # Sports / Labs style
                if "|" in child_facility.text:
                    available_facilities = [s for s in spans if s not in ["|", ","]]
                else:
                    # Hostel details with Boys/Girls
                    details = {}
                    current_category = None
                    temp_list = []
                    for s in spans:
                        if "Hostel" in s or "Boys" in s or "Girls" in s:
                            if current_category and temp_list:
                                details[current_category] = temp_list
                            current_category = s
                            temp_list = []
                        elif s not in ["|", ","]:
                            temp_list.append(s)
                    if current_category and temp_list:
                        details[current_category] = temp_list
                    result["facilities"].append({
                        "name": name,
                        "description": description,
                        "details": details
                    })
                    continue

        facility_data = {"name": name}
        if description:
            facility_data["description"] = description
        if available_facilities:
            facility_data["available_facilities"] = available_facilities

        result["facilities"].append(facility_data)

    # Other facilities at the bottom
    other_facilities = [span.get_text(strip=True) for span in soup.select("div.otherFacilityBox .OFLabels .itm")]
    result["other_facilities"] = other_facilities

    return result

def parse_faculty_full_html(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ Top header section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ Header card not found")
    driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)

    # section = wait.until(
    #     EC.presence_of_element_located(
    #         (By.CSS_SELECTOR, "div.wikkiContents.faqAccordian")
    #     )
    # )
    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,"div.wikkiContents.faqAccordian")
            )
        )
    except:
        print("⚠️ parse_faculty_full_html not available, skipping")
        return None

    # 🔥 Scroll for lazy content
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(2)

    html = driver.execute_script(
        "return arguments[0].innerHTML;", section
    )

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "author": {
            "name": "",
            "profile_url": "",
            "verified": False
        },
        "last_updated": "",
        "description": "",
        "faculty": []
    }

    # ✅ Author details
    author_tag = soup.select_one(".adp_usr_dtls a")
    if author_tag:
        data["author"]["name"] = author_tag.get_text(strip=True)
        data["author"]["profile_url"] = author_tag.get("href", "")
        data["author"]["verified"] = bool(author_tag.select_one(".tickIcon"))

    # ✅ Updated date
    date_tag = soup.select_one(".post-date")
    if date_tag:
        data["last_updated"] = (
            date_tag.get_text(strip=True)
            .replace("Updated on", "")
            .strip()
        )

    # ✅ Full description (first <p>)
    desc_p = soup.select_one(".abtSection p")
    if desc_p:
        data["description"] = desc_p.get_text(" ", strip=True)

    # ✅ Faculty table (FULL SAFE PARSE)
    table = soup.select_one(".abtSection table")
    if table:
        rows = table.find_all("tr")

        for row in rows[1:]:  # skip header
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            faculty_name = cols[0].get_text(" ", strip=True)

            qualifications = []
            for item in cols[1].select("p"):
                text = item.get_text(" ", strip=True)
                if text:
                    qualifications.append(text)

            data["faculty"].append({
                "faculty_name": faculty_name,
                "qualifications": qualifications
            })

    return {"college_info":college_info,"data":data}

def parse_faculty_reviews(driver,URLS):
    driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)

    section = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//h2[contains(text(),'Faculty Reviews')]/ancestor::section")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(0.5)

    html = driver.execute_script(
        "return arguments[0].innerHTML;", section
    )

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "overall_rating": "",
        "rating_out_of": "5",
        "based_on_reviews": "",
        "rating_distribution": [],
        "verified_reviews_info": ""
    }

    # ✅ Overall rating
    rating_tag = soup.select_one(".rvwScore h3")
    if rating_tag:
        data["overall_rating"] = rating_tag.get_text(strip=True)

    # ✅ Based on reviews count
    based_tag = soup.select_one(".refrnceTxt span")
    if based_tag:
        data["based_on_reviews"] = based_tag.get_text(strip=True)

    # ✅ Rating distribution (4-5, 3-4, etc.)
    for bar in soup.select(".starBar"):
        label_tag = bar.select_one(".starC a")
        percent_tag = bar.select_one(".starPrgrs")
        fill_tag = bar.select_one(".fillBar")

        data["rating_distribution"].append({
            "rating_range": label_tag.get_text(strip=True) if label_tag else "",
            "percentage_text": percent_tag.get_text(strip=True) if percent_tag else "",
            "percentage_width": fill_tag["style"].replace("width:", "").replace(";", "").strip()
            if fill_tag and fill_tag.has_attr("style") else ""
        })

    # ✅ Verified reviews description text
    verified_info = soup.select_one(".getAllrvws")
    if verified_info:
        data["verified_reviews_info"] = verified_info.get_text(" ", strip=True)

    return data

def parse_review_summarisation_all_tabs(driver,URLS):
    driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)


    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.ID, "ReviewSummarisationReviewSummary")
            )
        )
    except:
        print("⚠️ parse_review_summarisation_all_tabs not available, skipping")
        return None

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(2)

    final_data = {
        "heading": "",
        "tabs_data": {}
    }

    # Heading
    heading = section.find_element(By.CLASS_NAME, "rvwSmSecHeading")
    final_data["heading"] = heading.text.strip()

    # All tabs
    tabs = section.find_elements(By.CLASS_NAME, "rvwSmTabItem")

    for idx, tab in enumerate(tabs):
        tab_name = tab.find_element(By.CLASS_NAME, "rvwSmTabName").text.strip()

        # Click tab
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(1.5)

        # Fresh HTML after tab change
        html = driver.execute_script(
            "return arguments[0].innerHTML;", section
        )
        soup = BeautifulSoup(html, "html.parser")

        tab_data = {
            "likes": [],
            "info_text": ""
        }

        # Likes
        for li in soup.select(".likeSec ul.bulletList li"):
            gray = li.select_one(".grayItem")
            tab_data["likes"].append({
                "text": li.get_text(" ", strip=True).replace(
                    gray.get_text(strip=True), ""
                ).strip() if gray else li.get_text(strip=True),
                "review_count": gray.get_text(strip=True) if gray else ""
            })

        # Info text
        info = soup.select_one(".rvwSmInfoTxt")
        if info:
            tab_data["info_text"] = info.get_text(strip=True)

        final_data["tabs_data"][tab_name] = tab_data

    return final_data

def parse_articles_section(driver,URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["compare"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        try:
            section = wait.until(
            (EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")
                )
            )
            )
        except TimeoutException:
            print("⚠️ top header not found, using page source fallback")
            section = driver.find_element(By.TAG_NAME, "body")
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ Top header section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ compare card not found")
    driver.get(URLS["compare"])
    wait = WebDriverWait(driver, 15)

    try:
        section = wait.until(
            EC.presence_of_element_located((By.ID, "Articles"))
        )
    except TimeoutException:
        print("⚠️ Articles section not found, skipping...")
        return []
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(2)

    html = driver.execute_script("return arguments[0].innerHTML;", section)
    soup = BeautifulSoup(html, "html.parser")

    articles_data = []

    for card in soup.select(".articleCard_Wrapper"):
        title_tag = card.select_one("h3.articleTitle a")
        author_tag = card.select_one(".authorInfo a")
        date_tag = card.select_one(".articelUpdatedDate")
        image_tag = card.select_one(".imageBox img")
        views_tag = card.select_one(".viewsData label")
        comment_tag = card.select_one(".commentData label")

        # Image fallback: background-image if img not present
        if not image_tag:
            bg = card.select_one(".img-blurdiv")
            image_url = ""
            if bg:
                style = bg.get("style", "")
                match = re.search(r'url\("&quot;(.*?)&quot;\)', style)
                if match:
                    image_url = match.group(1)
        else:
            image_url = image_tag.get("src", "")

        articles_data.append({
            "title": title_tag.text.strip() if title_tag else "",
            "link": "https://www.shiksha.com" + title_tag.get("href") if title_tag else "",
            "author_name": author_tag.text.strip() if author_tag else "",
            "author_link": author_tag.get("href") if author_tag else "",
            "date": date_tag.text.strip() if date_tag else "",
            "image": image_url,
            "views": views_tag.text.strip() if views_tag else "",
            "comments": comment_tag.text.strip() if comment_tag else ""
        })

    return {"college_info":college_info,"articles":articles_data}


def parse_faq_scholarships_section(driver, URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }

    driver.get(URLS["scholarships"])
    wait = WebDriverWait(driver, 15)

    # ---------- COLLEGE HEADER ----------
    try:
        section = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-top-section")))
        img = section.find_element(By.ID, "topHeaderCard-gallery-image")
        college_info["college_name"] = img.get_attribute("alt")
        college_info["cover_image"] = img.get_attribute("src")

        badges = section.find_elements(By.CLASS_NAME, "b8cb")
        for badge in badges:
            text = badge.text.lower()
            if "video" in text:
                college_info["videos_count"] = int(re.search(r"\d+", text).group())
            elif "photo" in text:
                college_info["photos_count"] = int(re.search(r"\d+", text).group())
    except:
        print("⚠️ Top header section not found")

    # ---------- HEADER CARD DETAILS ----------
    try:
        header = wait.until(EC.presence_of_element_located((By.ID, "top-header-card-heading")))

        try:
            college_info["logo"] = header.find_element(By.CSS_SELECTOR, "div.c55b78 img").get_attribute("src")
        except:
            pass

        try:
            college_info["college_name"] = header.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            pass

        try:
            loc = header.find_element(By.CLASS_NAME, "_94eae8").text.strip()
            if "," in loc:
                college_info["location"], college_info["city"] = [x.strip() for x in loc.split(",", 1)]
            else:
                college_info["location"] = loc
        except:
            pass

        try:
            rating_text = header.find_element(By.CLASS_NAME, "f05f57").text
            match = re.search(r"([\d.]+)\s*/\s*5", rating_text)
            if match:
                college_info["rating"] = match.group(1)
        except:
            pass

        try:
            reviews_text = header.find_element(By.XPATH, ".//a[contains(text(),'Reviews')]").text
            college_info["reviews_count"] = int(re.search(r"\d+", reviews_text).group())
        except:
            pass

        try:
            qa_text = header.find_element(By.XPATH, ".//a[contains(text(),'Student Q')]").text.lower()
            num = re.search(r"[\d.]+", qa_text).group()
            college_info["qa_count"] = int(float(num) * 1000) if "k" in qa_text else int(num)
        except:
            pass

        try:
            items = header.find_elements(By.CSS_SELECTOR, "ul.e1a898 li")
            for item in items:
                txt = item.text.lower()
                if "institute" in txt:
                    college_info["institute_type"] = item.text.strip()
                elif "estd" in txt:
                    year = re.search(r"\d{4}", item.text)
                    if year:
                        college_info["established_year"] = year.group()
        except:
            pass

    except:
        print("⚠️ scholarship card not found")
    driver.get(URLS["scholarships"])
    wait = WebDriverWait(driver, 15)
    # section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wikkiContents.faqAccordian")))
    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,".wikkiContents.faqAccordian")
            )
        )
    except:
        print("⚠️ parse_faq_scholarships_section not available, skipping")
        return None
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", section)
    time.sleep(0.5)

    html = driver.execute_script("return arguments[0].innerHTML;", section)
    soup = BeautifulSoup(html, "html.parser")

    # Author
    author_tag = soup.select_one(".adp_usr_dtls a")
    author_name = author_tag.text.strip() if author_tag else ""
    author_link = author_tag.get("href") if author_tag else ""
    
    # Date
    date_tag = soup.select_one(".post-date")
    updated_on = date_tag.text.replace("Updated on", "").strip() if date_tag else ""

    # Paragraphs
    paragraphs = [p.text.strip() for p in soup.select(".abtSection p")]

    # Tables
    tables = []
    for table in soup.select(".abtSection table"):
        table_data = []
        for row in table.find_all("tr"):
            cols = [td.text.strip() for td in row.find_all(["td","th"])]
            table_data.append(cols)
        tables.append(table_data)

    # PDF links
    pdf_links = [a.get("data-link") for a in soup.select("a.smce-cta-link")]

    # Videos
    iframe_elements = driver.find_elements(By.CSS_SELECTOR, ".vcmsEmbed iframe")
    videos = []
    
    for iframe in iframe_elements:
        driver.execute_script("arguments[0].scrollIntoView(true);", iframe)
        time.sleep(0.5)  # wait for lazy loading
        src = iframe.get_attribute("src") or iframe.get_attribute("data-src")
        if src:
            videos.append(src)

    result = {}
    
    result["author_name"] = author_name
    result["author_link"] = author_link
    result["updated_on"] = updated_on
    result["paragraphs"] = paragraphs
    result["tables"] = tables
    result["pdf_links"] = pdf_links
    result["videos"] = videos


    return {"college_info":college_info,"result":result}

# def extract_shiksha_qna(driver,URLS):
#     driver.get(URLS["qna"])

#     # Thoda wait karo page load ke liye
#     import time
#     time.sleep(2)

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     result = {}

#     # ===== Question Details =====
#     question_data = {}
#     title_tag = soup.select_one("#quesTitle_5114413 .wikkiContents")
#     question_data['title'] = title_tag.get_text(strip=True) if title_tag else None

#     asker_tag = soup.select_one(".new-column .right-cl a")
#     question_data['asked_by'] = asker_tag.get_text(strip=True) if asker_tag else None
#     question_data['asker_profile'] = asker_tag['href'] if asker_tag else None

#     follower_tag = soup.select_one(".followersCountTextArea")
#     question_data['followers'] = int(follower_tag.get_text(strip=True).split()[0]) if follower_tag else 0

#     # Views
#     viewers_tag = soup.select_one(".viewers-span")
#     if viewers_tag:
#         views_text = viewers_tag.get_text(strip=True).replace("Views","").strip()
#         if "k" in views_text:
#             views_text = views_text.replace("k", "")
#             question_data['views'] = int(float(views_text) * 1000)
#         else:
#             question_data['views'] = int(views_text)
#     else:
#         question_data['views'] = 0


#     time_tag = soup.select_one("span.time span:last-child")
#     question_data['posted'] = time_tag.get_text(strip=True) if time_tag else None

#     result['question'] = question_data

#     # ===== Answers =====
#     answers = []
#     for li in soup.find_all("li", class_="module"):
#         answer = {}

#         author_tag = li.select_one(".avatar-name")
#         answer['author_name'] = author_tag.get_text(strip=True) if author_tag else None
#         answer['author_profile'] = author_tag['href'] if author_tag else None

#         level_tag = li.select_one(".lvl-name")
#         answer['contributor_level'] = level_tag.get_text(strip=True) if level_tag else None

#         time_tag = li.select_one(".time")
#         answer['time'] = time_tag.get_text(strip=True) if time_tag else None

#         content_tag = li.select_one("p[id^='answerMsgTxt_']")
#         if content_tag:
#             text = content_tag.get_text(strip=True)
#             text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
#             answer['content'] = text
#         else:
#             answer['content'] = None

#         upvote_tag = li.select_one("input[id^='userCountUpvote_']")
#         downvote_tag = li.select_one("input[id^='userCountDownvote_']")
#         answer['upvotes'] = int(upvote_tag['value']) if upvote_tag else 0
#         answer['downvotes'] = int(downvote_tag['value']) if downvote_tag else 0

#         share_tag = li.select_one("a.qSLayer")
#         answer['share_url'] = share_tag['data-shareurl'] if share_tag else None

#         report_tag = li.select_one("a.raLayerClk")
#         answer['report_url'] = report_tag['href'] if report_tag else None

#         answers.append(answer)

#     result['answers'] = answers

    # return result


def scrape_mba_colleges():
    driver = create_driver()
    all_data = []
    c_count = 41

    try:
        for base_url in BASE_URL:
            print("🔄 Scraping:", base_url)

            URLS = build_urls(base_url)
           

            college_data = {       
                "college_details":{
                "id":f"college_{c_count:03d}",
                "college_info":{
                 "college_info":scrape_college_info(driver,URLS),
                 "college_info_program":scrape_college_infopro(driver,URLS),
                },
                "courses": scrape_courses(driver,URLS),
                "fees":scrape_fees(driver,URLS),
                "reviews":{
                    "review_summary":scrape_review_summary(driver,URLS),
                    "reviews":scrape_reviews(driver,URLS),
                 },
                 "admission":{
                    "admission_overview":scrape_admission_overview(driver,URLS),
                    "admission_eligibility":scrape_admission_eligibility_selection(driver,URLS), 
                 },
                "placement":{
                    "placement_report":scrape_placement_report(driver,URLS),
                    "average_package":scrape_average_package_section(driver,URLS),
                    "placement_faqs":scrape_placement_faqs(driver,URLS),
                },               
                "cut_off":{
                "cut_off":scrape_cutoff(driver,URLS),
                },
                "ranking":{
                "ranking":scrape_ranking(driver,URLS),
                "ranking_section":scrape_ranking_section(driver,URLS),
                "ranking_criteria":parse_ranking_criteria_html(driver,URLS),
                },
                "gallery":{
                "gallery_page":scrape_mini_clips(driver,URLS),
                },
                "hotel_campus":{
                 "hostel_campus":scrape_hostel_campus_structured(driver,URLS),
                 "infrastructure":scrape_infrastructure_structured(driver,URLS)
                },
                "faculty":{
                   "faculty":parse_faculty_full_html(driver,URLS),
                    "faculty_reviews":parse_faculty_reviews(driver,URLS),
                    "review_summarisation":parse_review_summarisation_all_tabs(driver,URLS),                   
                },
                "compare":{
                    "articles":parse_articles_section(driver,URLS),
                },
                
                "scholarships":parse_faq_scholarships_section(driver,URLS),
                    }
               
                }
            all_data.append(college_data)
            c_count += 1
    finally:
        driver.quit()

    return all_data



import time
import os

TEMP_FILE = "en_details_data.tmp.json"
FINAL_FILE = "en_details_data.json"
UPDATE_INTERVAL = 6 * 60 * 60  # 6 hours

def auto_update_scraper():
    # Check last modified time
    # if os.path.exists(DATA_FILE):
    #     last_mod = os.path.getmtime(DATA_FILE)
    #     if time.time() - last_mod < UPDATE_INTERVAL:
    #         print("⏱️ Data is recent, no need to scrape")
    #         return

    print("🔄 Scraping started")
    data = scrape_mba_colleges()
    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Atomic swap → replaces old file with new one safely
    os.replace(TEMP_FILE, FINAL_FILE)

    print("✅ Data scraped & saved successfully (atomic write)")

if __name__ == "__main__":
    auto_update_scraper()
        
