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

PCOMBA_O_URL="https://www.shiksha.com/business-management-studies/mba-in-data-analytics-chp"
# PCOMBA_S_URL = "https://www.shiksha.com/business-management-studies/mba-in-digital-marketing-syllabus-chp"
# PCOMBA_C_URL = "https://www.shiksha.com/business-management-studies/mba-in-digital-marketing-career-chp"
PCOMBA_ADDMISSION_URL="https://www.shiksha.com/business-management-studies/mba-in-data-analytics-admission-chp"
# PCOMBA_A_URL = "https://www.shiksha.com/mba/articles/top-10-mba-hr-colleges-in-india-blogId-6938"
# PCOMBA_H_URL = "https://www.shiksha.com/online-courses/articles/recruiter-roles-and-responsibilities/"
PCOMBA_Q_URL = "https://www.shiksha.com/tags/data-analytics-tdp-510485"
PCOMBA_QD_URL="https://www.shiksha.com/tags/data-analytics-tdp-510485?type=discussion"


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




def extract_overview_data(driver):
    driver.get(PCOMBA_O_URL)
    WebDriverWait(driver, 15)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    section = soup.find("section", id="chp_section_overview")

    data = {}
    title = soup.find("div",class_="a54c")
    h1 = title.text.strip()
    data["title"] = h1
    # Updated Date
    updated_div = section.select_one(".f48b div span")
    data["updated_on"] = updated_div.get_text(strip=True) if updated_div else None

    # Author Info
    author_block = section.select_one(".be8c p._7417 a")
    author_role = section.select_one(".be8c p._7417 span.b0fc")
    data["author"] = {
        "name": author_block.get_text(strip=True) if author_block else None,
        "profile_url": author_block["href"] if author_block else None,
        "role": author_role.get_text(strip=True) if author_role else None
    }

    section = soup.find(id="wikkiContents_chp_section_overview_0")
    overview_paras = []
    
    if section:
        for p in section.find_all("p"):
            text = p.get_text(" ", strip=True)
            # Only take paragraphs with more than 50 characters (adjust as needed)
            if text and len(text) > 50:
                overview_paras.append(text)
    
    data["overview"] = overview_paras
        
    # Highlights Table
    highlights = {}
    table = section.find("table")
    if table:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) == 2:
                highlights[cols[0].get_text(strip=True)] = cols[1].get_text(" ", strip=True)
    data["highlights"] = highlights

    iframe = section.select_one(".vcmsEmbed iframe")
    
    if iframe:
        data["youtube_video"] = iframe.get("src") or iframe.get("data-src")
    else:
        data["youtube_video"] = None
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sectional-faqs-0"))
        )
    except:
        pass

    faqs = []

    # pura page me kahin bhi sectional-faqs dhundo
    faq_section = section.select_one("div.sectional-faqs-0")

    if faq_section:
        questions = faq_section.select("div.html-0")

        for q in questions:
            question = q.get_text(" ", strip=True).replace("Q:", "").strip()

            answer_div = q.find_next_sibling("div", class_="_16f53f")
            if not answer_div:
                continue

            content = answer_div.select_one(".cmsAContent")
            if not content:
                continue

            answer = content.get_text(" ", strip=True).replace("A:", "").strip()

            faqs.append({
                "question": question,
                "answer": answer
            })
    else:
        print("⚠️ FAQ section not available for this college/page")

    data["faqs"] = faqs
    toc = []
    toc_wrapper = soup.find("ul", id="tocWrapper")
    if toc_wrapper:
        for li in toc_wrapper.find_all("li"):
            toc.append({
                "title": li.get_text(" ", strip=True),
            })
    data["table_of_contents"] = toc


    # ==============================
    # ==============================
    # ELIGIBILITY SECTION
    # ==============================
    eligibility_section = soup.find("div", id="wikkiContents_chp_section_eligibility_1")
    eligibility_data = {}

    if eligibility_section:

        content = eligibility_section.find("div")

        # ------------------------------
        # Eligibility Description (Before h2)
        # ------------------------------
        description = []
        criteria_points = []

        for tag in content.children:
            if getattr(tag, "name", None) == "h2":
                break  # stop before Admission section

            if tag.name == "p":
                text = tag.get_text(" ", strip=True)
                if text and "Also Read" not in text:
                    description.append(text)

            if tag.name == "ul":
                for li in tag.find_all("li"):
                    criteria_points.append(li.get_text(" ", strip=True))

        eligibility_data["description"] = description
        eligibility_data["criteria_points"] = criteria_points

        # ------------------------------
        # YouTube Video (Eligibility only)
        # ------------------------------
        iframe = eligibility_section.find("iframe")
        eligibility_data["youtube_video"] = iframe.get("src") if iframe else None

        # ------------------------------
        # Admission Process (After h2)
        # ------------------------------
        admission_steps = []
        admission_heading = eligibility_section.find("h2", string=lambda x: x and "Admission" in x)

        if admission_heading:
            for sib in admission_heading.find_next_siblings():
                if sib.name == "p":
                        text = sib.get_text(" ", strip=True)
                        if text:
                            admission_steps.append(text)

            eligibility_data["admission_process"] = admission_steps

            # ==============================
            faqs = []

            faq_section = soup.find("div",class_="sectional-faqs")
            if faq_section:
                # All question divs have class "listener"
                question_divs = faq_section.find_all("div", class_="listener")
                
                for q_div in question_divs:
                    # Question is inside <strong>
                    question_tag = q_div.find("strong")
                    if question_tag:
                        question_text = question_tag.get_text(" ", strip=True).replace("Q: ", "")
                        
                        # Answer is inside the next sibling div with class "cmsAContent"
                        answer_tag = q_div.find_next("div", class_="cmsAContent")
                        if answer_tag:
                            # If answer has <li>, join them; otherwise, use text
                            if answer_tag.find("li"):
                                answer_text = " ".join(li.get_text(" ", strip=True) for li in answer_tag.find_all("li"))
                            else:
                                answer_text = answer_tag.get_text(" ", strip=True)
                            
                            faqs.append({
                                "question": question_text,
                                "answer": answer_text
                            })
        eligibility_data["faqs"] = faqs

    data["eligibility_section"] = eligibility_data

    # SYLLABUS & SPECIALIZATION SECTION
    # ==============================
    syllabus_section = soup.find("section", id="chp_section_coursesyllabus")
    syllabus_data = {}

    if syllabus_section:

        # Section Title
        title = syllabus_section.find("h2")
        syllabus_data["title"] = title.get_text(strip=True) if title else None

        content_block = syllabus_section.select_one(".wikkiContents")

        # Intro Paragraphs
        intro_paras = []
        if content_block:
            for p in content_block.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text and "Source:" not in text:
                    intro_paras.append(text)
        syllabus_data["description"] = intro_paras

        # ==============================
        # SEMESTER-WISE SYLLABUS TABLE
        # ==============================
        semester_syllabus = {}

        tables = content_block.find_all("table") if content_block else []

        if tables:
            syllabus_table = tables[0]   # ✅ FIRST table only
            current_semester = None

            for row in syllabus_table.find_all("tr"):
                th = row.find("th")
                tds = row.find_all("td")

                # Semester Header
                if th and not tds:
                    current_semester = th.get_text(strip=True)
                    semester_syllabus[current_semester] = []

                # Subjects
                elif current_semester and tds:
                    for td in tds:
                        subject = td.get_text(" ", strip=True)
                        if subject:
                            semester_syllabus[current_semester].append(subject)

        syllabus_data["semester_wise_syllabus"] = semester_syllabus

        # ==============================
        # SYLLABUS YOUTUBE VIDEO
        # ==============================
        iframe = syllabus_section.select_one(".vcmsEmbed iframe")
        syllabus_data["youtube_video"] = iframe.get("src") if iframe else None

        # ==============================
        # MBA SPECIALISATIONS TABLE
        # ==============================
        specialisations = []
        tables = content_block.find_all("table") if content_block else []

        if len(tables) > 1:
            spec_table = tables[1]
            rows = spec_table.find_all("tr")[1:]

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    specialisations.append({
                        "specialisation": cols[0].get_text(" ", strip=True),
                        "average_salary": cols[1].get_text(" ", strip=True),
                        "colleges": cols[2].get_text(" ", strip=True)
                    })

        syllabus_data["specialisations"] = specialisations

        # ==============================
        # POPULAR SPECIALIZATION BOX
        # ==============================
        popular_specs = []
        spec_box = syllabus_section.select_one(".specialization-box")

        if spec_box:
            for li in spec_box.select("ul.specialization-list li"):
                popular_specs.append({
                    "name": li.find("a").get_text(strip=True),
                    "url": li.find("a")["href"],
                    "college_count": li.find("p").get_text(strip=True)
                })

        syllabus_data["popular_specializations"] = popular_specs

        # ==============================
        # SYLLABUS FAQs
        # ==============================
        faqs = []
        faq_questions = syllabus_section.select(".sectional-faqs > div.html-0")
        faq_answers = syllabus_section.select(".sectional-faqs > div._16f53f")

        for q, a in zip(faq_questions, faq_answers):
            faqs.append({
                "question": q.get_text(" ", strip=True).replace("Q:", "").strip(),
                "answer": a.get_text(" ", strip=True).replace("A:", "").strip()
            })

        syllabus_data["faqs"] = faqs

    data["syllabus_section"] = syllabus_data

    college_sections = []

    college_section = soup.find("div", id="wikkiContents_chp_section_popularcolleges_0")
    if not college_section:
        print("⚠️ College section not found")
    else:
        table = college_section.find("table")
        if not table:
            print("⚠️ College table not found")
        else:
            rows = table.find_all("tr")[1:]  # skip header

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue

                college_tag = cols[0].find("a")
                college_name = college_tag.get_text(strip=True) if college_tag else cols[0].get_text(strip=True)
                college_url = college_tag["href"] if college_tag else None

                course_name = cols[1].get_text(" ", strip=True)
                fees = cols[2].get_text(strip=True)

                college_sections.append({
                    "college_name": college_name,
                    "college_url": college_url,
                    "course_name": course_name,
                    "fees": fees if fees and fees.lower() != "na" else None
                })

    data["college_section"] = college_sections

    # ==============================
    # ONLINE COURSES SECTION
    # ==============================
    online_courses_section = soup.find("section", id="chp_section_onlinecourses")
    online_courses_data = {}

    if online_courses_section:

        # -------- Title --------
        title = online_courses_section.find("h2")
        online_courses_data["title"] = title.get_text(strip=True) if title else None

        # -------- Description --------
        description = []
        content_block = online_courses_section.select_one(".wikkiContents")

        if content_block:
            for p in content_block.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text and "Source:" not in text:
                    description.append(text)

        online_courses_data["description"] = description

        # -------- Courses Table --------
        courses = []
        table = online_courses_section.find("table")

        if table:
            rows = table.find_all("tr")

            for row in rows:
                cols = row.find_all("td")

                # ✅ SAFETY CHECK (IndexError FIX)
                if len(cols) < 3:
                    continue

                course_name_tag = cols[0].find("a")

                courses.append({
                    "course_name": course_name_tag.get_text(strip=True) if course_name_tag else cols[0].get_text(strip=True),
                    "course_url": course_name_tag["href"] if course_name_tag else None,
                    "provider": cols[1].get_text(strip=True),
                    "fees": cols[2].get_text(strip=True)
                })

        online_courses_data["courses"] = courses

        # -------- FAQs --------
        faqs = []
        faq_section = online_courses_section.select_one(".sectional-faqs")

        if faq_section:
            question_divs = faq_section.select("div.html-0.c5db62.listener")

            for q_div in question_divs:
                question = q_div.get_text(" ", strip=True).replace("Q:", "").strip()

                answer_div = q_div.find_next_sibling("div", class_="_16f53f")
                answer = ""

                if answer_div:
                    answer_content = answer_div.select_one(".cmsAContent")
                    if answer_content:
                        answer = answer_content.get_text(" ", strip=True).replace("A:", "").strip()
                    else:
                        answer = answer_div.get_text(" ", strip=True).replace("A:", "").strip()

                if question and answer:
                    faqs.append({
                        "question": question,
                        "answer": answer
                    })

        online_courses_data["faqs"] = faqs

    data["online_courses_section"] = online_courses_data

    # ==============================
    # TYPES OF MBA FINANCE COURSES SECTION
    # ==============================
    types_section = soup.find("section", id="chp_section_topratecourses")
    types_data = {}

    if types_section:

        # Section Title
        title = types_section.find("h2")
        types_data["title"] = title.get_text(strip=True) if title else None

        content_block = types_section.select_one(".wikkiContents")

        # Intro Paragraphs
        intro_paras = []
        if content_block:
            # पहला div जिसमें content है
            first_div = content_block.find("div")
            if first_div:
                for p in first_div.select("p"):
                    text = p.get_text(" ", strip=True)
                    if text and "Note -" not in text and "Also read -" not in text:
                        intro_paras.append(text)
        
        types_data["description"] = intro_paras
        
        # ==============================
        # COURSE MODES TABLE
        # ==============================
        course_modes = []
        table = content_block.find("table") if content_block else None

        if table:
            rows = table.find_all("tr")[1:]  # पहली row header है इसलिए skip करें
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:  # यहाँ 2 columns हैं
                    mode_name = cols[0].get_text(strip=True)
                    
                    # Eligibility points निकालें
                    eligibility_points = []
                    ul = cols[1].find("ul")
                    if ul:
                        for li in ul.find_all("li"):
                            eligibility_points.append(li.get_text(" ", strip=True))
                    else:
                        # अगर ul नहीं है तो सीधे text लें
                        text = cols[1].get_text(" ", strip=True)
                        if text:
                            eligibility_points.append(text)
                    
                    course_modes.append({
                        "mode": mode_name,
                        "eligibility": eligibility_points
                    })

        types_data["course_modes"] = course_modes

        # Note about the information
        note = content_block.find("p", string=lambda t: t and "Note -" in t) if content_block else None
        if note:
            types_data["note"] = note.get_text(strip=True)

        # ==============================
        # POPULAR COURSES BOX
        # ==============================
        popular_courses = []
        popular_box = types_section.select_one(".specialization-box")

        if popular_box:
            for li in popular_box.select("ul.specialization-list li"):
                # Course name and link
                course_link_tag = li.find("a")
                strong_tag = li.find("strong")
                
                # Offered by information
                offered_by_tag = li.find("a", href=lambda x: x and "college" in x or "university" in x)
                
                # Rating and reviews
                rating_div = li.select_one(".rating-block")
                reviews_link = li.select_one("a.view_rvws")
                
                # Rating stars width (percentage)
                full_stars = li.select_one(".full_starts")
                rating_percentage = None
                if full_stars and full_stars.has_attr('style'):
                    style = full_stars['style']
                    if 'width:' in style:
                        rating_percentage = style.split('width:')[1].split('%')[0].strip() + '%'
                
                course_data = {
                    "course_name": strong_tag.get_text(strip=True) if strong_tag else None,
                    "course_url": course_link_tag["href"] if course_link_tag else None,
                    "institute_name": offered_by_tag.get_text(strip=True).replace("Offered By", "").strip() if offered_by_tag else None,
                    "institute_url": offered_by_tag["href"] if offered_by_tag else None,
                    "rating": rating_div.get_text(strip=True) if rating_div else None,
                    "rating_percentage": rating_percentage,
                    "reviews_count": reviews_link.get_text(strip=True).replace('reviews', '').strip() if reviews_link else None,
                    "reviews_url": reviews_link["href"] if reviews_link else None
                }
                popular_courses.append(course_data)

        types_data["popular_courses"] = popular_courses

        # ==============================
        # FAQs
        # ==============================
        faqs = []
        faq_section = types_section.select_one(".c358de")
        
        if faq_section:
            faq_items = faq_section.select(".html-0.c5db62")
            
            for faq_item in faq_items:
                question = faq_item.get_text(" ", strip=True).replace("Q:", "").strip()
                
                # अगला sibling जो answer है
                answer_div = faq_item.find_next_sibling("div", class_="_16f53f")
                answer = ""
                if answer_div:
                    answer_content = answer_div.select_one(".cmsAContent")
                    if answer_content:
                        answer = answer_content.get_text(" ", strip=True).replace("A:", "").strip()
                    else:
                        answer = answer_div.get_text(" ", strip=True).replace("A:", "").strip()
                
                faqs.append({
                    "question": question,
                    "answer": answer
                })

        types_data["faqs"] = faqs

    data["types_of_mba_finance_courses"] = types_data

    # POPULAR COLLEGES SECTION
    # ==============================
    popular_colleges_section = soup.find("section", id="chp_section_popularcolleges")
    popular_colleges_data = {}
    
    if popular_colleges_section:
    
        # Section title
        title = popular_colleges_section.find("h2")
        popular_colleges_data["title"] = title.get_text(strip=True) if title else None
    
        content_block = popular_colleges_section.select_one(".wikkiContents")
    
        # ------------------------------
        # Description Paragraphs
        # ------------------------------
        description = []
        if content_block:
            for p in content_block.select("p"):
                text = p.get_text(" ", strip=True)
                if text and "Source:" not in text:
                    description.append(text)
    
        popular_colleges_data["description"] = description
    
        # ------------------------------
        # Tables (Private + Government)
        # ------------------------------
        tables = content_block.find_all("table") if content_block else []
    
        private_colleges = []
        government_colleges = []
    
        # ✅ First table → Private colleges
        if len(tables) >= 1:
            rows = tables[0].find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    link = cols[0].find("a")
                    private_colleges.append({
                        "college_name": cols[0].get_text(" ", strip=True),
                        "college_url": link["href"] if link else None,
                        "total_fees": cols[1].get_text(" ", strip=True)
                    })
    
        # ✅ Second table → Government colleges
        if len(tables) >= 2:
            rows = tables[1].find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    link = cols[0].find("a")
                    government_colleges.append({
                        "college_name": cols[0].get_text(" ", strip=True),
                        "college_url": link["href"] if link else None,
                        "fees": cols[1].get_text(" ", strip=True)
                    })
    
        popular_colleges_data["private_colleges"] = private_colleges
        popular_colleges_data["government_colleges"] = government_colleges
    
        # ------------------------------
        # YouTube Video
        # ------------------------------
        iframe = popular_colleges_section.select_one(".vcmsEmbed iframe")
        popular_colleges_data["youtube_video"] = iframe.get("src") if iframe else None
    
    data["popular_colleges_section"] = popular_colleges_data
    
    # ==============================
    # SALARY & CAREER SECTION
    # ==============================
    salary_section = soup.find("section", id="chp_section_salary")
    salary_data = {}

    if salary_section:

        # ------------------------------
        # Title
        # ------------------------------
        title = salary_section.find("h2")
        salary_data["title"] = title.get_text(strip=True) if title else None

        content_block = salary_section.select_one(".wikkiContents")

        # ------------------------------
        # Description (intro paragraphs only)
        # ------------------------------
        description = []
        if content_block:
            for p in content_block.find_all("p", recursive=False):
                text = p.get_text(" ", strip=True)
                if text and "Source" not in text:
                    description.append(text)

        salary_data["description"] = description

        # ------------------------------
        # Tables
        # ------------------------------
        tables = content_block.find_all("table") if content_block else []

        # ==========================
        # TABLE 1: CORE INDUSTRIES
        # ==========================
        core_industries = []
        if len(tables) >= 1:
            table = tables[0]
            rows = table.find_all("tr")[1:]  # header skip
            for row in rows:
                cols = row.find_all("td")
                for col in cols:
                    text = col.get_text(" ", strip=True)
                    if text:
                        core_industries.append(text)

        salary_data["core_industries"] = core_industries

        # ==========================
        # TABLE 2: JOB ROLES & SALARY
        # ==========================
        job_roles_salary = []
        if len(tables) >= 2:
            table = tables[1]
            rows = table.find_all("tr")[1:]  # header skip

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    job_roles_salary.append({
                        "job_role": cols[0].get_text(" ", strip=True),
                        "average_salary": cols[1].get_text(" ", strip=True)
                    })

        salary_data["job_roles_salary"] = job_roles_salary

        # ==========================
        # TABLE 3: TOP RECRUITERS
        # ==========================
        top_recruiters = []
        if len(tables) >= 3:
            table = tables[2]
            cells = table.find_all("td")
            for cell in cells:
                text = cell.get_text(" ", strip=True)
                if text:
                    top_recruiters.append(text)

        salary_data["top_recruiters"] = top_recruiters

        # ------------------------------
        # FAQs
        # ------------------------------
        faqs = []
        faq_questions = salary_section.select(".html-0.c5db62.listener")

        for q in faq_questions:
            question = q.get_text(" ", strip=True).replace("Q:", "").strip()

            answer_div = q.find_next_sibling("div", class_="_16f53f")
            answer = ""

            if answer_div:
                answer_content = answer_div.select_one(".cmsAContent")
                if answer_content:
                    answer = answer_content.get_text(" ", strip=True)
                else:
                    answer = answer_div.get_text(" ", strip=True)

            answer = answer.replace("A:", "").strip()

            if question and answer:
                faqs.append({
                    "question": question,
                    "answer": answer
                })

        salary_data["faqs"] = faqs

    data["salary_section"] = salary_data

    study_section = soup.select_one("section#chp_section_studyabroadcourses")

    study_abroad_data = {}

    if study_section:
        # -------- Title --------
        title_tag = study_section.select_one("h2.tbSec2")
        if title_tag:
            study_abroad_data["title"] = title_tag.get_text(strip=True)

        # -------- Description --------
        desc_paragraphs = study_section.select("div#wikkiContents_chp_section_studyabroadcourses_0 > div > p")
        description = " ".join(p.get_text(" ", strip=True) for p in desc_paragraphs if p.get_text(strip=True))
        if description:
            study_abroad_data["description"] = description

        # -------- University Table --------
        table = study_section.select_one("div#wikkiContents_chp_section_studyabroadcourses_0 table")
        universities = []
        if table:
            rows = table.find_all("tr")
            headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == len(headers):
                    uni_data = {
                        headers[i]: cols[i].get_text(" ", strip=True) for i in range(len(headers))
                    }
                    # Also capture the link if available
                    link_tag = cols[0].find("a")
                    if link_tag and link_tag.get("href"):
                        uni_data["link"] = link_tag["href"]
                    universities.append(uni_data)
        if universities:
            study_abroad_data["universities"] = universities

    # Add to main data
    if study_abroad_data:
        data["study_abroad_courses"] = study_abroad_data
    # FAQ SECTION
    # ==============================
    faq_section = soup.find("section", id="chp_section_faqs")
    faq_data = {}

    if faq_section:

        # ------------------------------
        # Title
        # ------------------------------
        title = faq_section.find("h2")
        faq_data["title"] = title.get_text(strip=True) if title else None

        content_block = faq_section.select_one(".wikkiContents")
        
        # ------------------------------
        # Introduction
        # ------------------------------
        description = []
        if content_block:
            first_div = content_block.find("div")
            if first_div:
                for p in first_div.find_all("p"):
                    text = p.get_text(" ", strip=True)
                    if text:
                        description.append(text)
        
        faq_data["introduction"] = description
        
        # ------------------------------
        # FAQ Questions & Answers
        # ------------------------------
        faqs = []
        
        # सभी FAQ questions निकालें
        faq_questions = faq_section.select(".html-0.c5db62.listener")
        
        for question_div in faq_questions:
            question_text = question_div.get_text(" ", strip=True).replace("Q:", "").strip()

            # Answer container ढूंढें
            answer_div = question_div.find_next_sibling("div", class_="_16f53f")
            answer_text = ""
            
            if answer_div:
                answer_content = answer_div.select_one(".cmsAContent")
                if answer_content:
                    # पूरे answer को structured तरीके से निकालें
                    answer_parts = []
                    
                    # Paragraphs
                    for p in answer_content.find_all("p"):
                        text = p.get_text(" ", strip=True)
                        if text:
                            answer_parts.append(text)
                    
                    # Lists (ul/ol)
                    for list_elem in answer_content.find_all(["ul", "ol"]):
                        list_items = []
                        for li in list_elem.find_all("li"):
                            item_text = li.get_text(" ", strip=True)
                            if item_text:
                                list_items.append(item_text)
                        if list_items:
                            answer_parts.append("List: " + "; ".join(list_items))
                    
                    # Tables
                    for table in answer_content.find_all("table"):
                        # Table की basic information
                        table_data = []
                        rows = table.find_all("tr")
                        for row in rows:
                            cells = row.find_all(["th", "td"])
                            row_data = [cell.get_text(" ", strip=True) for cell in cells if cell.get_text(strip=True)]
                            if row_data:
                                table_data.append(" | ".join(row_data))
                        
                        if table_data:
                            answer_parts.append("Table: " + " || ".join(table_data))
                    
                    # अगर कोई direct text है (lists, tables के बिना)
                    if not answer_parts:
                        answer_text = answer_content.get_text(" ", strip=True)
                    else:
                        answer_text = " ".join(answer_parts)
                    
                    # "A:" remove करें अगर है तो
                    answer_text = answer_text.replace("A:", "").strip()
                else:
                    # अगर .cmsAContent नहीं है तो सीधे text लें
                    answer_text = answer_div.get_text(" ", strip=True).replace("A:", "").strip()
            
            if question_text and answer_text:
                faq = {
                    "question": question_text,
                    "answer": answer_text
                }
                
                # अगर answer में table data है तो उसे अलग से भी store करें
                if answer_content:
                    tables_in_answer = answer_content.find_all("table")
                    if tables_in_answer:
                        faq["has_table"] = True
                        
                        # पहले table की detailed data (अगर जरूरी हो)
                        table_data = []
                        for idx, table in enumerate(tables_in_answer):
                            table_rows = []
                            rows = table.find_all("tr")
                            for row in rows:
                                cells = row.find_all(["th", "td"])
                                row_data = []
                                for cell in cells:
                                    cell_text = cell.get_text(strip=True)
                                    
                                    # Check for links in cells
                                    links = cell.find_all("a")
                                    link_data = []
                                    for link in links:
                                        link_text = link.get_text(strip=True)
                                        link_href = link.get("href", "")
                                        if link_text:
                                            link_data.append({
                                                "text": link_text,
                                                "url": link_href
                                            })
                                    
                                    row_data.append({
                                        "text": cell_text,
                                        "links": link_data if link_data else None
                                    })
                                table_rows.append(row_data)
                            
                            if table_rows:
                                table_data.append({
                                    "table_index": idx,
                                    "rows": table_rows
                                })
                        
                        if table_data:
                            faq["table_data"] = table_data
                
                faqs.append(faq)
        
        faq_data["faqs"] = faqs
        
        # ------------------------------
        # Total FAQs Count
        # ------------------------------
        faq_data["total_faqs"] = len(faqs)

    data["faq_section"] = faq_data

    return data


def scrape_admission_overview(driver):
    driver.get(PCOMBA_ADDMISSION_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "overview":"",
        "sections": []
    }

    # ---------------- TITLE ----------------
    title = soup.find("div", class_="a54c")
    data["title"] = title.get_text(strip=True) if title else None

    # ---------------- META SECTION ----------------
    section1 = soup.find(id="chp_admission_overview")
    if section1:
        updated_div = section1.select_one(".f48b div span")
        data["updated_on"] = updated_div.get_text(strip=True) if updated_div else None

        author_block = section1.select_one(".be8c p._7417 a")
        author_role = section1.select_one(".be8c p._7417 span.b0fc")

        data["author"] = {
            "name": author_block.get_text(strip=True) if author_block else None,
            "profile_url": author_block["href"] if author_block else None,
            "role": author_role.get_text(strip=True) if author_role else None
        }

    # ---------------- MAIN CONTENT ----------------
    section = soup.find("div", id="wikkiContents_chp_admission_overview_0")
    if not section:
        return data

    main_container = section.find("div")
    if not main_container:
        return data

    intro_paras = []
    for el in main_container.find_all(["p", "h2", "h3"], recursive=True):
        if el.name in ["h2", "h3"]:
            break  # stop at first heading
        text = el.get_text(" ", strip=True)
        if text:
            intro_paras.append(text)

    data["overview"] = intro_paras
    current_section = None
    for element in main_container.find_all(recursive=True):
        if element.name in ["h2", "h3"]:
            if current_section:
                data["sections"].append(current_section)
            current_section = {"heading": element.get_text(strip=True), "content": []}
        elif element.name == "p" and current_section:
            text = element.get_text(" ", strip=True)
            if text:
                current_section["content"].append({"text": text})
        elif element.name == "ul" and current_section:
            items = [li.get_text(" ", strip=True) for li in element.find_all("li") if li.get_text(strip=True)]
            if items:
                current_section["content"].append({"items": items})
        elif element.name == "table" and current_section:
            rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])] for row in element.find_all("tr")]
            if rows:
                current_section["content"].append({"rows": rows})

    if current_section:
        data["sections"].append(current_section)

    return data



# def scrape_syllabus_section(driver):
#     driver.get(PCOMBA_S_URL)
#     time.sleep(3)

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     syllabus_data = {}

#     section = soup.find("section", id="chp_syllabus_overview")
#     if not section:
#         return syllabus_data

#     # =========================
#     # META
#     # =========================
#     title = soup.find("div", class_="a54c")
#     h1 = title.text.strip() if title else None
#     syllabus_data["title"] = h1
#     updated_span = section.select_one(".f48b span")
#     syllabus_data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

#     author_name = section.select_one(".be8c a")
#     author_role = section.select_one(".be8c span.b0fc")

#     syllabus_data["author"] = {
#         "name": author_name.get_text(strip=True) if author_name else None,
#         "profile_url": author_name["href"] if author_name else None,
#         "role": author_role.get_text(strip=True) if author_role else None
#     }

#     content = section.select_one(".wikkiContents > div")
#     if not content:
#         return syllabus_data

#     # =========================
#     # INTRO
#     # =========================
#     intro = []
#     for el in content.find_all(["p", "h2"], recursive=False):
#         if el.name == "h2":
#             break
#         txt = el.get_text(" ", strip=True)
#         if txt:
#             intro.append(txt)

#     syllabus_data["introduction"] = intro

#     # =========================
#     # TABLE PARSER
#     # =========================
#     def parse_table(table):
#         headers = [th.get_text(" ", strip=True) for th in table.find_all("th")]
#         data = []

#         for row in table.find_all("tr")[1:]:
#             cols = row.find_all("td")
#             if not cols:
#                 continue

#             row_obj = {}
#             for i, col in enumerate(cols):
#                 key = headers[i] if i < len(headers) else f"column_{i+1}"
#                 row_obj[key] = col.get_text(" ", strip=True)

#             data.append(row_obj)

#         return data

#     syllabus_data["sections"] = []

#     # =========================
#     # MAIN SECTION LOOP
#     # =========================
#     for h2 in content.find_all("h2"):
#         block = {
#             "title": h2.get_text(" ", strip=True),
#             "description": [],
#             "tables": {}
#         }

#         el = h2.find_next_sibling()

#         last_para = None

#         while el and el.name != "h2":
#             if el.name == "p":
#                 txt = el.get_text(" ", strip=True)
#                 if txt:
#                     block["description"].append(txt)
#                     last_para = txt.lower()

#             elif el.name == "ul":
#                 block["description"].append(
#                     [li.get_text(" ", strip=True) for li in el.find_all("li")]
#                 )

#             elif el.name == "table":
#                 table_data = parse_table(el)

#                 # 🔥 SMART LABELING
#                 if last_para:
#                     if "core" in last_para:
#                         block["tables"]["core_subjects"] = table_data
#                     elif "elective" in last_para:
#                         block["tables"]["elective_subjects"] = table_data
#                     elif "semester" in block["title"].lower():
#                         block["tables"]["semester_wise"] = table_data
#                     elif "book" in block["title"].lower():
#                         block["tables"]["books"] = table_data
#                     else:
#                         block["tables"].setdefault("others", []).append(table_data)
#                 else:
#                     block["tables"].setdefault("others", []).append(table_data)

#             el = el.find_next_sibling()

#         syllabus_data["sections"].append(block)

#     return syllabus_data
# def scrape_career_overview(driver):
#     driver.get(PCOMBA_C_URL)
#     soup = BeautifulSoup(driver.page_source,"html.parser")
#     section = soup.select_one("section#chp_career_overview")
#     if not section:
#         return {}

#     career_data = {}

#     title = soup.find("div", class_="a54c")
#     h1 = title.text.strip() if title else None
#     career_data ["title"] = h1
    
#     # Updated Date
#     updated_div = section.select_one(".f48b div span")
#     career_data ["updated_on"] = updated_div.get_text(strip=True) if updated_div else None

#     # Author Info
#     author_block = section.select_one(".be8c p._7417 a")
#     author_role = section.select_one(".be8c p._7417 span.b0fc")
#     career_data ["author"] = {
#         "name": author_block.get_text(strip=True) if author_block else None,
#         "profile_url": author_block["href"] if author_block else None,
#         "role": author_role.get_text(strip=True) if author_role else None
#     }

#     content = section.select_one("div#wikkiContents_chp_career_overview_0")
#     if not content:
#         return career_data

#     intro_paras = []

#     inner_div = content.find("div", recursive=False)
#     if inner_div:
#         for p in inner_div.find_all("p", recursive=False):
#             text = p.get_text(" ", strip=True)
#             if text:
#                 intro_paras.append(text)

#     career_data["overview"] = intro_paras

#     sections = []
#     current = None

#     for tag in content.find_all(["h2", "p", "ul", "ol", "table"], recursive=True):
#         if tag.name == "h2":
#            if current:
#                sections.append(current)
           
#            current = {
#                "title": tag.get_text(strip=True),
#                "content": []
#            }
                
#         elif current:

#             if tag.name == "table":
#                 rows = []
#                 for tr in tag.find_all("tr"):
#                     cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
#                     if cells:
#                         rows.append(cells)
#                 if rows:
#                     current["content"].append({"value": rows})

#     if current:
#         sections.append(current)

#     career_data["sections"] = sections
#     return career_data



# def scrape_top_colleges_article(driver):
#     driver.get(PCOMBA_A_URL)
#     time.sleep(5)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
    
#     data = {
#         "metadata": {
#             "title": None,
#             "author": {
#                 "name": None,
#                 "role": None,
#                 "profile_url": None
#             },
#             "image":"",
#             "updated_on": None,
#             "summary": None
#         },
#         "introduction": [],
#         "table_of_contents": [],
#         "colleges": [],
#         "related_articles": []
#     }
    
    
#     # ---------------- TITLE ----------------
#     title_div = soup.find("div", class_="flx-box mA")
#     if title_div:
#         h1_tag = title_div.find("h1")
#         data["metadata"]["title"] = h1_tag.get_text(strip=True) if h1_tag else title_div.get_text(strip=True)
    
#     # ---------------- AUTHOR AND UPDATE INFO ----------------
#     # Author info from user section
#     user_section = soup.find("div", class_="adp_user_tag")
#     if user_section:
#         if user_section:
#             name = user_section.find("div",class_="adp_usr_dtls")
#             author_name_elem = name.find("a")
#             if author_name_elem:
#                 data["metadata"]["author"]["name"] = author_name_elem.get_text(strip=True)
        
#         role_elem = user_section.find("div", class_="user_expert_level")
#         if role_elem:
#             data["metadata"]["author"]["role"] = role_elem.get_text(strip=True)
        
#         if author_name_elem:
#             data["metadata"]["author"]["profile_url"] = author_name_elem.get("href")
    
#     # Updated date
#     updated_div = soup.find("div", class_="blogdata_user")
#     if updated_div:
#         span_elem = updated_div.find("span")
#         if span_elem:
#             data["metadata"]["updated_on"] = span_elem.get_text(strip=True)
    
#     # ---------------- SUMMARY ----------------
#     summary_div = soup.find("div", class_="blogSummary")
#     if summary_div:
#         data["metadata"]["summary"] = summary_div.get_text(strip=True)
    
#     # ---------------- INTRODUCTION PARAGRAPHS ----------------
#     # Find the first wikkiContents div for introduction
#     intro_div = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#     if intro_div:
#         picture = intro_div.find("picture")
#         if picture:
           
#             img = picture.find("img")
     
#             img=img.get("src")
#             data["metadata"]["image"] = img

#         intro_paragraphs = []
#         # Get all paragraphs before the first table
#         for elem in intro_div.find_all(["p", "h2", "table"]):
#             if elem.name == "table":
#                 break
#             if elem.name == "p":
#                 text = elem.get_text(strip=True)
#                 if text and not text.startswith(("Also Read:", "Read More:")):
#                     intro_paragraphs.append(text)
#         data["introduction"] = intro_paragraphs
    
#     # ---------------- TABLE OF CONTENTS ----------------
#     toc_ul = soup.find("ul", id="tocWrapper")
#     if toc_ul:
#         toc_items = []
#         for li in toc_ul.find_all("li"):
#             item_text = li.get_text(strip=True)
#             if item_text:
#                 toc_items.append(item_text)
#         data["table_of_contents"] = toc_items
    
#     # ---------------- COLLEGES DETAILS ----------------
#     # Get all wikkiContents sections
#     all_wikki_contents = soup.find_all("div", class_="wikkiContents")
    
#     colleges_data = []
    
#     for section in all_wikki_contents:
#         # Find all h2 headings in this section
#         h2_headings = section.find_all("h2")
        
#         for h2 in h2_headings:
#             heading_text = h2.get_text(strip=True)
            
#             # Skip general headings
#             skip_headings = ["What is MBA in HR course?", "MBA HR Best Colleges in India", 
#                             "Top 10 MBA HR Colleges In India: Eligibility and Course Fee"]
            
#             if heading_text in skip_headings:
#                 continue
            
#             # Check if this is a college heading (contains college name keywords)
#             college_keywords = ["XLRI", "MDI", "NMIMS", "TISS", "IMI", "IIM", "XISS", 
#                                "UBS", "ISBM", "IISWBM", "Xavier", "Management", "Institute"]
            
#             if any(keyword in heading_text for keyword in college_keywords):
#                 college_info = {
#                     "name": heading_text,
#                     "description": [],
#                     "table": None
#                 }
                
#                 # Get description paragraphs after h2
#                 next_elem = h2.find_next_sibling()
#                 while next_elem and next_elem.name != "h2":
#                     if next_elem.name == "p":
#                         text = next_elem.get_text(strip=True)
#                         if text and not text.startswith(("Also Read:", "Read More:")):
#                             college_info["description"].append(text)
#                     elif next_elem.name == "table":
#                         # Extract table data
#                         table_data = extract_college_table(next_elem)
#                         if table_data:
#                             college_info["table"] = table_data
#                         break  # Stop after first table
                    
#                     next_elem = next_elem.find_next_sibling()
                
#                 colleges_data.append(college_info)
    
#     data["colleges"] = colleges_data
    
#     # ---------------- RELATED ARTICLES ----------------
#     # Find the last table with related articles
#     all_tables = soup.find_all("table")
#     related_articles_data = []
    
#     for table in all_tables:
#         # Check if this is the related articles table
#         table_html = str(table)
#         if "MBA in Digital Marketing" in table_html or "Top 10 MBA specializations" in table_html:
#             rows = table.find_all("tr")
#             for row in rows:
#                 cells = row.find_all("td")
#                 for cell in cells:
#                     link = cell.find("a")
#                     if link:
#                         related_articles_data.append({
#                             "title": link.get_text(strip=True),
#                             "url": link.get("href")
#                         })
#             break
    
#     if related_articles_data:
#         data["related_articles"] = related_articles_data
    
#     return data


# def extract_college_table(table_element):
#     """Extract structured data from college table"""
#     if not table_element:
#         return None
    
#     table_data = []
#     rows = table_element.find_all("tr")
    
#     for row in rows:
#         cells = []
#         for cell in row.find_all(["th", "td"]):
#             # Get cell text
#             cell_text = cell.get_text(" ", strip=True)
            
#             # Check for links
#             links = cell.find_all("a")
#             if links:
#                 cell_links = []
#                 for link in links:
#                     link_text = link.get_text(strip=True)
#                     link_url = link.get("href")
#                     if link_text and link_url:
#                         cell_links.append({
#                             "text": link_text,
#                             "url": link_url
#                         })
                
#                 if cell_links:
#                     cells.append({
#                         "text": cell_text,
#                         "links": cell_links
#                     })
#                 else:
#                     cells.append(cell_text)
#             else:
#                 cells.append(cell_text)
        
#         if cells:
#             table_data.append(cells)
    
#     return table_data if len(table_data) > 1 else None

# def scrape_top_article(driver):
#     driver.get(PCOMBA_H_URL)
#     time.sleep(5)
#     soup = BeautifulSoup(driver.page_source, "html.parser")

#     data = {
#         "metadata": {
#             "title": None,
#             "author": {
#                 "name": None,
#                 "role": None,
#                 "profile_url": None
#             },
#             "image": "",
#             "updated_on": None,
#             "summary": None
#         },
#         "introduction": [],
#         "table_of_contents": [],
#         "sections": [],
#         "related_articles": []
#     }

#     # ---------------- TITLE ----------------
#     title_div = soup.find("div", class_="flx-box mA")
#     if title_div:
#         h1_tag = title_div.find("h1")
#         data["metadata"]["title"] = h1_tag.get_text(strip=True) if h1_tag else title_div.get_text(strip=True)

#     # ---------------- AUTHOR ----------------
#     user_section = soup.find("div", class_="adp_user_tag")
#     if user_section:
#         name_div = user_section.find("div", class_="adp_usr_dtls")
#         if name_div:
#             a = name_div.find("a")
#             if a:
#                 data["metadata"]["author"]["name"] = a.get_text(strip=True)
#                 data["metadata"]["author"]["profile_url"] = a.get("href")

#         role_div = user_section.find("div", class_="user_expert_level")
#         if role_div:
#             data["metadata"]["author"]["role"] = role_div.get_text(strip=True)

#     # ---------------- UPDATED DATE ----------------
#     updated_div = soup.find("div", class_="blogdata_user")
#     if updated_div:
#         span = updated_div.find("span")
#         if span:
#             data["metadata"]["updated_on"] = span.get_text(strip=True)

#     # ---------------- SUMMARY ----------------
#     summary_div = soup.find("div", class_="blogSummary")
#     if summary_div:
#         data["metadata"]["summary"] = summary_div.get_text(strip=True)

#     # ---------------- INTRODUCTION ----------------
#     intro_div = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#     if intro_div:

#         # image
#         picture = intro_div.find("picture")
#         if picture:
#             img_tag = picture.find("img")
#             if img_tag:
#                 data["metadata"]["image"] = img_tag.get("src")

#         # paragraphs (ads / empty text ignored)
#         for p in intro_div.find_all("p"):
#             text = p.get_text(strip=True)
#             if text:
#                 data["introduction"].append(text)

#     # ---------------- TABLE OF CONTENTS + SECTIONS ----------------
#     content_blocks = soup.find_all("div", class_="wikkiContents")

#     for block in content_blocks:
#         heading = block.find(["h2", "h3"])
#         if heading:
#             section = {
#                 "title": heading.get_text(strip=True),
#                 "content": []
#             }

#             data["table_of_contents"].append(section["title"])

#             for p in block.find_all("p"):
#                 text = p.get_text(strip=True)
#                 if text:
#                     section["content"].append(text)

#             if section["content"]:
#                 data["sections"].append(section)

#     # ---------------- RELATED ARTICLES ----------------
#     related_blocks = soup.find_all("div", class_="feature-article-container-outer")

#     for article in related_blocks:
#         a_tag = article.find("a", class_="feature-article-container-inner")
#         if not a_tag:
#             continue

#         title_div = a_tag.find("div", class_="title")
#         img_tag = a_tag.find("img")

#         data["related_articles"].append({
#             "title": title_div.get_text(strip=True) if title_div else None,
#             "url": a_tag.get("href"),
#             "image": img_tag.get("src") if img_tag else None
#         })

#     return data


def scrape_shiksha_qa(driver):
    driver.get(PCOMBA_Q_URL)
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
    driver.get(PCOMBA_QD_URL)
    time.sleep(5)
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
              "mba_in_data_Analytics":{
                "overviews":extract_overview_data(driver),
                # "syllabus":scrape_syllabus_section(driver),
                # "career":scrape_career_overview(driver),
                "addmision":scrape_admission_overview(driver),
                # "affordable_hr_mba_college":scrape_top_colleges_article(driver),
                # "hr_recruiter_role":scrape_top_article(driver),
                "QA":{
                 "QA_ALL":scrape_shiksha_qa(driver),
                 "QA_D":scrape_tag_cta_D_block(driver),
                },
                
                   }
                }

    finally:
        driver.quit()
    
    return data



import os

TEMP_FILE = "distance_mba_data.tmp.json"
FINAL_FILE = "distance_mba_data.json"

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

