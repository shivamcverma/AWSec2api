from html import unescape
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

PCOMBA_O_URL="https://www.shiksha.com/engineering/aeronautical-engineering-chp"
PCOMBA_C_URL="https://www.shiksha.com/engineering/aeronautical-engineering-courses-chp"
PCOMBA_S_URL="https://www.shiksha.com/engineering/aeronautical-engineering-syllabus-chp"
PCOMBA_CAREER_URL = "https://www.shiksha.com/engineering/aeronautical-engineering-career-chp"
PCOMBA_ADDMISSION_URL="https://www.shiksha.com/engineering/aeronautical-engineering-admission-chp"
PCOMBA_FEES_URL = "https://www.shiksha.com/engineering/computer-science-engineering-fees-chp"
PCOMBA_PAID_URL = "https://www.shiksha.com/engineering/articles/why-engineering-is-still-a-highly-paid-career-stream-blogId-144603"
PCOMBA_5YEARS_URL = "https://www.shiksha.com/engineering/articles/why-engineering-is-still-a-highly-paid-career-stream-blogId-144603"
PCOMBA_JEEVSBITSAK_URL = "https://www.shiksha.com/all-you-need-to-know-about-aeronautical-engineering-salary-articlepage-158425"
PCOMBA_Q_URL = "https://www.shiksha.com/tags/aeronautical-engineering-tdp-197"
PCOMBA_QD_URL="https://www.shiksha.com/tags/aeronautical-engineering-tdp-197?type=discussion"


def create_driver():
    options = Options()

    # Mandatory for GitHub Actions
    # options.add_argument("--headless=new")
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
    # options.binary_location = "/usr/bin/chromium"

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

    soup = BeautifulSoup(driver.page_source, "html.parser")
    section = soup.find("section", id="chp_section_overview")

    data = {}
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        data["title"]=h1
    else:
        pass

    # ==============================
    # UPDATED DATE
    # ==============================
    updated_span = section.find("span")
    if updated_span:
        data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # ==============================
    # AUTHOR INFO
    # ==============================
    author_data = {}
    author_block = section.find("div", class_="c2675e")

    if author_block:
        author_link = author_block.find("a")
        role_span = author_block.find("span", class_="cbbdad")

        author_data["name"] = author_link.get_text(strip=True) if author_link else None
        author_data["profile_url"] = author_link["href"] if author_link else None
        author_data["role"] = role_span.get_text(strip=True) if role_span else None

    data["author"] = author_data

    # ==============================
    # MAIN OVERVIEW CONTENT
    # ==============================
    overview_section = soup.find(id="wikkiContents_chp_section_overview_0")
    data["overview"] = extract_rich_content(overview_section) if overview_section else {}

    # ==============================
    # FAQs
    # ==============================
    faqs = []
    faq_section = section.find("div", class_="sectional-faqs")

    if faq_section:
        questions = faq_section.find_all("div", class_="ea1844")
        answers = faq_section.find_all("div", class_="commentContent")

        for q, a in zip(questions, answers):
            question = q.get_text(" ", strip=True).replace("Q:", "").strip()
            answer = a.get_text(" ", strip=True).replace("A:", "").strip()
            faqs.append({"question": question, "answer": answer})

    data["faqs"] = faqs

    # ==============================
    # ELIGIBILITY SECTION
    # ==============================
    eligibility_section = soup.find("section", id="chp_section_eligibility")
    eligibility_data = {
        "title": None,
        "content": {},
        "faqs": []
    }

    if eligibility_section:
        # Section Title
        title_tag = eligibility_section.find("h2")
        eligibility_data["title"] = title_tag.get_text(" ", strip=True) if title_tag else None

        # Main Wiki Content
        wiki_content = eligibility_section.find("div", class_="wikkiContents")
        if wiki_content:
            eligibility_data["content"] = extract_rich_content(wiki_content)

        # Eligibility FAQs
        faq_section = eligibility_section.find("div", class_="sectional-faqs")
        if faq_section:
            questions = faq_section.find_all("div", class_="ea1844")
            answers = faq_section.find_all("div", class_="commentContent")
            for q, a in zip(questions, answers):
                eligibility_data["faqs"].append({
                    "question": q.get_text(" ", strip=True).replace("Q:", "").strip(),
                    "answer": a.get_text(" ", strip=True).replace("A:", "").strip()
                })

    data["eligibility"] = eligibility_data

    # ==============================
    # POPULAR EXAMS SECTION
    # ==============================
    popular_exams_section = soup.find("section", id="chp_section_popularexams")
    popular_exams_data = {
        "title": None,
        "content": {},
    }

    if popular_exams_section:
        title_tag = popular_exams_section.find("h2")
        popular_exams_data["title"] = title_tag.get_text(" ", strip=True) if title_tag else None

        wiki_content = popular_exams_section.find("div", class_="wikkiContents")
        if wiki_content:
            popular_exams_data["content"] = extract_rich_content(wiki_content)

    data["popular_exams"] = popular_exams_data
    # ==============================
    # TOP COURSES & SPECIALIZATIONS SECTION
    # ==============================
    top_courses_section = soup.find("section", id="chp_section_topratecourses")
    top_courses_data = {
        "title": None,
        "content": {},
    }

    if top_courses_section:
        # Section title
        title_tag = top_courses_section.find("h2")
        top_courses_data["title"] = title_tag.get_text(" ", strip=True) if title_tag else None

        # Wiki content inside the section
        wiki_content = top_courses_section.find("div", class_="wikkiContents")
        if wiki_content:
            top_courses_data["content"] = extract_rich_content(wiki_content)

    # Add it to the main data dictionary
    data["top_courses"] = top_courses_data
    # ==============================
    # COURSE SYLLABUS SECTION
    # ==============================
    syllabus_section = soup.find("section", id="chp_section_coursesyllabus")

    syllabus_data = {
        "title": None,
        "content": {},
        "faqs": []
    }

    if syllabus_section:
        # Section Title
        title_tag = syllabus_section.find("h2")
        syllabus_data["title"] = title_tag.get_text(" ", strip=True) if title_tag else None

        # Main Wiki Content
        wiki_content = syllabus_section.find(
            "div", id=lambda x: x and x.startswith("wikkiContents_chp_section_coursesyllabus")
        )
        if wiki_content:
            syllabus_data["content"] = extract_rich_content(wiki_content)

        # ==============================
        # SYLLABUS FAQs
        # ==============================
        faq_section = syllabus_section.find("div", class_="sectional-faqs")
        if faq_section:
            questions = faq_section.find_all("div", class_="ea1844")
            answers = faq_section.find_all("div", class_="commentContent")

            for q, a in zip(questions, answers):
                syllabus_data["faqs"].append({
                    "question": q.get_text(" ", strip=True).replace("Q:", "").strip(),
                    "answer": a.get_text(" ", strip=True).replace("A:", "").strip()
                })

    data["course_syllabus"] = syllabus_data
    # ==============================
    # POPULAR COLLEGES SECTION
    # ==============================
    popular_colleges_section = soup.find("section", id="chp_section_popularcolleges")

    popular_colleges_data = {
        "title": None,
        "content": {}
    }

    if popular_colleges_section:
        # Section Title
        title_tag = popular_colleges_section.find("h2")
        popular_colleges_data["title"] = (
            title_tag.get_text(" ", strip=True) if title_tag else None
        )

        # Main Wiki Content
        wiki_content = popular_colleges_section.find(
            "div",
            id=lambda x: x and x.startswith("wikkiContents_chp_section_popularcolleges")
        )

        if wiki_content:
            popular_colleges_data["content"] = extract_rich_content(wiki_content)

    data["popular_colleges"] = popular_colleges_data

    # ==============================
    # SALARY SECTION
    # ==============================
    salary_section = soup.find("section", id="chp_section_salary")

    salary_data = {
        "title": None,
        "content": {},
        "faqs": []
    }

    if salary_section:
        # Section Title
        title_tag = salary_section.find("h2")
        salary_data["title"] = (
            title_tag.get_text(" ", strip=True) if title_tag else None
        )

        # Main Wiki Content
        wiki_content = salary_section.find(
            "div",
            id=lambda x: x and x.startswith("wikkiContents_chp_section_salary")
        )
        if wiki_content:
            salary_data["content"] = extract_rich_content(wiki_content)

        # ==============================
        # SALARY FAQs
        # ==============================
        faq_section = salary_section.find("div", class_="sectional-faqs")
        if faq_section:
            questions = faq_section.find_all("div", class_="ea1844")
            answers = faq_section.find_all("div", class_="commentContent")

            for q, a in zip(questions, answers):
                salary_data["faqs"].append({
                    "question": q.get_text(" ", strip=True).replace("Q:", "").strip(),
                    "answer": a.get_text(" ", strip=True).replace("A:", "").strip()
                })

    data["salary"] = salary_data
    # ==============================
    # COURSE FAQs SECTION
    # ==============================
    faqs_section = soup.find("section", id="chp_section_faqs")

    course_faqs_data = {
        "title": None,
        "intro": {"blocks": []},
        "faqs": []
    }

    if faqs_section:
        # Section Title
        title_tag = faqs_section.find("h2")
        course_faqs_data["title"] = (
            title_tag.get_text(" ", strip=True) if title_tag else None
        )

        # Intro content (top wiki content)
        intro_content = faqs_section.find(
            "div",
            id=lambda x: x and x.startswith("wikkiContents_chp_section_faqs")
        )
        if intro_content:
            course_faqs_data["intro"] = extract_rich_content(intro_content)

        # Actual FAQs
        faq_container = faqs_section.find("div", class_="sectional-faqs")
        if faq_container:
            questions = faq_container.find_all("div", class_="ea1844")
            answers = faq_container.find_all("div", class_="commentContent")

            for q, a in zip(questions, answers):
                question_text = (
                    q.get_text(" ", strip=True)
                    .replace("Q:", "")
                    .strip()
                )

                answer_content = extract_rich_content(a)

                course_faqs_data["faqs"].append({
                    "question": question_text,
                    "answer": answer_content
                })

    data["course_faqs"] = course_faqs_data



    return data


def extract_rich_content(container):
    if not container:
        return {"blocks": []}

    content = {"blocks": []}

    def parse_node(node):
        # HEADINGS
        if node.name in ["h2", "h3", "h4"]:
            content["blocks"].append({"type": "heading", "value": node.get_text(" ", strip=True)})
        # PARAGRAPHS
        elif node.name == "p":
            text = node.get_text(" ", strip=True)
            if text:
                content["blocks"].append({"type": "paragraph", "value": text})
        # LISTS
        elif node.name == "ul":
            items = [li.get_text(" ", strip=True) for li in node.find_all("li")]
            if items:
                content["blocks"].append({"type": "list", "value": items})
        # TABLES
        elif node.name == "table":
            table_data = []
            for row in node.find_all("tr"):
                cols = [c.get_text(" ", strip=True) for c in row.find_all(["th", "td"])]
                if cols:
                    table_data.append(cols)
            if table_data:
                content["blocks"].append({"type": "table", "value": table_data})
        # LINKS
        elif node.name == "a" and node.get("href"):
            content["blocks"].append({
                "type": "link",
                "value": {"text": node.get_text(" ", strip=True), "url": node["href"]}
            })
        # IFRAME
        elif node.name == "iframe":
            src = node.get("src") or node.get("data-original")
            if src:
                content["blocks"].append({"type": "iframe", "value": src})
        # If node is a container, recursively parse its children
        elif node.name in ["div", "section", "span"]:
            for child in node.find_all(recursive=False):
                parse_node(child)

    # Start parsing from top-level container
    for node in container.find_all(recursive=False):
        parse_node(node)

    return content

def extract_rich_content(container):
    content = {"blocks": []}

    def parse_node(node):
        if node.name in ["h2", "h3", "h4"]:
            text = node.get_text(" ", strip=True)
            if text:
                content["blocks"].append({"type": "heading", "value": text})
        elif node.name == "p":
            text = node.get_text(" ", strip=True)
            if text:
                content["blocks"].append({"type": "paragraph", "value": text})
        elif node.name == "table":
            table_data = []
            for row in node.find_all("tr"):
                cols = [c.get_text(" ", strip=True) for c in row.find_all(["th", "td"])]
                if cols:
                    table_data.append(cols)
            if table_data:
                content["blocks"].append({"type": "table", "value": table_data})
        elif node.name == "a" and node.get("href"):
            content["blocks"].append({
                "type": "link",
                "value": {"text": node.get_text(" ", strip=True), "url": node["href"]}
            })
        elif node.name == "iframe":
            src = node.get("src") or node.get("data-original")
            if src:
                content["blocks"].append({"type": "iframe", "value": src})
        # recurse on children
        for child in node.find_all(recursive=False):
            parse_node(child)

    parse_node(container)

    return content

def extract_courses__data(driver):
    driver.get(PCOMBA_C_URL)
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.find("section", id="chp_courses_overview")
    if not section:
        return {}

    data = {}
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        data["title"]=h1
    else:
        pass

    # ==============================
    # UPDATED DATE
    # ==============================
    updated_span = section.find("span")
    data["updated_on"] = (
        updated_span.get_text(strip=True) if updated_span else None
    )

    # ==============================
    # AUTHOR INFO
    # ==============================
    author_data = {}
    author_block = section.find("div", class_="c2675e")

    if author_block:
        author_link = author_block.find("a")
        role_span = author_block.find("span", class_="cbbdad")
        img = author_block.find("img")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role_span.get_text(strip=True) if role_span else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # ==============================
    # MAIN COURSE OVERVIEW CONTENT
    # ==============================
    container = section.find(
        "div",
        id=lambda x: x and x.startswith("wikkiContents_chp_courses_overview")
    )

    data["content"] = (
        extract_rich_content(container)
        if container
        else {"blocks": []}
    )

    return data
def extract_rich_content(container):
    if not container:
        return {"blocks": []}

    content = {"blocks": []}

    def parse_node(node):
        # --------------------
        # HEADINGS
        # --------------------
        if node.name in ["h2", "h3", "h4"]:
            content["blocks"].append({
                "type": "heading",
                "value": node.get_text(" ", strip=True)
            })
            return

        # --------------------
        # PARAGRAPHS (skip if inside table)
        # --------------------
        if node.name == "p":
            if node.find_parent("table"):
                return
            text = node.get_text(" ", strip=True)
            if text:
                content["blocks"].append({
                    "type": "paragraph",
                    "value": text
                })
            return

        # --------------------
        # LISTS
        # --------------------
        if node.name == "ul":
            items = [
                li.get_text(" ", strip=True)
                for li in node.find_all("li", recursive=False)
            ]
            if items:
                content["blocks"].append({
                    "type": "list",
                    "value": items
                })
            return

        # --------------------
        # TABLES (important: stop recursion)
        # --------------------
        if node.name == "table":
            table_data = []
            for row in node.find_all("tr"):
                cols = [
                    c.get_text(" ", strip=True)
                    for c in row.find_all(["th", "td"])
                ]
                if cols:
                    table_data.append(cols)

            if table_data:
                content["blocks"].append({
                    "type": "table",
                    "value": table_data
                })
            return  # 🚨 no child parsing

        # --------------------
        # LINKS (only standalone)
        # --------------------
        if node.name == "a" and node.get("href"):
            if node.find_parent("table"):
                return
            content["blocks"].append({
                "type": "link",
                "value": {
                    "text": node.get_text(" ", strip=True),
                    "url": node["href"]
                }
            })
            return

        # --------------------
        # IFRAMES
        # --------------------
        if node.name == "iframe":
            src = node.get("src") or node.get("data-original")
            if src:
                content["blocks"].append({
                    "type": "iframe",
                    "value": src
                })
            return

        # --------------------
        # CONTAINER TAGS
        # --------------------
        if node.name in ["div", "section", "span"]:
            for child in node.find_all(recursive=False):
                parse_node(child)

    # start parsing
    for node in container.find_all(recursive=False):
        parse_node(node)

    return content

def scrape_syllabus_section(driver):
    driver.get(PCOMBA_S_URL)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    syllabus_data = {}

    # Main syllabus section
    syllabus_section = soup.find("section", id="chp_syllabus_overview")
    if not syllabus_section:
        return syllabus_data

    # ---------------------------------
    # BASIC INFO
    # ---------------------------------
    title = soup.find("h1")
    syllabus_data["title"] = title.get_text(strip=True) if title else None

    updated_span = syllabus_section.select_one("div.d957ae span")
    syllabus_data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # AUTHOR INFO
    author_name = syllabus_section.select_one("p.e9801a a")
    author_role = syllabus_section.select_one("p.e9801a span.cbbdad")
    syllabus_data["author"] = {
        "name": author_name.get_text(strip=True) if author_name else None,
        "profile_url": author_name["href"] if author_name else None,
        "role": author_role.get_text(strip=True) if author_role else None
    }

    # ---------------------------------
    # OVERVIEW SECTION CONTENT
    # ---------------------------------
    overview_block = syllabus_section.select_one("#wikkiContents_chp_syllabus_overview_0")
    if overview_block:
        syllabus_data["overview"] = extract_rich_content(overview_block)
    else:
        syllabus_data["overview"] = {"blocks": []}

    # ---------------------------------
    # LINKS FROM OVERVIEW
    # ---------------------------------
    overview_links = []
    if overview_block:
        for a in overview_block.find_all("a", href=True):
            overview_links.append({
                "text": a.get_text(strip=True),
                "url": a["href"]
            })
    syllabus_data["overview_links"] = overview_links

    # ---------------------------------
    # FULL SECTION TEXT
    # ---------------------------------
    text_parts = []
    for p in syllabus_section.find_all(["p", "li"], limit=200):
        text_parts.append(p.get_text(" ", strip=True))
    syllabus_data["full_section_text"] = "\n".join(text_parts)

    # ---------------------------------
    # FAQs
    # ---------------------------------
    syllabus_data["faqs"] = extract_faqs(syllabus_section)

    # =====================================================
    # 🔥 DETAILED ECE SYLLABUS SECTION (FIXED - USING DIV, NOT SECTION)
    # =====================================================
    detailed_div = soup.find("div", id="wikkiContents_chp_syllabus_popularcolleges_0")
    if detailed_div:
        syllabus_data["detailed_ece_syllabus"] = extract_rich_content(detailed_div)
    else:
        syllabus_data["detailed_ece_syllabus"] = {"blocks": []}

    # =====================================================
    # 🔥 CORE AND ELECTIVE SUBJECTS SECTION (FIXED - USING DIV, NOT SECTION)
    # =====================================================
    core_elective_div = soup.find("div", id="wikkiContents_chp_syllabus_popularexams_0")
    if core_elective_div:
        syllabus_data["core_elective_subjects"] = extract_rich_content(core_elective_div)
    else:
        syllabus_data["core_elective_subjects"] = {"blocks": []}

    # =====================================================
    # 🔥 POPULAR BOOKS SECTION (FIXED - USING DIV, NOT SECTION)
    # =====================================================
    books_div = soup.find("div", id="wikkiContents_chp_syllabus_popularspecialization_0")
    if books_div:
        syllabus_data["recommended_books"] = extract_rich_content(books_div)
    else:
        syllabus_data["recommended_books"] = {"blocks": []}

    return syllabus_data


def extract_rich_content(container):
    """Extract all content (headings, paragraphs, tables, lists) in order"""
    if not container:
        return {"blocks": []}

    content = {"blocks": []}

    def parse_node(node):
        if node is None:
            return

        # HEADINGS
        if node.name in ["h2", "h3", "h4"]:
            text = node.get_text(" ", strip=True)
            if text:
                content["blocks"].append({
           
                 
                    "text": text,
                  
                })
            return

        # PARAGRAPHS
        if node.name == "p":
            if node.find_parent("table"):
                return
            
            text = node.get_text(" ", strip=True)
            if text and len(text) > 10:
                block = {
                    "type": "paragraph",
                    "text": text
                }
                
                # Extract links from paragraph
                links = []
                for a in node.find_all("a", href=True):
                    links.append({
                        "text": a.get_text(strip=True),
                        "url": a["href"]
                    })
                
                if links:
                    block["links"] = links
                
                content["blocks"].append(block)
            return

        # TABLES
        if node.name == "table":
            # Get previous heading for context
            prev_heading = None
            # Look for the nearest previous heading
            prev_sibling = node.find_previous(["h2", "h3", "h4"])
            if prev_sibling:
                prev_heading = prev_sibling.get_text(" ", strip=True)
            
            # Parse table
            table_data = parse_table_data(node)
            
            if table_data:
                content["blocks"].append({
                   
                    "caption": prev_heading or "",
                    "data": table_data
                })
            return

        # LISTS
        if node.name in ["ul", "ol"]:
            items = []
            for li in node.find_all("li", recursive=False):
                item_text = li.get_text(" ", strip=True)
                if item_text:
                    items.append(item_text)
            
            if items:
                content["blocks"].append({
                    "type": "list",
                    "items": items
                })
            return

        # DIVS
        if node.name == "div":
            # Skip gradient/view more divs
            if "gradient-col" in node.get("class", []):
                return
            
            # Recursively parse other divs
            for child in node.find_all(recursive=False):
                parse_node(child)
            return

    # Start parsing from the container
    for child in container.find_all(recursive=False):
        parse_node(child)

    return content


def parse_table_data(table):
    """Parse table data based on table type"""
    if not table:
        return None
    
    # Check if it's a semester-wise table
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    
    # Semester table detection
    semester_keywords = ["semester", "Semester", "sem", "Sem"]
    is_semester_table = any(any(keyword in header for keyword in semester_keywords) for header in headers)
    
    if is_semester_table:
        return parse_semester_table(table)
    else:
        return parse_general_table(table)


def parse_semester_table(table):
    """Parse semester-wise syllabus table"""
    data = {}
    current_semester = None
    
    for row in table.find_all("tr"):
        th = row.find("th")
        if th:
            th_text = th.get_text(strip=True)
            # Check if it's a semester header
            if any(keyword in th_text for keyword in ["Semester", "semester", "Sem", "sem"]):
                current_semester = th_text
                data[current_semester] = []
                continue
        
        if current_semester:
            subjects = []
            for td in row.find_all("td"):
                subject_text = td.get_text(" ", strip=True)
                if subject_text and subject_text not in ["-", "&nbsp;"]:
                    subject_text = ' '.join(subject_text.split())
                    subjects.append(subject_text)
            
            if subjects:
                data[current_semester].extend(subjects)
    
    return data


def parse_general_table(table):
    """Parse general tables (subjects, books, etc.)"""
    data = {
        "headers": [],
        "rows": []
    }
    
    # Get headers
    header_row = table.find("tr")
    if header_row:
        data["headers"] = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
    
    # Get rows
    for row in table.find_all("tr")[1:]:  # Skip header
        cols = row.find_all(["td", "th"])
        if cols:
            row_data = {}
            for i, col in enumerate(cols):
                # Use header text as key if available
                if i < len(data["headers"]):
                    key = data["headers"][i]
                else:
                    key = f"col_{i}"
                
                row_data[key] = col.get_text(" ", strip=True)
            
            data["rows"].append(row_data)
    
    return data


def extract_faqs(section):
    """Extract FAQs from the section"""
    faqs = []
    faq_blocks = section.select(".sectional-faqs > div")
    
    i = 0
    while i < len(faq_blocks):
        q_block = faq_blocks[i]
        a_block = faq_blocks[i + 1] if i + 1 < len(faq_blocks) else None
        
        question = q_block.get_text(" ", strip=True).replace("Q:", "").strip()
        
        answer = None
        if a_block:
            answer_div = a_block.select_one(".cmsAContent")
            if answer_div:
                answer = answer_div.get_text("\n", strip=True)
        
        if question and answer:
            faqs.append({
                "question": question,
                "answer": answer
            })
        
        i += 2
    
    return faqs
  

def scrape_career_overview(driver):
    driver.get(PCOMBA_CAREER_URL)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    data = {
        "title":None,
        "meta": {},
        "intro": [],
        "sections": []
    }
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        data["title"]=h1
    else:
        pass
    section = soup.find("section", id="chp_career_overview")
    if not section:
        return data

    # ---------- META (date + author) ----------
    updated = section.select_one(".d957ae div span")
    author = section.select_one(".e9801a a")

    data["meta"] = {
        "updated_on": updated.get_text(strip=True) if updated else "",
        "author": author.get_text(strip=True) if author else ""
    }

    content_block = section.find(
        "div", id="wikkiContents_chp_career_overview_0"
    )
    if not content_block:
        return data

    container = content_block.find("div")

    current_section = None

    for tag in container.children:

        if not getattr(tag, "name", None):
            continue

        # ---------- INTRO (before first h2) ----------
        if tag.name == "p" and not current_section:
            text = unescape(tag.get_text(" ", strip=True))
            if len(text) > 30:
                data["intro"].append(text)
            continue

        # ---------- NEW SECTION ----------
        if tag.name in ["h2", "h3"]:
            current_section = {
                "title": unescape(tag.get_text(" ", strip=True)),
                "content": [],
                "tables": []
            }
            data["sections"].append(current_section)
            continue

        if not current_section:
            continue

        # ---------- PARAGRAPHS ----------
        if tag.name == "p":
            text = unescape(tag.get_text(" ", strip=True))
            if (
                len(text) > 30
                and not text.lower().startswith("note")
                and "source" not in text.lower()
            ):
                current_section["content"].append(text)

        # ---------- TABLES ----------
        if tag.name == "table":
            table_data = []
            headers = [
                unescape(th.get_text(" ", strip=True))
                for th in tag.find_all("th")
            ]

            for row in tag.find_all("tr")[1:]:
                cols = row.find_all(["td", "th"])
                if not cols:
                    continue

                row_obj = {}
                for i, col in enumerate(cols):
                    text = unescape(col.get_text(" ", strip=True))
                    key = headers[i] if i < len(headers) else f"col_{i}"
                    row_obj[key] = text

                table_data.append(row_obj)

            if table_data:
                current_section["tables"].append(table_data)

    return data


def scrape_admission_overview(driver):
    driver.get(PCOMBA_ADDMISSION_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "overview": [],
        "sections": []
    }

    # ---------------- TITLE ----------------
    # Try to find title - you might need to adjust this selector based on actual page
    title = soup.find("h1")
    if not title:
        # Try other common title selectors
        title = soup.find("div", class_=lambda x: x and ("title" in x or "heading" in x))
    data["title"] = title.get_text(strip=True) if title else "Computer Science Engineering Admission Overview"

    # ---------------- META SECTION ----------------
    section1 = soup.find(id="chp_admission_overview")
    if section1:
        # Updated date - looking for "Updated on Jun 19, 2025 12:14 IST"
        updated_div = section1.select_one(".d957ae div")
        if updated_div:
            text = updated_div.get_text(strip=True)
            if "Updated on" in text:
                # Extract just the date part
                date_part = text.split("Updated on")[-1].strip()
                data["updated_on"] = date_part

        # Author info
        author_block = section1.select_one(".c2675e")
        if author_block:
            author_link = author_block.select_one("p.e9801a a")
            author_role = author_block.select_one("p.e9801a span.cbbdad")
            
            data["author"] = {
                "name": author_link.get_text(strip=True) if author_link else None,
                "profile_url": author_link["href"] if author_link else None,
                "role": author_role.get_text(strip=True) if author_role else None
            }

    # ---------------- MAIN CONTENT ----------------
    section = soup.find("div", id="wikkiContents_chp_admission_overview_0")
    if not section:
        return data

    main_container = section.find("div")
    if not main_container:
        return data

    # Get overview/intro paragraphs (everything before first h2)
    intro_paras = []
    for el in main_container.find_all(["p", "h2"], recursive=False):
        if el.name == "h2":
            break  # stop at first heading
        if el.name == "p":
            text = el.get_text(" ", strip=True)
            if text:
                intro_paras.append(text)
    
    data["overview"] = intro_paras

    # Process all sections with headings
    current_section = None
    current_subsections = []
    
    # Process all elements
    elements = main_container.find_all(["h2", "h3", "p", "ul", "table", "div"], recursive=False)
    
    for element in elements:
        if element.name == "h2":
            # Save previous section if exists
            if current_section:
                if current_subsections:
                    current_section["subsections"] = current_subsections
                data["sections"].append(current_section)
            
            # Start new section
            current_section = {
                "heading": element.get_text(strip=True),
              
                "content": [],
                "subsections": []
            }
            current_subsections = []
            
        elif element.name == "h3" and current_section:
            # Start new subsection
            current_subsections.append({
                "heading": element.get_text(strip=True),
               
                "content": []
            })
            
        elif element.name == "p":
            # Get text content without walrus operator
            text_content = element.get_text(" ", strip=True)
            if text_content:  # Only add if there's actual text
                # Add text content
                if current_subsections:
                    # Add to latest subsection
                    current_subsections[-1]["content"].append({"text": text_content})
                elif current_section:
                    # Add to main section
                    current_section["content"].append({"text": text_content})
                
        elif element.name == "ul" and current_section:
            items = [li.get_text(" ", strip=True) for li in element.find_all("li") if li.get_text(strip=True)]
            if items:
                if current_subsections:
                    current_subsections[-1]["content"].append({"items": items})
                else:
                    current_section["content"].append({"items": items})
                    
        elif element.name == "table" and current_section:
            # Extract table data
            rows = []
            for row in element.find_all("tr"):
                row_data = []
                for cell in row.find_all(["th", "td"]):
                    # Handle cell content - get text and also check for links
                    cell_text = cell.get_text(" ", strip=True)
                    
                    # Check for links in the cell
                    links = []
                    for link in cell.find_all("a"):
                        links.append({
                            "text": link.get_text(strip=True),
                      
                        })
                    
                    row_data.append({
                        "text": cell_text,
                     
                    })
                
                if row_data:  # Only add non-empty rows
                    rows.append(row_data)
            
            if rows:
                if current_subsections:
                    current_subsections[-1]["content"].append({"table": rows})
                else:
                    current_section["content"].append({"table": rows})
        
        elif element.name == "div" and element.get("class") and "vcmsEmbed" in element.get("class", []):
            # Handle embedded videos
            iframe = element.find("iframe")
            if iframe:
                video_data = {
                    "type": "video",
                    "src": iframe.get("src", ""),
                    "title": iframe.get("title", ""),
                    "width": iframe.get("width", ""),
                    "height": iframe.get("height", "")
                }
                if current_subsections:
                    current_subsections[-1]["content"].append(video_data)
                elif current_section:
                    current_section["content"].append(video_data)

    # Add the last section
    if current_section:
        if current_subsections:
            current_section["subsections"] = current_subsections
        data["sections"].append(current_section)

    return data

def scrape_blog_paid(driver):
    driver.get(PCOMBA_PAID_URL)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    blog_data = {}
    
    # ---------------------------------
    # AUTHOR INFO (FIXED)
    # ---------------------------------
    title = soup.find("div",class_="flx-box mA")
    if title:
        h1 = title.find("h1").text.strip()
        blog_data["title"]= h1
    else:
        pass
    author = soup.find("div",class_="adp_usr_dtls")
    if author:
        name = author.find("a").text.strip()
        blog_data["Author_name"]= name
    else:
        pass
    author_data = {}
    author_div = soup.find("div", class_="adp_user")
    
    if author_div:
        author_name_tag = author_div.find("a", href=lambda x: x and "author" in x)
        author_link = author_div.find("a", class_="user-img")
        author_role = author_div.find("div", class_="user_expert_level")
        

        author_data = {
           
            "profile_url": author_name_tag["href"] if author_name_tag else None,
            "image": author_link.find("img")["src"] if author_link and author_link.find("img") else None,
            "role": author_role.get_text(strip=True) if author_role else None
        }
    
    blog_data["author"] = author_data
    
    # ---------------------------------
    # UPDATED DATE (FIXED)
    # ---------------------------------
    updated_div = soup.find("div", class_="blogdata_user")
    if updated_div:
        # Extract only the date part
        updated_text = updated_div.get_text(strip=True)
        # Remove "Updated on " and any extra text after date
        if "Updated on " in updated_text:
            date_part = updated_text.replace("Updated on ", "")
            # Take only the date part (assuming format like "Nov 26, 2025 12:21 IST")
            # Split by space and take first 5 parts (Month Day, Year Time Timezone)
            parts = date_part.split()
            if len(parts) >= 5:
                blog_data["updated_on"] = " ".join(parts[:5])
            else:
                blog_data["updated_on"] = date_part
        else:
            blog_data["updated_on"] = updated_text
    else:
        blog_data["updated_on"] = None
    
    # ---------------------------------
    # BLOG SUMMARY
    # ---------------------------------
    summary_div = soup.find("div", class_="blogSummary")
    blog_data["summary"] = summary_div.get_text(strip=True) if summary_div else None
    
    # ---------------------------------
    # MAIN BLOG CONTENT
    # ---------------------------------
    main_content_div = soup.find("div", id=lambda x: x and x.startswith("blogId-"))
    
    if main_content_div:
        blog_data["content"] = extract_blog_content(main_content_div)
    else:
        blog_data["content"] = {"sections": []}
    
    return blog_data


def extract_blog_content(container):
    """
    Extract structured content from blog article
    """
    if not container:
        return {"sections": []}
    
    content = {"sections": []}
    
    # Find all wikkiContents divs
    wikki_divs = container.find_all("div", id=lambda x: x and x.startswith("wikkiContents_"))
    
    for div in wikki_divs:
        # Skip empty divs
        if not div.get_text(strip=True):
            continue
            
        section_content = extract_section_content(div)
        if section_content:
            content["sections"].append(section_content)
    
    # Also extract content from other important divs
    # Look for video embeds
    video_embeds = container.find_all("div", class_="vcmsEmbed")
    for embed in video_embeds:
        section_content = extract_video_content(embed)
        if section_content:
            content["sections"].append(section_content)
    
    # Look for video reels/carousel
    reels_div = container.find("div", id="reelsWidget")
    if reels_div:
        section_content = extract_video_reels(reels_div)
        if section_content:
            content["sections"].append(section_content)
    
    return content


def extract_section_content(section_div):
    """
    Extract content from a single section div
    """
    if not section_div:
        return None
    
    section_data = {}
    
    # Check for heading in this section
    heading = section_div.find(["h2", "h3", "h4"])
    if heading:
        section_data["heading"] = {
            "text": heading.get_text(strip=True),
            "level": heading.name,
            "id": heading.get("id", "")
        }
    
    # Extract paragraphs
    paragraphs = []
    for p in section_div.find_all("p"):
        if p.find_parent("table"):
            continue
        
        text = p.get_text(" ", strip=True)
        if text and len(text) > 5:  # Reduced minimum length
            para_data = {"text": text}
            
            # Extract links from paragraph
            links = []
            for a in p.find_all("a", href=True):
                link_text = a.get_text(strip=True)
                if link_text:
                    links.append({
                        "text": link_text,
                        "url": a["href"]
                    })
            
            if links:
                para_data["links"] = links
            
            paragraphs.append(para_data)
    
    if paragraphs:
        section_data["paragraphs"] = paragraphs
    
    # Extract lists
    lists = []
    for list_tag in section_div.find_all(["ul", "ol"]):
        if list_tag.find_parent("table"):
            continue
        
        list_items = []
        for li in list_tag.find_all("li"):
            item_text = li.get_text(strip=True)
            if item_text:
                
                # Extract links from list items
                item_links = []
                for a in li.find_all("a", href=True):
                    link_text = a.get_text(strip=True)
                    if link_text:
                        item_links.append({
                            "text": link_text,
                            "url": a["href"]
                        })
                
                list_item = {"text": item_text}
                if item_links:
                    list_item["links"] = item_links
                
                list_items.append(list_item)
        
        if list_items:
            lists.append({
                "type": "ordered" if list_tag.name == "ol" else "unordered",
                "items": list_items
            })
    
    if lists:
        section_data["lists"] = lists
    
    # Extract tables
    tables = []
    for table in section_div.find_all("table"):
        table_data = parse_blog_table(table)
        if table_data:
            tables.append(table_data)
    
    if tables:
        section_data["tables"] = tables
    
    # Extract images (FIXED - getting src properly)
    images = []
    for img_div in section_div.find_all("div", class_=["photo-widget-full", "figure"]):
        img_tag = img_div.find("img")
        if img_tag:
            # Get src from img tag or from source tag inside picture
            src = img_tag.get("src")
            if not src:
                # Check for source tag
                source_tag = img_div.find("source")
                if source_tag:
                    src = source_tag.get("srcset")
            
            if src:
                image_data = {
                    "src": src,
                    "alt": img_tag.get("alt", ""),
                    "width": img_tag.get("width"),
                    "height": img_tag.get("height")
                }
                
                # Get caption if available
                caption = img_div.find(["p", "figcaption"])
                if caption:
                    image_data["caption"] = caption.get_text(strip=True)
                
                images.append(image_data)
    
    if images:
        section_data["images"] = images
    
    # Only return if there's actual content
    if any(key in section_data for key in ["heading", "paragraphs", "lists", "tables", "images"]):
        return section_data
    
    return None


def extract_video_content(video_div):
    """
    Extract video/iframe content
    """
    if not video_div:
        return None
    
    videos = []
    for iframe in video_div.find_all("iframe"):
        src = iframe.get("src")
        if src:
            video_data = {
                "src": src,
                "title": iframe.get("title", ""),
                "width": iframe.get("width"),
                "height": iframe.get("height")
            }
            videos.append(video_data)
    
    if videos:
        return {"videos": videos}
    
    return None


def extract_video_reels(reels_div):
    """
    Extract video reels/carousel content
    """
    if not reels_div:
        return None
    
    video_reels = []
    for li in reels_div.find_all("li", class_="thumbnailListener"):
        video_info = {}
        
        # Extract YouTube thumbnail
        img = li.find("img")
        if img:
            video_info["thumbnail"] = img.get("src")
            video_info["alt"] = img.get("alt", "")
        
        # Extract video title
        title_div = li.find("div", class_="ada2b9")
        if title_div:
            video_info["title"] = title_div.get_text(strip=True)
        
        # Extract iframe
        iframe = li.find("iframe")
        if iframe:
            video_info["embed_url"] = iframe.get("src")
        
        if video_info:
            video_reels.append(video_info)
    
    if video_reels:
        return {"video_reels": video_reels}
    
    return None


def parse_blog_table(table):
    """
    Parse blog article tables
    """
    if not table:
        return None
    
    table_data = {
        "headers": [],
        "rows": []
    }
    
    # Get headers from first row
    header_row = table.find("tr")
    if header_row:
        table_data["headers"] = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
    
    # Get data rows
    for row in table.find_all("tr")[1:]:  # Skip header row
        cols = row.find_all(["td", "th"])
        if cols:
            row_data = {}
            
            for i, col in enumerate(cols):
                # Use header as key if available
                if i < len(table_data["headers"]):
                    key = table_data["headers"][i]
                else:
                    key = f"col_{i}"
                
                cell_text = col.get_text(" ", strip=True)
                
                # Extract links from cell
                links = []
                for a in col.find_all("a", href=True):
                    link_text = a.get_text(strip=True)
                    if link_text:
                        links.append({
                            "text": link_text,
                            "url": a["href"]
                        })
                
                if links:
                    row_data[key] = {
                        "text": cell_text,
                        "links": links
                    }
                else:
                    row_data[key] = cell_text
            
            table_data["rows"].append(row_data)
    
    return table_data

    
def scrape_fees_overview_json(driver, timeout=30):
    driver.get(PCOMBA_FEES_URL)
    soup = BeautifulSoup(driver.page_source,"html.parser")

    result = {
        "title":None,
        "updated_on": None,
        "author": None,
        "author_profile_url":None,
        "author_designation":None,
        "content": []
    }
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        result["title"]=h1
    else:
        pass

    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        section = wait.until(
            EC.presence_of_element_located((By.ID, "chp_fees_overview"))
        )

        # -------- meta --------
        # ---------- Updated On ----------
        try:
            updated_on = section.find_element(
                By.XPATH, ".//div[contains(text(),'Updated on')]/span"
            ).text.strip()
            result["last_updated"] = updated_on
        except:
            result["last_updated"] = None


        # ---------- Author Details ----------
        try:
            author_block = section.find_element(By.CSS_SELECTOR, ".c2675e")

            author_link = author_block.find_element(By.TAG_NAME, "a")

            result["author"] = author_link.text.strip()
            result["author_profile_url"] = author_link.get_attribute("href")

            try:
                result["author_designation"] = author_block.find_element(
                    By.CSS_SELECTOR, ".cbbdad"
                ).text.strip()
            except:
                result["author_designation"] = None

        except:
            result["author"] = None
            result["author_profile_url"] = None
            result["author_designation"] = None


        # -------- main content --------
        content_root = section.find_element(By.CSS_SELECTOR, ".wikkiContents")

        elements = content_root.find_elements(
            By.XPATH, "./div/*"
        )

        for el in elements:
            tag = el.tag_name.lower()
            text = el.text.strip()

            if not text:
                continue

            # ---- headings ----
            if tag in ["h2", "h3"]:
                result["content"].append({
                    "type": "heading",
                    "level": tag,
                    "text": text
                })

            # ---- paragraphs ----
            elif tag == "p":
                result["content"].append({
                    "type": "paragraph",
                    "text": text
                })

            # ---- tables ----
            elif tag == "table":
                rows = el.find_elements(By.TAG_NAME, "tr")
                table_data = []

                for row in rows[1:]:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 2:
                        table_data.append({
                            "college": cols[0].text.strip(),
                            "fees": cols[1].text.strip()
                        })

                if table_data:
                    result["content"].append({
                        "type": "table",
                        "rows": table_data
                    })

        return result

    except TimeoutException:
    
        return None
    
def scrape_blog_data(driver):
    driver.get(PCOMBA_JEEVSBITSAK_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    result = {
        "title": None,
        "img": None,
        "article_info": {},
        "intro": [],
        "sections": []
    }

    # ---------------- TITLE ----------------
    # Try to find title from meta or h1 tag
    title_tag = soup.find("meta", property="og:title")
    if title_tag:
        result["title"] = title_tag.get("content", "").strip()
    else:
        h1_tag = soup.find("h1")
        if h1_tag:
            result["title"] = h1_tag.get_text(strip=True)

    # ---------------- FEATURED IMAGE ----------------
    img_tag = soup.find("picture")
    if img_tag:
        img = img_tag.find("img")
        if img:
            result["img"] = img.get("src", "")

    # ---------------- METADATA ----------------
    author_section = soup.select_one(".adp_user")

    if author_section:
        result["article_info"]["author"] = {
            "name": author_section.select_one(".adp_usr_dtls a").get_text(strip=True),
            "role": author_section.select_one(".user_expert_level").get_text(strip=True),
            "image": author_section.select_one("img")["src"] if author_section.select_one("img") else None
        }

    # Updated date
    update_span = soup.select_one(".blogdata_user span")
    if update_span:
        result["article_info"]["updated"] = update_span.get_text(strip=True)

    # Summary
    summary_div = soup.select_one("#blogSummary")
    if summary_div:
        result["article_info"]["summary"] = summary_div.get_text(strip=True)

    # ---------------- MAIN CONTENT ----------------
    content_div = soup.select_one("#blogId-158425")

    if not content_div:
        # Try alternative content div
        content_div = soup.select_one(".adpPwa_summary")
    
    if not content_div:
        return result

    # Remove unnecessary elements
    for bad in content_div.select(".b644f8, .predictorContainer, #prefernceWidget, script, style, .DFPRecoWrapper, .photo-widget-full"):
        bad.decompose()

    # Get all wikicontents sections
    wikki_sections = content_div.select(".wikkiContents")

    # Process introduction (content before first h2)
    intro_section = wikki_sections[0] if wikki_sections else None
    if intro_section:
        intro_paragraphs = intro_section.find_all("p")
        for p in intro_paragraphs:
            text = p.get_text(" ", strip=True)
            if text:
                result["intro"].append({
                    "content": text
                })

        # Also check for intro lists
        intro_lists = intro_section.find_all(["ul", "ol"])
        for lst in intro_lists:
            items = [li.get_text(" ", strip=True) for li in lst.find_all("li") if li.get_text(strip=True)]
            if items:
                result["intro"].append({
                    "items": items
                })

    # Process sections with headings
    current_section = None
    
    for wikki in wikki_sections:
        # Find headings
        headings = wikki.find_all(["h2", "h3"])
        
        for heading in headings:
            # If we have a current section, save it
            if current_section and current_section["content"]:
                result["sections"].append(current_section)
            
            # Start new section
            current_section = {
                "heading": heading.get_text(strip=True),
                "content": []
            }
            
            # Get content after this heading
            next_elements = []
            for sibling in heading.find_next_siblings():
                if sibling.name in ["h2", "h3"]:
                    break
                next_elements.append(sibling)
            
            # Process the elements after heading
            for element in next_elements:
                # PARAGRAPHS
                if element.name == "p":
                    text = element.get_text(" ", strip=True)
                    if text:
                        current_section["content"].append({
                            "content": text
                        })
                
                # LISTS
                elif element.name in ["ul", "ol"]:
                    items = [li.get_text(" ", strip=True) for li in element.find_all("li") if li.get_text(strip=True)]
                    if items:
                        current_section["content"].append({
                            "items": items
                        })
                
                # TABLES
                elif element.name == "table":
                    table_data = []
                    for tr in element.find_all("tr"):
                        row = []
                        for cell in tr.find_all(["th", "td"]):
                            row.append(cell.get_text(" ", strip=True))
                        if row:
                            table_data.append(row)
                    
                    if table_data:
                        current_section["content"].append({
                            "data": table_data
                        })
                
                # LINKS (standalone)
                elif element.name == "a" and element.parent.name not in ["p", "li"]:
                    href = element.get("href", "")
                    text = element.get_text(strip=True)
                    if href and text:
                        current_section["content"].append({
                            "text": text,
                            "url": href
                        })

    # Add the last section
    if current_section and current_section["content"]:
        result["sections"].append(current_section)

    # ---------------- FAQ SECTION ----------------
    faq_section = soup.select_one(".ab3f81")
    if faq_section:
        faqs = []
        qna_divs = faq_section.select(".ea1844, .f61835")
        
        for i in range(0, len(qna_divs), 2):
            if i + 1 < len(qna_divs):
                question_div = qna_divs[i]
                answer_div = qna_divs[i + 1]
                
                question = question_div.get_text(strip=True).replace("Q:", "").strip()
                answer = answer_div.get_text(strip=True).replace("A:", "").strip()
                
                if question and answer:
                    faqs.append({
                        "question": question,
                        "answer": answer
                    })
        
        if faqs:
            result["faqs"] = faqs

    return result

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
              "Aeronautical Engineering":{
                "overviews":extract_overview_data(driver),
                "course":extract_courses__data(driver),
                "syllabus":scrape_syllabus_section(driver),
                "career":scrape_career_overview(driver),
                "addmision":scrape_admission_overview(driver),
                "highly_Paid":scrape_blog_paid(driver),
                # "fees":scrape_fees_overview_json(driver, timeout=30),
                # "JEEVSBITSAK":scrape_blog_data(driver),
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

