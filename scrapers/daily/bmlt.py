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

PCOMBA_O_URL="https://www.shiksha.com/bmlt-bachelor-in-medical-laboratory-technology-chp"
PCOMBA_C_URL="https://www.shiksha.com/bmlt-bachelor-in-medical-laboratory-technology-courses-chp"
PCOMBA_MBA_SYLLABUS_URL = "https://www.shiksha.com/bmlt-bachelor-in-medical-laboratory-technology-syllabus-chp"
# PCOMBA_SUB_URL = "https://www.shiksha.com/md-doctor-of-medicine-subjects-chp"
# PCOMBA_MBA_CAREER_URL = "https://www.shiksha.com/md-doctor-of-medicine-career-chp"
PCOMBA_MBA_ADDMISSION_2026_URL = "https://www.shiksha.com/bmlt-bachelor-in-medical-laboratory-technology-admission-chp"
# PCOMBA_MBA_FEES_URL = "https://www.shiksha.com/mbbs-fees-chp"
# PCOMBA_COMP_URL = "https://www.shiksha.com/md-doctor-of-medicine-comparison-chp"
# MD_VS_MBBS = "https://www.shiksha.com/medicine-health-sciences/medicine/articles/md-vs-mbbs-differences-eligibility-admission-jobs-salary-2023-blogId-132969"
# AIIMS_IN_INDIA = "https://www.shiksha.com/medicine-health-sciences/articles/aiims-in-india-blogId-23925"
# MBBS_ALTERNATIVE = "https://www.shiksha.com/medicine-health-sciences/articles/alternative-courses-for-mbbs-know-eligibility-fees-and-package-in-lakh-blogId-169499"
# NEET_UG_2024 = "https://www.shiksha.com/medicine-health-sciences/neet-exam"
P_COLLEGE = "https://www.shiksha.com/medicine-health-sciences/colleges/bmlt-colleges-india?sby=popularity&rf=filters"
QA = "https://www.shiksha.com/tags/bmlt-tdp-699035"
QAD = "https://www.shiksha.com/tags/bmlt-tdp-699035?type=discussion"

def create_driver():
    options = Options()

    # Mandatory for GitHub Actions
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # # Optional but good
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    #     "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    # )

    # # Important for Ubuntu runner
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



def extract_course_data(driver):
    driver.get(PCOMBA_O_URL)
    time.sleep(5)
    wait = WebDriverWait(driver, 15)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}
    
    # =====================================================
    # BASIC COURSE INFORMATION
    # =====================================================
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = h1.text.strip() if h1 else None
    
    # Updated date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = span.text.strip() if span else None
    
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
    # OVERVIEW SECTION (chp_section_overview)
    # =====================================================
    overview_section = soup.find("section", id="chp_section_overview")
    
    if overview_section:
        overview_div = overview_section.find("div", id="wikkiContents_chp_section_overview_0")
        
        if overview_div:
            # Description paragraphs
            paragraphs = []
            for p in overview_div.find_all("p")[:6]:
                text = p.get_text(" ", strip=True)
                if text and len(text) > 10:  # Reduced length requirement
                    paragraphs.append(text)
            
            # Important links
            links = []
            for a in overview_div.find_all("a", href=True):
                links.append({
                    "title": a.get_text(strip=True),
                    "url": a["href"]
                })
            
            # Course details table
            highlight_rows = []
            for table in overview_div.find_all("table"):
                for row in table.find_all("tr")[1:]:  # Skip header row
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 2:
                        highlight_rows.append({
                            "Particular": cols[0].get_text(" ", strip=True),
                            "Details": cols[1].get_text(" ", strip=True)
                        })
            
            # FAQs from overview section
            overview_faqs = []
            faq_container = overview_section.find("div", id="sectional-faqs-0")
            if faq_container:
                faq_questions = faq_container.find_all("div", class_="html-0")
                for q in faq_questions:
                    question_elem = q.find("strong", class_="flx-box")
                    if question_elem:
                        question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                        
                        answer_div = q.find_next("div", class_="_16f53f")
                        if answer_div:
                            answer = " ".join(
                                p.get_text(" ", strip=True)
                                for p in answer_div.find_all("p")
                                if p.get_text(strip=True)
                            )
                            
                            overview_faqs.append({
                                "question": question,
                                "answer": answer
                            })
            
            data["overview"] = {
                "description": paragraphs,
                "important_links": links,
                "highlights": {
                    "columns": ["Particular", "Details"],
                    "rows": highlight_rows
                },
                "faqs": overview_faqs
            }
    
    # =====================================================
    # ELIGIBILITY SECTION (chp_section_eligibility)
    # =====================================================
    eligibility_section = soup.find("section", id="chp_section_eligibility")
    
    if eligibility_section:
        # Section title
        section_title = eligibility_section.find("h2", class_="tbSec2")
        section_name = section_title.text.strip() if section_title else "Eligibility"
        
        # Main content
        eligibility_div = eligibility_section.find("div", id="wikkiContents_chp_section_eligibility_1")
        
        # Description paragraphs
        description = []
        if eligibility_div:
            for p in eligibility_div.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text:
                    description.append(text)
        
        # Lists (eligibility criteria)
        eligibility_criteria = []
        if eligibility_div:
            for ul in eligibility_div.find_all("ul"):
                for li in ul.find_all("li"):
                    eligibility_criteria.append(li.get_text(" ", strip=True))
        
        # Admission process steps
        admission_steps = []
        if eligibility_div:
            # Look for admission heading
            admission_headings = eligibility_div.find_all(["h2", "h3", "h4"], string=lambda x: x and "admission" in x.lower() if x else False)
            if not admission_headings:
                # Check for any list after a heading containing "admission"
                for heading in eligibility_div.find_all(["h2", "h3", "h4"]):
                    if "admission" in heading.text.lower():
                        ul = heading.find_next("ul")
                        if ul:
                            for li in ul.find_all("li"):
                                admission_steps.append(li.get_text(" ", strip=True))
                        break
        
        # Useful links
        useful_links = []
        if eligibility_div:
            for a in eligibility_div.find_all("a", href=True):
                useful_links.append({
                    "title": a.get_text(strip=True),
                    "url": a["href"]
                })
        
        # FAQs from eligibility section
        eligibility_faqs = []
        faq_container = eligibility_section.find("div", class_="c358de")
        if faq_container:
            faq_section = faq_container.find("div", id="sectional-faqs-0")
            if faq_section:
                faq_questions = faq_section.find_all("div", class_="html-0")
                for q in faq_questions:
                    question_elem = q.find("strong", class_="flx-box")
                    if question_elem:
                        question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                        
                        answer_div = q.find_next("div", class_="_16f53f")
                        if answer_div:
                            answer = " ".join(
                                p.get_text(" ", strip=True)
                                for p in answer_div.find_all("p")
                                if p.get_text(strip=True)
                            )
                            
                            eligibility_faqs.append({
                                "question": question,
                                "answer": answer
                            })
        
        data["eligibility"] = {
            "section_title": section_name,
            "description": description,
            "eligibility_criteria": eligibility_criteria,
            "admission_steps": admission_steps,
            "useful_links": useful_links,
            "faqs": eligibility_faqs
        }
    
    # =====================================================
    # ADDITIONAL SECTIONS - Dynamically find all sections
    # =====================================================
    all_sections = soup.find_all("section", id=lambda x: x and x.startswith("chp_section_"))
    
    other_sections_data = {}
    
    for section in all_sections:
        section_id = section.get("id", "")
        section_name = section_id.replace("chp_section_", "")
        
        if section_name in ["overview", "eligibility"]:
            continue  # Already processed
            
        # Find section title
        section_title = section.find(["h1", "h2", "h3"])
        title_text = section_title.text.strip() if section_title else section_name
        
        # Find main content divs (they usually have ids starting with wikkiContents)
        content_divs = section.find_all("div", id=lambda x: x and x.startswith("wikkiContents_"))
        
        section_content = {
            "title": title_text,
            "content": []
        }
        
        for content_div in content_divs:
            # Get all paragraphs
            paragraphs = []
            for p in content_div.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text:
                    paragraphs.append(text)
            
            # Get all lists
            lists = []
            for ul in content_div.find_all("ul"):
                list_items = []
                for li in ul.find_all("li"):
                    list_items.append(li.get_text(" ", strip=True))
                if list_items:
                    lists.append(list_items)
            
            # Get all tables
            tables = []
            for table in content_div.find_all("table"):
                table_data = []
                for tr in table.find_all("tr"):
                    row = []
                    for td in tr.find_all(["td", "th"]):
                        row.append(td.get_text(" ", strip=True))
                    if row:
                        table_data.append(row)
                if table_data:
                    tables.append(table_data)
            
            # Get all links
            links = []
            for a in content_div.find_all("a", href=True):
                links.append({
                    "title": a.get_text(strip=True),
                    "url": a["href"]
                })
            
            if paragraphs or lists or tables or links:
                section_content["content"].append({
                    "paragraphs": paragraphs,
                    "lists": lists,
                    "tables": tables,
                    "links": links
                })
        
        # Find FAQs in this section
        section_faqs = []
        faq_container = section.find("div", class_="c358de")
        if faq_container:
            faq_section = faq_container.find("div", class_="_0c7561")
            if faq_section:
                faq_questions = faq_section.find_all("div", class_="html-0")
                for q in faq_questions:
                    question_elem = q.find("strong", class_="flx-box")
                    if question_elem:
                        question = question_elem.get_text(" ", strip=True).replace("Q:", "").strip()
                        
                        answer_div = q.find_next("div", class_="_16f53f")
                        if answer_div:
                            answer = " ".join(
                                p.get_text(" ", strip=True)
                                for p in answer_div.find_all("p")
                                if p.get_text(strip=True)
                            )
                            
                            section_faqs.append({
                                "question": question,
                                "answer": answer
                            })
        
        section_content["faqs"] = section_faqs
        
        other_sections_data[section_name] = section_content
    
    if other_sections_data:
        data["other_sections"] = other_sections_data
    
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



# def scrape_mbbs_subjects_overview(driver):
#     driver.get(PCOMBA_SUB_URL)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}

#     section = soup.find("section", id="chp_subjects_overview")
#     if not section:
#         return data

#     # ===============================
#     # Course Title - Improved extraction
#     # ===============================
#     # Try to find the page title from metadata or main heading
#     page_title = soup.find("title")
#     if page_title:
#         data["title"] = page_title.get_text(strip=True)
#     else:
#         # Look for h1 in the section
#         h1_tag = section.find("h1")
#         if h1_tag:
#             data["title"] = h1_tag.get_text(strip=True)
#         else:
#             # Use first meaningful text
#             first_para = section.find("p")
#             if first_para:
#                 text = first_para.get_text(strip=True)
#                 if len(text) > 20:  # Meaningful text
#                     data["title"] = text[:50] + "..." if len(text) > 50 else text
#                 else:
#                     data["title"] = "MD Subjects Overview"

#     # ===============================
#     # Updated Date
#     # ===============================
#     updated_div = section.find("div", string=lambda x: x and "Updated on" in x)
#     if updated_div:
#         span = updated_div.find("span")
#         if span:
#             data["updated_on"] = span.get_text(strip=True)
#         else:
#             text = updated_div.get_text(strip=True)
#             date_match = re.search(r'Updated on (.+)', text)
#             if date_match:
#                 data["updated_on"] = date_match.group(1)

#     # ===============================
#     # Author Info
#     # ===============================
#     author_block = section.find("div", class_="be8c")
#     if author_block:
#         author_info = {}
        
#         a_tag = author_block.find("a")
#         if a_tag:
#             author_info["name"] = a_tag.get_text(strip=True)
#             author_info["profile"] = a_tag.get("href", "")
        
#         img_tag = author_block.find("img")
#         if img_tag:
#             author_info["image"] = img_tag.get("src", "")
        
#         role_span = author_block.find("span", class_="b0fc")
#         if role_span:
#             author_info["role"] = role_span.get_text(strip=True)
        
#         author_info["verified"] = bool(author_block.find("i", class_="tickIcon"))
        
#         data["author"] = author_info

#     # =====================================================
#     # MAIN CONTENT DIV
#     # =====================================================
#     content = section.find("div", id="wikkiContents_chp_subjects_overview_0")
#     if not content:
#         return data

#     content_div = content.find("div")
#     if not content_div:
#         content_div = content

#     # =====================================================
#     # DESCRIPTION PARAGRAPHS
#     # =====================================================
#     description = []
#     seen_texts = set()  # To avoid duplicates
    
#     # Collect first few meaningful paragraphs
#     for p in content_div.find_all("p", limit=5):
#         text = p.get_text(" ", strip=True)
#         if (text and len(text) > 30 and 
#             "DFP-Banner" not in text and 
#             "Updated on" not in text and
#             text not in seen_texts):
#             description.append(text)
#             seen_texts.add(text)
    
#     data["description"] = description

#     # =====================================================
#     # TABLE EXTRACTION HELPER
#     # =====================================================
#     def extract_table(table):
#         headers = []
#         rows = []
        
#         # Extract headers
#         ths = table.find_all("th")
#         if ths:
#             headers = [th.get_text(" ", strip=True) for th in ths]
        
#         # Extract rows, skip header rows
#         for tr in table.find_all("tr"):
#             # Skip if it's a header row
#             if tr.find("th"):
#                 continue
                
#             tds = tr.find_all("td")
#             if tds:
#                 row_data = []
#                 for td in tds:
#                     # Handle lists
#                     lis = td.find_all("li")
#                     if lis:
#                         list_items = [li.get_text(" ", strip=True) for li in lis if li.get_text(strip=True)]
#                         row_data.append(list_items if list_items else td.get_text(" ", strip=True))
#                     else:
#                         row_data.append(td.get_text(" ", strip=True))
#                 if any(row_data):  # Only add non-empty rows
#                     rows.append(row_data)
        
#         return {"headers": headers, "rows": rows}

#     # =====================================================
#     # BASIC MEDICAL SCIENCES SUBJECTS (FIRST TABLE)
#     # =====================================================
#     basic_medical_sciences = []
    
#     # Find the first table in the content
#     first_table = content_div.find("table")
#     if first_table:
#         table_data = extract_table(first_table)
#         # Extract subjects from first column
#         for row in table_data["rows"]:
#             if row and row[0] and "month" not in row[0].lower() and "year" not in row[0].lower():
#                 basic_medical_sciences.append(row[0])
    
#     data["basic_medical_sciences"] = basic_medical_sciences

#     # =====================================================
#     # CLINICAL DISCIPLINES SUBJECTS (SECOND TABLE)
#     # =====================================================
#     clinical_disciplines = []
    
#     # Find all tables
#     all_tables = content_div.find_all("table")
#     if len(all_tables) >= 2:
#         second_table = all_tables[1]
#         table_data = extract_table(second_table)
#         # Extract subjects from first column
#         for row in table_data["rows"]:
#             if row and row[0] and "month" not in row[0].lower() and "year" not in row[0].lower():
#                 clinical_disciplines.append(row[0])
    
#     data["clinical_disciplines"] = clinical_disciplines

#     # =====================================================
#     # DETAILED SYLLABUS (Year-wise table - THIRD TABLE)
#     # =====================================================
#     detailed_syllabus = {"headers": [], "rows": []}
    
#     if len(all_tables) >= 3:
#         third_table = all_tables[2]
#         table_data = extract_table(third_table)
#         # Check if this is the year-wise table (has "Year" in headers)
#         headers_str = " ".join(table_data["headers"])
#         if "Year" in headers_str or "year" in headers_str.lower():
#             detailed_syllabus = table_data
    
#     data["detailed_syllabus"] = detailed_syllabus

#     # =====================================================
#     # SPECIALIZATIONS TABLE (FOURTH TABLE)
#     # =====================================================
#     specializations = {"headers": [], "rows": []}
    
#     if len(all_tables) >= 4:
#         fourth_table = all_tables[3]
#         table_data = extract_table(fourth_table)
#         # Check if this is specializations table
#         headers_str = " ".join(table_data["headers"])
#         if "Specialisation" in headers_str or "Specialization" in headers_str:
#             specializations = table_data
    
#     data["specializations"] = specializations

#     # =====================================================
#     # BOOKS AND AUTHORS TABLE (FIFTH TABLE)
#     # =====================================================
#     books_and_authors = {"headers": [], "rows": []}
    
#     if len(all_tables) >= 5:
#         fifth_table = all_tables[4]
#         table_data = extract_table(fifth_table)
#         # Check if this is books table
#         headers_str = " ".join(table_data["headers"])
#         if "Book" in headers_str or "Author" in headers_str:
#             books_and_authors = table_data
    
#     data["books_and_authors"] = books_and_authors

#     # =====================================================
#     # FAQs EXTRACTION
#     # =====================================================
#     faqs = []
#     faq_section = None
    
#     # Find FAQ section
#     for elem in content_div.find_all():
#         if elem.name in ['h2', 'h3'] and "Frequently Asked Questions" in elem.get_text():
#             faq_section = elem
#             break
    
#     if faq_section:
#         # Collect all elements after FAQ heading until next section
#         current_elem = faq_section
#         while current_elem:
#             current_elem = current_elem.find_next()
            
#             # Stop if we reach next section or end
#             if not current_elem or (current_elem.name in ['h2', 'h3'] and current_elem != faq_section):
#                 break
            
#             # Check for FAQ question
#             if current_elem.name == 'p' and current_elem.get("class") and "fQ" in current_elem.get("class"):
#                 question_elem = current_elem.find("strong")
#                 if not question_elem:
#                     question_elem = current_elem
                
#                 question = question_elem.get_text(" ", strip=True)
#                 # Clean question
#                 for prefix in ["Q:", "Q :", "Q."]:
#                     if question.startswith(prefix):
#                         question = question[len(prefix):].strip()
#                         break
                
#                 # Find answer
#                 answer_elem = current_elem.find_next("div", class_="fA")
#                 if answer_elem:
#                     answer = answer_elem.get_text(" ", strip=True)
#                     # Clean answer
#                     for prefix in ["A:", "A :", "A."]:
#                         if answer.startswith(prefix):
#                             answer = answer[len(prefix):].strip()
#                             break
                    
#                     if question and answer:
#                         faqs.append({
#                             "question": question,
#                             "answer": answer
#                         })
    
#     data["faqs"] = faqs

#     # =====================================================
#     # IMPORTANT LINKS (Unique links only)
#     # =====================================================
#     important_links = []
#     seen_urls = set()
    
#     for a in content_div.find_all("a", href=True):
#         text = a.get_text(strip=True)
#         url = a.get("href", "")
        
#         if (text and url and 
#             url not in seen_urls and
#             not url.startswith("#") and
#             "javascript:" not in url and
#             not any(x in text.lower() for x in ["ask", "gpt", "shiksha", "more", "view", "arrow"])):
            
#             important_links.append({
#                 "title": text,
#                 "url": url
#             })
#             seen_urls.add(url)
    
#     data["important_links"] = important_links

#     # =====================================================
#     # YOUTUBE VIDEOS
#     # =====================================================
#     youtube_videos = []
#     for iframe in content_div.find_all("iframe"):
#         src = iframe.get("src", "")
#         if src and ("youtube.com" in src or "youtu.be" in src):
#             youtube_videos.append(src)
    
#     data["youtube_videos"] = youtube_videos

#     # =====================================================
#     # ALL TABLES (for reference, but not duplicate of above)
#     # =====================================================
#     all_tables_data = []
#     table_count = 0
    
#     for table in content_div.find_all("table"):
#         table_data = extract_table(table)
#         if table_data["headers"] or table_data["rows"]:
#             # Add table type identifier
#             headers_str = " ".join(table_data["headers"])
#             table_type = "unknown"
            
#             if "Subject" in headers_str and "Book" not in headers_str:
#                 if "Specialisation" in headers_str:
#                     table_type = "specializations"
#                 elif "Year" in headers_str:
#                     table_type = "detailed_syllabus"
#                 else:
#                     table_type = "subjects"
#             elif "Book" in headers_str or "Author" in headers_str:
#                 table_type = "books"
            
#             all_tables_data.append({
#                 "table_number": table_count + 1,
#                 "type": table_type,
#                 "headers": table_data["headers"],
#                 "rows": table_data["rows"]
#             })
#             table_count += 1
    
#     data["all_tables"] = all_tables_data

#     return data

def scrape_bmlt_syllabus(driver):
    driver.get(PCOMBA_MBA_SYLLABUS_URL)
    wait = WebDriverWait(driver, 15)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "title": "",
        "updated_on": None,
        "author": None,
        "overview": [],
        "subjects": []
    }

    # ===============================
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = h1.text.strip() if h1 else None

    # ===============================
    # Updated Date
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = span.get_text(strip=True) if span else None

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": a.get_text(strip=True) if a else None,
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": author_block.find("span", class_="b0fc").get_text(strip=True)
                    if author_block.find("span", class_="b0fc") else None,
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # Main Content
    container = soup.find("div", id="wikkiContents_chp_syllabus_overview_0")

    if not container:
        return data

    # -------------------------------
    # Overview paragraphs (all paragraphs before tables)
    all_paragraphs = container.find_all("p")
    
    for p in all_paragraphs:
        text = p.get_text(" ", strip=True)
        if text and "DFP-Banner" not in text:
            # Skip if this paragraph is inside a table
            if p.find_parent("table"):
                continue
            data["overview"].append(text)
    
    # -------------------------------
    # All Tables Processing
    tables = container.find_all("table")
    
    for table in tables:
        rows = table.find_all("tr")
        
        # Check if it's a 2-column table
        if len(rows) > 0:
            first_row_cols = rows[0].find_all(["th", "td"])
            
            # Check for 2-column table
            if len(first_row_cols) == 2:
                # Get headers to check table type
                header1 = first_row_cols[0].get_text(" ", strip=True)
                header2 = first_row_cols[1].get_text(" ", strip=True)
                
                if "Subject title" in header1 and "Subject details" in header2:
                    # This is a 2-column subjects table
                    for row in rows[1:]:  # Skip header row
                        cols = row.find_all("td")
                        if len(cols) == 2:
                            subject_name = cols[0].get_text(" ", strip=True)
                            subject_cell = cols[1]
                            
                            # Description
                            description = ""
                            topics = []
                            
                            # Get description from paragraphs
                            paragraphs = subject_cell.find_all("p")
                            if paragraphs:
                                description = paragraphs[0].get_text(" ", strip=True)
                            else:
                                # If no paragraph, get all text
                                description = subject_cell.get_text(" ", strip=True)
                            
                            # Bullet Topics
                            ul = subject_cell.find("ul")
                            if ul:
                                for li in ul.find_all("li"):
                                    topic = li.get_text(" ", strip=True)
                                    if topic:
                                        topics.append(topic)
                            
                            if subject_name:
                                data["subjects"].append({
                                    "name": subject_name,
                                    "description": description,
                                    "topics": topics,
                                    "table_type": "core_elective_subjects"
                                })
                
                elif "Specialisation" in header1 or "Subjects" in header1:
                    # This is a 3-column specializations table (but we have 2 headers in first row)
                    # Actually check the table properly
                    if len(rows) > 1:
                        second_row_cols = rows[1].find_all(["td", "th"])
                        if len(second_row_cols) == 3:
                            # This is a 3-column table with merged header row
                            for row in rows[1:]:  # Start from row 1 since row 0 has headers
                                cols = row.find_all("td")
                                if len(cols) == 3:
                                    specialization_name = cols[0].get_text(" ", strip=True)
                                    subjects_cell = cols[1]
                                    details_cell = cols[2]
                                    
                                    # Process subjects (lists)
                                    subjects = []
                                    ul = subjects_cell.find("ul")
                                    if ul:
                                        for li in ul.find_all("li"):
                                            subject = li.get_text(" ", strip=True)
                                            if subject:
                                                subjects.append(subject)
                                    
                                    # Process details
                                    details = details_cell.get_text(" ", strip=True)
                                    
                                    if specialization_name:
                                        data["subjects"].append({
                                            "name": specialization_name,
                                            "description": details,
                                            "topics": subjects,
                                            "table_type": "specializations"
                                        })
            
            # Check if it's a 3-column table (Specializations)
            elif len(first_row_cols) == 3:
                # Get headers
                header1 = first_row_cols[0].get_text(" ", strip=True)
                header2 = first_row_cols[1].get_text(" ", strip=True)
                header3 = first_row_cols[2].get_text(" ", strip=True)
                
                if "Specialisation" in header1 or "Subject" in header1:
                    # This is a 3-column specializations or books table
                    if "Subjects" in header2 and "Details" in header3:
                        # Specializations table
                        for row in rows[1:]:
                            cols = row.find_all("td")
                            if len(cols) == 3:
                                specialization_name = cols[0].get_text(" ", strip=True)
                                subjects_cell = cols[1]
                                details_cell = cols[2]
                                
                                # Process subjects (lists)
                                subjects = []
                                ul = subjects_cell.find("ul")
                                if ul:
                                    for li in ul.find_all("li"):
                                        subject = li.get_text(" ", strip=True)
                                        if subject:
                                            subjects.append(subject)
                                
                                # Process details
                                details = details_cell.get_text(" ", strip=True)
                                
                                if specialization_name:
                                    data["subjects"].append({
                                        "name": specialization_name,
                                        "description": details,
                                        "topics": subjects,
                                        "table_type": "specializations"
                                    })
                    
                    elif "Book title" in header2 and "Author" in header3:
                        # Books table
                        for row in rows[1:]:
                            cols = row.find_all("td")
                            if len(cols) == 4:
                                subject = cols[0].get_text(" ", strip=True)
                                book_title = cols[1].get_text(" ", strip=True)
                                author = cols[2].get_text(" ", strip=True)
                                description = cols[3].get_text(" ", strip=True)
                                
                                if book_title:
                                    data["subjects"].append({
                                        "name": book_title,
                                        "description": description,
                                        "type": subject,
                                        "author": author,
                                        "table_type": "books"
                                    })
            
            # Check if it's a 4-column table (Detailed Syllabus table)
            elif len(first_row_cols) == 4:
                # This is the 4-column detailed syllabus table
                headers = []
                header_row = rows[0]
                header_cells = header_row.find_all(["th", "td"])
                for cell in header_cells:
                    header_text = cell.get_text(" ", strip=True)
                    if header_text:
                        headers.append(header_text)
                
                # Check if this is the detailed syllabus table
                if len(headers) >= 4:
                    current_semester = None
                    
                    for row in rows[1:]:  # Skip header row
                        cols = row.find_all(["td", "th"])
                        
                        if len(cols) >= 4:
                            # Extract semester if present
                            semester_cell = cols[0]
                            semester_text = semester_cell.get_text(" ", strip=True)
                            if semester_text and semester_text not in ["", "&nbsp;"]:
                                current_semester = semester_text
                            
                            # Extract other columns
                            core_elective = cols[1].get_text(" ", strip=True) if len(cols) > 1 else ""
                            subject_title = cols[2].get_text(" ", strip=True) if len(cols) > 2 else ""
                            subject_details_cell = cols[3] if len(cols) > 3 else None
                            
                            # Process subject details
                            description = ""
                            topics = []
                            
                            if subject_details_cell:
                                # Get all text from the cell
                                all_text = subject_details_cell.get_text(" ", strip=True)
                                description = all_text
                                
                                # Also check for lists in the cell
                                ul_elements = subject_details_cell.find_all("ul")
                                for ul in ul_elements:
                                    for li in ul.find_all("li"):
                                        topic = li.get_text(" ", strip=True)
                                        if topic:
                                            topics.append(topic)
                            
                            # Create subject entry
                            if subject_title or description:
                                data["subjects"].append({
                                    "semester": current_semester or "",
                                    "type": core_elective,
                                    "name": subject_title,
                                    "description": description,
                                    "topics": topics,
                                    "table_type": "detailed_syllabus"
                                })

    return data

# def scrape_md_career(driver):
#     driver.get(PCOMBA_MBA_CAREER_URL)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}

#     section = soup.find("section", id="chp_career_overview")
#     if not section:
#         return data
    
#     course_name_div = soup.find("div", class_="a54c")
#     if course_name_div:
#         h1 = course_name_div.find("h1")
#         data["title"] = h1.text.strip() if h1 else None
#     # ===============================
#     # Updated Date
#     updated_div = section.find("div", class_="f48b")
#     if updated_div:
#         span = updated_div.find("span")
#         data["updated_on"] = span.get_text(strip=True) if span else None

#     # ===============================
#     # Author Info
#     author_block = section.find("div", class_="be8c")
#     if author_block:
#         a = author_block.find("a")
#         img = author_block.find("img")
#         data["author"] = {
#             "name": a.get_text(strip=True) if a else None,
#             "profile": a["href"] if a else None,
#             "image": img["src"] if img else None,
#             "role": author_block.find("span", class_="b0fc").get_text(strip=True)
#                     if author_block.find("span", class_="b0fc") else None,
#             "verified": bool(author_block.find("i", class_="tickIcon"))
#         }

#     content = section.find("div", class_="wikkiContents")

#     # ===============================
#     # Career Overview (top intro paras only)
#     overview = []
#     for p in content.find_all("p"):
#         if p.find_parent("table"):
#             continue
#         txt = p.get_text(strip=True)
#         if txt:
#             overview.append(txt)
#         if len(overview) == 3:
#             break
#     data["career_overview"] = overview

#     # ===============================
#     # Helper: parse table
#     def parse_table(table):
#         rows = []
#         for tr in table.find_all("tr")[1:]:
#             cols = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
#             if cols:
#                 rows.append(cols)
#         return rows

#     # ===============================
#     # Helper: heading ke niche ke paragraphs
#     def extract_description(h2):
#         desc = []
#         for sib in h2.find_next_siblings():
#             if sib.name == "table" or sib.name == "h2":
#                 break
#             if sib.name == "p":
#                 text = sib.get_text(" ", strip=True)
#                 if text:
#                     desc.append(text)
#         return desc

#     # ===============================
#     data["sections"] = {}

#     for h2 in content.find_all("h2"):
#         heading = h2.get_text(strip=True)
#         key = heading.lower().replace(" ", "_").replace(":", "")

#         section_obj = {
#             "heading": heading,
#             "description": extract_description(h2),
#             "data": []
#         }

#         table = h2.find_next("table")
#         if table:
#             rows = parse_table(table)

#             # 🔹 Top Recruiters
#             if "top recruiters" in heading.lower():
#                 for r in rows:
#                     section_obj["data"].extend(r)

#             # 🔹 Core Sectors / Industries
#             elif "core sectors" in heading.lower() or "core industries" in heading.lower():
#                 for r in rows:
#                     section_obj["data"].extend(r)

#             # 🔹 Best Colleges
#             elif "best md colleges" in heading.lower():
#                 for r in rows:
#                     if len(r) >= 2:
#                         section_obj["data"].append({
#                             "college": r[0],
#                             "median_salary": r[1]
#                         })

#         data["sections"][key] = section_obj

#     return data

 
# # convert a list of Tags to clean text
def tags_to_text(tags):
    return [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

def scrape_addmission_2026_data(driver):

    driver.get(PCOMBA_MBA_ADDMISSION_2026_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}

    # ===================== MAIN SECTION =====================
    section = soup.find("section", id="chp_admission_overview")
    if not section:
        return data
    # Course Name
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = h1.text.strip() if h1 else None
    # ===================== UPDATED DATE =====================
    updated = section.find("div", string=lambda x: x and "Updated on" in x)
    if updated:
        span = updated.find("span")
        data["updated_on"] = span.get_text(strip=True) if span else updated.get_text(strip=True)

    # ===================== AUTHOR =====================
    author_block = section.find("div", class_="be8c")
    if author_block:
        author = {}
        a = author_block.find("a")
        img = author_block.find("img")

        author["name"] = a.get_text(strip=True) if a else None
        author["profile"] = a["href"] if a else None
        author["image"] = img["src"] if img else None

        role = author_block.find("span", class_="b0fc")
        author["role"] = role.get_text(strip=True) if role else None
        author["verified"] = bool(author_block.find("i", class_="tickIcon"))

        data["author"] = author

    # ===================== CONTENT SCRAPING =====================
    content_div = section.find("div", id=lambda x: x and "wikkiContents" in x)
    content_data = []

    for elem in content_div.find_all(
        ["h2", "h3", "p", "table", "ul", "iframe"], recursive=True
    ):

        # ---------- HEADINGS ----------
        if elem.name in ["h2", "h3"]:
            content_data.append({
                "type": "heading",
                "level": elem.name,
                "text": elem.get_text(" ", strip=True)
            })

        # ---------- PARAGRAPHS ----------
        elif elem.name == "p":
            links = []
            for a in elem.find_all("a"):
                links.append({
                    "text": a.get_text(strip=True),
                    "url": a.get("href")
                })

            content_data.append({
                "type": "paragraph",
                "text": elem.get_text(" ", strip=True),
                "links": links
            })

        # ---------- TABLES ----------
        elif elem.name == "table":
            table_data = []
            rows = elem.find_all("tr")
            headers = [th.get_text(strip=True) for th in rows[0].find_all("th")] if rows else []

            for row in rows[1:]:
                cols = [td.get_text(" ", strip=True) for td in row.find_all("td")]
                if headers and len(headers) == len(cols):
                    table_data.append(dict(zip(headers, cols)))
                else:
                    table_data.append(cols)

            content_data.append({
                "type": "table",
                "headers": headers,
                "rows": table_data
            })

        # ---------- IFRAME (YouTube) ----------
        elif elem.name == "iframe":
            content_data.append({
                "type": "video",
                "src": elem.get("src")
            })

    data["full_content"] = content_data

    return data


# def scrape_mba_fees_overview(driver):
#     driver.get(PCOMBA_MBA_FEES_URL)
#     soup = BeautifulSoup(driver.page_source, "html.parser")

#     data = {}

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
#         author_data = {
#             "name": clean(a),
#             "profile": a["href"] if a else None
#         }
        
#         img = author_block.find("img")
#         if img:
#             author_data["image"] = img["src"]
            
#         role_span = author_block.find("span", class_="b0fc")
#         if role_span:
#             author_data["role"] = clean(role_span)
            
#         tick_icon = author_block.find("i", class_="tickIcon")
#         author_data["verified"] = bool(tick_icon)
        
#         data["author"] = author_data

#     # ===============================
#     # Overview Section
#     overview_section = soup.find("div", id="wikkiContents_chp_fees_overview_0")
#     if overview_section:
#         # Overview text
#         overview_divs = overview_section.find_all("div", id=lambda x: x and "wikkiContents_multi_ADP_undefined" in x)
        
#         if overview_divs and len(overview_divs) > 0:
#             first_div = overview_divs[0]
#             paragraphs = first_div.find_all("p")
#             overview_text = []
            
#             for p in paragraphs:
#                 text = p.get_text(strip=True)
#                 if text and text != "\xa0":
#                     overview_text.append(text)
            
#             data["overview_text"] = overview_text

#     # ===============================
#     # Relevant Links Section
#     relevant_links_div = soup.find("div", string=lambda x: x and "Relevant Links for MBBS Course Fees:" in x)
#     if relevant_links_div:
#         # Find the parent div with helpful links
#         relevant_links = []
#         next_elem = relevant_links_div.find_next("p")
#         while next_elem and next_elem.name == "p":
#             a_tag = next_elem.find("a")
#             if a_tag:
#                 relevant_links.append({
#                     "title": a_tag.get_text(strip=True),
#                     "url": a_tag.get("href")
#                 })
#             next_elem = next_elem.find_next_sibling()
        
#         data["relevant_links"] = relevant_links

#     # ===============================
#     # MBBS Course Fees Structure Section
#     fees_structure_h2 = soup.find("h2", id="chp_fees_toc_0")
#     if fees_structure_h2:
#         # Get heading
#         data["fees_structure_heading"] = clean(fees_structure_h2)
        
#         # Get paragraph after heading
#         fees_para = fees_structure_h2.find_next("p")
#         if fees_para:
#             data["fees_structure_description"] = clean(fees_para)
        
#         # Get table data
#         table = fees_structure_h2.find_next("table")
#         if table:
#             fees_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     fees_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["fees_structure_table"] = fees_data
        
#         # Get helpful links after table
#         helpful_links_h2 = table.find_next("p") if table else None
#         if helpful_links_h2 and helpful_links_h2.find("span", style=lambda x: x and "color: #e03e2d" in x):
#             helpful_links = []
#             next_p = helpful_links_h2.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["fees_structure_helpful_links"] = helpful_links

#     # ===============================
#     # MBBS Course Fees in Top Colleges Section
#     top_colleges_h2 = soup.find("h2", id="chp_fees_toc_1")
#     if top_colleges_h2:
#         data["top_colleges_heading"] = clean(top_colleges_h2)
        
#         # Find AIIMS fees table section
#         aiims_table_para = top_colleges_h2.find_next("p", string=lambda x: x and "MBBS course fees structure at AIIMS" in x)
#         if aiims_table_para:
#             data["aiims_fees_description"] = clean(aiims_table_para)
            
#             # Get AIIMS fees table
#             aiims_table = aiims_table_para.find_next("table")
#             if aiims_table:
#                 aiims_data = []
#                 rows = aiims_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         college_link = cols[0].find("a")
#                         aiims_data.append({
#                             "college": clean(cols[0]),
#                             "fees": clean(cols[1]),
#                             "link": college_link.get("href") if college_link else None
#                         })
#                 data["aiims_fees_table"] = aiims_data

#     # ===============================
#     # Quick Links for Medical Courses
#     quick_links_para = soup.find("p", string=lambda x: x and "Quick Links for Medical Courses:" in x)
#     if quick_links_para:
#         data["quick_links_heading"] = clean(quick_links_para)
        
#         # Get quick links table
#         quick_links_table = quick_links_para.find_next("table")
#         if quick_links_table:
#             quick_links_data = []
#             rows = quick_links_table.find_all("tr")
#             for row in rows:
#                 cols = row.find_all("td")
#                 for col in cols:
#                     a_tag = col.find("a")
#                     if a_tag:
#                         quick_links_data.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
#             data["quick_links"] = quick_links_data

#     # ===============================
#     # MBBS Fees in Government College Section
#     govt_fees_h3 = soup.find("h3", id="chp_fees_toc_1_2")
#     if govt_fees_h3:
#         data["govt_fees_heading"] = clean(govt_fees_h3)
        
#         # Get description paragraph
#         govt_desc = govt_fees_h3.find_next("p")
#         if govt_desc:
#             data["govt_fees_description"] = clean(govt_desc)
        
#         # Get government fees table
#         govt_table = govt_fees_h3.find_next("table")
#         if govt_table:
#             govt_data = []
#             rows = govt_table.find_all("tr")
#             for row in rows[1:]:  # Skip header (first row has heading in second column)
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     govt_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["govt_fees_table"] = govt_data
        
#         # Get helpful links after table
#         helpful_links_start = govt_table.find_next("p") if govt_table else None
#         if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: #e03e2d" in x):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["govt_fees_helpful_links"] = helpful_links

#     # ===============================
#     # MBBS Course Fees in Top Private Colleges Section
#     private_fees_h3 = soup.find("h3", id="chp_fees_toc_1_3")
#     if private_fees_h3:
#         data["private_fees_heading"] = clean(private_fees_h3)
        
#         # Get description paragraph
#         private_desc = private_fees_h3.find_next("p")
#         if private_desc:
#             data["private_fees_description"] = clean(private_desc)
        
#         # Get private fees table
#         private_table = private_fees_h3.find_next("table")
#         if private_table:
#             private_data = []
#             rows = private_table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     private_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["private_fees_table"] = private_data
        
#         # Get suggested readings
#         suggested_readings_start = private_table.find_next("p") if private_table else None
#         if suggested_readings_start and suggested_readings_start.find("span", style=lambda x: x and "color: #e03e2d" in x):
#             suggested_readings = []
#             next_p = suggested_readings_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     suggested_readings.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["suggested_readings"] = suggested_readings

#     # ===============================
#     # MBBS Course Fees: Location-Wise Section
#     location_wise_h2 = soup.find("h2", id="chp_fees_toc_2")
#     if location_wise_h2:
#         data["location_wise_heading"] = clean(location_wise_h2)
        
#         # Get description paragraphs
#         desc_para1 = location_wise_h2.find_next("p")
#         if desc_para1:
#             data["location_wise_description1"] = clean(desc_para1)
        
#         desc_para2 = desc_para1.find_next("p") if desc_para1 else None
#         if desc_para2:
#             data["location_wise_description2"] = clean(desc_para2)

#     # ===============================
#     # Location-wise fees tables
#     data["location_wise_fees"] = {}
    
#     # Delhi Section
#     delhi_heading = soup.find("p", string=lambda x: x and "MBBS Fees in Delhi" in x)
#     if delhi_heading:
#         data["location_wise_fees"]["delhi"] = {
#             "heading": clean(delhi_heading),
#             "description": "",
#             "colleges": []
#         }
        
#         # Get description
#         delhi_desc = delhi_heading.find_next("p")
#         if delhi_desc:
#             data["location_wise_fees"]["delhi"]["description"] = clean(delhi_desc)
        
#         # Get Delhi table
#         delhi_table = delhi_heading.find_next("table")
#         if delhi_table:
#             delhi_data = []
#             rows = delhi_table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     delhi_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["location_wise_fees"]["delhi"]["colleges"] = delhi_data
        
#         # Get suggested readings after Delhi table
#         suggested_start = delhi_table.find_next("p") if delhi_table else None
#         if suggested_start and suggested_start.get_text(strip=True).startswith("Suggested Readings"):
#             suggested_readings = []
#             next_p = suggested_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     suggested_readings.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["location_wise_fees"]["delhi"]["suggested_readings"] = suggested_readings

#     # Kolkata Section
#     kolkata_heading = soup.find("p", string=lambda x: x and "MBBS Course Fees in Kolkata" in x)
#     if kolkata_heading:
#         data["location_wise_fees"]["kolkata"] = {
#             "heading": clean(kolkata_heading),
#             "description": "",
#             "colleges": []
#         }
        
#         # Get description
#         kolkata_desc = kolkata_heading.find_next("p")
#         if kolkata_desc:
#             data["location_wise_fees"]["kolkata"]["description"] = clean(kolkata_desc)
        
#         # Get Kolkata table
#         kolkata_table = kolkata_heading.find_next("table")
#         if kolkata_table:
#             kolkata_data = []
#             rows = kolkata_table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     kolkata_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["location_wise_fees"]["kolkata"]["colleges"] = kolkata_data

#     # Hyderabad Section
#     hyderabad_heading = soup.find("p", string=lambda x: x and "MBBS Fees in Hyderabad" in x)
#     if hyderabad_heading:
#         data["location_wise_fees"]["hyderabad"] = {
#             "heading": clean(hyderabad_heading),
#             "description": "",
#             "colleges": []
#         }
        
#         # Get description
#         hyderabad_desc = hyderabad_heading.find_next("p")
#         if hyderabad_desc:
#             data["location_wise_fees"]["hyderabad"]["description"] = clean(hyderabad_desc)
        
#         # Get Hyderabad table
#         hyderabad_table = hyderabad_heading.find_next("table")
#         if hyderabad_table:
#             hyderabad_data = []
#             rows = hyderabad_table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     hyderabad_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["location_wise_fees"]["hyderabad"]["colleges"] = hyderabad_data

#     # Bangalore Section
#     bangalore_heading = soup.find("p", string=lambda x: x and "MBBS Course Fee in Bangalore" in x)
#     if bangalore_heading:
#         data["location_wise_fees"]["bangalore"] = {
#             "heading": clean(bangalore_heading),
#             "description": "",
#             "colleges": []
#         }
        
#         # Get description
#         bangalore_desc = bangalore_heading.find_next("p")
#         if bangalore_desc:
#             data["location_wise_fees"]["bangalore"]["description"] = clean(bangalore_desc)
        
#         # Get Bangalore table
#         bangalore_table = bangalore_heading.find_next("table")
#         if bangalore_table:
#             bangalore_data = []
#             rows = bangalore_table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 2:
#                     college_link = cols[0].find("a")
#                     bangalore_data.append({
#                         "college": clean(cols[0]),
#                         "fees": clean(cols[1]),
#                         "link": college_link.get("href") if college_link else None
#                     })
#             data["location_wise_fees"]["bangalore"]["colleges"] = bangalore_data

#     return data

# def scrape_mbbs_vs_md_comparison(driver):
#     # Assuming URL is defined elsewhere
#     driver.get(PCOMBA_COMP_URL)  # आपका MD vs MBBS comparison URL
#     soup = BeautifulSoup(driver.page_source, "html.parser")
    
#     try:
#         author_elem = WebDriverWait(driver, 15).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.be8c a")
#             )
#         )
#     except:
#         print("Author info not found in time.")
#         author_elem = None

#     data = {}
#     # ---------- Course Name ----------
#     try:
#         title = soup.find("div",class_="a54c")
#         h1 = title.find("h1").text.strip()
#         data["title"] = h1
#     except:
#         data["title"] = None

#     # ---------- Updated Date ----------
#     try:
#         updated_elem = driver.find_element(
#             By.CSS_SELECTOR, "div.f48b > div > span"
#         )
#         data["updated_on"] = updated_elem.text.strip()
#     except:
#         data["updated_on"] = None

#     # ---------- Author Info ----------
#     data["author"] = None
#     try:
#         author_block = driver.find_element(By.CSS_SELECTOR, "div.be8c")
#         author_data = {}

#         # Image
#         try:
#             img_tag = author_block.find_element(By.CSS_SELECTOR, "img.ePPImg")
#             author_data["image"] = img_tag.get_attribute("src")
#         except:
#             author_data["image"] = None

#         # Name + profile
#         try:
#             a_tag = author_block.find_element(By.TAG_NAME, "a")
#             author_data["name"] = a_tag.text.strip()
#             author_data["profile"] = a_tag.get_attribute("href")
#         except:
#             author_data["name"] = None
#             author_data["profile"] = None

#         # Verified
#         try:
#             tick = author_block.find_element(By.CSS_SELECTOR, "i.tickIcon")
#             author_data["verified"] = True
#         except:
#             author_data["verified"] = False

#         # Role / designation
#         try:
#             role_span = author_block.find_element(By.CSS_SELECTOR, "span.b0fc")
#             author_data["role"] = role_span.text.strip()
#         except:
#             author_data["role"] = None

#         data["author"] = author_data
#     except:
#         data["author"] = None

#     # ===============================
#     # Overview Section
#     overview_section = soup.find("div", id="wikkiContents_chp_compare_overview_0")
#     if overview_section:
#         # Get all paragraphs before first heading
#         overview_paragraphs = []
#         for element in overview_section.find_all(["p", "h2"]):
#             if element.name == "p":
#                 overview_paragraphs.append(clean(element))
#             elif element.name == "h2":
#                 break
        
#         data["overview_text"] = overview_paragraphs

#     # ===============================
#     # MD vs MBBS: Highlights Section
#     highlights_h2 = soup.find("h2", id="chp_comparison_cp_toc_0")
#     if highlights_h2:
#         data["highlights_heading"] = clean(highlights_h2)
        
#         # Get description paragraph
#         highlights_desc = highlights_h2.find_next("p")
#         if highlights_desc:
#             data["highlights_description"] = clean(highlights_desc)
        
#         # Get comparison table
#         table = highlights_h2.find_next("table")
#         if table:
#             comparison_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     comparison_data.append({
#                         "parameter": clean(cols[0]),
#                         "mbbs": clean(cols[1]),
#                         "md": clean(cols[2])
#                     })
#             data["highlights_table"] = comparison_data
        
#         # Get note paragraph
#         note_p = table.find_next("p") if table else None
#         if note_p and "Note -" in clean(note_p):
#             data["highlights_note"] = clean(note_p)
        
#         # Get helpful links
#         helpful_links_start = note_p.find_next("p") if note_p else None
#         if helpful_links_start and "color: #e03e2d" in str(helpful_links_start):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling("p")
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 elif next_p.name == "h2":
#                     break
#                 next_p = next_p.find_next_sibling("p")
            
#             data["highlights_helpful_links"] = helpful_links

#     # ===============================
#     # MD vs MBBS: Eligibility Section
#     eligibility_h2 = soup.find("h2", id="chp_comparison_cp_toc_2")
#     if eligibility_h2:
#         data["eligibility_heading"] = clean(eligibility_h2)
        
#         # Get description paragraph
#         eligibility_desc = eligibility_h2.find_next("p")
#         if eligibility_desc:
#             data["eligibility_description"] = clean(eligibility_desc)
        
#         # Get eligibility table
#         table = eligibility_h2.find_next("table")
#         if table:
#             eligibility_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     eligibility_data.append({
#                         "parameter": clean(cols[0]),
#                         "mbbs": clean(cols[1]),
#                         "md": clean(cols[2])
#                     })
#             data["eligibility_table"] = eligibility_data
        
#         # Get note paragraph
#         note_p = table.find_next("p") if table else None
#         if note_p and "Note -" in clean(note_p):
#             data["eligibility_note"] = clean(note_p)
        
#         # Get helpful links
#         helpful_links_start = note_p.find_next("p") if note_p else None
#         if helpful_links_start and "color: #e03e2d" in str(helpful_links_start):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling("p")
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling("p")
            
#             data["eligibility_helpful_links"] = helpful_links

#     # ===============================
#     # Entrance Exams Section
#     entrance_exams_h2 = soup.find("h2", string=lambda x: x and "Entrance Exams" in x)
#     if entrance_exams_h2:
#         data["entrance_exams_heading"] = clean(entrance_exams_h2)
        
#         # Get description paragraph
#         entrance_desc = entrance_exams_h2.find_next("p")
#         if entrance_desc:
#             data["entrance_exams_description"] = clean(entrance_desc)
        
#         # Get entrance exams table
#         table = entrance_exams_h2.find_next("table")
#         if table:
#             entrance_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     entrance_data.append({
#                         "particular": clean(cols[0]),
#                         "mbbs": clean(cols[1]),
#                         "md": clean(cols[2])
#                     })
#             data["entrance_exams_table"] = entrance_data
        
#         # Get note paragraph
#         note_p = table.find_next("p") if table else None
#         if note_p and "Note -" in clean(note_p):
#             data["entrance_exams_note"] = clean(note_p)
        
#         # Get helpful links
#         helpful_links_start = note_p.find_next("p") if note_p else None
#         if helpful_links_start and "color: #e03e2d" in str(helpful_links_start):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling("p")
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling("p")
            
#             data["entrance_exams_helpful_links"] = helpful_links

#     # ===============================
#     # Course Syllabus Section
#     syllabus_h2 = soup.find("h2", id="chp_comparison_cp_toc_4")
#     if syllabus_h2:
#         data["syllabus_heading"] = clean(syllabus_h2)
        
#         # Get description paragraph
#         syllabus_desc = syllabus_h2.find_next("p")
#         if syllabus_desc:
#             data["syllabus_description"] = clean(syllabus_desc)
        
#         # Get syllabus table
#         table = syllabus_h2.find_next("table")
#         if table:
#             syllabus_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     syllabus_data.append({
#                         "semester": clean(cols[0]),
#                         "mbbs_syllabus": clean(cols[1]),
#                         "md_syllabus": clean(cols[2])
#                     })
#             data["syllabus_table"] = syllabus_data
        
#         # Get syllabus links
#         syllabus_links = []
#         for p in syllabus_h2.find_all_next("p", limit=3):
#             a_tag = p.find("a")
#             if a_tag and ("MBBS Syllabus" in clean(a_tag) or "MD Syllabus" in clean(a_tag)):
#                 syllabus_links.append({
#                     "title": clean(a_tag),
#                     "url": a_tag.get("href")
#                 })
        
#         data["syllabus_links"] = syllabus_links
        
#         # Get helpful links
#         helpful_links_start = syllabus_h2.find_next("p", string=lambda x: x and "Relevant Links" in x)
#         if helpful_links_start:
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling("p")
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling("p")
            
#             data["syllabus_helpful_links"] = helpful_links

#     # ===============================
#     # Top Colleges Section
#     top_colleges_h2 = soup.find("h2", id="chp_comparison_cp_toc_5")
#     if top_colleges_h2:
#         data["top_colleges_heading"] = clean(top_colleges_h2)
        
#         # Get description paragraph
#         top_colleges_desc = top_colleges_h2.find_next("p")
#         if top_colleges_desc:
#             data["top_colleges_description"] = clean(top_colleges_desc)
        
#         # Top MBBS Colleges
#         mbbs_colleges_h3 = soup.find("h3", id="chp_comparison_cp_toc_5_0")
#         if mbbs_colleges_h3:
#             data["mbbs_colleges_subheading"] = clean(mbbs_colleges_h3)
            
#             # Get description paragraph
#             mbbs_desc = mbbs_colleges_h3.find_next("p")
#             if mbbs_desc:
#                 data["mbbs_colleges_description"] = clean(mbbs_desc)
            
#             # Get MBBS colleges table
#             mbbs_table = mbbs_colleges_h3.find_next("table")
#             if mbbs_table:
#                 mbbs_colleges_data = []
#                 rows = mbbs_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         college_link = cols[0].find("a")
#                         mbbs_colleges_data.append({
#                             "college": clean(cols[0]),
#                             "fees": clean(cols[1]),
#                             "link": college_link.get("href") if college_link else None
#                         })
#                 data["mbbs_colleges_table"] = mbbs_colleges_data
            
#             # Get note
#             note_p = mbbs_table.find_next("p") if mbbs_table else None
#             if note_p and "Note -" in clean(note_p):
#                 data["mbbs_colleges_note"] = clean(note_p)
        
#         # Top MD Colleges
#         md_colleges_h3 = soup.find("h3", id="chp_comparison_cp_toc_5_1")
#         if md_colleges_h3:
#             data["md_colleges_subheading"] = clean(md_colleges_h3)
            
#             # Get description paragraph
#             md_desc = md_colleges_h3.find_next("p")
#             if md_desc:
#                 data["md_colleges_description"] = clean(md_desc)
            
#             # Get MD colleges table
#             md_table = md_colleges_h3.find_next("table")
#             if md_table:
#                 md_colleges_data = []
#                 rows = md_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         college_link = cols[0].find("a")
#                         md_colleges_data.append({
#                             "college": clean(cols[0]),
#                             "fees": clean(cols[1]),
#                             "link": college_link.get("href") if college_link else None
#                         })
#                 data["md_colleges_table"] = md_colleges_data
            
#             # Get note
#             note_p = md_table.find_next("p") if md_table else None
#             if note_p and "Note -" in clean(note_p):
#                 data["md_colleges_note"] = clean(note_p)
        
#         # Get helpful links
#         helpful_links_start = note_p.find_next("p") if note_p else None
#         if helpful_links_start and "color: #e03e2d" in str(helpful_links_start):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling("p")
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling("p")
            
#             data["colleges_helpful_links"] = helpful_links

#     # ===============================
#     # Jobs and Salary Section
#     jobs_salary_h2 = soup.find("h2", id="chp_comparison_cp_toc_6")
#     if jobs_salary_h2:
#         data["jobs_salary_heading"] = clean(jobs_salary_h2)
        
#         # Get description paragraph
#         jobs_desc = jobs_salary_h2.find_next("p")
#         if jobs_desc:
#             data["jobs_salary_description"] = clean(jobs_desc)
        
#         # MBBS Salary in India
#         mbbs_salary_h3 = soup.find("h3", id="chp_comparison_cp_toc_6_0")
#         if mbbs_salary_h3:
#             data["mbbs_salary_subheading"] = clean(mbbs_salary_h3)
            
#             # Get description paragraph
#             mbbs_salary_desc = mbbs_salary_h3.find_next("p")
#             if mbbs_salary_desc:
#                 data["mbbs_salary_description"] = clean(mbbs_salary_desc)
            
#             # Get MBBS salary table
#             mbbs_table = mbbs_salary_h3.find_next("table")
#             if mbbs_table:
#                 mbbs_salary_data = []
#                 rows = mbbs_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         mbbs_salary_data.append({
#                             "job_profile": clean(cols[0]),
#                             "salary": clean(cols[1])
#                         })
#                 data["mbbs_salary_table"] = mbbs_salary_data
            
#             # Get note
#             note_p = mbbs_table.find_next("p") if mbbs_table else None
#             if note_p and "Note:" in clean(note_p):
#                 data["mbbs_salary_note"] = clean(note_p)
            
#             # Get helpful links
#             helpful_links_start = note_p.find_next("p") if note_p else None
#             if helpful_links_start and "color: #e03e2d" in str(helpful_links_start):
#                 helpful_links = []
#                 next_p = helpful_links_start.find_next_sibling("p")
#                 while next_p and next_p.name == "p":
#                     a_tag = next_p.find("a")
#                     if a_tag:
#                         helpful_links.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
#                     next_p = next_p.find_next_sibling("p")
                
#                 data["mbbs_salary_helpful_links"] = helpful_links
        
#         # MD Salary in India
#         md_salary_h3 = soup.find("h3", id="chp_comparison_cp_toc_6_1")
#         if md_salary_h3:
#             data["md_salary_subheading"] = clean(md_salary_h3)
            
#             # Get description paragraph
#             md_salary_desc = md_salary_h3.find_next("p")
#             if md_salary_desc:
#                 data["md_salary_description"] = clean(md_salary_desc)
            
#             # Get MD salary table
#             md_table = md_salary_h3.find_next("table")
#             if md_table:
#                 md_salary_data = []
#                 rows = md_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         md_salary_data.append({
#                             "job_profile": clean(cols[0]),
#                             "salary": clean(cols[1])
#                         })
#                 data["md_salary_table"] = md_salary_data
            
#             # Get note
#             note_p = md_table.find_next("p") if md_table else None
#             if note_p and "Note:" in clean(note_p):
#                 data["md_salary_note"] = clean(note_p)
            
#             # Get helpful links
#             helpful_links_start = note_p.find_next("p") if note_p else None
#             if helpful_links_start and "color: #e03e2d" in str(helpful_links_start):
#                 helpful_links = []
#                 next_p = helpful_links_start.find_next_sibling("p")
#                 while next_p and next_p.name == "p":
#                     a_tag = next_p.find("a")
#                     if a_tag:
#                         helpful_links.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
#                     next_p = next_p.find_next_sibling("p")
                
#                 data["md_salary_helpful_links"] = helpful_links

#     return data

# def scrape_mbbs_vs_md(driver):
#     # Assuming URL is defined elsewhere
#     driver.get(MD_VS_MBBS)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     try:
#         author_elem = WebDriverWait(driver, 15).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
#             )
#         )
#     except:
#         print("Author info not found in time.")
#         author_elem = None

#     data = {}

#     # ---------- Course Name ----------
#     try:
#         course_name_elem = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.flx-box.mA h1")
#             )
#         )
#         data["title"] = course_name_elem.text.strip()
#     except:
#         data["title"] = None

#     # ---------- Updated Date ----------
#     try:
#         updated_elem = driver.find_element(
#             By.CSS_SELECTOR, "div.adp_blog div.blogdata_user span"
#         )
#         data["updated_on"] = updated_elem.text.strip()
#     except:
#         data["updated_on"] = None

#     # ---------- Author Info ----------
#     data["author"] = None
#     if author_elem:
#         author_data = {}

#         # Profile & image
#         try:
#             img_link = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user a.user-img"
#             )
#             author_data["profile"] = img_link.get_attribute("href")
#             img_tag = img_link.find_element(By.TAG_NAME, "img")
#             author_data["image"] = img_tag.get_attribute("src")
#         except:
#             author_data["profile"] = None
#             author_data["image"] = None

#         # Name
#         author_data["name"] = author_elem.text.strip()

#         # Verified
#         try:
#             tick_icon = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user i.tickIcon"
#             )
#             author_data["verified"] = True
#         except:
#             author_data["verified"] = False

#         # Role
#         try:
#             role_elem = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user div.user_expert_level"
#             )
#             author_data["role"] = role_elem.text.strip()
#         except:
#             author_data["role"] = None

#         data["author"] = author_data

#     # ===============================

#     # Overview Section
#     overview_div = soup.find("div", id="blogId-132969")
#     if overview_div:
#         # Get overview paragraphs
#         overview_sections = overview_div.find_all("div", id=lambda x: x and "wikkiContents_multi_ADP_undefined_ua_" in x)
        
#         if overview_sections and len(overview_sections) > 0:
#             overview_text = []
#             for section in overview_sections[:3]:  # First 3 overview sections
#                 paragraphs = section.find_all("p")
#                 for p in paragraphs:
#                     text = clean(p)
#                     if text:
#                         overview_text.append(text)
            
#             data["overview_text"] = overview_text

#     # ===============================
#     # FAQs Section
#     faq_section = soup.find("div", id="sectional-faqs-0")
#     if faq_section:
#         faqs = []
#         question_divs = faq_section.find_all("div", id=lambda x: x and "0::" in x)
        
#         for q_div in question_divs:
#             question_text = clean(q_div)
#             if question_text.startswith("Q:"):
#                 question_text = question_text.replace("Q:", "").strip()
            
#             # Get answer
#             answer_div = q_div.find_next("div", class_="_16f53f")
#             if answer_div:
#                 answer_content = answer_div.find("div", class_="cmsAContent")
#                 if answer_content:
#                     answer_text = clean(answer_content)
#                     if answer_text.startswith("A:"):
#                         answer_text = answer_text.replace("A:", "").strip()
                    
#                     faqs.append({
#                         "question": question_text,
#                         "answer": answer_text
#                     })
        
#         data["faqs"] = faqs

#     # ===============================
#     # Table of Contents
#     toc_div = soup.find("div", class_="_078b")
#     if toc_div:
#         toc_items = []
#         toc_list = toc_div.find("ul", id="tocWrapper")
#         if toc_list:
#             for li in toc_list.find_all("li"):
#                 toc_items.append(clean(li))
        
#         data["table_of_contents"] = toc_items

#     # ===============================
#     # MD vs MBBS: Highlights Section
#     highlights_h2 = soup.find("h2", id="toc_section_1")
#     if highlights_h2:
#         data["highlights_heading"] = clean(highlights_h2)
        
#         # Get description paragraph
#         highlights_desc = highlights_h2.find_next("p")
#         if highlights_desc:
#             data["highlights_description"] = clean(highlights_desc)
        
#         # Get highlights table
#         table = highlights_h2.find_next("table")
#         if table:
#             highlights_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     highlights_data.append({
#                         "parameter": clean(cols[0]),
#                         "mbbs": clean(cols[1]),
#                         "md": clean(cols[2])
#                     })
#             data["highlights_table"] = highlights_data
        
#         # Get note paragraph
#         note_p = table.find_next("p")
#         if note_p and "Note:" in note_p.get_text():
#             data["highlights_note"] = clean(note_p)
        
#         # Get helpful links after table
#         helpful_links_start = note_p.find_next("p") if note_p else table.find_next("p")
#         if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["highlights_helpful_links"] = helpful_links

#     # ===============================
#     # Difference Between MD vs MBBS Section
#     difference_h2 = soup.find("h2", id="toc_section_2")
#     if difference_h2:
#         data["difference_heading"] = clean(difference_h2)
        
#         # What is MBBS?
#         mbbs_heading = difference_h2.find_next("p", string=lambda x: x and "What is MBBS?" in x)
#         if mbbs_heading:
#             data["mbbs_definition_heading"] = clean(mbbs_heading)
#             mbbs_desc = mbbs_heading.find_next("p")
#             if mbbs_desc:
#                 data["mbbs_definition"] = clean(mbbs_desc)
                
#                 # What is MD?
#                 md_heading = mbbs_desc.find_next("p")
#                 if md_heading and "What is MD?" in md_heading.get_text():
#                     data["md_definition_heading"] = clean(md_heading)
#                     md_desc = md_heading.find_next("p")
#                     if md_desc:
#                         data["md_definition"] = clean(md_desc)
                        
#                         # Get additional paragraphs about MD
#                         additional_md_para = md_desc.find_next("p")
#                         if additional_md_para:
#                             data["md_additional_info"] = clean(additional_md_para)
                        
#                         # Get suggested readings
#                         suggested_readings_start = additional_md_para.find_next("p") if additional_md_para else None
#                         if suggested_readings_start and suggested_readings_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#                             suggested_readings = []
#                             next_p = suggested_readings_start.find_next_sibling()
#                             while next_p and next_p.name == "p":
#                                 a_tag = next_p.find("a")
#                                 if a_tag:
#                                     suggested_readings.append({
#                                         "title": clean(a_tag),
#                                         "url": a_tag.get("href")
#                                     })
#                                 next_p = next_p.find_next_sibling()
                            
#                             data["difference_suggested_readings"] = suggested_readings

#     # ===============================
#     # MD vs MBBS: Eligibility Section
#     eligibility_h2 = soup.find("h2", id="toc_section_3")
#     if eligibility_h2:
#         data["eligibility_heading"] = clean(eligibility_h2)
        
#         # Get description paragraphs
#         desc_para1 = eligibility_h2.find_next("p")
#         if desc_para1:
#             data["eligibility_description1"] = clean(desc_para1)
        
#         desc_para2 = desc_para1.find_next("p") if desc_para1 else None
#         if desc_para2:
#             data["eligibility_description2"] = clean(desc_para2)
        
#         # Get eligibility table
#         table = eligibility_h2.find_next("table")
#         if table:
#             eligibility_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     eligibility_data.append({
#                         "parameter": clean(cols[0]),
#                         "mbbs": clean(cols[1]),
#                         "md": clean(cols[2])
#                     })
#             data["eligibility_table"] = eligibility_data
        
#         # Get note paragraph
#         note_p = table.find_next("p")
#         if note_p and "Note:" in note_p.get_text():
#             data["eligibility_note"] = clean(note_p)
        
#         # Get helpful links
#         helpful_links_start = note_p.find_next("p") if note_p else table.find_next("p")
#         if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["eligibility_helpful_links"] = helpful_links

#     # ===============================
#     # MD vs MBBS: Entrance Exam Section
#     entrance_h2 = soup.find("h2", id="toc_section_4")
#     if entrance_h2:
#         data["entrance_exam_heading"] = clean(entrance_h2)
        
#         # Get description paragraph
#         entrance_desc = entrance_h2.find_next("p")
#         if entrance_desc:
#             data["entrance_exam_description"] = clean(entrance_desc)
        
#         # Get entrance exam table
#         table = entrance_h2.find_next("table")
#         if table:
#             entrance_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     entrance_data.append({
#                         "particular": clean(cols[0]),
#                         "mbbs": clean(cols[1]),
#                         "md": clean(cols[2])
#                     })
#             data["entrance_exam_table"] = entrance_data
        
#         # Get note paragraph
#         note_p = table.find_next("p")
#         if note_p and "Note:" in note_p.get_text():
#             data["entrance_exam_note"] = clean(note_p)
        
#         # Get helpful links
#         helpful_links_start = note_p.find_next("p") if note_p else table.find_next("p")
#         if helpful_links_start and helpful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#             helpful_links = []
#             next_p = helpful_links_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     helpful_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["entrance_exam_helpful_links"] = helpful_links

#     # ===============================
#     # MD vs MBBS: Syllabus Section
#     syllabus_h2 = soup.find("h2", id="toc_section_5")
#     if syllabus_h2:
#         data["syllabus_heading"] = clean(syllabus_h2)
        
#         # Get description paragraphs
#         desc_para1 = syllabus_h2.find_next("p")
#         if desc_para1:
#             data["syllabus_description1"] = clean(desc_para1)
        
#         desc_para2 = desc_para1.find_next("p") if desc_para1 else None
#         if desc_para2:
#             data["syllabus_description2"] = clean(desc_para2)
        
#         desc_para3 = desc_para2.find_next("p") if desc_para2 else None
#         if desc_para3:
#             data["syllabus_description3"] = clean(desc_para3)
        
#         # Get syllabus table
#         table = syllabus_h2.find_next("table")
#         if table:
#             syllabus_data = []
#             rows = table.find_all("tr")
#             for row in rows[1:]:  # Skip header
#                 cols = row.find_all("td")
#                 if len(cols) >= 3:
#                     # Extract list items from MBBS and MD columns
#                     mbbs_items = []
#                     md_items = []
                    
#                     mbbs_ul = cols[1].find("ul")
#                     if mbbs_ul:
#                         for li in mbbs_ul.find_all("li"):
#                             mbbs_items.append(clean(li))
                    
#                     md_ul = cols[2].find("ul")
#                     if md_ul:
#                         for li in md_ul.find_all("li"):
#                             md_items.append(clean(li))
                    
#                     syllabus_data.append({
#                         "semester": clean(cols[0]),
#                         "mbbs_subjects": mbbs_items,
#                         "md_subjects": md_items
#                     })
#             data["syllabus_table"] = syllabus_data
        
#         # Get syllabus links
#         syllabus_links_p = table.find_next("p")
#         if syllabus_links_p:
#             syllabus_links = []
#             a_tags = syllabus_links_p.find_all("a")
#             for a_tag in a_tags:
#                 syllabus_links.append({
#                     "title": clean(a_tag),
#                     "url": a_tag.get("href")
#                 })
#             data["syllabus_links"] = syllabus_links
        
#         # Get relevant links
#         relevant_links_start = syllabus_links_p.find_next("p") if syllabus_links_p else table.find_next("p")
#         if relevant_links_start and relevant_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#             relevant_links = []
#             next_p = relevant_links_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     relevant_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             data["syllabus_relevant_links"] = relevant_links

#     # ===============================
#     # MD vs MBBS: Top Colleges Section
#     top_colleges_h2 = soup.find("h2", id="toc_section_6")
#     if top_colleges_h2:
#         data["top_colleges_heading"] = clean(top_colleges_h2)
        
#         # Get description paragraph
#         desc_para = top_colleges_h2.find_next("p")
#         if desc_para:
#             data["top_colleges_description"] = clean(desc_para)
        
#         # Top MBBS Colleges Subsection
#         mbbs_colleges_h3 = soup.find("h3", string=lambda x: x and "Top MBBS Colleges" in x)
#         if mbbs_colleges_h3:
#             data["mbbs_colleges_subheading"] = clean(mbbs_colleges_h3)
            
#             # Get description
#             mbbs_desc = mbbs_colleges_h3.find_next("p")
#             if mbbs_desc:
#                 data["mbbs_colleges_description"] = clean(mbbs_desc)
            
#             # Get MBBS colleges table
#             mbbs_table = mbbs_colleges_h3.find_next("table")
#             if mbbs_table:
#                 mbbs_colleges_data = []
#                 rows = mbbs_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         college_link = cols[0].find("a")
#                         mbbs_colleges_data.append({
#                             "college": clean(cols[0]),
#                             "fees": clean(cols[1]),
#                             "link": college_link.get("href") if college_link else None
#                         })
#                 data["mbbs_colleges_table"] = mbbs_colleges_data
            
#             # Get note paragraph
#             note_p = mbbs_table.find_next("p")
#             if note_p and "Note:" in note_p.get_text():
#                 data["mbbs_colleges_note"] = clean(note_p)
        
#         # Top MD Colleges Subsection
#         md_colleges_h3 = soup.find("h3", string=lambda x: x and "Top MD Colleges" in x)
#         if md_colleges_h3:
#             data["md_colleges_subheading"] = clean(md_colleges_h3)
            
#             # Get description
#             md_desc = md_colleges_h3.find_next("p")
#             if md_desc:
#                 data["md_colleges_description"] = clean(md_desc)
            
#             # Get MD colleges table
#             md_table = md_colleges_h3.find_next("table")
#             if md_table:
#                 md_colleges_data = []
#                 rows = md_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         college_link = cols[0].find("a")
#                         md_colleges_data.append({
#                             "college": clean(cols[0]),
#                             "fees": clean(cols[1]),
#                             "link": college_link.get("href") if college_link else None
#                         })
#                 data["md_colleges_table"] = md_colleges_data
            
#             # Get note paragraph
#             note_p = md_table.find_next("p")
#             if note_p and "Note:" in note_p.get_text():
#                 data["md_colleges_note"] = clean(note_p)
            
#             # Get useful links
#             useful_links_start = note_p.find_next("p") if note_p else md_table.find_next("p")
#             if useful_links_start and useful_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#                 useful_links = []
#                 next_p = useful_links_start.find_next_sibling()
#                 while next_p and next_p.name == "p":
#                     a_tag = next_p.find("a")
#                     if a_tag:
#                         useful_links.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
#                     next_p = next_p.find_next_sibling()
                
#                 data["colleges_useful_links"] = useful_links

#     # ===============================
#     # MD vs MBBS: Jobs and Salary Section
#     jobs_h2 = soup.find("h2", id="toc_section_7")
#     if jobs_h2:
#         data["jobs_salary_heading"] = clean(jobs_h2)
        
#         # Get description paragraph
#         jobs_desc = jobs_h2.find_next("p")
#         if jobs_desc:
#             data["jobs_salary_description"] = clean(jobs_desc)
        
#         # MBBS Salary in India Subsection
#         mbbs_salary_h3 = soup.find("h3", string=lambda x: x and "MBBS Salary in India" in x)
#         if mbbs_salary_h3:
#             data["mbbs_salary_subheading"] = clean(mbbs_salary_h3)
            
#             # Get description
#             mbbs_salary_desc = mbbs_salary_h3.find_next("p")
#             if mbbs_salary_desc:
#                 data["mbbs_salary_description"] = clean(mbbs_salary_desc)
            
#             # Get MBBS salary table
#             mbbs_salary_table = mbbs_salary_h3.find_next("table")
#             if mbbs_salary_table:
#                 mbbs_salary_data = []
#                 rows = mbbs_salary_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         mbbs_salary_data.append({
#                             "job_profile": clean(cols[0]),
#                             "salary": clean(cols[1])
#                         })
#                 data["mbbs_salary_table"] = mbbs_salary_data
            
#             # Get note paragraph
#             note_p = mbbs_salary_table.find_next("p")
#             if note_p and "Note:" in note_p.get_text():
#                 data["mbbs_salary_note"] = clean(note_p)
            
#             # Get recommended links
#             recommended_links_start = note_p.find_next("p") if note_p else mbbs_salary_table.find_next("p")
#             if recommended_links_start and recommended_links_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#                 recommended_links = []
#                 next_p = recommended_links_start.find_next_sibling()
#                 while next_p and next_p.name == "p":
#                     a_tag = next_p.find("a")
#                     if a_tag:
#                         recommended_links.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
#                     next_p = next_p.find_next_sibling()
                
#                 data["mbbs_salary_recommended_links"] = recommended_links
        
#         # MD Salary in India Subsection
#         md_salary_h3 = soup.find("h3", string=lambda x: x and "MD Salary in India" in x)
#         if md_salary_h3:
#             data["md_salary_subheading"] = clean(md_salary_h3)
            
#             # Get description
#             md_salary_desc = md_salary_h3.find_next("p")
#             if md_salary_desc:
#                 data["md_salary_description"] = clean(md_salary_desc)
            
#             # Get MD salary table
#             md_salary_table = md_salary_h3.find_next("table")
#             if md_salary_table:
#                 md_salary_data = []
#                 rows = md_salary_table.find_all("tr")
#                 for row in rows[1:]:  # Skip header
#                     cols = row.find_all("td")
#                     if len(cols) >= 2:
#                         md_salary_data.append({
#                             "job_profile": clean(cols[0]),
#                             "salary": clean(cols[1])
#                         })
#                 data["md_salary_table"] = md_salary_data
            
#             # Get note paragraph
#             note_p = md_salary_table.find_next("p")
#             if note_p and "Note:" in note_p.get_text():
#                 data["md_salary_note"] = clean(note_p)
            
#             # Get suggested reading
#             suggested_reading_start = note_p.find_next("p") if note_p else md_salary_table.find_next("p")
#             if suggested_reading_start and suggested_reading_start.find("span", style=lambda x: x and "color: rgb(224, 62, 45)" in x):
#                 suggested_reading = []
#                 next_p = suggested_reading_start.find_next_sibling()
#                 while next_p and next_p.name == "p":
#                     a_tag = next_p.find("a")
#                     if a_tag:
#                         suggested_reading.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
#                     next_p = next_p.find_next_sibling()
                
#                 data["md_salary_suggested_reading"] = suggested_reading

#     # ===============================
#     # MD vs MBBS FAQs Section
#     faqs_h2 = soup.find("h2", id="toc_section_8")
#     if faqs_h2:
#         data["faqs_section_heading"] = clean(faqs_h2)
        
#         # Get all FAQ questions and answers
#         faq_wrapper = soup.find("div", id="faqWrapper_last")
#         if faq_wrapper:
#             detailed_faqs = []
#             question_paragraphs = faq_wrapper.find_all("p", class_="fQ")
            
#             for q_p in question_paragraphs:
#                 question_text = clean(q_p)
#                 if question_text.startswith("Q."):
#                     question_text = question_text.replace("Q.", "").strip()
                
#                 # Find answer
#                 answer_div = q_p.find_next("div", class_="fA")
#                 if answer_div:
#                     answer_text = clean(answer_div)
                    
#                     detailed_faqs.append({
#                         "question": question_text,
#                         "answer": answer_text
#                     })
            
#             data["detailed_faqs"] = detailed_faqs

#     # ===============================
#     # Explore More Exams Section
#     exams_section = soup.find("div", id="ADP_Exam_recoWidget_undefined")
#     if exams_section:
#         exams_heading = exams_section.find("h2", class_="heading")
#         if exams_heading:
#             data["exams_heading"] = clean(exams_heading)
        
#         # Get exam sliders
#         exam_sliders = exams_section.find_all("div", class_="examSlider")
#         if exam_sliders:
#             exams_list = []
#             for slider in exam_sliders:
#                 exam_name_div = slider.find("h2", class_="_2164")
#                 if exam_name_div:
#                     exam_name = clean(exam_name_div)
                    
#                     # Get exam dates
#                     date_div = slider.find("div", class_="_760f")
#                     exam_date = ""
#                     if date_div:
#                         strong_tag = date_div.find("strong")
#                         if strong_tag:
#                             exam_date = clean(strong_tag)
                    
#                     # Get exam links
#                     links = []
#                     link_items = slider.find_all("li")
#                     for li in link_items:
#                         a_tag = li.find("a")
#                         if a_tag:
#                             links.append({
#                                 "title": clean(a_tag),
#                                 "url": a_tag.get("href")
#                             })
                    
#                     exams_list.append({
#                         "exam_name": exam_name,
#                         "date": exam_date,
#                         "links": links
#                     })
            
#             data["explore_exams"] = exams_list

#     # ===============================
#     # Videos Section
#     videos_section = soup.find("div", id="reelsWidget")
#     if videos_section:
#         videos_heading = videos_section.find("strong", class_="b5e4")
#         if videos_heading:
#             data["videos_heading"] = clean(videos_heading)
        
#         # Get video thumbnails
#         video_items = videos_section.find_all("li", class_="_7c2b")
#         if video_items:
#             videos_list = []
#             for video in video_items:
#                 img_tag = video.find("img", class_="_97edf4")
#                 if img_tag:
#                     video_title_div = video.find("div", class_="_4a7330")
#                     video_title = clean(video_title_div) if video_title_div else ""
                    
#                     videos_list.append({
#                         "thumbnail": img_tag.get("src", ""),
#                         "title": video_title
#                     })
            
#             data["videos"] = videos_list

#     return data

# def scrape_aiims_data(driver):
#     driver.get(AIIMS_IN_INDIA)
#     soup = BeautifulSoup(driver.page_source,"html.parser")
#     try:
#         author_elem = WebDriverWait(driver, 15).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
#             )
#         )
#     except:
#         print("Author info not found in time.")
#         author_elem = None

#     data = {}

#     # ---------- Course Name ----------
#     try:
#         course_name_elem = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.flx-box.mA h1")
#             )
#         )
#         data["title"] = course_name_elem.text.strip()
#     except:
#         data["title"] = None

#     # ---------- Updated Date ----------
#     try:
#         updated_elem = driver.find_element(
#             By.CSS_SELECTOR, "div.adp_blog div.blogdata_user span"
#         )
#         data["updated_on"] = updated_elem.text.strip()
#     except:
#         data["updated_on"] = None

#     # ---------- Author Info ----------
#     data["author"] = None
#     if author_elem:
#         author_data = {}

#         # Profile & image
#         try:
#             img_link = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user a.user-img"
#             )
#             author_data["profile"] = img_link.get_attribute("href")
#             img_tag = img_link.find_element(By.TAG_NAME, "img")
#             author_data["image"] = img_tag.get_attribute("src")
#         except:
#             author_data["profile"] = None
#             author_data["image"] = None

#         # Name
#         author_data["name"] = author_elem.text.strip()

#         # Verified
#         try:
#             tick_icon = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user i.tickIcon"
#             )
#             author_data["verified"] = True
#         except:
#             author_data["verified"] = False

#         # Role
#         try:
#             role_elem = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user div.user_expert_level"
#             )
#             author_data["role"] = role_elem.text.strip()
#         except:
#             author_data["role"] = None

#         data["author"] = author_data
#     # ===============================
#     # Blog Summary Section
#     summary_div = soup.find("div", id="blogSummary")
#     if summary_div:
#         data["blog_summary"] = clean(summary_div)

#     # ===============================
#     # Main Content Section
#     main_content = soup.find("div", id="blogId-23925")
#     if main_content:
#         content_data = {}
        
#         # Introduction paragraph
#         intro_p = main_content.find("p")
#         if intro_p:
#             content_data["introduction"] = clean(intro_p)
        
#         # Featured image
#         img_caption = main_content.find("p", class_="_img-caption")
#         if img_caption:
#             content_data["featured_image_caption"] = clean(img_caption)
        
#         # Main description paragraphs
#         wikki_contents = main_content.find_all("div", class_="wikkiContents")
#         description_paragraphs = []
#         for wc in wikki_contents[:3]:  # Get first 3 content sections
#             paragraphs = wc.find_all("p")
#             for p in paragraphs:
#                 text = clean(p)
#                 if text and len(text) > 50:  # Filter out very short paragraphs
#                     description_paragraphs.append(text)
        
#         content_data["description_paragraphs"] = description_paragraphs
        
#         data["main_content"] = content_data

#     # ===============================
#     # FAQs Section
#     faq_section = soup.find("div", id="sectional-faqs-0")
#     if faq_section:
#         faqs = []
#         question_divs = faq_section.find_all("div", id=lambda x: x and "0::" in x)
        
#         for q_div in question_divs:
#             question_text = clean(q_div)
#             if question_text.startswith("Q:"):
#                 question_text = question_text.replace("Q:", "").strip()
            
#             # Get answer
#             answer_div = q_div.find_next("div", class_="_16f53f")
#             if answer_div:
#                 answer_content = answer_div.find("div", class_="cmsAContent")
#                 if answer_content:
#                     answer_text = clean(answer_content)
#                     if answer_text.startswith("A:"):
#                         answer_text = answer_text.replace("A:", "").strip()
                    
#                     faqs.append({
#                         "question": question_text,
#                         "answer": answer_text
#                     })
        
#         data["faqs"] = faqs

#     # ===============================
#     # Table of Contents
#     toc_div = soup.find("div", class_="_078b")
#     if toc_div:
#         toc_data = {}
        
#         toc_heading = toc_div.find("div")
#         if toc_heading:
#             toc_data["heading"] = clean(toc_heading)
        
#         toc_items = []
#         toc_list = toc_div.find("ul", id="tocWrapper")
#         if toc_list:
#             for li in toc_list.find_all("li"):
#                 item_data = {
#                     "text": clean(li),
#                     "section_id": li.get("data-scrol", "")
#                 }
#                 toc_items.append(item_data)
        
#         toc_data["items"] = toc_items
#         data["table_of_contents"] = toc_data

#     # ===============================
#     # NIRF Ranking 2025 Section
#     nirf_h2 = soup.find("h2", id="toc_section_1")
#     if nirf_h2:
#         nirf_data = {}
#         nirf_data["heading"] = clean(nirf_h2)
        
#         # Get description paragraphs
#         paragraphs = []
#         next_elem = nirf_h2.find_next_sibling()
#         while next_elem and next_elem.name == "p":
#             paragraphs.append(clean(next_elem))
#             next_elem = next_elem.find_next_sibling()
        
#         nirf_data["description"] = paragraphs
        
#         # Get related links
#         links_start = None
#         for p in paragraphs:
#             if "Also Read:" in p or "Read More:" in p:
#                 links_start = p
#                 break
        
#         if links_start:
#             related_links = []
#             next_p = links_start.find_next_sibling()
#             while next_p and next_p.name == "p":
#                 a_tag = next_p.find("a")
#                 if a_tag:
#                     related_links.append({
#                         "title": clean(a_tag),
#                         "url": a_tag.get("href")
#                     })
#                 next_p = next_p.find_next_sibling()
            
#             nirf_data["related_links"] = related_links
        
#         data["nirf_ranking_2025"] = nirf_data

#     # ===============================
#     # List of AIIMS in India Section
#     aiims_list_h2 = soup.find("h2", id="toc_section_2")
#     if aiims_list_h2:
#         aiims_list_data = {}
#         aiims_list_data["heading"] = clean(aiims_list_h2)
        
#         # Get description paragraph
#         desc_p = aiims_list_h2.find_next("p")
#         if desc_p:
#             aiims_list_data["description"] = clean(desc_p)
        
#         # Get AIIMS table
#         table = aiims_list_h2.find_next("table")
#         if table:
#             aiims_data = []
#             rows = table.find_all("tr")
            
#             # Extract headers
#             headers = []
#             if rows:
#                 header_row = rows[0]
#                 th_cells = header_row.find_all("th")
#                 for th in th_cells:
#                     headers.append(clean(th))
            
#             # Extract data rows
#             for row in rows[1:]:
#                 cells = row.find_all("td")
#                 if len(cells) >= 5:  # Ensure we have all 5 columns
#                     aiims_info = {
#                         "name": clean(cells[0]),
#                         "establishment_year": clean(cells[1]),
#                         "nirf_2025_rank": clean(cells[2]),
#                         "nirf_2024_rank": clean(cells[3]),
#                         "nirf_2023_rank": clean(cells[4])
#                     }
                    
#                     # Extract link if available
#                     name_link = cells[0].find("a")
#                     if name_link:
#                         aiims_info["link"] = name_link.get("href")
                    
#                     aiims_data.append(aiims_info)
            
#             aiims_list_data["table_headers"] = headers
#             aiims_list_data["aiims_list"] = aiims_data
        
#         # Get analysis after table
#         analysis_div = table.find_next("div")
#         if analysis_div:
#             aiims_list_data["analysis"] = clean(analysis_div)
        
#         # Get related links
#         related_links_start = analysis_div.find_next("div") if analysis_div else table.find_next("div")
#         if related_links_start:
#             related_links = []
#             ul_tag = related_links_start.find("ul")
#             if ul_tag:
#                 li_tags = ul_tag.find_all("li")
#                 for li in li_tags:
#                     a_tag = li.find("a")
#                     if a_tag:
#                         related_links.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
            
#             aiims_list_data["related_links"] = related_links
        
#         data["aiims_list_india"] = aiims_list_data

#     # ===============================
#     # Under-development AIIMS Section
#     under_dev_h2 = soup.find("h2", id="toc_section_3")
#     if under_dev_h2:
#         under_dev_data = {}
#         under_dev_data["heading"] = clean(under_dev_h2)
        
#         # Get description paragraph
#         desc_p = under_dev_h2.find_next("p")
#         if desc_p:
#             under_dev_data["description"] = clean(desc_p)
        
#         # Get under-development table
#         table = under_dev_h2.find_next("table")
#         if table:
#             under_dev_list = []
#             rows = table.find_all("tr")
            
#             # Extract headers
#             headers = []
#             if rows:
#                 header_row = rows[0]
#                 th_cells = header_row.find_all("th")
#                 for th in th_cells:
#                     headers.append(clean(th))
            
#             # Extract data rows
#             for row in rows[1:]:
#                 cells = row.find_all("td")
#                 if len(cells) >= 3:
#                     under_dev_info = {
#                         "name": clean(cells[0]),
#                         "state": clean(cells[1]),
#                         "status": clean(cells[2])
#                     }
#                     under_dev_list.append(under_dev_info)
            
#             under_dev_data["table_headers"] = headers
#             under_dev_data["under_development_list"] = under_dev_list
        
#         # Get related links
#         related_links_p = table.find_next("p")
#         if related_links_p:
#             a_tag = related_links_p.find("a")
#             if a_tag:
#                 under_dev_data["related_link"] = {
#                     "title": clean(a_tag),
#                     "url": a_tag.get("href")
#                 }
        
#         data["under_development_aiims"] = under_dev_data

#     # ===============================
#     # Courses Offered Section
#     courses_h2 = soup.find("h2", id="toc_section_4")
#     if courses_h2:
#         courses_data = {}
#         courses_data["heading"] = clean(courses_h2)
        
#         # Get description paragraph
#         desc_p = courses_h2.find_next("p")
#         if desc_p:
#             courses_data["description"] = clean(desc_p)
        
#         # Get courses table
#         table = courses_h2.find_next("table")
#         if table:
#             courses_list = []
#             rows = table.find_all("tr")
            
#             # Extract data rows
#             for row in rows:
#                 cells = row.find_all(["th", "td"])
#                 if len(cells) >= 3:
#                     course_info = {
#                         "undergraduate": clean(cells[0]),
#                         "postgraduate": clean(cells[1]),
#                         "super_specialization": clean(cells[2])
#                     }
#                     courses_list.append(course_info)
            
#             courses_data["courses_table"] = courses_list
        
#         # Get related links
#         related_links_p = table.find_next("p")
#         if related_links_p:
#             a_tag = related_links_p.find("a")
#             if a_tag:
#                 courses_data["related_link"] = {
#                     "title": clean(a_tag),
#                     "url": a_tag.get("href")
#                 }
        
#         data["courses_offered"] = courses_data

#     # ===============================
#     # Admission Process Section
#     admission_h2 = soup.find("h2", id="toc_section_5")
#     if admission_h2:
#         admission_data = {}
#         admission_data["heading"] = clean(admission_h2)
        
#         # Get description paragraph
#         desc_p = admission_h2.find_next("p")
#         if desc_p:
#             admission_data["description"] = clean(desc_p)
        
#         # Get admission table
#         table = admission_h2.find_next("table")
#         if table:
#             admission_process = []
#             rows = table.find_all("tr")
            
#             # Extract headers
#             headers = []
#             if rows:
#                 header_row = rows[0]
#                 th_cells = header_row.find_all("th")
#                 for th in th_cells:
#                     headers.append(clean(th))
            
#             # Extract data rows
#             for row in rows[1:]:
#                 cells = row.find_all("td")
#                 if len(cells) >= 2:
#                     process_info = {
#                         "course": clean(cells[0]),
#                         "entrance_test": clean(cells[1])
#                     }
                    
#                     # Extract links if available
#                     course_links = cells[0].find_all("a")
#                     entrance_links = cells[1].find_all("a")
                    
#                     if course_links:
#                         process_info["course_links"] = [link.get("href") for link in course_links]
#                     if entrance_links:
#                         process_info["entrance_links"] = [link.get("href") for link in entrance_links]
                    
#                     admission_process.append(process_info)
            
#             admission_data["table_headers"] = headers
#             admission_data["admission_process"] = admission_process
        
#         data["admission_process"] = admission_data

#     # ===============================
#     # Fee Structure Section
#     fees_h2 = soup.find("h2", id="toc_section_6")
#     if fees_h2:
#         fees_data = {}
#         fees_data["heading"] = clean(fees_h2)
        
#         # Get description paragraph
#         desc_p = fees_h2.find_next("p")
#         if desc_p:
#             fees_data["description"] = clean(desc_p)
        
#         # Get fee structure table
#         table = fees_h2.find_next("table")
#         if table:
#             fee_structure = []
#             rows = table.find_all("tr")
            
#             # Extract data rows
#             current_aiims = ""
#             for row in rows:
#                 cells = row.find_all(["th", "td"])
                
#                 if len(cells) == 1:
#                     # This might be a rowspan row with just AIIMS name
#                     current_aiims = clean(cells[0])
#                 elif len(cells) >= 3:
#                     fee_info = {
#                         "aiims": current_aiims if current_aiims else clean(cells[0]),
#                         "course": clean(cells[1]) if len(cells) >= 3 else clean(cells[0]),
#                         "annual_fee": clean(cells[2]) if len(cells) >= 3 else clean(cells[1])
#                     }
                    
#                     # Extract links if available
#                     course_link = cells[1].find("a") if len(cells) >= 3 else cells[0].find("a")
#                     if course_link:
#                         fee_info["course_link"] = course_link.get("href")
                    
#                     fee_structure.append(fee_info)
            
#             fees_data["fee_structure"] = fee_structure
        
#         data["fee_structure"] = fees_data

#     # ===============================
#     # Seat Intake Section
#     seats_h2 = soup.find("h2", id="toc_section_7")
#     if seats_h2:
#         seats_data = {}
#         seats_data["heading"] = clean(seats_h2)
        
#         # Get description paragraph
#         desc_p = seats_h2.find_next("p")
#         if desc_p:
#             seats_data["description"] = clean(desc_p)
        
#         # Get seat intake table
#         table = seats_h2.find_next("table")
#         if table:
#             seat_intake = []
#             rows = table.find_all("tr")
            
#             # Extract headers
#             headers = []
#             if rows:
#                 header_row = rows[0]
#                 th_cells = header_row.find_all("th")
#                 for th in th_cells:
#                     headers.append(clean(th))
            
#             # Extract data rows
#             for row in rows[1:]:
#                 cells = row.find_all("td")
#                 if len(cells) >= 2:
#                     seat_info = {
#                         "institute": clean(cells[0]),
#                         "seats": clean(cells[1])
#                     }
#                     seat_intake.append(seat_info)
            
#             seats_data["table_headers"] = headers
#             seats_data["seat_intake"] = seat_intake
        
#         data["seat_intake"] = seats_data

#     # ===============================
#     # NEET Cutoff Section
#     cutoff_h2 = soup.find("h2", id="toc_section_8")
#     if cutoff_h2:
#         cutoff_data = {}
#         cutoff_data["heading"] = clean(cutoff_h2)
        
#         # Get description paragraph
#         desc_p = cutoff_h2.find_next("p")
#         if desc_p:
#             cutoff_data["description"] = clean(desc_p)
        
#         # Get cutoff table
#         table = cutoff_h2.find_next("table")
#         if table:
#             cutoff_info = []
#             rows = table.find_all("tr")
            
#             # Extract headers
#             headers = []
#             if rows:
#                 header_row = rows[0]
#                 th_cells = header_row.find_all("th")
#                 for th in th_cells:
#                     headers.append(clean(th))
            
#             # Extract data rows
#             for row in rows[1:]:
#                 cells = row.find_all("td")
#                 if len(cells) >= 2:
#                     cutoff_item = {
#                         "aiims_institute": clean(cells[0]),
#                         "neet_2024_cutoff_rank": clean(cells[1])
#                     }
#                     cutoff_info.append(cutoff_item)
            
#             cutoff_data["table_headers"] = headers
#             cutoff_data["cutoff_info"] = cutoff_info
        
#         # Get concluding paragraph
#         concl_p = table.find_next("p")
#         if concl_p:
#             cutoff_data["conclusion"] = clean(concl_p)
        
#         # Get related links
#         related_links_start = concl_p.find_next("p") if concl_p else table.find_next("p")
#         if related_links_start and ("Read More:" in related_links_start.get_text() or "Also Read:" in related_links_start.get_text()):
#             related_links = []
#             ul_tag = related_links_start.find_next("ul")
#             if ul_tag:
#                 li_tags = ul_tag.find_all("li")
#                 for li in li_tags:
#                     a_tag = li.find("a")
#                     if a_tag:
#                         related_links.append({
#                             "title": clean(a_tag),
#                             "url": a_tag.get("href")
#                         })
            
#             cutoff_data["related_links"] = related_links
        
#         data["neet_cutoff"] = cutoff_data

#     # ===============================
#     # Explore Exams Section
#     exams_section = soup.find("div", id="ADP_Exam_recoWidget_undefined")
#     if exams_section:
#         exams_data = {}
        
#         # Get heading
#         heading = exams_section.find("h2", class_="heading")
#         if heading:
#             exams_data["heading"] = clean(heading)
        
#         # Get exam sliders
#         exam_sliders = exams_section.find_all("div", class_="examSlider")
#         if exam_sliders:
#             exams_list = []
#             for slider in exam_sliders:
#                 exam_name_div = slider.find("h2", class_="_2164")
#                 if exam_name_div:
#                     exam_info = {
#                         "exam_name": clean(exam_name_div)
#                     }
                    
#                     # Get exam link
#                     exam_link = exam_name_div.find_parent("a")
#                     if exam_link:
#                         exam_info["exam_link"] = exam_link.get("href")
                    
#                     # Get exam date
#                     date_div = slider.find("div", class_="_760f")
#                     if date_div:
#                         strong_tag = date_div.find("strong")
#                         if strong_tag:
#                             exam_info["date_title"] = clean(strong_tag)
                        
#                         date_span = date_div.find("p", class_="c1c4")
#                         if date_span:
#                             exam_info["date"] = clean(date_span)
                    
#                     # Get quick links
#                     quick_links = []
#                     link_items = slider.find_all("li")
#                     for li in link_items:
#                         a_tag = li.find("a")
#                         if a_tag:
#                             quick_links.append({
#                                 "title": clean(a_tag),
#                                 "url": a_tag.get("href")
#                             })
                    
#                     exam_info["quick_links"] = quick_links
#                     exams_list.append(exam_info)
            
#             exams_data["exams"] = exams_list
        
#         data["explore_exams"] = exams_data

#     # ===============================
#     # Comments Section
#     comments_section = soup.find("div", id="multiTag_comments")
#     if comments_section:
#         comments_data = {}
        
#         # Get comments heading
#         heading_div = comments_section.find("h2", class_="askQry-titl")
#         if heading_div:
#             comments_data["heading"] = clean(heading_div)
#             # Get comment count
#             count_span = heading_div.find_next("p")
#             if count_span:
#                 comments_data["count"] = clean(count_span)
        
#         # Get individual comments
#         comment_divs = comments_section.find_all("div", class_="qstn-div")
#         if comment_divs:
#             comments_list = []
#             for comment_div in comment_divs:
#                 comment_info = {}
                
#                 # Get user info
#                 user_div = comment_div.find("div", class_="qstn-det")
#                 if user_div:
#                     user_link = user_div.find("a", class_="ana--comments_user")
#                     if user_link:
#                         # Check for user image or initial
#                         img_tag = user_link.find("img")
#                         if img_tag:
#                             comment_info["user_image"] = img_tag.get("src", "")
#                         else:
#                             initial_div = user_link.find("p", class_="user-initial")
#                             if initial_div:
#                                 comment_info["user_initial"] = clean(initial_div)
                        
#                         comment_info["user_profile"] = user_link.get("href", "")
                    
#                     # Get user details
#                     user_details = user_div.find("div", class_="ana--comments_userdtls")
#                     if user_details:
#                         name_link = user_details.find("a", class_="blackLink")
#                         if name_link:
#                             comment_info["user_name"] = clean(name_link)
                        
#                         time_p = user_details.find("p", class_="ana--comments_time")
#                         if time_p:
#                             comment_info["timestamp"] = clean(time_p)
                
#                 # Get comment text
#                 comment_content = comment_div.find("div", class_="ana--comments_q")
#                 if comment_content:
#                     text_div = comment_content.find("div", class_="commentContent")
#                     if text_div:
#                         comment_info["comment"] = clean(text_div)
                
#                 # Get replies
#                 replies_div = comment_div.find("div", class_="ana--comments_answercol")
#                 if replies_div:
#                     reply_divs = replies_div.find_all("div", class_="ana--comments_ans")
#                     if reply_divs:
#                         replies_list = []
#                         for reply_div in reply_divs:
#                             reply_info = {}
                            
#                             # Get reply user info
#                             reply_user_div = reply_div.find("div", class_="qstn-det")
#                             if reply_user_div:
#                                 reply_user_link = reply_user_div.find("a", class_="ana--comments_user")
#                                 if reply_user_link:
#                                     reply_initial = reply_user_link.find("p", class_="user-initial")
#                                     if reply_initial:
#                                         reply_info["user_initial"] = clean(reply_initial)
                                    
#                                     reply_info["user_profile"] = reply_user_link.get("href", "")
                                
#                                 # Get reply user details
#                                 reply_details = reply_user_div.find("div", class_="ana--comments_userdtls")
#                                 if reply_details:
#                                     reply_name = reply_details.find("a", class_="blackLink")
#                                     if reply_name:
#                                         reply_info["user_name"] = clean(reply_name)
                                    
#                                     reply_time = reply_details.find("p", class_="ana--comments_time")
#                                     if reply_time:
#                                         reply_info["timestamp"] = clean(reply_time)
                            
#                             # Get reply text
#                             reply_content = reply_div.find("div", class_="ana--comments_anscol")
#                             if reply_content:
#                                 reply_text = reply_content.find("div", class_="commentContent")
#                                 if reply_text:
#                                     reply_info["reply"] = clean(reply_text)
                            
#                             replies_list.append(reply_info)
                        
#                         comment_info["replies"] = replies_list
                
#                 comments_list.append(comment_info)
            
#             comments_data["comments"] = comments_list
        
#         data["comments"] = comments_data

#     # ===============================
#     # Download and Share Section
#     download_div = soup.find("div", class_="dnld-btn")
#     if download_div:
#         download_data = {}
        
#         download_text = download_div.find("p")
#         if download_text:
#             download_data["text"] = clean(download_text)
        
#         download_link = download_div.find("a", class_="button--orange")
#         if download_link:
#             download_data["button_text"] = clean(download_link)
#             download_data["action"] = download_link.get("href", "")
        
#         data["download_section"] = download_data

#     # ===============================
#     # Social Sharing Section
#     share_div = soup.find("div", class_="shareWidget-btm")
#     if share_div:
#         share_data = {}
        
#         share_text = share_div.find("span", class_="sharethis")
#         if share_text:
#             share_data["heading"] = clean(share_text)
        
#         # Get social media links
#         social_links = []
#         social_band = share_div.find("ul", class_="sharing-band-list")
#         if social_band:
#             li_tags = social_band.find_all("li")
#             for li in li_tags[1:]:  # Skip the first li which contains "Share this" text
#                 a_tag = li.find("a")
#                 if a_tag:
#                     platform_info = {
#                         "url": a_tag.get("href", ""),
#                         "aria_label": a_tag.get("aria-label", "")
#                     }
                    
#                     # Determine platform from icon class
#                     icon = a_tag.find("i")
#                     if icon:
#                         class_name = icon.get("class", "")
#                         if "facebook" in class_name:
#                             platform_info["platform"] = "facebook"
#                         elif "twitter" in class_name:
#                             platform_info["platform"] = "twitter"
#                         elif "linkedin" in class_name:
#                             platform_info["platform"] = "linkedin"
#                         elif "email" in class_name:
#                             platform_info["platform"] = "email"
                    
#                     social_links.append(platform_info)
        
#         share_data["social_links"] = social_links
#         data["social_sharing"] = share_data

#     # ===============================
#     # Feedback Section
#     feedback_div = soup.find("div", id="feedbackSection")
#     if feedback_div:
#         feedback_data = {}
        
#         # Get feedback image
#         feedback_img = feedback_div.find("img")
#         if feedback_img:
#             feedback_data["image_src"] = feedback_img.get("src", "")
        
#         # Get feedback heading
#         heading = feedback_div.find("h2", class_="so-widget-heading")
#         if heading:
#             feedback_data["heading"] = clean(heading)
        
#         # Get feedback text
#         text = feedback_div.find("p", class_="fdbkTxt")
#         if text:
#             feedback_data["text"] = clean(text)
        
#         # Get rating stars
#         rating_stars = feedback_div.find_all("span", class_="rating-icon-wrpr")
#         if rating_stars:
#             feedback_data["rating_stars"] = len(rating_stars)
        
#         data["feedback_section"] = feedback_data

#     return data

# def scrape_alternative_mbbs(driver):
   
#     # Get the page content
#     driver.get(MBBS_ALTERNATIVE)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
    
#     # Initialize data structure
#     data = {
#         "title": None,
#         "updated_on": None,
#         "author": None,
#         "description": "",
#         "useful_links": [],
#         "table_of_contents": [],
#         "sections": [],
#         "faqs": []
#     }
    
#     # ---------- Get Author Info using Selenium ----------
#     try:
#         author_elem = WebDriverWait(driver, 15).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.adp_blog div.adp_usr_dtls a")
#             )
#         )
#     except:
#         print("Author info not found in time.")
#         author_elem = None
    
#     # ---------- Course Name ----------
#     try:
#         course_name_elem = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "div.flx-box.mA h1")
#             )
#         )
#         data["title"] = course_name_elem.text.strip()
#     except:
#         data["title"] = None
    
#     # ---------- Updated Date ----------
#     try:
#         updated_elem = driver.find_element(
#             By.CSS_SELECTOR, "div.adp_blog div.blogdata_user span"
#         )
#         data["updated_on"] = updated_elem.text.strip()
#     except:
#         data["updated_on"] = None
    
#     # ---------- Author Info ----------
#     if author_elem:
#         author_data = {}

#         # Profile & image
#         try:
#             img_link = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user a.user-img"
#             )
#             author_data["profile"] = img_link.get_attribute("href")
#             img_tag = img_link.find_element(By.TAG_NAME, "img")
#             author_data["image"] = img_tag.get_attribute("src")
#         except:
#             author_data["profile"] = None
#             author_data["image"] = None

#         # Name
#         author_data["name"] = author_elem.text.strip()

#         # Verified
#         try:
#             tick_icon = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user i.tickIcon"
#             )
#             author_data["verified"] = True
#         except:
#             author_data["verified"] = False

#         # Role
#         try:
#             role_elem = driver.find_element(
#                 By.CSS_SELECTOR, "div.adp_blog div.adp_user div.user_expert_level"
#             )
#             author_data["role"] = role_elem.text.strip()
#         except:
#             author_data["role"] = None

#         data["author"] = author_data
#     else:
#         data["author"] = None
    
#     # ---------- Continue with BeautifulSoup scraping for content ----------
    
#     # 1️⃣ Course Description and Useful Links
#     desc_elem = soup.find(id="wikkiContents_multi_ADP_undefined_ua_0")
#     if desc_elem:
#         description_texts = []
#         for p in desc_elem.find_all("p"):
#             text = p.get_text(strip=True)
#             if text:
#                 description_texts.append(text)
#             for a in p.find_all("a", href=True):
#                 href = a["href"]
#                 if href not in data["useful_links"]:
#                     data["useful_links"].append(href)
#         data["description"] = "\n".join(description_texts)
    
#     # 2️⃣ Table of Contents
#     toc_items = soup.select("ul#tocWrapper li")
#     if toc_items:
#         data["table_of_contents"] = [li.get_text(strip=True) for li in toc_items]
    
#     # 3️⃣ Sections (h2 + content + tables)
#     # Get all wikkiContents divs
#     section_containers = soup.find_all("div", class_="wikkiContents")
    
#     for container in section_containers:
#         section_data = {}
        
#         # Check if it's a section with h2 (not FAQ section)
#         h2 = container.find("h2")
#         if h2 and h2.get("id", "").startswith("toc_section_"):
#             section_data["title"] = h2.get_text(strip=True)
            
#             # Get all content excluding the h2 itself
#             content_parts = []
            
#             # Get paragraphs after h2
#             for elem in container.find_all(["p", "div"]):
#                 # Skip the h2 element
#                 if elem.name == "h2":
#                     continue
                
#                 # Get text from paragraph
#                 if elem.name == "p":
#                     text = elem.get_text(strip=True)
#                     if text and not text.startswith("Useful Links:") and not text.startswith("Suggested readings:"):
#                         content_parts.append(text)
                
#                 # Get text from div (content divs)
#                 elif elem.name == "div" and not elem.get("class"):
#                     text = elem.get_text(strip=True)
#                     if text:
#                         content_parts.append(text)
            
#             section_data["content"] = "\n".join(content_parts)
            
#             # Extract tables in this section
#             tables_data = []
#             for table in container.find_all("table"):
#                 table_rows = []
#                 for row in table.find_all("tr"):
#                     cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
#                     if cells:
#                         table_rows.append(cells)
#                 if table_rows:
#                     tables_data.append(table_rows)
#             section_data["tables"] = tables_data
            
#             # Add suggested links if present
#             suggested_links = []
#             for p in container.find_all("p"):
#                 if "Suggested readings:" in p.get_text() or "Suggested Reading:" in p.get_text():
#                     for a in p.find_all("a", href=True):
#                         suggested_links.append(a["href"])
#             if suggested_links:
#                 section_data["suggested_links"] = suggested_links
            
#             data["sections"].append(section_data)
    
#     # 4️⃣ FAQ Section (special handling)
#     faq_section = soup.find("h2", id="toc_section_8")
#     if faq_section:
#         faq_container = faq_section.find_parent("div", class_="faqWrapper") or faq_section.find_parent("div", class_="wikkiContents")
        
#         if faq_container:
#             faq_data = {
#                 "title": faq_section.get_text(strip=True),
#                 "faqs": []
#             }
            
#             # Extract individual FAQ Q&A pairs
#             faq_questions = faq_container.find_all(class_="fQ")
            
#             for q in faq_questions:
#                 question_text = q.get_text(strip=True).replace("Q.", "").strip()
#                 question_id = q.find("strong").get("id", "") if q.find("strong") else ""
                
#                 # Find corresponding answer
#                 if question_id:
#                     answer_id = question_id.replace("faq_q", "faq_a")
#                     answer_div = faq_container.find("div", id=answer_id)
                    
#                     if answer_div:
#                         answer_content = []
#                         tables_data = []
                        
#                         # Extract text content
#                         for elem in answer_div.find_all(["p", "ul", "table"]):
#                             if elem.name == "p":
#                                 text = elem.get_text(strip=True)
#                                 if text and not text.startswith("A."):
#                                     answer_content.append(text)
#                             elif elem.name == "ul":
#                                 list_items = [li.get_text(strip=True) for li in elem.find_all("li")]
#                                 if list_items:
#                                     answer_content.append("\n".join([f"• {item}" for item in list_items]))
#                             elif elem.name == "table":
#                                 table_rows = []
#                                 for row in elem.find_all("tr"):
#                                     cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
#                                     if cells:
#                                         table_rows.append(cells)
#                                 if table_rows:
#                                     tables_data.append(table_rows)
                        
#                         faq_entry = {
#                             "question": question_text,
#                             "answer": "\n".join(answer_content),
#                             "tables": tables_data
#                         }
                        
#                         faq_data["faqs"].append(faq_entry)
            
#             data["sections"].append(faq_data)
    
#     # 5️⃣ Additional FAQs from other sections
#     sectional_faqs = soup.find("div", class_="sectional-faqs")
#     if sectional_faqs:
#         faq_listeners = sectional_faqs.find_all(class_="listener")
        
#         for i in range(0, len(faq_listeners), 2):
#             if i + 1 < len(faq_listeners):
#                 question_elem = faq_listeners[i]
#                 answer_elem = faq_listeners[i + 1]
                
#                 # Extract question
#                 question_spans = question_elem.find_all("span")
#                 question = question_spans[1].get_text(strip=True) if len(question_spans) > 1 else question_elem.get_text(strip=True).replace("Q:", "").strip()
                
#                 # Extract answer
#                 answer_content = answer_elem.find("div", class_="cmsAContent")
#                 if answer_content:
#                     answer_text = answer_content.get_text(strip=True).replace("A:", "").strip()
                    
#                     # Extract tables from answer
#                     tables_data = []
#                     for table in answer_content.find_all("table"):
#                         table_rows = []
#                         for row in table.find_all("tr"):
#                             cells = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
#                             if cells:
#                                 table_rows.append(cells)
#                         if table_rows:
#                             tables_data.append(table_rows)
                    
#                     data["faqs"].append({
#                         "question": question,
#                         "answer": answer_text,
#                         "tables": tables_data
#                     })
    
#     return data

# def scrape_neet_page_corrected(driver):
#     driver.get(NEET_UG_2024)
#     data = {
#         "title": None,
#         "updated_on": None,
#         "author": None,
#         "description": "",
#         "latest_news": [],
#         "table_of_contents": [],
#         "sections": [],
#         "faqs": []
#     }
    
#     # Get page source and parse with BeautifulSoup
#     soup = BeautifulSoup(driver.page_source, "html.parser")
    
#     # ---------- Get Author Info ----------
#     title = soup.find("div",class_="exam_wrap")
#     h1 = title.find("h1").text.strip()
#     data["title"]=h1
#     try:
#         author_section = soup.find("div", class_="ppBox")
#         if author_section:
#             author_data = {}
            
#             # Author name
#             author_name = author_section.find("a", href=lambda x: x and "author" in x)
#             if author_name:
#                 author_data["name"] = author_name.get_text(strip=True)
#                 author_data["profile"] = author_name["href"]
            
#             # Author image
#             img_tag = author_section.find("img", class_="ePPImg")
#             if img_tag:
#                 author_data["image"] = img_tag["src"]
            
#             # Author role and verification
#             role_text = ""
#             role_elem = author_section.find("p", class_="ePPDetail")
#             if role_elem:
#                 role_text = role_elem.get_text(strip=True)
#                 # Extract role
#                 if "By" in role_text and "," in role_text:
#                     role_parts = role_text.split(",")
#                     if len(role_parts) > 1:
#                         author_data["role"] = role_parts[1].strip()
            
#             # Verified status
#             tick_icon = author_section.find("i", class_="tickIcon")
#             author_data["verified"] = tick_icon is not None
            
#             data["author"] = author_data
#     except Exception as e:
#         print(f"Error extracting author info: {e}")
#         data["author"] = None
    
#     # ---------- Get Updated Date ----------
#     try:
#         updated_elem = soup.find("div", class_="updatedOn")
#         if updated_elem:
#             span = updated_elem.find("span")
#             if span:
#                 data["updated_on"] = span.get_text(strip=True).replace("Updated on", "").strip()
#     except:
#         data["updated_on"] = None
    
#     # ---------- Get Description/Intro Section ----------
#     try:
#         intro_section = soup.find("div", id="wikkiContents_homepage__0")
#         if intro_section:
#             description_texts = []
            
#             # Get only the first few paragraphs (before "Latest News:")
#             for p in intro_section.find_all("p"):
#                 text = p.get_text(strip=True)
#                 if text and "Latest News:" not in text:
#                     description_texts.append(text)
#                 elif "Latest News:" in text:
#                     # Stop at latest news
#                     break
            
#             data["description"] = "\n".join(description_texts)
            
#             # Get latest news
#             news_section = intro_section.find("ul")
#             if news_section:
#                 for li in news_section.find_all("li"):
#                     a_tag = li.find("a")
#                     if a_tag:
#                         news_item = {
#                             "title": a_tag.get("title", ""),
#                             "link": a_tag.get("href", ""),
#                             "text": a_tag.get_text(strip=True)
#                         }
#                         data["latest_news"].append(news_item)
#     except Exception as e:
#         print(f"Error extracting description: {e}")
    
#     # ---------- Get Table of Contents ----------
#     try:
#         toc_wrapper = soup.find("ul", id="tocWrapper")
#         if toc_wrapper:
#             toc_items = toc_wrapper.find_all("li")
#             for item in toc_items:
#                 text = item.get_text(strip=True)
#                 if text and text not in data["table_of_contents"]:
#                     data["table_of_contents"].append(text)
#     except Exception as e:
#         print(f"Error extracting table of contents: {e}")
    
#     # ---------- Get All Main Sections ----------
#     try:
#         # Find all sectionalWrapperClass divs that contain sections
#         sectional_wrappers = soup.find_all("div", class_="sectionalWrapperClass")
        
#         for wrapper in sectional_wrappers:
#             # Look for h2Container within wrapper
#             h2_container = wrapper.find("div", class_="h2Container")
#             if h2_container:
#                 h2 = h2_container.find("h2")
#                 if h2:
#                     section_data = {
#                         "title": h2.get_text(strip=True),
#                         "content": "",
#                         "tables": [],
#                         "subsections": []
#                     }
                    
#                     # Find the content after h2
#                     # Look for wikkiContents div after h2
#                     content_div = wrapper.find("div", class_="wikkiContents")
#                     if content_div:
#                         content_parts = []
#                         current_subsection = None
                        
#                         # Process all elements in content
#                         for elem in content_div.find_all(["p", "h3", "ul", "table", "iframe", "div"]):
#                             # Skip unwanted divs
#                             if elem.name == "div" and elem.get("class") and any(cls in ["showWikiReadLess"] for cls in elem.get("class")):
#                                 continue
                            
#                             if elem.name == "p":
#                                 text = elem.get_text(strip=True)
#                                 if text and not text.startswith("Also Read:"):
#                                     content_parts.append(text)
                            
#                             elif elem.name == "h3":
#                                 # This is a subsection
#                                 subsection_text = elem.get_text(strip=True)
#                                 if subsection_text:
#                                     if current_subsection:
#                                         section_data["subsections"].append(current_subsection)
#                                     current_subsection = {
#                                         "title": subsection_text,
#                                         "content": ""
#                                     }
                            
#                             elif elem.name == "ul":
#                                 list_items = []
#                                 for li in elem.find_all("li"):
#                                     li_text = li.get_text(strip=True)
#                                     if li_text:
#                                         list_items.append(f"• {li_text}")
#                                 if list_items:
#                                     list_text = "\n".join(list_items)
#                                     if current_subsection:
#                                         current_subsection["content"] += f"\n{list_text}"
#                                     else:
#                                         content_parts.append(list_text)
                            
#                             elif elem.name == "table":
#                                 # Extract table data
#                                 table_data = extract_table_data(elem)
#                                 if table_data:
#                                     section_data["tables"].append(table_data)
                            
#                             elif elem.name == "iframe":
#                                 video_src = elem.get("src", "")
#                                 if video_src:
#                                     section_data["video_link"] = video_src
                        
#                         # Add the last subsection if exists
#                         if current_subsection:
#                             section_data["subsections"].append(current_subsection)
                        
#                         section_data["content"] = "\n".join(content_parts)
                        
#                         data["sections"].append(section_data)
#     except Exception as e:
#         print(f"Error extracting sections: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # ---------- Get All FAQs ----------
#     try:
#         # Extract FAQs from all FAQ sections
#         faq_sections = soup.find_all("div", class_="sectional-faqs")
        
#         for faq_section in faq_sections:
#             # Get all question-answer pairs
#             faq_items = faq_section.find_all("div", class_="listener")
            
#             for item in faq_items:
#                 # Extract question
#                 question_elem = item.find("strong", class_="flx-box")
#                 if question_elem:
#                     # Get question text properly
#                     question_spans = question_elem.find_all("span")
#                     if len(question_spans) >= 2:
#                         question_text = question_spans[1].get_text(strip=True)
#                     else:
#                         # Try to extract Q: from text
#                         full_text = question_elem.get_text(strip=True)
#                         if "Q:" in full_text:
#                             question_text = full_text.split("Q:", 1)[1].strip()
#                         else:
#                             question_text = full_text
                    
#                     # Find answer div
#                     answer_div = item.find_next_sibling("div", class_="_16f53f")
#                     if answer_div:
#                         answer_content = answer_div.find("div", class_="wikkiContents")
#                         if answer_content:
#                             # Extract answer text
#                             answer_text_div = answer_content.find("div", class_="_843b17")
#                             if answer_text_div:
#                                 answer_text = ""
#                                 answer_div_content = answer_text_div.find("div")
                                
#                                 if answer_div_content:
#                                     # Extract paragraphs
#                                     for p in answer_div_content.find_all("p"):
#                                         p_text = p.get_text(strip=True)
#                                         if p_text and not p_text.startswith("A:"):
#                                             answer_text += p_text + "\n"
                                    
#                                     # Extract lists
#                                     for ul in answer_div_content.find_all("ul"):
#                                         list_items = []
#                                         for li in ul.find_all("li"):
#                                             li_text = li.get_text(strip=True)
#                                             if li_text:
#                                                 list_items.append(f"• {li_text}")
#                                         if list_items:
#                                             answer_text += "\n".join(list_items) + "\n"
                                    
#                                     # If no paragraphs found, get all text
#                                     if not answer_text:
#                                         answer_text = answer_div_content.get_text(strip=True)
#                                 else:
#                                     # Fallback to entire text
#                                     answer_text = answer_text_div.get_text(strip=True).replace("A:", "").replace("A:&nbsp;", "").strip()
                                
#                                 # Extract tables from answer
#                                 tables_in_answer = []
#                                 if answer_div_content:
#                                     for table in answer_div_content.find_all("table"):
#                                         table_data = extract_table_data(table)
#                                         if table_data:
#                                             tables_in_answer.append(table_data)
                                
#                                 # Check if FAQ already exists
#                                 existing_faq = False
#                                 for existing in data["faqs"]:
#                                     if existing["question"] == question_text:
#                                         existing_faq = True
#                                         break
                                
#                                 if not existing_faq and question_text and answer_text:
#                                     data["faqs"].append({
#                                         "question": question_text,
#                                         "answer": answer_text.strip(),
#                                         "tables": tables_in_answer
#                                     })
#     except Exception as e:
#         print(f"Error extracting FAQs: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # ---------- Clean up FAQs ----------
#     # Remove duplicates and empty FAQs
#     unique_faqs = []
#     seen_questions = set()
    
#     for faq in data["faqs"]:
#         question = faq["question"].strip()
#         if question and question not in seen_questions:
#             seen_questions.add(question)
#             unique_faqs.append(faq)
    
#     data["faqs"] = unique_faqs
    
#     return data


# def extract_table_data(table_element):
 
#     try:
#         table_data = []
#         for row in table_element.find_all("tr"):
#             row_data = []
#             for cell in row.find_all(["th", "td"]):
#                 # Get cell text and clean it
#                 cell_text = cell.get_text(strip=True)
                
#                 # Remove extra whitespace and newlines
#                 cell_text = re.sub(r'\s+', ' ', cell_text)
                
#                 # Check if cell has colspan or rowspan
#                 colspan = cell.get('colspan', '1')
#                 rowspan = cell.get('rowspan', '1')
                
#                 row_data.append(cell_text)
            
#             if row_data:  # Only add non-empty rows
#                 table_data.append(row_data)
        
#         return table_data if table_data else None
#     except Exception as e:
#         print(f"Error extracting table: {e}")
#         return None

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
    # page_title=soup.find("div",class_="_9617")
    # ptitle = page_title.find("h1").text.strip()
    # data["Page_title"] = ptitle
    h2_tag = soup.find('h1',class_="d972")
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
              "BMLT":{
                   "overviews":extract_course_data(driver),
                   "courses":scrape_courses_overview_section(driver),
                   "syllabus":scrape_bmlt_syllabus(driver),
                #    "subject":scrape_mbbs_subjects_overview(driver),               
                #    "career":scrape_md_career(driver),
                   "addmission":scrape_addmission_2026_data(driver),
                #    "fees": scrape_mba_fees_overview(driver),
                #    "comparison": scrape_mbbs_vs_md_comparison(driver),
                #    "MD VS MBBS":scrape_mbbs_vs_md(driver),
                #   "AIIMS COLLEGE IN INDIA":scrape_aiims_data(driver),
                #   "ALTERNATIVE MBBS":scrape_alternative_mbbs(driver),
                #   "NEET UG 2024":scrape_neet_page_corrected(driver),
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

