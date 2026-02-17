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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

PCOMBA_O_URL="https://www.shiksha.com/mba-masters-of-business-administration-chp"
PCOMBA_C_URL="https://www.shiksha.com/mba-masters-of-business-administration-courses-chp"
PCOMBA_MBA_SYLLABUS_URL = "https://www.shiksha.com/mba-masters-of-business-administration-syllabus-chp"
PCOMBA_MBA_CAREER_URL = "https://www.shiksha.com/mba-masters-of-business-administration-career-chp"
PCOMBA_MBA_ADDMISSION_2026_URL = "https://www.shiksha.com/mba-masters-of-business-administration-admission-chp"
PCOMBA_MBA_FEES_URL = "https://www.shiksha.com/mba-masters-of-business-administration-fees-chp"
PCOMBA_MBA_PGDM_URL = "https://www.shiksha.com/mba/articles/what-is-the-difference-between-pgdm-and-mba-blogId-11131"
PCOMBA_MBA_MSC_URL = "https://www.shiksha.com/mba/articles/mba-vs-msc-differences-eligibility-admission-jobs-salary-blogId-133399"
PCOMBA_CAT_EXAM_URL = "https://www.shiksha.com/mba/cat-exam"


URLS = {
    "overviews":"https://www.shiksha.com/mba/cat-exam",
    "result":"https://www.shiksha.com/mba/cat-exam-results",
    "cut_off":"https://www.shiksha.com/mba/cat-exam-cutoff",
    "ans_key":"https://www.shiksha.com/mba/cat-exam-answer-key",
    "counselling":"https://www.shiksha.com/mba/cat-exam-counselling",
    "analysis":"https://www.shiksha.com/mba/cat-exam-analysis",
    "question_paper":"https://www.shiksha.com/mba/cat-exam-question-papers",
    "admit_card":"https://www.shiksha.com/mba/cat-exam-admit-card",
    "dates":"https://www.shiksha.com/mba/cat-exam-dates",
    "mock_test":"https://www.shiksha.com/mba/cat-exam-mocktest",
    "registration":"https://www.shiksha.com/mba/cat-exam-registration",
    "syllabus":"https://www.shiksha.com/mba/cat-exam-syllabus",
    "pattern":"https://www.shiksha.com/mba/cat-exam-pattern",
    "preparation":"https://www.shiksha.com/mba/cat-exam-preparation",
    "books":"https://www.shiksha.com/mba/cat-exam-books",
    "notification":"https://www.shiksha.com/mba/cat-exam-notification",
    "center":"https://www.shiksha.com/mba/cat-exam-centre",
    "news":"https://www.shiksha.com/mba/cat-exam-news",
    "accepting_college":"https://www.shiksha.com/mba/colleges/mba-colleges-accepting-cat-india?sby=popularity",
    "mba_with_low_fees":"https://www.shiksha.com/mba/articles/mba-colleges-in-india-with-low-fees-blogId-23533",
                   
}


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



def extract_course_data(driver):
    driver.get(PCOMBA_O_URL)
    wait = WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}

    # -------------------------------
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = h1.text.strip() if h1 else None

    # -------------------------------
    # Updated date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = span.text.strip() if span else None

    # -------------------------------
    # Author info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        data["author"] = {
            "name": author_block.find("a").text.strip() if author_block.find("a") else None,
            "profile": author_block.find("a")["href"] if author_block.find("a") else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": author_block.find("span", class_="b0fc").text.strip() if author_block.find("span", class_="b0fc") else None,
            "verified": True if author_block.find("i", class_="tickIcon") else False
        }

    # =====================================================
    # OVERVIEW SECTION (ALREADY DONE)
    # =====================================================
    overview_div = soup.find("div", id="wikkiContents_chp_section_overview_0")
    if overview_div:

        paragraphs = []
        for p in overview_div.find_all("p"):
            text = p.get_text(" ", strip=True)
            if text and len(text) > 30:
                paragraphs.append(text)

        links = []
        for a in overview_div.find_all("a", href=True):
            links.append({
                "title": a.get_text(strip=True),
                "url": a["href"]
            })

        highlight_rows = []
        for table in overview_div.find_all("table"):
            for row in table.find_all("tr")[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) == 2:
                    highlight_rows.append({
                        "Particular": cols[0].get_text(" ", strip=True),
                        "Details": cols[1].get_text(" ", strip=True)
                    })

        data["overview"] = {
            "description": paragraphs,
            "important_links": links,
            "highlights": {
                "columns": ["Particular", "Details"],
                "rows": highlight_rows
            }
        }

    # =====================================================
    # ELIGIBILITY SECTION (NEW)
    # =====================================================
    eligibility_section = soup.find("section", id="chp_section_eligibility")
    if eligibility_section:

        eligibility_div = eligibility_section.find(
            "div", id="wikkiContents_chp_section_eligibility_1"
        )

        # ---- Description Paragraphs
        eligibility_paragraphs = []
        if eligibility_div:
            for p in eligibility_div.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text and len(text) > 30:
                    eligibility_paragraphs.append(text)

        # ---- Useful Links
        eligibility_links = []
        if eligibility_div:
            for a in eligibility_div.find_all("a", href=True):
                eligibility_links.append({
                    "title": a.get_text(strip=True),
                    "url": a["href"]
                })

        # ---- Admission Steps
        admission_steps = []
        if eligibility_div:
            ul = eligibility_div.find("ul")
            if ul:
                for li in ul.find_all("li"):
                    admission_steps.append(li.get_text(" ", strip=True))

        # ---- FAQs (Q&A)
        faqs = []
        faq_blocks = eligibility_section.find_all("div", class_="html-0")
        for faq in faq_blocks:
            question = faq.get_text(" ", strip=True).replace("Q:", "").strip()

            answer_block = faq.find_next("div", class_="_16f53f")
            if answer_block:
                answer_text = " ".join(
                    p.get_text(" ", strip=True)
                    for p in answer_block.find_all("p")
                )
                faqs.append({
                    "question": question,
                    "answer": answer_text
                })

        data["eligibility"] = {
            "description": eligibility_paragraphs,
            "important_links": eligibility_links,
            "admission_steps": admission_steps,
            "faqs": faqs
        }

    return data
def clean(tag):
    return tag.get_text(" ", strip=True) if tag else None


def scrape_courses_overview_section(driver):
    driver.get(PCOMBA_C_URL)
    wait = WebDriverWait(driver, 15)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # ===============================
    # MAIN DATA OBJECT (ONLY ONCE)
    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "courses": {
            "intro": {
                "paragraphs": [],
                "related_links": []
            },
            "sections": {},
            "videos": []
        }
    }

    # ===============================
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # COURSES OVERVIEW SECTION
    container = soup.find("div", id="wikkiContents_chp_courses_overview_0")
    if not container:
        return data

    current_section = "intro"
    active_sub = None

    for elem in container.find_all(["h2", "h3", "p", "table", "ul", "iframe"], recursive=True):

        # ---------- H2 (NEW SECTION)
        if elem.name == "h2":
            current_section = clean(elem)
            active_sub = None
            data["courses"]["sections"][current_section] = {
                "paragraphs": [],
                "tables": [],
                "lists": [],
                "related_links": [],
                "sub_sections": {}
            }

        # ---------- H3 (SUB SECTION)
        elif elem.name == "h3":
            active_sub = clean(elem)
            data["courses"]["sections"][current_section]["sub_sections"][active_sub] = {
                "paragraphs": [],
                "tables": [],
                "lists": []
            }

        # ---------- PARAGRAPHS
        elif elem.name == "p":
            text = clean(elem)
            if not text:
                continue

            link = elem.find("a", href=True)

            target = (
                data["courses"]["sections"][current_section]["sub_sections"][active_sub]
                if active_sub
                else data["courses"]["sections"].get(current_section)
            )

            if current_section == "intro":
                if link:
                    data["courses"]["intro"]["related_links"].append({
                        "text": clean(link),
                        "url": link["href"]
                    })
                else:
                    data["courses"]["intro"]["paragraphs"].append(text)
            else:
                if link and text.lower().startswith(("also read", "know more")):
                    target["related_links"].append({
                        "text": clean(link),
                        "url": link["href"]
                    })
                else:
                    target["paragraphs"].append(text)

        # ---------- TABLES
        elif elem.name == "table":
            rows = []
            for tr in elem.find_all("tr"):
                cells = [clean(td) for td in tr.find_all(["th", "td"]) if clean(td)]
                if cells:
                    rows.append(cells)

            if rows:
                target = (
                    data["courses"]["sections"][current_section]["sub_sections"][active_sub]
                    if active_sub
                    else data["courses"]["sections"][current_section]
                )
                target["tables"].append(rows)

        # ---------- LISTS
        elif elem.name == "ul":
            items = [clean(li) for li in elem.find_all("li") if clean(li)]
            if items:
                target = (
                    data["courses"]["sections"][current_section]["sub_sections"][active_sub]
                    if active_sub
                    else data["courses"]["sections"][current_section]
                )
                target["lists"].append(items)

        # ---------- VIDEOS
        elif elem.name == "iframe":
            src = elem.get("data-original") or elem.get("src")
            if src:
                data["courses"]["videos"].append(src)
    # SPECIALIZATION-WISE SYLLABUS
    spec_container = soup.find("div", id="wikkiContents_chp_syllabus_popularspecialization_0")
    if spec_container:
        table = spec_container.find("table")
        if table:
            for tr in table.find_all("tr")[1:]:  # Skip header row
                tds = tr.find_all("td")
                if len(tds) == 3:
                    spec_name_tag = tds[0].find("a")
                    spec_name = clean(spec_name_tag) if spec_name_tag else clean(tds[0])
                    spec_link = spec_name_tag["href"] if spec_name_tag else None
    
                    subjects = [li.get_text(strip=True) for li in tds[1].find_all("li")]
                    description = clean(tds[2])
    
                    data["courses"]["specializations"][spec_name] = {
                        "link": spec_link,
                        "subjects": subjects,
                        "description": description
                    }
    
    # VIDEOS inside specialization section
    if spec_container:  # Check if the container exists
        for iframe in spec_container.find_all("iframe"):
            src = iframe.get("src") or iframe.get("data-src")
            if src:
                data["courses"]["videos"].append(src)
    
    return data

def scrape_mba_syllabus(driver):
    driver.get(PCOMBA_MBA_SYLLABUS_URL)
    wait = WebDriverWait(driver, 15)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "courses": {
            "intro": {"paragraphs": [], "links": []},
            "syllabus_2025": {"description": [], "semester_wise": [], "note": None},
            "specializations": {},
            "videos": [],
            "suggested_reads": [],
            "top_colleges": []  # <-- Add this
        }
    }

    # ===============================
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # GENERAL SYLLABUS
    container = soup.find("div", id="wikkiContents_chp_syllabus_overview_0")
    current_semester = None
    if container:
        for elem in container.find_all(["p", "h2", "table", "iframe", "a"], recursive=True):
            # PARAGRAPHS
            if elem.name == "p":
                text = elem.get_text(" ", strip=True)
                if not text or "DFP-Banner" in text:
                    continue
                link = elem.find("a", href=True)
                if text.lower().startswith("note"):
                    data["courses"]["syllabus_2025"]["note"] = text
                    continue
                if "Suggested Read" in text:
                    continue
                if not data["courses"]["syllabus_2025"]["description"]:
                    if link:
                        data["courses"]["intro"]["links"].append({
                            "text": link.get_text(strip=True),
                            "url": link["href"]
                        })
                    else:
                        data["courses"]["intro"]["paragraphs"].append(text)
                else:
                    data["courses"]["syllabus_2025"]["description"].append(text)

            # TABLES
            elif elem.name == "table":
                for tr in elem.find_all("tr"):
                    th = tr.find("th")
                    if th:
                        semester_text = th.get_text(" ", strip=True)
                        if "Semester" in semester_text:
                            current_semester = {
                                "semester": semester_text.replace("MBA Course Syllabus", "")
                                                         .replace("MBA Course Subjects", "")
                                                         .replace("MBA Subjects", "")
                                                         .strip(),
                                "subjects": []
                            }
                            data["courses"]["syllabus_2025"]["semester_wise"].append(current_semester)
                    else:
                        for td in tr.find_all("td"):
                            subject = td.get_text(" ", strip=True)
                            if subject and subject != "-" and current_semester:
                                current_semester["subjects"].append(subject)

            # VIDEOS
            elif elem.name == "iframe":
                src = elem.get("src") or elem.get("data-src")
                if src:
                    data["courses"]["videos"].append(src)

            # SUGGESTED READS
            elif elem.name == "a":
                if "MBA Outlook Report" in elem.get_text():
                    data["courses"]["suggested_reads"].append({
                        "title": elem.get_text(strip=True),
                        "url": elem.get("href") or elem.get("data-link")
                    })

    # ===============================
    # SPECIALIZATION-WISE SYLLABUS
    spec_container = soup.find("div", id="wikkiContents_chp_syllabus_popularcolleges_0")
    if spec_container:
        current_spec = None
        current_semester = None

        for elem in spec_container.find_all(["p", "h3", "table"], recursive=True):
            if elem.name == "p":
                text = elem.get_text(" ", strip=True)
                if text:
                    current_spec_desc = data["courses"]["specializations"].get(current_spec, {})
                    if current_spec:
                        current_spec_desc.setdefault("description", []).append(text)
                        data["courses"]["specializations"][current_spec] = current_spec_desc

            elif elem.name == "h3":
                current_spec = clean(elem)
                data["courses"]["specializations"][current_spec] = {
                    "description": [],
                    "semester_wise": []
                }
                current_semester = None

            elif elem.name == "table" and current_spec:
                for tr in elem.find_all("tr"):
                    th = tr.find("th")
                    if th:
                        semester_text = th.get_text(" ", strip=True)
                        if "Semester" in semester_text:
                            current_semester = {
                                "semester": semester_text.strip(),
                                "subjects": []
                            }
                            data["courses"]["specializations"][current_spec]["semester_wise"].append(current_semester)
                    else:
                        for td in tr.find_all("td"):
                            subject = td.get_text(" ", strip=True)
                            if subject and subject != "-" and current_semester:
                                current_semester["subjects"].append(subject)
    
    # Find the specific section
    data["courses"].setdefault("top_colleges", [])

    section = soup.find("section", id="chp_syllabus_topratecourses")
    if section:
        tables = section.find_all("table")
        for table in tables:
            rows = table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_name = cols[0].get_text(strip=True)
                    pdf_link_tag = cols[1].find("a", class_="smce-cta-link")
                    pdf_link = pdf_link_tag.get("data-link") if pdf_link_tag else None
                    data["courses"]["top_colleges"].append({
                        "college": college_name,
                        "pdf_link": pdf_link
                    })

    return data

def scrape_mba_career(driver):
    driver.get(PCOMBA_MBA_CAREER_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}
    # ===============================
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # 1. Career Overview Text
    overview_div = soup.find("div", id="wikkiContents_chp_career_overview_0")
    if overview_div:
        paragraphs = overview_div.find_all("p")
        overview_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        data["career_overview"] = overview_texts

    # 2. Top MBA Career Profiles and Salary
    data["career_profiles"] = []
    tables = overview_div.find_all("table")
    if tables:
        # First table: career profiles
        profile_table = tables[0]
        rows = profile_table.find_all("tr")[1:]  # skip header
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                job_profile = cols[0].get_text(strip=True)
                description = cols[1].get_text(strip=True)
                avg_salary = cols[2].get_text(strip=True)
                data["career_profiles"].append({
                    "job_profile": job_profile,
                    "description": description,
                    "average_salary": avg_salary
                })

    # 3. MBA Scope In India: Sectors
    data["mba_sectors"] = []
    if len(tables) > 1:
        sector_table = tables[1]
        rows = sector_table.find_all("tr")[1:]  # skip header
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                sector1 = cols[0].get_text(strip=True)
                sector2 = cols[1].get_text(strip=True)
                data["mba_sectors"].append([sector1, sector2])

    # 4. Average Salary Based on MBA Specializations
    data["specializations_salary"] = []
    if len(tables) > 2:
        spec_table = tables[2]
        rows = spec_table.find_all("tr")[1:]  # skip header
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                specialization = cols[0].get_text(strip=True)
                avg_salary = cols[1].get_text(strip=True)
                data["specializations_salary"].append({
                    "specialization": specialization,
                    "average_salary": avg_salary
                })

    # 5. Top Recruiters
    data["top_recruiters"] = []
    if len(tables) > 3:
        recruiter_table = tables[3]
        rows = recruiter_table.find_all("tr")[1:]  # skip header
        for row in rows:
            cols = row.find_all("td")
            recruiters = [c.get_text(strip=True) for c in cols if c.get_text(strip=True)]
            data["top_recruiters"].extend(recruiters)

    # 6. Top Colleges (IIM + Private)
    data["top_colleges"] = []
    if len(tables) > 4:
        college_tables = tables[4:]  # IIM + Private colleges tables
        for table in college_tables:
            rows = table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_name = cols[0].get_text(strip=True)
                    median_salary = cols[1].get_text(strip=True)
                    link_tag = cols[0].find("a")
                    link = link_tag.get("href") if link_tag else None
                    data["top_colleges"].append({
                        "college": college_name,
                        "median_salary": median_salary,
                        "link": link
                    })

    return data
 
def scrape_addmission_2026_data(driver):
    driver.get(PCOMBA_MBA_ADDMISSION_2026_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {}
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # Section 1: Overview
    overview_section = soup.find("div", id="wikkiContents_chp_admission_overview_0")
    if overview_section:
        overview_paragraphs = overview_section.find_all("p")
        data['overview_text'] = " ".join([p.get_text(strip=True) for p in overview_paragraphs])

        # Scrape suggested / useful links in overview
        overview_links = []
        for p in overview_section.find_all("p"):
            a_tag = p.find("a")
            if a_tag and a_tag.get("href"):
                overview_links.append({"text": a_tag.get_text(strip=True), "url": a_tag['href']})
        data['overview_links'] = overview_links

    # Section 2: MBA Eligibility
    eligibility_section = soup.find("h2", id="chp_admission_toc_0")
    if eligibility_section:
        eligibility_data = {}
        top_colleges_table = eligibility_section.find_next("table")
        if top_colleges_table:
            rows = top_colleges_table.find_all("tr")
            top_colleges = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 3:
                    top_colleges.append({
                        "college_name": cols[0].get_text(strip=True),
                        "mba_courses": [li.get_text(strip=True) for li in cols[1].find_all("li")],
                        "eligibility_criteria": [li.get_text(strip=True) for li in cols[2].find_all("li")]
                    })
            eligibility_data['top_colleges'] = top_colleges

        general_table = top_colleges_table.find_next("table")
        if general_table:
            rows = general_table.find_all("tr")
            general_eligibility = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 4:
                    general_eligibility.append({
                        "particulars": cols[0].get_text(strip=True),
                        "tier_1": cols[1].get_text(strip=True),
                        "tier_2": cols[2].get_text(strip=True),
                        "tier_3": cols[3].get_text(strip=True),
                    })
            eligibility_data['general'] = general_eligibility

        data['eligibility'] = eligibility_data

    # Section 3: Admission Process
    admission_section = soup.find("h2", id="chp_admission_toc_1")
    if admission_section:
        process_list = admission_section.find_next("ul")
        if process_list:
            data['admission_process'] = [li.get_text(strip=True) for li in process_list.find_all("li")]

    # Section 4: Entrance Exams
    exams_section = soup.find("h2", id="chp_admission_toc_2")
    if exams_section:
        exams_table = exams_section.find_next("table")
        if exams_table:
            rows = exams_table.find_all("tr")
            entrance_exams = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    entrance_exams.append({
                        "exam_name": cols[0].get_text(strip=True),
                        "exam_schedule": cols[1].get_text(strip=True)
                    })
            data['entrance_exams'] = entrance_exams

    # Section 5: Exam Syllabus
    syllabus_section = soup.find("h2", id="chp_admission_toc_3")
    if syllabus_section:
        syllabus_table = syllabus_section.find_next("table")
        if syllabus_table:
            rows = syllabus_table.find_all("tr")
            exam_syllabus = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    exam_syllabus.append({
                        "exam_name": cols[0].get_text(strip=True),
                        "syllabus_details": [p.get_text(strip=True) for p in cols[1].find_all("p")]
                    })
            data['exam_syllabus'] = exam_syllabus

    # Section 6: Best Colleges (IIMs & IITs)
    best_colleges_section = soup.find("h2", id="chp_admission_toc_5")
    if best_colleges_section:
        tables = best_colleges_section.find_all_next("table", limit=2)
        best_colleges = {}
        if tables:
            # IIMs
            iim_rows = tables[0].find_all("tr")[1:]
            best_colleges['IIMs'] = [{"college_name": cols[0].get_text(strip=True),
                                      "mba_fees": cols[1].get_text(strip=True)}
                                     for row in iim_rows if (cols := row.find_all("td")) and len(cols) == 2]
            # IITs
            iit_rows = tables[1].find_all("tr")[1:]
            best_colleges['IITs'] = [{"college_name": cols[0].get_text(strip=True),
                                      "mba_fees": cols[1].get_text(strip=True)}
                                     for row in iit_rows if (cols := row.find_all("td")) and len(cols) == 2]
        data['best_colleges'] = best_colleges

    # Section 6a: Top Government Colleges
    gov_colleges_section = soup.find("h3", id="chp_admission_toc_5_2")
    if gov_colleges_section:
        gov_table = gov_colleges_section.find_next("table")
        if gov_table:
            rows = gov_table.find_all("tr")[1:]
            government_colleges = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link = cols[0].find("a")['href'] if cols[0].find("a") else None
                    government_colleges.append({
                        "college_name": cols[0].get_text(strip=True),
                        "admission_url": link,
                        "mba_fees": cols[1].get_text(strip=True)
                    })
            data['government_colleges'] = government_colleges

    # Section 6b: Top Private Colleges
    private_colleges_section = soup.find("h3", id="chp_admission_toc_5_3")
    if private_colleges_section:
        private_table = private_colleges_section.find_next("table")
        if private_table:
            rows = private_table.find_all("tr")[1:]
            private_colleges = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link = cols[0].find("a")['href'] if cols[0].find("a") else None
                    private_colleges.append({
                        "college_name": cols[0].get_text(strip=True),
                        "admission_url": link,
                        "mba_fees": cols[1].get_text(strip=True)
                    })
            data['private_colleges'] = private_colleges

    # Section 7: Important Dates
    dates_section = soup.find("h2", id="chp_admission_toc_4")
    if dates_section:
        dates_table = dates_section.find_next("table")
        if dates_table:
            rows = dates_table.find_all("tr")
            important_dates = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    important_dates.append({
                        "event": cols[0].get_text(strip=True),
                        "date": cols[1].get_text(strip=True)
                    })
            data['important_dates'] = important_dates

    # Section 8: Contact Info
    contact_section = soup.find("div", id="contact_info")
    if contact_section:
        contact_paragraphs = contact_section.find_all("p")
        data['contact_info'] = [p.get_text(strip=True) for p in contact_paragraphs]

    # Section 9: Placements
    placement_section = soup.find("h2", id="chp_admission_toc_8")
    if placement_section:
        placement_table = placement_section.find_next("table")
        if placement_table:
            rows = placement_table.find_all("tr")[1:]
            placements = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link = cols[0].find("a")['href'] if cols[0].find("a") else None
                    placements.append({
                        "college_name": cols[0].get_text(strip=True),
                        "placement_url": link,
                        "average_package": cols[1].get_text(strip=True)
                    })
            data['placements'] = placements

    return data

def scrape_mba_fees_overview(driver):
    driver.get(PCOMBA_MBA_FEES_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # ===============================
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # MBA Fees Overview
    fees_overview_div = soup.find("div", id="wikkiContents_chp_fees_overview_0")
    if fees_overview_div:
        paragraphs = fees_overview_div.find_all("p")
        overview_text = []
        helpful_links = []

        for p in paragraphs:
            a_tag = p.find("a")
            if a_tag:
                helpful_links.append({
                    "title": a_tag.get_text(strip=True),
                    "url": a_tag.get("href")
                })
            else:
                text = p.get_text(strip=True)
                if text and text != "\xa0":
                    overview_text.append(text)

        data["fees_overview"] = overview_text
        data["fees_helpful_links"] = helpful_links

    # ===============================
    # MBA Course Fees: Location Wise
    data["location_wise_fees"] = []

    location_section = soup.find("div", id="wikkiContents_chp_fees_locationwisefees_0")
    if location_section:
        current_city = None

        for element in location_section.find_all(["h3", "table", "p"], recursive=True):

            # City Heading
            if element.name == "h3":
                current_city = element.get_text(strip=True)
                data["location_wise_fees"].append({
                    "city": current_city,
                    "colleges": [],
                    "read_more": None
                })

            # Colleges Table
            elif element.name == "table" and current_city:
                rows = element.find_all("tr")[1:]  # skip header
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_tag = cols[0].find("a")
                        data["location_wise_fees"][-1]["colleges"].append({
                            "college": cols[0].get_text(strip=True),
                            "fees": cols[1].get_text(strip=True),
                            "link": college_tag.get("href") if college_tag else None
                        })

            # Read More Link
            elif element.name == "p" and current_city:
                a_tag = element.find("a")
                if a_tag and "Click Here" in a_tag.get_text():
                    data["location_wise_fees"][-1]["read_more"] = a_tag.get("href")

    return data

def scrape_pgdm_vs_mba_article(driver):
    driver.get(PCOMBA_MBA_PGDM_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}
    title = soup.find("div",class_="flx-box mA")
    h1 = title.find("h1").text.strip()
    data["title"] = h1
    author_section = soup.find("div", class_="adp_blog")

    if author_section:
        author = {}

        author_link = author_section.select_one(
            ".adp_user_tag .adp_usr_dtls > a[href*='/author/']"
        )

        if author_link:
            author["name"] = author_link.get_text(strip=True)
            author["profile"] = author_link.get("href")

            # ✅ VERIFIED CHECK (CORRECT)
            author["verified"] = bool(author_link.select_one("i.tickIcon"))

        # Author Image
        img = author_section.select_one(".adp_user_tag img")
        if img:
            author["image"] = img.get("src")

        # Author Role
        role = author_section.select_one(".user_expert_level")
        if role:
            author["role"] = role.get_text(strip=True)

        data["author"] = author

        # Updated Date
        updated_span = author_section.select_one(".blogdata_user span")
        if updated_span:
            data["updated_on"] = updated_span.get_text(strip=True)
    # ===============================
    # Blog Summary
    summary_div = soup.find("div", id="blogSummary")
    if summary_div:
        data["summary"] = summary_div.get_text(strip=True)

    # ===============================
    # Intro Section
    intro_div = soup.find("div", id=lambda x: x and x.startswith("wikkiContents_multi"))
    if intro_div:
        data["introduction"] = {
            "text": [p.get_text(strip=True) for p in intro_div.find_all("p") if p.get_text(strip=True)],
            "image": None
        }

        img = intro_div.find("img")
        if img:
            data["introduction"]["image"] = img.get("src")

    # ===============================
    # Table of Contents
    data["table_of_contents"] = []
    toc = soup.find("ul", id="tocWrapper")
    if toc:
        for li in toc.find_all("li"):
            data["table_of_contents"].append(li.get_text(strip=True))

    # ===============================
    # Content Sections (h2 + paragraphs)
    data["sections"] = []

    for section in soup.find_all("div", class_="wikkiContents"):
        h2 = section.find("h2")
        if not h2:
            continue

        section_data = {
            "heading": h2.get_text(strip=True),
            "content": [],
            "tables": []
        }

        # Paragraphs
        for p in section.find_all("p", recursive=False):
            text = p.get_text(" ", strip=True)
            if text:
                section_data["content"].append(text)

        # Tables
        for table in section.find_all("table"):
            table_data = []
            rows = table.find_all("tr")

            headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])] if rows else []

            for row in rows[1:]:
                cols = row.find_all("td")
                if not cols:
                    continue
                row_data = {}
                for i, col in enumerate(cols):
                    key = headers[i] if i < len(headers) else f"col_{i}"
                    row_data[key] = col.get_text(" ", strip=True)
                table_data.append(row_data)

            section_data["tables"].append(table_data)

        data["sections"].append(section_data)

    # ===============================
    # Video Section
    data["video"] = None
    
    iframe = soup.select_one("div iframe[src*='youtube'], iframe[src*='youtube']")
    if iframe:
        data["video"] = iframe.get("src")
    # ===============================
    # Colleges Offering MBA / PGDM
# ===============================
# Colleges Offering MBA / PGDM (FIXED)
    data["colleges"] = []
    
    for h2 in soup.find_all("h2"):
        heading_text = h2.get_text(strip=True).lower()
    
        if "college" in heading_text and ("mba" in heading_text or "pgdm" in heading_text):
            table = h2.find_next("table")
            if not table:
                continue
    
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    a = cols[0].find("a")
                    data["colleges"].append({
                        "college": cols[0].get_text(strip=True),
                        "program": cols[1].get_text(strip=True),
                        "link": a.get("href") if a else None
                    })

    return data


def scrape_mba_msc(driver):
    driver.get(PCOMBA_MBA_MSC_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # ======================
    # BASIC METADATA
    # ======================

    title_div = soup.find("div", class_="flx-box mA")
    data["title"] = title_div.find("h1").get_text(strip=True) if title_div else None

    author = soup.select_one(".adp_usr_dtls a")
    data["author_name"] = author.get_text(strip=True) if author else None

    role = soup.select_one(".user_expert_level")
    data["author_role"] = role.get_text(strip=True) if role else None

    author_img = soup.select_one(".user-img img")
    data["author_image"] = author_img["src"] if author_img else None

    updated = soup.select_one(".blogdata_user span")
    data["updated_on"] = updated.get_text(strip=True) if updated else None

    summary = soup.select_one("#blogSummary")
    data["summary"] = summary.get_text(" ", strip=True) if summary else None

    # ======================
    # ALL TEXT SECTIONS (H2/H3 + P)
    # ======================

    sections = []
    current_section = None

    content_root = soup.select(".wikkiContents")

    for block in content_root:
        for tag in block.find_all(["h2", "h3", "p"], recursive=False):
            if tag.name in ["h2", "h3"]:
                current_section = {
                    "heading": tag.get_text(strip=True),
                    "content": []
                }
                sections.append(current_section)
            elif tag.name == "p" and current_section:
                current_section["content"].append(
                    tag.get_text(" ", strip=True)
                )

    data["content_sections"] = sections

    # ======================
    # QUICK LINKS & RELATED LINKS
    # ======================

    links_data = {
        "mba_links": [],
        "msc_links": [],
        "related_topics": []
    }

    for p in soup.find_all("p"):
        text = p.get_text(strip=True).lower()
        a = p.find("a")

        if not a:
            continue

        link = {
            "title": a.get_text(strip=True),
            "url": a.get("href")
        }

        if "mba exam" in text:
            links_data["mba_links"].append(link)
        elif "msc exam" in text:
            links_data["msc_links"].append(link)
        elif "students also liked" in text or "topics" in text:
            links_data["related_topics"].append(link)

    data["important_links"] = links_data

    # ======================
    # FAQs (Q & A)
    # ======================

    faqs = []

    faq_blocks = soup.select(".sectional-faqs .listener")

    for q_block in faq_blocks:
        question = q_block.get_text(" ", strip=True)

        answer_block = q_block.find_next_sibling("div")
        answer = None

        if answer_block:
            ans_div = answer_block.select_one(".cmsAContent")
            if ans_div:
                answer = ans_div.get_text(" ", strip=True)

        faqs.append({
            "question": question.replace("Q:", "").strip(),
            "answer": answer
        })

    data["faqs"] = faqs

    # ======================
    # ALL TABLES (GENERIC)
    # ======================

    tables_data = []

    for table in soup.find_all("table"):
        table_json = []

        rows = table.find_all("tr")
        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]

        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) == len(headers):
                row_data = {}
                for i in range(len(headers)):
                    row_data[headers[i]] = cols[i].get_text(" ", strip=True)
                table_json.append(row_data)

        if table_json:
            tables_data.append(table_json)

    data["tables"] = tables_data

    # ======================
    # ARTICLE IMAGES
    # ======================

    data["article_images"] = [
        img.get("src") for img in soup.select(".wikkiContents img")
        if img.get("src")
    ]

 
    return data

from bs4 import BeautifulSoup, Tag

def scrape_full_article(driver):
    driver.get(PCOMBA_MBA_MSC_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    output = {
        "sections": [],
        "faqs": []
    }

    current_section = {
        "heading": "Introduction",
        "content": []
    }
    output["sections"].append(current_section)

    # =========================
    # MAIN CONTENT SCRAPER
    # =========================

    for container in soup.select(".wikkiContents"):
        for elem in container.children:

            if not isinstance(elem, Tag):
                continue

            # ---------- HEADINGS ----------
            if elem.name in ["h2", "h3"]:
                current_section = {
                    "heading": elem.get_text(" ", strip=True),
                    "content": []
                }
                output["sections"].append(current_section)

            # ---------- PARAGRAPH ----------
            elif elem.name == "p":
                text = elem.get_text(" ", strip=True)
                if not text:
                    continue

                links = [
                    {
                        "text": a.get_text(strip=True),
                        "url": a.get("href")
                    }
                    for a in elem.find_all("a", href=True)
                ]

                # Detect RED / STRONG heading-style paragraph
                if elem.find("strong") and elem.find("span"):
                    current_section["content"].append({
                        "type": "subheading",
                        "text": text
                    })
                else:
                    current_section["content"].append({
                        "type": "paragraph",
                        "text": text,
                        "links": links if links else None
                    })

            # ---------- LIST ----------
            elif elem.name in ["ul", "ol"]:
                items = []
                for li in elem.find_all("li"):
                    items.append(li.get_text(" ", strip=True))

                if items:
                    current_section["content"].append({
                        "type": "list",
                        "items": items
                    })

            # ---------- TABLE ----------
            elif elem.name == "table":
                rows = elem.find_all("tr")
                if not rows:
                    continue

                headers = [
                    th.get_text(" ", strip=True)
                    for th in rows[0].find_all(["th", "td"])
                ]

                table_data = []
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) == len(headers):
                        row_dict = {}
                        for i in range(len(headers)):
                            row_dict[headers[i]] = cols[i].get_text(" ", strip=True)
                        table_data.append(row_dict)

                if table_data:
                    current_section["content"].append({
                        "type": "table",
                        "rows": table_data
                    })

    # =========================
    # FAQ SCRAPER
    # =========================

    for q in soup.select(".listener"):
        question = q.get_text(" ", strip=True).replace("Q:", "").strip()

        answer_block = q.find_next_sibling("div")
        answer = None

        if answer_block:
            ans = answer_block.select_one(".cmsAContent")
            if ans:
                answer = ans.get_text(" ", strip=True)

        if question and answer:
            output["faqs"].append({
                "question": question,
                "answer": answer
            })

    return output


def scrape_full_cat_exam(driver, URLS):
    
    driver.get(URLS["overviews"])
    
    wait = WebDriverWait(driver, 15)  # Increased wait time
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sectionalWrapperClass"))
        )
    soup = BeautifulSoup(driver.page_source, "html.parser")


    data = {
        "Title":[],
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }
    title = soup.find("h1",class_="event_name")
    h1 = title.text.strip()
    data["Title"]=h1
    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")

    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author["href"] if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title = li.get_text(strip=True)
        if title:
            data["toc"].append(title)



    
    # final_data = {"sections": []}
    
    try:
        # 1. Wait for main page content to load
        print("Loading page...")
        wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Additional wait for dynamic content
        time.sleep(2)
        
        # 2. Find all section containers
        section_wrappers = driver.find_elements(By.CSS_SELECTOR, "div.sectionalWrapperClass")
        print(f"Found {len(section_wrappers)} 'sectionalWrapperClass' blocks on the page.")
        
        for wrapper_index, wrapper in enumerate(section_wrappers):
            try:
                section_data = {
                    "heading": "",
                    "paragraphs": [],
                    "lists": [],
                    "links": [],
                    "videos": []
                }
                
                # 3. Extract heading (h2)
                try:
                    h2_element = wrapper.find_element(By.CSS_SELECTOR, "div.h2Container h2")
                    section_data["heading"] = h2_element.text.strip()
                except NoSuchElementException:
                    print(f"  Block {wrapper_index+1}: No heading found, skipping.")
                    continue
                    
                print(f"  Processing block {wrapper_index+1}: {section_data['heading']}")
                
                # 4. Find main content area (wikkiContents)
                main_content_div = None
                try:
                    # Strategy A: Find div with id starting with 'wikkiContents_'
                    possible_main_divs = wrapper.find_elements(By.CSS_SELECTOR, "div[id^='wikkiContents_']")
                    for div in possible_main_divs:
                        if 'wikkiContents' in div.get_attribute("class"):
                            main_content_div = div
                            break
                except NoSuchElementException:
                    pass
                    
                # Strategy B: If not found by A, find wikkiContents with 'showFullData' class
                if not main_content_div:
                    try:
                        all_wikkis = wrapper.find_elements(By.CSS_SELECTOR, "div.wikkiContents")
                        for wikki in all_wikkis:
                            classes = wikki.get_attribute("class")
                            if classes and 'showFullData' in classes:
                                main_content_div = wikki
                                break
                            elif classes and 'faqAccordian' not in classes:
                                main_content_div = main_content_div or wikki
                    except NoSuchElementException:
                        pass
                
                # Extract content if main content area is found
                if main_content_div:
                    # 5. Extract paragraphs
                    paragraphs = main_content_div.find_elements(By.TAG_NAME, "p")
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and len(text) > 10:
                            lower_text = text.lower()
                            if not (lower_text.startswith("also read") or 
                                    "check cat cut offs" in lower_text or
                                    "predict cat" in lower_text):
                                section_data["paragraphs"].append(text)
                    
                    # 6. Extract list items
                    list_items = main_content_div.find_elements(By.CSS_SELECTOR, "ul li")
                    for li in list_items:
                        text = li.text.strip()
                        if (text and 10 < len(text) < 500 and 
                            not text.startswith("Hi") and 
                            not text.startswith("A: ")):
                            section_data["lists"].append(text)
                    
                    # 7. Extract links (only from paragraphs and lists)
                    links_in_content = main_content_div.find_elements(By.CSS_SELECTOR, "p a[href], li a[href]")
                    for link in links_in_content:
                        try:
                            link_text = link.text.strip()
                            link_url = link.get_attribute("href")
                            if link_text and link_url:
                                section_data["links"].append({
                                    "text": link_text,
                                    "url": link_url
                                })
                        except Exception as e:
                            print(f"    Error extracting link: {e}")
                    
                    # 8. Extract videos (iframes)
                    iframes = main_content_div.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        try:
                            src = iframe.get_attribute("src")
                            if src and src.strip():
                                section_data["videos"].append(src.strip())
                        except Exception as e:
                            print(f"    Error extracting video link: {e}")
                            
                    # 9. Extract additional text from .embed divs
                    embed_divs = main_content_div.find_elements(By.CSS_SELECTOR, "div.embed")
                    for embed in embed_divs:
                        text = embed.text.strip()
                        if text and len(text) > 30:
                            section_data["paragraphs"].append(text)
                
                # 10. Add processed data (only if it has content)
                if (section_data["paragraphs"] or section_data["lists"] or 
                    section_data["links"] or section_data["videos"]):
                    # Remove duplicates from paragraphs and lists (preserve order)
                    seen_paras = set()
                    unique_paras = []
                    for p in section_data["paragraphs"]:
                        if p not in seen_paras:
                            seen_paras.add(p)
                            unique_paras.append(p)
                    section_data["paragraphs"] = unique_paras
                    
                    seen_lists = set()
                    unique_lists = []
                    for l in section_data["lists"]:
                        if l not in seen_lists:
                            seen_lists.add(l)
                            unique_lists.append(l)
                    section_data["lists"] = unique_lists
                    
                    data["sections"].append(section_data)
                    print(f"    ✓ Successfully extracted. Paragraphs: {len(section_data['paragraphs'])}, Lists: {len(section_data['lists'])}")
                else:
                    print(f"    ✗ No valid content extracted from this block.")
                    
            except Exception as e:
                print(f"  Error processing block {wrapper_index+1}: {str(e)[:100]}...")
                continue
        
        print(f"\nTotal extracted sections: {len(data['sections'])}")
        
    except TimeoutException:
        print("Error: Page load timeout. Page structure might be different or network is slow.")
        return None
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None
        
    return data


def scrape_full_cat_exam_result_bulletproof(driver, URLS):
    """
    BULLETPROOF SOLUTION - Will definitely extract the content
    """
    
    driver.get(URLS["result"])
    
    # Wait and scroll to load all content
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)
    
    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }
    
    # Your existing code for title, meta, intro, live_blog, toc...
    # Keep your original code here
    
    print("\n" + "="*60)
    print("BULLETPROOF SECTION EXTRACTION")
    print("="*60)
    
    # ===== METHOD 1: DIRECT DOM ACCESS =====
    print("\nTrying Method 1: Direct DOM access...")
    
    try:
        # Execute JavaScript to directly access the content
        js_code = """
        // Find the specific content we want
        const targetDiv = document.querySelector('div[id^="wikkiContents_"][class*="showFullData"]');
        
        if (!targetDiv) {
            console.log("Target div not found");
            return null;
        }
        
        console.log("Found target div:", targetDiv.id);
        
        // Get the first inner div
        const innerDiv = targetDiv.querySelector('div:first-child');
        if (!innerDiv) {
            console.log("Inner div not found");
            return null;
        }
        
        // Extract content
        const section = {
            heading: "",
            paragraphs: [],
            lists: [],
            links: [],
            videos: []
        };
        
        // Get heading from h2 in the same wrapper
        const wrapper = targetDiv.closest('.sectionalWrapperClass');
        if (wrapper) {
            const h2 = wrapper.querySelector('.h2Container h2');
            if (h2) {
                section.heading = h2.innerText.trim();
                console.log("Heading:", section.heading);
            }
        }
        
        // Extract ALL paragraphs
        const allParagraphs = innerDiv.querySelectorAll('p');
        console.log("Found paragraphs:", allParagraphs.length);
        
        allParagraphs.forEach((p, index) => {
            const text = p.innerText.trim();
            if (text && text.length > 10) {
                section.paragraphs.push(text);
                if (index < 3) {
                    console.log(`Paragraph ${index + 1}:`, text.substring(0, 80) + '...');
                }
            }
        });
        
        // Extract ALL list items
        const allListItems = innerDiv.querySelectorAll('li');
        console.log("Found list items:", allListItems.length);
        
        allListItems.forEach((li, index) => {
            const text = li.innerText.trim();
            if (text && text.length > 5) {
                section.lists.push(text);
                if (index < 3) {
                    console.log(`List item ${index + 1}:`, text.substring(0, 80) + '...');
                }
            }
        });
        
        // Extract embedded h2
        const embeddedH2s = innerDiv.querySelectorAll('h2');
        embeddedH2s.forEach(h2 => {
            const text = h2.innerText.trim();
            if (text) {
                section.paragraphs.push('## ' + text);
                console.log("Embedded H2:", text);
            }
        });
        
        console.log("Total extracted:", section.paragraphs.length, "paragraphs,", section.lists.length, "lists");
        return section;
        """
        
        result = driver.execute_script(js_code)
        
        if result:
            data["sections"].append(result)
            print(f"✓ Method 1 SUCCESS: Extracted section '{result['heading']}'")
            print(f"  Paragraphs: {len(result['paragraphs'])}")
            print(f"  Lists: {len(result['lists'])}")
            return data
            
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    # ===== METHOD 2: SIMPLE TEXT EXTRACTION =====
    print("\nTrying Method 2: Simple text extraction...")
    
    try:
        # Get page source and extract using BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the specific div
        target_div = soup.find('div', id=lambda x: x and x.startswith('wikkiContents_'))
        
        if target_div:
            print(f"Found target div: {target_div.get('id', 'No ID')}")
            
            # Get heading
            wrapper = target_div.find_parent('div', class_='sectionalWrapperClass')
            heading = ""
            if wrapper:
                h2 = wrapper.find('div', class_='h2Container').find('h2') if wrapper.find('div', class_='h2Container') else None
                if h2:
                    heading = h2.get_text(strip=True)
                    print(f"Heading: {heading}")
            
            section = {
                "heading": heading,
                "paragraphs": [],
                "lists": [],
                "links": [],
                "videos": []
            }
            
            # Get the first inner div
            inner_div = target_div.find('div')
            if inner_div:
                # Extract paragraphs
                for p in inner_div.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:
                        section["paragraphs"].append(text)
                
                # Extract lists
                for li in inner_div.find_all('li'):
                    text = li.get_text(strip=True)
                    if text and len(text) > 5:
                        section["lists"].append(text)
                
                # Extract embedded h2
                for h2 in inner_div.find_all('h2'):
                    text = h2.get_text(strip=True)
                    if text:
                        section["paragraphs"].append(f"## {text}")
            
            if section["paragraphs"] or section["lists"]:
                data["sections"].append(section)
                print(f"✓ Method 2 SUCCESS: Extracted {len(section['paragraphs'])} paragraphs, {len(section['lists'])} lists")
                return data
                
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    # ===== METHOD 3: HARDCODED EXTRACTION =====
    print("\nTrying Method 3: Hardcoded extraction...")
    
    try:
        # Since we know the exact HTML structure, let's extract it directly
        page_html = driver.page_source
        
        # Look for the specific pattern
        import re
        
        # Find the wikkiContents div
        pattern = r'<div[^>]*id="wikkiContents_[^"]*"[^>]*class="[^"]*wikkiContents[^"]*showFullData[^"]*"[^>]*>(.*?)<div class="showWikiReadLess"'
        match = re.search(pattern, page_html, re.DOTALL)
        
        if match:
            content_html = match.group(1)
            soup = BeautifulSoup(content_html, 'html.parser')
            
            # Get heading
            heading_pattern = r'<h2[^>]*id="content_toc_\d+"[^>]*>(.*?)</h2>'
            heading_match = re.search(heading_pattern, page_html)
            heading = heading_match.group(1).strip() if heading_match else "How to Download CAT 2025 Result?"
            
            section = {
                "heading": heading,
                "paragraphs": [],
                "lists": [],
                "links": [],
                "videos": []
            }
            
            # Extract paragraphs
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    section["paragraphs"].append(text)
            
            # Extract lists
            for li in soup.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    section["lists"].append(text)
            
            # Extract embedded h2
            for h2 in soup.find_all('h2'):
                text = h2.get_text(strip=True)
                if text:
                    section["paragraphs"].append(f"## {text}")
            
            if section["paragraphs"] or section["lists"]:
                data["sections"].append(section)
                print(f"✓ Method 3 SUCCESS: Extracted content!")
                return data
    
    except Exception as e:
        print(f"Method 3 failed: {e}")
    
    # ===== METHOD 4: LAST RESORT - XPATH =====
    print("\nTrying Method 4: XPath extraction...")
    
    try:
        # Use XPath to find the exact element
        xpath = "//div[starts-with(@id, 'wikkiContents_') and contains(@class, 'showFullData')]"
        content_div = driver.find_element(By.XPATH, xpath)
        
        if content_div:
            print("Found div with XPath")
            
            # Get heading using XPath
            try:
                heading_xpath = "//div[@class='sectionalWrapperClass']//div[@class='h2Container']/h2"
                heading_element = driver.find_element(By.XPATH, heading_xpath)
                heading = heading_element.text.strip()
            except:
                heading = "How to Download CAT 2025 Result?"
            
            section = {
                "heading": heading,
                "paragraphs": [],
                "lists": [],
                "links": [],
                "videos": []
            }
            
            # Get all text from the div
            all_text = content_div.text.strip()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            for line in lines:
                if len(line) > 50:
                    section["paragraphs"].append(line)
                elif len(line) > 10:
                    section["lists"].append(line)
            
            if section["paragraphs"] or section["lists"]:
                data["sections"].append(section)
                print(f"✓ Method 4 SUCCESS: Extracted {len(section['paragraphs'])} paragraphs")
                return data
    
    except Exception as e:
        print(f"Method 4 failed: {e}")
    
    # ===== METHOD 5: DEBUG AND SAVE HTML =====
    print("\nTrying Method 5: Debug mode...")
    
    try:
        # Save the HTML for debugging
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page to debug_page.html")
        
        # Try to manually find the content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Print all divs with wikkiContents
        all_wikkis = soup.find_all('div', class_='wikkiContents')
        print(f"Found {len(all_wikkis)} wikkiContents divs")
        
        for i, wikki in enumerate(all_wikkis):
            print(f"\nWikki {i+1}:")
            print(f"  ID: {wikki.get('id', 'No ID')}")
            print(f"  Classes: {wikki.get('class', [])}")
            
            # Check parent
            parent = wikki.parent
            if parent:
                print(f"  Parent classes: {parent.get('class', [])}")
            
            # Check if it has paragraphs
            paragraphs = wikki.find_all('p')
            print(f"  Has {len(paragraphs)} paragraphs")
            
            if paragraphs and i == 0:  # Use the first one with content
                section = {
                    "heading": "How to Download CAT 2025 Result?",
                    "paragraphs": [],
                    "lists": [],
                    "links": [],
                    "videos": []
                }
                
                for p in paragraphs[:5]:  # Take first 5 paragraphs
                    text = p.get_text(strip=True)
                    if text:
                        section["paragraphs"].append(text)
                
                data["sections"].append(section)
                print(f"✓ Method 5: Added section with {len(section['paragraphs'])} paragraphs")
                return data
    
    except Exception as e:
        print(f"Method 5 failed: {e}")
    
    print("\n" + "="*60)
    print("ALL METHODS FAILED!")
    print("="*60)
    print("The page structure might be different than expected.")
    print("Check debug_page.html to see the actual HTML structure.")
    
    return data





def scrape_cat_toppers_data(driver, URLS):
    """
    Clean version - केवल सही tables से डेटा लेता है
    """
    try:
        print(f"🌐 Website: {URLS['result']}")
        driver.get(URLS["result"])
        time.sleep(4)
        
        # Scroll to load content
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(2)
        
        # Clean data structure
        scraped_data = {
            "page_info": {
                "url": URLS["result"],
                "title": driver.title,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "data": {
                "section_title": "CAT 2025 Toppers List",
                "tables": [],
                "cat_2025_toppers": [],  # केवल CAT 2025 toppers
                "percentile_summaries": []  # केवल percentile tables
            }
        }
        
        print("🔍 डेटा ढूंढ रहा हूँ...")
        
        # 1. पहले SPECIFIC SECTION ढूंढें
        section_element = None
        try:
            # "wikkiContents_results__3" ID वाला div ढूंढें
            section_element = driver.find_element(By.ID, "wikkiContents_results__3")
            print("✓ Toppers section मिला")
        except:
            try:
                # "CAT 2025 Toppers List" heading ढूंढें
                section_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'CAT 2025 Toppers List')]")
                print("✓ Heading मिला")
            except:
                section_element = driver.find_element(By.TAG_NAME, "body")
                print("⚠️ Specific section नहीं मिला, पूरा पेज scan कर रहा हूँ")
        
        # 2. इस SECTION में सिर्फ CAT 2025 Toppers की table ढूंढें
        print("\n🎯 CAT 2025 Toppers Table ढूंढ रहा हूँ...")
        
        # Method 1: border='1' वाली table ढूंढें (आपके HTML में यही है)
        try:
            toppers_table = section_element.find_element(By.CSS_SELECTOR, "table[border='1']")
            print("✓ Border वाली table मिली")
            process_toppers_table(toppers_table, scraped_data)
        except:
            print("⚠️ Border वाली table नहीं मिली, अन्य methods try कर रहा हूँ...")
            
            # Method 2: सभी tables में search करें
            all_tables = section_element.find_elements(By.TAG_NAME, "table")
            print(f"Section में {len(all_tables)} tables मिले")
            
            for table in all_tables:
                try:
                    table_text = table.text.strip()
                    
                    # Check if this is CAT 2025 toppers table
                    if ("Sr.No." in table_text and 
                        "Name of CAT 2025 Toppers" in table_text and 
                        "CAT Percentile" in table_text):
                        
                        print("✓ CAT 2025 Toppers Table मिली!")
                        process_toppers_table(table, scraped_data)
                        break
                        
                except:
                    continue
        
        # 3. PERCENTILE TABLES ढूंढें (100, 99.99, 99.98)
        print("\n📈 Percentile Tables ढूंढ रहा हूँ...")
        
        # Find all h3 headings for percentile sections
        try:
            percentile_headings = driver.find_elements(By.XPATH, "//h3[contains(text(), 'Percentilers')]")
            
            for heading in percentile_headings:
                heading_text = heading.text.strip()
                print(f"✓ {heading_text} heading मिला")
                
                # इस heading के बाद की table ढूंढें
                try:
                    # Get next table after this heading
                    next_table = heading.find_element(By.XPATH, "./following-sibling::table[1]")
                    table_text = next_table.text.strip()
                    
                    table_data = {
                        "title": heading_text,
                        "content": table_text,
                        "type": "percentile_summary"
                    }
                    
                    scraped_data["data"]["percentile_summaries"].append(table_data)
                    print(f"  ✓ Table data extracted")
                    
                except Exception as e:
                    print(f"  ⚠️ Table नहीं मिली: {e}")
                    
        except Exception as e:
            print(f"Percentile headings error: {e}")
        
        # 4. FINAL RESULTS
        print("\n" + "="*60)
        print("✅ CLEAN RESULTS - CAT 2025 TOPPERS")
        print("="*60)
        
        print(f"📊 CAT 2025 Toppers Found: {len(scraped_data['data']['cat_2025_toppers'])}")
        print(f"📈 Percentile Tables: {len(scraped_data['data']['percentile_summaries'])}")
        
        # Show CAT 2025 toppers
        if scraped_data["data"]["cat_2025_toppers"]:
            print(f"\n🏆 CAT 2025 TOPPERS LIST:")
            for i, topper in enumerate(scraped_data["data"]["cat_2025_toppers"], 1):
                rank = topper.get("rank", "")
                name = topper.get("name", "")
                percentile = topper.get("percentile", "")
                print(f"  {i}. Rank {rank}: {name} - {percentile}")
        
        # Show percentile summaries
        if scraped_data["data"]["percentile_summaries"]:
            print(f"\n📊 PERCENTILE SUMMARIES:")
            for i, summary in enumerate(scraped_data["data"]["percentile_summaries"], 1):
                title = summary.get("title", "")
                content = summary.get("content", "")[:100]
                print(f"  {i}. {title}: {content}...")
        
        print("="*60)
        
        return scraped_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_toppers_table(table_element, scraped_data):
    """CAT 2025 toppers table process करें"""
    try:
        print("📋 Toppers table process कर रहा हूँ...")
        
        # Get all rows
        rows = table_element.find_elements(By.TAG_NAME, "tr")
        
        if len(rows) < 2:
            print("⚠️ Table में पर्याप्त rows नहीं हैं")
            return
        
        # Skip header row
        for row in rows[1:]:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 3:
                    rank = cells[0].text.strip()
                    name_cell = cells[1]
                    
                    # Get name (check for link)
                    name_links = name_cell.find_elements(By.TAG_NAME, "a")
                    if name_links:
                        name = name_links[0].text.strip()
                    else:
                        name = name_cell.text.strip()
                    
                    percentile = cells[2].text.strip()
                    
                    # Add only if all fields are present
                    if rank and name and percentile:
                        topper = {
                            "rank": rank,
                            "name": name,
                            "percentile": percentile
                        }
                        scraped_data["data"]["cat_2025_toppers"].append(topper)
                        print(f"  ✓ {rank}. {name} - {percentile}")
                
            except Exception as e:
                print(f"  ⚠️ Row error: {e}")
                continue
        
        print(f"✅ Total {len(scraped_data['data']['cat_2025_toppers'])} toppers extracted")
        
    except Exception as e:
        print(f"Table processing error: {e}")


def scrape_cutoff_section(driver, URLS):
    driver.get(URLS["cut_off"])
    wait = WebDriverWait(driver, 40)

    # Scroll to trigger lazy load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # ✅ WAIT FOR ACTUAL BLOCK
    cutoff_block = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.wikkiContents.faqAccordian")
        )
    )

    # ================= CLICK READ MORE =================
    driver.execute_script("arguments[0].scrollIntoView(true);", cutoff_block)
    time.sleep(1)

    for btn in driver.find_elements(By.CSS_SELECTOR, ".toggle-button a"):
        try:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.8)
        except:
            pass

    data = {
        "section": {
            "paragraphs": [],
            "links": [],
        }
    }

    # ================= PARAGRAPHS =================
    for p in cutoff_block.find_elements(By.CSS_SELECTOR, "p"):
        text = p.text.strip()
        if text:
            data["section"]["paragraphs"].append(text)

    # ================= LINKS =================
    for a in cutoff_block.find_elements(By.TAG_NAME, "a"):
        href = a.get_attribute("href")
        if href:
            data["section"]["links"].append({
                "text": a.text.strip(),
                "url": href
            })

    cutoff_data = driver.execute_script("""
    let containers = document.querySelectorAll('.sectionalWrapperClass .wikkiContents.faqAccordian.showFullData');
    let result = [];
    
    containers.forEach(container => {
        // show hidden rows
        container.querySelectorAll('.hidden-row').forEach(el => el.style.display='table-row');
    
        let currentContext = {headings: [], paragraphs: []};
        let nodes = container.querySelectorAll('h2, h3, p, div.table-container');
    
        nodes.forEach(node => {
            let tag = node.tagName.toLowerCase();
    
            // headings
            if(tag === 'h2' || tag === 'h3'){
                let txt = node.innerText.trim();
                if(txt) currentContext.headings.push(txt);
            }
    
            // paragraphs NOT inside table
            if(tag === 'p' && !node.closest('.table-container')){
                let txt = node.innerText.trim();
                if(txt) currentContext.paragraphs.push(txt);
            }
    
            // tables
            if(tag === 'div' && node.classList.contains('table-container')){
                let table = node.querySelector('table');
                if(!table) return;
    
                let headers = [];
                table.querySelectorAll('th').forEach(th => headers.push(th.innerText.trim()));
    
                let rows = [];
                table.querySelectorAll('tr').forEach(tr => {
                    let cells = tr.querySelectorAll('td');
                    if(cells.length){
                        let collegeCell = cells[0].querySelector('a');
                        let collegeName = collegeCell ? collegeCell.innerText.trim() : cells[0].innerText.trim();
                        let link = collegeCell ? collegeCell.href : null;
                        let percentile = cells[1].innerText.trim();
                        rows.push({college: collegeName, link: link, cat_percentile: percentile});
                    }
                });
    
                result.push({
                    context: {...currentContext},
                    table: {headers, rows}
                });
    
                // reset context
                currentContext = {headings: [], paragraphs: []};
            }
        });
    });
    
    return result;
    """)
    
    
    data["Table_data"] = cutoff_data
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Final result
    years_cutoff = []
    
    # Select only the specific section
    for section in soup.select("div#wikkiContents_cutoff__6"):
        for h3 in section.find_all("h3"):
            table = h3.find_next("table")
            if table:
                headers = [th.get_text(strip=True) for th in table.find_all("th")]
    
                rows = []
                for tr in table.find_all("tr")[1:]:  # skip header row
                    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if cells:
                        rows.append(cells)
    
                years_cutoff.append({
                    "heading": h3.get_text(strip=True),
                    "table": {
                        "headers": headers,
                        "rows": rows
                    }
                })
    
    
    # Example: print structured data
    data["years_cutoff"]=years_cutoff
  
    return data



def scrape_ans_key(driver, URLS):
    driver.get(URLS["ans_key"])
    time.sleep(5)
    
    # Scroll page to load all content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    
    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt and txt not in data["intro"]:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt and txt not in data["live_blog"]:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt and title_txt not in data["toc"]:
            data["toc"].append(title_txt)

    # SECTIONS
    sections_data = []
    
    # Find all h2 elements and their parent sections
    all_h2 = soup.find_all('h2')
    
    for h2 in all_h2:
        h2_text = h2.get_text(strip=True)
        
        # Look for answer key related sections
        if 'Answer Key' in h2_text or 'answer key' in h2_text.lower():
            
            # Find the parent sectionalWrapperClass
            section = h2.find_parent('div', class_='sectionalWrapperClass')
            if not section:
                # Try to find the section containing this h2
                parent_div = h2.find_parent('div')
                while parent_div and 'sectionalWrapperClass' not in parent_div.get('class', []):
                    parent_div = parent_div.find_parent('div')
                section = parent_div
            
            if section:
                section_info = {
                    "section_title": h2_text,
                    "intro": [],
                    "tables": []
                }
                
                # Extract text content
                for p in section.find_all('p'):
                    if not p.find_parent('table'):
                        text = p.get_text(" ", strip=True)
                        if text and len(text) > 10 and text not in section_info["intro"]:
                            section_info["intro"].append(text)
                
                # Get list items
                for li in section.find_all('li'):
                    if not li.find_parent('table'):
                        text = li.get_text(" ", strip=True)
                        if text and len(text) > 3 and f"• {text}" not in section_info["intro"]:
                            section_info["intro"].append(f"• {text}")
                
                # Extract ALL tables in this section
                tables = section.find_all('table')
                for table in tables:
                    headers = []
                    rows = []
                    
                    # Extract headers
                    for th in table.find_all('th'):
                        header_text = th.get_text(strip=True)
                        if header_text and header_text not in headers:
                            headers.append(header_text)
                    
                    # Extract all rows with data
                    for tr in table.find_all('tr'):
                        # Skip if it's a header-only row
                        if tr.find('th') and not tr.find('td'):
                            continue
                        
                        tds = tr.find_all('td')
                        if tds:
                            row_data = []
                            for td in tds:
                                text = td.get_text(" ", strip=True)
                                row_data.append(text)
                            
                            if any(cell.strip() for cell in row_data):
                                rows.append(row_data)
                    
                    if rows:
                        section_info["tables"].append({
                            "headers": headers,
                            "rows": rows
                        })
                
                sections_data.append(section_info)
    
    # If no specific sections found, get all tables from page
    if not sections_data:
        sections_data = extract_all_page_tables(soup)
    
    data["sections"] = sections_data
    
    return data


def extract_all_page_tables(soup):
    """Extract all tables from the entire page"""
    sections_data = []
    
    # Create a main section with all tables
    all_tables = soup.find_all('table')
    
    if all_tables:
        main_section = {
            "section_title": "CAT 2025 Answer Key Data",
            "intro": ["Extracted data from CAT answer key page"],
            "tables": []
        }
        
        for table in all_tables:
            headers = []
            rows = []
            
            # Extract headers
            for th in table.find_all('th'):
                header_text = th.get_text(strip=True)
                if header_text and header_text not in headers:
                    headers.append(header_text)
            
            # Extract rows
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if tds:
                    row_data = [td.get_text(" ", strip=True) for td in tds]
                    if any(cell.strip() for cell in row_data):
                        rows.append(row_data)
            
            if rows:
                main_section["tables"].append({
                    "headers": headers,
                    "rows": rows
                })
        
        sections_data.append(main_section)
    
    return sections_data
def scrape_counselling(driver, URLS):
    driver.get(URLS["counselling"])
    time.sleep(5)
    
    # Scroll to load images
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    
    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            data["toc"].append(title_txt)
    
    # SECTIONS
    sections_data = []
    
    for section in soup.select('div.sectionalWrapperClass'):
        section_info = {
            "section_title": "",
            "intro": [],
            "tables": [],
            "images": []  # सिर्फ URLs store करेंगे
        }
        
        # Title
        h2 = section.select_one('h2')
        if h2:
            section_info["section_title"] = h2.get_text(strip=True)
        
        # Content
        content_div = section.select_one('.wikkiContents')
        if content_div:
            # Text
            for p in content_div.find_all('p'):
                if not p.find_parent('table'):
                    text = p.get_text(" ", strip=True)
                    if text and len(text) > 10:
                        section_info["intro"].append(text)
            
            # Images - सिर्फ URLs
            for img in content_div.find_all('img'):
                img_url = get_real_image_url(img)
                if img_url:
                    section_info["images"].append(img_url)
        
        # Tables
        for table in section.find_all('table'):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            rows = []
            
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if tds:
                    rows.append([td.get_text(strip=True) for td in tds])
            
            if rows:
                section_info["tables"].append({
                    "headers": headers,
                    "rows": rows
                })
        
        sections_data.append(section_info)
    
    data["sections"] = sections_data
    
    return data


def get_real_image_url(img_tag):
    """Get real image URL from img tag"""
    # Check various attributes for real image URL
    for attr in ['data-src', 'src', 'data-lazy-src', 'data-original']:
        if img_tag.get(attr):
            url = img_tag[attr]
            # Skip data URIs and empty URLs
            if url and not url.startswith('data:'):
                return url
    return None

def scrape_faqs_selenium(driver, URLS):
    driver.get(URLS["counselling"])
    time.sleep(3)
    
    # Scroll to load FAQ section
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    faqs_data = []
    
    # Find FAQ sections
    faq_sections = soup.select('.sectional-faqs')
    
    for section in faq_sections:
        # Find questions
        questions = section.select('.html-0.c5db62.listener')
        
        for q in questions:
            # Get question
            q_elem = q.select_one('strong.flx-box')
            if q_elem:
                question = q_elem.get_text(" ", strip=True)
                question = question.replace("Q:", "").strip()
                
                # Get answer
                answer_div = q.find_next_sibling('div', class_='_16f53f')
                if answer_div:
                    answer_elem = answer_div.select_one('._843b17')
                    if answer_elem:
                        answer = answer_elem.get_text(" ", strip=True)
                        answer = answer.replace("A:", "").strip()
                        
                        # Remove GPT part
                        if "Not satisfied with answer?" in answer:
                            answer = answer.split("Not satisfied with answer?")[0].strip()
                        
                        if question and answer:
                            faqs_data.append({
                                "question": question,
                                "answer": answer
                            })
    
    return faqs_data
def scrape_analysis(driver, URLS):
    driver.get(URLS["analysis"])
    
    # Better scrolling for lazy loading
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            data["toc"].append(title_txt)

    wait = WebDriverWait(driver, 25)
    
    try:
        # Find all section wrappers
        wrappers = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "sectionalWrapperClass"))
        )
        
        print(f"Found {len(wrappers)} sectionalWrapperClass elements")
        
        for i, wrapper in enumerate(wrappers):
            try:
                section = {
                    "heading": "",
                    "highlights": [],
                    "table": [],
                    "also_read": [],
                    "video_url": "",
                    "faqs": []  # ✅ NEW: Added FAQs inside each section
                }
                
                # HEADING - better extraction
                wrapper_html = wrapper.get_attribute("outerHTML")
                wrapper_soup = BeautifulSoup(wrapper_html, "html.parser")
                
                # Find heading
                h2_element = wrapper_soup.find("h2")
                if h2_element:
                    section["heading"] = h2_element.get_text(strip=True)
                
                # Skip if no heading (first empty section)
                if not section["heading"]:
                    print(f"Skipping section {i+1} - no heading found")
                    continue
                
                print(f"Section {i+1} heading: {section['heading']}")
                
                # Find content div
                content_div = wrapper_soup.select_one("div.wikkiContents.faqAccordian.showFullData")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.wikkiContents")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.faqAccordian")
                if not content_div:
                    content_div = wrapper_soup
                
                # HIGHLIGHTS - better extraction
                # Look for first UL that has bullet points (not navigation or links)
                all_uls = content_div.find_all("ul")
                for ul in all_uls:
                    lis = ul.find_all("li")
                    if lis and len(lis) > 2:  # Likely a highlights list
                        # Check if this looks like highlights (not also read links)
                        first_li_text = lis[0].get_text(strip=True)
                        if len(first_li_text) < 150 and not first_li_text.startswith("http"):
                            for li_elem in lis:
                                text = li_elem.get_text(" ", strip=True)
                                if text and not text.startswith("http"):
                                    section["highlights"].append(text)
                            break
                
                # TABLE - better extraction with line breaks
                tables = content_div.find_all("table")
                if tables:
                    table = tables[0]
                    rows = table.find_all("tr")
                    for row in rows:
                        cols = []
                        cells = row.find_all(["th", "td"])
                        for cell in cells:
                            # Preserve line breaks in table cells
                            cell_text = ""
                            for content in cell.contents:
                                if content.name == "br":
                                    cell_text += "\n"
                                elif content.name is None:  # Text node
                                    cell_text += str(content)
                                elif content.name == "p":
                                    cell_text += content.get_text() + "\n"
                            cols.append(cell_text.strip())
                        
                        if cols and any(cols):  # Check if not empty
                            section["table"].append(cols)
                
                # ALSO READ - better detection
                # Method 1: Look for text containing "Also Read" or "also read"
                for elem in content_div.find_all(string=lambda text: text and "Also Read" in text):
                    parent = elem.parent
                    # Find next UL after this text
                    next_ul = None
                    current = parent
                    while current:
                        next_sibling = current.find_next_sibling()
                        if next_sibling and next_sibling.name == "ul":
                            next_ul = next_sibling
                            break
                        current = next_sibling
                    
                    if next_ul:
                        for a in next_ul.find_all("a", href=True):
                            title = a.get_text(" ", strip=True)
                            url = a["href"]
                            if title and url:
                                section["also_read"].append({
                                    "title": title,
                                    "url": url
                                })
                        break
                
                # Method 2: Look for UL with links that have article-like titles
                if not section["also_read"]:
                    for ul in content_div.find_all("ul"):
                        links = ul.find_all("a", href=True)
                        if links and len(links) >= 2:
                            # Check if links look like article links (not navigation)
                            first_link_text = links[0].get_text(strip=True)
                            if len(first_link_text) > 20 and "CAT" in first_link_text.upper():
                                for a in links:
                                    title = a.get_text(" ", strip=True)
                                    url = a["href"]
                                    if title and url and "shiksha" in url:
                                        section["also_read"].append({
                                            "title": title,
                                            "url": url
                                        })
                                break
                
                # VIDEO URL - extract real YouTube URL
                iframe = content_div.find("iframe", src=True)
                if iframe:
                    src = iframe["src"]
                    # Check if it's a real YouTube URL, not a placeholder
                    if "youtube.com" in src or "youtu.be" in src:
                        section["video_url"] = src
                    elif "data:image" not in src:  # Not a placeholder
                        section["video_url"] = src
                
                # Also check for YouTube embed div
                if not section["video_url"]:
                    youtube_div = content_div.find("div", class_="vcmsEmbed")
                    if youtube_div:
                        iframe = youtube_div.find("iframe", src=True)
                        if iframe and "youtube" in iframe["src"]:
                            section["video_url"] = iframe["src"]
                
                # ✅ NEW: EXTRACT FAQS FROM THIS SECTION
                try:
                    # Look for FAQ wrapper within the section
                    faq_wrapper = content_div.select_one(".AnATaggedFaqWrapper")
                    
                    if faq_wrapper:
                        # Find FAQ container
                        faq_container = faq_wrapper.select_one("._0c7561.sectional-faqs")
                        
                        if faq_container:
                            # Extract all FAQs
                            section_faqs = []
                            
                            # Find all question divs
                            question_divs = []
                            
                            # Method 1: Look for divs with IDs containing "::"
                            for div in faq_container.find_all("div", id=True):
                                if "::" in div["id"]:
                                    question_divs.append(div)
                            
                            # Method 2: Look for strong tags with class "flx-box"
                            if not question_divs:
                                for strong in faq_container.find_all("strong", class_="flx-box"):
                                    parent_div = strong.find_parent("div")
                                    if parent_div:
                                        question_divs.append(parent_div)
                            
                            for q_div in question_divs:
                                try:
                                    faq_item = {
                                        "question": "",
                                        "answer": "",
                                        "links": []
                                    }
                                    
                                    # Extract question
                                    question_elem = q_div.find("strong", class_="flx-box")
                                    if question_elem:
                                        question_text = question_elem.get_text(strip=True)
                                        # Clean up question text
                                        question_text = question_text.replace("Q:", "").replace("Q :", "").strip()
                                        faq_item["question"] = question_text
                                    
                                    # Find answer div (next sibling with class "_16f53f")
                                    answer_div = q_div.find_next_sibling("div", class_="_16f53f")
                                    if answer_div:
                                        # Extract answer from wikkiContents
                                        answer_content = answer_div.select_one("div.wikkiContents")
                                        if answer_content:
                                            answer_text = answer_content.get_text(" ", strip=True)
                                            # Clean up answer text
                                            answer_text = answer_text.replace("A:", "").replace("A :", "").strip()
                                            faq_item["answer"] = answer_text
                                            
                                            # Extract links
                                            for link in answer_content.find_all("a", href=True):
                                                faq_item["links"].append({
                                                    "text": link.get_text(strip=True),
                                                    "url": link["href"]
                                                })
                                    
                                    if faq_item["question"] and faq_item["answer"]:
                                        section_faqs.append(faq_item)
                                        
                                except Exception as e:
                                    print(f"  Error parsing FAQ in section {i+1}: {e}")
                                    continue
                            
                            section["faqs"] = section_faqs
                            print(f"  Found {len(section_faqs)} FAQs in this section")
                            
                except Exception as e:
                    print(f"  Error extracting FAQs from section {i+1}: {e}")
                
                # Clean up highlights (remove duplicates and empty)
                section["highlights"] = list(dict.fromkeys([h for h in section["highlights"] if h.strip()]))
                
                # Clean up table data (fix formatting issues)
                cleaned_table = []
                for row in section["table"]:
                    cleaned_row = []
                    for cell in row:
                        # Fix common issues
                        cell = cell.replace("\n\n", "\n")
                        cell = cell.strip()
                        cleaned_row.append(cell)
                    cleaned_table.append(cleaned_row)
                section["table"] = cleaned_table
                
                data["sections"].append(section)
                
            except Exception as e:
                print(f"Error in section {i+1}: {str(e)[:100]}")
                continue
    
    except Exception as e:
        print(f"Error finding sections: {e}")

    # ✅ NEW: ALSO CHECK FOR STANDALONE FAQS (outside sections)
    try:
        print("\nLooking for standalone FAQs...")
        standalone_faqs = []
        
        # Find all FAQ wrappers in the entire page
        all_faq_wrappers = soup.find_all("div", class_="AnATaggedFaqWrapper")
        
        for faq_wrapper in all_faq_wrappers:
            # Check if this FAQ wrapper is NOT inside any section we already processed
            in_section = False
            for section in data["sections"]:
                # Simple check: if FAQ wrapper HTML contains section heading
                if section["heading"] and section["heading"] in str(faq_wrapper):
                    in_section = True
                    break
            
            if not in_section:
                # Extract standalone FAQs
                faq_container = faq_wrapper.select_one("._0c7561.sectional-faqs")
                if faq_container:
                    # Create a special section for standalone FAQs
                    faq_section = {
                        "heading": "FAQs",
                        "highlights": [],
                        "table": [],
                        "also_read": [],
                        "video_url": "",
                        "faqs": []
                    }
                    
                    # Extract FAQs using the same logic
                    question_divs = []
                    
                    # Method 1: Look for divs with IDs containing "::"
                    for div in faq_container.find_all("div", id=True):
                        if "::" in div["id"]:
                            question_divs.append(div)
                    
                    # Method 2: Look for strong tags with class "flx-box"
                    if not question_divs:
                        for strong in faq_container.find_all("strong", class_="flx-box"):
                            parent_div = strong.find_parent("div")
                            if parent_div:
                                question_divs.append(parent_div)
                    
                    for q_div in question_divs:
                        try:
                            faq_item = {
                                "question": "",
                                "answer": "",
                                "links": []
                            }
                            
                            # Extract question
                            question_elem = q_div.find("strong", class_="flx-box")
                            if question_elem:
                                question_text = question_elem.get_text(strip=True)
                                question_text = question_text.replace("Q:", "").replace("Q :", "").strip()
                                faq_item["question"] = question_text
                            
                            # Find answer div
                            answer_div = q_div.find_next_sibling("div", class_="_16f53f")
                            if answer_div:
                                answer_content = answer_div.select_one("div.wikkiContents")
                                if answer_content:
                                    answer_text = answer_content.get_text(" ", strip=True)
                                    answer_text = answer_text.replace("A:", "").replace("A :", "").strip()
                                    faq_item["answer"] = answer_text
                                    
                                    # Extract links
                                    for link in answer_content.find_all("a", href=True):
                                        faq_item["links"].append({
                                            "text": link.get_text(strip=True),
                                            "url": link["href"]
                                        })
                            
                            if faq_item["question"] and faq_item["answer"]:
                                faq_section["faqs"].append(faq_item)
                                
                        except Exception as e:
                            print(f"  Error parsing standalone FAQ: {e}")
                            continue
                    
                    if faq_section["faqs"]:
                        data["sections"].append(faq_section)
                        print(f"Added standalone FAQ section with {len(faq_section['faqs'])} FAQs")
                        
    except Exception as e:
        print(f"Error finding standalone FAQs: {e}")

    # Post-process: Remove empty sections
    data["sections"] = [s for s in data["sections"] if s["heading"] or s["highlights"] or s["table"] or s["faqs"]]
    
    print(f"\nScraped {len(data['sections'])} valid sections successfully")
    
    # Print summary
    for i, section in enumerate(data["sections"]):
        print(f"\nSection {i+1}: {section['heading']}")
        print(f"  Highlights: {len(section['highlights'])}")
        print(f"  Table rows: {len(section['table'])}")
        print(f"  Also read: {len(section['also_read'])}")
        print(f"  FAQs: {len(section.get('faqs', []))}")
        if section['video_url']:
            print(f"  Video: {section['video_url'][:50]}...")
    
    return data

def scrape_question_paper(driver, URLS):
    driver.get(URLS["question_paper"])
    
    # Better scrolling for lazy loading
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            data["toc"].append(title_txt)
    
    wait = WebDriverWait(driver, 25)
    
    try:
        # Find all section wrappers
        wrappers = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "sectionalWrapperClass"))
        )
        
        print(f"Found {len(wrappers)} sectionalWrapperClass elements")
        
        for i, wrapper in enumerate(wrappers):
            try:
                section = {
                    "heading": "",
                    "highlights": [],
                    "table": [],
                    "also_read": [],
                    "video_url": "",
                    "memory_based_questions": [],  # ✅ NEW: For memory based questions
                    "faqs": []  # ✅ NEW: For FAQs
                }
                
                # HEADING - better extraction
                wrapper_html = wrapper.get_attribute("outerHTML")
                wrapper_soup = BeautifulSoup(wrapper_html, "html.parser")
                
                # Find heading
                h2_element = wrapper_soup.find("h2")
                if h2_element:
                    section["heading"] = h2_element.get_text(strip=True)
                
                # Skip if no heading (first empty section)
                if not section["heading"]:
                    print(f"Skipping section {i+1} - no heading found")
                    continue
                
                print(f"Section {i+1} heading: {section['heading']}")
                
                # Find content div
                content_div = wrapper_soup.select_one("div.wikkiContents.faqAccordian.showFullData")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.wikkiContents")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.faqAccordian")
                if not content_div:
                    content_div = wrapper_soup
                
                # HIGHLIGHTS - better extraction
                # Look for first UL that has bullet points (not navigation or links)
                all_uls = content_div.find_all("ul")
                for ul in all_uls:
                    lis = ul.find_all("li")
                    if lis and len(lis) > 2:  # Likely a highlights list
                        # Check if this looks like highlights (not also read links)
                        first_li_text = lis[0].get_text(strip=True)
                        if len(first_li_text) < 150 and not first_li_text.startswith("http"):
                            for li_elem in lis:
                                text = li_elem.get_text(" ", strip=True)
                                if text and not text.startswith("http"):
                                    section["highlights"].append(text)
                            break
                
                # TABLE - better extraction with line breaks
                tables = content_div.find_all("table")
                if tables:
                    table = tables[0]
                    rows = table.find_all("tr")
                    for row in rows:
                        cols = []
                        cells = row.find_all(["th", "td"])
                        for cell in cells:
                            # Preserve line breaks in table cells
                            cell_text = ""
                            for content in cell.contents:
                                if content.name == "br":
                                    cell_text += "\n"
                                elif content.name is None:  # Text node
                                    cell_text += str(content)
                                elif content.name == "p":
                                    cell_text += content.get_text() + "\n"
                            cols.append(cell_text.strip())
                        
                        if cols and any(cols):  # Check if not empty
                            section["table"].append(cols)
                
                # ✅ NEW: MEMORY BASED QUESTIONS
                # Look for questions after "CAT 2025 Questions (Memory Based)" or similar headings
                memory_questions = []
                
                # Find all h3 headings
                h3_elements = content_div.find_all("h3")
                for h3 in h3_elements:
                    h3_text = h3.get_text(strip=True).lower()
                    if "memory based" in h3_text or "questions" in h3_text:
                        # Get all content after this h3 until next h3 or end
                        current = h3.next_sibling
                        while current and (current.name != "h3"):
                            if current.name == "p":
                                text = current.get_text(strip=True)
                                if text and len(text) > 10:  # Meaningful text
                                    # Check if it's a question (starts with Q: or has question mark)
                                    if text.startswith("Q:") or "?" in text or text[:20].lower().find("question") != -1:
                                        memory_questions.append(text)
                            elif current.name == "ul":
                                # Handle questions in list format
                                for li in current.find_all("li"):
                                    li_text = li.get_text(strip=True)
                                    if li_text:
                                        memory_questions.append(li_text)
                            current = current.next_sibling
                
                # Also look for paragraphs that contain "Q:" pattern
                all_paragraphs = content_div.find_all("p")
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if text and (text.startswith("Q:") or text.startswith("Q ")):
                        memory_questions.append(text)
                
                section["memory_based_questions"] = memory_questions
                
                # ALSO READ - better detection
                # Method 1: Look for text containing "Also Read" or "also read"
                for elem in content_div.find_all(string=lambda text: text and "Also Read" in text):
                    parent = elem.parent
                    # Find next UL after this text
                    next_ul = None
                    current = parent
                    while current:
                        next_sibling = current.find_next_sibling()
                        if next_sibling and next_sibling.name == "ul":
                            next_ul = next_sibling
                            break
                        current = next_sibling
                    
                    if next_ul:
                        for a in next_ul.find_all("a", href=True):
                            title = a.get_text(" ", strip=True)
                            url = a["href"]
                            if title and url:
                                section["also_read"].append({
                                    "title": title,
                                    "url": url
                                })
                        break
                
                # Method 2: Look for UL with links that have article-like titles
                if not section["also_read"]:
                    for ul in content_div.find_all("ul"):
                        links = ul.find_all("a", href=True)
                        if links and len(links) >= 2:
                            # Check if links look like article links (not navigation)
                            first_link_text = links[0].get_text(strip=True)
                            if len(first_link_text) > 20 and "CAT" in first_link_text.upper():
                                for a in links:
                                    title = a.get_text(" ", strip=True)
                                    url = a["href"]
                                    if title and url and "shiksha" in url:
                                        section["also_read"].append({
                                            "title": title,
                                            "url": url
                                        })
                                break
                
                # VIDEO URL - extract real YouTube URL
                iframe = content_div.find("iframe", src=True)
                if iframe:
                    src = iframe["src"]
                    # Check if it's a real YouTube URL, not a placeholder
                    if "youtube.com" in src or "youtu.be" in src:
                        section["video_url"] = src
                    elif "data:image" not in src:  # Not a placeholder
                        section["video_url"] = src
                
                # Also check for YouTube embed div
                if not section["video_url"]:
                    youtube_div = content_div.find("div", class_="vcmsEmbed")
                    if youtube_div:
                        iframe = youtube_div.find("iframe", src=True)
                        if iframe and "youtube" in iframe["src"]:
                            section["video_url"] = iframe["src"]
                
                # ✅ NEW: EXTRACT FAQS FROM THIS SECTION
                try:
                    # Look for FAQ wrapper within the section
                    faq_wrapper = wrapper_soup.select_one(".AnATaggedFaqWrapper")
                    
                    if faq_wrapper:
                        # Find FAQ container
                        faq_container = faq_wrapper.select_one("._0c7561.sectional-faqs")
                        
                        if faq_container:
                            # Extract all FAQs
                            section_faqs = []
                            
                            # Find all question divs
                            question_divs = []
                            
                            # Method 1: Look for divs with IDs containing "::"
                            for div in faq_container.find_all("div", id=True):
                                if "::" in div["id"]:
                                    question_divs.append(div)
                            
                            # Method 2: Look for strong tags with class "flx-box"
                            if not question_divs:
                                for strong in faq_container.find_all("strong", class_="flx-box"):
                                    parent_div = strong.find_parent("div")
                                    if parent_div:
                                        question_divs.append(parent_div)
                            
                            for q_div in question_divs:
                                try:
                                    faq_item = {
                                        "question": "",
                                        "answer": "",
                                        "links": []
                                    }
                                    
                                    # Extract question
                                    question_elem = q_div.find("strong", class_="flx-box")
                                    if question_elem:
                                        question_text = question_elem.get_text(strip=True)
                                        # Clean up question text
                                        question_text = question_text.replace("Q:", "").replace("Q :", "").strip()
                                        faq_item["question"] = question_text
                                    
                                    # Find answer div (next sibling with class "_16f53f")
                                    answer_div = q_div.find_next_sibling("div", class_="_16f53f")
                                    if answer_div:
                                        # Extract answer from wikkiContents
                                        answer_content = answer_div.select_one("div.wikkiContents")
                                        if answer_content:
                                            answer_text = answer_content.get_text(" ", strip=True)
                                            # Clean up answer text
                                            answer_text = answer_text.replace("A:", "").replace("A :", "").strip()
                                            faq_item["answer"] = answer_text
                                            
                                            # Extract links
                                            for link in answer_content.find_all("a", href=True):
                                                faq_item["links"].append({
                                                    "text": link.get_text(strip=True),
                                                    "url": link["href"]
                                                })
                                    
                                    if faq_item["question"] and faq_item["answer"]:
                                        section_faqs.append(faq_item)
                                        
                                except Exception as e:
                                    print(f"  Error parsing FAQ in section {i+1}: {e}")
                                    continue
                            
                            section["faqs"] = section_faqs
                            print(f"  Found {len(section_faqs)} FAQs in this section")
                            
                except Exception as e:
                    print(f"  Error extracting FAQs from section {i+1}: {e}")
                
                # Clean up highlights (remove duplicates and empty)
                section["highlights"] = list(dict.fromkeys([h for h in section["highlights"] if h.strip()]))
                
                # Clean up table data (fix formatting issues)
                cleaned_table = []
                for row in section["table"]:
                    cleaned_row = []
                    for cell in row:
                        # Fix common issues
                        cell = cell.replace("\n\n", "\n")
                        cell = cell.strip()
                        cleaned_row.append(cell)
                    cleaned_table.append(cleaned_row)
                section["table"] = cleaned_table
                
                data["sections"].append(section)
                
            except Exception as e:
                print(f"Error in section {i+1}: {str(e)[:100]}")
                continue
    
    except Exception as e:
        print(f"Error finding sections: {e}")
    
    # Post-process: Remove empty sections
    data["sections"] = [s for s in data["sections"] if s["heading"] or s["highlights"] or s["table"] or s.get("faqs") or s.get("memory_based_questions")]
    
    print(f"\nScraped {len(data['sections'])} valid sections successfully")
    
    # Print summary
    for i, section in enumerate(data["sections"]):
        print(f"\nSection {i+1}: {section['heading']}")
        print(f"  Highlights: {len(section['highlights'])}")
        print(f"  Table rows: {len(section['table'])}")
        print(f"  Also read: {len(section['also_read'])}")
        print(f"  Memory based questions: {len(section.get('memory_based_questions', []))}")
        print(f"  FAQs: {len(section.get('faqs', []))}")
        if section['video_url']:
            print(f"  Video: {section['video_url'][:50]}...")
    
    return data

def scrape_admit_card(driver, URLS):
    driver.get(URLS["admit_card"])
    
    # Better scrolling for lazy loading
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            data["toc"].append(title_txt)
    
    wait = WebDriverWait(driver, 25)
    
    try:
        # Find all section wrappers
        wrappers = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "sectionalWrapperClass"))
        )
        
        print(f"Found {len(wrappers)} sectionalWrapperClass elements")
        
        for i, wrapper in enumerate(wrappers):
            try:
                section = {
                    "heading": "",
                    "process_steps": [],
                    "problem_solution_table": [],
                    "highlights": [],
                    "table": [],
                    "also_read": [],
                    "video_url": "",
                    "image_url": "",
                    "image_caption": "",
                    "faqs": []
                }
                
                # HEADING
                wrapper_html = wrapper.get_attribute("outerHTML")
                wrapper_soup = BeautifulSoup(wrapper_html, "html.parser")
                
                h2_element = wrapper_soup.find("h2")
                if h2_element:
                    section["heading"] = h2_element.get_text(strip=True)
                
                if not section["heading"]:
                    print(f"Skipping section {i+1} - no heading found")
                    continue
                
                print(f"Section {i+1} heading: {section['heading']}")
                
                # Find content div
                content_div = wrapper_soup.select_one("div.wikkiContents.faqAccordian.showFullData")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.wikkiContents")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.faqAccordian")
                if not content_div:
                    content_div = wrapper_soup
                
                # EXTRACT IMAGE AND CAPTION (filter icons)
                try:
                    img_tag = content_div.find("img")
                    if img_tag and img_tag.get("src"):
                        img_src = img_tag["src"]
                        # Skip icons
                        if not any(icon in img_src.lower() for icon in [".svg", "icon", "icons", "bell", "calendar"]):
                            section["image_url"] = img_src
                            
                    caption_div = content_div.find("div", class_="photo-widget-full")
                    if caption_div:
                        caption = caption_div.find("strong", class_="_img-caption")
                        if caption:
                            section["image_caption"] = caption.get_text(strip=True)
                except:
                    pass
                
                # PROCESS STEPS
                try:
                    first_paragraph = content_div.find("p")
                    if first_paragraph:
                        current = first_paragraph
                        while current:
                            next_sibling = current.find_next_sibling()
                            if next_sibling and next_sibling.name == "ul":
                                steps = []
                                for li_elem in next_sibling.find_all("li"):
                                    step_text = li_elem.get_text(" ", strip=True)
                                    step_text = ' '.join(step_text.split())
                                    if step_text:
                                        steps.append(step_text)
                                section["process_steps"] = steps
                                break
                            current = next_sibling
                except Exception as e:
                    print(f"  Error extracting process steps: {e}")
                
                # PROBLEM-SOLUTION TABLE
                try:
                    h3_elements = content_div.find_all("h3")
                    for h3 in h3_elements:
                        h3_text = h3.get_text(strip=True).lower()
                        if "problem" in h3_text:
                            current = h3
                            while current:
                                next_sibling = current.find_next_sibling()
                                if next_sibling and next_sibling.name == "table":
                                    table_data = []
                                    rows = next_sibling.find_all("tr")
                                    for row in rows:
                                        cols = []
                                        cells = row.find_all(["th", "td"])
                                        for cell in cells:
                                            cell_text = cell.get_text(" ", strip=True)
                                            cols.append(cell_text)
                                        if cols:
                                            table_data.append(cols)
                                    section["problem_solution_table"] = table_data
                                    break
                                current = next_sibling
                            break
                except Exception as e:
                    print(f"  Error extracting problem-solution table: {e}")
                
                # HIGHLIGHTS (avoid duplicates with process_steps)
                all_uls = content_div.find_all("ul")
                for ul in all_uls:
                    lis = ul.find_all("li")
                    if lis and len(lis) > 2:
                        first_li_text = lis[0].get_text(strip=True)
                        if len(first_li_text) < 150 and not first_li_text.startswith("http"):
                            # Skip if this is the process steps ul
                            if "visit" not in first_li_text.lower() and "click" not in first_li_text.lower():
                                for li_elem in lis:
                                    text = li_elem.get_text(" ", strip=True)
                                    # Skip if already in process_steps
                                    if text and text not in section["process_steps"]:
                                        section["highlights"].append(text)
                                break
                
                # TABLE
                tables = content_div.find_all("table")
                if tables:
                    for table_idx, table in enumerate(tables):
                        # Skip if this is the problem-solution table
                        if table_idx == 0 and section.get("problem_solution_table"):
                            continue
                            
                        table_data = []
                        rows = table.find_all("tr")
                        for row in rows:
                            cols = []
                            cells = row.find_all(["th", "td"])
                            for cell in cells:
                                cell_text = ""
                                for content in cell.contents:
                                    if content.name == "br":
                                        cell_text += "\n"
                                    elif content.name is None:
                                        cell_text += str(content)
                                    elif content.name == "p":
                                        cell_text += content.get_text() + "\n"
                                cols.append(cell_text.strip())
                            
                            if cols and any(cols):
                                table_data.append(cols)
                        
                        if table_data:
                            if not section["table"]:
                                section["table"] = table_data
                            else:
                                if "additional_tables" not in section:
                                    section["additional_tables"] = []
                                section["additional_tables"].append(table_data)
                
                # ALSO READ (filter short titles)
                for elem in content_div.find_all(string=lambda text: text and "Also Read" in text):
                    parent = elem.parent
                    next_ul = None
                    current = parent
                    while current:
                        next_sibling = current.find_next_sibling()
                        if next_sibling and next_sibling.name == "ul":
                            next_ul = next_sibling
                            break
                        current = next_sibling
                    
                    if next_ul:
                        for a in next_ul.find_all("a", href=True):
                            title = a.get_text(" ", strip=True)
                            url = a["href"]
                            # Filter short titles
                            if title and url and len(title.strip()) > 1:
                                section["also_read"].append({
                                    "title": title,
                                    "url": url
                                })
                        break
                
                # VIDEO URL
                iframe = content_div.find("iframe", src=True)
                if iframe:
                    src = iframe["src"]
                    if "youtube.com" in src or "youtu.be" in src:
                        section["video_url"] = src
                    elif "data:image" not in src:
                        section["video_url"] = src
                
                if not section["video_url"]:
                    youtube_div = content_div.find("div", class_="vcmsEmbed")
                    if youtube_div:
                        iframe = youtube_div.find("iframe", src=True)
                        if iframe and "youtube" in iframe["src"]:
                            section["video_url"] = iframe["src"]
                
                # FAQS
                try:
                    faq_wrapper = wrapper_soup.select_one(".AnATaggedFaqWrapper")
                    
                    if faq_wrapper:
                        faq_container = faq_wrapper.select_one("._0c7561.sectional-faqs")
                        
                        if faq_container:
                            section_faqs = []
                            question_divs = []
                            
                            # Method 1: IDs with "::"
                            for div in faq_container.find_all("div", id=True):
                                if "::" in div["id"]:
                                    question_divs.append(div)
                            
                            # Method 2: strong tags
                            if not question_divs:
                                for strong in faq_container.find_all("strong", class_="flx-box"):
                                    parent_div = strong.find_parent("div")
                                    if parent_div:
                                        question_divs.append(parent_div)
                            
                            for q_div in question_divs:
                                try:
                                    faq_item = {
                                        "question": "",
                                        "answer": "",
                                        "links": []
                                    }
                                    
                                    question_elem = q_div.find("strong", class_="flx-box")
                                    if question_elem:
                                        question_text = question_elem.get_text(strip=True)
                                        question_text = question_text.replace("Q:", "").replace("Q :", "").strip()
                                        faq_item["question"] = question_text
                                    
                                    answer_div = q_div.find_next_sibling("div", class_="_16f53f")
                                    if answer_div:
                                        answer_content = answer_div.select_one("div.wikkiContents")
                                        if answer_content:
                                            answer_text = answer_content.get_text(" ", strip=True)
                                            answer_text = answer_text.replace("A:", "").replace("A :", "").strip()
                                            faq_item["answer"] = answer_text
                                            
                                            for link in answer_content.find_all("a", href=True):
                                                faq_item["links"].append({
                                                    "text": link.get_text(strip=True),
                                                    "url": link["href"]
                                                })
                                    
                                    if faq_item["question"] and faq_item["answer"]:
                                        section_faqs.append(faq_item)
                                        
                                except Exception as e:
                                    print(f"  Error parsing FAQ: {e}")
                                    continue
                            
                            section["faqs"] = section_faqs
                            print(f"  Found {len(section_faqs)} FAQs")
                            
                except Exception as e:
                    print(f"  Error extracting FAQs: {e}")
                
                # Clean up
                section["highlights"] = list(dict.fromkeys([h for h in section["highlights"] if h.strip()]))
                
                cleaned_table = []
                for row in section["table"]:
                    cleaned_row = []
                    for cell in row:
                        cell = cell.replace("\n\n", "\n").strip()
                        cleaned_row.append(cell)
                    cleaned_table.append(cleaned_row)
                section["table"] = cleaned_table
                
                section["process_steps"] = [step for step in section["process_steps"] if step.strip()]
                
                data["sections"].append(section)
                
            except Exception as e:
                print(f"Error in section {i+1}: {str(e)[:100]}")
                continue
    
    except Exception as e:
        print(f"Error finding sections: {e}")
    
    # Post-process: Remove empty sections and filter out promotional sections
    filtered_sections = []
    promotional_keywords = ["1650Institutes", "Explore more", "News & Updates"]
    
    for s in data["sections"]:
        # Skip promotional sections
        if any(keyword in s["heading"] for keyword in promotional_keywords):
            continue
        
        # Keep if has meaningful content
        if (s["heading"] and 
            (s.get("process_steps") or s.get("table") or s.get("highlights") or 
             s.get("faqs") or s.get("problem_solution_table"))):
            filtered_sections.append(s)
    
    data["sections"] = filtered_sections
        
    return data

def scrape_dates(driver, URLS):
    driver.get(URLS["dates"])
    
    # Better scrolling for lazy loading
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            data["toc"].append(title_txt)
    
    wait = WebDriverWait(driver, 25)
    
    try:
        # Find all section wrappers
        wrappers = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "sectionalWrapperClass"))
        )
        
        print(f"Found {len(wrappers)} sectionalWrapperClass elements")
        
        for i, wrapper in enumerate(wrappers):
            try:
                section = {
                    "heading": "",
                    "key_highlights": [],  # ✅ CHANGED: Better structure
                    "statistics": {},
                    "highlights": [],
                    "table": [],
                    "also_read": [],
                    "video_url": "",
                    "image_url": "",
                    "image_caption": "",
                    "call_to_action": {},
                    "faqs": []
                }
                
                # HEADING
                wrapper_html = wrapper.get_attribute("outerHTML")
                wrapper_soup = BeautifulSoup(wrapper_html, "html.parser")
                
                h2_element = wrapper_soup.find("h2")
                if h2_element:
                    section["heading"] = h2_element.get_text(strip=True)
                
                if not section["heading"]:
                    print(f"Skipping section {i+1} - no heading found")
                    continue
                
                print(f"Section {i+1} heading: {section['heading']}")
                
                # Find content div
                content_div = wrapper_soup.select_one("div.wikkiContents.faqAccordian.showFullData")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.wikkiContents")
                if not content_div:
                    content_div = wrapper_soup.select_one("div.faqAccordian")
                if not content_div:
                    content_div = wrapper_soup
                
                # ✅ IMPROVED: EXTRACT STATISTICS FROM INTRODUCTION
                try:
                    intro_paragraphs = content_div.find_all("p")
                    for p in intro_paragraphs:
                        text = p.get_text(strip=True)
                        if "lakh candidates" in text.lower() or "candidates" in text.lower():
                            import re
                            
                            # Extract numbers
                            numbers = re.findall(r'(\d+\.?\d*)\s*(lakh|lacs|thousand)', text, re.IGNORECASE)
                            if numbers:
                                for num, unit in numbers:
                                    if "registered" in text.lower():
                                        section["statistics"]["registered_candidates"] = f"{num} {unit}"
                                    elif "appeared" in text.lower():
                                        section["statistics"]["appeared_candidates"] = f"{num} {unit}"
                            
                            # Extract IIM information
                            if "IIM" in text:
                                iim_match = re.search(r'IIM\s+[A-Za-z\s]+', text)
                                if iim_match:
                                    section["statistics"]["convening_iim"] = iim_match.group(0)
                                    
                except Exception as e:
                    print(f"  Error extracting statistics: {e}")
                
                # ✅ IMPROVED: KEY HIGHLIGHTS - PARSE PROPERLY
                try:
                    # Find all tables
                    tables = content_div.find_all("table")
                    for table in tables:
                        table_text = table.get_text().lower()
                        
                        # Check if this is the key highlights table
                        if "features" in table_text or "details" in table_text or "exam" in table_text:
                            key_highlights = []
                            
                            rows = table.find_all("tr")
                            for row_idx, row in enumerate(rows):
                                # Skip header if it's the first row
                                if row_idx == 0:
                                    continue
                                    
                                cells = row.find_all(["td"])
                                if len(cells) >= 2:
                                    feature_cell = cells[0]
                                    details_cell = cells[1]
                                    
                                    # Extract feature name
                                    feature = feature_cell.get_text(" ", strip=True)
                                    
                                    # Extract details - handle different formats
                                    details_text = details_cell.get_text(" ", strip=True)
                                    details_links = []
                                    details_list = []
                                    
                                    # Check if details cell has lists
                                    ul = details_cell.find("ul")
                                    if ul:
                                        # Extract list items
                                        for li in ul.find_all("li"):
                                            li_text = li.get_text(" ", strip=True)
                                            li_links = []
                                            
                                            # Extract links from list item
                                            for a in li.find_all("a", href=True):
                                                li_links.append({
                                                    "text": a.get_text(strip=True),
                                                    "url": a["href"]
                                                })
                                            
                                            if li_links:
                                                details_list.append({
                                                    "text": li_text,
                                                    "links": li_links
                                                })
                                            else:
                                                details_list.append(li_text)
                                        
                                        details = {
                                            "text": details_text,
                                            "list": details_list
                                        }
                                    else:
                                        # Check for individual links
                                        links = []
                                        for a in details_cell.find_all("a", href=True):
                                            links.append({
                                                "text": a.get_text(strip=True),
                                                "url": a["href"]
                                            })
                                        
                                        if links:
                                            details = {
                                                "text": details_text,
                                                "links": links
                                            }
                                        else:
                                            details = details_text
                                    
                                    key_highlights.append({
                                        "feature": feature,
                                        "details": details
                                    })
                            
                            if key_highlights:
                                section["key_highlights"] = key_highlights
                                break
                                
                except Exception as e:
                    print(f"  Error extracting key highlights: {e}")
                    import traceback
                    traceback.print_exc()
                
                # ✅ IMPROVED: CALL TO ACTION
                try:
                    # Look for div with border style
                    for div in content_div.find_all("div"):
                        style = div.get("style", "")
                        if "border: 1px solid #666666" in style or "background: #f3f6f8" in style:
                            cta_text = div.get_text(" ", strip=True)
                            cta_link = div.find("a", href=True)
                            
                            if cta_link:
                                section["call_to_action"] = {
                                    "text": cta_text[:200] + "..." if len(cta_text) > 200 else cta_text,
                                    "button_text": cta_link.get_text(strip=True),
                                    "url": cta_link["href"]
                                }
                                break
                except Exception as e:
                    print(f"  Error extracting call to action: {e}")
                
                # HIGHLIGHTS
                all_uls = content_div.find_all("ul")
                for ul in all_uls:
                    # Skip if this ul is inside a table (already captured in key_highlights)
                    if ul.find_parent("table"):
                        continue
                        
                    lis = ul.find_all("li")
                    if lis:
                        for li_elem in lis:
                            text = li_elem.get_text(" ", strip=True)
                            if text and len(text) > 10:  # Meaningful text
                                # Check if not already in key_highlights
                                if not any(text in str(h) for h in section.get("key_highlights", [])):
                                    section["highlights"].append(text)
                
                # REGULAR TABLES (excluding key highlights table)
                tables = content_div.find_all("table")
                if tables:
                    key_highlight_tables_found = 0
                    for table in tables:
                        table_text = table.get_text().lower()
                        
                        # Skip key highlights tables
                        if "features" in table_text or "details" in table_text:
                            key_highlight_tables_found += 1
                            if key_highlight_tables_found > 1:
                                # This is an additional key highlights table, skip it
                                continue
                            else:
                                # First key highlights table, already processed
                                continue
                        
                        # Process regular tables
                        table_data = []
                        rows = table.find_all("tr")
                        for row in rows:
                            cols = []
                            cells = row.find_all(["th", "td"])
                            for cell in cells:
                                cell_text = cell.get_text(" ", strip=True)
                                cols.append(cell_text)
                            
                            if cols and any(cols):
                                table_data.append(cols)
                        
                        if table_data:
                            section["table"].append(table_data)
                
                # ALSO READ
                for elem in content_div.find_all(string=lambda text: text and "Also Read" in text):
                    parent = elem.parent
                    next_ul = None
                    current = parent
                    while current:
                        next_sibling = current.find_next_sibling()
                        if next_sibling and next_sibling.name == "ul":
                            next_ul = next_sibling
                            break
                        current = next_sibling
                    
                    if next_ul:
                        for a in next_ul.find_all("a", href=True):
                            title = a.get_text(" ", strip=True)
                            url = a["href"]
                            if title and url and len(title.strip()) > 1:
                                section["also_read"].append({
                                    "title": title,
                                    "url": url
                                })
                        break
                
                # VIDEO URL
                iframe = content_div.find("iframe", src=True)
                if iframe:
                    src = iframe["src"]
                    if "youtube.com" in src or "youtu.be" in src:
                        section["video_url"] = src
                
                # ✅ IMPROVED: EXTRACT FAQS
                try:
                    faq_wrapper = wrapper_soup.select_one(".AnATaggedFaqWrapper")
                    
                    if faq_wrapper:
                        faq_container = faq_wrapper.select_one("._0c7561.sectional-faqs")
                        
                        if faq_container:
                            section_faqs = []
                            
                            # Find question-answer pairs
                            # Look for divs with question
                            question_divs = faq_container.find_all("div", id=lambda x: x and "::" in str(x))
                            
                            for q_div in question_divs:
                                try:
                                    faq_item = {
                                        "question": "",
                                        "answer": "",
                                        "links": []
                                    }
                                    
                                    # Extract question
                                    question_elem = q_div.find("strong", class_="flx-box")
                                    if question_elem:
                                        question_text = question_elem.get_text(strip=True)
                                        question_text = question_text.replace("Q:", "").replace("Q :", "").strip()
                                        faq_item["question"] = question_text
                                    
                                    # Find answer
                                    answer_div = q_div.find_next_sibling("div", class_="_16f53f")
                                    if answer_div:
                                        answer_content = answer_div.select_one("div.wikkiContents")
                                        if answer_content:
                                            # Get all text from answer
                                            answer_text = ""
                                            for elem in answer_content.descendants:
                                                if elem.name is None:  # Text node
                                                    answer_text += str(elem)
                                                elif elem.name == "a":
                                                    answer_text += elem.get_text() + " "
                                            
                                            answer_text = answer_text.strip()
                                            answer_text = answer_text.replace("A:", "").replace("A :", "").strip()
                                            faq_item["answer"] = answer_text
                                            
                                            # Extract links
                                            for link in answer_content.find_all("a", href=True):
                                                faq_item["links"].append({
                                                    "text": link.get_text(strip=True),
                                                    "url": link["href"]
                                                })
                                    
                                    if faq_item["question"] and faq_item["answer"]:
                                        section_faqs.append(faq_item)
                                        
                                except Exception as e:
                                    print(f"  Error parsing FAQ: {e}")
                                    continue
                            
                            section["faqs"] = section_faqs
                            print(f"  Found {len(section_faqs)} FAQs")
                            
                except Exception as e:
                    print(f"  Error extracting FAQs: {e}")
                
                # Clean up highlights
                section["highlights"] = list(dict.fromkeys([h for h in section["highlights"] if h.strip()]))
                
                data["sections"].append(section)
                
            except Exception as e:
                print(f"Error in section {i+1}: {str(e)[:100]}")
                import traceback
                traceback.print_exc()
                continue
    
    except Exception as e:
        print(f"Error finding sections: {e}")
        import traceback
        traceback.print_exc()
    
    # Post-process: Remove empty sections
    filtered_sections = []
    
    for s in data["sections"]:
        # Check if section has meaningful content
        has_content = False
        
        # Check key_highlights
        if s.get("key_highlights") and len(s["key_highlights"]) > 0:
            has_content = True
        
        # Check table
        if s.get("table") and len(s["table"]) > 0:
            has_content = True
        
        # Check highlights
        if s.get("highlights") and len(s["highlights"]) > 0:
            has_content = True
        
        # Check FAQs
        if s.get("faqs") and len(s["faqs"]) > 0:
            has_content = True
        
        # Check statistics
        if s.get("statistics") and len(s["statistics"]) > 0:
            has_content = True
        
        if s["heading"] and has_content:
            filtered_sections.append(s)
    
    data["sections"] = filtered_sections
    
    return data

def scrape_mock_test(driver, URLS):
    driver.get(URLS["mock_test"])
    
    # Better scrolling for lazy loading
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE (दोनों स्ट्रक्चर के लिए)
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        # पहले content_toc_573797 वाला title देखें
        new_title = soup.find("h2", id="content_toc_573797")
        if not new_title:
            # फिर content_toc_523057 वाला title देखें
            new_title = soup.find("h2", id="content_toc_523057")
        
        if new_title:
            data["Title"] = new_title.text.strip()
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META (दोनों स्ट्रक्चर के लिए)
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO (दोनों स्ट्रक्चर के लिए)
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        # पहले wikiiContents_mocktest__1 से intro
        wiki_content_1 = soup.find("div", {"id": "wikkiContents_mocktest__1"})
        if wiki_content_1:
            first_p = wiki_content_1.find("p")
            if first_p:
                data["intro"].append(first_p.get_text(" ", strip=True))
        else:
            # फिर wikiiContents_mocktest__3 से intro
            wiki_content_3 = soup.find("div", {"id": "wikkiContents_mocktest__3"})
            if wiki_content_3:
                paragraphs = wiki_content_3.find_all("p")
                for p in paragraphs[:2]:  # पहले 2 paragraphs intro के लिए
                    txt = p.get_text(" ", strip=True)
                    if txt:
                        data["intro"].append(txt)

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC (Table of Contents)
    toc_items = []
    
    # पहले TOC wrapper से
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items

    # ==================== SECTIONS PART ====================
    sections_data = []
    
    # 1. पहला HTML structure (CAT Free Mock Test with solutions)
    wiki_content_1 = soup.find("div", {"id": "wikkiContents_mocktest__1"})
    if wiki_content_1:
        # पहले paragraph को sections में add करें
        first_p = wiki_content_1.find("p")
        if first_p:
            first_para_text = first_p.get_text(" ", strip=True)
            if first_para_text:
                sections_data.append({
                    "section_title": "CAT Free Mock Test with solutions by Shiksha",
                    "content": [first_para_text]
                })
        
        # Key Aspects सेक्शन
        h3_tag = wiki_content_1.find("h3")
        if h3_tag and "Key Aspects" in h3_tag.text:
            section_content = []
            ul_tag = h3_tag.find_next("ul")
            if ul_tag:
                for li in ul_tag.find_all("li"):
                    txt = li.get_text(" ", strip=True)
                    if txt:
                        section_content.append(f"• {txt}")
            
            if section_content:
                sections_data.append({
                    "section_title": h3_tag.text.strip(),
                    "content": section_content
                })
        
        # Mock Test Table सेक्शन (PDF links)
        table_1 = wiki_content_1.find("table")
        if table_1:
            table_content = []
            
            # सभी PDF लिंक्स निकालें
            for a_tag in table_1.find_all("a", class_="smce-docs"):
                link_text = a_tag.get_text(strip=True)
                link_href = a_tag.get("href", "")
                
                # अगर href नहीं है तो data-link देखें
                if not link_href and a_tag.get("data-link"):
                    link_href = a_tag.get("data-link")
                
                if link_href:
                    # पिछला strong tag देखें
                    prev_strong = a_tag.find_previous("strong")
                    if prev_strong:
                        label = prev_strong.get_text(strip=True)
                        table_content.append(f"{label}: {link_href}")
                    else:
                        table_content.append(f"{link_text}: {link_href}")
            
            if table_content:
                sections_data.append({
                    "section_title": "CAT Free Mock Tests with Download Links",
                    "content": table_content
                })

    # 2. दूसरा HTML structure (What is the CAT Mock Test Structure?)
    wiki_content_3 = soup.find("div", {"id": "wikkiContents_mocktest__3"})
    if wiki_content_3:
        # "What is the CAT Mock Test Structure?" सेक्शन
        all_paragraphs = wiki_content_3.find_all("p")
        if len(all_paragraphs) >= 2:
            # पहले 2 paragraphs
            content_paragraphs = []
            for p in all_paragraphs[:2]:
                txt = p.get_text(" ", strip=True)
                if txt:
                    content_paragraphs.append(txt)
            
            if content_paragraphs:
                sections_data.append({
                    "section_title": "What is the CAT Mock Test Structure?",
                    "content": content_paragraphs
                })
        
        # Table content
        table_container = wiki_content_3.find("div", class_="table-container")
        if table_container:
            table_3 = table_container.find("table")
            if table_3:
                table_data = []
                rows = table_3.find_all("tr")
                
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    row_content = []
                    for cell in cells:
                        # Text निकालें
                        cell_text = cell.get_text(" ", strip=True)
                        if cell_text:
                            row_content.append(cell_text)
                        
                        # Lists निकालें
                        lists = cell.find_all("ul")
                        for ul in lists:
                            list_items = []
                            for li in ul.find_all("li"):
                                li_text = li.get_text(" ", strip=True)
                                if li_text:
                                    list_items.append(f"• {li_text}")
                            if list_items:
                                row_content.extend(list_items)
                    
                    if row_content:
                        table_data.append(" | ".join(row_content))
                
                if table_data:
                    sections_data.append({
                        "section_title": "CAT 2025 Mock Test Details",
                        "content": table_data
                    })
        
        # "Check Out:" links
        check_out_ul = wiki_content_3.find("ul")
        if check_out_ul:
            check_out_content = []
            for li in check_out_ul.find_all("li"):
                link = li.find("a")
                if link:
                    link_text = link.get_text(" ", strip=True)
                    link_href = link.get("href", "")
                    if link_text and link_href:
                        check_out_content.append(f"{link_text}: {link_href}")
            
            if check_out_content:
                sections_data.append({
                    "section_title": "Check Out CAT Preparation Resources",
                    "content": check_out_content
                })

    # 3. FAQ सेक्शन (दोनों structures के लिए)
    # पहले AnATaggedFaqWrapper ढूँढें
    faq_wrappers = soup.find_all("div", class_="AnATaggedFaqWrapper")
    
    for faq_wrapper in faq_wrappers:
        # Commonly asked questions heading
        common_heading = faq_wrapper.find("h5")
        if common_heading and "Commonly asked" in common_heading.text:
            # Check if already exists
            if not any("Commonly Asked" in s["section_title"] for s in sections_data):
                sections_data.append({
                    "section_title": "Commonly Asked Questions",
                    "content": ["Frequently asked questions about CAT preparation and mock tests"]
                })
        
        # अलग-अलग FAQ questions
        faq_items = faq_wrapper.find_all("div", class_="html-0 c5db62 listener")
        for faq in faq_items:
            question_elem = faq.find("strong", class_="flx-box")
            if question_elem:
                question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                
                # Check if question already exists
                if not any(question == s["section_title"] for s in sections_data):
                    # Answer ढूँढें
                    answer_div = faq.find_next("div", class_="wikkiContents")
                    answer_text = ""
                    if answer_div:
                        paragraphs = answer_div.find_all("p")
                        if paragraphs:
                            answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                    
                    if question and answer_text:
                        sections_data.append({
                            "section_title": question,
                            "content": [answer_text]
                        })

    data["sections"] = sections_data
    # ==================== END SECTIONS PART ====================
    
    return data

def scrape_registration(driver, URLS):
    driver.get(URLS["registration"])
    
    # Better scrolling for lazy loading with more wait time for images
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Increased wait time for images to load
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE (for both structures)
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        # Check all possible title IDs
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META (for both structures)
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO (for both structures)
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        # Get intro from all possible wiki contents
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC (Table of Contents)
    toc_items = []
    
    # First from TOC wrapper
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items

    # ==================== SECTIONS PART ====================
    sections_data = []
    
    # 1. First Registration HTML structure (wikiiContents_registration__1)
    wiki_content_reg_1 = soup.find("div", {"id": "wikkiContents_registration__1"})
    if wiki_content_reg_1:
        # First paragraph - IIM CAT Registration highlights
        first_p = wiki_content_reg_1.find("p")
        if first_p:
            first_para_text = first_p.get_text(" ", strip=True)
            if first_para_text:
                sections_data.append({
                    "section_title": "IIM CAT Registration 2025: Highlights",
                    "content": [first_para_text]
                })
        
        # Registration table section
        table_1 = wiki_content_reg_1.find("table")
        if table_1:
            table_content = []
            rows = table_1.find_all("tr")
            
            for row in rows:
                cells = row.find_all(["th", "td"])
                row_content = []
                for cell in cells:
                    # Extract text
                    cell_text = cell.get_text(" ", strip=True)
                    if cell_text:
                        row_content.append(cell_text)
                    
                    # Extract lists
                    lists = cell.find_all("ul")
                    for ul in lists:
                        list_items = []
                        for li_item in ul.find_all("li"):
                            li_text = li_item.get_text(" ", strip=True)
                            if li_text:
                                list_items.append(f"• {li_text}")
                        if list_items:
                            row_content.extend(list_items)
                
                if row_content:
                    table_content.append(" | ".join(row_content))
            
            if table_content:
                sections_data.append({
                    "section_title": "CAT 2025 Registration Details",
                    "content": table_content
                })
        
        # "Also Read:" links
        also_read_ul = wiki_content_reg_1.find("ul")
        if also_read_ul:
            also_read_content = []
            for li_item in also_read_ul.find_all("li"):
                link = li_item.find("a")
                if link:
                    link_text = link.get_text(" ", strip=True)
                    link_href = link.get("href", "")
                    if link_text and link_href:
                        also_read_content.append(f"{link_text}: {link_href}")
            
            if also_read_content:
                sections_data.append({
                    "section_title": "Also Read",
                    "content": also_read_content
                })

    # 2. Second Registration HTML structure (wikiiContents_registration__3)
    wiki_content_reg_3 = soup.find("div", {"id": "wikkiContents_registration__3"})
    if wiki_content_reg_3:
        # First paragraph - IIM CAT 2025 Registration Process
        first_p_reg3 = wiki_content_reg_3.find("p")
        if first_p_reg3:
            first_para_text_reg3 = first_p_reg3.get_text(" ", strip=True)
            if first_para_text_reg3:
                sections_data.append({
                    "section_title": "IIM CAT 2025 Registration Process",
                    "content": [first_para_text_reg3]
                })
        
        # IMAGE LINKS - first image (FIXED VERSION)
        photo_widgets = wiki_content_reg_3.find_all("div", class_="photo-widget-full")
        processed_images = []
        for photo_widget in photo_widgets:
            # Find image
            img_tag = photo_widget.find("img")
            if img_tag:
                # Check multiple attributes for image URL (handle lazy loading)
                img_src = img_tag.get("src", "")
                
                # If src is a data:image (placeholder), check for actual image in data-src
                if img_src and img_src.startswith('data:image'):
                    # Try to get actual image from data-src attribute (common for lazy loading)
                    img_src = img_tag.get("data-src", img_tag.get("data-lazy-src", ""))
                
                # Also check for srcset
                if not img_src or img_src.startswith('data:'):
                    srcset = img_tag.get("srcset", "")
                    if srcset:
                        # Take first URL from srcset
                        img_src = srcset.split(',')[0].strip().split(' ')[0]
                
                img_alt = img_tag.get("alt", "CAT Image")
                if img_src and not img_src.startswith('data:') and img_src not in processed_images:
                    processed_images.append(img_src)
                    # Find caption
                    caption_tag = photo_widget.find("p", class_="_img-caption")
                    caption = caption_tag.get_text(strip=True) if caption_tag else img_alt
                    
                    sections_data.append({
                        "section_title": f"Image: {caption}",
                        "content": [f"Image URL: {img_src}"]
                    })
        
        # "Register for CAT 2025" section
        register_h3 = wiki_content_reg_3.find("h3")
        if register_h3 and "Register for CAT 2025" in register_h3.text:
            register_content = []
            
            # iimcat.ac.in link
            register_link = register_h3.find_next("a")
            if register_link and "iimcat.ac.in" in register_link.get("href", ""):
                link_href = register_link.get("href", "")
                register_content.append(f"Registration Link: {link_href}")
            
            register_ul = register_h3.find_next("ul")
            if register_ul:
                for li_item in register_ul.find_all("li"):
                    li_text = li_item.get_text(" ", strip=True)
                    if li_text:
                        register_content.append(f"• {li_text}")
            
            if register_content:
                sections_data.append({
                    "section_title": register_h3.text.strip(),
                    "content": register_content
                })
        
        # "Fill CAT Application Form 2025" section
        fill_form_headings = wiki_content_reg_3.find_all("h3")
        for heading in fill_form_headings:
            if "Fill CAT Application Form 2025" in heading.text:
                fill_form_content = []
                
                # Paragraph after heading
                next_p = heading.find_next("p")
                if next_p:
                    fill_form_content.append(next_p.get_text(" ", strip=True))
                
                # Second image (CAT application form)
                next_photo = heading.find_next("div", class_="photo-widget-full")
                if next_photo:
                    img_tag = next_photo.find("img")
                    if img_tag:
                        img_src = img_tag.get("src", "")
                        
                        # If src is a data:image, check for actual image
                        if img_src and img_src.startswith('data:image'):
                            img_src = img_tag.get("data-src", img_tag.get("data-lazy-src", ""))
                        
                        if not img_src or img_src.startswith('data:'):
                            srcset = img_tag.get("srcset", "")
                            if srcset:
                                img_src = srcset.split(',')[0].strip().split(' ')[0]
                        
                        img_alt = img_tag.get("alt", "CAT Application Form")
                        if img_src and not img_src.startswith('data:') and img_src not in processed_images:
                            processed_images.append(img_src)
                            fill_form_content.append(f"Image: {img_alt} - {img_src}")
                
                # 6 sections list items
                ol_tag = wiki_content_reg_3.find("ol")
                if ol_tag:
                    for li_item in ol_tag.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            # Clean the text
                            li_text = li_text.replace("&nbsp;", " ").strip()
                            fill_form_content.append(f"• {li_text}")
                
                if fill_form_content:
                    sections_data.append({
                        "section_title": heading.text.strip(),
                        "content": fill_form_content
                    })
                break
        
        # Payment information - collect all paragraphs
        payment_content = []
        all_paragraphs = wiki_content_reg_3.find_all("p")
        
        for p_tag in all_paragraphs:
            p_text = p_tag.get_text(" ", strip=True)
            if p_text and ("ayment of CAT Registration Fees" in p_text or 
                          "The third and last step in CAT exam registration" in p_text):
                # Fix "Payment" text
                if p_text.startswith("ayment"):
                    p_text = "P" + p_text
                if p_text not in payment_content:
                    payment_content.append(p_text)
        
        if payment_content:
            sections_data.append({
                "section_title": "CAT Registration Fee Payment",
                "content": payment_content
            })
        
        # VIDEO EMBED (FIXED VERSION)
        video_div = wiki_content_reg_3.find("div", class_="vcmsEmbed")
        if video_div:
            iframe_tag = video_div.find("iframe")
            if iframe_tag:
                video_src = iframe_tag.get("src", "")
                
                # If src is not a full YouTube URL, check for data-src
                if video_src and not video_src.startswith('https://www.youtube.com'):
                    # Check for YouTube embed in data-src
                    data_src = iframe_tag.get("data-src", "")
                    if "youtube.com" in data_src:
                        video_src = data_src
                    
                    # Also check for YouTube URL in other attributes
                    if not video_src or "youtube.com" not in video_src:
                        # Check all attributes for YouTube URL
                        for attr_name, attr_value in iframe_tag.attrs.items():
                            if "youtube.com" in str(attr_value):
                                video_src = attr_value
                                break
                
                if video_src and ("youtube.com" in video_src or "youtu.be" in video_src):
                    sections_data.append({
                        "section_title": "CAT Registration Video Tutorial",
                        "content": [f"Video URL: {video_src}"]
                    })
        
        # "Also Read:" link
        also_read_link = wiki_content_reg_3.find("a", href=lambda x: x and "cat-eligibility" in x)
        if also_read_link:
            link_text = also_read_link.get_text(" ", strip=True)
            link_href = also_read_link.get("href", "")
            if link_text and link_href:
                # Check if this also read section already exists
                if not any(s["section_title"] == "Also Read" for s in sections_data):
                    sections_data.append({
                        "section_title": "Also Read",
                        "content": [f"{link_text}: {link_href}"]
                    })

    # 3. New Registration HTML structure (wikkiContents_registration__4) - ADDED THIS SECTION
    wiki_content_reg_4 = soup.find("div", {"id": "wikkiContents_registration__4"})
    if wiki_content_reg_4:
        # Extract title from h2 with id content_toc_554141
        section_title_h2 = soup.find("h2", id="content_toc_554141")
        section_title = section_title_h2.text.strip() if section_title_h2 else "What is CAT Exam Fees?"
        
        # Extract content
        content_items = []
        
        # First paragraph
        first_p = wiki_content_reg_4.find("p")
        if first_p:
            para_text = first_p.get_text(" ", strip=True)
            if para_text:
                content_items.append(para_text)
        
        # Table extraction
        table = wiki_content_reg_4.find("table")
        if table:
            table_content = []
            rows = table.find_all("tr")
            
            for row in rows:
                cells = row.find_all(["th", "td"])
                row_content = []
                for cell in cells:
                    cell_text = cell.get_text(" ", strip=True)
                    if cell_text:
                        row_content.append(cell_text)
                
                if row_content:
                    table_content.append(" | ".join(row_content))
            
            if table_content:
                content_items.extend(table_content)
        
        if content_items:
            sections_data.append({
                "section_title": section_title,
                "content": content_items
            })
        
        # FAQ section inside this div
        faq_wrapper_reg_4 = wiki_content_reg_4.find_next("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper_reg_4:
            faq_items = faq_wrapper_reg_4.find_all("div", class_="html-0 c5db62 listener")
            for faq in faq_items:
                question_elem = faq.find("strong", class_="flx-box")
                if question_elem:
                    question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                    
                    # Check if question already exists
                    if not any(question == s["section_title"] for s in sections_data):
                        # Find answer
                        answer_div = faq.find_next("div", class_="wikkiContents")
                        answer_text = ""
                        if answer_div:
                            paragraphs = answer_div.find_all("p")
                            if paragraphs:
                                answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                            else:
                                answer_div_content = answer_div.find("div")
                                if answer_div_content:
                                    answer_text = answer_div_content.get_text(" ", strip=True)
                                else:
                                    answer_text = answer_div.get_text(" ", strip=True)
                        
                        if question and answer_text:
                            # Remove "A:"
                            if answer_text.startswith("A:"):
                                answer_text = answer_text[2:].strip()
                            
                            sections_data.append({
                                "section_title": question,
                                "content": [answer_text]
                            })

    # 4. New Registration HTML structure (wikkiContents_registration__5) - ADDED THIS SECTION
    wiki_content_reg_5 = soup.find("div", {"id": "wikkiContents_registration__5"})
    if wiki_content_reg_5:
        # Extract title from h2 with id content_toc_861716
        section_title_h2 = soup.find("h2", id="content_toc_861716")
        section_title = section_title_h2.text.strip() if section_title_h2 else "Documents Required for CAT 2025 Application Form"
        
        # Extract content
        content_items = []
        
        # First paragraph
        first_p = wiki_content_reg_5.find("p")
        if first_p:
            para_text = first_p.get_text(" ", strip=True)
            if para_text:
                content_items.append(para_text)
        
        # Extract unordered list items
        ul_list = wiki_content_reg_5.find("ul")
        if ul_list:
            for li_item in ul_list.find_all("li"):
                li_text = li_item.get_text(" ", strip=True)
                if li_text:
                    content_items.append(f"• {li_text}")
        
        # Extract h3 headings and their content
        h3_headings = wiki_content_reg_5.find_all("h3")
        for h3 in h3_headings:
            heading_text = h3.get_text(" ", strip=True)
            if heading_text:
                # Add heading as a separate item
                content_items.append(heading_text)
                
                # Get paragraph after h3
                next_p = h3.find_next("p")
                if next_p:
                    para_text = next_p.get_text(" ", strip=True)
                    if para_text:
                        content_items.append(para_text)
                
                # Get table after h3
                next_table = h3.find_next("table")
                if next_table:
                    table_content = []
                    rows = next_table.find_all("tr")
                    
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_content = []
                        for cell in cells:
                            cell_text = cell.get_text(" ", strip=True)
                            if cell_text:
                                row_content.append(cell_text)
                        
                        if row_content:
                            table_content.append(" | ".join(row_content))
                    
                    if table_content:
                        content_items.extend(table_content)
        
        # Extract all paragraphs with links (Also Read sections)
        all_links = wiki_content_reg_5.find_all("a")
        for link in all_links:
            link_text = link.get_text(" ", strip=True)
            link_href = link.get("href", "")
            if link_text and link_href:
                # Check if it's an "Also Read" link
                parent_p = link.find_parent("p")
                if parent_p and "Also Read" in parent_p.get_text():
                    content_items.append(f"Also Read: {link_text}: {link_href}")
        
        # Extract images with lazy loading handling
        photo_widgets = wiki_content_reg_5.find_all("div", class_="photo-widget-full")
        for photo_widget in photo_widgets:
            img_tag = photo_widget.find("img")
            if img_tag:
                # Handle lazy loading
                img_src = img_tag.get("src", "")
                if img_src and img_src.startswith('data:image'):
                    img_src = img_tag.get("data-src", img_tag.get("data-lazy-src", ""))
                
                if not img_src or img_src.startswith('data:'):
                    srcset = img_tag.get("srcset", "")
                    if srcset:
                        img_src = srcset.split(',')[0].strip().split(' ')[0]
                
                img_alt = img_tag.get("alt", "CAT Image")
                if img_src and not img_src.startswith('data:'):
                    # Find caption
                    caption_tag = photo_widget.find("p", class_="_img-caption")
                    caption = caption_tag.get_text(strip=True) if caption_tag else img_alt
                    
                    content_items.append(f"Image: {caption} - URL: {img_src}")
        
        # Extract PDF links table
        pdf_tables = wiki_content_reg_5.find_all("table")
        for pdf_table in pdf_tables:
            # Check if this table contains PDF links
            pdf_links = pdf_table.find_all("a", class_="smce-docs")
            if pdf_links:
                for pdf_link in pdf_links:
                    pdf_title = pdf_link.get("title", "")
                    pdf_href = pdf_link.get("href", "")
                    if pdf_title and pdf_href and pdf_href.endswith('.pdf'):
                        content_items.append(f"PDF: {pdf_title}: {pdf_href}")
        
        # Extract video embed
        video_div = wiki_content_reg_5.find("div", class_="vcmsEmbed")
        if video_div:
            iframe_tag = video_div.find("iframe")
            if iframe_tag:
                video_src = iframe_tag.get("src", "")
                
                # Handle lazy loading for video
                if video_src and not video_src.startswith('https://www.youtube.com'):
                    data_src = iframe_tag.get("data-src", "")
                    if "youtube.com" in data_src:
                        video_src = data_src
                
                if video_src and ("youtube.com" in video_src or "youtu.be" in video_src):
                    content_items.append(f"Video URL: {video_src}")
        
        if content_items:
            sections_data.append({
                "section_title": section_title,
                "content": content_items
            })

    # 5. FAQ section (for all structures)
    faq_wrappers = soup.find_all("div", class_="AnATaggedFaqWrapper")
    
    for faq_wrapper in faq_wrappers:
        # Commonly asked questions heading
        common_heading = faq_wrapper.find("h5")
        if common_heading and "Commonly asked" in common_heading.text:
            # Check if already exists
            if not any("Commonly Asked" in s["section_title"] for s in sections_data):
                sections_data.append({
                    "section_title": "Commonly Asked Questions",
                    "content": ["Frequently asked questions about CAT registration"]
                })
        
        # Different FAQ questions
        faq_items = faq_wrapper.find_all("div", class_="html-0 c5db62 listener")
        for faq in faq_items:
            question_elem = faq.find("strong", class_="flx-box")
            if question_elem:
                question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                
                # Check if question already exists
                if not any(question == s["section_title"] for s in sections_data):
                    # Find answer
                    answer_div = faq.find_next("div", class_="wikkiContents")
                    answer_text = ""
                    if answer_div:
                        paragraphs = answer_div.find_all("p")
                        if paragraphs:
                            answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                        else:
                            # If no p tag, get direct text
                            answer_div_content = answer_div.find("div")
                            if answer_div_content:
                                answer_text = answer_div_content.get_text(" ", strip=True)
                            else:
                                answer_text = answer_div.get_text(" ", strip=True)
                    
                    if question and answer_text:
                        # Remove "A:"
                        if answer_text.startswith("A:"):
                            answer_text = answer_text[2:].strip()
                        
                        sections_data.append({
                            "section_title": question,
                            "content": [answer_text]
                        })

    data["sections"] = sections_data
    # ==================== END SECTIONS PART ====================
    
    return data

def scrape_syllabus(driver, URLS):
    driver.get(URLS["syllabus"])
    
    # Better scrolling for lazy loading with more wait time for images
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Increased wait time for images to load
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE (for both structures)
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        # Check all possible title IDs
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META (for both structures)
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO (for both structures)
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        # Get intro from all possible wiki contents
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC (Table of Contents)
    toc_items = []
    
    # First from TOC wrapper
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # ==================== SECTIONS PART ====================
    sections_data = []
    
    # Find all sectionalWrapperClass divs
    sectional_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
    
    for wrapper in sectional_wrappers:
        # Extract section title from h2
        h2_title = wrapper.find("h2")
        if h2_title:
            section_title = h2_title.text.strip()
            
            # Find the corresponding wikkiContents div
            # Look for wikkiContents divs with IDs containing syllabus
            wiki_content_div = wrapper.find("div", id=lambda x: x and "wikkiContents" in x and "syllabus" in x)
            
            if wiki_content_div:
                content_items = []
                
                # Extract all paragraphs
                paragraphs = wiki_content_div.find_all("p")
                for p in paragraphs:
                    p_text = p.get_text(" ", strip=True)
                    if p_text:
                        # Check for "Also Read:" links within paragraphs
                        also_read_links = p.find_all("a")
                        if also_read_links and "Also Read" in p_text:
                            for link in also_read_links:
                                link_text = link.get_text(" ", strip=True)
                                link_href = link.get("href", "")
                                if link_text and link_href:
                                    content_items.append(f"Also Read: {link_text}: {link_href}")
                        else:
                            content_items.append(p_text)
                
                # Extract unordered list items
                ul_lists = wiki_content_div.find_all("ul")
                for ul in ul_lists:
                    for li_item in ul.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            # Check for "Also Read:" links within list items
                            also_read_links = li_item.find_all("a")
                            if also_read_links and "Also Read" in li_text:
                                for link in also_read_links:
                                    link_text = link.get_text(" ", strip=True)
                                    link_href = link.get("href", "")
                                    if link_text and link_href:
                                        content_items.append(f"Also Read: {link_text}: {link_href}")
                            else:
                                content_items.append(f"• {li_text}")
                
                # Extract tables
                tables = wiki_content_div.find_all("table")
                for table in tables:
                    table_content = []
                    rows = table.find_all("tr")
                    
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_content = []
                        for cell in cells:
                            cell_text = cell.get_text(" ", strip=True)
                            if cell_text:
                                row_content.append(cell_text)
                        
                        if row_content:
                            table_content.append(" | ".join(row_content))
                    
                    if table_content:
                        content_items.extend(table_content)
                
                # Extract images
                images = wiki_content_div.find_all("img")
                for img in images:
                    img_src = img.get("src", "")
                    img_alt = img.get("alt", "")
                    
                    # Handle lazy loading
                    if img_src and img_src.startswith('data:image'):
                        img_src = img.get("data-src", img.get("data-lazy-src", ""))
                    
                    if not img_src or img_src.startswith('data:'):
                        srcset = img.get("srcset", "")
                        if srcset:
                            img_src = srcset.split(',')[0].strip().split(' ')[0]
                    
                    if img_src and not img_src.startswith('data:'):
                        content_items.append(f"Image: {img_alt} - URL: {img_src}")
                
                # Extract videos
                video_divs = wiki_content_div.find_all("div", class_="vcmsEmbed")
                for video_div in video_divs:
                    iframe_tag = video_div.find("iframe")
                    if iframe_tag:
                        video_src = iframe_tag.get("src", "")
                        
                        # Handle lazy loading for video
                        if video_src and not video_src.startswith('https://www.youtube.com'):
                            data_src = iframe_tag.get("data-src", "")
                            if "youtube.com" in data_src:
                                video_src = data_src
                        
                        if video_src and ("youtube.com" in video_src or "youtu.be" in video_src):
                            content_items.append(f"Video URL: {video_src}")
                
                # Add section to sections_data if content exists
                if content_items:
                    sections_data.append({
                        "section_title": section_title,
                        "content": content_items
                    })
        
        # Extract FAQ section from AnATaggedFaqWrapper
        faq_wrapper = wrapper.find("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper:
            # Commonly asked questions heading
            common_heading = faq_wrapper.find("h5")
            if common_heading and "Commonly asked" in common_heading.text:
                # Check if already exists
                if not any("Commonly Asked" in s["section_title"] for s in sections_data):
                    sections_data.append({
                        "section_title": "Commonly Asked Questions",
                        "content": ["Frequently asked questions about CAT syllabus"]
                    })
            
            # Different FAQ questions
            faq_items = faq_wrapper.find_all("div", class_="html-0 c5db62 listener")
            for faq in faq_items:
                question_elem = faq.find("strong", class_="flx-box")
                if question_elem:
                    question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                    
                    # Check if question already exists
                    if not any(question == s["section_title"] for s in sections_data):
                        # Find answer
                        answer_div = faq.find_next("div", class_="wikkiContents")
                        answer_text = ""
                        if answer_div:
                            paragraphs = answer_div.find_all("p")
                            if paragraphs:
                                answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                            else:
                                answer_div_content = answer_div.find("div")
                                if answer_div_content:
                                    answer_text = answer_div_content.get_text(" ", strip=True)
                                else:
                                    answer_text = answer_div.get_text(" ", strip=True)
                        
                        if question and answer_text:
                            # Remove "A:"
                            if answer_text.startswith("A:"):
                                answer_text = answer_text[2:].strip()
                            
                            sections_data.append({
                                "section_title": question,
                                "content": [answer_text]
                            })
    
    # Also check for wikkiContents_syllabus__1 directly (in case it's not in sectionalWrapperClass)
    wiki_content_syllabus_1 = soup.find("div", {"id": "wikkiContents_syllabus__1"})
    if wiki_content_syllabus_1 and not any("wikkiContents_syllabus__1" in str(item) for item in sections_data):
        # Find the h2 title for this section
        h2_title_syllabus = soup.find("h2", id="content_toc_1023922")
        section_title = h2_title_syllabus.text.strip() if h2_title_syllabus else "CAT Syllabus 2025: Highlights"
        
        content_items = []
        
        # Extract all content similar to above
        paragraphs = wiki_content_syllabus_1.find_all("p")
        for p in paragraphs:
            p_text = p.get_text(" ", strip=True)
            if p_text:
                content_items.append(p_text)
        
        ul_lists = wiki_content_syllabus_1.find_all("ul")
        for ul in ul_lists:
            for li_item in ul.find_all("li"):
                li_text = li_item.get_text(" ", strip=True)
                if li_text:
                    content_items.append(f"• {li_text}")
        
        if content_items:
            # Check if this section already exists
            if not any(section_title == s["section_title"] for s in sections_data):
                sections_data.append({
                    "section_title": section_title,
                    "content": content_items
                })
    
    data["sections"] = sections_data
    # ==================== END SECTIONS PART ====================
    
    return data

def scrape_pattern(driver, URLS):
    driver.get(URLS["pattern"])
    
    # Better scrolling for lazy loading with more wait time for images
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    toc_items = []
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # ==================== SECTIONS PART ====================
    sections_data = []
    processed_sections = set()  # To avoid duplicate sections
    
    # Find all sectionalWrapperClass divs
    sectional_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
    
    for wrapper in sectional_wrappers:
        # Extract section title from h2
        h2_title = wrapper.find("h2")
        if h2_title:
            section_title = h2_title.text.strip()
            
            # Skip if already processed
            if section_title in processed_sections:
                continue
            processed_sections.add(section_title)
            
            # Find the corresponding wikkiContents div
            wiki_content_div = None
            # Try different patterns for wikkiContents IDs
            possible_ids = [
                lambda x: x and "wikkiContents" in x and "pattern" in x,
                lambda x: x and "wikkiContents" in x,
                lambda x: x and "__" in x
            ]
            
            for id_checker in possible_ids:
                wiki_content_div = wrapper.find("div", id=id_checker)
                if wiki_content_div:
                    break
            
            if not wiki_content_div:
                # Try to find any wikkiContents div in wrapper
                wiki_content_div = wrapper.find("div", class_="wikkiContents")
            
            if wiki_content_div:
                content_items = []
                processed_texts = set()  # To avoid duplicate content
                
                # Function to add content if not duplicate
                def add_content(text):
                    if text and text not in processed_texts:
                        processed_texts.add(text)
                        content_items.append(text)
                
                # Extract paragraphs
                paragraphs = wiki_content_div.find_all("p")
                for p in paragraphs:
                    p_text = p.get_text(" ", strip=True)
                    if p_text:
                        # Check for "Also Read:" links within paragraphs
                        if "Also Read:" in p_text:
                            also_read_links = p.find_all("a")
                            for link in also_read_links:
                                link_text = link.get_text(" ", strip=True)
                                link_href = link.get("href", "")
                                if link_text and link_href:
                                    add_content(f"Also Read: {link_text}: {link_href}")
                        else:
                            add_content(p_text)
                
                # Extract h3 headings and their following content
                h3_headings = wiki_content_div.find_all("h3")
                for h3 in h3_headings:
                    h3_text = h3.get_text(" ", strip=True)
                    if h3_text:
                        add_content(h3_text)
                    
                    # Get content after h3 until next heading
                    next_element = h3.find_next_sibling()
                    while next_element and next_element.name not in ['h2', 'h3', 'h4']:
                        if next_element.name == 'p':
                            p_text = next_element.get_text(" ", strip=True)
                            if p_text:
                                add_content(p_text)
                        elif next_element.name == 'ul':
                            for li_item in next_element.find_all("li"):
                                li_text = li_item.get_text(" ", strip=True)
                                if li_text:
                                    add_content(f"• {li_text}")
                        elif next_element.name == 'table':
                            # Handle table separately
                            pass
                        
                        next_element = next_element.find_next_sibling()
                
                # Extract unordered list items (excluding those inside tables)
                ul_lists = wiki_content_div.find_all("ul")
                for ul in ul_lists:
                    # Skip if ul is inside a table
                    if ul.find_parent("table"):
                        continue
                    
                    for li_item in ul.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            # Remove list-style-type:none items
                            if li_item.get("style") and "list-style-type: none" in li_item.get("style"):
                                continue
                            add_content(f"• {li_text}")
                
                # Extract ordered list items (excluding those inside tables)
                ol_lists = wiki_content_div.find_all("ol")
                for ol in ol_lists:
                    # Skip if ol is inside a table
                    if ol.find_parent("table"):
                        continue
                    
                    for li_item in ol.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            add_content(f"• {li_text}")
                
                # Extract tables - PROPER FORMAT
                tables = wiki_content_div.find_all("table")
                for table in tables:
                    table_content = []
                    rows = table.find_all("tr")
                    
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_content = []
                        
                        for cell in cells:
                            # Get text from cell (excluding nested lists for now)
                            cell_text = cell.get_text(" ", strip=True)
                            
                            # Clean up the text
                            if cell_text:
                                # Remove extra whitespace
                                cell_text = ' '.join(cell_text.split())
                                row_content.append(cell_text)
                        
                        if row_content:
                            # Join with pipe for table format
                            table_content.append(" | ".join(row_content))
                    
                    if table_content:
                        # Add table content as separate items
                        for row in table_content:
                            add_content(row)
                
                # Extract images (excluding those inside tables)
                images = wiki_content_div.find_all("img")
                for img in images:
                    # Skip if img is inside a table
                    if img.find_parent("table"):
                        continue
                    
                    img_src = img.get("src", "")
                    img_alt = img.get("alt", "")
                    
                    # Handle lazy loading
                    if img_src and img_src.startswith('data:image'):
                        img_src = img.get("data-src", img.get("data-lazy-src", ""))
                    
                    if not img_src or img_src.startswith('data:'):
                        srcset = img.get("srcset", "")
                        if srcset:
                            img_src = srcset.split(',')[0].strip().split(' ')[0]
                    
                    if img_src and not img_src.startswith('data:'):
                        add_content(f"Image: {img_alt} - URL: {img_src}")
                
                # Extract videos
                video_divs = wiki_content_div.find_all("div", class_="vcmsEmbed")
                for video_div in video_divs:
                    iframe_tag = video_div.find("iframe")
                    if iframe_tag:
                        video_src = iframe_tag.get("src", "")
                        
                        # Handle lazy loading for video
                        if video_src and not video_src.startswith('https://www.youtube.com'):
                            data_src = iframe_tag.get("data-src", "")
                            if "youtube.com" in data_src:
                                video_src = data_src
                        
                        if video_src and ("youtube.com" in video_src or "youtu.be" in video_src):
                            add_content(f"Video URL: {video_src}")
                
                # Add section to sections_data if content exists
                if content_items:
                    sections_data.append({
                        "section_title": section_title,
                        "content": content_items
                    })
        
        # Extract FAQ section from AnATaggedFaqWrapper
        faq_wrapper = wrapper.find("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper:
            # Commonly asked questions heading
            common_heading = faq_wrapper.find("h5")
            if common_heading and "Commonly asked" in common_heading.text:
                if "Commonly Asked Questions" not in processed_sections:
                    processed_sections.add("Commonly Asked Questions")
                    sections_data.append({
                        "section_title": "Commonly Asked Questions",
                        "content": ["Frequently asked questions about CAT pattern"]
                    })
            
            # Different FAQ questions
            faq_items = faq_wrapper.find_all("div", class_="html-0 c5db62 listener")
            for faq in faq_items:
                question_elem = faq.find("strong", class_="flx-box")
                if question_elem:
                    question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                    
                    if question not in processed_sections:
                        processed_sections.add(question)
                        # Find answer
                        answer_div = faq.find_next("div", class_="wikkiContents")
                        answer_text = ""
                        if answer_div:
                            paragraphs = answer_div.find_all("p")
                            if paragraphs:
                                answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                            else:
                                answer_div_content = answer_div.find("div")
                                if answer_div_content:
                                    answer_text = answer_div_content.get_text(" ", strip=True)
                                else:
                                    answer_text = answer_div.get_text(" ", strip=True)
                        
                        if question and answer_text:
                            # Remove "A:"
                            if answer_text.startswith("A:"):
                                answer_text = answer_text[2:].strip()
                            
                            sections_data.append({
                                "section_title": question,
                                "content": [answer_text]
                            })
    
    # Also check for specific wikkiContents_pattern__1
    wiki_content_pattern_1 = soup.find("div", {"id": "wikkiContents_pattern__1"})
    if wiki_content_pattern_1 and "What is CAT Exam Pattern 2025?" not in processed_sections:
        h2_title_pattern = soup.find("h2", id="content_toc_1022814")
        section_title = h2_title_pattern.text.strip() if h2_title_pattern else "What is CAT Exam Pattern 2025?"
        
        if section_title not in processed_sections:
            processed_sections.add(section_title)
            content_items = []
            processed_texts = set()
            
            def add_content_specific(text):
                if text and text not in processed_texts:
                    processed_texts.add(text)
                    content_items.append(text)
            
            # Extract in proper order
            elements = wiki_content_pattern_1.find_all(["p", "ul", "ol", "h3", "table"])
            for elem in elements:
                if elem.name == 'p':
                    p_text = elem.get_text(" ", strip=True)
                    if p_text:
                        add_content_specific(p_text)
                elif elem.name == 'h3':
                    h3_text = elem.get_text(" ", strip=True)
                    if h3_text:
                        add_content_specific(h3_text)
                elif elem.name == 'ul':
                    for li_item in elem.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            add_content_specific(f"• {li_text}")
                elif elem.name == 'ol':
                    for li_item in elem.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            add_content_specific(f"• {li_text}")
                elif elem.name == 'table':
                    table_content = []
                    rows = elem.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_content = []
                        for cell in cells:
                            cell_text = cell.get_text(" ", strip=True)
                            if cell_text:
                                row_content.append(cell_text)
                        if row_content:
                            table_content.append(" | ".join(row_content))
                    
                    if table_content:
                        for row in table_content:
                            add_content_specific(row)
            
            if content_items:
                sections_data.append({
                    "section_title": section_title,
                    "content": content_items
                })
    
    data["sections"] = sections_data
    return data

def scrape_preparation(driver, URLS):
    driver.get(URLS["preparation"])
    
    # Better scrolling for lazy loading with more wait time for images
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    toc_items = []
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # ==================== SECTIONS PART ====================
    sections_data = []
    processed_sections = set()
    
    # Find all sectionalWrapperClass divs
    sectional_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
    
    for wrapper in sectional_wrappers:
        # Extract section title from h2
        h2_title = wrapper.find("h2")
        if h2_title:
            section_title = h2_title.text.strip()
            
            # Skip if already processed
            if section_title in processed_sections:
                continue
            processed_sections.add(section_title)
            
            # Find the corresponding wikkiContents div
            wiki_content_div = wrapper.find("div", id=lambda x: x and "wikkiContents" in x and "preparation" in x)
            
            if not wiki_content_div:
                wiki_content_div = wrapper.find("div", class_="wikkiContents")
            
            if wiki_content_div:
                content_items = []
                processed_texts = set()
                
                # Function to add content if not duplicate
                def add_content(text):
                    if text and text not in processed_texts:
                        # Clean the text
                        text = ' '.join(text.split())  # Remove extra whitespace
                        processed_texts.add(text)
                        content_items.append(text)
                
                # Extract paragraphs
                paragraphs = wiki_content_div.find_all("p")
                for p in paragraphs:
                    p_text = p.get_text(" ", strip=True)
                    if p_text:
                        # Clean paragraph text
                        p_text = ' '.join(p_text.split())
                        add_content(p_text)
                
                # Extract unordered list items
                ul_lists = wiki_content_div.find_all("ul")
                for ul in ul_lists:
                    # Skip if ul is inside a table or has special styling
                    if ul.find_parent("table") or (ul.get("style") and "list-style-type: none" in ul.get("style")):
                        continue
                    
                    for li_item in ul.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            # Clean and add bullet point
                            li_text = ' '.join(li_text.split())
                            add_content(f"• {li_text}")
                
                # Extract ordered list items
                ol_lists = wiki_content_div.find_all("ol")
                for ol in ol_lists:
                    if ol.find_parent("table"):
                        continue
                    
                    for li_item in ol.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            li_text = ' '.join(li_text.split())
                            add_content(f"• {li_text}")
                
                # Extract images
                images = wiki_content_div.find_all("img")
                for img in images:
                    if img.find_parent("table"):
                        continue
                    
                    img_src = img.get("src", "")
                    img_alt = img.get("alt", "")
                    
                    # Handle lazy loading
                    if img_src and img_src.startswith('data:image'):
                        img_src = img.get("data-src", img.get("data-lazy-src", ""))
                    
                    if not img_src or img_src.startswith('data:'):
                        srcset = img.get("srcset", "")
                        if srcset:
                            img_src = srcset.split(',')[0].strip().split(' ')[0]
                    
                    if img_src and not img_src.startswith('data:'):
                        add_content(f"Image: {img_alt} - URL: {img_src}")
                
                # Extract videos
                video_divs = wiki_content_div.find_all("div", class_="vcmsEmbed")
                for video_div in video_divs:
                    iframe_tag = video_div.find("iframe")
                    if iframe_tag:
                        video_src = iframe_tag.get("src", "")
                        
                        if video_src and not video_src.startswith('https://www.youtube.com'):
                            data_src = iframe_tag.get("data-src", "")
                            if "youtube.com" in data_src:
                                video_src = data_src
                        
                        if video_src and ("youtube.com" in video_src or "youtu.be" in video_src):
                            add_content(f"Video URL: {video_src}")
                
                # Extract tables
                tables = wiki_content_div.find_all("table")
                for table in tables:
                    table_content = []
                    rows = table.find_all("tr")
                    
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_content = []
                        
                        for cell in cells:
                            cell_text = cell.get_text(" ", strip=True)
                            if cell_text:
                                cell_text = ' '.join(cell_text.split())
                                row_content.append(cell_text)
                        
                        if row_content:
                            table_content.append(" | ".join(row_content))
                    
                    if table_content:
                        for row in table_content:
                            add_content(row)
                
                # Add section to sections_data if content exists
                if content_items:
                    sections_data.append({
                        "section_title": section_title,
                        "content": content_items
                    })
        
        # Extract FAQ section from AnATaggedFaqWrapper
        faq_wrapper = wrapper.find("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper:
            # Commonly asked questions heading
            common_heading = faq_wrapper.find("h5")
            if common_heading and "Commonly asked" in common_heading.text:
                if "Commonly Asked Questions" not in processed_sections:
                    processed_sections.add("Commonly Asked Questions")
                    sections_data.append({
                        "section_title": "Commonly Asked Questions",
                        "content": ["Frequently asked questions about CAT preparation"]
                    })
            
            # Different FAQ questions
            faq_items = faq_wrapper.find_all("div", class_="html-0 c5db62 listener")
            for faq in faq_items:
                question_elem = faq.find("strong", class_="flx-box")
                if question_elem:
                    question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                    
                    if question not in processed_sections:
                        processed_sections.add(question)
                        # Find answer
                        answer_div = faq.find_next("div", class_="wikkiContents")
                        answer_text = ""
                        if answer_div:
                            paragraphs = answer_div.find_all("p")
                            if paragraphs:
                                answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                            else:
                                answer_div_content = answer_div.find("div")
                                if answer_div_content:
                                    answer_text = answer_div_content.get_text(" ", strip=True)
                                else:
                                    answer_text = answer_div.get_text(" ", strip=True)
                        
                        if question and answer_text:
                            # Remove "A:"
                            if answer_text.startswith("A:"):
                                answer_text = answer_text[2:].strip()
                            
                            # Clean answer text
                            answer_text = ' '.join(answer_text.split())
                            sections_data.append({
                                "section_title": question,
                                "content": [answer_text]
                            })
    
    # Also check for specific wikkiContents_preparation__1
    wiki_content_preparation_1 = soup.find("div", {"id": "wikkiContents_preparation__1"})
    if wiki_content_preparation_1 and "CAT Preparation Strategy 2025" not in processed_sections:
        h2_title_preparation = soup.find("h2", id="content_toc_1087128")
        section_title = h2_title_preparation.text.strip() if h2_title_preparation else "CAT Preparation Strategy 2025"
        
        if section_title not in processed_sections:
            processed_sections.add(section_title)
            content_items = []
            processed_texts = set()
            
            def add_content_specific(text):
                if text and text not in processed_texts:
                    text = ' '.join(text.split())
                    processed_texts.add(text)
                    content_items.append(text)
            
            # Extract main content
            main_div = wiki_content_preparation_1.find("div")
            if main_div:
                # Extract paragraphs
                paragraphs = main_div.find_all("p")
                for p in paragraphs:
                    p_text = p.get_text(" ", strip=True)
                    if p_text:
                        add_content_specific(p_text)
                
                # Extract unordered list items
                ul_lists = main_div.find_all("ul")
                for ul in ul_lists:
                    # Skip nested ul with list-style-type: none
                    parent_li = ul.find_parent("li")
                    if parent_li and parent_li.get("style") and "list-style-type: none" in parent_li.get("style"):
                        continue
                    
                    for li_item in ul.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            # Check if this li contains nested lists
                            nested_ul = li_item.find("ul")
                            nested_ol = li_item.find("ol")
                            if not nested_ul and not nested_ol:
                                add_content_specific(f"• {li_text}")
                
                # Extract images
                images = main_div.find_all("img")
                for img in images:
                    img_src = img.get("src", "")
                    img_alt = img.get("alt", "")
                    
                    if img_src and img_src.startswith('data:image'):
                        img_src = img.get("data-src", img.get("data-lazy-src", ""))
                    
                    if not img_src or img_src.startswith('data:'):
                        srcset = img.get("srcset", "")
                        if srcset:
                            img_src = srcset.split(',')[0].strip().split(' ')[0]
                    
                    if img_src and not img_src.startswith('data:'):
                        add_content_specific(f"Image: {img_alt} - URL: {img_src}")
            
            if content_items:
                sections_data.append({
                    "section_title": section_title,
                    "content": content_items
                })
    
    data["sections"] = sections_data
    return data

def scrape_books(driver, URLS):
    driver.get(URLS["books"])
    
    # Better scrolling for lazy loading with more wait time for images
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    toc_items = []
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # ==================== SECTIONS PART ====================
    sections_data = []
    processed_sections = set()
    
    # Find all sectionalWrapperClass divs
    sectional_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
    
    for wrapper in sectional_wrappers:
        # Extract section title from h2
        h2_title = wrapper.find("h2")
        if h2_title:
            section_title = h2_title.text.strip()
            
            # Skip if already processed
            if section_title in processed_sections:
                continue
            processed_sections.add(section_title)
            
            # Find the corresponding wikkiContents div
            wiki_content_div = wrapper.find("div", id=lambda x: x and "wikkiContents" in x and "books" in x)
            
            if not wiki_content_div:
                wiki_content_div = wrapper.find("div", class_="wikkiContents")
            
            if wiki_content_div:
                content_items = []
                processed_texts = set()
                
                # Function to add content if not duplicate
                def add_content(text):
                    if text and text not in processed_texts:
                        # Clean the text
                        text = ' '.join(text.split())  # Remove extra whitespace
                        processed_texts.add(text)
                        content_items.append(text)
                
                # Extract paragraphs (including those with links)
                paragraphs = wiki_content_div.find_all("p")
                for p in paragraphs:
                    p_text = p.get_text(" ", strip=True)
                    if p_text:
                        # Check for "Also Read:" in paragraph
                        if "Also Read:" in p_text:
                            # Extract links from "Also Read:" section
                            also_read_links = p.find_all("a")
                            for link in also_read_links:
                                link_text = link.get_text(" ", strip=True)
                                link_href = link.get("href", "")
                                if link_text and link_href:
                                    add_content(f"Also Read: {link_text}: {link_href}")
                        else:
                            # Regular paragraph
                            p_text = ' '.join(p_text.split())
                            add_content(p_text)
                
                # Extract h3 headings
                h3_headings = wiki_content_div.find_all("h3")
                for h3 in h3_headings:
                    h3_text = h3.get_text(" ", strip=True)
                    if h3_text:
                        h3_text = ' '.join(h3_text.split())
                        add_content(h3_text)
                
                # Extract unordered list items
                ul_lists = wiki_content_div.find_all("ul")
                for ul in ul_lists:
                    # Skip if ul is inside a table or has special styling
                    if ul.find_parent("table"):
                        continue
                    
                    for li_item in ul.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            # Clean and add bullet point
                            li_text = ' '.join(li_text.split())
                            add_content(f"• {li_text}")
                
                # Extract ordered list items
                ol_lists = wiki_content_div.find_all("ol")
                for ol in ol_lists:
                    if ol.find_parent("table"):
                        continue
                    
                    for li_item in ol.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            li_text = ' '.join(li_text.split())
                            add_content(f"• {li_text}")
                
                # Extract images
                images = wiki_content_div.find_all("img")
                for img in images:
                    if img.find_parent("table"):
                        continue
                    
                    img_src = img.get("src", "")
                    img_alt = img.get("alt", "")
                    
                    # Handle lazy loading
                    if img_src and img_src.startswith('data:image'):
                        img_src = img.get("data-src", img.get("data-lazy-src", ""))
                    
                    if not img_src or img_src.startswith('data:'):
                        srcset = img.get("srcset", "")
                        if srcset:
                            img_src = srcset.split(',')[0].strip().split(' ')[0]
                    
                    if img_src and not img_src.startswith('data:'):
                        add_content(f"Image: {img_alt} - URL: {img_src}")
                
                # Extract videos
                video_divs = wiki_content_div.find_all("div", class_="vcmsEmbed")
                for video_div in video_divs:
                    iframe_tag = video_div.find("iframe")
                    if iframe_tag:
                        video_src = iframe_tag.get("src", "")
                        
                        if video_src and not video_src.startswith('https://www.youtube.com'):
                            data_src = iframe_tag.get("data-src", "")
                            if "youtube.com" in data_src:
                                video_src = data_src
                        
                        if video_src and ("youtube.com" in video_src or "youtu.be" in video_src):
                            add_content(f"Video URL: {video_src}")
                
                # Extract tables
                tables = wiki_content_div.find_all("table")
                for table in tables:
                    table_content = []
                    rows = table.find_all("tr")
                    
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        row_content = []
                        
                        for cell in cells:
                            cell_text = cell.get_text(" ", strip=True)
                            if cell_text:
                                cell_text = ' '.join(cell_text.split())
                                row_content.append(cell_text)
                        
                        if row_content:
                            table_content.append(" | ".join(row_content))
                    
                    if table_content:
                        for row in table_content:
                            add_content(row)
                
                # Add section to sections_data if content exists
                if content_items:
                    sections_data.append({
                        "section_title": section_title,
                        "content": content_items
                    })
        
        # Extract FAQ section from AnATaggedFaqWrapper
        faq_wrapper = wrapper.find("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper:
            # Commonly asked questions heading
            common_heading = faq_wrapper.find("h5")
            if common_heading and "Commonly asked" in common_heading.text:
                if "Commonly Asked Questions" not in processed_sections:
                    processed_sections.add("Commonly Asked Questions")
                    sections_data.append({
                        "section_title": "Commonly Asked Questions",
                        "content": ["Frequently asked questions about CAT books"]
                    })
            
            # Different FAQ questions
            faq_items = faq_wrapper.find_all("div", class_="html-0 c5db62 listener")
            for faq in faq_items:
                question_elem = faq.find("strong", class_="flx-box")
                if question_elem:
                    question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                    
                    if question not in processed_sections:
                        processed_sections.add(question)
                        # Find answer
                        answer_div = faq.find_next("div", class_="wikkiContents")
                        answer_text = ""
                        if answer_div:
                            paragraphs = answer_div.find_all("p")
                            if paragraphs:
                                answer_text = " ".join([p.get_text(" ", strip=True) for p in paragraphs])
                            else:
                                answer_div_content = answer_div.find("div")
                                if answer_div_content:
                                    answer_text = answer_div_content.get_text(" ", strip=True)
                                else:
                                    answer_text = answer_div.get_text(" ", strip=True)
                        
                        if question and answer_text:
                            # Remove "A:"
                            if answer_text.startswith("A:"):
                                answer_text = answer_text[2:].strip()
                            
                            # Clean answer text
                            answer_text = ' '.join(answer_text.split())
                            sections_data.append({
                                "section_title": question,
                                "content": [answer_text]
                            })
    
    # Also check for specific wikkiContents_books__1
    wiki_content_books_1 = soup.find("div", {"id": "wikkiContents_books__1"})
    if wiki_content_books_1 and "Best Books for CAT Preparation 2025" not in processed_sections:
        h2_title_books = soup.find("h2", id="content_toc_827218")
        section_title = h2_title_books.text.strip() if h2_title_books else "Best Books for CAT Preparation 2025"
        
        if section_title not in processed_sections:
            processed_sections.add(section_title)
            content_items = []
            processed_texts = set()
            
            def add_content_specific(text):
                if text and text not in processed_texts:
                    text = ' '.join(text.split())
                    processed_texts.add(text)
                    content_items.append(text)
            
            # Extract main content
            main_div = wiki_content_books_1.find("div")
            if main_div:
                # Extract paragraphs
                paragraphs = main_div.find_all("p")
                for p in paragraphs:
                    p_text = p.get_text(" ", strip=True)
                    if p_text:
                        # Handle "Also Read:" paragraphs specially
                        if "Also Read:" in p_text:
                            # Extract individual links
                            links = p.find_all("a")
                            for link in links:
                                link_text = link.get_text(" ", strip=True)
                                link_href = link.get("href", "")
                                if link_text and link_href:
                                    add_content_specific(f"Also Read: {link_text}: {link_href}")
                        else:
                            add_content_specific(p_text)
                
                # Extract h3 headings
                h3_headings = main_div.find_all("h3")
                for h3 in h3_headings:
                    h3_text = h3.get_text(" ", strip=True)
                    if h3_text:
                        add_content_specific(h3_text)
                
                # Extract unordered list items
                ul_lists = main_div.find_all("ul")
                for ul in ul_lists:
                    for li_item in ul.find_all("li"):
                        li_text = li_item.get_text(" ", strip=True)
                        if li_text:
                            add_content_specific(f"• {li_text}")
            
            if content_items:
                sections_data.append({
                    "section_title": section_title,
                    "content": content_items
                })
    
    data["sections"] = sections_data
    return data

def scrape_notification(driver, URLS):
    driver.get(URLS["notification"])
    
    # Better scrolling for lazy loading with more wait time for images
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break
    
    # Add images to intro
    photo_widgets = soup.find_all("div", class_="photo-widget-full")
    
    for widget in photo_widgets:
        # Check for images
        img_tag = widget.find("img", class_="lazy")
        if img_tag:
            data["intro"].append({"image_src": img_tag.get("src", "")})
        
        # Check for YouTube videos
        iframe_tag = widget.find("iframe")
        if iframe_tag and "youtube.com" in iframe_tag.get("src", ""):
            data["intro"].append({"youtube_url": iframe_tag.get("src", "")})

    # LIVE BLOG
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    toc_items = []
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # SECTIONS - सभी sectionalWrapperClass सेक्शन्स स्क्रैप करें
    all_sections = soup.find_all("div", class_="sectionalWrapperClass")
    
    for section in all_sections:
        section_data = {}
        
        # Heading निकालें
        h2_tag = section.find("h2")
        if h2_tag:
            section_data["heading"] = h2_tag.text.strip()
        
        # Paragraphs निकालें
        paragraphs = []
        for p_tag in section.find_all("p"):
            p_text = p_tag.text.strip()
            if p_text:
                paragraphs.append(p_text)
        if paragraphs:
            section_data["paragraphs"] = paragraphs
        
        # Images निकालें
        images = []
        for img_tag in section.find_all("img"):
            img_data = {
                "src": img_tag.get("src", ""),
            }
            images.append(img_data)
        if images:
            section_data["images"] = images
        
        # YouTube videos निकालें
        youtube_videos = []
        for iframe_tag in section.find_all("iframe"):
            if "youtube.com" in iframe_tag.get("src", ""):
                youtube_videos.append({
                    "url": iframe_tag.get("src", ""),
                })
        if youtube_videos:
            section_data["youtube_videos"] = youtube_videos
        
        # Tables निकालें
        tables = []
        for table_tag in section.find_all("table"):
            table_data = []
            # Table rows निकालें
            for row in table_tag.find_all("tr"):
                row_data = []
                for cell in row.find_all(["td", "th"]):
                    row_data.append(cell.text.strip())
                if row_data:
                    table_data.append(row_data)
            if table_data:
                section_data["tables"] = table_data
        
        # अगर section में कुछ डेटा है तो sections list में add करें
        if section_data:
            data["sections"].append(section_data)
    
    return data

def scrape_center(driver, URLS):
    driver.get(URLS["center"])
    
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break
    
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    toc_items = []
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # SPECIFIC SECTION DATA (What is CAT exam centre?)
    section_div = soup.find("div", id="wikkiContents_centre__1")
    
    if section_div:
        section_data = {}
        
        # HEADING
        heading_tag = soup.find("h2", id="content_toc_1071594")
        if heading_tag:
            section_data["heading"] = heading_tag.text.strip()
        
        # PARAGRAPHS (table के cells को exclude करें)
        paragraphs = []
        for p_tag in section_div.find_all("p"):
            # Check if this p tag is inside a table
            if p_tag.find_parent("table"):
                continue  # Skip table content
            
            p_text = p_tag.get_text(" ", strip=True)
            if p_text:
                links = []
                for link in p_tag.find_all("a"):
                    links.append({
                        "text": link.text.strip(),
                        "href": link.get("href", "")
                    })
                paragraphs.append({
                    "text": p_text,
                    "links": links if links else []
                })
        
        if paragraphs:
            section_data["paragraphs"] = paragraphs
        
        if section_data:
            data["sections"].append(section_data)
    
    # ALL OTHER SECTIONS DATA SCRAPING - NO DUPLICATES
    all_section_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
    
    # Track headings to avoid duplicates
    seen_headings = set()
    
    for wrapper in all_section_wrappers:
        section_data = {}
        
        # HEADING
        h2_tag = wrapper.find("h2")
        if h2_tag:
            heading_text = h2_tag.text.strip()
            
            # Skip if heading already processed (avoid duplicates)
            if heading_text in seen_headings:
                continue
                
            seen_headings.add(heading_text)
            section_data["heading"] = heading_text
        
        # FIND WIKKI CONTENT
        wikki_div = None
        for div in wrapper.find_all("div", class_="wikkiContents"):
            div_id = div.get("id", "")
            if div_id.startswith("wikkiContents_"):
                wikki_div = div
                break
        
        if wikki_div:
            # PARAGRAPHS - table content को exclude करें
            paragraphs = []
            seen_paragraphs = set()
            for p_tag in wikki_div.find_all("p"):
                # Skip if this paragraph is inside a table
                if p_tag.find_parent("table"):
                    continue
                
                p_text = p_tag.get_text(" ", strip=True)
                if p_text and p_text not in seen_paragraphs and len(p_text) > 20:
                    seen_paragraphs.add(p_text)
                    links = []
                    for link in p_tag.find_all("a"):
                        links.append({
                            "text": link.text.strip(),
                            "href": link.get("href", "")
                        })
                    paragraphs.append({
                        "text": p_text,
                        "links": links if links else []
                    })
            
            if paragraphs:
                section_data["paragraphs"] = paragraphs
            
            # LISTS (ul/ol) - table content को exclude करें
            lists = []
            seen_lists = set()
            for list_tag in wikki_div.find_all(["ul", "ol"]):
                # Skip if this list is inside a table
                if list_tag.find_parent("table"):
                    continue
                
                list_items = []
                for li_tag in list_tag.find_all("li"):
                    item_text = li_tag.text.strip()
                    if item_text:
                        list_items.append(item_text)
                
                if list_items:
                    list_str = "|".join(list_items)
                    if list_str not in seen_lists:
                        seen_lists.add(list_str)
                        list_type = "unordered" if list_tag.name == "ul" else "ordered"
                        lists.append({
                            "type": list_type,
                            "items": list_items
                        })
            
            if lists:
                section_data["lists"] = lists
            
            # TABLES - सिर्फ tables का data
            tables = []
            for table_tag in wrapper.find_all("table"):
                table_data = []
                # Extract all rows
                for row in table_tag.find_all("tr"):
                    row_data = []
                    # Extract all cells (td/th)
                    for cell in row.find_all(["td", "th"]):
                        cell_text = cell.get_text(" ", strip=True)
                        if cell_text:
                            row_data.append(cell_text)
                    
                    if row_data:  # Only add non-empty rows
                        table_data.append(row_data)
                
                if table_data:  # Only add non-empty tables
                    # Check if this table already exists (avoid duplicates)
                    table_str = "|".join(["|".join(row) for row in table_data])
                    if not any(t["table_str"] == table_str for t in tables if "table_str" in t):
                        tables.append({
                            "table_data": table_data,
                            "table_str": table_str  # For duplicate checking
                        })
            
            if tables:
                section_data["tables"] = [t["table_data"] for t in tables]
            
            # YOUTUBE VIDEOS
            youtube_videos = []
            seen_videos = set()
            for iframe in wikki_div.find_all("iframe"):
                video_url = iframe.get("src", "")
                if "youtube.com" in video_url and video_url not in seen_videos:
                    seen_videos.add(video_url)
                    youtube_videos.append({
                        "url": video_url
                    })
            
            if youtube_videos:
                section_data["youtube_videos"] = youtube_videos
        
        # FAQS SECTION
        faq_wrapper = wrapper.find("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper:
            faqs = []
            seen_questions = set()
            faq_items = faq_wrapper.find_all("div", id=lambda x: x and "::" in x)
            
            for faq_item in faq_items:
                question_div = faq_item
                answer_div = faq_item.find_next_sibling("div", class_="_16f53f")
                
                if question_div and answer_div:
                    question = question_div.get_text(" ", strip=True)
                    answer = answer_div.get_text(" ", strip=True)
                    
                    # Clean question text
                    question = question.replace("Q:", "").replace("Q :", "").strip()
                    
                    if question and answer and question not in seen_questions:
                        seen_questions.add(question)
                        faqs.append({
                            "question": question,
                            "answer": answer[:500] + "..." if len(answer) > 500 else answer
                        })
            
            if faqs:
                section_data["faqs"] = faqs
        
        # Add section data if it has content
        if section_data and "heading" in section_data:
            data["sections"].append(section_data)
    
    return data

def scrape_news(driver, URLS):
    driver.get(URLS["news"])
    
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "live_blog": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()

    # META
    updated = soup.select_one(".updatedOn span")
    author = soup.select_one(".ePPDetail a")
    
    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author_name": author.get_text(strip=True) if author else "",
        "author_profile": author.get("href", "") if author else ""
    }

    # INTRO
    intro_div = soup.select_one(".intro-sec")
    if intro_div:
        for p in intro_div.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if txt:
                data["intro"].append(txt)
    else:
        wiki_ids = [
            "wikkiContents_mocktest__1",
            "wikkiContents_mocktest__3", 
            "wikkiContents_registration__1",
            "wikkiContents_registration__3"
        ]
        
        for wiki_id in wiki_ids:
            wiki_content = soup.find("div", {"id": wiki_id})
            if wiki_content:
                first_p = wiki_content.find("p")
                if first_p:
                    intro_text = first_p.get_text(" ", strip=True)
                    if intro_text and intro_text not in data["intro"]:
                        data["intro"].append(intro_text)
                        break
    
    for blog in soup.select(".date_liveblog_list div"):
        txt = blog.get_text(" ", strip=True)
        if txt:
            data["live_blog"].append(txt)

    # TOC
    toc_items = []
    for li in soup.select("#tocWrapper li"):
        title_txt = li.get_text(strip=True)
        if title_txt:
            toc_items.append(title_txt)
    
    data["toc"] = toc_items
    
    # ALL SECTIONS DATA SCRAPING
    all_section_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
    
    # Track headings to avoid duplicates
    seen_headings = set()
    
    for wrapper in all_section_wrappers:
        section_data = {}
        
        # HEADING
        h2_tag = wrapper.find("h2")
        if h2_tag:
            heading_text = h2_tag.text.strip()
            
            # Skip if heading already processed (avoid duplicates)
            if heading_text in seen_headings:
                continue
                
            seen_headings.add(heading_text)
            section_data["heading"] = heading_text
            section_data["heading_id"] = h2_tag.get("id", "")
        
        # FIND WIKKI CONTENT
        wikki_div = None
        for div in wrapper.find_all("div", class_="wikkiContents"):
            div_id = div.get("id", "")
            if div_id.startswith("wikkiContents_"):
                wikki_div = div
                break
        
        if wikki_div:
            # PARAGRAPHS - table content को exclude करें
            paragraphs = []
            seen_paragraphs = set()
            for p_tag in wikki_div.find_all("p"):
                # Skip if this paragraph is inside a table or list
                if p_tag.find_parent("table") or p_tag.find_parent(["ul", "ol"]):
                    continue
                
                p_text = p_tag.get_text(" ", strip=True)
                if p_text and p_text not in seen_paragraphs and len(p_text) > 10:
                    seen_paragraphs.add(p_text)
                    links = []
                    for link in p_tag.find_all("a"):
                        links.append({
                            "text": link.text.strip(),
                            "href": link.get("href", "")
                        })
                    paragraphs.append({
                        "text": p_text,
                        "links": links if links else []
                    })
            
            if paragraphs:
                section_data["paragraphs"] = paragraphs
            
            # LISTS (ul/ol) - table content को exclude करें
            lists = []
            seen_lists = set()
            
            # Process lists with their headings
            for list_tag in wikki_div.find_all(["ul", "ol"]):
                # Skip if this list is inside a table
                if list_tag.find_parent("table"):
                    continue
                
                # Create a unique identifier for this list
                list_items = []
                for li_tag in list_tag.find_all("li"):
                    item_text = li_tag.text.strip()
                    if item_text:
                        # Extract links from list items
                        item_links = []
                        for link in li_tag.find_all("a"):
                            item_links.append({
                                "text": link.text.strip(),
                                "href": link.get("href", "")
                            })
                        
                        list_items.append({
                            "text": item_text,
                            "links": item_links if item_links else []
                        })
                
                if list_items:
                    list_str = "|".join([item["text"] for item in list_items])
                    if list_str not in seen_lists:
                        seen_lists.add(list_str)
                        list_type = "unordered" if list_tag.name == "ul" else "ordered"
                        
                        # Try to find a heading for this list
                        list_heading = ""
                        # Check previous sibling for heading
                        prev_elem = list_tag.find_previous(['p', 'strong', 'h3', 'h4'])
                        if prev_elem and prev_elem.text.strip():
                            list_heading = prev_elem.text.strip()
                        
                        lists.append({
                            "heading": list_heading if list_heading else f"{list_type.capitalize()} List",
                            "type": list_type,
                            "items": list_items
                        })
            
            if lists:
                section_data["lists"] = lists
            
            # IMPORTANT POINTS (strong tags) - lists के headings को exclude करें
            important_points = []
            for strong_tag in wikki_div.find_all("strong"):
                strong_text = strong_tag.text.strip()
                # Skip if this strong tag is a list heading
                is_list_heading = False
                for lst in lists:
                    if lst["heading"] == strong_text:
                        is_list_heading = True
                        break
                
                if strong_text and strong_text not in important_points and not is_list_heading:
                    important_points.append(strong_text)
            
            if important_points:
                section_data["important_points"] = important_points
            
            # YOUTUBE VIDEOS
            youtube_videos = []
            seen_videos = set()
            for iframe in wikki_div.find_all("iframe"):
                video_url = iframe.get("src", "")
                if "youtube.com" in video_url and video_url not in seen_videos:
                    seen_videos.add(video_url)
                    youtube_videos.append({
                        "url": video_url
                    })
            
            if youtube_videos:
                section_data["youtube_videos"] = youtube_videos
        
        # TABLES - सिर्फ tables का data
        tables = []
        for table_tag in wrapper.find_all("table"):
            table_data = []
            # Extract all rows
            for row in table_tag.find_all("tr"):
                row_data = []
                # Extract all cells (td/th)
                for cell in row.find_all(["td", "th"]):
                    cell_text = cell.get_text(" ", strip=True)
                    if cell_text:
                        row_data.append(cell_text)
                
                if row_data:  # Only add non-empty rows
                    table_data.append(row_data)
            
            if table_data:  # Only add non-empty tables
                # Check if this table already exists (avoid duplicates)
                table_str = "|".join(["|".join(row) for row in table_data])
                if not any(t["table_str"] == table_str for t in tables if "table_str" in t):
                    tables.append({
                        "table_data": table_data,
                        "table_str": table_str  # For duplicate checking
                    })
        
        if tables:
            # Only store the table data, not the Tag objects
            section_data["tables"] = [t["table_data"] for t in tables]
        
        # FAQS SECTION
        faq_wrapper = wrapper.find("div", class_="AnATaggedFaqWrapper")
        if faq_wrapper:
            faqs = []
            seen_questions = set()
            faq_items = faq_wrapper.find_all("div", id=lambda x: x and "::" in x)
            
            for faq_item in faq_items:
                question_div = faq_item
                answer_div = faq_item.find_next_sibling("div", class_="_16f53f")
                
                if question_div and answer_div:
                    question = question_div.get_text(" ", strip=True)
                    answer = answer_div.get_text(" ", strip=True)
                    
                    # Clean question text
                    question = question.replace("Q:", "").replace("Q :", "").strip()
                    
                    if question and answer and question not in seen_questions:
                        seen_questions.add(question)
                        faqs.append({
                            "question": question,
                            "answer": answer[:500] + "..." if len(answer) > 500 else answer
                        })
            
            if faqs:
                section_data["faqs"] = faqs
        
        # IMAGES
        images = []
        seen_images = set()
        for img_tag in wrapper.find_all("img"):
            img_src = img_tag.get("src", "")
            img_alt = img_tag.get("alt", "")
            
            # Filter out common icons/placeholders
            if (img_src and img_src not in seen_images and 
                not img_src.endswith(".svg") and 
                not "commonIcons" in img_src and
                not img_src.startswith("data:")):
                
                seen_images.add(img_src)
                images.append({
                    "src": img_src,
                    "alt": img_alt
                })
        
        if images:
            section_data["images"] = images
        
        # Add section data if it has content
        if section_data and "heading" in section_data:
            data["sections"].append(section_data)
    
    return data

def scrape_accepting_college(driver, URLS):
    driver.get(URLS["accepting_college"])
    
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {},
        "intro": [],
        "toc": [],
        "sections": []
    }

    # TITLE
    title = soup.find("h1", class_="event_name")
    if title:
        data["Title"] = title.text.strip()
    else:
        title_ids = ["content_toc_573797", "content_toc_523057", "content_toc_780609", "content_toc_1053680"]
        for title_id in title_ids:
            new_title = soup.find("h2", id=title_id)
            if new_title:
                data["Title"] = new_title.text.strip()
                break
        else:
            title_tag = soup.find("h1") or soup.find("h2")
            if title_tag:
                data["Title"] = title_tag.text.strip()
    
    # META (Updated on and Author)
    updated = soup.find("p", class_="_9ad6")
    if updated:
        data["meta"]["updated_on"] = updated.text.strip()
    
    author = soup.find("a", class_="_9b27")
    if author:
        data["meta"]["author_name"] = author.text.strip()
        data["meta"]["author_profile"] = author.get("href", "")
    
    # MAIN CONTENT SECTION
    main_section = soup.find("section", class_="subcontainer")
    if main_section:
        section_data = {}
        
        # MAIN HEADING
        main_heading = main_section.find("h2")
        if main_heading:
            section_data["heading"] = main_heading.text.strip()
        
        # INTRO PARAGRAPH
        intro_para = main_section.find("p")
        if intro_para:
            data["intro"].append(intro_para.get_text(" ", strip=True))
        
        # TABLE OF CONTENTS
        toc_div = main_section.find("div", class_="newTocWrapper")
        if toc_div:
            toc_items = []
            # Get all li items from TOC
            for li in toc_div.find_all("li"):
                toc_text = li.get_text(" ", strip=True)
                if toc_text:
                    toc_items.append(toc_text)
            data["toc"] = toc_items
        
        # ALL SECTIONS (h2, h3 with their content)
        sections = []
        
        # Find all h2 and h3 headings
        headings = main_section.find_all(["h2", "h3"])
        
        for i, heading in enumerate(headings):
            if heading.get("id") and heading.get("id").startswith("ctp_bhst_toc_"):
                section_item = {}
                section_item["heading"] = heading.text.strip()
                section_item["heading_id"] = heading.get("id", "")
                
                # Get content after this heading until next heading
                content_items = []
                next_element = heading.find_next_sibling()
                
                while next_element and next_element.name not in ["h2", "h3"]:
                    if next_element.name == "p":
                        p_text = next_element.get_text(" ", strip=True)
                        if p_text:
                            links = []
                            for link in next_element.find_all("a"):
                                links.append({
                                    "text": link.text.strip(),
                                    "href": link.get("href", "")
                                })
                            content_items.append({
                                "type": "paragraph",
                                "text": p_text,
                                "links": links if links else []
                            })
                    
                    elif next_element.name == "ul":
                        list_items = []
                        for li in next_element.find_all("li"):
                            li_text = li.text.strip()
                            if li_text:
                                li_links = []
                                for link in li.find_all("a"):
                                    li_links.append({
                                        "text": link.text.strip(),
                                        "href": link.get("href", "")
                                    })
                                list_items.append({
                                    "text": li_text,
                                    "links": li_links if li_links else []
                                })
                        
                        if list_items:
                            content_items.append({
                                "type": "unordered_list",
                                "items": list_items
                            })
                    
                    elif next_element.name == "table":
                        table_data = []
                        for row in next_element.find_all("tr"):
                            row_data = []
                            for cell in row.find_all(["td", "th"]):
                                cell_text = cell.get_text(" ", strip=True)
                                if cell_text:
                                    row_data.append(cell_text)
                            
                            if row_data:
                                table_data.append(row_data)
                        
                        if table_data:
                            content_items.append({
                                "type": "table",
                                "data": table_data
                            })
                    
                    # Move to next sibling
                    next_element = next_element.find_next_sibling()
                
                if content_items:
                    section_item["content"] = content_items
                
                sections.append(section_item)
        
        if sections:
            section_data["sub_sections"] = sections
        
        if section_data:
            data["sections"].append(section_data)
    
    return data

def scrape_with_low_fees(driver, URLS):
    driver.get(URLS["mba_with_low_fees"])
    
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "Title": "",
        "meta": {
            "author_name": "",
            "author_profile": "",
            "author_designation": "",
            "author_image": ""
        },
        "content": [],
        "faqs": [],
        "summary": {}
    }

    # TITLE
    title = soup.find("h1", class_="event_name") or soup.find("h1") or soup.find("h2")
    if title:
        data["Title"] = title.text.strip()
    
    # AUTHOR INFO - COMPLETE DETAILS
    # Look for author link
    author_link = soup.find("a", href=lambda x: x and "/author/" in x if x else False)
    if author_link:
        data["meta"]["author_name"] = author_link.text.strip()
        data["meta"]["author_profile"] = author_link.get("href", "")
    
    # If not found in link, search in whole page
    if not data["meta"]["author_name"]:
        import re
        html_content = str(soup)
        # Try to find author name in page
        name_match = re.search(r'>([A-Z][a-z]+ [A-Z][a-z]+)<', html_content)
        if name_match:
            data["meta"]["author_name"] = name_match.group(1)
    
    # AUTHOR DESIGNATION
    designation = soup.find("div", class_="user_expert_level")
    if designation:
        data["meta"]["author_designation"] = designation.get_text().strip()
    
    # AUTHOR IMAGE
    img = soup.find("img", alt=lambda x: x and "Saumya" in str(x) if x else False)
    if not img:
        # Try other ways to find author image
        img = soup.find("img", src=lambda x: x and "Saumya" in str(x) if x else False)
    if not img:
        # Look for any image in author section
        author_section = soup.select_one(".author-info, .author-details, .post-author")
        if author_section:
            img = author_section.find("img")
    
    if img:
        data["meta"]["author_image"] = img.get("src", "")

    # FIND MAIN CONTENT
    main_content = soup.select_one("#blogId-23533") or soup.select_one(".adpPwa_summary") or soup

    # REMOVE ALL UNWANTED ELEMENTS
    unwanted = [
        ".onSiteDFPReco_new", ".DFPRecoWrapper", ".DFPReco", ".dfpRecobox",
        "#poll-container-box-1", ".sliderContainer", ".openVideoContainer",
        "._078b", ".embed", "._906ee8", ".c358de", ".sectional-faqs",
        ".d684be", "._16f53f", "._581b44", "._057223", ".dea386", "._9df549",
        "#recoWidget_onSiteDFPReco", "#dfpReco_ADP", "#ADP_Exam_recoWidget",
        "#reelsWidget", "#livePlayer"
    ]
    
    for selector in unwanted:
        for element in main_content.select(selector):
            element.decompose()
    
    # EXTRACT CLEAN SECTIONS
    sections = main_content.select(".wikkiContents")
    
    for section in sections:
        # SKIP ADS AND SHORT SECTIONS
        section_text = section.get_text(strip=True)
        
        if len(section_text) < 100:
            continue
            
        ad_keywords = ["Apply Now", "Last Date", "Admission Open", "Rank", "Click Here"]
        if any(keyword in section_text for keyword in ad_keywords):
            continue
        
        # GET HEADINGS
        headings = section.find_all(["h2", "h3", "h4"])
        if not headings:
            continue
            
        section_content = {
            "headings": [],
            "text": [],
            "table": None
        }
        
        # ADD HEADINGS
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if heading_text and heading_text not in ["Also Read:", "Read More:"]:
                section_content["headings"].append(heading_text)
        
        # GET PARAGRAPHS (EXCLUDE TABLE CONTENT)
        paragraphs = section.find_all("p")
        
        # Identify table paragraphs to exclude
        table_paragraphs = set()
        tables = section.find_all("table")
        for table in tables:
            table_ps = table.find_all("p")
            for p in table_ps:
                table_paragraphs.add(p)
        
        for para in paragraphs:
            if para in table_paragraphs:
                continue
                
            para_text = para.get_text(strip=True)
            if para_text and len(para_text) > 30 and "Apply Now" not in para_text:
                section_content["text"].append(para_text)
        
        # GET TABLE IF EXISTS
        if tables:
            table = tables[0]
            table_data = {
                "headers": [],
                "data": []
            }
            
            # Get headers
            headers = table.find_all("th")
            if headers:
                table_data["headers"] = [th.get_text(strip=True) for th in headers]
            else:
                first_row = table.find("tr")
                if first_row:
                    cells = first_row.find_all(["td", "th"])
                    table_data["headers"] = [cell.get_text(strip=True) for cell in cells]
            
            # Get data rows
            rows = table.find_all("tr")
            start_idx = 1 if headers else 0
            
            for i in range(start_idx, len(rows)):
                row = rows[i]
                cells = row.find_all(["td", "th"])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table_data["data"].append(row_data)
            
            if table_data["data"]:
                section_content["table"] = table_data
        
        # Only add if section has content
        if section_content["headings"] or section_content["text"] or section_content["table"]:
            data["content"].append(section_content)
    
    # EXTRACT FAQS
    faq_items = soup.select(".c5db62.listener, .html-0")
    for faq in faq_items:
        question_elem = faq.select_one("strong.flx-box")
        if question_elem:
            question = question_elem.get_text(strip=True).replace("Q: ", "")
            
            answer_div = faq.find_next("div", class_="_16f53f")
            if answer_div:
                answer_elem = answer_div.select_one(".cmsAContent")
                if answer_elem:
                    answer = answer_elem.get_text(strip=True).replace("A: ", "")
                    
                    # Remove GPT button text
                    gpt_button = answer_elem.find_next("div", class_="_581b44")
                    if gpt_button:
                        gpt_text = gpt_button.get_text(strip=True)
                        answer = answer.replace(gpt_text, "")
                    
                    data["faqs"].append({
                        "question": question,
                        "answer": answer
                    })
    
    # EXTRACT SUMMARY INFORMATION
    import re
    
    fees = set()
    colleges = []
    
    for section in data["content"]:
        # Extract from text
        for text in section["text"]:
            found_fees = re.findall(r'INR\s*([\d\.,]+\s*(?:Lakh|L|Lac|lakh|LPA))', text, re.IGNORECASE)
            fees.update(found_fees)
        
        # Extract from table
        if section.get("table"):
            for row in section["table"]["data"]:
                for cell in row:
                    found_fees = re.findall(r'INR\s*([\d\.,]+\s*(?:Lakh|L|Lac|lakh|LPA))', cell, re.IGNORECASE)
                    fees.update(found_fees)
        
        # Extract college names from headings
        for heading in section["headings"]:
            if any(word in heading for word in ["University", "College", "Institute", "FMS", "JBIMS", "TISS"]):
                colleges.append(heading)
    
    # Clean up college list
    colleges = list(set(colleges))
    
    # Add summary
    data["summary"] = {
        "all_fees": sorted(list(fees)),
        "colleges_found": colleges,
        "total_colleges": len(colleges)
    }
    
    return data
    
def scrape_mba_colleges():
    driver = create_driver()

      

    try:
       data = {
              "MBA":{
                   "overviews":extract_course_data(driver),
                   "courses":scrape_courses_overview_section(driver),
                   "mba syllabus":scrape_mba_syllabus(driver),
                   "mba career":scrape_mba_career(driver),
                   "mba addmission 2026":scrape_addmission_2026_data(driver),
                   "mba fees": scrape_mba_fees_overview(driver),
                   "MBA VS PGDM":scrape_pgdm_vs_mba_article(driver),
                   "MBA VS MSC":{
                       "INFO":scrape_mba_msc(driver),
                       "ARTICAL":scrape_full_article(driver)
                   },
                     "CAT EXAM":{
                         "overviews":scrape_full_cat_exam(driver, URLS),
                        "result_section":{
                         "result":scrape_full_cat_exam_result_bulletproof(driver, URLS),
                         "CAT 2025 LIST":scrape_cat_toppers_data(driver, URLS),
                        },
                        
                     },
                    "CUT_OFF":scrape_cutoff_section(driver, URLS),
                    "answer_key":scrape_ans_key(driver, URLS),
                    "counselling":{
                       "page_data":scrape_counselling(driver, URLS),
                       "q_A":scrape_faqs_selenium(driver, URLS),
                    },
                    "analysis":scrape_analysis(driver, URLS),
                    "question_paper": scrape_question_paper(driver, URLS),
                    "admit_card":scrape_admit_card(driver, URLS),
                    "dates":scrape_dates(driver, URLS),
                    "mock_text":scrape_mock_test(driver, URLS),
                    "registion":scrape_registration(driver, URLS),
                    "syllabus":scrape_syllabus(driver, URLS),
                    "pattern":scrape_pattern(driver, URLS),
                    "preparation":scrape_preparation(driver, URLS),
                    "books":scrape_books(driver, URLS),
                    "notification":scrape_notification(driver, URLS),
                    "center":scrape_center(driver, URLS),
                    "news":scrape_news(driver, URLS),
                    "accepting_college":{
                        "overview":scrape_accepting_college(driver, URLS),
                        "mba_with_low_fees":scrape_with_low_fees(driver, URLS),
                    }
                   }
                }
       
        
        # data["overview"] =  overviews
        # data["courses"] = courses

    finally:
        driver.quit()
    
    return data



import os

TEMP_FILE = "popular_mba_data.tmp.json"
FINAL_FILE = "popular_mba_data.json"

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

