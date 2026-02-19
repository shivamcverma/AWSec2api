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

PCOMBA_O_URL="https://www.shiksha.com/mph-master-of-public-health-chp"
PCOMBA_SUB_URL="https://www.shiksha.com/md-doctor-of-medicine-subjects-chp"
PCOMBA_COM_URL = "https://www.shiksha.com/md-doctor-of-medicine-comparison-chp"
PCOMBA_MD_VS_MBBS_URL ="https://www.shiksha.com/medicine-health-sciences/medicine/articles/md-vs-mbbs-differences-eligibility-admission-jobs-salary-2023-blogId-132969"
PCOMBA_TOTAL_IIAMS_URL = "https://www.shiksha.com/medicine-health-sciences/articles/aiims-in-india-blogId-23925"
PCOMBA_C_URL="https://www.shiksha.com/engineering/computer-science-engineering-courses-chp"
PCOMBA_S_URL="https://www.shiksha.com/mph-master-of-public-health-syllabus-chp"
PCOMBA_CAREER_URL = "https://www.shiksha.com/mph-master-of-public-health-career-chp"
PCOMBA_ADDMISSION_URL="https://www.shiksha.com/engineering/computer-science-engineering-admission-chp"
PCOMBA_FEES_URL = "https://www.shiksha.com/engineering/computer-science-engineering-fees-chp"
PCOMBA_JEEVSBITSAK_URL = "https://www.shiksha.com/engineering/articles/jee-main-vs-bitsat-exam-difficulty-level-pattern-and-syllabus-blogId-53799"
PCOMBA_Q_URL = "https://www.shiksha.com/tags/mph-tdp-718618"
PCOMBA_QD_URL="https://www.shiksha.com/tags/mph-tdp-718618?type=discussion"


def create_driver():
    options = Options()

    # Mandatory for GitHub Actions
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Optional but good
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    #     "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    # )

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

def extract_subjects_data(driver):
    driver.get(PCOMBA_SUB_URL)  # URL aapke hisaab se change karein # Aapka URL yahan daalein
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.find("section", id="chp_subjects_overview")
    if not section:
        return {}

    data = {
        "title": None,
        "updated_on": None,
        "author": {},
        "content": {"blocks": []}
    }

    # ==============================
    # UPDATED DATE
    # ==============================
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        data["title"]=h1
    else:
        pass
    d957ae_div = section.find("div", class_="d957ae")
    if d957ae_div:
        updated_div = d957ae_div.find("div")
        if updated_div:
            updated_span = updated_div.find("span")
            data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # ==============================
    # AUTHOR INFO
    # ==============================
    author_block = section.find("div", class_="c2675e")
    if author_block:
        author_link = author_block.find("a")
        role_span = author_block.find("span", class_="cbbdad")
        img = author_block.find("img")
        
        data["author"] = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role_span.get_text(strip=True) if role_span else None,
            "image": img["src"] if img else None
        }

    # ==============================
    # MAIN CONTENT
    # ==============================
    container = section.find("div", id=lambda x: x and x.startswith("wikkiContents_chp_subjects_overview"))
    
    if container:
        content_blocks = []
        
        # Sabhi top-level elements ko process karo
        for element in container.find_all(recursive=False):
            blocks = parse_subject_element(element)
            if blocks:
                if isinstance(blocks, list):
                    content_blocks.extend(blocks)
                else:
                    content_blocks.append(blocks)
        
        data["content"]["blocks"] = content_blocks

    return data


def parse_subject_element(element):
    """Parse individual elements from MD subjects page"""
    blocks = []
    
    # ----------------------------
    # HEADINGS
    # ----------------------------
    if element.name in ["h2", "h3", "h4"]:
        return {
            "type": "heading",
            "value": element.get_text(" ", strip=True)
        }
    
    # ----------------------------
    # PARAGRAPHS
    # ----------------------------
    if element.name == "p":
        # Skip empty paragraphs or DFP banner
        text = element.get_text(" ", strip=True)
        if text and text != "DFP-Banner":
            return {
                "type": "paragraph",
                "value": text
            }
        return None
    
    # ----------------------------
    # TABLES - YAHAN SE MD SUBJECTS KI TABLES AAYENGI
    # ----------------------------
    if element.name == "table":
        table_data = []
        rows = element.find_all("tr")
        
        for row in rows:
            cols = []
            for cell in row.find_all(["th", "td"]):
                # Cell ke andar ke saare text ko lein (including lists)
                cell_text = cell.get_text(" ", strip=True)
                if cell_text:
                    cols.append(cell_text)
            if cols:
                table_data.append(cols)
        
        if table_data:
            return {
                "type": "table",
                "value": table_data
            }
    
    # ----------------------------
    # LISTS (ul/ol)
    # ----------------------------
    if element.name in ["ul", "ol"]:
        items = []
        for li in element.find_all("li", recursive=False):
            text = li.get_text(" ", strip=True)
            if text:
                items.append(text)
        
        if items:
            return {
                "type": "list",
                "value": items
            }
    
    # ----------------------------
    # DEFINITION LISTS (dl) - MD subjects mein tables dl ke andar hain
    # ----------------------------
    if element.name == "dl":
        for dd in element.find_all("dd"):
            table = dd.find("table")
            if table:
                table_block = parse_subject_element(table)
                if table_block:
                    blocks.append(table_block)
            else:
                text = dd.get_text(" ", strip=True)
                if text:
                    blocks.append({
                        "type": "paragraph",
                        "value": text
                    })
        return blocks if blocks else None
    
    # ----------------------------
    # DIVs - unke andar ke elements process karo
    # ----------------------------
    if element.name == "div":
        for child in element.find_all(recursive=False):
            child_blocks = parse_subject_element(child)
            if child_blocks:
                if isinstance(child_blocks, list):
                    blocks.extend(child_blocks)
                else:
                    blocks.append(child_blocks)
        return blocks if blocks else None
    
    return None


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

    syllabus_section = soup.find("section", id="chp_syllabus_overview")
    if not syllabus_section:
        return syllabus_data

    # ---------------------------------
    # TITLE
    # ---------------------------------
    title = soup.find("h1")
    syllabus_data["title"] = title.get_text(strip=True) if title else None

    # ---------------------------------
    # UPDATED DATE
    # ---------------------------------
    updated_span = syllabus_section.select_one("div.d957ae span")
    syllabus_data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # ---------------------------------
    # AUTHOR INFO
    # ---------------------------------
    author_name = syllabus_section.select_one("p.e9801a a")
    author_role = syllabus_section.select_one("p.e9801a span.cbbdad")

    syllabus_data["author"] = {
        "name": author_name.get_text(strip=True) if author_name else None,
        "profile_url": author_name["href"] if author_name else None,
        "role": author_role.get_text(strip=True) if author_role else None
    }

    # ---------------------------------
    # 🔥 PURE FULL TEXT (NO DATA LOSS)
    # ---------------------------------
    text_parts = []
    for p in syllabus_section.find_all(["p", "li"], limit=200):
        text_parts.append(p.get_text(" ", strip=True))

    syllabus_data["full_section_text"] = "\n".join(text_parts)


    # ---------------------------------
    # OVERVIEW / INTRO CONTENT
    # ---------------------------------
    overview_block = syllabus_section.select_one("#wikkiContents_chp_syllabus_overview_0")
    overview_paragraphs = []

    if overview_block:
        for p in overview_block.find_all("p"):
            text = p.get_text(" ", strip=True)
            if text and len(text) > 20:
                overview_paragraphs.append(text)

    syllabus_data["overview"] = overview_paragraphs

    # ---------------------------------
    # LINKS PRESENT IN OVERVIEW
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
    # 🔥 FAQ SECTION (QUESTIONS + ANSWERS)
    # ---------------------------------
    faqs = []
    faq_blocks = syllabus_section.select(".sectional-faqs > div")

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
   # 🔥 NEW SECTION: CORE + ELECTIVE + BOOKS
    # =====================================================
    popular_section = soup.find("section", id="chp_syllabus_popularspecialization")
    popular_data = {}

    if popular_section:
        popular_data["section_title"] = popular_section.find("h2").get_text(strip=True)

        from html import unescape

        intro_content = []

        intro_block = popular_section.find(
            "div", id="wikkiContents_chp_syllabus_popularspecialization_0"
        )

        SKIP_TEXTS = {
            "Core CSE Subjects",
            "CSE Subject Details",
            "Elective CSE Subjects"
        }

        if intro_block:
            for tag in intro_block.find_all(["h2", "h3", "p"], recursive=True):

                # ❌ skip if tag is inside table
                if tag.find_parent("table"):
                    continue

                text = unescape(tag.get_text(" ", strip=True))

                # ❌ skip junk / table labels / notes
                if (
                    not text
                    or len(text) < 25
                    or text in SKIP_TEXTS
                    or text.lower().startswith("note")
                ):
                    continue

                intro_content.append({
                    "type": tag.name,
                    "text": text
                })

        popular_data["intro"] = intro_content

        # -------- CORE SUBJECTS TABLE --------
        core_subjects = []
        core_table = popular_section.find("h3", string=lambda x: x and "Core Computer" in x)
        if core_table:
            table = core_table.find_next("table")
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    core_subjects.append({
                        "subject": cols[0].get_text(strip=True),
                        "details": cols[1].get_text(" ", strip=True)
                    })
        popular_data["core_subjects"] = core_subjects

        # -------- ELECTIVE SUBJECTS TABLE --------
        elective_subjects = []
        elective_table = popular_section.find("h3", string=lambda x: x and "Elective Computer" in x)
        if elective_table:
            table = elective_table.find_next("table")
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    elective_subjects.append({
                        "subject": cols[0].get_text(strip=True),
                        "details": cols[1].get_text(" ", strip=True)
                    })
        popular_data["elective_subjects"] = elective_subjects

        # -------- POPULAR BOOKS TABLE --------
        books = []
        books_heading = popular_section.find("h2", string=lambda x: x and "Popular Books" in x)
        if books_heading:
            table = books_heading.find_next("table")
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) == 3:
                    books.append({
                        "subject": cols[0].get_text(strip=True),
                        "book_title": cols[1].get_text(" ", strip=True),
                        "author": cols[2].get_text(" ", strip=True)
                    })
        popular_data["recommended_books"] = books

    syllabus_data["popular_specialization"] = popular_data
 
    
    syllabus_data["faqs"] = faqs

    from html import unescape

    comparison_data = {}

    block = soup.find(
        "div", id="wikkiContents_chp_syllabus_topratecourses_0"
    )

    if block:
        inner = block.find("div")

        # 1️⃣ Intro paragraph (top)
        intro_p = inner.find("p")
        comparison_data["intro"] = unescape(
            intro_p.get_text(" ", strip=True)
        ) if intro_p else ""

        # 2️⃣ Title (h3)
        h3 = inner.find("h3")
        comparison_data["title"] = unescape(
            h3.get_text(" ", strip=True)
        ) if h3 else ""

        # 3️⃣ Description paragraph (after h3)
        desc_p = h3.find_next_sibling("p") if h3 else None
        comparison_data["description"] = unescape(
            desc_p.get_text(" ", strip=True)
        ) if desc_p else ""

        # 4️⃣ Table scraping
        table = inner.find("table")
        table_data = []

        if table:
            headers = [
                unescape(th.get_text(" ", strip=True))
                for th in table.find_all("th")
            ]

            for row in table.find_all("tr")[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) == len(headers):
                    row_obj = {}
                    for i, col in enumerate(cols):
                        # list support inside td
                        ul = col.find("ul")
                        if ul:
                            row_obj[headers[i]] = [
                                unescape(li.get_text(" ", strip=True))
                                for li in ul.find_all("li")
                            ]
                        else:
                            row_obj[headers[i]] = unescape(
                                col.get_text(" ", strip=True)
                            )
                    table_data.append(row_obj)

        comparison_data["table"] = table_data

        # 5️⃣ Note
        note_p = inner.find("p", string=lambda x: x and "Note" in x)
        comparison_data["note"] = unescape(
            note_p.get_text(" ", strip=True)
        ) if note_p else ""

    popular_data["mtech_comparison"] = comparison_data
    syllabus_data = scrape_detailed_syllabus_section(soup, syllabus_data)
    return syllabus_data
def parse_semester_table(table):
    semesters = {}
    current_sem = None

    for row in table.find_all("tr"):
        th = row.find("th")
        if th:
            current_sem = th.get_text(strip=True)
            semesters[current_sem] = []
            continue

        if current_sem:
            subjects = [td.get_text(" ", strip=True) for td in row.find_all("td")]
            subjects = [s for s in subjects if s and s != "-"]
            if subjects:
                semesters[current_sem].extend(subjects)

    return semesters
def scrape_detailed_syllabus_section(soup, syllabus_data):

    section = soup.find("section", id="chp_syllabus_popularexams")
    if not section:
        return syllabus_data

    detailed_data = {}

    # ---------------------------------
    # INTRO TEXT
    # ---------------------------------
    intro_block = section.select_one(".wikkiContents > div")
    intro_paragraphs = []

    if intro_block:
        for p in intro_block.find_all("p", recursive=False):
            text = p.get_text(" ", strip=True)
            if len(text) > 30:
                intro_paragraphs.append(text)

    detailed_data["intro"] = intro_paragraphs

    # ---------------------------------
    # COURSE-WISE SYLLABUS TABLES
    # ---------------------------------
    course_syllabus = {}

    headings = section.find_all("h3")
    for h in headings:
        course_name = h.get_text(" ", strip=True)
        table = h.find_next("table")

        if table:
            course_syllabus[course_name] = parse_semester_table(table)

    detailed_data["course_syllabus"] = course_syllabus

    # ---------------------------------
    # 🔥 POPULAR EXAMS
    # ---------------------------------
    exams = []
    exam_cards = section.select(".uilp_exam_card")

    for card in exam_cards:
        exam_name = card.select_one(".exam_flnm")
        exam_link = card.select_one(".exam_title")
        dates = []

        for row in card.select(".exam_impdates tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                dates.append({
                    "date": cols[0].get_text(" ", strip=True),
                    "event": cols[1].get_text(" ", strip=True)
                })

        exams.append({
            "name": exam_name.get_text(strip=True) if exam_name else None,
            "url": exam_link["href"] if exam_link else None,
            "important_dates": dates
        })

    detailed_data["popular_exams"] = exams

    # ---------------------------------
    # 🔥 FAQs
    # ---------------------------------
    faqs = []
    faq_section = section.select_one(".sectional-faqs")

    questions = faq_section.select("div.listener")
    answers = faq_section.select("div.f61835")

    for q_div, a_div in zip(questions, answers):
        question = q_div.get_text(" ", strip=True).replace("Q:", "").strip()

        ans_content = a_div.select_one(".cmsAContent")
        if not ans_content:
            continue

        answer = ans_content.get_text("\n", strip=True)
        links = [
            {"text": a.get_text(strip=True), "url": a["href"]}
            for a in ans_content.find_all("a", href=True)
        ]

        faqs.append({
            "question": question,
            "answer": answer,
            "links": links
        })


    detailed_data["faqs"] = faqs

    # ---------------------------------
    syllabus_data["detailed_cse_syllabus"] = detailed_data
    return syllabus_data



def scrape_career_overview(driver):
    driver.get(PCOMBA_CAREER_URL)
    time.sleep(3)
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
        "title":None,
        "article_info": {},
        "intro": [],
        "sections": []
    }
    title = soup.find("div",class_="flx-box mA")
    if title:
        h1 = title.find("h1").text.strip()
        result["title"]=h1
    else:
        pass
    # ---------------- METADATA ----------------
    author_section = soup.select_one(".adp_user")

    if author_section:
        result["article_info"]["author"] = {
            "name": author_section.select_one(".adp_usr_dtls a").get_text(strip=True),
            "role": author_section.select_one(".user_expert_level").get_text(strip=True),
            "image": author_section.select_one("img")["src"]
        }

    result["article_info"]["updated"] = soup.select_one(
        ".blogdata_user span"
    ).get_text(strip=True)

    result["article_info"]["summary"] = soup.select_one(
        "#blogSummary"
    ).get_text(strip=True)

    # ---------------- MAIN CONTENT ----------------
    content_div = soup.select_one("#blogId-53799")

    if not content_div:
        return result

    # Remove junk
    for bad in content_div.select(".openVideoContainer, .b644f8, script, style"):
        bad.decompose()

    wikki_sections = content_div.select(".wikkiContents")

    current_section = None

    for wikki in wikki_sections:

        for element in wikki.find_all(
            ["h2","h3","p","ul","ol","table","img","a"], 
            recursive=True
        ):

            # -------- HEADINGS --------
            if element.name in ["h2","h3"]:

                if current_section:
                    result["sections"].append(current_section)

                current_section = {
                    "heading": element.get_text(strip=True),
                    "content": []
                }

            # -------- PARAGRAPHS --------
            elif element.name == "p":
                text = element.get_text(" ", strip=True)

                if not text:
                    continue

                item = {
                   
                    "content": text
                }

                if current_section:
                    current_section["content"].append(item)
                else:
                    result["intro"].append(item)

            # -------- LISTS --------
            elif element.name in ["ul","ol"]:
                items = [
                    li.get_text(" ", strip=True)
                    for li in element.find_all("li")
                ]

                if items:
                    data = {
                       
                        "items": items
                    }

                    if current_section:
                        current_section["content"].append(data)

            # -------- TABLES --------
            elif element.name == "table":
                table_data = []

                for tr in element.find_all("tr"):
                    row = []
                    for cell in tr.find_all(["th","td"]):
                        row.append(cell.get_text(" ", strip=True))

                    if row:
                        table_data.append(row)

                if table_data:
                    current_section["content"].append({
                        
                        "data": table_data
                    })

            # -------- IMAGES --------
            elif element.name == "img":
                src = element.get("src")

                if src:
                    img = {
                        
                        "src": src,
                        "alt": element.get("alt")
                    }

                    if current_section:
                        current_section["content"].append(img)

            # -------- LINKS (Also Read etc) --------
            elif element.name == "a":
                href = element.get("href")
                text = element.get_text(strip=True)

                if href and text:
                    link = {
                       
                        "text": text,
                        "url": href
                    }

                    if current_section:
                        current_section["content"].append(link)

    if current_section:
        result["sections"].append(current_section)

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
def extract_compare_overview_data(driver):
    driver.get(PCOMBA_COM_URL)
    time.sleep(3)
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.find("section", id="chp_compare_overview")
    if not section:
        return {}

    data = {}

    # ==============================
    # UPDATED DATE
    # ==============================
    updated_div = section.find("div", string=lambda x: x and "Updated on" in x)
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
    # MAIN CONTENT
    # ==============================
    container = section.find(
        "div",
        id=lambda x: x and x.startswith("wikkiContents_chp_compare_overview")
    )

    data["content"] = (
        extract_rich_content(container)
        if container
        else {"blocks": []}
    )

    return data
def extract_MD_VS_MBBS_data(driver):
    driver.get(PCOMBA_MD_VS_MBBS_URL)
    time.sleep(3)
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}

    # ======================================
    # AUTHOR + UPDATED DATE
    # ======================================
    blog_section = soup.find("div", class_="adp_blog")

    if blog_section:
        # Updated date
        updated_span = blog_section.find("div", class_="blogdata_user")
        if updated_span:
            span = updated_span.find("span")
            data["updated_on"] = span.get_text(strip=True) if span else None
        else:
            data["updated_on"] = None

        # Author info
        author_block = blog_section.find("div", class_="adp_user")
        author_data = {}

        if author_block:
            author_link = author_block.find("a", href=True)
            img = author_block.find("img")
            role_div = author_block.find("div", class_="user_expert_level")

            author_data = {
                "name": author_link.get_text(strip=True) if author_link else None,
                "profile_url": author_link["href"] if author_link else None,
                "role": role_div.get_text(strip=True) if role_div else None,
                "image": img["src"] if img else None
            }

        data["author"] = author_data
    else:
        data["updated_on"] = None
        data["author"] = {}

    # ======================================
    # MAIN CONTENT (Multiple Containers)
    # ======================================
    content = {"blocks": []}

    content_containers = soup.find_all(
        "div",
        id=lambda x: x and x.startswith("wikkiContents_multi_ADP")
    )

    for container in content_containers:
        parsed = extract_rich_content(container)
        content["blocks"].extend(parsed["blocks"])

    data["content"] = content

    # ======================================
    # FAQ SECTION (Structured Extraction)
    # ======================================
    faqs = []
    faq_section = soup.find("div", class_="sectional-faqs")

    if faq_section:
        questions = faq_section.find_all("div", class_="html-0")

        for q in questions:
            question_text = q.get_text(" ", strip=True)

            answer_block = q.find_next_sibling("div")
            if answer_block:
                answer_content = answer_block.get_text(" ", strip=True)
            else:
                answer_content = None

            if question_text:
                faqs.append({
                    "question": question_text.replace("Q:", "").strip(),
                    "answer": answer_content.replace("A:", "").strip() if answer_content else None
                })

    data["faqs"] = faqs

    return data

def extract_rich_content(container):
    if not container:
        return {"blocks": []}

    content = {"blocks": []}

    def parse_node(node):

        # --------------------
        # HEADINGS
        # --------------------
        if node.name in ["h1", "h2", "h3", "h4"]:
            content["blocks"].append({
                "type": "heading",
                "value": node.get_text(" ", strip=True)
            })
            return

        # --------------------
        # PARAGRAPHS
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
        # IMAGES (picture/img)
        # --------------------
        if node.name in ["img"]:
            src = node.get("src")
            alt = node.get("alt")
            if src:
                content["blocks"].append({
                    "type": "image",
                    "value": {
                        "url": src,
                        "alt": alt
                    }
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
        # TABLES
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
            return

        # --------------------
        # LINKS (standalone)
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
        # CONTAINERS
        # --------------------
        if node.name in ["div", "section", "span", "picture"]:
            for child in node.find_all(recursive=False):
                parse_node(child)

    for node in container.find_all(recursive=False):
        parse_node(node)

    return content
def extract_TOTAL_IIAMS_page(driver):
    driver.get(PCOMBA_TOTAL_IIAMS_URL)
    time.sleep(3)
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}

    # ======================================
    # AUTHOR + UPDATED DATE
    # ======================================
    blog_section = soup.find("div", class_="adp_blog")

    if blog_section:
        updated_span = blog_section.find("div", class_="blogdata_user")
        data["updated_on"] = (
            updated_span.get_text(strip=True)
            if updated_span else None
        )

        author_block = blog_section.find("div", class_="adp_user")
        author_data = {}

        if author_block:
            author_link = author_block.find("a", href=True)
            img = author_block.find("img")
            role_div = author_block.find("div", class_="user_expert_level")

            author_data = {
                "name": author_link.get_text(strip=True) if author_link else None,
                "profile_url": author_link["href"] if author_link else None,
                "role": role_div.get_text(strip=True) if role_div else None,
                "image": img["src"] if img else None
            }

        data["author"] = author_data
    else:
        data["updated_on"] = None
        data["author"] = {}

    # ======================================
    # MAIN CONTENT (Skip TOC)
    # ======================================
    content = {"blocks": []}

    content_containers = soup.find_all(
        "div",
        id=lambda x: x and x.startswith("wikkiContents_multi_ADP")
    )

    for container in content_containers:
        parsed = extract_rich_content(container)
        content["blocks"].extend(parsed["blocks"])

    data["content"] = content

    # ======================================
    # MULTIPLE FAQ SECTIONS
    # ======================================
    faqs = []

    faq_sections = soup.find_all("div", class_="sectional-faqs")

    for faq_section in faq_sections:
        questions = faq_section.find_all("div", class_="html-0")

        for q in questions:
            question_text = q.get_text(" ", strip=True)

            answer_block = q.find_next_sibling("div")
            if answer_block:
                answer_text = answer_block.get_text(" ", strip=True)
            else:
                answer_text = None

            if question_text:
                faqs.append({
                    "question": question_text.replace("Q:", "").strip(),
                    "answer": answer_text.replace("A:", "").strip() if answer_text else None
                })

    data["faqs"] = faqs

    return data






def scrape_mba_colleges():
    driver = create_driver()

      

    try:
       data = {
              "MPH":{
                "overviews":extract_overview_data(driver),
                # "subject":extract_subjects_data(driver),
                # "comparision":extract_compare_overview_data(driver),
                # "MD_VS_MBBS":extract_MD_VS_MBBS_data(driver),
                # "TOTAL_IIAMS":extract_TOTAL_IIAMS_page(driver),
                # "course":extract_courses__data(driver),
                "syllabus":scrape_syllabus_section(driver),
                "career":scrape_career_overview(driver),
                # "addmision":scrape_admission_overview(driver),
                # "fees":scrape_fees_overview_json(driver, timeout=30),
                # # "JEEVSBITSAK":scrape_blog_data(driver),
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

