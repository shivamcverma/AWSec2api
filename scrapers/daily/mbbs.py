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

PCOMBA_O_URL="https://www.shiksha.com/mbbs-chp"
PCOMBA_C_URL="https://www.shiksha.com/mbbs-courses-chp"
# PCOMBA_MBA_SYLLABUS_URL = "https://www.shiksha.com/mba-masters-of-business-administration-syllabus-chp"
PCOMBA_SUB_URL = "https://www.shiksha.com/mbbs-subjects-chp"
PCOMBA_MBA_CAREER_URL = "https://www.shiksha.com/mbbs-career-chp"
PCOMBA_MBA_ADDMISSION_2026_URL = "https://www.shiksha.com/mbbs-admission-chp"
PCOMBA_MBA_FEES_URL = "https://www.shiksha.com/mbbs-fees-chp"
PCOMBA_COMP_URL = "https://www.shiksha.com/mbbs-comparison-chp"
MD_VS_MBBS = "https://www.shiksha.com/medicine-health-sciences/medicine/articles/md-vs-mbbs-differences-eligibility-admission-jobs-salary-2023-blogId-132969"
AIIMS_IN_INDIA = "https://www.shiksha.com/medicine-health-sciences/articles/aiims-in-india-blogId-23925"
MBBS_ALTERNATIVE = "https://www.shiksha.com/medicine-health-sciences/articles/alternative-courses-for-mbbs-know-eligibility-fees-and-package-in-lakh-blogId-169499"
NEET_UG_2024 = "https://www.shiksha.com/medicine-health-sciences/neet-exam"
P_COLLEGE = "https://www.shiksha.com/medicine-health-sciences/colleges/mbbs-colleges-india?sby=popularity&rf=filters"
QA = "https://www.shiksha.com/tags/mbbs-tdp-401"
QAD = "https://www.shiksha.com/tags/mbbs-tdp-401?type=discussion"

def create_driver():

    options = Options()

    options.binary_location = "/usr/bin/chromium-browser"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    return driver


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
    # ELIGIBILITY SECTION (UPDATED & ENHANCED)
    # =====================================================
    eligibility_section = soup.find("section", id="chp_section_eligibility")

    if eligibility_section:
        eligibility_div = eligibility_section.find(
            "div", id="wikkiContents_chp_section_eligibility_1"
        )

        # ----------------------------
        # Description Paragraphs
        # ----------------------------
        description = []
        if eligibility_div:
            for p in eligibility_div.find_all("p")[:2]:
                text = p.get_text(" ", strip=True)
                if text:
                    description.append(text)

        # ----------------------------
        # Eligibility Tables
        # ----------------------------
        eligibility_tables = []
        if eligibility_div:
            for table in eligibility_div.find_all("table"):
                headers = []
                rows = []

                # table headers
                ths = table.find_all("th")
                headers = [th.get_text(" ", strip=True) for th in ths]

                # table rows
                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if tds:
                        rows.append([td.get_text(" ", strip=True) for td in tds])

                if headers or rows:
                    eligibility_tables.append({
                        "headers": headers,
                        "rows": rows
                    })

        # ----------------------------
        # Admission Steps
        # ----------------------------
        admission_steps = []
        if eligibility_div:
            admission_heading = eligibility_div.find("h2", string=lambda x: x and "Step-by-Step" in x)
            if admission_heading:
                ul = admission_heading.find_next("ul")
                if ul:
                    for li in ul.find_all("li"):
                        admission_steps.append(li.get_text(" ", strip=True))

        # ----------------------------
        # Scholarships
        # ----------------------------
        scholarships = []
        scholarship_heading = eligibility_div.find("h2", string=lambda x: x and "Scholarships" in x)

        if scholarship_heading:
            table = scholarship_heading.find_next("table")
            if table:
                for tr in table.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if len(tds) == 2:
                        college = tds[0].get_text(" ", strip=True)
                        schemes = [li.get_text(" ", strip=True) for li in tds[1].find_all("li")]
                        scholarships.append({
                            "college": college,
                            "scholarships": schemes
                        })

        # ----------------------------
        # Useful Links
        # ----------------------------
        useful_links = []
        if eligibility_div:
            for a in eligibility_div.find_all("a", href=True):
                useful_links.append({
                    "title": a.get_text(strip=True),
                    "url": a["href"]
                })

        # ----------------------------
        # FAQs
        # ----------------------------
        faqs = []
        faq_questions = eligibility_section.find_all("div", class_="html-0")

        for q in faq_questions:
            question = q.get_text(" ", strip=True).replace("Q:", "").strip()
            answer_div = q.find_next("div", class_="_16f53f")

            if answer_div:
                answer = " ".join(
                    p.get_text(" ", strip=True)
                    for p in answer_div.find_all("p")
                    if p.get_text(strip=True)
                )

                faqs.append({
                    "question": question,
                    "answer": answer
                })

        # ----------------------------
        # Final Data Structure
        # ----------------------------
        data["eligibility"] = {
            "description": description,
            "tables": eligibility_tables,
            "admission_steps": admission_steps,
            "scholarships": scholarships,
            "useful_links": useful_links,
            "faqs": faqs
        }

    # COURSE SYLLABUS / MBBS SUBJECTS SECTION
    # =====================================================
    coursesyllabus_section = soup.find("section", id="chp_section_coursesyllabus")

    if coursesyllabus_section:
        syllabus_div = coursesyllabus_section.find(
            "div", id="wikkiContents_chp_section_coursesyllabus_0"
        )

        # ----------------------------
        # Description Paragraphs
        # ----------------------------
        syllabus_description = []
        if syllabus_div:
            for p in syllabus_div.find_all("p")[:2]:
                text = p.get_text(" ", strip=True)
                if text:
                    syllabus_description.append(text)

        # ----------------------------
        # MBBS Subjects (Phase-wise Table)
        # ----------------------------
        phases = []
        if syllabus_div:
            table = syllabus_div.find("table")
            if table:
                for tr in table.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if len(tds) == 2:
                        phase_name = tds[0].get_text(" ", strip=True)
                        subjects = [
                            li.get_text(" ", strip=True)
                            for li in tds[1].find_all("li")
                        ]
                        phases.append({
                            "phase": phase_name,
                            "subjects": subjects
                        })

        # ----------------------------
        # Useful / Recommended Links
        # ----------------------------
        syllabus_links = []
        if syllabus_div:
            for a in syllabus_div.find_all("a", href=True):
                syllabus_links.append({
                    "title": a.get_text(strip=True),
                    "url": a["href"]
                })

        # ----------------------------
        # FAQs
        # ----------------------------
        syllabus_faqs = []
        faq_questions = coursesyllabus_section.find_all("div", class_="html-0")

        for q in faq_questions:
            question = q.get_text(" ", strip=True).replace("Q:", "").strip()
            answer_div = q.find_next("div", class_="_16f53f")

            if answer_div:
                answer = " ".join(
                    p.get_text(" ", strip=True)
                    for p in answer_div.find_all("p")
                    if p.get_text(strip=True)
                )

                syllabus_faqs.append({
                    "question": question,
                    "answer": answer
                })

        # ----------------------------
        # Final Data Add
        # ----------------------------
        data["course_syllabus"] = {
            "description": syllabus_description,
            "phases": phases,
            "important_links": syllabus_links,
            "faqs": syllabus_faqs
        }
    # =====================================================
    # POPULAR COLLEGES SECTION
    # =====================================================
    popular_section = soup.find(
        "div",
        id="wikkiContents_chp_section_popularcolleges_0"
    )

    if popular_section:
        content_div = popular_section.find("div")

        # ----------------------------
        # Description Paragraphs
        # ----------------------------
        descriptions = []
        for p in content_div.find_all("p", recursive=False):
            text = p.get_text(" ", strip=True)
            if text and "Note:" not in text:
                descriptions.append(text)

        # ----------------------------
        # AIIMS Colleges Table
        # ----------------------------
        aiims_colleges = []
        aiims_heading = content_div.find("h3", string=lambda x: x and "AIIMS" in x)

        if aiims_heading:
            table = aiims_heading.find_next("table")
            if table:
                for tr in table.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if len(tds) == 3:
                        link = tds[1].find("a")
                        aiims_colleges.append({
                            "nirf_rank": tds[0].get_text(strip=True),
                            "college": tds[1].get_text(" ", strip=True),
                            "url": link["href"] if link else None,
                            "total_fees_inr": tds[2].get_text(strip=True)
                        })

        # ----------------------------
        # Government Colleges Fees
        # ----------------------------
        government_colleges = []
        govt_heading = content_div.find(
            "h3", string=lambda x: x and "Government" in x
        )

        if govt_heading:
            table = govt_heading.find_next("table")
            if table:
                for tr in table.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if len(tds) == 2:
                        link = tds[0].find("a")
                        government_colleges.append({
                            "college": tds[0].get_text(" ", strip=True),
                            "url": link["href"] if link else None,
                            "fees_inr": tds[1].get_text(strip=True)
                        })

        # ----------------------------
        # Private Colleges Fees
        # ----------------------------
        private_colleges = []
        private_heading = content_div.find(
            "h3", string=lambda x: x and "Private" in x
        )

        if private_heading:
            table = private_heading.find_next("table")
            if table:
                for tr in table.find_all("tr")[1:]:
                    tds = tr.find_all("td")
                    if len(tds) == 2:
                        link = tds[0].find("a")
                        private_colleges.append({
                            "college": tds[0].get_text(" ", strip=True),
                            "url": link["href"] if link else None,
                            "fees_inr": tds[1].get_text(strip=True)
                        })

        # ----------------------------
        # Related Links
        # ----------------------------
        related_links = []
        for a in content_div.find_all("a", href=True):
            title = a.get_text(strip=True)
            if title and "http" in a["href"]:
                related_links.append({
                    "title": title,
                    "url": a["href"]
                })

        # ----------------------------
        # YouTube Videos
        # ----------------------------
        videos = []
        for iframe in content_div.find_all("iframe"):
            src = iframe.get("src")
            if src and "youtube" in src:
                videos.append(src)

        # ----------------------------
        # Final Data Structure
        # ----------------------------
        data["popular_colleges"] = {
            "description": descriptions,
            "aiims": aiims_colleges,
            "government_colleges": government_colleges,
            "private_colleges": private_colleges,
            "related_links": related_links,
            "videos": videos
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



def scrape_mbbs_subjects_overview(driver):
    driver.get(PCOMBA_SUB_URL)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    data = {}

    section = soup.find("section", id="chp_subjects_overview")
    if not section:
        return data

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

    # =====================================================
    # MAIN CONTENT DIV
    # =====================================================
    content = section.find("div", id="wikkiContents_chp_subjects_overview_0")
    if not content:
        return data

    content_div = content.find("div")

    # =====================================================
    # INTRO / DESCRIPTION
    # =====================================================
    description = []
    for p in content_div.find_all("p")[:11]:
        text = p.get_text(" ", strip=True)
        if text:
            description.append(text)

    data["description"] = description

    # =====================================================
    # YOUTUBE VIDEOS
    # =====================================================
    videos = []
    for iframe in content_div.find_all("iframe"):
        src = iframe.get("src")
        if src and "youtube" in src:
            videos.append(src)

    data["videos"] = videos

    # =====================================================
    # HELPER FUNCTION FOR TABLE EXTRACTION
    # =====================================================
    def extract_table(table):
        headers = []
        rows = []

        ths = table.find_all("th")
        if ths:
            headers = [th.get_text(" ", strip=True) for th in ths]

        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if tds:
                rows.append([td.get_text(" ", strip=True) for td in tds])

        return {
            "headers": headers,
            "rows": rows
        }

    # =====================================================
    # SEMESTER / YEAR-WISE SYLLABUS
    # =====================================================
    semester_syllabus = []

    for h3 in content_div.find_all("h3"):
        title = h3.get_text(" ", strip=True)
        table = h3.find_next("table")

        if table:
            semester_syllabus.append({
                "title": title,
                "table": extract_table(table)
            })

    data["semester_wise_syllabus"] = semester_syllabus

    # =====================================================
    # CORE & ELECTIVE SUBJECTS
    # =====================================================
    subjects_sections = []

    for h2 in content_div.find_all("h2"):
        title = h2.get_text(" ", strip=True)
        table = h2.find_next("table")

        if table:
            subjects_sections.append({
                "title": title,
                "table": extract_table(table)
            })

    data["subjects_categories"] = subjects_sections

    # =====================================================
    # BOOKS & AUTHORS
    # =====================================================
    books = []

    for h2 in content_div.find_all(["h2", "h3"]):
        if "Books" in h2.get_text():
            title = h2.get_text(" ", strip=True)
            table = h2.find_next("table")

            if table:
                books.append({
                    "category": title,
                    "table": extract_table(table)
                })

    data["books"] = books

    # =====================================================
    # HELPFUL / RELEVANT LINKS
    # =====================================================
    links = []
    for a in content_div.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text:
            links.append({
                "title": text,
                "url": a["href"]
            })

    data["links"] = links

    return data

# def scrape_mba_syllabus(driver):
#     driver.get(PCOMBA_MBA_SYLLABUS_URL)
#     wait = WebDriverWait(driver, 15)
#     soup = BeautifulSoup(driver.page_source, "html.parser")

#     data = {
#         "title": None,
#         "updated_on": None,
#         "author": None,
#         "courses": {
#             "intro": {"paragraphs": [], "links": []},
#             "syllabus_2025": {"description": [], "semester_wise": [], "note": None},
#             "specializations": {},
#             "videos": [],
#             "suggested_reads": [],
#             "top_colleges": []  # <-- Add this
#         }
#     }

#     # ===============================
#     # Course Name
#     course_name_div = soup.find("div", class_="a54c")
#     if course_name_div:
#         h1 = course_name_div.find("h1")
#         data["title"] = clean(h1)

#     # ===============================
#     # Updated Date
#     updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
#     if updated_div:
#         span = updated_div.find("span")
#         data["updated_on"] = clean(span)

#     # ===============================
#     # Author Info
#     author_block = soup.find("div", class_="be8c")
#     if author_block:
#         a = author_block.find("a")
#         data["author"] = {
#             "name": clean(a),
#             "profile": a["href"] if a else None,
#             "image": author_block.find("img")["src"] if author_block.find("img") else None,
#             "role": clean(author_block.find("span", class_="b0fc")),
#             "verified": bool(author_block.find("i", class_="tickIcon"))
#         }

#     # ===============================
#     # GENERAL SYLLABUS
#     container = soup.find("div", id="wikkiContents_chp_syllabus_overview_0")
#     current_semester = None
#     if container:
#         for elem in container.find_all(["p", "h2", "table", "iframe", "a"], recursive=True):
#             # PARAGRAPHS
#             if elem.name == "p":
#                 text = elem.get_text(" ", strip=True)
#                 if not text or "DFP-Banner" in text:
#                     continue
#                 link = elem.find("a", href=True)
#                 if text.lower().startswith("note"):
#                     data["courses"]["syllabus_2025"]["note"] = text
#                     continue
#                 if "Suggested Read" in text:
#                     continue
#                 if not data["courses"]["syllabus_2025"]["description"]:
#                     if link:
#                         data["courses"]["intro"]["links"].append({
#                             "text": link.get_text(strip=True),
#                             "url": link["href"]
#                         })
#                     else:
#                         data["courses"]["intro"]["paragraphs"].append(text)
#                 else:
#                     data["courses"]["syllabus_2025"]["description"].append(text)

#             # TABLES
#             elif elem.name == "table":
#                 for tr in elem.find_all("tr"):
#                     th = tr.find("th")
#                     if th:
#                         semester_text = th.get_text(" ", strip=True)
#                         if "Semester" in semester_text:
#                             current_semester = {
#                                 "semester": semester_text.replace("MBA Course Syllabus", "")
#                                                          .replace("MBA Course Subjects", "")
#                                                          .replace("MBA Subjects", "")
#                                                          .strip(),
#                                 "subjects": []
#                             }
#                             data["courses"]["syllabus_2025"]["semester_wise"].append(current_semester)
#                     else:
#                         for td in tr.find_all("td"):
#                             subject = td.get_text(" ", strip=True)
#                             if subject and subject != "-" and current_semester:
#                                 current_semester["subjects"].append(subject)

#             # VIDEOS
#             elif elem.name == "iframe":
#                 src = elem.get("src") or elem.get("data-src")
#                 if src:
#                     data["courses"]["videos"].append(src)

#             # SUGGESTED READS
#             elif elem.name == "a":
#                 if "MBA Outlook Report" in elem.get_text():
#                     data["courses"]["suggested_reads"].append({
#                         "title": elem.get_text(strip=True),
#                         "url": elem.get("href") or elem.get("data-link")
#                     })

#     # ===============================
#     # SPECIALIZATION-WISE SYLLABUS
#     spec_container = soup.find("div", id="wikkiContents_chp_syllabus_popularcolleges_0")
#     if spec_container:
#         current_spec = None
#         current_semester = None

#         for elem in spec_container.find_all(["p", "h3", "table"], recursive=True):
#             if elem.name == "p":
#                 text = elem.get_text(" ", strip=True)
#                 if text:
#                     current_spec_desc = data["courses"]["specializations"].get(current_spec, {})
#                     if current_spec:
#                         current_spec_desc.setdefault("description", []).append(text)
#                         data["courses"]["specializations"][current_spec] = current_spec_desc

#             elif elem.name == "h3":
#                 current_spec = clean(elem)
#                 data["courses"]["specializations"][current_spec] = {
#                     "description": [],
#                     "semester_wise": []
#                 }
#                 current_semester = None

#             elif elem.name == "table" and current_spec:
#                 for tr in elem.find_all("tr"):
#                     th = tr.find("th")
#                     if th:
#                         semester_text = th.get_text(" ", strip=True)
#                         if "Semester" in semester_text:
#                             current_semester = {
#                                 "semester": semester_text.strip(),
#                                 "subjects": []
#                             }
#                             data["courses"]["specializations"][current_spec]["semester_wise"].append(current_semester)
#                     else:
#                         for td in tr.find_all("td"):
#                             subject = td.get_text(" ", strip=True)
#                             if subject and subject != "-" and current_semester:
#                                 current_semester["subjects"].append(subject)
    
#     # Find the specific section
#     data["courses"].setdefault("top_colleges", [])

#     section = soup.find("section", id="chp_syllabus_topratecourses")
#     if section:
#         tables = section.find_all("table")
#         for table in tables:
#             rows = table.find_all("tr")[1:]  # skip header
#             for row in rows:
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_name = cols[0].get_text(strip=True)
#                     pdf_link_tag = cols[1].find("a", class_="smce-cta-link")
#                     pdf_link = pdf_link_tag.get("data-link") if pdf_link_tag else None
#                     data["courses"]["top_colleges"].append({
#                         "college": college_name,
#                         "pdf_link": pdf_link
#                     })

#     return data

def scrape_mbbs_career(driver):
    driver.get(PCOMBA_MBA_CAREER_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}

    section = soup.find("section", id="chp_career_overview")
    if not section:
        return data

    # ===============================
    # Updated Date
    updated_div = section.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = section.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    content = section.find("div", class_="wikkiContents")

    # ===============================
    # 1. Career Overview (only text, no tables)
    overview_text = []
    for p in content.find_all("p")[:3]:
        txt = p.get_text(strip=True)
        if txt:
            overview_text.append(txt)
    data["career_overview"] = overview_text

    # ===============================
    # Helper: parse tables
    def parse_table(table):
        rows = []
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        for tr in table.find_all("tr")[1:]:
            cols = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if cols:
                rows.append(cols)
        return headers, rows

    # ===============================
    data["job_profiles"] = []
    data["emerging_trends"] = []
    data["industries"] = []
    data["courses_after_mbbs"] = []
    data["top_recruiters"] = []
    data["best_colleges"] = []

    for tag in content.find_all(["h2", "h3"]):
        title = tag.get_text(strip=True).lower()

        next_el = tag.find_next_sibling()

        # 🔹 Top MBBS Job Profiles
        if "job profiles" in title:
            table = tag.find_next("table")
            _, rows = parse_table(table)
            for r in rows:
                data["job_profiles"].append({
                    "profile": r[0],
                    "description": r[1],
                    "average_salary": r[2]
                })

        # 🔹 Emerging Trends
        elif "emerging trends" in title:
            ul = tag.find_next("ul")
            if ul:
                data["emerging_trends"] = [
                    li.get_text(strip=True) for li in ul.find_all("li")
                ]

        # 🔹 Scope / Industries
        elif "scope in india" in title:
            table = tag.find_next("table")
            _, rows = parse_table(table)
            for r in rows:
                data["industries"].append({
                    "industry": r[0],
                    "description": r[1]
                })

        # 🔹 Courses after MBBS
        elif "courses after mbbs" in title:
            table = tag.find_next("table")
            _, rows = parse_table(table)
            for r in rows:
                data["courses_after_mbbs"].append({
                    "course": r[0],
                    "description": r[1]
                })

        # 🔹 Top Recruiters
        elif "top recruiters" in title:
            table = tag.find_next("table")
            _, rows = parse_table(table)
            for r in rows:
                data["top_recruiters"].extend(r)

        # 🔹 Best Colleges for Placements
        elif "best mbbs colleges" in title:
            table = tag.find_next("table")
            _, rows = parse_table(table)
            for r in rows:
                data["best_colleges"].append({
                    "college": r[0],
                    "highest_package": r[1]
                })

    return data

 
# # convert a list of Tags to clean text
def tags_to_text(tags):
    return [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

def scrape_addmission_2026_data(driver):
    driver.get(PCOMBA_MBA_ADDMISSION_2026_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {}
    
    # Course Title
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        author_data = {
            "name": clean(a),
            "profile": a["href"] if a else None
        }
        
        img = author_block.find("img")
        if img:
            author_data["image"] = img["src"]
            
        role_span = author_block.find("span", class_="b0fc")
        if role_span:
            author_data["role"] = clean(role_span)
            
        tick_icon = author_block.find("i", class_="tickIcon")
        author_data["verified"] = bool(tick_icon)
        
        data["author"] = author_data

    # Overview Text
    overview_section = soup.find("div", id="wikkiContents_chp_admission_overview_0")
    if overview_section:
        paragraphs = overview_section.find_all("p")[:4]
        data['overview_text'] = tags_to_text(paragraphs)

        # Overview Links
        overview_links = []
        for p in paragraphs:
            a_tags = p.find_all("a")
            for a_tag in a_tags:
                if a_tag and a_tag.get("href"):
                    overview_links.append({
                        "text": a_tag.get_text(strip=True),
                        "url": a_tag['href']
                    })
        data['overview_links'] = overview_links

    # Latest News Section
    latest_news_p = soup.find("p", string=lambda x: x and "Latest News:" in x)
    if latest_news_p:
        # Latest news heading and paragraph
        data["latest_news_heading"] = clean(latest_news_p)
        
        # Latest news list items
        ul = latest_news_p.find_next("ul")
        if ul:
            news_items = []
            for li in ul.find_all("li"):
                news_items.append(clean(li))
            data["latest_news"] = news_items

    # Eligibility Section with heading and paragraph
    eligibility_h2 = soup.find("h2", id="chp_admission_toc_1")
    if eligibility_h2:
        # Get the heading text
        data["eligibility_heading"] = clean(eligibility_h2)
        
        # Get paragraph after heading
        eligibility_p = eligibility_h2.find_next("p")
        if eligibility_p:
            data["eligibility_description"] = clean(eligibility_p)
        
        # Get table data
        table = eligibility_h2.find_next("table")
        if table:
            eligibility_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    eligibility_data.append({
                        "particular": clean(cols[0]),
                        "criteria": clean(cols[1])
                    })
            data["eligibility_table"] = eligibility_data

    # Entrance Exams Section with heading and paragraph
    exams_h2 = soup.find("h2", id="chp_admission_toc_3")
    if exams_h2:
        # Get the heading text
        data["entrance_exams_heading"] = clean(exams_h2)
        
        # Get paragraph after heading
        exams_p = exams_h2.find_next("p")
        if exams_p:
            data["entrance_exams_description"] = clean(exams_p)
        
        # Get table data
        table = exams_h2.find_next("table")
        if table:
            exams_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    exams_data.append({
                        "exam": clean(cols[0]),
                        "date": clean(cols[1]),
                        "schedule": clean(cols[2])
                    })
            data["entrance_exams_table"] = exams_data

    # Syllabus Section with heading and paragraph
    syllabus_h3 = soup.find("h3", id="chp_admission_toc_3_0")
    if syllabus_h3:
        # Get the heading text
        data["syllabus_heading"] = clean(syllabus_h3)
        
        # Get paragraph after heading
        syllabus_p = syllabus_h3.find_next("p")
        if syllabus_p:
            data["syllabus_description"] = clean(syllabus_p)
        
        # Get table data
        table = syllabus_h3.find_next("table")
        if table:
            syllabus_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    syllabus_data.append({
                        "exam": clean(cols[0]),
                        "syllabus": clean(cols[1])
                    })
            data["syllabus_table"] = syllabus_data
        
        # Get paragraph after table
        after_table_p = table.find_next("p") if table else None
        if after_table_p and "Click here" in after_table_p.get_text():
            data["syllabus_links_paragraph"] = clean(after_table_p)

    # MBBS Admission Application Status Section
    application_status_h2 = soup.find("h2", id="chp_admission_toc_5")
    if application_status_h2:
        # Get the heading text
        data["application_status_heading"] = clean(application_status_h2)
        
        # Get paragraph after heading
        app_status_p = application_status_h2.find_next("p")
        if app_status_p:
            data["application_status_description"] = clean(app_status_p)

    # AIIMS Colleges Section with heading and paragraph
    aiims_h3 = soup.find("h3", id="chp_admission_toc_5_0")
    if aiims_h3:
        # Get the heading text
        data["aiims_colleges_heading"] = clean(aiims_h3)
        
        # Get paragraph after heading
        aiims_p = aiims_h3.find_next("p")
        if aiims_p:
            data["aiims_colleges_description"] = clean(aiims_p)
        
        # Get table data
        table = aiims_h3.find_next("table")
        if table:
            aiims_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    aiims_data.append({
                        "nirf_ranking": clean(cols[0]),
                        "college_name": clean(cols[1]),
                        "fees": clean(cols[2])
                    })
            data["aiims_colleges_table"] = aiims_data

    # Government Colleges Section with heading and paragraph
    govt_h3 = soup.find("h3", id="chp_admission_toc_5_1")
    if govt_h3:
        # Get the heading text
        data["government_colleges_heading"] = clean(govt_h3)
        
        # Get paragraph after heading
        govt_p = govt_h3.find_next("p")
        if govt_p:
            data["government_colleges_description"] = clean(govt_p)
        
        # Get table data
        table = govt_h3.find_next("table")
        if table:
            govt_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    govt_data.append({
                        "college_details": clean(cols[0]),
                        "fees": clean(cols[1])
                    })
            data["government_colleges_table"] = govt_data

    # Private Colleges Section with heading and paragraph
    private_h3 = soup.find("h3", id="chp_admission_toc_5_2")
    if private_h3:
        # Get the heading text
        data["private_colleges_heading"] = clean(private_h3)
        
        # Get paragraph after heading
        private_p = private_h3.find_next("p")
        if private_p:
            data["private_colleges_description"] = clean(private_p)
        
        # Get table data
        table = private_h3.find_next("table")
        if table:
            private_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    private_data.append({
                        "college_details": clean(cols[0]),
                        "fees": clean(cols[1])
                    })
            data["private_colleges_table"] = private_data

    # Placements Section with heading and paragraph
    placements_h2 = soup.find("h2", string=lambda x: x and "Placements" in x)
    if placements_h2:
        # Get the heading text
        data["placements_heading"] = clean(placements_h2)
        
        # Get paragraph after heading
        placements_p = placements_h2.find_next("p")
        if placements_p:
            data["placements_description"] = clean(placements_p)
        
        # Get table data
        table = placements_h2.find_next("table")
        if table:
            placements_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    placements_data.append({
                        "college_name": clean(cols[0]),
                        "highest_package": clean(cols[1])
                    })
            data["placements_table"] = placements_data

    # Useful/Suggested Links sections
    # Find all paragraphs with red colored text (useful links)
    useful_links = []
    for p in soup.find_all("p"):
        if p.find("span", style=lambda x: x and "color: #e03e2d" in x):
            span = p.find("span", style=lambda x: x and "color: #e03e2d" in x)
            if span:
                # Get the paragraph text as heading
                heading_text = clean(span)
                
                # Find all links in the next siblings until next heading
                links = []
                next_elem = p.find_next_sibling()
                while next_elem and next_elem.name not in ["h2", "h3", "h4"]:
                    if next_elem.name == "p":
                        a_tag = next_elem.find("a")
                        if a_tag and a_tag.get("href"):
                            links.append({
                                "text": clean(a_tag),
                                "url": a_tag['href']
                            })
                    next_elem = next_elem.find_next_sibling()
                
                if links:
                    useful_links.append({
                        "heading": heading_text,
                        "links": links
                    })
    
    if useful_links:
        data["useful_links"] = useful_links

    # Contact Info
    contact_section = soup.find("div", id="contact_info")
    if contact_section:
        data['contact_info'] = tags_to_text(contact_section.find_all("p"))

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
        author_data = {
            "name": clean(a),
            "profile": a["href"] if a else None
        }
        
        img = author_block.find("img")
        if img:
            author_data["image"] = img["src"]
            
        role_span = author_block.find("span", class_="b0fc")
        if role_span:
            author_data["role"] = clean(role_span)
            
        tick_icon = author_block.find("i", class_="tickIcon")
        author_data["verified"] = bool(tick_icon)
        
        data["author"] = author_data

    # ===============================
    # Overview Section
    overview_section = soup.find("div", id="wikkiContents_chp_fees_overview_0")
    if overview_section:
        # Overview text
        overview_divs = overview_section.find_all("div", id=lambda x: x and "wikkiContents_multi_ADP_undefined" in x)
        
        if overview_divs and len(overview_divs) > 0:
            first_div = overview_divs[0]
            paragraphs = first_div.find_all("p")
            overview_text = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and text != "\xa0":
                    overview_text.append(text)
            
            data["overview_text"] = overview_text

    # ===============================
    # Relevant Links Section
    relevant_links_div = soup.find("div", string=lambda x: x and "Relevant Links for MBBS Course Fees:" in x)
    if relevant_links_div:
        # Find the parent div with helpful links
        relevant_links = []
        next_elem = relevant_links_div.find_next("p")
        while next_elem and next_elem.name == "p":
            a_tag = next_elem.find("a")
            if a_tag:
                relevant_links.append({
                    "title": a_tag.get_text(strip=True),
                    "url": a_tag.get("href")
                })
            next_elem = next_elem.find_next_sibling()
        
        data["relevant_links"] = relevant_links

    # ===============================
    # MBBS Course Fees Structure Section
    fees_structure_h2 = soup.find("h2", id="chp_fees_toc_0")
    if fees_structure_h2:
        # Get heading
        data["fees_structure_heading"] = clean(fees_structure_h2)
        
        # Get paragraph after heading
        fees_para = fees_structure_h2.find_next("p")
        if fees_para:
            data["fees_structure_description"] = clean(fees_para)
        
        # Get table data
        table = fees_structure_h2.find_next("table")
        if table:
            fees_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    fees_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["fees_structure_table"] = fees_data
        
        # Get helpful links after table
        helpful_links_h2 = table.find_next("p") if table else None
        if helpful_links_h2 and helpful_links_h2.find("span", style=lambda x: x and "color: #e03e2d" in x):
            helpful_links = []
            next_p = helpful_links_h2.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["fees_structure_helpful_links"] = helpful_links

    # ===============================
    # MBBS Course Fees in Top Colleges Section
    top_colleges_h2 = soup.find("h2", id="chp_fees_toc_1")
    if top_colleges_h2:
        data["top_colleges_heading"] = clean(top_colleges_h2)
        
        # Find AIIMS fees table section
        aiims_table_para = top_colleges_h2.find_next("p", string=lambda x: x and "MBBS course fees structure at AIIMS" in x)
        if aiims_table_para:
            data["aiims_fees_description"] = clean(aiims_table_para)
            
            # Get AIIMS fees table
            aiims_table = aiims_table_para.find_next("table")
            if aiims_table:
                aiims_data = []
                rows = aiims_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_link = cols[0].find("a")
                        aiims_data.append({
                            "college": clean(cols[0]),
                            "fees": clean(cols[1]),
                            "link": college_link.get("href") if college_link else None
                        })
                data["aiims_fees_table"] = aiims_data

    # ===============================
    # Quick Links for Medical Courses
    quick_links_para = soup.find("p", string=lambda x: x and "Quick Links for Medical Courses:" in x)
    if quick_links_para:
        data["quick_links_heading"] = clean(quick_links_para)
        
        # Get quick links table
        quick_links_table = quick_links_para.find_next("table")
        if quick_links_table:
            quick_links_data = []
            rows = quick_links_table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                for col in cols:
                    a_tag = col.find("a")
                    if a_tag:
                        quick_links_data.append({
                            "title": clean(a_tag),
                            "url": a_tag.get("href")
                        })
            data["quick_links"] = quick_links_data

    # ===============================
    # MBBS Fees in Government College Section
    govt_fees_h3 = soup.find("h3", id="chp_fees_toc_1_2")
    if govt_fees_h3:
        data["govt_fees_heading"] = clean(govt_fees_h3)
        
        # Get description paragraph
        govt_desc = govt_fees_h3.find_next("p")
        if govt_desc:
            data["govt_fees_description"] = clean(govt_desc)
        
        # Get government fees table
        govt_table = govt_fees_h3.find_next("table")
        if govt_table:
            govt_data = []
            rows = govt_table.find_all("tr")
            for row in rows[1:]:  # Skip header (first row has heading in second column)
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    govt_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["govt_fees_table"] = govt_data
        
        # Get helpful links after table
        helpful_links_start = govt_table.find_next("p") if govt_table else None
        if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: #e03e2d" in x):
            helpful_links = []
            next_p = helpful_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["govt_fees_helpful_links"] = helpful_links

    # ===============================
    # MBBS Course Fees in Top Private Colleges Section
    private_fees_h3 = soup.find("h3", id="chp_fees_toc_1_3")
    if private_fees_h3:
        data["private_fees_heading"] = clean(private_fees_h3)
        
        # Get description paragraph
        private_desc = private_fees_h3.find_next("p")
        if private_desc:
            data["private_fees_description"] = clean(private_desc)
        
        # Get private fees table
        private_table = private_fees_h3.find_next("table")
        if private_table:
            private_data = []
            rows = private_table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    private_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["private_fees_table"] = private_data
        
        # Get suggested readings
        suggested_readings_start = private_table.find_next("p") if private_table else None
        if suggested_readings_start and suggested_readings_start.find("span", style=lambda x: x and "color: #e03e2d" in x):
            suggested_readings = []
            next_p = suggested_readings_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    suggested_readings.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["suggested_readings"] = suggested_readings

    # ===============================
    # MBBS Course Fees: Location-Wise Section
    location_wise_h2 = soup.find("h2", id="chp_fees_toc_2")
    if location_wise_h2:
        data["location_wise_heading"] = clean(location_wise_h2)
        
        # Get description paragraphs
        desc_para1 = location_wise_h2.find_next("p")
        if desc_para1:
            data["location_wise_description1"] = clean(desc_para1)
        
        desc_para2 = desc_para1.find_next("p") if desc_para1 else None
        if desc_para2:
            data["location_wise_description2"] = clean(desc_para2)

    # ===============================
    # Location-wise fees tables
    data["location_wise_fees"] = {}
    
    # Delhi Section
    delhi_heading = soup.find("p", string=lambda x: x and "MBBS Fees in Delhi" in x)
    if delhi_heading:
        data["location_wise_fees"]["delhi"] = {
            "heading": clean(delhi_heading),
            "description": "",
            "colleges": []
        }
        
        # Get description
        delhi_desc = delhi_heading.find_next("p")
        if delhi_desc:
            data["location_wise_fees"]["delhi"]["description"] = clean(delhi_desc)
        
        # Get Delhi table
        delhi_table = delhi_heading.find_next("table")
        if delhi_table:
            delhi_data = []
            rows = delhi_table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    delhi_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["location_wise_fees"]["delhi"]["colleges"] = delhi_data
        
        # Get suggested readings after Delhi table
        suggested_start = delhi_table.find_next("p") if delhi_table else None
        if suggested_start and suggested_start.get_text(strip=True).startswith("Suggested Readings"):
            suggested_readings = []
            next_p = suggested_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    suggested_readings.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["location_wise_fees"]["delhi"]["suggested_readings"] = suggested_readings

    # Kolkata Section
    kolkata_heading = soup.find("p", string=lambda x: x and "MBBS Course Fees in Kolkata" in x)
    if kolkata_heading:
        data["location_wise_fees"]["kolkata"] = {
            "heading": clean(kolkata_heading),
            "description": "",
            "colleges": []
        }
        
        # Get description
        kolkata_desc = kolkata_heading.find_next("p")
        if kolkata_desc:
            data["location_wise_fees"]["kolkata"]["description"] = clean(kolkata_desc)
        
        # Get Kolkata table
        kolkata_table = kolkata_heading.find_next("table")
        if kolkata_table:
            kolkata_data = []
            rows = kolkata_table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    kolkata_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["location_wise_fees"]["kolkata"]["colleges"] = kolkata_data

    # Hyderabad Section
    hyderabad_heading = soup.find("p", string=lambda x: x and "MBBS Fees in Hyderabad" in x)
    if hyderabad_heading:
        data["location_wise_fees"]["hyderabad"] = {
            "heading": clean(hyderabad_heading),
            "description": "",
            "colleges": []
        }
        
        # Get description
        hyderabad_desc = hyderabad_heading.find_next("p")
        if hyderabad_desc:
            data["location_wise_fees"]["hyderabad"]["description"] = clean(hyderabad_desc)
        
        # Get Hyderabad table
        hyderabad_table = hyderabad_heading.find_next("table")
        if hyderabad_table:
            hyderabad_data = []
            rows = hyderabad_table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    hyderabad_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["location_wise_fees"]["hyderabad"]["colleges"] = hyderabad_data

    # Bangalore Section
    bangalore_heading = soup.find("p", string=lambda x: x and "MBBS Course Fee in Bangalore" in x)
    if bangalore_heading:
        data["location_wise_fees"]["bangalore"] = {
            "heading": clean(bangalore_heading),
            "description": "",
            "colleges": []
        }
        
        # Get description
        bangalore_desc = bangalore_heading.find_next("p")
        if bangalore_desc:
            data["location_wise_fees"]["bangalore"]["description"] = clean(bangalore_desc)
        
        # Get Bangalore table
        bangalore_table = bangalore_heading.find_next("table")
        if bangalore_table:
            bangalore_data = []
            rows = bangalore_table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 2:
                    college_link = cols[0].find("a")
                    bangalore_data.append({
                        "college": clean(cols[0]),
                        "fees": clean(cols[1]),
                        "link": college_link.get("href") if college_link else None
                    })
            data["location_wise_fees"]["bangalore"]["colleges"] = bangalore_data

    return data

def scrape_mbbs_vs_bams_comparison(driver):
    # Assuming URL is defined elsewhere
    driver.get(PCOMBA_COMP_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    try:
        author_elem = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
            )
        )
    except:
        print("Author info not found in time.")
        author_elem = None

    data = {}

    # ---------- Course Name ----------
    try:
        course_name_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.a54c h1")
            )
        )
        data["title"] = course_name_elem.text.strip()
    except:
        data["title"] = None

    # ---------- Updated Date ----------
    try:
        updated_elem = driver.find_element(
            By.CSS_SELECTOR, "div.f48b span"
        )
        data["updated_on"] = updated_elem.text.strip()
    except:
        data["updated_on"] = None

    # ---------- Author Info ----------
    data["author"] = None

    try:
        author_block = driver.find_element(By.CSS_SELECTOR, "div.be8c")
        author_data = {}

        # Image
        try:
            img_tag = author_block.find_element(By.CSS_SELECTOR, "img.ePPImg")
            author_data["image"] = img_tag.get_attribute("src")
        except:
            author_data["image"] = None

        # Name + profile
        try:
            a_tag = author_block.find_element(By.TAG_NAME, "a")
            author_data["name"] = a_tag.text.strip()
            author_data["profile"] = a_tag.get_attribute("href")
        except:
            author_data["name"] = None
            author_data["profile"] = None

        # Verified
        try:
            tick = author_block.find_element(By.CSS_SELECTOR, "i.tickIcon")
            author_data["verified"] = True
        except:
            author_data["verified"] = False

        # Role / designation
        try:
            role_span = author_block.find_element(By.CSS_SELECTOR, "span.b0fc")
            author_data["role"] = role_span.text.strip()
        except:
            author_data["role"] = None

        data["author"] = author_data

    except:
        data["author"] = None

    # ===============================
    # Overview Section
    overview_section = soup.find("div", id="wikkiContents_chp_compare_overview_0")
    if overview_section:
        # Get all paragraphs before first heading
        overview_paragraphs = []
        for element in overview_section.find_all(["p", "h2"]):
            if element.name == "p":
                overview_paragraphs.append(clean(element))
            elif element.name == "h2":
                break
        
        data["overview_text"] = overview_paragraphs

    # ===============================
    # MBBS Vs BAMS: Course Overview Section
    course_overview_h2 = soup.find("h2", id="chp_comparison_cp_toc_0")
    if course_overview_h2:
        data["course_overview_heading"] = clean(course_overview_h2)
        
        # Get paragraphs after heading
        desc_para1 = course_overview_h2.find_next("p")
        if desc_para1:
            data["course_overview_description1"] = clean(desc_para1)
        
        desc_para2 = desc_para1.find_next("p") if desc_para1 else None
        if desc_para2:
            data["course_overview_description2"] = clean(desc_para2)
        
        # Get comparison table
        table = course_overview_h2.find_next("table")
        if table:
            comparison_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    comparison_data.append({
                        "particular": clean(cols[0]),
                        "mbbs": clean(cols[1]),
                        "bams": clean(cols[2])
                    })
            data["course_overview_table"] = comparison_data
        
        # Get helpful links after table
        helpful_links_start = table.find_next("p") if table else None
        if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: #e03e2d" in x):
            helpful_links = []
            next_p = helpful_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                elif next_p.name == "h2":
                    break
                next_p = next_p.find_next_sibling()
            
            data["course_overview_helpful_links"] = helpful_links

    # ===============================
    # MBBS vs BAMS: Definition Section
    definition_h2 = soup.find("h2", id="chp_comparison_cp_toc_1")
    if definition_h2:
        data["definition_heading"] = clean(definition_h2)
        
        # Get description paragraph
        definition_desc = definition_h2.find_next("p")
        if definition_desc:
            data["definition_description"] = clean(definition_desc)
        
        # What is MBBS?
        mbbs_h3 = soup.find("h3", id="chp_comparison_cp_toc_1_0")
        if mbbs_h3:
            data["mbbs_definition_heading"] = clean(mbbs_h3)
            mbbs_desc = mbbs_h3.find_next("p")
            if mbbs_desc:
                data["mbbs_definition"] = clean(mbbs_desc)
        
        # What is BAMS?
        bams_h3 = soup.find("h3", id="chp_comparison_cp_toc_1_1")
        if bams_h3:
            data["bams_definition_heading"] = clean(bams_h3)
            bams_desc = bams_h3.find_next("p")
            if bams_desc:
                data["bams_definition"] = clean(bams_desc)

    # ===============================
    # MBBS Vs BAMS: Eligibility Criteria Section
    eligibility_h2 = soup.find("h2", id="chp_comparison_cp_toc_2")
    if eligibility_h2:
        data["eligibility_heading"] = clean(eligibility_h2)
        
        # Get description paragraph
        eligibility_desc = eligibility_h2.find_next("p")
        if eligibility_desc:
            data["eligibility_description"] = clean(eligibility_desc)
        
        # Get eligibility table
        table = eligibility_h2.find_next("table")
        if table:
            eligibility_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    eligibility_data.append({
                        "particular": clean(cols[0]),
                        "mbbs": clean(cols[1]),
                        "bams": clean(cols[2])
                    })
            data["eligibility_table"] = eligibility_data

    # ===============================
    # MBBS Vs BAMS: Admission Criteria Section
    admission_h2 = soup.find("h2", id="chp_comparison_cp_toc_3")
    if admission_h2:
        data["admission_heading"] = clean(admission_h2)
        
        # Get description paragraph
        admission_desc = admission_h2.find_next("p")
        if admission_desc:
            data["admission_description"] = clean(admission_desc)
        
        # Get admission table
        table = admission_h2.find_next("table")
        if table:
            admission_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    admission_data.append({
                        "particular": clean(cols[0]),
                        "mbbs": clean(cols[1]),
                        "bams": clean(cols[2])
                    })
            data["admission_table"] = admission_data

    # ===============================
    # MBBS Vs BAMS: Top Colleges Section
    top_colleges_h2 = soup.find("h2", id="chp_comparison_cp_toc_4")
    if top_colleges_h2:
        data["top_colleges_heading"] = clean(top_colleges_h2)
        
        # Get description paragraphs
        desc_para1 = top_colleges_h2.find_next("p")
        if desc_para1:
            data["top_colleges_description1"] = clean(desc_para1)
        
        desc_para2 = desc_para1.find_next("p") if desc_para1 else None
        if desc_para2:
            data["top_colleges_description2"] = clean(desc_para2)
        
        # Get Top MBBS Colleges table
        mbbs_colleges_heading = soup.find("p", string=lambda x: x and "Top MBBS Colleges in India" in x)
        if mbbs_colleges_heading:
            data["mbbs_colleges_subheading"] = clean(mbbs_colleges_heading)
            
            # Get MBBS colleges table
            mbbs_table = mbbs_colleges_heading.find_next("table")
            if mbbs_table:
                mbbs_colleges_data = []
                rows = mbbs_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_link = cols[0].find("a")
                        mbbs_colleges_data.append({
                            "college": clean(cols[0]),
                            "fees": clean(cols[1]),
                            "link": college_link.get("href") if college_link else None
                        })
                data["mbbs_colleges_table"] = mbbs_colleges_data
        
        # Top BAMS Colleges
        bams_h3 = soup.find("h3", id="chp_comparison_cp_toc_4_0")
        if bams_h3:
            data["bams_colleges_heading"] = clean(bams_h3)
            
            # Get description paragraph
            bams_desc = bams_h3.find_next("p")
            if bams_desc:
                data["bams_colleges_description"] = clean(bams_desc)
            
            # Get BAMS colleges table
            bams_table = bams_h3.find_next("table")
            if bams_table:
                bams_colleges_data = []
                rows = bams_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_link = cols[0].find("a")
                        bams_colleges_data.append({
                            "college": clean(cols[0]),
                            "fees": clean(cols[1]),
                            "link": college_link.get("href") if college_link else None
                        })
                data["bams_colleges_table"] = bams_colleges_data

    # ===============================
    # MBBS Vs BAMS: Career Prospects, Job Profiles and Salary Section
    career_h2 = soup.find("h2", id="chp_comparison_cp_toc_5")
    if career_h2:
        data["career_heading"] = clean(career_h2)
        
        # Get description paragraph
        career_desc = career_h2.find_next("p")
        if career_desc:
            data["career_description"] = clean(career_desc)
        
        # MBBS Career Scope
        mbbs_career_h3 = soup.find("h3", id="chp_comparison_cp_toc_5_0")
        if mbbs_career_h3:
            data["mbbs_career_heading"] = clean(mbbs_career_h3)
            
            # Get description paragraph
            mbbs_career_desc = mbbs_career_h3.find_next("p")
            if mbbs_career_desc:
                data["mbbs_career_description"] = clean(mbbs_career_desc)
            
            # Get MBBS career table
            mbbs_career_table = mbbs_career_h3.find_next("table")
            if mbbs_career_table:
                mbbs_career_data = []
                rows = mbbs_career_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        mbbs_career_data.append({
                            "job_profile": clean(cols[0]),
                            "salary": clean(cols[1])
                        })
                data["mbbs_career_table"] = mbbs_career_data
        
        # BAMS Career Scope
        bams_career_h3 = soup.find("h3", id="chp_comparison_cp_toc_5_1")
        if bams_career_h3:
            data["bams_career_heading"] = clean(bams_career_h3)
            
            # Get description paragraph
            bams_career_desc = bams_career_h3.find_next("p")
            if bams_career_desc:
                data["bams_career_description"] = clean(bams_career_desc)
            
            # Get BAMS career table
            bams_career_table = bams_career_h3.find_next("table")
            if bams_career_table:
                bams_career_data = []
                rows = bams_career_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        bams_career_data.append({
                            "job_profile": clean(cols[0]),
                            "salary": clean(cols[1])
                        })
                data["bams_career_table"] = bams_career_data
        
        # Get helpful links after career tables
        helpful_links_start = bams_career_table.find_next("p") if bams_career_table else None
        if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: #e03e2d" in x):
            helpful_links = []
            next_p = helpful_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["career_helpful_links"] = helpful_links
        
        # Get conclusion paragraph
        conclusion_start = helpful_links_start.find_next("p") if helpful_links_start else None
        if conclusion_start:
            data["conclusion"] = clean(conclusion_start)

    return data

def scrape_mbbs_vs_md_comparison(driver):
    # Assuming URL is defined elsewhere
    driver.get(MD_VS_MBBS)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    try:
        author_elem = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
            )
        )
    except:
        print("Author info not found in time.")
        author_elem = None

    data = {}

    # ---------- Course Name ----------
    try:
        course_name_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.flx-box.mA h1")
            )
        )
        data["title"] = course_name_elem.text.strip()
    except:
        data["title"] = None

    # ---------- Updated Date ----------
    try:
        updated_elem = driver.find_element(
            By.CSS_SELECTOR, "div.adp_blog div.blogdata_user span"
        )
        data["updated_on"] = updated_elem.text.strip()
    except:
        data["updated_on"] = None

    # ---------- Author Info ----------
    data["author"] = None
    if author_elem:
        author_data = {}

        # Profile & image
        try:
            img_link = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user a.user-img"
            )
            author_data["profile"] = img_link.get_attribute("href")
            img_tag = img_link.find_element(By.TAG_NAME, "img")
            author_data["image"] = img_tag.get_attribute("src")
        except:
            author_data["profile"] = None
            author_data["image"] = None

        # Name
        author_data["name"] = author_elem.text.strip()

        # Verified
        try:
            tick_icon = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user i.tickIcon"
            )
            author_data["verified"] = True
        except:
            author_data["verified"] = False

        # Role
        try:
            role_elem = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user div.user_expert_level"
            )
            author_data["role"] = role_elem.text.strip()
        except:
            author_data["role"] = None

        data["author"] = author_data

    # ===============================

    # Overview Section
    overview_div = soup.find("div", id="blogId-132969")
    if overview_div:
        # Get overview paragraphs
        overview_sections = overview_div.find_all("div", id=lambda x: x and "wikkiContents_multi_ADP_undefined_ua_" in x)
        
        if overview_sections and len(overview_sections) > 0:
            overview_text = []
            for section in overview_sections[:3]:  # First 3 overview sections
                paragraphs = section.find_all("p")
                for p in paragraphs:
                    text = clean(p)
                    if text:
                        overview_text.append(text)
            
            data["overview_text"] = overview_text

    # ===============================
    # FAQs Section
    faq_section = soup.find("div", id="sectional-faqs-0")
    if faq_section:
        faqs = []
        question_divs = faq_section.find_all("div", id=lambda x: x and "0::" in x)
        
        for q_div in question_divs:
            question_text = clean(q_div)
            if question_text.startswith("Q:"):
                question_text = question_text.replace("Q:", "").strip()
            
            # Get answer
            answer_div = q_div.find_next("div", class_="_16f53f")
            if answer_div:
                answer_content = answer_div.find("div", class_="cmsAContent")
                if answer_content:
                    answer_text = clean(answer_content)
                    if answer_text.startswith("A:"):
                        answer_text = answer_text.replace("A:", "").strip()
                    
                    faqs.append({
                        "question": question_text,
                        "answer": answer_text
                    })
        
        data["faqs"] = faqs

    # ===============================
    # Table of Contents
    toc_div = soup.find("div", class_="_078b")
    if toc_div:
        toc_items = []
        toc_list = toc_div.find("ul", id="tocWrapper")
        if toc_list:
            for li in toc_list.find_all("li"):
                toc_items.append(clean(li))
        
        data["table_of_contents"] = toc_items

    # ===============================
    # MD vs MBBS: Highlights Section
    highlights_h2 = soup.find("h2", id="toc_section_1")
    if highlights_h2:
        data["highlights_heading"] = clean(highlights_h2)
        
        # Get description paragraph
        highlights_desc = highlights_h2.find_next("p")
        if highlights_desc:
            data["highlights_description"] = clean(highlights_desc)
        
        # Get highlights table
        table = highlights_h2.find_next("table")
        if table:
            highlights_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    highlights_data.append({
                        "parameter": clean(cols[0]),
                        "mbbs": clean(cols[1]),
                        "md": clean(cols[2])
                    })
            data["highlights_table"] = highlights_data
        
        # Get note paragraph
        note_p = table.find_next("p")
        if note_p and "Note:" in note_p.get_text():
            data["highlights_note"] = clean(note_p)
        
        # Get helpful links after table
        helpful_links_start = note_p.find_next("p") if note_p else table.find_next("p")
        if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
            helpful_links = []
            next_p = helpful_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["highlights_helpful_links"] = helpful_links

    # ===============================
    # Difference Between MD vs MBBS Section
    difference_h2 = soup.find("h2", id="toc_section_2")
    if difference_h2:
        data["difference_heading"] = clean(difference_h2)
        
        # What is MBBS?
        mbbs_heading = difference_h2.find_next("p", string=lambda x: x and "What is MBBS?" in x)
        if mbbs_heading:
            data["mbbs_definition_heading"] = clean(mbbs_heading)
            mbbs_desc = mbbs_heading.find_next("p")
            if mbbs_desc:
                data["mbbs_definition"] = clean(mbbs_desc)
                
                # What is MD?
                md_heading = mbbs_desc.find_next("p")
                if md_heading and "What is MD?" in md_heading.get_text():
                    data["md_definition_heading"] = clean(md_heading)
                    md_desc = md_heading.find_next("p")
                    if md_desc:
                        data["md_definition"] = clean(md_desc)
                        
                        # Get additional paragraphs about MD
                        additional_md_para = md_desc.find_next("p")
                        if additional_md_para:
                            data["md_additional_info"] = clean(additional_md_para)
                        
                        # Get suggested readings
                        suggested_readings_start = additional_md_para.find_next("p") if additional_md_para else None
                        if suggested_readings_start and suggested_readings_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
                            suggested_readings = []
                            next_p = suggested_readings_start.find_next_sibling()
                            while next_p and next_p.name == "p":
                                a_tag = next_p.find("a")
                                if a_tag:
                                    suggested_readings.append({
                                        "title": clean(a_tag),
                                        "url": a_tag.get("href")
                                    })
                                next_p = next_p.find_next_sibling()
                            
                            data["difference_suggested_readings"] = suggested_readings

    # ===============================
    # MD vs MBBS: Eligibility Section
    eligibility_h2 = soup.find("h2", id="toc_section_3")
    if eligibility_h2:
        data["eligibility_heading"] = clean(eligibility_h2)
        
        # Get description paragraphs
        desc_para1 = eligibility_h2.find_next("p")
        if desc_para1:
            data["eligibility_description1"] = clean(desc_para1)
        
        desc_para2 = desc_para1.find_next("p") if desc_para1 else None
        if desc_para2:
            data["eligibility_description2"] = clean(desc_para2)
        
        # Get eligibility table
        table = eligibility_h2.find_next("table")
        if table:
            eligibility_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    eligibility_data.append({
                        "parameter": clean(cols[0]),
                        "mbbs": clean(cols[1]),
                        "md": clean(cols[2])
                    })
            data["eligibility_table"] = eligibility_data
        
        # Get note paragraph
        note_p = table.find_next("p")
        if note_p and "Note:" in note_p.get_text():
            data["eligibility_note"] = clean(note_p)
        
        # Get helpful links
        helpful_links_start = note_p.find_next("p") if note_p else table.find_next("p")
        if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
            helpful_links = []
            next_p = helpful_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["eligibility_helpful_links"] = helpful_links

    # ===============================
    # MD vs MBBS: Entrance Exam Section
    entrance_h2 = soup.find("h2", id="toc_section_4")
    if entrance_h2:
        data["entrance_exam_heading"] = clean(entrance_h2)
        
        # Get description paragraph
        entrance_desc = entrance_h2.find_next("p")
        if entrance_desc:
            data["entrance_exam_description"] = clean(entrance_desc)
        
        # Get entrance exam table
        table = entrance_h2.find_next("table")
        if table:
            entrance_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    entrance_data.append({
                        "particular": clean(cols[0]),
                        "mbbs": clean(cols[1]),
                        "md": clean(cols[2])
                    })
            data["entrance_exam_table"] = entrance_data
        
        # Get note paragraph
        note_p = table.find_next("p")
        if note_p and "Note:" in note_p.get_text():
            data["entrance_exam_note"] = clean(note_p)
        
        # Get helpful links
        helpful_links_start = note_p.find_next("p") if note_p else table.find_next("p")
        if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
            helpful_links = []
            next_p = helpful_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    helpful_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["entrance_exam_helpful_links"] = helpful_links

    # ===============================
    # MD vs MBBS: Syllabus Section
    syllabus_h2 = soup.find("h2", id="toc_section_5")
    if syllabus_h2:
        data["syllabus_heading"] = clean(syllabus_h2)
        
        # Get description paragraphs
        desc_para1 = syllabus_h2.find_next("p")
        if desc_para1:
            data["syllabus_description1"] = clean(desc_para1)
        
        desc_para2 = desc_para1.find_next("p") if desc_para1 else None
        if desc_para2:
            data["syllabus_description2"] = clean(desc_para2)
        
        desc_para3 = desc_para2.find_next("p") if desc_para2 else None
        if desc_para3:
            data["syllabus_description3"] = clean(desc_para3)
        
        # Get syllabus table
        table = syllabus_h2.find_next("table")
        if table:
            syllabus_data = []
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header
                cols = row.find_all("td")
                if len(cols) >= 3:
                    # Extract list items from MBBS and MD columns
                    mbbs_items = []
                    md_items = []
                    
                    mbbs_ul = cols[1].find("ul")
                    if mbbs_ul:
                        for li in mbbs_ul.find_all("li"):
                            mbbs_items.append(clean(li))
                    
                    md_ul = cols[2].find("ul")
                    if md_ul:
                        for li in md_ul.find_all("li"):
                            md_items.append(clean(li))
                    
                    syllabus_data.append({
                        "semester": clean(cols[0]),
                        "mbbs_subjects": mbbs_items,
                        "md_subjects": md_items
                    })
            data["syllabus_table"] = syllabus_data
        
        # Get syllabus links
        syllabus_links_p = table.find_next("p")
        if syllabus_links_p:
            syllabus_links = []
            a_tags = syllabus_links_p.find_all("a")
            for a_tag in a_tags:
                syllabus_links.append({
                    "title": clean(a_tag),
                    "url": a_tag.get("href")
                })
            data["syllabus_links"] = syllabus_links
        
        # Get relevant links
        relevant_links_start = syllabus_links_p.find_next("p") if syllabus_links_p else table.find_next("p")
        if relevant_links_start and relevant_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
            relevant_links = []
            next_p = relevant_links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    relevant_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            data["syllabus_relevant_links"] = relevant_links

    # ===============================
    # MD vs MBBS: Top Colleges Section
    top_colleges_h2 = soup.find("h2", id="toc_section_6")
    if top_colleges_h2:
        data["top_colleges_heading"] = clean(top_colleges_h2)
        
        # Get description paragraph
        desc_para = top_colleges_h2.find_next("p")
        if desc_para:
            data["top_colleges_description"] = clean(desc_para)
        
        # Top MBBS Colleges Subsection
        mbbs_colleges_h3 = soup.find("h3", string=lambda x: x and "Top MBBS Colleges" in x)
        if mbbs_colleges_h3:
            data["mbbs_colleges_subheading"] = clean(mbbs_colleges_h3)
            
            # Get description
            mbbs_desc = mbbs_colleges_h3.find_next("p")
            if mbbs_desc:
                data["mbbs_colleges_description"] = clean(mbbs_desc)
            
            # Get MBBS colleges table
            mbbs_table = mbbs_colleges_h3.find_next("table")
            if mbbs_table:
                mbbs_colleges_data = []
                rows = mbbs_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_link = cols[0].find("a")
                        mbbs_colleges_data.append({
                            "college": clean(cols[0]),
                            "fees": clean(cols[1]),
                            "link": college_link.get("href") if college_link else None
                        })
                data["mbbs_colleges_table"] = mbbs_colleges_data
            
            # Get note paragraph
            note_p = mbbs_table.find_next("p")
            if note_p and "Note:" in note_p.get_text():
                data["mbbs_colleges_note"] = clean(note_p)
        
        # Top MD Colleges Subsection
        md_colleges_h3 = soup.find("h3", string=lambda x: x and "Top MD Colleges" in x)
        if md_colleges_h3:
            data["md_colleges_subheading"] = clean(md_colleges_h3)
            
            # Get description
            md_desc = md_colleges_h3.find_next("p")
            if md_desc:
                data["md_colleges_description"] = clean(md_desc)
            
            # Get MD colleges table
            md_table = md_colleges_h3.find_next("table")
            if md_table:
                md_colleges_data = []
                rows = md_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_link = cols[0].find("a")
                        md_colleges_data.append({
                            "college": clean(cols[0]),
                            "fees": clean(cols[1]),
                            "link": college_link.get("href") if college_link else None
                        })
                data["md_colleges_table"] = md_colleges_data
            
            # Get note paragraph
            note_p = md_table.find_next("p")
            if note_p and "Note:" in note_p.get_text():
                data["md_colleges_note"] = clean(note_p)
            
            # Get useful links
            useful_links_start = note_p.find_next("p") if note_p else md_table.find_next("p")
            if useful_links_start and useful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
                useful_links = []
                next_p = useful_links_start.find_next_sibling()
                while next_p and next_p.name == "p":
                    a_tag = next_p.find("a")
                    if a_tag:
                        useful_links.append({
                            "title": clean(a_tag),
                            "url": a_tag.get("href")
                        })
                    next_p = next_p.find_next_sibling()
                
                data["colleges_useful_links"] = useful_links

    # ===============================
    # MD vs MBBS: Jobs and Salary Section
    jobs_h2 = soup.find("h2", id="toc_section_7")
    if jobs_h2:
        data["jobs_salary_heading"] = clean(jobs_h2)
        
        # Get description paragraph
        jobs_desc = jobs_h2.find_next("p")
        if jobs_desc:
            data["jobs_salary_description"] = clean(jobs_desc)
        
        # MBBS Salary in India Subsection
        mbbs_salary_h3 = soup.find("h3", string=lambda x: x and "MBBS Salary in India" in x)
        if mbbs_salary_h3:
            data["mbbs_salary_subheading"] = clean(mbbs_salary_h3)
            
            # Get description
            mbbs_salary_desc = mbbs_salary_h3.find_next("p")
            if mbbs_salary_desc:
                data["mbbs_salary_description"] = clean(mbbs_salary_desc)
            
            # Get MBBS salary table
            mbbs_salary_table = mbbs_salary_h3.find_next("table")
            if mbbs_salary_table:
                mbbs_salary_data = []
                rows = mbbs_salary_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        mbbs_salary_data.append({
                            "job_profile": clean(cols[0]),
                            "salary": clean(cols[1])
                        })
                data["mbbs_salary_table"] = mbbs_salary_data
            
            # Get note paragraph
            note_p = mbbs_salary_table.find_next("p")
            if note_p and "Note:" in note_p.get_text():
                data["mbbs_salary_note"] = clean(note_p)
            
            # Get recommended links
            recommended_links_start = note_p.find_next("p") if note_p else mbbs_salary_table.find_next("p")
            if recommended_links_start and recommended_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
                recommended_links = []
                next_p = recommended_links_start.find_next_sibling()
                while next_p and next_p.name == "p":
                    a_tag = next_p.find("a")
                    if a_tag:
                        recommended_links.append({
                            "title": clean(a_tag),
                            "url": a_tag.get("href")
                        })
                    next_p = next_p.find_next_sibling()
                
                data["mbbs_salary_recommended_links"] = recommended_links
        
        # MD Salary in India Subsection
        md_salary_h3 = soup.find("h3", string=lambda x: x and "MD Salary in India" in x)
        if md_salary_h3:
            data["md_salary_subheading"] = clean(md_salary_h3)
            
            # Get description
            md_salary_desc = md_salary_h3.find_next("p")
            if md_salary_desc:
                data["md_salary_description"] = clean(md_salary_desc)
            
            # Get MD salary table
            md_salary_table = md_salary_h3.find_next("table")
            if md_salary_table:
                md_salary_data = []
                rows = md_salary_table.find_all("tr")
                for row in rows[1:]:  # Skip header
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        md_salary_data.append({
                            "job_profile": clean(cols[0]),
                            "salary": clean(cols[1])
                        })
                data["md_salary_table"] = md_salary_data
            
            # Get note paragraph
            note_p = md_salary_table.find_next("p")
            if note_p and "Note:" in note_p.get_text():
                data["md_salary_note"] = clean(note_p)
            
            # Get suggested reading
            suggested_reading_start = note_p.find_next("p") if note_p else md_salary_table.find_next("p")
            if suggested_reading_start and suggested_reading_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
                suggested_reading = []
                next_p = suggested_reading_start.find_next_sibling()
                while next_p and next_p.name == "p":
                    a_tag = next_p.find("a")
                    if a_tag:
                        suggested_reading.append({
                            "title": clean(a_tag),
                            "url": a_tag.get("href")
                        })
                    next_p = next_p.find_next_sibling()
                
                data["md_salary_suggested_reading"] = suggested_reading

    # ===============================
    # MD vs MBBS FAQs Section
    faqs_h2 = soup.find("h2", id="toc_section_8")
    if faqs_h2:
        data["faqs_section_heading"] = clean(faqs_h2)
        
        # Get all FAQ questions and answers
        faq_wrapper = soup.find("div", id="faqWrapper_last")
        if faq_wrapper:
            detailed_faqs = []
            question_paragraphs = faq_wrapper.find_all("p", class_="fQ")
            
            for q_p in question_paragraphs:
                question_text = clean(q_p)
                if question_text.startswith("Q."):
                    question_text = question_text.replace("Q.", "").strip()
                
                # Find answer
                answer_div = q_p.find_next("div", class_="fA")
                if answer_div:
                    answer_text = clean(answer_div)
                    
                    detailed_faqs.append({
                        "question": question_text,
                        "answer": answer_text
                    })
            
            data["detailed_faqs"] = detailed_faqs

    # ===============================
    # Explore More Exams Section
    exams_section = soup.find("div", id="ADP_Exam_recoWidget_undefined")
    if exams_section:
        exams_heading = exams_section.find("h2", class_="heading")
        if exams_heading:
            data["exams_heading"] = clean(exams_heading)
        
        # Get exam sliders
        exam_sliders = exams_section.find_all("div", class_="examSlider")
        if exam_sliders:
            exams_list = []
            for slider in exam_sliders:
                exam_name_div = slider.find("h2", class_="_2164")
                if exam_name_div:
                    exam_name = clean(exam_name_div)
                    
                    # Get exam dates
                    date_div = slider.find("div", class_="_760f")
                    exam_date = ""
                    if date_div:
                        strong_tag = date_div.find("strong")
                        if strong_tag:
                            exam_date = clean(strong_tag)
                    
                    # Get exam links
                    links = []
                    link_items = slider.find_all("li")
                    for li in link_items:
                        a_tag = li.find("a")
                        if a_tag:
                            links.append({
                                "title": clean(a_tag),
                                "url": a_tag.get("href")
                            })
                    
                    exams_list.append({
                        "exam_name": exam_name,
                        "date": exam_date,
                        "links": links
                    })
            
            data["explore_exams"] = exams_list

    # ===============================
    # Videos Section
    videos_section = soup.find("div", id="reelsWidget")
    if videos_section:
        videos_heading = videos_section.find("strong", class_="b5e4")
        if videos_heading:
            data["videos_heading"] = clean(videos_heading)
        
        # Get video thumbnails
        video_items = videos_section.find_all("li", class_="_7c2b")
        if video_items:
            videos_list = []
            for video in video_items:
                img_tag = video.find("img", class_="_97edf4")
                if img_tag:
                    video_title_div = video.find("div", class_="_4a7330")
                    video_title = clean(video_title_div) if video_title_div else ""
                    
                    videos_list.append({
                        "thumbnail": img_tag.get("src", ""),
                        "title": video_title
                    })
            
            data["videos"] = videos_list

    return data

def scrape_aiims_data(driver):
    driver.get(AIIMS_IN_INDIA)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    try:
        author_elem = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
            )
        )
    except:
        print("Author info not found in time.")
        author_elem = None

    data = {}

    # ---------- Course Name ----------
    try:
        course_name_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.flx-box.mA h1")
            )
        )
        data["title"] = course_name_elem.text.strip()
    except:
        data["title"] = None

    # ---------- Updated Date ----------
    try:
        updated_elem = driver.find_element(
            By.CSS_SELECTOR, "div.adp_blog div.blogdata_user span"
        )
        data["updated_on"] = updated_elem.text.strip()
    except:
        data["updated_on"] = None

    # ---------- Author Info ----------
    data["author"] = None
    if author_elem:
        author_data = {}

        # Profile & image
        try:
            img_link = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user a.user-img"
            )
            author_data["profile"] = img_link.get_attribute("href")
            img_tag = img_link.find_element(By.TAG_NAME, "img")
            author_data["image"] = img_tag.get_attribute("src")
        except:
            author_data["profile"] = None
            author_data["image"] = None

        # Name
        author_data["name"] = author_elem.text.strip()

        # Verified
        try:
            tick_icon = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user i.tickIcon"
            )
            author_data["verified"] = True
        except:
            author_data["verified"] = False

        # Role
        try:
            role_elem = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user div.user_expert_level"
            )
            author_data["role"] = role_elem.text.strip()
        except:
            author_data["role"] = None

        data["author"] = author_data
    # ===============================
    # Blog Summary Section
    summary_div = soup.find("div", id="blogSummary")
    if summary_div:
        data["blog_summary"] = clean(summary_div)

    # ===============================
    # Main Content Section
    main_content = soup.find("div", id="blogId-23925")
    if main_content:
        content_data = {}
        
        # Introduction paragraph
        intro_p = main_content.find("p")
        if intro_p:
            content_data["introduction"] = clean(intro_p)
        
        # Featured image
        img_caption = main_content.find("p", class_="_img-caption")
        if img_caption:
            content_data["featured_image_caption"] = clean(img_caption)
        
        # Main description paragraphs
        wikki_contents = main_content.find_all("div", class_="wikkiContents")
        description_paragraphs = []
        for wc in wikki_contents[:3]:  # Get first 3 content sections
            paragraphs = wc.find_all("p")
            for p in paragraphs:
                text = clean(p)
                if text and len(text) > 50:  # Filter out very short paragraphs
                    description_paragraphs.append(text)
        
        content_data["description_paragraphs"] = description_paragraphs
        
        data["main_content"] = content_data

    # ===============================
    # FAQs Section
    faq_section = soup.find("div", id="sectional-faqs-0")
    if faq_section:
        faqs = []
        question_divs = faq_section.find_all("div", id=lambda x: x and "0::" in x)
        
        for q_div in question_divs:
            question_text = clean(q_div)
            if question_text.startswith("Q:"):
                question_text = question_text.replace("Q:", "").strip()
            
            # Get answer
            answer_div = q_div.find_next("div", class_="_16f53f")
            if answer_div:
                answer_content = answer_div.find("div", class_="cmsAContent")
                if answer_content:
                    answer_text = clean(answer_content)
                    if answer_text.startswith("A:"):
                        answer_text = answer_text.replace("A:", "").strip()
                    
                    faqs.append({
                        "question": question_text,
                        "answer": answer_text
                    })
        
        data["faqs"] = faqs

    # ===============================
    # Table of Contents
    toc_div = soup.find("div", class_="_078b")
    if toc_div:
        toc_data = {}
        
        toc_heading = toc_div.find("div")
        if toc_heading:
            toc_data["heading"] = clean(toc_heading)
        
        toc_items = []
        toc_list = toc_div.find("ul", id="tocWrapper")
        if toc_list:
            for li in toc_list.find_all("li"):
                item_data = {
                    "text": clean(li),
                    "section_id": li.get("data-scrol", "")
                }
                toc_items.append(item_data)
        
        toc_data["items"] = toc_items
        data["table_of_contents"] = toc_data

    # ===============================
    # NIRF Ranking 2025 Section
    nirf_h2 = soup.find("h2", id="toc_section_1")
    if nirf_h2:
        nirf_data = {}
        nirf_data["heading"] = clean(nirf_h2)
        
        # Get description paragraphs
        paragraphs = []
        next_elem = nirf_h2.find_next_sibling()
        while next_elem and next_elem.name == "p":
            paragraphs.append(clean(next_elem))
            next_elem = next_elem.find_next_sibling()
        
        nirf_data["description"] = paragraphs
        
        # Get related links
        links_start = None
        for p in paragraphs:
            if "Also Read:" in p or "Read More:" in p:
                links_start = p
                break
        
        if links_start:
            related_links = []
            next_p = links_start.find_next_sibling()
            while next_p and next_p.name == "p":
                a_tag = next_p.find("a")
                if a_tag:
                    related_links.append({
                        "title": clean(a_tag),
                        "url": a_tag.get("href")
                    })
                next_p = next_p.find_next_sibling()
            
            nirf_data["related_links"] = related_links
        
        data["nirf_ranking_2025"] = nirf_data

    # ===============================
    # List of AIIMS in India Section
    aiims_list_h2 = soup.find("h2", id="toc_section_2")
    if aiims_list_h2:
        aiims_list_data = {}
        aiims_list_data["heading"] = clean(aiims_list_h2)
        
        # Get description paragraph
        desc_p = aiims_list_h2.find_next("p")
        if desc_p:
            aiims_list_data["description"] = clean(desc_p)
        
        # Get AIIMS table
        table = aiims_list_h2.find_next("table")
        if table:
            aiims_data = []
            rows = table.find_all("tr")
            
            # Extract headers
            headers = []
            if rows:
                header_row = rows[0]
                th_cells = header_row.find_all("th")
                for th in th_cells:
                    headers.append(clean(th))
            
            # Extract data rows
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 5:  # Ensure we have all 5 columns
                    aiims_info = {
                        "name": clean(cells[0]),
                        "establishment_year": clean(cells[1]),
                        "nirf_2025_rank": clean(cells[2]),
                        "nirf_2024_rank": clean(cells[3]),
                        "nirf_2023_rank": clean(cells[4])
                    }
                    
                    # Extract link if available
                    name_link = cells[0].find("a")
                    if name_link:
                        aiims_info["link"] = name_link.get("href")
                    
                    aiims_data.append(aiims_info)
            
            aiims_list_data["table_headers"] = headers
            aiims_list_data["aiims_list"] = aiims_data
        
        # Get analysis after table
        analysis_div = table.find_next("div")
        if analysis_div:
            aiims_list_data["analysis"] = clean(analysis_div)
        
        # Get related links
        related_links_start = analysis_div.find_next("div") if analysis_div else table.find_next("div")
        if related_links_start:
            related_links = []
            ul_tag = related_links_start.find("ul")
            if ul_tag:
                li_tags = ul_tag.find_all("li")
                for li in li_tags:
                    a_tag = li.find("a")
                    if a_tag:
                        related_links.append({
                            "title": clean(a_tag),
                            "url": a_tag.get("href")
                        })
            
            aiims_list_data["related_links"] = related_links
        
        data["aiims_list_india"] = aiims_list_data

    # ===============================
    # Under-development AIIMS Section
    under_dev_h2 = soup.find("h2", id="toc_section_3")
    if under_dev_h2:
        under_dev_data = {}
        under_dev_data["heading"] = clean(under_dev_h2)
        
        # Get description paragraph
        desc_p = under_dev_h2.find_next("p")
        if desc_p:
            under_dev_data["description"] = clean(desc_p)
        
        # Get under-development table
        table = under_dev_h2.find_next("table")
        if table:
            under_dev_list = []
            rows = table.find_all("tr")
            
            # Extract headers
            headers = []
            if rows:
                header_row = rows[0]
                th_cells = header_row.find_all("th")
                for th in th_cells:
                    headers.append(clean(th))
            
            # Extract data rows
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    under_dev_info = {
                        "name": clean(cells[0]),
                        "state": clean(cells[1]),
                        "status": clean(cells[2])
                    }
                    under_dev_list.append(under_dev_info)
            
            under_dev_data["table_headers"] = headers
            under_dev_data["under_development_list"] = under_dev_list
        
        # Get related links
        related_links_p = table.find_next("p")
        if related_links_p:
            a_tag = related_links_p.find("a")
            if a_tag:
                under_dev_data["related_link"] = {
                    "title": clean(a_tag),
                    "url": a_tag.get("href")
                }
        
        data["under_development_aiims"] = under_dev_data

    # ===============================
    # Courses Offered Section
    courses_h2 = soup.find("h2", id="toc_section_4")
    if courses_h2:
        courses_data = {}
        courses_data["heading"] = clean(courses_h2)
        
        # Get description paragraph
        desc_p = courses_h2.find_next("p")
        if desc_p:
            courses_data["description"] = clean(desc_p)
        
        # Get courses table
        table = courses_h2.find_next("table")
        if table:
            courses_list = []
            rows = table.find_all("tr")
            
            # Extract data rows
            for row in rows:
                cells = row.find_all(["th", "td"])
                if len(cells) >= 3:
                    course_info = {
                        "undergraduate": clean(cells[0]),
                        "postgraduate": clean(cells[1]),
                        "super_specialization": clean(cells[2])
                    }
                    courses_list.append(course_info)
            
            courses_data["courses_table"] = courses_list
        
        # Get related links
        related_links_p = table.find_next("p")
        if related_links_p:
            a_tag = related_links_p.find("a")
            if a_tag:
                courses_data["related_link"] = {
                    "title": clean(a_tag),
                    "url": a_tag.get("href")
                }
        
        data["courses_offered"] = courses_data

    # ===============================
    # Admission Process Section
    admission_h2 = soup.find("h2", id="toc_section_5")
    if admission_h2:
        admission_data = {}
        admission_data["heading"] = clean(admission_h2)
        
        # Get description paragraph
        desc_p = admission_h2.find_next("p")
        if desc_p:
            admission_data["description"] = clean(desc_p)
        
        # Get admission table
        table = admission_h2.find_next("table")
        if table:
            admission_process = []
            rows = table.find_all("tr")
            
            # Extract headers
            headers = []
            if rows:
                header_row = rows[0]
                th_cells = header_row.find_all("th")
                for th in th_cells:
                    headers.append(clean(th))
            
            # Extract data rows
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    process_info = {
                        "course": clean(cells[0]),
                        "entrance_test": clean(cells[1])
                    }
                    
                    # Extract links if available
                    course_links = cells[0].find_all("a")
                    entrance_links = cells[1].find_all("a")
                    
                    if course_links:
                        process_info["course_links"] = [link.get("href") for link in course_links]
                    if entrance_links:
                        process_info["entrance_links"] = [link.get("href") for link in entrance_links]
                    
                    admission_process.append(process_info)
            
            admission_data["table_headers"] = headers
            admission_data["admission_process"] = admission_process
        
        data["admission_process"] = admission_data

    # ===============================
    # Fee Structure Section
    fees_h2 = soup.find("h2", id="toc_section_6")
    if fees_h2:
        fees_data = {}
        fees_data["heading"] = clean(fees_h2)
        
        # Get description paragraph
        desc_p = fees_h2.find_next("p")
        if desc_p:
            fees_data["description"] = clean(desc_p)
        
        # Get fee structure table
        table = fees_h2.find_next("table")
        if table:
            fee_structure = []
            rows = table.find_all("tr")
            
            # Extract data rows
            current_aiims = ""
            for row in rows:
                cells = row.find_all(["th", "td"])
                
                if len(cells) == 1:
                    # This might be a rowspan row with just AIIMS name
                    current_aiims = clean(cells[0])
                elif len(cells) >= 3:
                    fee_info = {
                        "aiims": current_aiims if current_aiims else clean(cells[0]),
                        "course": clean(cells[1]) if len(cells) >= 3 else clean(cells[0]),
                        "annual_fee": clean(cells[2]) if len(cells) >= 3 else clean(cells[1])
                    }
                    
                    # Extract links if available
                    course_link = cells[1].find("a") if len(cells) >= 3 else cells[0].find("a")
                    if course_link:
                        fee_info["course_link"] = course_link.get("href")
                    
                    fee_structure.append(fee_info)
            
            fees_data["fee_structure"] = fee_structure
        
        data["fee_structure"] = fees_data

    # ===============================
    # Seat Intake Section
    seats_h2 = soup.find("h2", id="toc_section_7")
    if seats_h2:
        seats_data = {}
        seats_data["heading"] = clean(seats_h2)
        
        # Get description paragraph
        desc_p = seats_h2.find_next("p")
        if desc_p:
            seats_data["description"] = clean(desc_p)
        
        # Get seat intake table
        table = seats_h2.find_next("table")
        if table:
            seat_intake = []
            rows = table.find_all("tr")
            
            # Extract headers
            headers = []
            if rows:
                header_row = rows[0]
                th_cells = header_row.find_all("th")
                for th in th_cells:
                    headers.append(clean(th))
            
            # Extract data rows
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    seat_info = {
                        "institute": clean(cells[0]),
                        "seats": clean(cells[1])
                    }
                    seat_intake.append(seat_info)
            
            seats_data["table_headers"] = headers
            seats_data["seat_intake"] = seat_intake
        
        data["seat_intake"] = seats_data

    # ===============================
    # NEET Cutoff Section
    cutoff_h2 = soup.find("h2", id="toc_section_8")
    if cutoff_h2:
        cutoff_data = {}
        cutoff_data["heading"] = clean(cutoff_h2)
        
        # Get description paragraph
        desc_p = cutoff_h2.find_next("p")
        if desc_p:
            cutoff_data["description"] = clean(desc_p)
        
        # Get cutoff table
        table = cutoff_h2.find_next("table")
        if table:
            cutoff_info = []
            rows = table.find_all("tr")
            
            # Extract headers
            headers = []
            if rows:
                header_row = rows[0]
                th_cells = header_row.find_all("th")
                for th in th_cells:
                    headers.append(clean(th))
            
            # Extract data rows
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    cutoff_item = {
                        "aiims_institute": clean(cells[0]),
                        "neet_2024_cutoff_rank": clean(cells[1])
                    }
                    cutoff_info.append(cutoff_item)
            
            cutoff_data["table_headers"] = headers
            cutoff_data["cutoff_info"] = cutoff_info
        
        # Get concluding paragraph
        concl_p = table.find_next("p")
        if concl_p:
            cutoff_data["conclusion"] = clean(concl_p)
        
        # Get related links
        related_links_start = concl_p.find_next("p") if concl_p else table.find_next("p")
        if related_links_start and ("Read More:" in related_links_start.get_text() or "Also Read:" in related_links_start.get_text()):
            related_links = []
            ul_tag = related_links_start.find_next("ul")
            if ul_tag:
                li_tags = ul_tag.find_all("li")
                for li in li_tags:
                    a_tag = li.find("a")
                    if a_tag:
                        related_links.append({
                            "title": clean(a_tag),
                            "url": a_tag.get("href")
                        })
            
            cutoff_data["related_links"] = related_links
        
        data["neet_cutoff"] = cutoff_data

    # ===============================
    # Explore Exams Section
    exams_section = soup.find("div", id="ADP_Exam_recoWidget_undefined")
    if exams_section:
        exams_data = {}
        
        # Get heading
        heading = exams_section.find("h2", class_="heading")
        if heading:
            exams_data["heading"] = clean(heading)
        
        # Get exam sliders
        exam_sliders = exams_section.find_all("div", class_="examSlider")
        if exam_sliders:
            exams_list = []
            for slider in exam_sliders:
                exam_name_div = slider.find("h2", class_="_2164")
                if exam_name_div:
                    exam_info = {
                        "exam_name": clean(exam_name_div)
                    }
                    
                    # Get exam link
                    exam_link = exam_name_div.find_parent("a")
                    if exam_link:
                        exam_info["exam_link"] = exam_link.get("href")
                    
                    # Get exam date
                    date_div = slider.find("div", class_="_760f")
                    if date_div:
                        strong_tag = date_div.find("strong")
                        if strong_tag:
                            exam_info["date_title"] = clean(strong_tag)
                        
                        date_span = date_div.find("p", class_="c1c4")
                        if date_span:
                            exam_info["date"] = clean(date_span)
                    
                    # Get quick links
                    quick_links = []
                    link_items = slider.find_all("li")
                    for li in link_items:
                        a_tag = li.find("a")
                        if a_tag:
                            quick_links.append({
                                "title": clean(a_tag),
                                "url": a_tag.get("href")
                            })
                    
                    exam_info["quick_links"] = quick_links
                    exams_list.append(exam_info)
            
            exams_data["exams"] = exams_list
        
        data["explore_exams"] = exams_data

    # ===============================
    # Comments Section
    comments_section = soup.find("div", id="multiTag_comments")
    if comments_section:
        comments_data = {}
        
        # Get comments heading
        heading_div = comments_section.find("h2", class_="askQry-titl")
        if heading_div:
            comments_data["heading"] = clean(heading_div)
            # Get comment count
            count_span = heading_div.find_next("p")
            if count_span:
                comments_data["count"] = clean(count_span)
        
        # Get individual comments
        comment_divs = comments_section.find_all("div", class_="qstn-div")
        if comment_divs:
            comments_list = []
            for comment_div in comment_divs:
                comment_info = {}
                
                # Get user info
                user_div = comment_div.find("div", class_="qstn-det")
                if user_div:
                    user_link = user_div.find("a", class_="ana--comments_user")
                    if user_link:
                        # Check for user image or initial
                        img_tag = user_link.find("img")
                        if img_tag:
                            comment_info["user_image"] = img_tag.get("src", "")
                        else:
                            initial_div = user_link.find("p", class_="user-initial")
                            if initial_div:
                                comment_info["user_initial"] = clean(initial_div)
                        
                        comment_info["user_profile"] = user_link.get("href", "")
                    
                    # Get user details
                    user_details = user_div.find("div", class_="ana--comments_userdtls")
                    if user_details:
                        name_link = user_details.find("a", class_="blackLink")
                        if name_link:
                            comment_info["user_name"] = clean(name_link)
                        
                        time_p = user_details.find("p", class_="ana--comments_time")
                        if time_p:
                            comment_info["timestamp"] = clean(time_p)
                
                # Get comment text
                comment_content = comment_div.find("div", class_="ana--comments_q")
                if comment_content:
                    text_div = comment_content.find("div", class_="commentContent")
                    if text_div:
                        comment_info["comment"] = clean(text_div)
                
                # Get replies
                replies_div = comment_div.find("div", class_="ana--comments_answercol")
                if replies_div:
                    reply_divs = replies_div.find_all("div", class_="ana--comments_ans")
                    if reply_divs:
                        replies_list = []
                        for reply_div in reply_divs:
                            reply_info = {}
                            
                            # Get reply user info
                            reply_user_div = reply_div.find("div", class_="qstn-det")
                            if reply_user_div:
                                reply_user_link = reply_user_div.find("a", class_="ana--comments_user")
                                if reply_user_link:
                                    reply_initial = reply_user_link.find("p", class_="user-initial")
                                    if reply_initial:
                                        reply_info["user_initial"] = clean(reply_initial)
                                    
                                    reply_info["user_profile"] = reply_user_link.get("href", "")
                                
                                # Get reply user details
                                reply_details = reply_user_div.find("div", class_="ana--comments_userdtls")
                                if reply_details:
                                    reply_name = reply_details.find("a", class_="blackLink")
                                    if reply_name:
                                        reply_info["user_name"] = clean(reply_name)
                                    
                                    reply_time = reply_details.find("p", class_="ana--comments_time")
                                    if reply_time:
                                        reply_info["timestamp"] = clean(reply_time)
                            
                            # Get reply text
                            reply_content = reply_div.find("div", class_="ana--comments_anscol")
                            if reply_content:
                                reply_text = reply_content.find("div", class_="commentContent")
                                if reply_text:
                                    reply_info["reply"] = clean(reply_text)
                            
                            replies_list.append(reply_info)
                        
                        comment_info["replies"] = replies_list
                
                comments_list.append(comment_info)
            
            comments_data["comments"] = comments_list
        
        data["comments"] = comments_data

    # ===============================
    # Download and Share Section
    download_div = soup.find("div", class_="dnld-btn")
    if download_div:
        download_data = {}
        
        download_text = download_div.find("p")
        if download_text:
            download_data["text"] = clean(download_text)
        
        download_link = download_div.find("a", class_="button--orange")
        if download_link:
            download_data["button_text"] = clean(download_link)
            download_data["action"] = download_link.get("href", "")
        
        data["download_section"] = download_data

    # ===============================
    # Social Sharing Section
    share_div = soup.find("div", class_="shareWidget-btm")
    if share_div:
        share_data = {}
        
        share_text = share_div.find("span", class_="sharethis")
        if share_text:
            share_data["heading"] = clean(share_text)
        
        # Get social media links
        social_links = []
        social_band = share_div.find("ul", class_="sharing-band-list")
        if social_band:
            li_tags = social_band.find_all("li")
            for li in li_tags[1:]:  # Skip the first li which contains "Share this" text
                a_tag = li.find("a")
                if a_tag:
                    platform_info = {
                        "url": a_tag.get("href", ""),
                        "aria_label": a_tag.get("aria-label", "")
                    }
                    
                    # Determine platform from icon class
                    icon = a_tag.find("i")
                    if icon:
                        class_name = icon.get("class", "")
                        if "facebook" in class_name:
                            platform_info["platform"] = "facebook"
                        elif "twitter" in class_name:
                            platform_info["platform"] = "twitter"
                        elif "linkedin" in class_name:
                            platform_info["platform"] = "linkedin"
                        elif "email" in class_name:
                            platform_info["platform"] = "email"
                    
                    social_links.append(platform_info)
        
        share_data["social_links"] = social_links
        data["social_sharing"] = share_data

    # ===============================
    # Feedback Section
    feedback_div = soup.find("div", id="feedbackSection")
    if feedback_div:
        feedback_data = {}
        
        # Get feedback image
        feedback_img = feedback_div.find("img")
        if feedback_img:
            feedback_data["image_src"] = feedback_img.get("src", "")
        
        # Get feedback heading
        heading = feedback_div.find("h2", class_="so-widget-heading")
        if heading:
            feedback_data["heading"] = clean(heading)
        
        # Get feedback text
        text = feedback_div.find("p", class_="fdbkTxt")
        if text:
            feedback_data["text"] = clean(text)
        
        # Get rating stars
        rating_stars = feedback_div.find_all("span", class_="rating-icon-wrpr")
        if rating_stars:
            feedback_data["rating_stars"] = len(rating_stars)
        
        data["feedback_section"] = feedback_data

    return data

def scrape_alternative_mbbs(driver):
   
    # Get the page content
    driver.get(MBBS_ALTERNATIVE)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Initialize data structure
    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "description": "",
        "useful_links": [],
        "table_of_contents": [],
        "sections": [],
        "faqs": []
    }
    
    # ---------- Get Author Info using Selenium ----------
    try:
        author_elem = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
            )
        )
    except:
        print("Author info not found in time.")
        author_elem = None
    
    # ---------- Course Name ----------
    try:
        course_name_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.flx-box.mA h1")
            )
        )
        data["title"] = course_name_elem.text.strip()
    except:
        data["title"] = None
    
    # ---------- Updated Date ----------
    try:
        updated_elem = driver.find_element(
            By.CSS_SELECTOR, "div.adp_blog div.blogdata_user span"
        )
        data["updated_on"] = updated_elem.text.strip()
    except:
        data["updated_on"] = None
    
    # ---------- Author Info ----------
    if author_elem:
        author_data = {}

        # Profile & image
        try:
            img_link = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user a.user-img"
            )
            author_data["profile"] = img_link.get_attribute("href")
            img_tag = img_link.find_element(By.TAG_NAME, "img")
            author_data["image"] = img_tag.get_attribute("src")
        except:
            author_data["profile"] = None
            author_data["image"] = None

        # Name
        author_data["name"] = author_elem.text.strip()

        # Verified
        try:
            tick_icon = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user i.tickIcon"
            )
            author_data["verified"] = True
        except:
            author_data["verified"] = False

        # Role
        try:
            role_elem = driver.find_element(
                By.CSS_SELECTOR, "div.adp_blog div.adp_user div.user_expert_level"
            )
            author_data["role"] = role_elem.text.strip()
        except:
            author_data["role"] = None

        data["author"] = author_data
    else:
        data["author"] = None
    
    # ---------- Continue with BeautifulSoup scraping for content ----------
    
    # 1️⃣ Course Description and Useful Links
    desc_elem = soup.find(id="wikkiContents_multi_ADP_undefined_ua_0")
    if desc_elem:
        description_texts = []
        for p in desc_elem.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                description_texts.append(text)
            for a in p.find_all("a", href=True):
                href = a["href"]
                if href not in data["useful_links"]:
                    data["useful_links"].append(href)
        data["description"] = "\n".join(description_texts)
    
    # 2️⃣ Table of Contents
    toc_items = soup.select("ul#tocWrapper li")
    if toc_items:
        data["table_of_contents"] = [li.get_text(strip=True) for li in toc_items]
    
    # 3️⃣ Sections (h2 + content + tables)
    # Get all wikkiContents divs
    section_containers = soup.find_all("div", class_="wikkiContents")
    
    for container in section_containers:
        section_data = {}
        
        # Check if it's a section with h2 (not FAQ section)
        h2 = container.find("h2")
        if h2 and h2.get("id", "").startswith("toc_section_"):
            section_data["title"] = h2.get_text(strip=True)
            
            # Get all content excluding the h2 itself
            content_parts = []
            
            # Get paragraphs after h2
            for elem in container.find_all(["p", "div"]):
                # Skip the h2 element
                if elem.name == "h2":
                    continue
                
                # Get text from paragraph
                if elem.name == "p":
                    text = elem.get_text(strip=True)
                    if text and not text.startswith("Useful Links:") and not text.startswith("Suggested readings:"):
                        content_parts.append(text)
                
                # Get text from div (content divs)
                elif elem.name == "div" and not elem.get("class"):
                    text = elem.get_text(strip=True)
                    if text:
                        content_parts.append(text)
            
            section_data["content"] = "\n".join(content_parts)
            
            # Extract tables in this section
            tables_data = []
            for table in container.find_all("table"):
                table_rows = []
                for row in table.find_all("tr"):
                    cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                    if cells:
                        table_rows.append(cells)
                if table_rows:
                    tables_data.append(table_rows)
            section_data["tables"] = tables_data
            
            # Add suggested links if present
            suggested_links = []
            for p in container.find_all("p"):
                if "Suggested readings:" in p.get_text() or "Suggested Reading:" in p.get_text():
                    for a in p.find_all("a", href=True):
                        suggested_links.append(a["href"])
            if suggested_links:
                section_data["suggested_links"] = suggested_links
            
            data["sections"].append(section_data)
    
    # 4️⃣ FAQ Section (special handling)
    faq_section = soup.find("h2", id="toc_section_8")
    if faq_section:
        faq_container = faq_section.find_parent("div", class_="faqWrapper") or faq_section.find_parent("div", class_="wikkiContents")
        
        if faq_container:
            faq_data = {
                "title": faq_section.get_text(strip=True),
                "faqs": []
            }
            
            # Extract individual FAQ Q&A pairs
            faq_questions = faq_container.find_all(class_="fQ")
            
            for q in faq_questions:
                question_text = q.get_text(strip=True).replace("Q.", "").strip()
                question_id = q.find("strong").get("id", "") if q.find("strong") else ""
                
                # Find corresponding answer
                if question_id:
                    answer_id = question_id.replace("faq_q", "faq_a")
                    answer_div = faq_container.find("div", id=answer_id)
                    
                    if answer_div:
                        answer_content = []
                        tables_data = []
                        
                        # Extract text content
                        for elem in answer_div.find_all(["p", "ul", "table"]):
                            if elem.name == "p":
                                text = elem.get_text(strip=True)
                                if text and not text.startswith("A."):
                                    answer_content.append(text)
                            elif elem.name == "ul":
                                list_items = [li.get_text(strip=True) for li in elem.find_all("li")]
                                if list_items:
                                    answer_content.append("\n".join([f"• {item}" for item in list_items]))
                            elif elem.name == "table":
                                table_rows = []
                                for row in elem.find_all("tr"):
                                    cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                                    if cells:
                                        table_rows.append(cells)
                                if table_rows:
                                    tables_data.append(table_rows)
                        
                        faq_entry = {
                            "question": question_text,
                            "answer": "\n".join(answer_content),
                            "tables": tables_data
                        }
                        
                        faq_data["faqs"].append(faq_entry)
            
            data["sections"].append(faq_data)
    
    # 5️⃣ Additional FAQs from other sections
    sectional_faqs = soup.find("div", class_="sectional-faqs")
    if sectional_faqs:
        faq_listeners = sectional_faqs.find_all(class_="listener")
        
        for i in range(0, len(faq_listeners), 2):
            if i + 1 < len(faq_listeners):
                question_elem = faq_listeners[i]
                answer_elem = faq_listeners[i + 1]
                
                # Extract question
                question_spans = question_elem.find_all("span")
                question = question_spans[1].get_text(strip=True) if len(question_spans) > 1 else question_elem.get_text(strip=True).replace("Q:", "").strip()
                
                # Extract answer
                answer_content = answer_elem.find("div", class_="cmsAContent")
                if answer_content:
                    answer_text = answer_content.get_text(strip=True).replace("A:", "").strip()
                    
                    # Extract tables from answer
                    tables_data = []
                    for table in answer_content.find_all("table"):
                        table_rows = []
                        for row in table.find_all("tr"):
                            cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                            if cells:
                                table_rows.append(cells)
                        if table_rows:
                            tables_data.append(table_rows)
                    
                    data["faqs"].append({
                        "question": question,
                        "answer": answer_text,
                        "tables": tables_data
                    })
    
    return data

def scrape_neet_page_corrected(driver):
    driver.get(NEET_UG_2024)
    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "description": "",
        "latest_news": [],
        "table_of_contents": [],
        "sections": [],
        "faqs": []
    }
    
    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # ---------- Get Author Info ----------
    title = soup.find("div",class_="exam_wrap")
    h1 = title.find("h1").text.strip()
    data["title"]=h1
    try:
        author_section = soup.find("div", class_="ppBox")
        if author_section:
            author_data = {}
            
            # Author name
            author_name = author_section.find("a", href=lambda x: x and "author" in x)
            if author_name:
                author_data["name"] = author_name.get_text(strip=True)
                author_data["profile"] = author_name["href"]
            
            # Author image
            img_tag = author_section.find("img", class_="ePPImg")
            if img_tag:
                author_data["image"] = img_tag["src"]
            
            # Author role and verification
            role_text = ""
            role_elem = author_section.find("p", class_="ePPDetail")
            if role_elem:
                role_text = role_elem.get_text(strip=True)
                # Extract role
                if "By" in role_text and "," in role_text:
                    role_parts = role_text.split(",")
                    if len(role_parts) > 1:
                        author_data["role"] = role_parts[1].strip()
            
            # Verified status
            tick_icon = author_section.find("i", class_="tickIcon")
            author_data["verified"] = tick_icon is not None
            
            data["author"] = author_data
    except Exception as e:
        print(f"Error extracting author info: {e}")
        data["author"] = None
    
    # ---------- Get Updated Date ----------
    try:
        updated_elem = soup.find("div", class_="updatedOn")
        if updated_elem:
            span = updated_elem.find("span")
            if span:
                data["updated_on"] = span.get_text(strip=True).replace("Updated on", "").strip()
    except:
        data["updated_on"] = None
    
    # ---------- Get Description/Intro Section ----------
    try:
        intro_section = soup.find("div", id="wikkiContents_homepage__0")
        if intro_section:
            description_texts = []
            
            # Get only the first few paragraphs (before "Latest News:")
            for p in intro_section.find_all("p"):
                text = p.get_text(strip=True)
                if text and "Latest News:" not in text:
                    description_texts.append(text)
                elif "Latest News:" in text:
                    # Stop at latest news
                    break
            
            data["description"] = "\n".join(description_texts)
            
            # Get latest news
            news_section = intro_section.find("ul")
            if news_section:
                for li in news_section.find_all("li"):
                    a_tag = li.find("a")
                    if a_tag:
                        news_item = {
                            "title": a_tag.get("title", ""),
                            "link": a_tag.get("href", ""),
                            "text": a_tag.get_text(strip=True)
                        }
                        data["latest_news"].append(news_item)
    except Exception as e:
        print(f"Error extracting description: {e}")
    
    # ---------- Get Table of Contents ----------
    try:
        toc_wrapper = soup.find("ul", id="tocWrapper")
        if toc_wrapper:
            toc_items = toc_wrapper.find_all("li")
            for item in toc_items:
                text = item.get_text(strip=True)
                if text and text not in data["table_of_contents"]:
                    data["table_of_contents"].append(text)
    except Exception as e:
        print(f"Error extracting table of contents: {e}")
    
    # ---------- Get All Main Sections ----------
    try:
        # Find all sectionalWrapperClass divs that contain sections
        sectional_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
        
        for wrapper in sectional_wrappers:
            # Look for h2Container within wrapper
            h2_container = wrapper.find("div", class_="h2Container")
            if h2_container:
                h2 = h2_container.find("h2")
                if h2:
                    section_data = {
                        "title": h2.get_text(strip=True),
                        "content": "",
                        "tables": [],
                        "subsections": []
                    }
                    
                    # Find the content after h2
                    # Look for wikkiContents div after h2
                    content_div = wrapper.find("div", class_="wikkiContents")
                    if content_div:
                        content_parts = []
                        current_subsection = None
                        
                        # Process all elements in content
                        for elem in content_div.find_all(["p", "h3", "ul", "table", "iframe", "div"]):
                            # Skip unwanted divs
                            if elem.name == "div" and elem.get("class") and any(cls in ["showWikiReadLess"] for cls in elem.get("class")):
                                continue
                            
                            if elem.name == "p":
                                text = elem.get_text(strip=True)
                                if text and not text.startswith("Also Read:"):
                                    content_parts.append(text)
                            
                            elif elem.name == "h3":
                                # This is a subsection
                                subsection_text = elem.get_text(strip=True)
                                if subsection_text:
                                    if current_subsection:
                                        section_data["subsections"].append(current_subsection)
                                    current_subsection = {
                                        "title": subsection_text,
                                        "content": ""
                                    }
                            
                            elif elem.name == "ul":
                                list_items = []
                                for li in elem.find_all("li"):
                                    li_text = li.get_text(strip=True)
                                    if li_text:
                                        list_items.append(f"• {li_text}")
                                if list_items:
                                    list_text = "\n".join(list_items)
                                    if current_subsection:
                                        current_subsection["content"] += f"\n{list_text}"
                                    else:
                                        content_parts.append(list_text)
                            
                            elif elem.name == "table":
                                # Extract table data
                                table_data = extract_table_data(elem)
                                if table_data:
                                    section_data["tables"].append(table_data)
                            
                            elif elem.name == "iframe":
                                video_src = elem.get("src", "")
                                if video_src:
                                    section_data["video_link"] = video_src
                        
                        # Add the last subsection if exists
                        if current_subsection:
                            section_data["subsections"].append(current_subsection)
                        
                        section_data["content"] = "\n".join(content_parts)
                        
                        data["sections"].append(section_data)
    except Exception as e:
        print(f"Error extracting sections: {e}")
        import traceback
        traceback.print_exc()
    
    # ---------- Get All FAQs ----------
    try:
        # Extract FAQs from all FAQ sections
        faq_sections = soup.find_all("div", class_="sectional-faqs")
        
        for faq_section in faq_sections:
            # Get all question-answer pairs
            faq_items = faq_section.find_all("div", class_="listener")
            
            for item in faq_items:
                # Extract question
                question_elem = item.find("strong", class_="flx-box")
                if question_elem:
                    # Get question text properly
                    question_spans = question_elem.find_all("span")
                    if len(question_spans) >= 2:
                        question_text = question_spans[1].get_text(strip=True)
                    else:
                        # Try to extract Q: from text
                        full_text = question_elem.get_text(strip=True)
                        if "Q:" in full_text:
                            question_text = full_text.split("Q:", 1)[1].strip()
                        else:
                            question_text = full_text
                    
                    # Find answer div
                    answer_div = item.find_next_sibling("div", class_="_16f53f")
                    if answer_div:
                        answer_content = answer_div.find("div", class_="wikkiContents")
                        if answer_content:
                            # Extract answer text
                            answer_text_div = answer_content.find("div", class_="_843b17")
                            if answer_text_div:
                                answer_text = ""
                                answer_div_content = answer_text_div.find("div")
                                
                                if answer_div_content:
                                    # Extract paragraphs
                                    for p in answer_div_content.find_all("p"):
                                        p_text = p.get_text(strip=True)
                                        if p_text and not p_text.startswith("A:"):
                                            answer_text += p_text + "\n"
                                    
                                    # Extract lists
                                    for ul in answer_div_content.find_all("ul"):
                                        list_items = []
                                        for li in ul.find_all("li"):
                                            li_text = li.get_text(strip=True)
                                            if li_text:
                                                list_items.append(f"• {li_text}")
                                        if list_items:
                                            answer_text += "\n".join(list_items) + "\n"
                                    
                                    # If no paragraphs found, get all text
                                    if not answer_text:
                                        answer_text = answer_div_content.get_text(strip=True)
                                else:
                                    # Fallback to entire text
                                    answer_text = answer_text_div.get_text(strip=True).replace("A:", "").replace("A:&nbsp;", "").strip()
                                
                                # Extract tables from answer
                                tables_in_answer = []
                                if answer_div_content:
                                    for table in answer_div_content.find_all("table"):
                                        table_data = extract_table_data(table)
                                        if table_data:
                                            tables_in_answer.append(table_data)
                                
                                # Check if FAQ already exists
                                existing_faq = False
                                for existing in data["faqs"]:
                                    if existing["question"] == question_text:
                                        existing_faq = True
                                        break
                                
                                if not existing_faq and question_text and answer_text:
                                    data["faqs"].append({
                                        "question": question_text,
                                        "answer": answer_text.strip(),
                                        "tables": tables_in_answer
                                    })
    except Exception as e:
        print(f"Error extracting FAQs: {e}")
        import traceback
        traceback.print_exc()
    
    # ---------- Clean up FAQs ----------
    # Remove duplicates and empty FAQs
    unique_faqs = []
    seen_questions = set()
    
    for faq in data["faqs"]:
        question = faq["question"].strip()
        if question and question not in seen_questions:
            seen_questions.add(question)
            unique_faqs.append(faq)
    
    data["faqs"] = unique_faqs
    
    return data


def extract_table_data(table_element):
    """
    Extract table data properly
    """
    try:
        table_data = []
        for row in table_element.find_all("tr"):
            row_data = []
            for cell in row.find_all(["th", "td"]):
                # Get cell text and clean it
                cell_text = cell.get_text(strip=True)
                
                # Remove extra whitespace and newlines
                cell_text = re.sub(r'\s+', ' ', cell_text)
                
                # Check if cell has colspan or rowspan
                colspan = cell.get('colspan', '1')
                rowspan = cell.get('rowspan', '1')
                
                row_data.append(cell_text)
            
            if row_data:  # Only add non-empty rows
                table_data.append(row_data)
        
        return table_data if table_data else None
    except Exception as e:
        print(f"Error extracting table: {e}")
        return None

def scrape_p_colleges_data(driver):
    driver.get(P_COLLEGE)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    
    data = {
        "Page_title":"",
        "title": "",
        "description": "",
        "table_of_contents": [],
        "sections": []
    }
    
    # Title
    page_title=soup.find("div",class_="_9617")
    ptitle = page_title.find("h1").text.strip()
    data["Page_title"] = ptitle
    h2_tag = soup.find('h2')
    if h2_tag:
        data["title"] = h2_tag.text.strip()
    
    # Description
    p =  soup.find("div",class_="faq__according-wrapper")
    first_p = p.find("p")

    if first_p:
        data["description"] = first_p.get_text(" ", strip=True)

    
    # Table of Contents
    toc_wrapper = soup.find('div', class_='newTocWrapper')
    if toc_wrapper:
        toc_items = toc_wrapper.find_all('a', class_='toc')
        for item in toc_items:
            toc_text = item.text.strip()
            # पूरा text लें, कटे हुए नहीं
            data["table_of_contents"].append(toc_text)
    
    # Sections - केवल वही sections लें जिनकी ID ctp_bhst_toc से शुरू हो
    sections = soup.find_all('h2', id=lambda x: x and x.startswith('ctp_bhst_toc'))
    
    for section in sections:
        section_id = section.get('id', '')
        section_title = section.text.strip()
        
        section_data = {
            "title": section_title,
            "id": section_id,
            "content": "",
            "tables": [],
            "lists": [],
            "subsections": []
        }
        
        # Get content till next h2
        current = section.find_next_sibling()
        content_parts = []
        seen_tables = set()  # Duplicate tables avoid करने के लिए
        
        while current and (not hasattr(current, 'name') or current.name != 'h2'):
            if hasattr(current, 'name'):
                if current.name == 'p':
                    text = current.text.strip()
                    if text:
                        content_parts.append(text)
                
                elif current.name == 'table':
                    # Extract table
                    table_html = str(current)
                    if table_html not in seen_tables:  # Duplicate check
                        table_data = extract_table_data_fixed(current)
                        if table_data:
                            section_data["tables"].append(table_data)
                            seen_tables.add(table_html)
                
                elif current.name == 'ul':
                    # Extract list
                    list_items = []
                    for li in current.find_all('li'):
                        li_text = li.text.strip()
                        if li_text:
                            list_items.append(li_text)
                    if list_items:
                        section_data["lists"].append(list_items)
                
                elif current.name == 'h3':
                    # Subsection
                    subsection_title = current.text.strip()
                    subsection_id = current.get('id', '')
                    
                    # Get subsection content
                    sub_content = []
                    sub_current = current.find_next_sibling()
                    sub_seen_tables = set()
                    
                    while sub_current and (not hasattr(sub_current, 'name') or sub_current.name not in ['h2', 'h3']):
                        if hasattr(sub_current, 'name'):
                            if sub_current.name == 'p':
                                text = sub_current.text.strip()
                                if text:
                                    sub_content.append(text)
                            elif sub_current.name == 'table':
                                table_html = str(sub_current)
                                if table_html not in sub_seen_tables:
                                    table_data = extract_table_data_fixed(sub_current)
                                    if table_data:
                                        section_data["tables"].append(table_data)
                                        sub_seen_tables.add(table_html)
                        
                        sub_current = sub_current.find_next_sibling()
                    
                    section_data["subsections"].append({
                        "title": subsection_title,
                        "id": subsection_id,
                        "content": " ".join(sub_content)
                    })
            
            current = current.find_next_sibling() if hasattr(current, 'next_sibling') else None
        
        section_data["content"] = " ".join(content_parts)
        data["sections"].append(section_data)
    
    # Remove duplicate sections (State-Wise section जो empty है)
    data["sections"] = [section for section in data["sections"] if section["content"].strip() or section["tables"] or section["lists"]]
    
    return data

def extract_table_data_fixed(table):
    """
    टेबल से डेटा सही तरीके से निकालें
    """
    table_data = []
    
    # सभी rows निकालें
    rows = table.find_all('tr')
    for row in rows:
        # सभी cells निकालें (th और td दोनों)
        cells = row.find_all(['th', 'td'])
        row_data = []
        
        for cell in cells:
            # Cell text clean करें
            cell_text = cell.text.strip()
            # Multiple spaces को single space में बदलें
            cell_text = ' '.join(cell_text.split())
            row_data.append(cell_text)
        
        if row_data:  # केवल non-empty rows add करें
            table_data.append(row_data)
    
    return table_data if table_data else None


def scrape_shiksha_qa(driver):
    driver.get(QA)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.post-col[questionid][answerid][type='Q']"))
        )
    except:
        print("No Q&A blocks loaded!")
        return {}

    soup = BeautifulSoup(driver.page_source, "html.parser")

    result = {
        "tag_name": None,
        "description": None,
        "stats": {},
        "questions": []
    }

    # Optional: get tag name & description if exists
    tag_head = soup.select_one("div.tag-head")
    if tag_head:
        tag_name_el = tag_head.select_one("h1.tag-p")
        desc_el = tag_head.select_one("p.tag-bind")
        if tag_name_el:
            result["tag_name"] = tag_name_el.get_text(strip=True)
        if desc_el:
            result["description"] = desc_el.get_text(" ", strip=True)

    # Stats
    stats_cells = soup.select("div.ana-table div.ana-cell")
    stats_keys = ["Questions", "Discussions", "Active Users", "Followers"]
    for key, cell in zip(stats_keys, stats_cells):
        count_tag = cell.select_one("b")
        if count_tag:
            value = count_tag.get("valuecount") or count_tag.get_text(strip=True)
            result["stats"][key] = value

    questions_dict = {}

    for post in soup.select("div.post-col[questionid][answerid][type='Q']"):
        q_text_el = post.select_one("div.dtl-qstn .wikkiContents")
        if not q_text_el:
            continue
        question_text = q_text_el.get_text(" ", strip=True)

        # Tags
        tags = [{"tag_name": a.get_text(strip=True), "tag_url": a.get("href")}
                for a in post.select("div.ana-qstn-block .qstn-row a")]

        # Followers
        followers_el = post.select_one("span.followersCountTextArea")
        followers = int(followers_el.get("valuecount", "0")) if followers_el else 0

        # Author
        author_el = post.select_one("div.avatar-col .avatar-name")
        author_name = author_el.get_text(strip=True) if author_el else None
        author_url = author_el.get("href") if author_el else None

        # Answer text
        answer_el = post.select_one("div.avatar-col .rp-txt .wikkiContents")
        answer_text = answer_el.get_text(" ", strip=True) if answer_el else None

        # Upvotes / downvotes
        upvote_el = post.select_one("a.up-thumb.like-a")
        downvote_el = post.select_one("a.up-thumb.like-d")
        upvotes = int(upvote_el.get_text(strip=True)) if upvote_el and upvote_el.get_text(strip=True).isdigit() else 0
        downvotes = int(downvote_el.get_text(strip=True)) if downvote_el and downvote_el.get_text(strip=True).isdigit() else 0

        # Posted time (if available)
        time_el = post.select_one("div.col-head span")
        posted_time = time_el.get_text(strip=True) if time_el else None

        # Group by question
        if question_text not in questions_dict:
            questions_dict[question_text] = {
                "tags": tags,
                "followers": followers,
                "answers": []
            }
        questions_dict[question_text]["answers"].append({
            "author": {"name": author_name, "profile_url": author_url},
            "answer_text": answer_text,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "posted_time": posted_time
        })

    # Convert dict to list
    for q_text, data in questions_dict.items():
        result["questions"].append({
            "question_text": q_text,
            "tags": data["tags"],
            "followers": data["followers"],
            "answers": data["answers"]
        })

    return result


def scrape_tag_cta_D_block(driver):
    driver.get(QAD)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    result = {
        "questions": []  # store all Q&A and discussion blocks
    }

    # Scrape all Q&A and discussion blocks
    qa_blocks = soup.select("div.post-col[questionid][answerid][type='Q'], div.post-col[questionid][answerid][type='D']")
    for block in qa_blocks:
        block_type = block.get("type", "Q")
        qa_data = {
          
            "posted_time": None,
            "tags": [],
            "question_text": None,
            "followers": 0,
            "views": 0,
            "author": {
                "name": None,
                "profile_url": None,
            },
            "answer_text": None,
        }

        # Posted time
        posted_span = block.select_one("div.col-head span")
        if posted_span:
            qa_data["posted_time"] = posted_span.get_text(strip=True)

        # Tags
        tag_links = block.select("div.ana-qstn-block div.qstn-row a")
        for a in tag_links:
            qa_data["tags"].append({
                "tag_name": a.get_text(strip=True),
                "tag_url": a.get("href")
            })

        # Question / Discussion text
        question_div = block.select_one("div.dtl-qstn a div.wikkiContents")
        if question_div:
            qa_data["question_text"] = question_div.get_text(" ", strip=True)

        # Followers
        followers_span = block.select_one("span.followersCountTextArea, span.follower")
        if followers_span:
            qa_data["followers"] = int(followers_span.get("valuecount", "0"))

        # Views
        views_span = block.select_one("div.right-cl span.viewers-span")
        if views_span:
            views_text = views_span.get_text(strip=True).split()[0].replace("k","000").replace("K","000")
            try:
                qa_data["views"] = int(views_text)
            except:
                qa_data["views"] = views_text

        # Author info
        author_name_a = block.select_one("div.avatar-col a.avatar-name")
        if author_name_a:
            qa_data["author"]["name"] = author_name_a.get_text(strip=True)
            qa_data["author"]["profile_url"] = author_name_a.get("href")

        # Answer / Comment text
        answer_div = block.select_one("div.avatar-col div.wikkiContents")
        if answer_div:
            paragraphs = answer_div.find_all("p")
            if paragraphs:
                qa_data["answer_text"] = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
            else:
                # Sometimes discussion/comment text is direct text without <p>
                qa_data["answer_text"] = answer_div.get_text(" ", strip=True)

        result["questions"].append(qa_data)

    return result


def scrape_mba_colleges():
    driver = create_driver()

      

    try:
       data = {
              "MBBS":{
                   "overviews":extract_course_data(driver),
                   "courses":scrape_courses_overview_section(driver),
                   "subject":scrape_mbbs_subjects_overview(driver),               
                   "career":scrape_mbbs_career(driver),
                   "addmission":scrape_addmission_2026_data(driver),
                   "fees": scrape_mba_fees_overview(driver),
                   "comparison": scrape_mbbs_vs_bams_comparison(driver),
                   "MD VS MBBS":scrape_mbbs_vs_md_comparison(driver),
                  "AIIMS COLLEGE IN INDIA":scrape_aiims_data(driver),
                  "ALTERNATIVE MBBS":scrape_alternative_mbbs(driver),
                  "NEET UG 2024":scrape_neet_page_corrected(driver),
                  "POPULAR COLLEGE":scrape_p_colleges_data(driver),
                   "QAN":{
                        "QA":scrape_shiksha_qa(driver),
                        "QAD":scrape_tag_cta_D_block(driver),
                    }

                   }
                }
       

    finally:
        driver.quit()
    
    return data



import os

TEMP_FILE = "mbbs.tmp.json"
FINAL_FILE = "mbbs.json"

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

