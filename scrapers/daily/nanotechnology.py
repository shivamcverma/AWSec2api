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

PCOMBA_O_URL="https://www.shiksha.com/engineering/nanotechnology-chp"
PCOMBA_C_URL="https://www.shiksha.com/engineering/nanotechnology-syllabus-chp"
PCOMBA_S_URL="https://www.shiksha.com/engineering/nanotechnology-syllabus-chp"
PCOMBA_SUB_URL="https://www.shiksha.com/engineering/electronics-engineering-subjects-chp"
PCOMBA_CAREER_URL = "https://www.shiksha.com/engineering/electronics-engineering-career-chp"
PCOMBA_ADDMISSION_URL="https://www.shiksha.com/engineering/nanotechnology-admission-chp"
PCOMBA_EXAM_URL = "https://www.shiksha.com/articles/engineering-entrance-exams-in-india-blogId-5645"
PCOMBA_FEES_URL = "https://www.shiksha.com/engineering/computer-science-engineering-fees-chp"
PCOMBA_JEEVSBITSAK_URL = "https://www.shiksha.com/engineering/articles/jee-main-vs-bitsat-exam-difficulty-level-pattern-and-syllabus-blogId-53799"
PCOMBA_Q_URL = "https://www.shiksha.com/tags/computer-science-engineering-tdp-391267"
PCOMBA_QD_URL="https://www.shiksha.com/tags/computer-science-engineering-tdp-391267?type=discussion"


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


def extract_syllabus__data(driver):
    driver.get(PCOMBA_S_URL)
    WebDriverWait(driver, 15)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    section = soup.find("section", id="chp_syllabus_overview")
    if not section:
        return {}

    data = {}

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
    # MAIN SYLLABUS CONTENT
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

    return data



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

def extract_EXAM_data(driver):
   
    driver.get(PCOMBA_EXAM_URL)
    time.sleep(5)
    
    # Wait for main content to load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for some seconds for JS to load
    wait = WebDriverWait(driver, 15)

    # Now get the soup
    soup = BeautifulSoup(driver.page_source, "html.parser")
 
    
    data = {
        "title": "",
        "author": {
            "name":"",
        },
    "updated_on": "",
        "updated_on": "",
        "summary": "",
        "content": {"blocks": []},
        "faqs": [],
        "poll": {},
        "recommended_exams": [],
        "videos": []
    }
    
    # ==============================
    # EXTRACT AUTHOR INFO
    # ==============================
    try:
        wait = WebDriverWait(driver, 20)  # 20 sec
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.adp_blog")))
    except:
        print("Author block not visible or timeout!")

    author_block = soup.find("div", class_="adp_blog")
    if author_block:
        user_tag = author_block.find("div", class_="adp_usr_dtls")
        if user_tag:
            author_link = user_tag.find("a")
            if author_link:
                data["author"]["name"] = author_link.text.strip()
                data["author"]["profile_url"] = author_link.get("href", "").strip()
                author_img = author_link.find("img")
                if author_img:
                    data["author"]["image"] = author_img.get("src", "").strip()
            role_elem = user_tag.find("div", class_="user_expert_level")
            if role_elem:
                data["author"]["role"] = role_elem.get_text(strip=True)


        # Updated date
        blogdata_user = author_block.find("div", class_="blogdata_user")
        if blogdata_user:
            updated_span = blogdata_user.find("span")
            if updated_span:
                updated_text = updated_span.get_text(strip=True)
                data["updated_on"] = updated_text.split("Updated on")[-1].strip()

    
    # ==============================
    # EXTRACT SUMMARY
    # ==============================
    summary_div = soup.find("div", class_="blogSummary")
    if summary_div:
        data["summary"] = summary_div.get_text(strip=True)
    
    # ==============================
    # EXTRACT MAIN CONTENT
    # ==============================
    main_content = soup.find("div", id=lambda x: x and x.startswith("blogId-"))
    if main_content:
        data["content"] = extract_rich_content_shiksha(main_content)
    
    # ==============================
    # EXTRACT FAQS
    # ==============================
    faq_section = soup.find("div", class_="sectional-faqs")
    if faq_section:
        data["faqs"] = extract_faqs(faq_section)
    
    # ==============================
    # EXTRACT POLL
    # ==============================
    poll_container = soup.find("div", id="poll-container")
    if poll_container:
        data["poll"] = extract_poll_data(poll_container)
    
    # ==============================
    # EXTRACT RECOMMENDED EXAMS
    # ==============================
    slider_container = soup.find("div", id="ADP_Exam_recoWidget_undefined")
    if slider_container:
        data["recommended_exams"] = extract_recommended_exams(slider_container)
    
    # ==============================
    # EXTRACT VIDEOS
    # ==============================
    videos_container = soup.find("div", id="reelsWidget")
    if videos_container:
        data["videos"] = extract_videos(videos_container)
    
    return data

def extract_rich_content_shiksha(container):
    """Extract rich content from Shiksha blog format"""
    if not container:
        return {"blocks": []}
    
    content = {"blocks": []}
    
    # Get all wikkiContents sections
    content_sections = container.find_all("div", class_="wikkiContents")
    
    for section in content_sections:
        # Process each section's content
        for element in section.find_all(recursive=False):
            process_element(element, content)
    
    return content

def process_element(element, content):
    """Process individual HTML elements"""
    
    # HEADINGS (h2, h3, h4)
    if element.name in ["h2", "h3", "h4"]:
        content["blocks"].append({
            "type": "heading",
            "level": element.name,
            "value": element.get_text(" ", strip=True)
        })
        return
    
    # PARAGRAPHS
    elif element.name == "p":
        # Skip if inside table
        if element.find_parent("table"):
            return
        
        text = element.get_text(" ", strip=True)
        if text:
            content["blocks"].append({
                "type": "paragraph",
                "value": text
            })
        
        # Extract links from paragraph
        links = element.find_all("a", href=True)
        for link in links:
            if not link.find_parent("table"):
                content["blocks"].append({
                    "type": "link",
                    "value": {
                        "text": link.get_text(" ", strip=True),
                        "url": link["href"]
                    }
                })
        return
    
    # TABLES
    elif element.name == "table":
        table_data = []
        for row in element.find_all("tr"):
            cols = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all(["th", "td"])
            ]
            if cols:
                table_data.append(cols)
        
        if table_data:
            content["blocks"].append({
                "type": "table",
                "value": table_data
            })
        return
    
    # IMAGES
    elif element.name == "img" or element.find("img"):
        img = element.find("img") if element.name != "img" else element
        if img and img.get("src"):
            content["blocks"].append({
                "type": "image",
                "value": img["src"],
                "alt": img.get("alt", ""),
                "width": img.get("width"),
                "height": img.get("height")
            })
        return
    
    # IFRAMES/VIDEOS
    elif element.name == "iframe" or element.find("iframe"):
        iframe = element.find("iframe") if element.name != "iframe" else element
        if iframe and iframe.get("src"):
            content["blocks"].append({
                "type": "iframe",
                "value": iframe["src"]
            })
        return
    
    # DIVS with content
    elif element.name == "div":
        # Check for photo widgets
        if "photo-widget-full" in element.get("class", []):
            img = element.find("img")
            if img and img.get("src"):
                content["blocks"].append({
                    "type": "image",
                    "value": img["src"],
                    "alt": img.get("alt", ""),
                    "caption": element.get_text(" ", strip=True)
                })
        else:
            # Process child elements recursively
            for child in element.find_all(recursive=False):
                process_element(child, content)

def extract_faqs(faq_section):
    """Extract FAQ questions and answers"""
    faqs = []
    
    faq_items = faq_section.find_all("div", class_="html-0")
    for faq_item in faq_items:
        question_elem = faq_item.find("strong")
        if question_elem:
            question = question_elem.get_text(strip=True).replace("Q: ", "")
            
            # Find the answer in next sibling
            next_sibling = faq_item.find_next_sibling("div", class_="f61835")
            answer = ""
            if next_sibling:
                answer_div = next_sibling.find("div", class_="cmsAContent")
                if answer_div:
                    answer = answer_div.get_text(" ", strip=True)
            
            faqs.append({
                "question": question,
                "answer": answer
            })
    
    return faqs

def extract_poll_data(poll_container):
    """Extract poll data"""
    poll = {
        "question": "",
        "options": [],
        "total_votes": "",
        "comments": 0,
        "is_live": False
    }
    
    # Extract question
    question_div = poll_container.find("div", class_="poll-question")
    if question_div:
        poll["question"] = question_div.get_text(strip=True)
    
    # Extract options
    options_div = poll_container.find("div", class_="poll-options")
    if options_div:
        options = options_div.find_all("div", class_="poll-option")
        for option in options:
            label = option.find("label")
            if label:
                poll["options"].append(label.get_text(strip=True))
    
    # Extract poll info
    info_div = poll_container.find("div", class_="poll-info")
    if info_div:
        # Total votes
        votes_span = info_div.find("span", class_="poll-info-text")
        if votes_span:
            poll["total_votes"] = votes_span.get_text(strip=True)
        
        # Comments count
        comment_div = info_div.find("div", class_="comment-container")
        if comment_div:
            comment_text = comment_div.get_text(strip=True)
            poll["comments"] = int(''.join(filter(str.isdigit, comment_text)) or 0)
        
        # Check if live
        live_indicator = info_div.find("div", class_="liveCapsule")
        if live_indicator:
            poll["is_live"] = True
    
    return poll

def extract_recommended_exams(slider_container):
    """Extract recommended exams data"""
    exams = []
    
    exam_sliders = slider_container.find_all("div", class_="examSlider")
    for slider in exam_sliders:
        exam = {
            "name": "",
            "dates": [],
            "links": {},
            "is_live": False
        }
        
        # Exam name
        name_h2 = slider.find("h2", class_="a52fbf")
        if name_h2:
            exam["name"] = name_h2.get_text(strip=True)
        
        # Check if live
        live_capsule = slider.find("div", class_="liveCapsule")
        if live_capsule:
            exam["is_live"] = True
        
        # Exam dates
        date_div = slider.find("div", class_="eb6a61")
        if date_div:
            strong_elem = date_div.find("strong")
            date_elem = date_div.find("p", class_="a8bb55")
            if strong_elem and date_elem:
                exam["dates"].append({
                    "event": strong_elem.get_text(strip=True),
                    "date": date_elem.get_text(strip=True)
                })
        
        # Links
        links_ul = slider.find("ul", class_="bb1431")
        if links_ul:
            links = links_ul.find_all("a")
            for link in links:
                link_text = link.get_text(strip=True)
                link_url = link.get("href")
                exam["links"][link_text.lower().replace(" ", "_")] = link_url
        
        exams.append(exam)
    
    return exams

def extract_videos(videos_container):
    """Extract video data"""
    videos = []
    
    video_items = videos_container.find_all("li", class_="thumbnailListener")
    for item in video_items:
        video = {
            "title": "",
            "thumbnail": "",
            "url": "",
            "duration": ""
        }
        
        # Extract YouTube thumbnail
        img = item.find("img")
        if img and img.get("src"):
            video["thumbnail"] = img["src"]
        
        # Extract title
        title_div = item.find("div", class_="ada2b9")
        if title_div:
            video["title"] = title_div.get_text(strip=True)
        
        # Extract iframe URL
        iframe = item.find("iframe")
        if iframe and iframe.get("src"):
            video["url"] = iframe["src"]
        
        # Extract duration
        duration_div = item.find("div", class_="e6852b")
        if duration_div:
            video["duration"] = duration_div.get_text(strip=True)
        
        videos.append(video)
    
    return videos

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
              "Nanotechnology":{
                "overviews":extract_overview_data(driver),
                # "course":extract_courses__data(driver),
                # "subject":scrape_mechanical_engineering_subjects(driver),
                "syllabus":extract_syllabus__data(driver),
                # "career":scrape_career_overview(driver),
                "addmision":scrape_admission_overview(driver),
                "Entrance exam":extract_EXAM_data(driver)
                # "fees":scrape_fees_overview_json(driver, timeout=30),
                # "JEEVSBITSAK":scrape_blog_data(driver),
                # "QA":{
                #  "QA_ALL":scrape_shiksha_qa(driver),
                #  "QA_D":scrape_tag_cta_D_block(driver),
                # },
                
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

