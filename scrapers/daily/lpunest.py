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

URLS = {
    "overviews":"https://www.shiksha.com/mba/lpu-nest-exam",
    "MBA":"https://www.shiksha.com/engineering/lpu-nest-exam/mba-1071",
    "Bdes_Bsc":"https://www.shiksha.com/engineering/lpu-nest-exam/bdes-bsc-design-1073",
    "LLB":"https://www.shiksha.com/engineering/lpu-nest-exam/llb-and-integrated-law-programmes-1075",
    "LLM":"https://www.shiksha.com/engineering/lpu-nest-exam/llm-1077",
    "BHMCT":"https://www.shiksha.com/engineering/lpu-nest-exam/bhmct-bsc-1079",
    "Agriculture":"https://www.shiksha.com/engineering/lpu-nest-exam/agriculture-1081",
    "Bpharma":"https://www.shiksha.com/engineering/lpu-nest-exam/bpharma-bpt-bsc-medical-lab-technology-1083",
    "Slot_booking":"https://www.shiksha.com/engineering/lpu-nest-exam-slot-booking",
    "result":"https://www.shiksha.com/mba/lpu-nest-exam-results",
    "cut_off":"https://www.shiksha.com/mba/lpu-nest-exam-cutoff",
    "app_form":"https://www.shiksha.com/mba/lpu-nest-exam-application-form",
    "ans_key":"https://www.shiksha.com/mba/lpu-nest-exam-answer-key",
    "counselling":"https://www.shiksha.com/mba/lpu-nest-exam-counselling",
    "analysis":"https://www.shiksha.com/mba/lpu-nest-exam-analysis",
    "question_paper":"https://www.shiksha.com/mba/lpu-nest-exam-question-papers",
    "admit_card":"https://www.shiksha.com/mba/lpu-nest-exam-admit-card",
    "dates":"https://www.shiksha.com/mba/lpu-nest-exam-dates",
    "mock_test":"https://www.shiksha.com/mba/lpu-nest-exam-mocktest",
    "registration":"https://www.shiksha.com/mba/lpu-nest-exam-registration",
    "syllabus":"https://www.shiksha.com/mba/lpu-nest-exam-syllabus",
    "pattern":"https://www.shiksha.com/mba/lpu-nest-exam-pattern",
    "preparation":"https://www.shiksha.com/mba/lpu-nest-exam-preparation",
    "college":"https://www.shiksha.com/mba/lpu-nest-exam-colleges",
    "books":"https://www.shiksha.com/mba/lpu-nest-exam-books",
    "notification":"https://www.shiksha.com/mba/lpu-nest-exam-notification",
    "center":"https://www.shiksha.com/mba/lpu-nest-exam-centre",
    "news":"https://www.shiksha.com/mba/lpu-nest-exam-news",
    "accepting_college":"https://www.shiksha.com/mba/colleges/mba-colleges-accepting-cat-india?sby=popularity",
    "mba_with_low_fees":"https://www.shiksha.com/mba/articles/mba-colleges-in-india-with-low-fees-blogId-23533",
                   
}


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

def extract_cat_exam_data(driver, URLS):
    driver.get(URLS["overviews"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_rich_content(container):

    if not container:
        return {"blocks": []}

    content = {"blocks": []}

    elements = container.find_all(
        ["h2", "h3", "h4", "p", "ul", "table", "iframe"],
        recursive=True
    )

    for element in elements:

        # HEADINGS
        if element.name in ["h2", "h3", "h4"]:
            text = element.get_text(" ", strip=True)
            if text:
                content["blocks"].append({
                    "type": "heading",
                    "value": text
                })

        # PARAGRAPH
        elif element.name == "p":
            if element.find_parent("table"):
                continue
            text = element.get_text(" ", strip=True)
            if text:
                content["blocks"].append({
                    "type": "paragraph",
                    "value": text
                })

        # LIST
        elif element.name == "ul":
            items = [
                li.get_text(" ", strip=True)
                for li in element.find_all("li", recursive=False)
            ]
            if items:
                content["blocks"].append({
                    "type": "list",
                    "value": items
                })

        # TABLE
        elif element.name == "table":
            table_data = []
            for row in element.find_all("tr"):
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

        # IFRAME
        elif element.name == "iframe":
            src = element.get("src") or element.get("data-original")
            if src:
                content["blocks"].append({
                    "type": "iframe",
                    "value": src
                })

    return content

def extract_faqs(soup):

    faqs = []
    question_blocks = soup.find_all("strong", class_="flx-box")

    for q in question_blocks:
        question = q.get_text(" ", strip=True).replace("Q:", "").strip()

        answer_wrapper = q.find_parent().find_next_sibling("div")
        if not answer_wrapper:
            continue

        answer_div = answer_wrapper.find("div", class_="facb5f")
        if not answer_div:
            continue

        answer = answer_div.get_text(" ", strip=True).replace("A:", "").strip()

        faqs.append({
            "question": question,
            "answer": answer
        })

    return faqs

def extract_polls(soup):

    polls = []
    poll_containers = soup.find_all("div", class_="poll-container")

    for poll in poll_containers:
        question_div = poll.find("div", class_="poll-question")
        options = poll.find_all("div", class_="poll-option")
        votes_span = poll.find("span", string=lambda x: x and "votes" in x)

        if not question_div:
            continue

        poll_data = {
            "question": question_div.get_text(strip=True),
            "options": [
                opt.get_text(" ", strip=True)
                for opt in options
            ],
            "votes": votes_span.get_text(strip=True) if votes_span else None
        }

        polls.append(poll_data)

    return polls

def extract_result_data(driver, URLS):
    driver.get(URLS["result"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_cut_off_data(driver, URLS):
    driver.get(URLS["cut_off"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_sel_proccess_data(driver, URLS):
    driver.get(URLS["app_form"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_answerkey_data(driver, URLS):
    driver.get(URLS["ans_key"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_Counselling_data(driver, URLS):
    driver.get(URLS["counselling"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_Analysis_data(driver, URLS):
    driver.get(URLS["analysis"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_question_paper_data(driver, URLS):
    driver.get(URLS["question_paper"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_admit_card_data(driver, URLS):
    driver.get(URLS["admit_card"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_dates_data(driver, URLS):
    driver.get(URLS["dates"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_mock_test_data(driver, URLS):
    driver.get(URLS["mock_test"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_registration_data(driver, URLS):
    driver.get(URLS["registration"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_syllabus_data(driver, URLS):
    driver.get(URLS["syllabus"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_pattern_data(driver, URLS):
    driver.get(URLS["pattern"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_preparation_data(driver, URLS):
    driver.get(URLS["preparation"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_books_data(driver, URLS):
    driver.get(URLS["books"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_notification_data(driver, URLS):
    driver.get(URLS["notification"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_center_data(driver, URLS):
    driver.get(URLS["center"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_news_data(driver, URLS):
    driver.get(URLS["news"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_barch_data(driver, URLS):
    driver.get(URLS["Slot_booking"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data

def extract_mba_data(driver, URLS):
    driver.get(URLS["MBA"])

    # Wait until page loads
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
    except:
        pass

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
def extract_Bdes_Bsc_data(driver, URLS):
    driver.get(URLS["Bdes_Bsc"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
def extract_LLB_data(driver, URLS):
    driver.get(URLS["LLB"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
def extract_LLM_data(driver, URLS):
    driver.get(URLS["LLM"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
def extract_BHMCT_data(driver, URLS):
    driver.get(URLS["BHMCT"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
def extract_Agriculture_data(driver, URLS):
    driver.get(URLS["Agriculture"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
def extract_Bpharma_data(driver, URLS):
    driver.get(URLS["Bpharma"])

    # Wait until page loads
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    # Scroll to bottom (for lazy loading content)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # =====================================
    # TITLE
    # =====================================
    h1 = soup.find("h1")
    data["title"] = h1.get_text(strip=True) if h1 else None

    # =====================================
    # UPDATED DATE
    # =====================================
    updated_span = soup.find("span", string=lambda x: x and "Updated" in x)
    data["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

    # =====================================
    # AUTHOR INFO
    # =====================================
    author_data = {}
    author_block = soup.find("div", class_="ppBox")

    if author_block:
        author_link = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("p", class_="ePPDetail")

        author_data = {
            "name": author_link.get_text(strip=True) if author_link else None,
            "profile_url": author_link["href"] if author_link else None,
            "role": role.get_text(" ", strip=True) if role else None,
            "image": img["src"] if img else None
        }

    data["author"] = author_data

    # =====================================
    # ALL CONTENT SECTIONS
    # =====================================
    sections = soup.find_all("div", class_="sectionalWrapperClass")
    all_sections = []

    for sec in sections:
        content_blocks = extract_rich_content(sec)
        if content_blocks["blocks"]:
            all_sections.append(content_blocks)

    data["content_sections"] = all_sections

    # =====================================
    # FAQ SECTION
    # =====================================
    data["faqs"] = extract_faqs(soup)

    # =====================================
    # POLL SECTION
    # =====================================
    data["polls"] = extract_polls(soup)

    return data
    
def scrape_mba_colleges():
    driver = create_driver()

      

    try:
       data = {
                "lpu-nest":{
                    "overviews":extract_cat_exam_data(driver, URLS),
                    "MBA":extract_mba_data(driver, URLS),
                    "Bdes_Bsc":extract_Bdes_Bsc_data(driver, URLS),
                    "LLB":extract_LLB_data(driver, URLS),
                    "LLM":extract_LLM_data(driver, URLS),
                    "BHMCT":extract_BHMCT_data(driver, URLS),
                    "Agriculture":extract_Agriculture_data(driver, URLS),
                    "Bpharma":extract_Bpharma_data(driver, URLS),
                    "Slot_booking":extract_barch_data(driver, URLS),
                    "result":extract_result_data(driver, URLS),      
                    "Application_Form":extract_sel_proccess_data(driver, URLS),
                    # "CUT_OFF":extract_cut_off_data(driver, URLS),
                    # "answer_key":extract_answerkey_data(driver, URLS),
                    "counselling":extract_Counselling_data(driver, URLS),
                    # "analysis":extract_Analysis_data(driver, URLS),
                    "question_paper": extract_question_paper_data(driver, URLS),
                    "admit_card":extract_admit_card_data(driver, URLS),
                    "dates":extract_dates_data(driver, URLS),
                    # "mock_text":extract_mock_test_data(driver, URLS),
                    # "registion":extract_registration_data(driver, URLS),
                    "syllabus":extract_syllabus_data(driver, URLS),
                    "pattern":extract_pattern_data(driver, URLS),
                    # "preparation":extract_preparation_data(driver, URLS),
                    # "books":extract_books_data(driver, URLS),
                    # "college":extract_college_data(driver, URLS),
                    # "notification":extract_notification_data(driver, URLS),
                    "center":extract_center_data(driver, URLS),
                    "news":extract_news_data(driver, URLS),
                    # "accepting_college":{
                    #     "overview":scrape_accepting_college(driver, URLS),
                    #     "mba_with_low_fees":scrape_with_low_fees(driver, URLS),
                    # }
           }
       }

    finally:
        driver.quit()
    
    return data



import os

TEMP_FILE = "lpunest.tmp.json"
FINAL_FILE = "lpunest.json"

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
