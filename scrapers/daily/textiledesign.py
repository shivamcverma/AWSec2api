from html import unescape
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from typing import Dict, List, Any, Optional
from html import unescape
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

PCOMBA_O_URL="https://www.shiksha.com/design/textile-design-chp"
PCOMBA_C_URL="https://www.shiksha.com/design/jewellery-design-courses-chp"
PCOMBA_SUB_URL= "https://www.shiksha.com/engineering/robotics-engineering-subjects-chp"
PCOMBA_S_URL="https://www.shiksha.com/design/textile-design-syllabus-chp"
PCOMBA_CAREER_URL = "https://www.shiksha.com/design/textile-design-career-chp"
PCOMBA_SALLARY_URL = "https://www.shiksha.com/engineering/construction-engineering-career-chp"
PCOMBA_ADDMISSION_URL="https://www.shiksha.com/design/textile-design-admission-chp"
PCOMBA_GOODSCROR_URL = "https://www.shiksha.com/engineering/articles/what-is-a-good-score-in-jee-main-to-qualify-for-jee-advanced-blogId-61841"
PCOMBA_FEES_URL = "https://www.shiksha.com/design/fashion-designing-fees-chp"
PCOMBA_NIRFRANK_URL = "https://www.shiksha.com/humanities-social-sciences/articles/nirf-2025-26-rankings-blogId-15699"
PCOMBA_5YEARS_URL = "https://www.shiksha.com/engineering/articles/engineering-stream-popularity-trends-in-last-5-years-blogId-144539"
PCOMBA_PAID_URL = "https://www.shiksha.com/engineering/articles/why-engineering-is-still-a-highly-paid-career-stream-blogId-144603"
CEED_AND_UCEED  = "https://www.shiksha.com/design/articles/time-management-tips-for-ceed-and-uceed-2026-blogId-113263"
PCOMBA_JEEVSBITSAK_URL = "https://www.shiksha.com/engineering/articles/jee-main-vs-bitsat-exam-difficulty-level-pattern-and-syllabus-blogId-53799"
PCOMBA_Q_URL = "https://www.shiksha.com/tags/textile-design-tdp-67"
PCOMBA_QD_URL="https://www.shiksha.com/tags/textile-design-tdp-67?type=discussion"


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
        img = author_block.find("img")
        pic = img.get("src")
        author_data["image"]=pic
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
    pic = soup.find("div",class_="figure")
    if pic:
        img = pic.find("img").get("src")
        data["img"]=img
    else:
        print("dfnvszxnb")
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

def extract_syllabus__data(driver):
    driver.get(PCOMBA_S_URL)
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # ==============================
    # OVERVIEW SECTION
    # ==============================
    section = soup.find("section", id="chp_syllabus_overview")
    if not section:
        return {}

    data = {}

    title = soup.find("div", class_="d8a6c4")
    if title and title.find("h1"):
        data["title"] = title.find("h1").get_text(strip=True)

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
        img = author_block.find("img")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role_span.get_text(strip=True) if role_span else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # ==============================
    # MAIN OVERVIEW CONTENT
    # ==============================
    container = section.find(
        "div",
        id=lambda x: x and x.startswith("wikkiContents_chp_syllabus_overview")
    )

    data["content"] = (
        extract_rich_content(container)
        if container
        else {"blocks": []}
    )

    # ==============================
    # FULL SEMESTERWISE CONTENT (NOTHING MISSED)
    # ==============================
    semester_section = soup.find("section", id="chp_syllabus_semesterwise")
    semesterwise_content = []

    if semester_section:
   

        for tag in semester_section.find_all(
            ["h2", "h3", "p", "table", "ul"], recursive=True
        ):

            # HEADINGS
            if tag.name in ["h2", "h3"]:
                text = tag.get_text(" ", strip=True)
                if text:
                    semesterwise_content.append({
                        "type": "heading",
                        "tag": tag.name,
                        "text": text
                    })

            # PARAGRAPHS
            elif tag.name == "p":
                text = tag.get_text(" ", strip=True)
                if text:
                    semesterwise_content.append({
                        "type": "paragraph",
                        "text": text
                    })

            # LISTS (future-proof)
            elif tag.name == "ul":
                items = [
                    li.get_text(" ", strip=True)
                    for li in tag.find_all("li")
                    if li.get_text(strip=True)
                ]
                if items:
                    semesterwise_content.append({
                        "type": "list",
                        "items": items
                    })

            # TABLES
            elif tag.name == "table":
                table_data = []
                current_semester = None

                for row in tag.find_all("tr"):
                    th = row.find("th")
                    if th:
                        current_semester = th.get_text(" ", strip=True)
                        table_data.append({
                            "semester": current_semester,
                            "subjects": []
                        })
                    else:
                        tds = row.find_all("td")
                        if current_semester and tds:
                            subjects = [
                                td.get_text(" ", strip=True)
                                for td in tds
                                if td.get_text(strip=True) and td.get_text(strip=True) != "-"
                            ]
                            if subjects:
                                table_data[-1]["subjects"].extend(subjects)

                if table_data:
                    semesterwise_content.append({
                        "type": "table",
                        "data": table_data
                    })

    data["semesterwise_syllabus"] = semesterwise_content\
        # ==============================
    # ==============================
    # SYLLABUS COMPARISON (FIXED — h2 INCLUDED)
    # ==============================
    others_section = soup.find("section", id="chp_syllabus_others1")
    others_content = []

    if others_section:

        for tag in others_section.find_all(
            ["h2", "h3", "p", "table", "ul"],
            recursive=True
        ):

            # HEADINGS
            if tag.name in ["h2", "h3"]:
                text = tag.get_text(" ", strip=True)
                if text:
                    others_content.append({
                        "type": "heading",
                        "tag": tag.name,
                        "text": text
                    })

            # PARAGRAPHS
            elif tag.name == "p":
                text = tag.get_text(" ", strip=True)
                if text:
                    others_content.append({
                        "type": "paragraph",
                        "text": text
                    })

            # LISTS
            elif tag.name == "ul":
                items = [
                    li.get_text(" ", strip=True)
                    for li in tag.find_all("li")
                    if li.get_text(strip=True)
                ]
                if items:
                    others_content.append({
                        "type": "list",
                        "items": items
                    })

            # TABLES
            elif tag.name == "table":
                rows = []
                for tr in tag.find_all("tr"):
                    cells = [
                        cell.get_text(" ", strip=True)
                        for cell in tr.find_all(["th", "td"])
                        if cell.get_text(strip=True)
                    ]
                    if cells:
                        rows.append(cells)

                if rows:
                    others_content.append({
                        "type": "table",
                        "rows": rows
                    })

    data["syllabus_comparison"] = others_content

    core_section = soup.find("section", id="chp_syllabus_coresubjects")
    data["core_and_elective_subjects"] = (
        extract_section_everything(core_section)
        if core_section else []
    )

    entrance_section = soup.find("section", id="chp_syllabus_entranceexamsyllabus")
    data["entrance_exam_syllabus"] = (
        extract_section_everything(entrance_section)
        if entrance_section else []
)


    return data

def extract_section_everything(section):
    content = []

    # ---------- MAIN FLOW ----------
    for tag in section.find_all(
        ["h2", "h3", "p", "table", "ul"],
        recursive=True
    ):

        # HEADINGS
        if tag.name in ["h2", "h3"]:
            text = tag.get_text(" ", strip=True)
            if text:
                content.append({
                    "type": "heading",
                    "tag": tag.name,
                    "text": text
                })

        # PARAGRAPHS
        elif tag.name == "p":
            text = tag.get_text(" ", strip=True)
            if text and text != "\xa0":
                content.append({
                    "type": "paragraph",
                    "text": text
                })

        # LISTS
        elif tag.name == "ul":
            items = [
                li.get_text(" ", strip=True)
                for li in tag.find_all("li")
                if li.get_text(strip=True)
            ]
            if items:
                content.append({
                    "type": "list",
                    "items": items
                })

        # TABLES
        elif tag.name == "table":
            rows = []
            for tr in tag.find_all("tr"):
                cells = [
                    cell.get_text(" ", strip=True)
                    for cell in tr.find_all(["th", "td"])
                    if cell.get_text(strip=True)
                ]
                if cells:
                    rows.append(cells)

            if rows:
                content.append({
                    "type": "table",
                    "rows": rows
                })

    # ---------- FAQ BLOCK ----------
    faq_blocks = section.find_all("div", class_="sectional-faqs")
    faqs = []

    for faq in faq_blocks:
        questions = faq.find_all("strong", class_="flx-box")

        for q in questions:
            question = q.get_text(" ", strip=True).replace("Q:", "").strip()

            answer_div = q.find_next("div", class_="f61835")
            answer_parts = []

            if answer_div:
                for el in answer_div.find_all(["p", "ul", "table"], recursive=True):

                    if el.name == "p":
                        txt = el.get_text(" ", strip=True)
                        if txt:
                            answer_parts.append({
                                "type": "paragraph",
                                "text": txt
                            })

                    elif el.name == "ul":
                        items = [
                            li.get_text(" ", strip=True)
                            for li in el.find_all("li")
                            if li.get_text(strip=True)
                        ]
                        if items:
                            answer_parts.append({
                                "type": "list",
                                "items": items
                            })

                    elif el.name == "table":
                        rows = []
                        for tr in el.find_all("tr"):
                            cells = [
                                c.get_text(" ", strip=True)
                                for c in tr.find_all(["th", "td"])
                                if c.get_text(strip=True)
                            ]
                            if cells:
                                rows.append(cells)
                        if rows:
                            answer_parts.append({
                                "type": "table",
                                "rows": rows
                            })

            if question and answer_parts:
                faqs.append({
                    "question": question,
                    "answer": answer_parts
                })

    if faqs:
        content.append({
            "type": "faq",
            "data": faqs
        })

    return content


def extract_environmental_subjects_data(driver):
    # load the page (Selenium)
    driver.get(PCOMBA_SUB_URL)
    time.sleep(3)
    # let JS render (if needed)
    WebDriverWait(driver, 10)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # find the correct section
    section = soup.find("section", id="chp_subjects_overview")
    if not section:
        return {}

    data = {}

    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        data["title"]= h1
    else:
        pass
    # UPDATED ON
    updated_span = section.find("div", class_="d957ae")
    if updated_span:
        updated_date = updated_span.find("span")
        data["updated_on"] = updated_date.get_text(strip=True) if updated_date else None

    # AUTHOR INFO
    author_block = section.find("div", class_="c2675e")
    if author_block:
        name_tag = author_block.find("a")
        role_tag = author_block.find("span", class_="cbbdad")
        img_tag = author_block.find("img")
        data["author"] = {
            "name": name_tag.get_text(strip=True) if name_tag else None,
            "profile_url": name_tag["href"] if name_tag and name_tag.has_attr("href") else None,
            "role": role_tag.get_text(strip=True) if role_tag else None,
            "image": img_tag["src"] if img_tag and img_tag.has_attr("src") else None,
        }
    else:
        data["author"] = {}

    # parse the main content inside the “wikkiContents” block
    content_container = section.find(
        "div",
        id=lambda x: x and x.startswith("wikkiContents_chp_subjects_overview")
    )

    data["content"] = extract_rich_content(content_container)

    return data


def extract_rich_content(container):
    """
    Same style as your helper — walk through the container
    and generate structured blocks.
    """

    if not container:
        return {"blocks": []}

    content = {"blocks": []}

    def parse_node(node):

        # HEADINGS
        if node.name in ["h2", "h3", "h4"]:
            text = node.get_text(" ", strip=True)
            if text:
                content["blocks"].append({
                    "type": "heading",
                    "value": text
                })
            return

        # PARAGRAPHS
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

        # UNORDERED LISTS
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

        # TABLES
        if node.name == "table":
            table_rows = []
            for row in node.find_all("tr"):
                cols = [
                    c.get_text(" ", strip=True)
                    for c in row.find_all(["th", "td"])
                ]
                if cols:
                    table_rows.append(cols)
            if table_rows:
                content["blocks"].append({
                    "type": "table",
                    "value": table_rows
                })
            return

        # LINKS (standalone)
        if node.name == "a" and node.has_attr("href"):
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

        # IFRAMES
        if node.name == "iframe":
            src = node.get("src") or node.get("data-original")
            if src:
                content["blocks"].append({
                    "type": "iframe",
                    "value": src
                })
            return

        # Containers — dive deeper
        if node.name in ["div", "section", "span"]:
            for child in node.find_all(recursive=False):
                parse_node(child)

    # start at top level
    for child in container.find_all(recursive=False):
        parse_node(child)

    return content



def scrape_career_overview(driver):
    driver.get(PCOMBA_CAREER_URL)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    data = {
        "title":None,
        "author": {},
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


def scrape_civil_engineering_data(driver):
    driver.get(PCOMBA_SALLARY_URL)
    time.sleep(3)  # wait for page

    # ---------- WAIT ----------
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "wikkiContents_chp_career_overview_0"))
        )
    except Exception as e:
        print(f"Page load timeout: {e}")

    # scroll to ensure lazy content loads
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    result = {
        "title": None,
        "metadata": {},
        "sections": []
    }

    # ---------- TITLE ----------
    h1 = soup.find("h1")
    result["title"] = h1.text.strip() if h1 else driver.title

    # ---------- METADATA ----------
    last_updated = soup.find("span", string=lambda t: t and "IST" in t)
    if last_updated:
        result["metadata"]["last_updated"] = last_updated.text.strip()

    # ---------- AUTHOR ----------
    author_img = soup.find("img", alt=True)
    if author_img and "Akansha" in author_img.get("alt", ""):
        author_div = author_img.find_parent("div", class_="c2675e")
        if author_div:
            name = author_div.find("a")
            role = author_div.find("span", class_="cbbdad")
            result["metadata"]["author"] = {
                "name": name.text.strip() if name else None,
                "role": role.text.strip() if role else None,
                "image": author_img.get("src")
            }

    # ---------- OVERVIEW ----------
    overview_div = driver.find_element(By.ID, "wikkiContents_chp_career_overview_0")
    overview_paras = [
        p.text.strip()
        for p in overview_div.find_elements(By.TAG_NAME, "p")
        if len(p.text.strip()) > 60
    ]
    result["metadata"]["overview"] = overview_paras[:2]

    # ---------- MAIN SECTIONS ----------
    # find all H2s
    h2_elements = overview_div.find_elements(By.TAG_NAME, "h2")

    for h2 in h2_elements:
        section_title = h2.text.strip()
        if not section_title:
            continue

        # Collect all siblings until next h2
        content_items = []
        next_sibling = h2.find_element(By.XPATH, "following-sibling::*[1]")
        while next_sibling:
            tag = next_sibling.tag_name.lower()
            # stop if next h2
            if tag == "h2":
                break

            item = process_selenium_element(next_sibling)
            if item:
                content_items.append(item)

            # move to next sibling
            try:
                next_sibling = next_sibling.find_element(By.XPATH, "following-sibling::*[1]")
            except:
                break

        if content_items:
            result["sections"].append({
                "section_title": section_title,
                "content": content_items
            })

    return result


def process_selenium_element(element):
    tag = element.tag_name.lower()
    text = element.text.strip()
    if not text:
        return None

    cls = element.get_attribute("class") or ""
    el_id = element.get_attribute("id") or ""
    if any(x in cls for x in ["gradient-col"]) or "viewMore" in el_id:
        return None

    # Subheading
    if tag == "h3":
        return {"type": "subheading", "heading": text}

    # Paragraph
    if tag == "p" and len(text) > 30 and not any(x in text.lower() for x in ["http", "view more"]):
        return {"type": "paragraph", "text": text}

    # Table
    if tag == "table":
        table_data = []
        rows = element.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.XPATH, "./th | ./td")
            row_data = [c.text.strip() for c in cells if c.text.strip()]
            if row_data:
                table_data.append(row_data)
        if table_data:
            return {"type": "table", "data": table_data}

    # List
    if tag in ["ul", "ol"]:
        items = [li.text.strip() for li in element.find_elements(By.TAG_NAME, "li") if li.text.strip()]
        if items:
            return {"type": "list", "ordered": tag == "ol", "items": items}

    return None


def scrape_admission_overview(driver):
    driver.get(PCOMBA_ADDMISSION_URL)
    
    # Wait for main content to load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "chp_admission_overview"))
        )
    except:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wikkiContents"))
        )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {
        "title": "",
        "updated_on": "",
        "author": {},
        "content": {"blocks": []},
        "tables": [],
        "videos": []
    }
    
    # ==============================
    # EXTRACT MAIN SECTION
    # ==============================
    section = soup.find("section", id="chp_admission_overview")
    if not section:
        return data
    
    # ==============================
    # EXTRACT TITLE FROM PAGE
    # ==============================
    title_elem = soup.find("h1")
    if title_elem:
        data["title"] = title_elem.get_text(strip=True)
    
    # ==============================
    # EXTRACT UPDATED DATE
    # ==============================
    d957ae_div = section.find("div", class_="d957ae")
    if d957ae_div:
        date_div = d957ae_div.find("div")
        if date_div:
            date_span = date_div.find("span")
            if date_span:
                data["updated_on"] = date_span.get_text(strip=True)
    
    # ==============================
    # EXTRACT AUTHOR INFO
    # ==============================
    author_block = section.find("div", class_="c2675e")
    if author_block:
        author_data = {}
        
        # Author image
        img = author_block.find("img")
        if img:
            author_data["image"] = img.get("src", "")
            author_data["alt"] = img.get("alt", "")
        
        # Author name and details
        name_elem = author_block.find("p", class_="e9801a")
        if name_elem:
            # Author name with link
            author_link = name_elem.find("a")
            if author_link:
                author_data["name"] = author_link.get_text(strip=True)
                author_data["profile_url"] = author_link.get("href", "")
            
            # Author role
            role_span = name_elem.find("span", class_="cbbdad")
            if role_span:
                author_data["role"] = role_span.get_text(strip=True)
        
        data["author"] = author_data
    
    # ==============================
    # EXTRACT MAIN CONTENT
    # ==============================
    wikki_contents = section.find("div", id=lambda x: x and x.startswith("wikkiContents_chp_admission_overview"))
    if wikki_contents:
        # Extract content without links in paragraphs
        content_data = extract_content_without_links(wikki_contents)
        if content_data:
            data["content"] = content_data
            
            # Extract tables with context
            tables_data = extract_tables_with_context(wikki_contents)
            if tables_data:
                data["tables"] = tables_data
            
            # Extract videos only
            videos_data = extract_videos_only(wikki_contents)
            if videos_data:
                data["videos"] = videos_data
    
    return data

def extract_content_without_links(container):
    """Extract content without text links, only keep video and image links"""
    if not container:
        return {"blocks": []}
    
    content = {"blocks": []}
    
    # Get the main content div inside wikkiContents
    main_div = container.find("div")
    if not main_div:
        return content
    
    def parse_node(node, parent=None):
        # Skip processed nodes
        if hasattr(node, '_processed') and node._processed:
            return
        
        node._processed = True
        
        # HEADINGS (remove IDs)
        if node.name in ["h2", "h3", "h4", "h5", "h6"]:
            heading_text = node.get_text(" ", strip=True)
            if heading_text:
                # Clean heading text - remove links but keep text
                clean_text = heading_text
                # Remove any HTML IDs from output
                
                content["blocks"].append({
                    "type": "heading",
                    "level": node.name,
                    "value": clean_text
                })
            return
        
        # PARAGRAPHS (remove links, keep only text)
        elif node.name == "p":
            # Skip if inside table
            if node.find_parent("table"):
                return
            
            # Get text without links (but keep the link text as regular text)
            # First, create a copy of the node
            node_copy = BeautifulSoup(str(node), 'html.parser')
            p_tag = node_copy.find('p')
            
            # Replace all <a> tags with just their text content
            for a_tag in p_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            
            text = p_tag.get_text(" ", strip=True)
            if text and len(text.strip()) > 10:
                content["blocks"].append({
                    "type": "paragraph",
                    "value": text
                })
            return
        
        # LISTS (remove links from list items)
        elif node.name in ["ul", "ol"]:
            items = []
            for li in node.find_all("li", recursive=False):
                # Clean li text - remove links but keep text
                li_copy = BeautifulSoup(str(li), 'html.parser')
                li_tag = li_copy.find('li')
                
                # Replace all <a> tags with just their text content
                for a_tag in li_tag.find_all('a'):
                    a_tag.replace_with(a_tag.get_text())
                
                item_text = li_tag.get_text(" ", strip=True)
                if item_text:
                    items.append(item_text)
            
            if items:
                content["blocks"].append({
                    "type": "list",
                    "ordered": node.name == "ol",
                    "value": items
                })
            return
        
        # TABLES (handle separately)
        elif node.name == "table":
            return
        
        # IMAGES (keep only image links)
        elif node.name == "img":
            img_src = node.get("src")
            img_alt = node.get("alt", "")
            
            # Only include significant images (not icons)
            if img_src and not is_icon_image(node):
                content["blocks"].append({
                    "type": "image",
                    "value": img_src,
                    "alt": img_alt
                })
            return
        
        # VIDEO DIVS (keep video iframes)
        elif node.name == "div" and "vcmsEmbed" in node.get("class", []):
            iframe = node.find("iframe")
            if iframe and iframe.get("src"):
                content["blocks"].append({
                    "type": "video",
                    "value": iframe["src"],
                    "title": iframe.get("title", "")
                })
            return
        
        # For other divs, process children
        elif node.name == "div":
            for child in node.find_all(recursive=False):
                parse_node(child, node)
            return
    
    # Parse all top-level elements
    for child in main_div.find_all(recursive=False):
        parse_node(child)
    
    return content

def is_icon_image(img_tag):
    """Check if image is an icon (small decorative image)"""
    width = img_tag.get("width")
    height = img_tag.get("height")
    
    if width and height:
        try:
            w = int(width)
            h = int(height)
            # Consider images smaller than 50px as icons
            if w < 50 or h < 50:
                return True
        except:
            pass
    
    # Check if it's likely an icon by src or class
    src = img_tag.get("src", "").lower()
    if any(icon_indicator in src for icon_indicator in ['icon', 'svg', 'bullet', 'arrow', 'tick']):
        return True
    
    return False

def extract_tables_with_context(container):
    """Extract tables with their context (nearby heading and paragraph)"""
    tables_data = []
    
    if not container:
        return tables_data
    
    # Find all tables
    tables = container.find_all("table")
    
    for table in tables:
        table_data = {
            "context": {
                "heading": "",
                "paragraph": ""
            },
            "headers": [],
            "data": []
        }
        
        # Find nearest heading (look backwards)
        heading = None
        prev_elem = table.find_previous()
        while prev_elem and not heading:
            if prev_elem.name in ["h2", "h3", "h4", "h5", "h6"]:
                heading = prev_elem
            else:
                # Check if this element contains a heading
                heading_in_elem = prev_elem.find(["h2", "h3", "h4", "h5", "h6"])
                if heading_in_elem:
                    heading = heading_in_elem
                else:
                    prev_elem = prev_elem.find_previous()
        
        if heading:
            # Clean heading text (remove links)
            heading_copy = BeautifulSoup(str(heading), 'html.parser')
            heading_tag = heading_copy.find(heading.name)
            for a_tag in heading_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            table_data["context"]["heading"] = heading_tag.get_text(" ", strip=True)
        
        # Find nearest paragraph (look backwards, but after heading)
        paragraph = None
        if heading:
            # Look between heading and table
            current = heading.find_next()
            while current and current != table:
                if current.name == "p":
                    paragraph = current
                    break
                current = current.find_next()
        
        if not paragraph:
            # If no paragraph found after heading, look for any nearby paragraph
            paragraph = table.find_previous("p")
        
        if paragraph:
            # Clean paragraph text (remove links)
            para_copy = BeautifulSoup(str(paragraph), 'html.parser')
            p_tag = para_copy.find('p')
            for a_tag in p_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            table_data["context"]["paragraph"] = p_tag.get_text(" ", strip=True)
        
        # Extract table headers
        header_row = table.find("tr")
        if header_row:
            headers = []
            for cell in header_row.find_all(["th", "td"]):
                # Clean cell text (remove links)
                cell_copy = BeautifulSoup(str(cell), 'html.parser')
                cell_tag = cell_copy.find(cell.name)
                for a_tag in cell_tag.find_all('a'):
                    a_tag.replace_with(a_tag.get_text())
                header_text = cell_tag.get_text(" ", strip=True)
                if header_text:
                    headers.append(header_text)
            table_data["headers"] = headers
        
        # Extract table data (skip header row)
        rows = table.find_all("tr")
        start_idx = 1 if header_row and table_data["headers"] else 0
        
        for i in range(start_idx, len(rows)):
            row = rows[i]
            row_data = []
            cells = row.find_all(["td", "th"])
            
            for cell in cells:
                # Clean cell text (remove links)
                cell_copy = BeautifulSoup(str(cell), 'html.parser')
                cell_tag = cell_copy.find(cell.name)
                for a_tag in cell_tag.find_all('a'):
                    a_tag.replace_with(a_tag.get_text())
                cell_text = cell_tag.get_text(" ", strip=True)
                row_data.append(cell_text)
            
            if row_data:
                table_data["data"].append(row_data)
        
        if table_data["data"] or table_data["context"]["heading"]:
            tables_data.append(table_data)
    
    return tables_data

def extract_videos_only(container):
    """Extract only video iframes"""
    videos_data = []
    
    if not container:
        return videos_data
    
    # Find video embeds
    video_divs = container.find_all("div", class_="vcmsEmbed")
    
    for video_div in video_divs:
        iframe = video_div.find("iframe")
        if iframe and iframe.get("src"):
            video_info = {
                "src": iframe.get("src", ""),
                "title": iframe.get("title", "")
            }
            
            # Find context (nearest heading)
            heading = video_div.find_previous(["h2", "h3", "h4"])
            if heading:
                # Clean heading text
                heading_copy = BeautifulSoup(str(heading), 'html.parser')
                heading_tag = heading_copy.find(heading.name)
                for a_tag in heading_tag.find_all('a'):
                    a_tag.replace_with(a_tag.get_text())
                video_info["context"] = heading_tag.get_text(" ", strip=True)
            
            videos_data.append(video_info)
    
    return videos_data

# Alternative: More structured extraction
def extract_structured_admission_data(container):
    """Extract admission data in structured format"""
    if not container:
        return {}
    
    structured_data = {
        "eligibility": [],
        "admission_process": [],
        "exams": [],
        "syllabus": [],
        "colleges": {
            "government": {"btech": [], "mtech": []},
            "private": {"btech": [], "mtech": []}
        },
        "placements": []
    }
    
    # Find all headings
    headings = container.find_all(["h2", "h3", "h4"])
    
    for heading in headings:
        heading_text = heading.get_text(" ", strip=True).lower()
        
        # ELIGIBILITY SECTION
        if "eligibility" in heading_text:
            # Find next table
            table = heading.find_next("table")
            if table:
                eligibility_data = extract_clean_table_data(table)
                if eligibility_data:
                    structured_data["eligibility"].extend(eligibility_data)
        
        # ADMISSION PROCESS
        elif "admission process" in heading_text:
            # Find next list
            ul = heading.find_next("ul")
            if ul:
                process_steps = []
                for li in ul.find_all("li"):
                    # Clean text (remove links)
                    li_copy = BeautifulSoup(str(li), 'html.parser')
                    li_tag = li_copy.find('li')
                    for a_tag in li_tag.find_all('a'):
                        a_tag.replace_with(a_tag.get_text())
                    step_text = li_tag.get_text(" ", strip=True)
                    if step_text:
                        process_steps.append(step_text)
                structured_data["admission_process"] = process_steps
        
        # EXAMS
        elif "exams" in heading_text and "syllabus" not in heading_text:
            # Find next table
            table = heading.find_next("table")
            if table:
                exams_data = extract_clean_table_data(table)
                if exams_data:
                    structured_data["exams"] = exams_data
        
        # SYLLABUS
        elif "syllabus" in heading_text:
            # Find next table
            table = heading.find_next("table")
            if table:
                syllabus_data = extract_clean_table_data(table)
                if syllabus_data:
                    structured_data["syllabus"] = syllabus_data
        
        # COLLEGES
        elif "colleges" in heading_text:
            is_government = "government" in heading_text
            is_private = "private" in heading_text
            
            # Find BTech and MTech sections
            current = heading
            for _ in range(5):  # Look for next few headings
                current = current.find_next(["h4", "strong"])
                if not current:
                    break
                
                current_text = current.get_text(" ", strip=True).lower()
                
                if "btech" in current_text:
                    table = current.find_next("table")
                    if table:
                        college_data = extract_college_table_data(table)
                        if is_government:
                            structured_data["colleges"]["government"]["btech"] = college_data
                        elif is_private:
                            structured_data["colleges"]["private"]["btech"] = college_data
                
                elif "mtech" in current_text:
                    table = current.find_next("table")
                    if table:
                        college_data = extract_college_table_data(table)
                        if is_government:
                            structured_data["colleges"]["government"]["mtech"] = college_data
                        elif is_private:
                            structured_data["colleges"]["private"]["mtech"] = college_data
        
        # PLACEMENTS
        elif "placements" in heading_text:
            table = heading.find_next("table")
            if table:
                placements_data = extract_clean_table_data(table)
                if placements_data:
                    structured_data["placements"] = placements_data
    
    return structured_data

def extract_clean_table_data(table):
    """Extract clean table data without links"""
    data = []
    
    if not table:
        return data
    
    rows = table.find_all("tr")
    for row in rows:
        row_data = []
        cells = row.find_all(["td", "th"])
        
        for cell in cells:
            # Clean cell text (remove links)
            cell_copy = BeautifulSoup(str(cell), 'html.parser')
            cell_tag = cell_copy.find(cell.name)
            for a_tag in cell_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            cell_text = cell_tag.get_text(" ", strip=True)
            row_data.append(cell_text)
        
        if row_data:
            data.append(row_data)
    
    return data

def extract_college_table_data(table):
    """Extract college data from table"""
    colleges = []
    
    if not table:
        return colleges
    
    rows = table.find_all("tr")
    # Skip header row
    start_idx = 1 if rows[0].find("th") else 0
    
    for i in range(start_idx, len(rows)):
        row = rows[i]
        cols = row.find_all("td")
        
        if len(cols) >= 2:
            college_info = {}
            
            # First column: College name (clean text)
            first_col = cols[0]
            first_col_copy = BeautifulSoup(str(first_col), 'html.parser')
            first_col_tag = first_col_copy.find('td')
            for a_tag in first_col_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            college_info["name"] = first_col_tag.get_text(" ", strip=True)
            
            # Second column: Fee
            if len(cols) > 1:
                second_col = cols[1]
                second_col_copy = BeautifulSoup(str(second_col), 'html.parser')
                second_col_tag = second_col_copy.find('td')
                for a_tag in second_col_tag.find_all('a'):
                    a_tag.replace_with(a_tag.get_text())
                college_info["fee"] = second_col_tag.get_text(" ", strip=True)
            
            colleges.append(college_info)
    
    return colleges

# Updated main function with structured data
def scrape_admission_overview_structured(driver):
    """Main function with structured data extraction"""
    driver.get(PCOMBA_ADDMISSION_URL)
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "chp_admission_overview"))
        )
    except:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "wikkiContents"))
        )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {
        "title": "",
        "updated_on": "",
        "author": {},
        "overview": "",
        "structured_data": {},
        "content": {"blocks": []},
        "videos": []
    }
    
    section = soup.find("section", id="chp_admission_overview")
    if not section:
        return data
    
    # Extract title
    title_elem = soup.find("h1")
    if title_elem:
        data["title"] = title_elem.get_text(strip=True)
    
    # Extract date
    date_span = section.find("span")
    if date_span:
        data["updated_on"] = date_span.get_text(strip=True)
    
    # Extract author
    author_block = section.find("div", class_="c2675e")
    if author_block:
        author_data = {}
        
        img = author_block.find("img")
        if img:
            author_data["image"] = img.get("src", "")
        
        name_elem = author_block.find("p", class_="e9801a")
        if name_elem:
            author_link = name_elem.find("a")
            if author_link:
                author_data["name"] = author_link.get_text(strip=True)
            
            role_span = name_elem.find("span", class_="cbbdad")
            if role_span:
                author_data["role"] = role_span.get_text(strip=True)
        
        data["author"] = author_data
    
    # Extract overview (first paragraph)
    first_p = section.find("p")
    if first_p:
        # Clean paragraph text
        p_copy = BeautifulSoup(str(first_p), 'html.parser')
        p_tag = p_copy.find('p')
        for a_tag in p_tag.find_all('a'):
            a_tag.replace_with(a_tag.get_text())
        data["overview"] = p_tag.get_text(" ", strip=True)
    
    # Extract wikkiContents for structured data
    wikki_contents = section.find("div", id=lambda x: x and x.startswith("wikkiContents_chp_admission_overview"))
    if wikki_contents:
        # Extract structured data
        structured_data = extract_structured_admission_data(wikki_contents)
        data["structured_data"] = structured_data
        
        # Extract clean content (without links)
        content_data = extract_clean_content(wikki_contents)
        data["content"] = content_data
        
        # Extract videos
        videos_data = extract_videos_only(wikki_contents)
        data["videos"] = videos_data
    
    return data

def extract_clean_content(container):
    """Extract clean content without any links"""
    if not container:
        return {"blocks": []}
    
    content = {"blocks": []}
    main_div = container.find("div")
    
    if not main_div:
        return content
    
    # Find all direct children
    for element in main_div.find_all(recursive=False):
        # Skip tables (handled in structured data)
        if element.name == "table":
            continue
        
        # Skip video divs (handled separately)
        if element.name == "div" and "vcmsEmbed" in element.get("class", []):
            continue
        
        # Process headings
        if element.name in ["h2", "h3", "h4", "h5", "h6"]:
            # Clean heading text
            heading_copy = BeautifulSoup(str(element), 'html.parser')
            heading_tag = heading_copy.find(element.name)
            for a_tag in heading_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            
            heading_text = heading_tag.get_text(" ", strip=True)
            if heading_text:
                content["blocks"].append({
                    "type": "heading",
                    "level": element.name,
                    "value": heading_text
                })
        
        # Process paragraphs
        elif element.name == "p":
            # Clean paragraph text
            p_copy = BeautifulSoup(str(element), 'html.parser')
            p_tag = p_copy.find('p')
            for a_tag in p_tag.find_all('a'):
                a_tag.replace_with(a_tag.get_text())
            
            text = p_tag.get_text(" ", strip=True)
            if text and len(text.strip()) > 10:
                content["blocks"].append({
                    "type": "paragraph",
                    "value": text
                })
        
        # Process lists
        elif element.name in ["ul", "ol"]:
            items = []
            for li in element.find_all("li"):
                # Clean list item text
                li_copy = BeautifulSoup(str(li), 'html.parser')
                li_tag = li_copy.find('li')
                for a_tag in li_tag.find_all('a'):
                    a_tag.replace_with(a_tag.get_text())
                
                item_text = li_tag.get_text(" ", strip=True)
                if item_text:
                    items.append(item_text)
            
            if items:
                content["blocks"].append({
                    "type": "list",
                    "ordered": element.name == "ol",
                    "value": items
                })
    
    return content

def scrape_fees_overview_json(driver, timeout=30):
    driver.get(PCOMBA_FEES_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    result = {
       
                "title": None,
                "updated_on": None,
                "author": None,
                "author_profile_url": None,
                "author_designation": None,
                "content": []
            }
     

    
    # Extract title
    title = soup.find("div", class_="d8a6c4")
    if title:
        h1 = title.find("h1")
        if h1:
            result["title"] = h1.text.strip()
    
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # -------- meta --------
        # ---------- Updated On ----------
        try:
            updated_on_element = driver.find_element(
                By.XPATH, "//div[contains(text(),'Updated on')]/span"
            )
            result["updated_on"] = updated_on_element.text.strip()
        except:
            result["updated_on"] = None

        # ---------- Author Details ----------
        try:
            author_block = driver.find_element(By.CSS_SELECTOR, ".c2675e")
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
        # Find all wiki content sections
        wiki_sections = driver.find_elements(By.CSS_SELECTOR, ".wikkiContents.faqAccordian")
        
        for wiki_section in wiki_sections:
            # Get the section title (h2 before the wiki section)
            try:
                section_title_element = wiki_section.find_element(By.XPATH, "./preceding-sibling::h2[@class='tbSec2'][1]")
                section_title = section_title_element.text.strip()
            except:
                # Try alternative method to find section title
                try:
                    section_title_element = driver.execute_script("""
                        var element = arguments[0];
                        var prev = element.previousElementSibling;
                        while (prev) {
                            if (prev.tagName === 'H2' && prev.className.includes('tbSec2')) {
                                return prev;
                            }
                            prev = prev.previousElementSibling;
                        }
                        return null;
                    """, wiki_section)
                    if section_title_element:
                        section_title = section_title_element.text.strip()
                    else:
                        pass
                except:
                    pass
            
            # Create section object
            section_data = {
                # "section_title": section_title,
                "subsections": []
            }
            
            # Process content within the wiki section
            current_subsection = None
            
            # Get all child elements
            elements = wiki_section.find_elements(By.XPATH, ".//div[contains(@class, 'faqAccordian')]//* | .//p | .//h3 | .//h4 | .//table")
            
            for element in elements:
                tag_name = element.tag_name.lower()
                text = element.text.strip()
                
                if not text:
                    continue
                
                # Handle H3 subsections
                if tag_name == "h3":
                    current_subsection = {
                        "subsection_title": text,
                        "content": []
                    }
                    section_data["subsections"].append(current_subsection)
                
                # Handle H4 sub-subsections
                elif tag_name == "h4":
                    if current_subsection:
                        subsubsection = {
                            "subsubsection_title": text,
                            "content": []
                        }
                        current_subsection["content"].append(subsubsection)
                
                # Handle paragraphs
                elif tag_name == "p":
                    para_data = {
                        "type": "paragraph",
                        "text": text
                    }
                    
                    # Check if it's a note
                    if "note" in text.lower() or "info" in text.lower():
                        para_data["type"] = "note"
                    
                    # Check for links
                    links = element.find_elements(By.TAG_NAME, "a")
                    if links:
                        para_data["links"] = []
                        for link in links:
                            para_data["links"].append({
                                "text": link.text.strip(),
                                "url": link.get_attribute("href")
                            })
                    
                    # Add to appropriate level
                    if current_subsection:
                        if current_subsection["content"] and isinstance(current_subsection["content"][-1], dict) and "subsubsection_title" in current_subsection["content"][-1]:
                            current_subsection["content"][-1]["content"].append(para_data)
                        else:
                            current_subsection["content"].append(para_data)
                    else:
                        section_data["subsections"].append({
                            
                            "content": [para_data]
                        })
                
                # Handle tables
                elif tag_name == "table":
                    table_data = {
                        "type": "table",
                        "headers": [],
                        "rows": []
                    }
                    
                    # Extract headers
                    try:
                        header_row = element.find_element(By.TAG_NAME, "tr")
                        headers = header_row.find_elements(By.TAG_NAME, "th")
                        if not headers:
                            headers = header_row.find_elements(By.TAG_NAME, "td")
                        
                        for header in headers:
                            table_data["headers"].append(header.text.strip())
                    except:
                        table_data["headers"] = ["College/Institution", "Fees"]
                    
                    # Extract rows
                    rows = element.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            row_data = {}
                            for i, cell in enumerate(cells):
                                cell_text = cell.text.strip()
                                
                                # Extract links
                                links = cell.find_elements(By.TAG_NAME, "a")
                                if links:
                                    link_info = []
                                    for link in links:
                                        link_info.append({
                                            "text": link.text.strip(),
                                            "url": link.get_attribute("href")
                                        })
                                    row_data[table_data["headers"][i] if i < len(table_data["headers"]) else f"Column_{i+1}"] = {
                                        "text": cell_text,
                                        "links": link_info
                                    }
                                else:
                                    row_data[table_data["headers"][i] if i < len(table_data["headers"]) else f"Column_{i+1}"] = cell_text
                            
                            if row_data:
                                table_data["rows"].append(row_data)
                    
                    # Add table to appropriate level
                    if current_subsection:
                        if current_subsection["content"] and isinstance(current_subsection["content"][-1], dict) and "subsubsection_title" in current_subsection["content"][-1]:
                            current_subsection["content"][-1]["content"].append(table_data)
                        else:
                            current_subsection["content"].append(table_data)
                    else:
                        section_data["subsections"].append({
                          
                            "content": [table_data]
                        })
                
                # Handle embedded content
                elif tag_name == "div" and "vcmsEmbed" in element.get_attribute("class"):
                    iframes = element.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        iframe = iframes[0]
                        embed_data = {
                       
                            "url": iframe.get_attribute("src"),
                            "title": iframe.get_attribute("title") or "Embedded Video"
                        }
                        
                        if current_subsection:
                            current_subsection["content"].append(embed_data)
            
            # Add section to main content
            result["content"].append(section_data)
        
        # If no wiki sections found, try alternative approach
        if not result["content"]:
            # Extract all h2 sections
            h2_sections = driver.find_elements(By.CSS_SELECTOR, "h2.tbSec2")
            
            for h2 in h2_sections:
                section_title = h2.text.strip()
                section_data = {
                    "section_title": section_title,
                    "subsections": []
                }
                
                # Get content after this h2 until next h2
                try:
                    next_elements = driver.execute_script("""
                        var element = arguments[0];
                        var contents = [];
                        var next = element.nextElementSibling;
                        
                        while (next && !(next.tagName === 'H2' && next.className.includes('tbSec2'))) {
                            contents.push(next);
                            next = next.nextElementSibling;
                        }
                        return contents;
                    """, h2)
                    
                    current_subsection = None
                    
                    for elem in next_elements:
                        tag_name = elem.tag_name.lower() if hasattr(elem, 'tag_name') else 'div'
                        text = elem.text.strip()
                        
                        if not text:
                            continue
                        
                        # Similar processing logic as above...
                        # (You would add the same processing logic here for fallback)
                        
                except:
                    pass
                
                if section_data["subsections"]:
                    result["content"].append(section_data)

        return result

    except TimeoutException:
        print("Timeout occurred while loading the page")
        return result
    except Exception as e:
        print(f"Error scraping fees overview: {e}")
        import traceback
        traceback.print_exc()
        return result
    
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

def scrape_5years(driver):
    driver.get(PCOMBA_5YEARS_URL)
    time.sleep(5)
    # Wait for main content to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".wikkiContents"))
    )
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    scraped_data = {
        "title":None,
        "author":{},
        "article_info": {},
        "engineering_trends": {},
        "top_streams": [],
        "trending_streams": [],
        "related_links": [],
        "complete_article": []  # All content in sequence
    }

    # ---------------------------
    # 1. Article Info
    # ---------------------------
    # Get author properly
    title = soup.find("div",class_="flx-box mA")
    if title:
        h1 = title.find("h1").text.strip()
        scraped_data["title"]= h1
    else:
        pass
    # ---------- META (date + author) ----------
    author_data = {}
    author_block = soup.find("div", class_="c2675e")

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

    scraped_data["author"] = author_data
        
    author_link = soup.select_one('.adp_user a')
    if author_link:
        # Get text and remove tick icon
        author_text = author_link.get_text(strip=True)
        # Clean the author name
        scraped_data["article_info"]["author"] = re.sub(r'\s*<.*?>.*?</.*?>', '', author_text).strip()
    else:
        pass
    
    scraped_data["article_info"]["author_role"] = soup.select_one('.user_expert_level').get_text(strip=True) if soup.select_one('.user_expert_level') else None
    
    # Get updated date - fix for "6mins read" issue
    blogdata_span = soup.select_one('.blogdata_user span')
    if blogdata_span:
        date_text = blogdata_span.get_text(strip=True)
        # Check if it's actually a date or "6mins read"
        if 'Updated' in date_text:
            scraped_data["article_info"]["updated_date"] = date_text
        else:
            # Look for date elsewhere
            date_elem = soup.find(string=re.compile(r'Updated on'))
            scraped_data["article_info"]["updated_date"] = date_elem.strip() if date_elem else date_text
    else:
        scraped_data["article_info"]["updated_date"] = None
    
    scraped_data["article_info"]["summary"] = soup.select_one('#blogSummary').get_text(strip=True) if soup.select_one('#blogSummary') else None
    
    # Get main image caption
    img_caption = soup.select_one('._img-caption')
    scraped_data["article_info"]["main_image_caption"] = img_caption.get_text(strip=True) if img_caption else None

    # ---------------------------
    # 2. COMPLETE ARTICLE CONTENT EXTRACTION
    # ---------------------------
    # Get the main article container
    article_container = soup.find('div', id='blogId-144539') or soup.find('div', class_='adpPwa_summary')
    
    if article_container:
        # Get ALL wikkiContents divs in order
        all_wikki_divs = article_container.find_all('div', class_='wikkiContents')
        
        for wikki_div in all_wikki_divs:
            # Skip empty divs
            if not wikki_div.text.strip():
                continue
            
            # Process all elements in this div
            elements = wikki_div.find_all(['h2', 'h3', 'p', 'ul', 'table'])
            
            for element in elements:
                # Handle headings
                if element.name in ['h2', 'h3']:
                    heading_text = element.get_text(strip=True)
                    if heading_text:
                        scraped_data["complete_article"].append({
                            "type": "heading",
                            "level": element.name,
                            "text": heading_text,
                            "id": element.get('id', '')
                        })
                
                # Handle paragraphs (EXCLUDE table content)
                elif element.name == 'p':
                    # Skip if inside a table
                    if element.find_parent('table'):
                        continue
                    
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        # Skip image captions and "Also Read"/"Read More"
                        if not element.find_parent('div', class_='photo-widget-full'):
                            if not any(x in text for x in ["Also Read:", "Read More:"]):
                                scraped_data["complete_article"].append({
                                    "type": "paragraph",
                                    "text": text
                                })
                
                # Handle list items (but not for tables)
                elif element.name == 'ul':
                    # Skip if inside a table
                    if element.find_parent('table'):
                        continue
                    
                    for li in element.find_all('li'):
                        text = li.get_text(strip=True)
                        if text:
                            scraped_data["complete_article"].append({
                                "type": "list_item",
                                "text": text
                            })
    
    # ---------------------------
    # 3. Engineering Trends Table
    # ---------------------------
    trends_table = soup.find('table', style=re.compile(r'height\s*:\s*185px'))
    if trends_table:
        rows = trends_table.find_all('tr')
        if len(rows) >= 3:
            years = [cell.get_text(strip=True) for cell in rows[0].find_all(['th','td'])[1:6]]
            trends_data = []
            for row in rows[2:]:
                cells = row.find_all(['td','th'])
                if len(cells) >= 6:
                    stream_name = cells[0].get_text(strip=True)
                    link = cells[0].find('a')
                    if link:
                        stream_name = link.get_text(strip=True)
                    enrollments = {}
                    for i in range(1,6):
                        text = cells[i].get_text(strip=True)
                        match = re.search(r'([\d\.]+)', text.replace(',', ''))
                        enrollments[years[i-1]] = float(match.group(1)) if match else None
                    trends_data.append({"stream": stream_name, "enrollments": enrollments})
            scraped_data["engineering_trends"] = {
                "data_source": "AISHE Reports",
                "years": years,
                "streams": trends_data,
                "note": "Enrollment numbers in lakhs",
                "total_streams_extracted": len(trends_data)
            }

    # ---------------------------
    # 4. Top Streams
    # ---------------------------
    top_section = soup.find('h2', id='toc_section_2')
    if top_section:
        # Find the parent wikkiContents div containing top streams section
        parent_div = top_section.find_parent('div', class_='wikkiContents')
        if parent_div:
            # Find all h3 in this section
            h3_elements = parent_div.find_all('h3')
            
            for idx, h3 in enumerate(h3_elements[:5], 1):  # Limit to 5
                stream_name = re.sub(r'^#\d+\.\s*', '', h3.get_text(strip=True))
                stream_data = {"rank": idx, "stream": stream_name, "career_opportunities": [], "colleges": []}

                # Get career opportunities from the next UL
                next_ul = h3.find_next('ul')
                if next_ul:
                    # Find nested ULs (the actual career list is in a nested UL)
                    nested_uls = next_ul.find_all('ul')
                    if nested_uls:
                        # First nested UL contains career opportunities
                        career_ul = nested_uls[0]
                        for li in career_ul.find_all('li'):
                            text = li.get_text(strip=True)
                            if text and not text.startswith('Career Opportunities:'):
                                stream_data["career_opportunities"].append(text)
                
                # Get colleges table
                table = h3.find_next('table')
                if table:
                    colleges = []
                    rows = table.find_all('tr')
                    if len(rows) > 1:
                        for row in rows[1:]:
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                colleges.append({
                                    "institute_name": cells[0].get_text(strip=True),
                                    "nirf_rank": cells[1].get_text(strip=True),
                                    "admission_mode": cells[2].get_text(strip=True)
                                })
                    stream_data["colleges"] = colleges
                
                scraped_data["top_streams"].append(stream_data)

    # ---------------------------
    # 5. Trending Streams
    # ---------------------------
    trending_section = soup.find('h2', id='toc_section_3')
    if trending_section:
        parent_div = trending_section.find_parent('div', class_='wikkiContents')
        if parent_div:
            trending_data = {
                "stream_category": "AI/Data Science/ML", 
                "career_opportunities": [], 
                "colleges": []
            }
            
            # Get career opportunities
            next_ul = trending_section.find_next('ul')
            if next_ul:
                nested_uls = next_ul.find_all('ul')
                if nested_uls:
                    career_ul = nested_uls[0]
                    for li in career_ul.find_all('li'):
                        text = li.get_text(strip=True)
                        if text and not text.startswith('Career opportunities:'):
                            trending_data["career_opportunities"].append(text)
            
            # Get colleges table
            table = trending_section.find_next('table')
            if table:
                colleges = []
                rows = table.find_all('tr')
                if len(rows) > 1:
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            colleges.append({
                                "institute_name": cells[0].get_text(strip=True),
                                "nirf_rank": cells[1].get_text(strip=True),
                                "admission_mode": cells[2].get_text(strip=True)
                            })
                trending_data["colleges"] = colleges
            
            scraped_data["trending_streams"].append(trending_data)

    # ---------------------------
    # 6. Related Links
    # ---------------------------
    for text in ["Also Read:", "Read More:"]:
        p_tag = soup.find('p', string=lambda s: text in str(s) if s else False)
        if p_tag:
            ul = p_tag.find_next('ul')
            if ul:
                for a in ul.find_all('a'):
                    link_data = {
                        "text": a.get_text(strip=True), 
                        "url": a.get('href','#')
                    }
                    if not any(link['text'] == link_data['text'] for link in scraped_data["related_links"]):
                        scraped_data["related_links"].append(link_data)

    # ---------------------------
    # 7. Extract ALL paragraphs separately (for verification)
    # ---------------------------
    all_paragraphs_list = []
    
    # Method 1: Get all paragraphs from wikkiContents
    wikki_divs = soup.find_all('div', class_='wikkiContents')
    for wikki in wikki_divs:
        paragraphs = wikki.find_all('p')
        for p in paragraphs:
            # Skip if inside table
            if p.find_parent('table'):
                continue
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                # Filter out unwanted text
                skip_keywords = ["Also Read:", "Read More:", "Institute Name", "NIRF", "Mode of", "Year", "2020-21"]
                if not any(keyword in text for keyword in skip_keywords):
                    all_paragraphs_list.append(text)
    
    # Method 2: Get paragraphs from specific sections
    sections = soup.find_all(['h2', 'h3'])
    for section in sections:
        if section.name == 'h2' and section.get('id', '').startswith('toc_section_'):
            # Get paragraph right after heading
            next_p = section.find_next('p')
            if next_p:
                text = next_p.get_text(strip=True)
                if text and text not in all_paragraphs_list:
                    all_paragraphs_list.append(text)
    
    # Add to scraped_data
    scraped_data["all_paragraphs"] = all_paragraphs_list

    # ---------------------------
    # 8. Extract specific missing paragraphs
    # ---------------------------
    missing_content = []
    
    # Paragraphs that should be captured:
    target_phrases = [
        "Over the past 5 years, enrollment in the computer engineering stream",
        "Steadily, the engineering streams that are growing in popularity",
        "Under the National Education Policy (NEP) 2020",
        "Here are the top 5 engineering streams that enjoy high popularity"
    ]
    
    # Search for these paragraphs
    for wikki in wikki_divs:
        paragraphs = wikki.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            for phrase in target_phrases:
                if phrase in text and text not in missing_content:
                    missing_content.append(text)
                    break
    
    if missing_content:
        scraped_data["key_paragraphs"] = missing_content

    return scraped_data

def scrape_blog_paid(driver):
    driver.get(PCOMBA_PAID_URL)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    blog_data = {}
    
    # ---------------------------------
    # AUTHOR INFO (FIXED)
    # ---------------------------------
    img = soup.find("picture")
    if img:
        source = img.find("source")
        src=source.get("srcset")
        blog_data["img"]=src
    else:
        pass
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

def extract_article_data(driver):
    """
    Extract article data from the given URL
    """
    driver.get(PCOMBA_GOODSCROR_URL)
    # Wait for page to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "adp_blog"))
    )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Initialize data dictionary
    data = {}
    
    # ==============================
    # ARTICLE TITLE
    # ==============================
    title_elem = soup.find("h1")
    if title_elem:
        data["title"] = title_elem.get_text(strip=True)
    
    # ==============================
    # AUTHOR INFO
    # ==============================
    author_data = {}
    author_div = soup.find("div", class_="adp_user_tag")
    
    if author_div:
        author_link = author_div.find("a", class_="user-img")
        author_name_div = author_div.find("div", class_="adp_usr_dtls")
        
        if author_link:
            # Author profile URL
            author_data["profile_url"] = author_link.get("href", "")
            # Author image
            img = author_link.find("img")
            if img:
                author_data["image_url"] = img.get("src", "")
        
        if author_name_div:
            author_name_link = author_name_div.find("a")
            if author_name_link:
                # Extract author name without the tick icon text
                author_name_text = author_name_link.get_text(strip=True)
                # Remove any extra spaces and separate name
                if "Satyendra" in author_name_text:
                    author_data["name"] = "Satyendra Singh"
                else:
                    author_data["name"] = author_name_text
    
    data["author"] = author_data
    
    # ==============================
    # UPDATE DATE
    # ==============================
    date_span = soup.find("div", class_="blogdata_user").find("span")
    if date_span:
        data["updated_date"] = date_span.get_text(strip=True)
    
    # ==============================
    # SUMMARY
    # ==============================
    summary_div = soup.find("div", class_="blogSummary")
    if summary_div:
        data["summary"] = summary_div.get_text(strip=True)
    
    # ==============================
    # MAIN CONTENT
    # ==============================
    main_content = {}
    
    # Extract image and caption
    photo_widget = soup.find("div", class_="photo-widget-full")
    if photo_widget:
        img = photo_widget.find("img")
        if img:
            main_content["featured_image"] = {
                "url": img.get("src", ""),
                "alt": img.get("alt", ""),
                "width": img.get("width", ""),
                "height": img.get("height", "")
            }
        
        caption = photo_widget.find("p")
        if caption:
            strong = caption.find("strong")
            if strong:
                main_content["image_caption"] = strong.get_text(strip=True)
    
    # Extract content sections
    content_sections = []
    
    # Get all wikkiContents sections
    wikki_sections = soup.find_all("div", class_="wikkiContents")
    
    for section in wikki_sections:
        section_data = {}
        
        # Check if section has heading
        heading = section.find(["h1", "h2", "h3", "h4", "h5", "h6"])
        if heading:
            section_data["heading"] = heading.get_text(strip=True)
            heading_id = heading.get("id", "")
            if heading_id:
                section_data["id"] = heading_id
        
        # Extract paragraphs
        paragraphs = section.find_all("p")[:1]
        if paragraphs:
            section_data["paragraphs"] = [
                p.get_text(" ", strip=True) 
                for p in paragraphs 
                if p.get_text(strip=True)
            ]
        
        # Extract tables
        tables = section.find_all("table")
        if tables:
            section_data["tables"] = []
            for table in tables:
                table_data = []
                for row in table.find_all("tr"):
                    row_data = []
                    for cell in row.find_all(["th", "td"]):
                        row_data.append(cell.get_text(" ", strip=True))
                    if row_data:
                        table_data.append(row_data)
                if table_data:
                    section_data["tables"].append(table_data)
        
        # Extract lists
        lists = section.find_all(["ul", "ol"])
        if lists:
            section_data["lists"] = []
            for list_elem in lists:
                items = [
                    li.get_text(" ", strip=True) 
                    for li in list_elem.find_all("li")
                ]
                if items:
                    section_data["lists"].append(items)
        
        # Extract links
        links = section.find_all("a")
        if links:
            section_data["links"] = []
            for link in links:
                link_text = link.get_text(strip=True)
                link_url = link.get("href", "")
                if link_text and link_url:
                    section_data["links"].append({
                        "text": link_text,
                        "url": link_url
                    })
        
        if section_data:
            content_sections.append(section_data)
    
    main_content["sections"] = content_sections
    data["content"] = main_content
    
    # ==============================
    # TABLE OF CONTENTS
    # ==============================
    toc_div = soup.find("div", class_="b644f8")
    if toc_div:
        toc_items = []
        toc_list = toc_div.find("ul", class_="cea02e")
        if toc_list:
            for item in toc_list.find_all("li"):
                item_text = item.get_text(strip=True)
                item_id = item.get("data-scrol", "")
                if item_text:
                    toc_items.append({
                        "text": item_text,
                        "id": item_id
                    })
        if toc_items:
            data["table_of_contents"] = toc_items
    
    # ==============================
    # FAQ SECTION
    # ==============================
    faq_section = soup.find("div", class_="ab3f81")
    if faq_section:
        faqs = []
        faq_items = faq_section.find_all("div", id=lambda x: x and "::" in str(x))
        
        for i in range(0, len(faq_items), 2):
            if i + 1 < len(faq_items):
                question_div = faq_items[i]
                answer_div = faq_items[i + 1]
                
                # Extract question
                question_text = ""
                question_span = question_div.find("span", recursive=True)
                if question_span:
                    question_text = question_span.get_text(strip=True)
                
                # Extract answer
                answer_text = ""
                answer_content = answer_div.find("div", class_="cmsAContent")
                if answer_content:
                    answer_text = answer_content.get_text(" ", strip=True)
                
                if question_text and answer_text:
                    faqs.append({
                        "question": question_text,
                        "answer": answer_text
                    })
        
        if faqs:
            data["faqs"] = faqs
    
    # ==============================
    # POLL DATA
    # ==============================
    poll_div = soup.find("div", id="poll-container-box-1")
    if poll_div:
        poll_data = {}
        
        # Poll question
        question_div = poll_div.find("div", class_="poll-question")
        if question_div:
            poll_data["question"] = question_div.get_text(strip=True)
        
        # Poll options
        options_div = poll_div.find("div", class_="poll-options")
        if options_div:
            options = []
            for option_div in options_div.find_all("div", class_="poll-option"):
                label = option_div.find("label")
                if label:
                    options.append(label.get_text(strip=True))
            if options:
                poll_data["options"] = options
        
        # Poll stats
        info_div = poll_div.find("div", class_="poll-info")
        if info_div:
            votes_span = info_div.find("span", class_="poll-info-text")
            if votes_span:
                poll_data["votes"] = votes_span.get_text(strip=True)
        
        if poll_data:
            data["poll"] = poll_data
    
    # ==============================
    # RECOMMENDED COLLEGES
    # ==============================
    reco_widget = soup.find("div", class_="recoWidgetSection")
    if reco_widget:
        colleges = []
        college_cards = reco_widget.find_all("div", class_="collegCard")
        
        for card in college_cards:
            college_info = {}
            
            # College name and URL
            name_link = card.find("a", class_="blackLink")
            if name_link:
                college_info["name"] = name_link.get_text(strip=True)
                college_info["url"] = name_link.get("href", "")
            
            # College logo
            logo = card.find("img", class_="lImg")
            if logo:
                college_info["logo"] = logo.get("src", "")
            
            # Location
            location_div = card.find("div", class_="location")
            if location_div:
                location_span = location_div.find("span", class_="locationName")
                if location_span:
                    college_info["location"] = location_span.get_text(strip=True)
            
            # NIRF Rank
            rank_span = card.find("span", class_="rank")
            if rank_span:
                college_info["nirf_rank"] = rank_span.get_text(strip=True)
            
            # Courses and fees
            bluLinkBox = card.find("div", class_="bluLinkBox")
            if bluLinkBox:
                course_link = bluLinkBox.find("a", class_="link")
                if course_link:
                    college_info["courses_offered"] = course_link.get_text(strip=True)
                
                starBox = bluLinkBox.find("span", class_="starBox")
                if starBox:
                    college_info["rating"] = starBox.get_text(strip=True)
            
            # Fees
            fees_div = card.find("span", class_="comma")
            if fees_div:
                college_info = fees_div.get_text(strip=True)
            
            if college_info:
                colleges.append(college_info)
        
        if colleges:
            data["recommended_colleges"] = colleges
    
    return data


# def extract_rich_content_from_article(driver):

#     driver.get(PCOMBA_GOODSCROR_URL)
#     WebDriverWait(driver, 15).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "adp_blog"))
#     )
    
#     soup = BeautifulSoup(driver.page_source, "html.parser")
    
#     # Find the main article container
#     article_container = soup.find("div", id=lambda x: x and "blogId-" in str(x))
#     if not article_container:
#         return {"blocks": []}
    
#     content = {"blocks": []}
    
#     def parse_node(node):
#         # Skip script and style tags
#         if node.name in ["script", "style"]:
#             return
        
#         # HEADINGS
#         if node.name in ["h1", "h2", "h3", "h4"]:
#             text = node.get_text(" ", strip=True)
#             if text:
#                 content["blocks"].append({
#                     "type": "heading",
#                     "value": text,
#                     "level": int(node.name[1]) if node.name.startswith("h") else 1
#                 })
#             return
        
#         # PARAGRAPHS
#         elif node.name == "p":
#             if node.find_parent("table"):
#                 return
#             text = node.get_text(" ", strip=True)
#             if text:
#                 # Check if it's a caption
#                 if node.find("strong", class_="_img-caption"):
#                     content["blocks"].append({
#                         "type": "image_caption",
#                         "value": text
#                     })
#                 else:
#                     content["blocks"].append({
#                         "type": "paragraph",
#                         "value": text
#                     })
#             return
        
#         # LISTS
#         elif node.name in ["ul", "ol"]:
#             items = []
#             for li in node.find_all("li", recursive=False):
#                 item_text = li.get_text(" ", strip=True)
#                 if item_text:
#                     items.append(item_text)
            
#             if items:
#                 content["blocks"].append({
#                     "type": "list",
#                     "value": items,
#                     "ordered": node.name == "ol"
#                 })
#             return
        
#         # TABLES
#         elif node.name == "table":
#             table_data = []
#             for row in node.find_all("tr"):
#                 cols = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
#                 if cols:
#                     table_data.append(cols)
            
#             if table_data:
#                 content["blocks"].append({
#                     "type": "table",
#                     "value": table_data
#                 })
#             return
        
#         # IMAGES
#         elif node.name == "img":
#             src = node.get("src") or node.get("data-src")
#             if src:
#                 img_block = {
#                     "type": "image",
#                     "value": src,
#                     "alt": node.get("alt", ""),
#                     "width": node.get("width", ""),
#                     "height": node.get("height", "")
#                 }
                
#                 # Check for picture element parent
#                 if node.find_parent("picture"):
#                     source_tags = node.find_previous_siblings("source")
#                     if source_tags:
#                         img_block["sources"] = []
#                         for source in source_tags:
#                             img_block["sources"].append({
#                                 "srcset": source.get("srcset", ""),
#                                 "media": source.get("media", "")
#                             })
                
#                 content["blocks"].append(img_block)
#             return
        
#         # LINKS
#         elif node.name == "a" and node.get("href"):
#             if node.find_parent("table"):
#                 return
#             link_text = node.get_text(" ", strip=True)
#             if link_text:
#                 content["blocks"].append({
#                     "type": "link",
#                     "value": {
#                         "text": link_text,
#                         "url": node.get("href", "")
#                     }
#                 })
#             return
        
#         # IFRAMES
#         elif node.name == "iframe":
#             src = node.get("src") or node.get("data-src")
#             if src:
#                 content["blocks"].append({
#                     "type": "iframe",
#                     "value": src
#                 })
#             return
        
#         # DIVS and other containers - process their children
#         elif node.name in ["div", "section", "article"]:
#             # Skip certain containers
#             skip_classes = ["recoWidgetSection", "photo-widget-full", "poll-container"]
#             if any(cls in str(node.get("class", [])) for cls in skip_classes):
#                 return
            
#             for child in node.children:
#                 if child.name:
#                     parse_node(child)
    
#     # Start parsing from the main container
#     for child in article_container.children:
#         if child.name:
#             parse_node(child)
    
#     return content

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
              "Textile Design":{
                "overviews":extract_overview_data(driver),
                # "course":extract_courses__data(driver),
                # "subject":extract_environmental_subjects_data(driver),
                "syllabus":extract_syllabus__data(driver),
                "career":scrape_career_overview(driver),
                # "salary":scrape_civil_engineering_data(driver),
                # "Good score":extract_article_data(driver),
                "addmision":scrape_admission_overview(driver),
                # "5years":scrape_5years(driver),
                # "paid":scrape_blog_paid(driver),
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

