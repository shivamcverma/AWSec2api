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

PCOMBA_O_URL="https://www.shiksha.com/engineering/mechanical-engineering-chp"
PCOMBA_C_URL="https://www.shiksha.com/engineering/mechanical-engineering-courses-chp"
# PCOMBA_S_URL="https://www.shiksha.com/engineering/computer-science-engineering-syllabus-chp"
# PCOMBA_CAREER_URL = "https://www.shiksha.com/engineering/mechanical-engineering-career-chp"
PCOMBA_SUB_URL= "https://www.shiksha.com/engineering/mechanical-engineering-subjects-chp"
PCOMBA_SALARY_URL = "https://www.shiksha.com/engineering/mechanical-engineering-career-chp"
PCOMBA_ADDMISSION_URL="https://www.shiksha.com/engineering/mechanical-engineering-admission-chp"
# PCOMBA_FEES_URL = "https://www.shiksha.com/engineering/computer-science-engineering-fees-chp"
# PCOMBA_JEEVSBITSAK_URL = "https://www.shiksha.com/engineering/articles/jee-main-vs-bitsat-exam-difficulty-level-pattern-and-syllabus-blogId-53799"
PCOMBA_Q_URL = "https://www.shiksha.com/tags/mechanical-engineering-tdp-204"
PCOMBA_QD_URL="https://www.shiksha.com/tags/mechanical-engineering-tdp-204?type=discussion"


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

# def scrape_syllabus_section(driver):
#     driver.get(PCOMBA_S_URL)
#     time.sleep(3)

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     syllabus_data = {}

#     syllabus_section = soup.find("section", id="chp_syllabus_overview")
#     if not syllabus_section:
#         return syllabus_data

#     # ---------------------------------
#     # TITLE
#     # ---------------------------------
#     title = soup.find("h1")
#     syllabus_data["title"] = title.get_text(strip=True) if title else None

#     # ---------------------------------
#     # UPDATED DATE
#     # ---------------------------------
#     updated_span = syllabus_section.select_one("div.d957ae span")
#     syllabus_data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

#     # ---------------------------------
#     # AUTHOR INFO
#     # ---------------------------------
#     author_name = syllabus_section.select_one("p.e9801a a")
#     author_role = syllabus_section.select_one("p.e9801a span.cbbdad")

#     syllabus_data["author"] = {
#         "name": author_name.get_text(strip=True) if author_name else None,
#         "profile_url": author_name["href"] if author_name else None,
#         "role": author_role.get_text(strip=True) if author_role else None
#     }

#     # ---------------------------------
#     # 🔥 PURE FULL TEXT (NO DATA LOSS)
#     # ---------------------------------
#     text_parts = []
#     for p in syllabus_section.find_all(["p", "li"], limit=200):
#         text_parts.append(p.get_text(" ", strip=True))

#     syllabus_data["full_section_text"] = "\n".join(text_parts)


#     # ---------------------------------
#     # OVERVIEW / INTRO CONTENT
#     # ---------------------------------
#     overview_block = syllabus_section.select_one("#wikkiContents_chp_syllabus_overview_0")
#     overview_paragraphs = []

#     if overview_block:
#         for p in overview_block.find_all("p"):
#             text = p.get_text(" ", strip=True)
#             if text and len(text) > 20:
#                 overview_paragraphs.append(text)

#     syllabus_data["overview"] = overview_paragraphs

#     # ---------------------------------
#     # LINKS PRESENT IN OVERVIEW
#     # ---------------------------------
#     overview_links = []
#     if overview_block:
#         for a in overview_block.find_all("a", href=True):
#             overview_links.append({
#                 "text": a.get_text(strip=True),
#                 "url": a["href"]
#             })

#     syllabus_data["overview_links"] = overview_links

#     # ---------------------------------
#     # 🔥 FAQ SECTION (QUESTIONS + ANSWERS)
#     # ---------------------------------
#     faqs = []
#     faq_blocks = syllabus_section.select(".sectional-faqs > div")

#     i = 0
#     while i < len(faq_blocks):
#         q_block = faq_blocks[i]
#         a_block = faq_blocks[i + 1] if i + 1 < len(faq_blocks) else None

#         question = q_block.get_text(" ", strip=True).replace("Q:", "").strip()

#         answer = None
#         if a_block:
#             answer_div = a_block.select_one(".cmsAContent")
#             if answer_div:
#                 answer = answer_div.get_text("\n", strip=True)

#         if question and answer:
#             faqs.append({
#                 "question": question,
#                 "answer": answer
#             })

#         i += 2
#    # 🔥 NEW SECTION: CORE + ELECTIVE + BOOKS
#     # =====================================================
#     popular_section = soup.find("section", id="chp_syllabus_popularspecialization")
#     popular_data = {}

#     if popular_section:
#         popular_data["section_title"] = popular_section.find("h2").get_text(strip=True)

#         from html import unescape

#         intro_content = []

#         intro_block = popular_section.find(
#             "div", id="wikkiContents_chp_syllabus_popularspecialization_0"
#         )

#         SKIP_TEXTS = {
#             "Core CSE Subjects",
#             "CSE Subject Details",
#             "Elective CSE Subjects"
#         }

#         if intro_block:
#             for tag in intro_block.find_all(["h2", "h3", "p"], recursive=True):

#                 # ❌ skip if tag is inside table
#                 if tag.find_parent("table"):
#                     continue

#                 text = unescape(tag.get_text(" ", strip=True))

#                 # ❌ skip junk / table labels / notes
#                 if (
#                     not text
#                     or len(text) < 25
#                     or text in SKIP_TEXTS
#                     or text.lower().startswith("note")
#                 ):
#                     continue

#                 intro_content.append({
#                     "type": tag.name,
#                     "text": text
#                 })

#         popular_data["intro"] = intro_content

#         # -------- CORE SUBJECTS TABLE --------
#         core_subjects = []
#         core_table = popular_section.find("h3", string=lambda x: x and "Core Computer" in x)
#         if core_table:
#             table = core_table.find_next("table")
#             for row in table.find_all("tr")[1:]:
#                 cols = row.find_all("td")
#                 if len(cols) == 2:
#                     core_subjects.append({
#                         "subject": cols[0].get_text(strip=True),
#                         "details": cols[1].get_text(" ", strip=True)
#                     })
#         popular_data["core_subjects"] = core_subjects

#         # -------- ELECTIVE SUBJECTS TABLE --------
#         elective_subjects = []
#         elective_table = popular_section.find("h3", string=lambda x: x and "Elective Computer" in x)
#         if elective_table:
#             table = elective_table.find_next("table")
#             for row in table.find_all("tr")[1:]:
#                 cols = row.find_all("td")
#                 if len(cols) == 2:
#                     elective_subjects.append({
#                         "subject": cols[0].get_text(strip=True),
#                         "details": cols[1].get_text(" ", strip=True)
#                     })
#         popular_data["elective_subjects"] = elective_subjects

#         # -------- POPULAR BOOKS TABLE --------
#         books = []
#         books_heading = popular_section.find("h2", string=lambda x: x and "Popular Books" in x)
#         if books_heading:
#             table = books_heading.find_next("table")
#             for row in table.find_all("tr")[1:]:
#                 cols = row.find_all("td")
#                 if len(cols) == 3:
#                     books.append({
#                         "subject": cols[0].get_text(strip=True),
#                         "book_title": cols[1].get_text(" ", strip=True),
#                         "author": cols[2].get_text(" ", strip=True)
#                     })
#         popular_data["recommended_books"] = books

#     syllabus_data["popular_specialization"] = popular_data
 
    
#     syllabus_data["faqs"] = faqs

#     from html import unescape

#     comparison_data = {}

#     block = soup.find(
#         "div", id="wikkiContents_chp_syllabus_topratecourses_0"
#     )

#     if block:
#         inner = block.find("div")

#         # 1️⃣ Intro paragraph (top)
#         intro_p = inner.find("p")
#         comparison_data["intro"] = unescape(
#             intro_p.get_text(" ", strip=True)
#         ) if intro_p else ""

#         # 2️⃣ Title (h3)
#         h3 = inner.find("h3")
#         comparison_data["title"] = unescape(
#             h3.get_text(" ", strip=True)
#         ) if h3 else ""

#         # 3️⃣ Description paragraph (after h3)
#         desc_p = h3.find_next_sibling("p") if h3 else None
#         comparison_data["description"] = unescape(
#             desc_p.get_text(" ", strip=True)
#         ) if desc_p else ""

#         # 4️⃣ Table scraping
#         table = inner.find("table")
#         table_data = []

#         if table:
#             headers = [
#                 unescape(th.get_text(" ", strip=True))
#                 for th in table.find_all("th")
#             ]

#             for row in table.find_all("tr")[1:]:
#                 cols = row.find_all(["td", "th"])
#                 if len(cols) == len(headers):
#                     row_obj = {}
#                     for i, col in enumerate(cols):
#                         # list support inside td
#                         ul = col.find("ul")
#                         if ul:
#                             row_obj[headers[i]] = [
#                                 unescape(li.get_text(" ", strip=True))
#                                 for li in ul.find_all("li")
#                             ]
#                         else:
#                             row_obj[headers[i]] = unescape(
#                                 col.get_text(" ", strip=True)
#                             )
#                     table_data.append(row_obj)

#         comparison_data["table"] = table_data

#         # 5️⃣ Note
#         note_p = inner.find("p", string=lambda x: x and "Note" in x)
#         comparison_data["note"] = unescape(
#             note_p.get_text(" ", strip=True)
#         ) if note_p else ""

#     popular_data["mtech_comparison"] = comparison_data
#     syllabus_data = scrape_detailed_syllabus_section(soup, syllabus_data)
#     return syllabus_data

# def parse_semester_table(table):
#     semesters = {}
#     current_sem = None

#     for row in table.find_all("tr"):
#         th = row.find("th")
#         if th:
#             current_sem = th.get_text(strip=True)
#             semesters[current_sem] = []
#             continue

#         if current_sem:
#             subjects = [td.get_text(" ", strip=True) for td in row.find_all("td")]
#             subjects = [s for s in subjects if s and s != "-"]
#             if subjects:
#                 semesters[current_sem].extend(subjects)

#     return semesters

# def scrape_detailed_syllabus_section(soup, syllabus_data):

#     section = soup.find("section", id="chp_syllabus_popularexams")
#     if not section:
#         return syllabus_data

#     detailed_data = {}

#     # ---------------------------------
#     # INTRO TEXT
#     # ---------------------------------
#     intro_block = section.select_one(".wikkiContents > div")
#     intro_paragraphs = []

#     if intro_block:
#         for p in intro_block.find_all("p", recursive=False):
#             text = p.get_text(" ", strip=True)
#             if len(text) > 30:
#                 intro_paragraphs.append(text)

#     detailed_data["intro"] = intro_paragraphs

#     # ---------------------------------
#     # COURSE-WISE SYLLABUS TABLES
#     # ---------------------------------
#     course_syllabus = {}

#     headings = section.find_all("h3")
#     for h in headings:
#         course_name = h.get_text(" ", strip=True)
#         table = h.find_next("table")

#         if table:
#             course_syllabus[course_name] = parse_semester_table(table)

#     detailed_data["course_syllabus"] = course_syllabus

#     # ---------------------------------
#     # 🔥 POPULAR EXAMS
#     # ---------------------------------
#     exams = []
#     exam_cards = section.select(".uilp_exam_card")

#     for card in exam_cards:
#         exam_name = card.select_one(".exam_flnm")
#         exam_link = card.select_one(".exam_title")
#         dates = []

#         for row in card.select(".exam_impdates tr"):
#             cols = row.find_all("td")
#             if len(cols) == 2:
#                 dates.append({
#                     "date": cols[0].get_text(" ", strip=True),
#                     "event": cols[1].get_text(" ", strip=True)
#                 })

#         exams.append({
#             "name": exam_name.get_text(strip=True) if exam_name else None,
#             "url": exam_link["href"] if exam_link else None,
#             "important_dates": dates
#         })

#     detailed_data["popular_exams"] = exams

#     # ---------------------------------
#     # 🔥 FAQs
#     # ---------------------------------
#     faqs = []
#     faq_section = section.select_one(".sectional-faqs")

#     questions = faq_section.select("div.listener")
#     answers = faq_section.select("div.f61835")

#     for q_div, a_div in zip(questions, answers):
#         question = q_div.get_text(" ", strip=True).replace("Q:", "").strip()

#         ans_content = a_div.select_one(".cmsAContent")
#         if not ans_content:
#             continue

#         answer = ans_content.get_text("\n", strip=True)
#         links = [
#             {"text": a.get_text(strip=True), "url": a["href"]}
#             for a in ans_content.find_all("a", href=True)
#         ]

#         faqs.append({
#             "question": question,
#             "answer": answer,
#             "links": links
#         })


#     detailed_data["faqs"] = faqs

#     # ---------------------------------
#     syllabus_data["detailed_cse_syllabus"] = detailed_data
#     return syllabus_data



# def scrape_career_overview(driver):
#     driver.get(PCOMBA_CAREER_URL)
#     soup = BeautifulSoup(driver.page_source,"html.parser")
#     data = {
#         "title":None,
#         "meta": {},
#         "intro": [],
#         "sections": []
#     }
#     title = soup.find("div",class_="d8a6c4")
#     if title:
#         h1 = title.find("h1").text.strip()
#         data["title"]=h1
#     else:
#         pass
#     section = soup.find("section", id="chp_career_overview")
#     if not section:
#         return data

#     # ---------- META (date + author) ----------
#     updated = section.select_one(".d957ae div span")
#     author = section.select_one(".e9801a a")

#     data["meta"] = {
#         "updated_on": updated.get_text(strip=True) if updated else "",
#         "author": author.get_text(strip=True) if author else ""
#     }

#     content_block = section.find(
#         "div", id="wikkiContents_chp_career_overview_0"
#     )
#     if not content_block:
#         return data

#     container = content_block.find("div")

#     current_section = None

#     for tag in container.children:

#         if not getattr(tag, "name", None):
#             continue

#         # ---------- INTRO (before first h2) ----------
#         if tag.name == "p" and not current_section:
#             text = unescape(tag.get_text(" ", strip=True))
#             if len(text) > 30:
#                 data["intro"].append(text)
#             continue

#         # ---------- NEW SECTION ----------
#         if tag.name in ["h2", "h3"]:
#             current_section = {
#                 "title": unescape(tag.get_text(" ", strip=True)),
#                 "content": [],
#                 "tables": []
#             }
#             data["sections"].append(current_section)
#             continue

#         if not current_section:
#             continue

#         # ---------- PARAGRAPHS ----------
#         if tag.name == "p":
#             text = unescape(tag.get_text(" ", strip=True))
#             if (
#                 len(text) > 30
#                 and not text.lower().startswith("note")
#                 and "source" not in text.lower()
#             ):
#                 current_section["content"].append(text)

#         # ---------- TABLES ----------
#         if tag.name == "table":
#             table_data = []
#             headers = [
#                 unescape(th.get_text(" ", strip=True))
#                 for th in tag.find_all("th")
#             ]

#             for row in tag.find_all("tr")[1:]:
#                 cols = row.find_all(["td", "th"])
#                 if not cols:
#                     continue

#                 row_obj = {}
#                 for i, col in enumerate(cols):
#                     text = unescape(col.get_text(" ", strip=True))
#                     key = headers[i] if i < len(headers) else f"col_{i}"
#                     row_obj[key] = text

#                 table_data.append(row_obj)

#             if table_data:
#                 current_section["tables"].append(table_data)

#     return data

def scrape_mechanical_engineering_subjects(driver):

    driver.get(PCOMBA_SUB_URL)  # या आपका subjects URL
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    result = {
        "title":None,
        "metadata": {},
        "sections": []
    }
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        result["title"]=h1
    else:
        pass
    # ---------- METADATA ----------
    update_span = soup.select_one(".d957ae div span")
    result["metadata"]["last_updated"] = update_span.get_text(strip=True) if update_span else None
    
    author_div = soup.select_one(".c2675e")
    if author_div:
        result["metadata"]["author"] = {
            "name": author_div.select_one(".e9801a a").get_text(strip=True),
            "role": author_div.select_one(".cbbdad").get_text(strip=True),
            "image": author_div.select_one("img")["src"] if author_div.select_one("img") else None
        }
    
    # Overview
    overview_div = soup.select_one("#wikkiContents_chp_subjects_overview_0")
    if overview_div:
        overview_texts = []
        for p in overview_div.find_all("p"):
            if not p.find("iframe"):
                text = p.get_text(strip=True)
                if text:
                    overview_texts.append(text)
        result["metadata"]["overview"] = overview_texts
    
    # FAQ
    faqs = []
    faq_div = soup.select_one(".ab3f81")
    if faq_div:
        faq_items = faq_div.find_all(class_="html-0")
        for faq_item in faq_items:
            question = faq_item.get_text(strip=True).replace("Q:", "").strip()
            
            # Find corresponding answer
            answer_div = faq_item.find_next(class_="f61835")
            if answer_div:
                answer = answer_div.select_one(".cmsAContent")
                if answer:
                    faqs.append({
                        "question": question,
                        "answer": answer.get_text(" ", strip=True)
                    })
        
        if faqs:
            result["metadata"]["faqs"] = faqs
    
    # TOC
    toc_div = soup.select_one(".b644f8")
    if toc_div:
        toc_items = [li.get_text(strip=True) for li in toc_div.select("li")]
        result["metadata"]["table_of_contents"] = toc_items
    
    # ---------- MAIN SECTIONS ----------
    print("=" * 50)
    print("SCRAPING SUBJECTS DATA")
    print("=" * 50)
    
    # Find all h2 with class tbSec2
    all_h2_headings = soup.find_all("h2", class_="tbSec2")
    print(f"Found {len(all_h2_headings)} h2 headings")
    
    for i, h2 in enumerate(all_h2_headings):
        section_title = h2.get_text(strip=True)
        print(f"\n[{i+1}] Processing section: '{section_title}'")
        
        # Find the next wikki div
        wikki_div = find_wikki_div_after_h2(h2)
        
        if wikki_div:
            print(f"  ✓ Found wikki div: {wikki_div.get('id', 'No ID')}")
            section_content = extract_subjects_content(wikki_div)
            print(f"  ✓ Extracted {len(section_content)} content elements")
            
            if section_content:
                result["sections"].append({
                    "section_title": section_title,
                    "content": section_content
                })
        else:
            print(f"  ✗ No wikki div found")
    
    print(f"\nTotal sections added: {len(result['sections'])}")
    print("=" * 50)
    
    return result


def find_wikki_div_after_h2(h2_element):
    """Find wikki div after h2 element"""
    # Method 1: Look for next div with wikkiContents or specific pattern
    current = h2_element.next_sibling
    
    while current:
        if hasattr(current, 'name') and current.name == 'div':
            # Check if it's a wikki div
            div_id = current.get('id', '')
            div_classes = current.get('class', [])
            
            if ('wikkiContents' in div_id or 
                'wikkiContents' in str(div_classes) or
                'faqAccordian' in str(div_classes)):
                return current
        
        current = current.next_sibling
    
    # Method 2: Use find_next
    wikki_div = h2_element.find_next("div", class_="wikkiContents")
    if wikki_div:
        return wikki_div
    
    wikki_div = h2_element.find_next("div", class_="faqAccordian")
    if wikki_div:
        return wikki_div
    
    # Method 3: Look for div with specific ID pattern
    wikki_div = h2_element.find_next("div", id=lambda x: x and 'wikkiContents' in x)
    return wikki_div


def extract_subjects_content(wikki_div):
    """Extract content from subjects wikki div"""
    content = []
    
    # Get the main content div
    content_div = wikki_div.find("div")
    if not content_div:
        content_div = wikki_div
    
    # Process all elements in order
    elements = []
    
    # Function to collect all relevant elements
    def collect_all_elements(node):
        if not hasattr(node, 'name'):
            return
        
        # Check if node itself is relevant
        if node.name in ['p', 'h3', 'h4', 'table', 'ul', 'ol']:
            elements.append(node)
        
        # Process children
        if hasattr(node, 'children'):
            for child in node.children:
                collect_all_elements(child)
    
    collect_all_elements(content_div)
    
    # Process collected elements
    for element in elements:
        if element.name in ["h3", "h4"]:
            heading_text = element.get_text(strip=True)
            if heading_text:
                content.append({
                    "type": "subheading",
                    "heading": heading_text,
                    "level": "h3" if element.name == "h3" else "h4"
                })
        
        elif element.name == "p":
            # Skip if inside table or other container
            if element.find_parent('table'):
                continue
                
            text = element.get_text(" ", strip=True)
            text = ' '.join(text.split())
            
            if text and len(text) > 10:
                # Skip unwanted content
                if not any(x in str(element) for x in ['iframe', 'View more', '&nbsp;']):
                    content.append({
                        "type": "paragraph",
                        "text": text
                    })
        
        elif element.name == "table":
            table_data = extract_table_data_subjects(element)
            if table_data:
                content.append({
                    "type": "table",
                    "data": table_data
                })
        
        elif element.name in ["ul", "ol"]:
            list_items = extract_list_items(element)
            if list_items:
                content.append({
                    "type": "list",
                    "items": list_items,
                    "ordered": element.name == "ol"
                })
    
    return content


def extract_table_data_subjects(table_element):
    """Extract table data for subjects"""
    table_data = []
    
    for row in table_element.find_all("tr"):
        row_cells = []
        
        for cell in row.find_all(["th", "td"]):
            # Get cell text and clean it
            cell_text = cell.get_text(" ", strip=True)
            cell_text = ' '.join(cell_text.split())
            
            # Get links if present
            links = []
            for link in cell.find_all("a"):
                link_text = link.get_text(strip=True)
                link_href = link.get("href", "")
                if link_text and link_href:
                    links.append({
                        "text": link_text,
                        "href": link_href
                    })
            
            if cell_text:
                row_cells.append({
                    "text": cell_text,
                    "links": links if links else None
                })
            elif links:
                # If no text but has links
                row_cells.append({
                    "text": "",
                    "links": links
                })
        
        if row_cells:
            table_data.append(row_cells)
    
    return table_data if table_data else None


def extract_list_items(list_element):
    """Extract list items"""
    items = []
    
    for li in list_element.find_all("li"):
        item_text = li.get_text(" ", strip=True)
        item_text = ' '.join(item_text.split())
        
        if item_text:
            items.append(item_text)
    
    return items if items else None


def scrape_mechanical_engineering_data(driver):
    driver.get(PCOMBA_SALARY_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    result = {
        "title":None,
        "metadata": {},
        "sections": []
    }
    
    title = soup.find("div",class_="d8a6c4")
    if title:
        h1 = title.find("h1").text.strip()
        result["title"]=h1
    else:
        pass
    # ---------- METADATA ----------
    update_span = soup.select_one(".d957ae div span")
    result["metadata"]["last_updated"] = update_span.get_text(strip=True) if update_span else None
    
    author_div = soup.select_one(".c2675e")
    if author_div:
        result["metadata"]["author"] = {
            "name": author_div.select_one(".e9801a a").get_text(strip=True),
            "role": author_div.select_one(".cbbdad").get_text(strip=True),
            "image": author_div.select_one("img")["src"] if author_div.select_one("img") else None
        }
    
    overview_div = soup.select_one("#wikkiContents_chp_career_overview_0")
    if overview_div:
        overview_texts = []
        for p in overview_div.find_all("p"):
            if not p.find("iframe"):
                text = p.get_text(strip=True)
                if text:
                    overview_texts.append(text)
        result["metadata"]["overview"] = overview_texts
    
    faq_div = soup.select_one(".ab3f81")
    if faq_div:
        faq_question = faq_div.select_one(".html-0")
        faq_answer = faq_div.select_one(".f61835 .cmsAContent")
        
        if faq_question and faq_answer:
            result["metadata"]["faqs"] = [{
                "question": faq_question.get_text(strip=True).replace("Q:", "").strip(),
                "answer": faq_answer.get_text(" ", strip=True)
            }]
    
    toc_div = soup.select_one(".b644f8")
    if toc_div:
        toc_items = [li.get_text(strip=True) for li in toc_div.select("li")]
        result["metadata"]["table_of_contents"] = toc_items
    
    # ---------- MAIN CONTENT - IMPROVED VERSION ----------
    print("=" * 50)
    print("DEBUGGING IMPROVED VERSION")
    print("=" * 50)
    
    # Find all h2 with class tbSec2
    all_h2_headings = soup.find_all("h2", class_="tbSec2")
    print(f"Found {len(all_h2_headings)} h2 headings")
    
    for i, h2 in enumerate(all_h2_headings):
        section_title = h2.get_text(strip=True)
        print(f"\n[{i+1}] Processing section: '{section_title}'")
        
        # Try multiple methods to find the wikki div
        
        # Method 1: Use find_next with specific pattern
        wikki_div = None
        
        # Look through next siblings until we find a wikki div
        current = h2.next_sibling
        while current:
            if hasattr(current, 'name') and current.name == 'div':
                div_id = current.get('id', '')
                if 'wikkiContents_chp_career_' in div_id:
                    wikki_div = current
                    break
            current = current.next_sibling
        
        # Method 2: If still not found, use find_all_next
        if not wikki_div:
            next_divs = h2.find_all_next("div", id=lambda x: x and 'wikkiContents_chp_career_' in x)
            if next_divs:
                # Take the first one that comes after this h2
                for div in next_divs:
                    # Check if this div hasn't already been assigned to a previous h2
                    already_used = any(
                        sec['section_title'] == section_title or 
                        div.get('id') in [s.get('id', '') for s in result['sections']]
                        for sec in result['sections']
                    )
                    if not already_used:
                        wikki_div = div
                        break
        
        if wikki_div:
            print(f"  ✓ Found wikki div: {wikki_div.get('id')}")
            
            # Extract content
            section_content = extract_content_from_wikki(wikki_div)
            
            if section_content:
                result["sections"].append({
                    "section_title": section_title,
                    "content": section_content
                })
                print(f"  ✓ Added {len(section_content)} content elements")
            else:
                print(f"  ✗ No content extracted")
        else:
            print(f"  ✗ No wikki div found")
            
            # Debug: Show what comes after h2
            print(f"  Debug next 5 elements after h2:")
            current = h2.next_sibling
            count = 0
            while current and count < 5:
                if hasattr(current, 'name'):
                    print(f"    {count+1}. {current.name} id:{current.get('id', 'none')}")
                current = current.next_sibling
                count += 1
    
    print(f"\nTotal sections added: {len(result['sections'])}")
    print("=" * 50)
    
    # If still no sections, use alternative approach
    if len(result["sections"]) == 0:
        print("\nTrying ALTERNATIVE APPROACH...")
        result["sections"] = extract_sections_alternative(soup)
        print(f"Alternative approach found {len(result['sections'])} sections")
    
    return result


def extract_content_from_wikki(wikki_div):
    """Extract content from wikki div"""
    content = []
    
    # Find the main content div inside wikki
    content_div = wikki_div.find("div")
    if not content_div:
        content_div = wikki_div
    
    # Get all elements we care about
    elements = []
    
    # Process all children recursively
    def collect_elements(node):
        if not hasattr(node, 'name'):
            return
        
        if node.name in ['p', 'h3', 'table']:
            elements.append(node)
        elif hasattr(node, 'children'):
            for child in node.children:
                collect_elements(child)
    
    collect_elements(content_div)
    
    # Process elements in order
    for element in elements:
        if element.name == "h3":
            heading = element.get_text(strip=True)
            if heading:
                content.append({
                    "type": "subheading",
                    "heading": heading
                })
        
        elif element.name == "p":
            # Skip if inside a table
            if element.find_parent('table'):
                continue
                
            text = element.get_text(" ", strip=True)
            text = ' '.join(text.split())
            
            if text and len(text) > 10:
                # Skip iframes and empty content
                if "iframe" not in str(element) and "View more" not in text:
                    content.append({
                        "type": "paragraph",
                        "text": text
                    })
        
        elif element.name == "table":
            table_data = []
            for tr in element.find_all("tr"):
                row = []
                for cell in tr.find_all(["th", "td"]):
                    cell_text = cell.get_text(" ", strip=True)
                    cell_text = ' '.join(cell_text.split())
                    if cell_text:
                        row.append(cell_text)
                if row:
                    table_data.append(row)
            
            if table_data:
                content.append({
                    "type": "table",
                    "data": table_data
                })
    
    return content


def extract_sections_alternative(soup):
    """Alternative approach to extract sections"""
    sections = []
    
    # Find all wikki divs
    wikki_divs = soup.find_all("div", id=lambda x: x and 'wikkiContents_chp_career_' in x)
    print(f"Found {len(wikki_divs)} wikki divs")
    
    for wikki_div in wikki_divs:
        # Find the closest h2 before this div
        h2 = wikki_div.find_previous("h2", class_="tbSec2")
        
        if h2:
            section_title = h2.get_text(strip=True)
            print(f"  Processing: '{section_title}'")
            
            # Extract content
            section_content = extract_content_from_wikki(wikki_div)
            
            if section_content:
                sections.append({
                    "section_title": section_title,
                    "content": section_content
                })
    
    return sections

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


# def scrape_fees_overview_json(driver, timeout=30):
#     driver.get(PCOMBA_FEES_URL)
#     soup = BeautifulSoup(driver.page_source,"html.parser")

#     result = {
#         "title":None,
#         "updated_on": None,
#         "author": None,
#         "author_profile_url":None,
#         "author_designation":None,
#         "content": []
#     }
#     title = soup.find("div",class_="d8a6c4")
#     if title:
#         h1 = title.find("h1").text.strip()
#         result["title"]=h1
#     else:
#         pass

#     try:
#         wait = WebDriverWait(driver, timeout)
#         wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

#         section = wait.until(
#             EC.presence_of_element_located((By.ID, "chp_fees_overview"))
#         )

#         # -------- meta --------
#         # ---------- Updated On ----------
#         try:
#             updated_on = section.find_element(
#                 By.XPATH, ".//div[contains(text(),'Updated on')]/span"
#             ).text.strip()
#             result["last_updated"] = updated_on
#         except:
#             result["last_updated"] = None


#         # ---------- Author Details ----------
#         try:
#             author_block = section.find_element(By.CSS_SELECTOR, ".c2675e")

#             author_link = author_block.find_element(By.TAG_NAME, "a")

#             result["author"] = author_link.text.strip()
#             result["author_profile_url"] = author_link.get_attribute("href")

#             try:
#                 result["author_designation"] = author_block.find_element(
#                     By.CSS_SELECTOR, ".cbbdad"
#                 ).text.strip()
#             except:
#                 result["author_designation"] = None

#         except:
#             result["author"] = None
#             result["author_profile_url"] = None
#             result["author_designation"] = None


#         # -------- main content --------
#         content_root = section.find_element(By.CSS_SELECTOR, ".wikkiContents")

#         elements = content_root.find_elements(
#             By.XPATH, "./div/*"
#         )

#         for el in elements:
#             tag = el.tag_name.lower()
#             text = el.text.strip()

#             if not text:
#                 continue

#             # ---- headings ----
#             if tag in ["h2", "h3"]:
#                 result["content"].append({
#                     "type": "heading",
#                     "level": tag,
#                     "text": text
#                 })

#             # ---- paragraphs ----
#             elif tag == "p":
#                 result["content"].append({
#                     "type": "paragraph",
#                     "text": text
#                 })

#             # ---- tables ----
#             elif tag == "table":
#                 rows = el.find_elements(By.TAG_NAME, "tr")
#                 table_data = []

#                 for row in rows[1:]:
#                     cols = row.find_elements(By.TAG_NAME, "td")
#                     if len(cols) >= 2:
#                         table_data.append({
#                             "college": cols[0].text.strip(),
#                             "fees": cols[1].text.strip()
#                         })

#                 if table_data:
#                     result["content"].append({
#                         "type": "table",
#                         "rows": table_data
#                     })

#         return result

#     except TimeoutException:
    
#         return None
    
# def scrape_blog_data(driver):
#     driver.get(PCOMBA_JEEVSBITSAK_URL)
#     soup = BeautifulSoup(driver.page_source, "html.parser")

#     result = {
#         "title":None,
#         "article_info": {},
#         "intro": [],
#         "sections": []
#     }
#     title = soup.find("div",class_="flx-box mA")
#     if title:
#         h1 = title.find("h1").text.strip()
#         result["title"]=h1
#     else:
#         pass
#     # ---------------- METADATA ----------------
#     author_section = soup.select_one(".adp_user")

#     if author_section:
#         result["article_info"]["author"] = {
#             "name": author_section.select_one(".adp_usr_dtls a").get_text(strip=True),
#             "role": author_section.select_one(".user_expert_level").get_text(strip=True),
#             "image": author_section.select_one("img")["src"]
#         }

#     result["article_info"]["updated"] = soup.select_one(
#         ".blogdata_user span"
#     ).get_text(strip=True)

#     result["article_info"]["summary"] = soup.select_one(
#         "#blogSummary"
#     ).get_text(strip=True)

#     # ---------------- MAIN CONTENT ----------------
#     content_div = soup.select_one("#blogId-53799")

#     if not content_div:
#         return result

#     # Remove junk
#     for bad in content_div.select(".openVideoContainer, .b644f8, script, style"):
#         bad.decompose()

#     wikki_sections = content_div.select(".wikkiContents")

#     current_section = None

#     for wikki in wikki_sections:

#         for element in wikki.find_all(
#             ["h2","h3","p","ul","ol","table","img","a"], 
#             recursive=True
#         ):

#             # -------- HEADINGS --------
#             if element.name in ["h2","h3"]:

#                 if current_section:
#                     result["sections"].append(current_section)

#                 current_section = {
#                     "heading": element.get_text(strip=True),
#                     "content": []
#                 }

#             # -------- PARAGRAPHS --------
#             elif element.name == "p":
#                 text = element.get_text(" ", strip=True)

#                 if not text:
#                     continue

#                 item = {
                   
#                     "content": text
#                 }

#                 if current_section:
#                     current_section["content"].append(item)
#                 else:
#                     result["intro"].append(item)

#             # -------- LISTS --------
#             elif element.name in ["ul","ol"]:
#                 items = [
#                     li.get_text(" ", strip=True)
#                     for li in element.find_all("li")
#                 ]

#                 if items:
#                     data = {
                       
#                         "items": items
#                     }

#                     if current_section:
#                         current_section["content"].append(data)

#             # -------- TABLES --------
#             elif element.name == "table":
#                 table_data = []

#                 for tr in element.find_all("tr"):
#                     row = []
#                     for cell in tr.find_all(["th","td"]):
#                         row.append(cell.get_text(" ", strip=True))

#                     if row:
#                         table_data.append(row)

#                 if table_data:
#                     current_section["content"].append({
                        
#                         "data": table_data
#                     })

#             # -------- IMAGES --------
#             elif element.name == "img":
#                 src = element.get("src")

#                 if src:
#                     img = {
                        
#                         "src": src,
#                         "alt": element.get("alt")
#                     }

#                     if current_section:
#                         current_section["content"].append(img)

#             # -------- LINKS (Also Read etc) --------
#             elif element.name == "a":
#                 href = element.get("href")
#                 text = element.get_text(strip=True)

#                 if href and text:
#                     link = {
                       
#                         "text": text,
#                         "url": href
#                     }

#                     if current_section:
#                         current_section["content"].append(link)

#     if current_section:
#         result["sections"].append(current_section)

#     return result

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
              "Machenical Engineering":{
                "overviews":extract_overview_data(driver),
                "course":extract_courses__data(driver),
                # "syllabus":scrape_syllabus_section(driver),
                # "career":scrape_career_overview(driver),
                "salary":scrape_mechanical_engineering_data(driver),
                "subject":scrape_mechanical_engineering_subjects(driver),
                "addmision":scrape_admission_overview(driver),
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

