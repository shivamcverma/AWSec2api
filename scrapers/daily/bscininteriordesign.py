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

PCOMBA_O_URL="https://www.shiksha.com/design/b-sc-in-interior-design-chp"
PCOMBA_C_URL="https://www.shiksha.com/design/b-sc-in-interior-design-courses-chp"
# PCOMBA_MBA_SYLLABUS_URL = "https://www.shiksha.com/b-des-bachelor-of-design-syllabus-chp"
# PCOMBA_SUB_URL = "https://www.shiksha.com/md-doctor-of-medicine-subjects-chp"
# PCOMBA_MBA_CAREER_URL = "https://www.shiksha.com/b-des-bachelor-of-design-career-chp"
PCOMBA_MBA_ADDMISSION_2026_URL = "https://www.shiksha.com/design/b-sc-in-interior-design-admission-chp"
# PCOMBA_MBA_FEES_URL = "https://www.shiksha.com/mbbs-fees-chp"
# LIST_OF_NIFTS = "https://www.shiksha.com/design/articles/list-of-nifts-in-india-blogId-30549"
# NIFT_COURSE_FEES = "https://www.shiksha.com/design/articles/fee-structure-for-ug-and-pg-design-courses-in-nifts-blogId-30907"
# NIFTS_SEAT = "https://www.shiksha.com/design/fashion-design/articles/colleges-accepting-nift-scores-2026-total-seats-course-wise-seat-intake-blogId-13134" 
# NIFTS_PLACEMENT ="https://www.shiksha.com/design/articles/nift-placements-blogId-90375"
# CAREER_AFTER_MDES = "https://www.shiksha.com/design/articles/career-after-mdes-blogId-70121"
# NIFTS_INTERVIEWS = "https://www.shiksha.com/design/fashion-design/articles/10-tips-to-crack-interview-for-design-courses-at-nid-nift-iit-blogId-12314"
P_COLLEGE = "https://www.shiksha.com/design/interior-design/colleges/b-sc-colleges-india?sby=popularity&rf=filters"
QA = "https://www.shiksha.com/tags/interior-design-tdp-66"
QAD = "https://www.shiksha.com/tags/interior-design-tdp-66?type=discussion"

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

    service = Service("/snap/bin/chromedriver")

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
    soup = BeautifulSoup(driver.page_source, "html.parser")
    data = {}

    # =====================================================
    # 1. OVERVIEW SECTION
    # =====================================================
    overview_sec = soup.find("section", id="chp_section_overview")
    if not overview_sec:
        return data

    data["meta"] = {}
    
    # Extract title from the page
    title = soup.find("title")
    if title:
        data["meta"]["title"] = title.text.strip()
    
    # Extract updated date - Fixed selector
    updated_info = overview_sec.find("div", class_="d957ae")
    if updated_info:
        first_div = updated_info.find("div")
        if first_div:
            span = first_div.find("span")
            data["meta"]["updated_on"] = span.text.strip() if span else None

    # Extract author information
    author_div = overview_sec.find("div", class_="c2675e")
    if author_div:
        author_link = author_div.find("a")
        role_span = author_div.find("span", class_="cbbdad")
        
        data["meta"]["author"] = {
            "name": author_link.text.strip() if author_link else None,
            "profile": author_link.get("href") if author_link else None,
            "role": role_span.text.strip() if role_span else None,
            "verified": bool(author_div.find("i", class_="tickIcon"))
        }

    # ---------------- OVERVIEW CONTENT ----------------
    data["overview"] = {"content_flow": [], "faqs": []}
    content_div = overview_sec.find("div", id="wikkiContents_chp_section_overview_0")

    if content_div:
        main_div = content_div.find("div")
        if main_div:
            # Process all child elements
            for tag in main_div.children:
                if hasattr(tag, 'name'):  # Check if it's a tag element
                    if tag.name in ["h2", "h3"]:
                        # Extract clean text
                        clean_text = tag.get_text(strip=True)
                        
                        # Check for colored background in spans
                        color_spans = tag.find_all("span", style=lambda x: x and "background-color" in x.lower())
                        for color_span in color_spans:
                            # Remove the colored span text from clean text
                            clean_text = clean_text.replace(color_span.get_text(strip=True), "").strip()
                        
                        # Check for any remaining styling
                        style_attr = tag.get("style", "")
                        if any(style in style_attr.lower() for style in ["background", "color"]):
                            data["overview"]["content_flow"].append({
                             
                                "text": clean_text,
                           
                            })
                        elif color_spans:
                            data["overview"]["content_flow"].append({
                            
                                "text": clean_text,
                                "level": 2 if tag.name == "h2" else 3,
                              
                            })
                        else:
                            data["overview"]["content_flow"].append({
                              
                                "text": clean_text,
                                
                            })

                    elif tag.name == "p":
                        text = tag.get_text(" ", strip=True)
                        if text and text.strip():
                            # Check for special styling
                            color_span = tag.find("span", style=lambda x: x and "color: #e03e2d" in x)
                            strong_tags = tag.find_all("strong")
                            em_tag = tag.find("em")
                            
                            # Extract all links
                            links = []
                            for link in tag.find_all("a"):
                                links.append({
                                    "text": link.get_text(strip=True),
                                    "url": link.get("href")
                                })
                            
                            item = {
                               
                                "text": text
                            }
                            
                            
                                
                            data["overview"]["content_flow"].append(item)

                    elif tag.name == "table":
                        rows = []
                        for tr in tag.find_all("tr"):
                            cols = []
                            for td in tr.find_all(["th", "td"]):
                                # Extract text, checking for inner divs
                                cell_text = td.get_text(" ", strip=True)
                                
                                # Check for inner div with text
                                div = td.find("div")
                                if div:
                                    div_text = div.get_text(" ", strip=True)
                                    if div_text:
                                        cell_text = div_text
                                
                                cols.append(cell_text)
                            if cols:
                                rows.append(cols)
                        
                        if rows:
                            data["overview"]["content_flow"].append({
                               
                                "rows": rows
                            })

       
                # Handle text nodes (like "&nbsp;")
                elif tag.string and tag.string.strip():
                    text = tag.string.strip()
                    if text and text != "&nbsp;":
                        data["overview"]["content_flow"].append({
                    
                            "content": text
                        })

    # ---------------- OVERVIEW FAQ ----------------
    faq_container = overview_sec.find("div", class_="sectional-faqs")
    if faq_container:
        faq_items = faq_container.find_all("div", class_="html-0")
        for q in faq_items:
            ans_box = q.find_next_sibling("div", class_="f61835")
            
            # Extract answer with proper formatting
            answer_data = {}
            if ans_box:
                answer_div = ans_box.find("div", class_="cmsAContent")
                if answer_div:
                    # Process all answer content
                    answer_content = []
                    
                    # Handle paragraphs
                    for p in answer_div.find_all("p"):
                        p_text = p.get_text(" ", strip=True)
                        if p_text:
                            p_links = []
                            for link in p.find_all("a"):
                                p_links.append({
                                    "text": link.get_text(strip=True),
                                    "url": link.get("href")
                                })
                            
                            p_item = {
                              
                                "text": p_text
                            }
                            if p_links:
                                p_item["links"] = p_links
                            answer_content.append(p_item)
                    
                    # Handle unordered lists
                    for ul in answer_div.find_all("ul"):
                        list_items = []
                        for li in ul.find_all("li"):
                            li_text = li.get_text(" ", strip=True)
                            if li_text:
                                list_items.append(li_text)
                        
                        if list_items:
                            answer_content.append({
                         
                                "items": list_items
                            })
                    
                    # Handle tables
                    for table in answer_div.find_all("table"):
                        table_rows = []
                        for tr in table.find_all("tr"):
                            cols = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
                            if cols:
                                table_rows.append(cols)
                        
                        if table_rows:
                            answer_content.append({
                           
                                "rows": table_rows
                            })
                    
                    answer_data["content"] = answer_content
            
            # Extract question text
            question_spans = q.find_all("span")
            question_text = ""
            for span in question_spans:
                if span.text.strip() and "Q:" not in span.text:
                    question_text = span.text.strip()
                    break
            
            if not question_text:
                # Fallback: get all text and clean it
                question_text = q.get_text(" ", strip=True).replace("Q:", "").strip()
            
            # Extract question ID from the element
            question_id = q.get("id", "").replace("0::", "")
            
            # Check for GPT integration
            gpt_div = None
            if ans_box:
                gpt_div = ans_box.find("div", class_="cf05b5")
            
            data["overview"]["faqs"].append({
        
                "question": question_text,
                "answer": answer_data,
             
            })

    # =====================================================
    # 2. ELIGIBILITY SECTION
    # =====================================================
    eligibility_sec = soup.find("section", id="chp_section_eligibility")
    data["eligibility"] = {"title": None, "content_flow": [], "faqs": []}

    if eligibility_sec:
        # Extract title
        h2 = eligibility_sec.find("h2", class_="tbSec2")
        if h2:
            data["eligibility"]["title"] = h2.get_text(strip=True)

        # Extract main content
        content_div = eligibility_sec.find("div", id="wikkiContents_chp_section_eligibility_1")
        
        if content_div:
            main_div = content_div.find("div")
            if main_div:
                for tag in main_div.children:
                    if hasattr(tag, 'name'):
                        if tag.name in ["h2", "h3"]:
                            # Extract clean text
                            clean_text = tag.get_text(strip=True)
                            
                            # Check for colored background
                            color_span = tag.find("span", style=lambda x: x and "background-color" in x.lower())
                            if color_span:
                                # Remove the colored span text
                                clean_text = clean_text.replace(color_span.get_text(strip=True), "").strip()
                                data["eligibility"]["content_flow"].append({
                                  
                                    "text": clean_text,
                                    "level": 2 if tag.name == "h2" else 3,
                
                                })
                            else:
                                data["eligibility"]["content_flow"].append({
                                  
                                    "text": clean_text,
                                    "level": 2 if tag.name == "h2" else 3
                                })

                        elif tag.name == "p":
                            text = tag.get_text(" ", strip=True)
                            if text and text.strip():
                                # Check for colored text
                                color_span = tag.find("span", style=lambda x: x and "color: #e03e2d" in x)
                                links = []
                                for link in tag.find_all("a"):
                                    links.append({
                                        "text": link.get_text(strip=True),
                                        "url": link.get("href")
                                    })
                                
                                item = {
                                   
                                    "text": text
                                }
                                
                               
                                data["eligibility"]["content_flow"].append(item)

                        elif tag.name == "table":
                            rows = []
                            for tr in tag.find_all("tr"):
                                cols = []
                                for td in tr.find_all(["th", "td"]):
                                    # Handle potential divs inside table cells
                                    cell_text = td.get_text(" ", strip=True)
                                    div = td.find("div")
                                    if div:
                                        div_text = div.get_text(" ", strip=True)
                                        if div_text:
                                            cell_text = div_text
                                    cols.append(cell_text)
                                if cols:
                                    rows.append(cols)
                            
                            if rows:
                                data["eligibility"]["content_flow"].append({
                                 
                                    "rows": rows
                                })

        # ---------------- ELIGIBILITY FAQ ----------------
        faq_container = eligibility_sec.find("div", class_="sectional-faqs")
        if faq_container:
            faq_items = faq_container.find_all("div", class_="html-0")
            for q in faq_items:
                ans_box = q.find_next_sibling("div", class_="f61835")
                
                # Extract answer with proper formatting
                answer_data = {}
                if ans_box:
                    answer_div = ans_box.find("div", class_="cmsAContent")
                    if answer_div:
                        answer_content = []
                        
                        # Process paragraphs
                        for p in answer_div.find_all("p"):
                            p_text = p.get_text(" ", strip=True)
                            if p_text:
                                p_links = []
                                for link in p.find_all("a"):
                                    p_links.append({
                                        "text": link.get_text(strip=True),
                                        "url": link.get("href")
                                    })
                                
                                p_item = {
                                 
                                    "text": p_text
                                }
                                if p_links:
                                    p_item["links"] = p_links
                                answer_content.append(p_item)
                        
                        # Process unordered lists
                        for ul in answer_div.find_all("ul"):
                            list_items = []
                            for li in ul.find_all("li"):
                                li_text = li.get_text(" ", strip=True)
                                if li_text:
                                    list_items.append(li_text)
                            
                            if list_items:
                                answer_content.append({
                                
                                    "items": list_items
                                })
                        
                        answer_data["content"] = answer_content
                
                # Extract question
                question_spans = q.find_all("span")
                question_text = ""
                for span in question_spans:
                    if span.text.strip() and "Q:" not in span.text:
                        question_text = span.text.strip()
                        break
                
                if not question_text:
                    question_text = q.get_text(" ", strip=True).replace("Q:", "").strip()
                
                # Extract question ID
                question_id = q.get("id", "").replace("0::", "")
                
                data["eligibility"]["faqs"].append({
               
                    "question": question_text,
                    "answer": answer_data
                })
    top_rate_div = soup.find("div", id="wikkiContents_chp_section_topratecourses_0")
    data["top_rate_courses"] = {
        "title":{},
        "content_flow": []
        }
    title = soup.find(id="chp_section_topratecourses")
    title_tag =title.find("h2", class_="tbSec2")
    ti = title_tag.get_text(strip=True) if title_tag else None
    data["top_rate_courses"]["title"] = ti

    if top_rate_div:
        main_div = top_rate_div.find("div")
        if main_div:
            for tag in main_div.children:
                if hasattr(tag, "name"):

                    # ---------- PARAGRAPHS ----------
                    if tag.name == "p":
                        text = tag.get_text(" ", strip=True)
                        if text and text != "&nbsp;":
                            links = []
                            for a in tag.find_all("a"):
                                links.append({
                                    "text": a.get_text(strip=True),
                                    "url": a.get("href")
                                })

                            item = {"text": text}
                            if links:
                                item["links"] = links

                            data["top_rate_courses"]["content_flow"].append(item)

                    # ---------- TABLE ----------
                    elif tag.name == "table":
                        table_data = []
                        for tr in tag.find_all("tr"):
                            row = []
                            for td in tr.find_all(["th", "td"]):
                                cell_text = td.get_text(" ", strip=True)

                                inner_div = td.find("div")
                                if inner_div:
                                    inner_text = inner_div.get_text(" ", strip=True)
                                    if inner_text:
                                        cell_text = inner_text

                                row.append(cell_text)

                            if row:
                                table_data.append(row)

                        if table_data:
                            data["top_rate_courses"]["content_flow"].append({
                                "rows": table_data
                            })

                    # ---------- TEXT NODES ----------
                    elif tag.string and tag.string.strip():
                        clean_text = tag.string.strip()
                        if clean_text and clean_text != "&nbsp;":
                            data["top_rate_courses"]["content_flow"].append({
                                "text": clean_text
                            })

    return data

def clean(tag):
    return tag.get_text(" ", strip=True) if tag else None


def scrape_courses_overview_section(driver):
    driver.get(PCOMBA_C_URL)
    WebDriverWait(driver, 15)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # ===============================
    # MAIN DATA OBJECT
    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "courses": {
            "sections": {},
            "videos": [],
            "specializations": {}
        }
    }

    # ===============================
    # COURSE TITLE
    course_name_div = soup.find("div", class_="a54c")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # UPDATED DATE
    updated_wrapper = soup.find("div", class_="d957ae")
    if updated_wrapper:
        span = updated_wrapper.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # AUTHOR INFO
    author_block = soup.find("div", class_="c2675e")
    if author_block:
        a = author_block.find("a")
        img = author_block.find("img")
        role = author_block.find("span", class_="cbbdad")

        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": img["src"] if img else None,
            "role": clean(role),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # COURSES OVERVIEW CONTENT
    container = soup.find("div", id="wikkiContents_chp_courses_overview_0")
    if not container:
        return data

    # INIT INTRO SECTION
    current_section = "intro"
    active_sub = None

    data["courses"]["sections"]["intro"] = {
        "paragraphs": [],
        "tables": [],
        "lists": [],
        "related_links": [],
        "sub_sections": {}
    }

    # ===============================
    # MAIN PARSER LOOP
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

            if current_section == "intro":
                if link:
                    data["courses"]["sections"]["intro"]["related_links"].append({
                        "text": clean(link),
                        "url": link["href"]
                    })
                else:
                    data["courses"]["sections"]["intro"]["paragraphs"].append(text)
            else:
                target = (
                    data["courses"]["sections"][current_section]["sub_sections"][active_sub]
                    if active_sub
                    else data["courses"]["sections"][current_section]
                )
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

    # ===============================
    # SPECIALIZATION-WISE SYLLABUS
    spec_container = soup.find("div", id="wikkiContents_chp_syllabus_popularspecialization_0")
    if spec_container:
        table = spec_container.find("table")
        if table:
            for tr in table.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) == 3:
                    spec_tag = tds[0].find("a")
                    spec_name = clean(spec_tag) if spec_tag else clean(tds[0])
                    spec_link = spec_tag["href"] if spec_tag else None

                    subjects = [clean(li) for li in tds[1].find_all("li")]
                    description = clean(tds[2])

                    data["courses"]["specializations"][spec_name] = {
                        "link": spec_link,
                        "subjects": subjects,
                        "description": description
                    }

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


# def extract_syllabus_overview(driver):
#     driver.get(PCOMBA_MBA_SYLLABUS_URL)
#     time.sleep(3)
#     soup = BeautifulSoup(driver.page_source, "html.parser")

#     data = {
#         "meta": {},
#         "content_flow": []
#     }

#     section = soup.find("section", id="chp_syllabus_overview")
#     if not section:
#         return data
#     title = soup.find("div",class_="d8a6c4")
#     h1 = title.find("h1").text.strip()
#     data["meta"]["title"]= h1
#     # =====================================================
#     # META DATA (Updated on + Author)
#     # =====================================================
#     meta_div = section.find("div", class_="d957ae")
#     if meta_div:
#         # Updated on
#         updated_span = meta_div.find("span")
#         data["meta"]["updated_on"] = updated_span.get_text(strip=True) if updated_span else None

#         # Author info
#         author_div = meta_div.find("div", class_="c2675e")
#         if author_div:
#             author_link = author_div.find("a")
#             role_span = author_div.find("span", class_="cbbdad")

#             data["meta"]["author"] = {
#                 "name": author_link.get_text(strip=True) if author_link else None,
#                 "profile": author_link["href"] if author_link and author_link.has_attr("href") else None,
#                 "role": role_span.get_text(strip=True) if role_span else None,
#                 "verified": bool(author_div.find("i", class_="tickIcon"))
#             }

#     # =====================================================
#     # MAIN CONTENT
#     # =====================================================
#     content_div = section.find(
#         "div",
#         id=lambda x: x and x.startswith("wikkiContents_chp_syllabus_overview")
#     )

#     if not content_div:
#         return data

#     for tag in content_div.find_all(
#         ["h2", "h3", "p", "table", "ul", "a"],
#         recursive=True
#     ):
#         # ---------------- HEADINGS ----------------
#         if tag.name in ["h2", "h3"]:
#             text = tag.get_text(" ", strip=True)
#             if text:
#                 data["content_flow"].append({
                   
#                     "level": 2 if tag.name == "h2" else 3,
#                     "text": text
#                 })

#         # ---------------- PARAGRAPHS ----------------
#         elif tag.name == "p":
#             text = tag.get_text(" ", strip=True)
#             if text:
#                 data["content_flow"].append({
                 
#                     "text": text
#                 })

#         # ---------------- TABLES ----------------
#         elif tag.name == "table":
#             table_data = []
#             for tr in tag.find_all("tr"):
#                 row = [
#                     cell.get_text(" ", strip=True)
#                     for cell in tr.find_all(["th", "td"])
#                 ]
#                 if row:
#                     table_data.append(row)

#             if table_data:
#                 data["content_flow"].append({
     
#                     "rows": table_data
#                 })

#         # ---------------- LISTS ----------------
#         elif tag.name == "ul":
#             items = [
#                 li.get_text(" ", strip=True)
#                 for li in tag.find_all("li")
#             ]
#             if items:
#                 data["content_flow"].append({
         
#                     "items": items
#                 })

#         # ---------------- LINKS ----------------
#         elif tag.name == "a":
#             href = tag.get("href")
#             text = tag.get_text(strip=True)
#             if href and text:
#                 data["content_flow"].append({
               
#                     "text": text,
#                     "url": href
#                 })

#     return data

# def scrape_md_career(driver):
#     driver.get(PCOMBA_MBA_CAREER_URL)
#     time.sleep(5)

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}

#     section = soup.find("section", id="chp_career_overview")
#     if not section:
#         return data

#     # =====================================================
#     # COURSE TITLE
#     # =====================================================
#     course_name_div = soup.find("div", class_="d8a6c4")
#     if course_name_div:
#         h1 = course_name_div.find("h1")
#         data["title"] = h1.get_text(strip=True) if h1 else None

#     # =====================================================
#     # META (UPDATED DATE + AUTHOR)
#     # =====================================================
#     data["meta"] = {}

#     meta_div = section.find("div", class_="d957ae")
#     if meta_div:
#         span = meta_div.find("span")
#         data["meta"]["updated_on"] = span.get_text(strip=True) if span else None

#         author_div = meta_div.find("div", class_="c2675e")
#         if author_div:
#             a = author_div.find("a")
#             img = author_div.find("img")
#             role = author_div.find("span", class_="cbbdad")

#             data["meta"]["author"] = {
#                 "name": a.get_text(strip=True) if a else None,
#                 "profile": a["href"] if a else None,
#                 "image": img["src"] if img else None,
#                 "role": role.get_text(strip=True) if role else None,
#                 "verified": bool(author_div.find("i", class_="tickIcon"))
#             }

#     # =====================================================
#     # MAIN CONTENT (SEQUENTIAL – FULL SCRAPE)
#     # =====================================================
#     data["content_flow"] = []

#     content_div = section.find(
#         "div",
#         id=lambda x: x and x.startswith("wikkiContents_chp_career_overview")
#     )

#     if not content_div:
#         return data

#     for tag in content_div.find_all(
#         ["h2", "h3", "p", "table", "ul", "a", "iframe"],
#         recursive=True
#     ):
#         # ---------------- HEADINGS ----------------
#         if tag.name in ["h2", "h3"]:
#             text = tag.get_text(" ", strip=True)
#             if text:
#                 data["content_flow"].append({
               
#                     "level": tag.name,
#                     "text": text
#                 })

#         # ---------------- PARAGRAPHS ----------------
#         elif tag.name == "p":
#             text = tag.get_text(" ", strip=True)
#             if text:
#                 data["content_flow"].append({
                 
#                     "text": text
#                 })

#         # ---------------- TABLES ----------------
#         elif tag.name == "table":
#             rows = []
#             for tr in tag.find_all("tr"):
#                 cols = [
#                     cell.get_text(" ", strip=True)
#                     for cell in tr.find_all(["th", "td"])
#                 ]
#                 if cols:
#                     rows.append(cols)

#             if rows:
#                 data["content_flow"].append({
                 
#                     "rows": rows
#                 })

#         # ---------------- LISTS ----------------
#         elif tag.name == "ul":
#             items = [
#                 li.get_text(" ", strip=True)
#                 for li in tag.find_all("li")
#             ]
#             if items:
#                 data["content_flow"].append({
                  
#                     "items": items
#                 })

#         # ---------------- LINKS ----------------
#         elif tag.name == "a":
#             href = tag.get("href")
#             text = tag.get_text(strip=True)
#             if href and text:
#                 data["content_flow"].append({
           
#                     "text": text,
#                     "url": href
#                 })

#         # ---------------- VIDEOS ----------------
#         elif tag.name == "iframe":
#             src = tag.get("src")
#             if src:
#                 data["content_flow"].append({
                 
#                     "src": src
#                 })

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

    # ===================== TITLE =====================
    course_name_div = soup.find("div", class_="d8a6c4")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = h1.get_text(strip=True) if h1 else None

    # ===================== UPDATED DATE =====================
    updated_div = section.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = span.get_text(strip=True) if span else updated_div.get_text(strip=True)

    # ===================== AUTHOR INFO =====================
    author_wrapper = section.find("div", class_="c2675e")
    if author_wrapper:
        a = author_wrapper.find("a")
        img = author_wrapper.find("img")
        role = author_wrapper.find("span", class_="cbbdad")

        data["author"] = {
            "name": a.get_text(strip=True) if a else None,
            "profile": a["href"] if a else None,
            "image": img["src"] if img else None,
            "role": role.get_text(strip=True) if role else None,
            "verified": bool(author_wrapper.find("i", class_="tickIcon"))
        }

    # ===================== CONTENT =====================
    content_div = section.find("div", class_="wikkiContents")
    if not content_div:
        return data

    full_content = []

    for elem in content_div.find("div", recursive=False).children:

        if not hasattr(elem, "name"):
            continue

        # ---------- HEADINGS ----------
        if elem.name in ["h2", "h3"]:
            full_content.append({
           
                "level": elem.name,
                "text": elem.get_text(" ", strip=True)
            })

        # ---------- PARAGRAPHS ----------
        elif elem.name == "p":
            links = [
                {"text": a.get_text(strip=True), "url": a.get("href")}
                for a in elem.find_all("a")
            ]
            full_content.append({
           
                "text": elem.get_text(" ", strip=True),
                "links": links
            })

        # ---------- LIST ----------
        elif elem.name == "ul":
            items = [li.get_text(" ", strip=True) for li in elem.find_all("li")]
            full_content.append({
              
                "items": items
            })

        # ---------- TABLE ----------
        elif elem.name == "table":
            table_rows = []
            headers = []

            rows = elem.find_all("tr")
            if rows:
                headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]

                for tr in rows[1:]:
                    cells = []
                    for td in tr.find_all("td"):
                        # UL inside TD handling
                        ul = td.find("ul")
                        if ul:
                            cells.append(
                                "; ".join(li.get_text(" ", strip=True) for li in ul.find_all("li"))
                            )
                        else:
                            cells.append(td.get_text(" ", strip=True))

                    if headers and len(headers) == len(cells):
                        table_rows.append(dict(zip(headers, cells)))
                    else:
                        table_rows.append(cells)

            full_content.append({
           
                "headers": headers,
                "rows": table_rows
            })

        # ---------- IFRAME / VIDEO ----------
        elif elem.name == "iframe":
            full_content.append({
             
                "src": elem.get("src")
            })

    data["full_content"] = full_content

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

# def scrape_mdes_career_data(driver):
#     driver.get(CAREER_AFTER_MDES)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}
#     data["meta"] = {}

#     # ---------- Updated Date ----------
#     updated_div = soup.select_one("div.blogdata_user > span")
#     if updated_div and "Updated on" in updated_div.text:
#         data["meta"]["updated_on"] = updated_div.get_text(strip=True)


#     # ---------- Reading Time (optional but useful) ----------
#     reading_time = soup.find(
#         "span",
#         string=lambda x: x and "mins read" in x.lower()
#     )
#     if reading_time:
#         data["meta"]["reading_time"] = reading_time.get_text(strip=True)


#     author_section = soup.find("div", class_="adp_user")

#     if author_section:
#         author_anchor = author_section.select_one("div.adp_usr_dtls > a")

#         name = None
#         if author_anchor:
#             # Only direct text nodes (no svg, no img)
#             name = "".join(author_anchor.find_all(string=True, recursive=False)).strip()

#         data["meta"]["author"] = {
#             "name": name,
#             "profile": author_anchor["href"] if author_anchor else None,
#             "role": author_section.select_one(".user_expert_level").get_text(strip=True)
#                     if author_section.select_one(".user_expert_level") else None,
#             "verified": bool(author_section.select_one("i.tickIcon"))
#         }



#     main_div = soup.find("div", id="blogId-70121")
#     if not main_div:
#         return data

#     # ===================== TITLE =====================
#     h1 = soup.find("h1")
#     data["title"] = h1.get_text(strip=True) if h1 else None

#     # ===================== INTRO CONTENT =====================
#     intro_section = main_div.find("div", class_="wikkiContents")
#     intro_content = []

#     if intro_section:
#         for p in intro_section.find_all("p", recursive=False):
#             intro_content.append(p.get_text(" ", strip=True))

#     data["intro"] = intro_content

#     # ===================== TABLE OF CONTENTS =====================
#     toc = []
#     toc_wrapper = soup.find("ul", id="tocWrapper")
#     if toc_wrapper:
#         for li in toc_wrapper.find_all("li"):
#             toc.append(li.get_text(" ", strip=True))

#     data["table_of_contents"] = toc

#     # ===================== FULL CONTENT =====================
#     full_content = []

#     content_blocks = main_div.find_all("div", class_="wikkiContents")

#     for block in content_blocks:
#         for elem in block.children:

#             if not hasattr(elem, "name"):
#                 continue

#             # ---------- HEADINGS ----------
#             if elem.name in ["h2", "h3"]:
#                 full_content.append({
#                     "type": "heading",
#                     "level": elem.name,
#                     "text": elem.get_text(" ", strip=True)
#                 })

#             # ---------- PARAGRAPH ----------
#             elif elem.name == "p":
#                 links = [
#                     {"text": a.get_text(strip=True), "url": a.get("href")}
#                     for a in elem.find_all("a", href=True)
#                 ]

#                 full_content.append({
#                     "type": "paragraph",
#                     "text": elem.get_text(" ", strip=True),
#                     "links": links
#                 })

#             # ---------- LIST ----------
#             elif elem.name == "ul":
#                 items = [li.get_text(" ", strip=True) for li in elem.find_all("li")]
#                 full_content.append({
#                     "type": "list",
#                     "items": items
#                 })

#             # ---------- TABLE ----------
#             elif elem.name == "table":
#                 headers = []
#                 rows_data = []

#                 rows = elem.find_all("tr")
#                 if rows:
#                     headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]

#                     for tr in rows[1:]:
#                         cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
#                         if headers and len(headers) == len(cells):
#                             rows_data.append(dict(zip(headers, cells)))
#                         else:
#                             rows_data.append(cells)

#                 full_content.append({
#                     "type": "table",
#                     "headers": headers,
#                     "rows": rows_data
#                 })

#             # ---------- IMAGE ----------
#             elif elem.name == "div" and elem.find("img"):
#                 img = elem.find("img")
#                 full_content.append({
#                     "type": "image",
#                     "src": img.get("src"),
#                     "alt": img.get("alt")
#                 })

#             # ---------- VIDEO ----------
#             elif elem.name == "iframe":
#                 full_content.append({
#                     "type": "video",
#                     "src": elem.get("src")
#                 })

#     data["full_content"] = full_content

#     return data

# def scrape_nift_admission_data(driver):

#     driver.get(LIST_OF_NIFTS)

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}
#     data["meta"] = {}


#     # ---------- Updated Date ----------
#     updated_div = soup.select_one("div.blogdata_user > span")
#     if updated_div and "Updated on" in updated_div.text:
#         data["meta"]["updated_on"] = updated_div.get_text(strip=True)


#     # ---------- Reading Time (optional but useful) ----------
#     reading_time = soup.find(
#         "span",
#         string=lambda x: x and "mins read" in x.lower()
#     )
#     if reading_time:
#         data["meta"]["reading_time"] = reading_time.get_text(strip=True)


#     author_section = soup.find("div", class_="adp_user")

#     if author_section:
#         author_anchor = author_section.select_one("div.adp_usr_dtls > a")

#         name = None
#         if author_anchor:
#             # Only direct text nodes (no svg, no img)
#             name = "".join(author_anchor.find_all(string=True, recursive=False)).strip()

#         data["meta"]["author"] = {
#             "name": name,
#             "profile": author_anchor["href"] if author_anchor else None,
#             "role": author_section.select_one(".user_expert_level").get_text(strip=True)
#                     if author_section.select_one(".user_expert_level") else None,
#             "verified": bool(author_section.select_one("i.tickIcon"))
#         }
#     # ===================== MAIN CONTENT =====================
#     # Title - पहला h1 ढूँढें
#     h1 = soup.find("h1")
#     data["title"] = h1.get_text(strip=True) if h1 else "NIFT Admission Information"
#     picture = soup.find("picture")

#     img_tag = picture.find("img")
#     img_url = img_tag.get("src")

#     data["meta"]["img"] = img_url

#     # ===================== INTRODUCTION SECTION =====================
#     intro_section = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#     intro_content = []
    
#     if intro_section:
#         # पहले पैराग्राफ (italic वाला)
#         first_p = intro_section.find("p", style="text-align: justify;")
#         if first_p:
#             intro_content.append(first_p.get_text(" ", strip=True))
        
#         # बाकी पैराग्राफ
#         other_ps = intro_section.find_all("p", recursive=True)
#         for p in other_ps[1:]:  # पहले को छोड़कर
#             text = p.get_text(" ", strip=True)
#             if text and not text.startswith("NIFT Institutes"):  # कैप्शन वाला नहीं
#                 intro_content.append(text)
    
#     data["intro"] = intro_content

#     # ===================== TABLE OF CONTENTS =====================
#     toc = []
#     toc_wrapper = soup.find("ul", id="tocWrapper")
#     if toc_wrapper:
#         for li in toc_wrapper.find_all("li"):
#             toc.append(li.get_text(" ", strip=True))
    
#     data["table_of_contents"] = toc

#     # ===================== MAIN CONTENT SECTIONS =====================
#     full_content = []
    
#     # सभी content sections ढूँढें
#     content_sections = soup.find_all("div", class_="wikkiContents")
    
#     for section in content_sections:
#         # Section ID से section पहचानें
#         section_id = section.get("id", "")
        
#         # प्रत्येक element को process करें
#         for elem in section.children:
#             if not hasattr(elem, "name"):
#                 continue
            
#             # ---------- HEADINGS ----------
#             if elem.name in ["h2"]:
#                 heading_text = elem.get_text(" ", strip=True)
                
#                 # Table of contents से link करने के लिए ID
#                 heading_id = elem.get("id", "")
                
#                 full_content.append({
                  
              
#                     "text": heading_text,
        
#                 })
            
#             # ---------- PARAGRAPHS ----------
#             elif elem.name == "p":
#                 text = elem.get_text(" ", strip=True)
#                 if text:  # खाली paragraphs को ignore करें
#                     # Links निकालें
#                     links = []
#                     for a in elem.find_all("a", href=True):
#                         links.append({
#                             "text": a.get_text(strip=True),
                          
#                         })
                    
#                     full_content.append({
                    
#                         "text": text,
                    
#                     })
            
#             # ---------- LISTS ----------
#             elif elem.name == "ul":
#                 items = []
#                 for li in elem.find_all("li"):
#                     item_text = li.get_text(" ", strip=True)
#                     # List items के अंदर links
#                     item_links = []
#                     for a in li.find_all("a", href=True):
#                         item_links.append({
#                             "text": a.get_text(strip=True),
              
#                         })
                    
#                     items.append({
#                         "text": item_text,
             
#                     })
                
#                 full_content.append({
             
#                     "items": items
#                 })
            
#             # ---------- TABLES ----------
#             elif elem.name == "table":
#                 table_data = []
#                 headers = []
                
#                 # Headers निकालें
#                 thead = elem.find("thead")
#                 if thead:
#                     headers = [th.get_text(strip=True) for th in thead.find_all("th")]
                
#                 # Rows निकालें
#                 tbody = elem.find("tbody") or elem
#                 rows = tbody.find_all("tr")
                
#                 for tr in rows:
#                     row_data = {}
#                     cells = tr.find_all(["td", "th"])
                    
#                     if headers:  # Table के headers हैं
#                         for idx, cell in enumerate(cells):
#                             if idx < len(headers):
#                                 # Cell में links check करें
#                                 cell_links = []
#                                 for a in cell.find_all("a", href=True):
#                                     cell_links.append({
#                                         "text": a.get_text(strip=True),
                               
#                                     })
                                
#                                 cell_data = {
#                                     "text": cell.get_text(" ", strip=True),
                                  
#                                 }
#                                 row_data[headers[idx]] = cell_data
#                     else:  # No headers, array format में data
#                         row_cells = []
#                         for cell in cells:
#                             cell_links = []
#                             for a in cell.find_all("a", href=True):
#                                 cell_links.append({
#                                     "text": a.get_text(strip=True),
                   
#                                 })
                            
#                             row_cells.append({
#                                 "text": cell.get_text(" ", strip=True),
                       
#                             })
#                         table_data.append(row_cells)
#                         continue
                    
#                     if row_data:
#                         table_data.append(row_data)
                
#                 full_content.append({
               
#                     "headers": headers,
#                     "data": table_data,
#                     "rows_count": len(table_data)
#                 })
            
#             # ---------- IMAGES ----------
#             elif elem.name == "div" and elem.find("img"):
#                 img = elem.find("img")
#                 caption = elem.find("p", class_="_img-caption") or elem.find("strong", class_="_img-caption")
                
#                 full_content.append({
#                     "type": "image",
#                     "src": img.get("src"),
#                     "alt": img.get("alt", ""),
#                     "caption": caption.get_text(strip=True) if caption else None
#                 })

#     data["full_content"] = full_content

#     # ===================== KEY STATISTICS =====================
#     # Introduction से important statistics निकालें
#     key_stats = {}
    
#     # पहले paragraph से statistics
#     first_paragraph = intro_content[0] if intro_content else ""
#     if "19 participating NIFTs" in first_paragraph:
#         key_stats["total_institutes"] = 19
#     if "intake of 5076 seats" in first_paragraph:
#         key_stats["total_seats"] = 5076
    
#     data["key_statistics"] = key_stats

#     # ===================== SUMMARY DATA =====================
#     # Tables से summary data निकालें
#     summary = {}
    
#     for item in full_content:
#         if item.get("type") == "table":
#             table_headers = item.get("headers", [])
#             if "Institute" in table_headers and "2025 Rank" in table_headers:
#                 # Rankings table
#                 summary["rankings_2025"] = item.get("data", [])
#             elif "Name of the Institute" in table_headers and "India Today Ranking 2025" in table_headers:
#                 # Detailed rankings table
#                 summary["detailed_rankings"] = item.get("data", [])

#     data["summary_data"] = summary

#     return data

# def scrape_nift_fee_structure_data(driver):
#     driver.get(NIFT_COURSE_FEES)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}
#     data["meta"] = {}
    
#     # ---------- Updated Date ----------
#     updated_div = soup.select_one("div.blogdata_user > span")
#     if updated_div and "Updated on" in updated_div.text:
#         data["meta"]["updated_on"] = updated_div.get_text(strip=True)
    
#     # ---------- Author Information ----------
#     author_section = soup.find("div", class_="adp_user")
#     if author_section:
#         author_anchor = author_section.select_one("div.adp_usr_dtls > a")
#         name = None
#         if author_anchor:
#             name = "".join(author_anchor.find_all(string=True, recursive=False)).strip()
        
#         data["meta"]["author"] = {
#             "name": name,
#             "profile": author_anchor["href"] if author_anchor else None,
#             "role": author_section.select_one(".user_expert_level").get_text(strip=True)
#                     if author_section.select_one(".user_expert_level") else None,
#             "verified": bool(author_section.select_one("i.tickIcon"))
#         }
    
#     # ---------- Title ----------
#     h1 = soup.find("h1")
#     data["title"] = h1.get_text(strip=True) if h1 else "NIFT Fee Structure Information"
    
#     # ---------- Main Image ----------
#     picture = soup.find("picture")
#     if picture:
#         img_tag = picture.find("img")
#         if img_tag:
#             data["meta"]["img"] = img_tag.get("src")
#     else:
#         # Alternative image search
#         img_div = soup.find("div", class_="photo-widget-full")
#         if img_div:
#             img = img_div.find("img")
#             if img:
#                 data["meta"]["img"] = img.get("src")
    
#     # ===================== BLOG SUMMARY =====================
#     blog_summary = soup.find("div", id="blogSummary")
#     if blog_summary:
#         data["blog_summary"] = blog_summary.get_text(strip=True)
    
#     # ===================== INTRODUCTION SECTION =====================
#     intro_section = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#     intro_content = []
    
#     if intro_section:
#         # First paragraph (italic)
#         first_p = intro_section.find("p", style="text-align: justify;")
#         if first_p:
#             intro_content.append(first_p.get_text(" ", strip=True))
        
#         # Second paragraph (bold)
#         second_p = intro_section.find_all("p")[1] if len(intro_section.find_all("p")) > 1 else None
#         if second_p:
#             intro_content.append(second_p.get_text(" ", strip=True))
    
#     data["intro"] = intro_content
    
#     # ===================== FAQ SECTION =====================
#     faqs = []
#     sectional_faqs = soup.find_all("div", class_="sectional-faqs")
    
#     for faq_section in sectional_faqs:
#         questions = faq_section.find_all("div", class_="html-0")
#         answers = faq_section.find_all("div", class_="f61835")
        
#         for q, a in zip(questions, answers):
#             question = q.get_text(" ", strip=True).replace("Q:", "").strip()
            
#             # Extract answer text
#             answer_div = a.find("div", class_="cmsAContent")
#             if answer_div:
#                 answer_text = answer_div.get_text(" ", strip=True)
                
#                 # Extract tables from answer if present
#                 tables = []
#                 for table in answer_div.find_all("table"):
#                     table_data = extract_table_data(table)
#                     if table_data:
#                         tables.append(table_data)
                
#                 faqs.append({
#                     "question": question,
#                     "answer": answer_text,
#                     "tables": tables if tables else None
#                 })
    
#     data["faqs"] = faqs
    
#     # ===================== TABLE OF CONTENTS =====================
#     toc = []
#     toc_wrapper = soup.find("ul", id="tocWrapper")
#     if toc_wrapper:
#         for li in toc_wrapper.find_all("li"):
#             toc.append(li.get_text(" ", strip=True))
    
#     data["table_of_contents"] = toc
    
#     # ===================== MAIN CONTENT SECTIONS =====================
#     full_content = []
    
#     # Find all content sections
#     content_sections = soup.find_all("div", class_=["wikkiContents", "ab3f81"])
    
#     for section in content_sections:
#         # Skip FAQ sections since we already processed them
#         if "sectional-faqs" in section.get("class", []):
#             continue
        
#         # Process each element in the section
#         for elem in section.children:
#             if not hasattr(elem, "name"):
#                 continue
            
#             # ---------- HEADINGS ----------
#             if elem.name in ["h2", "h3"]:
#                 heading_text = elem.get_text(" ", strip=True)
#                 heading_id = elem.get("id", "")
                
#                 full_content.append({
#                     "type": "heading",
#                     "level": 2 if elem.name == "h2" else 3,
#                     "text": heading_text,
#                     "id": heading_id if heading_id else None
#                 })
            
#             # ---------- PARAGRAPHS ----------
#             elif elem.name == "p":
#                 text = elem.get_text(" ", strip=True)
#                 if text and len(text) > 10:  # Skip very short paragraphs
#                     full_content.append({
#                         "type": "paragraph",
#                         "text": text
#                     })
            
#             # ---------- LISTS ----------
#             elif elem.name == "ul":
#                 items = []
#                 for li in elem.find_all("li"):
#                     item_text = li.get_text(" ", strip=True)
#                     if item_text:
#                         items.append(item_text)
                
#                 if items:
#                     full_content.append({
#                         "type": "list",
#                         "items": items
#                     })
            
#             # ---------- TABLES ----------
#             elif elem.name == "table":
#                 table_data = extract_table_data(elem)
#                 if table_data:
#                     full_content.append({
#                         "type": "table",
#                         "data": table_data
#                     })
            
#             # ---------- DIV WITH TABLE ----------
#             elif elem.name == "div" and elem.find("table"):
#                 table_data = extract_table_data(elem.find("table"))
#                 if table_data:
#                     full_content.append({
#                         "type": "table",
#                         "data": table_data
#                     })
    
#     data["full_content"] = full_content
    
#     # ===================== FEE STRUCTURE SUMMARY =====================
#     # Extract key fee information from tables
#     fee_summary = {
#         "non_nri_fees": [],
#         "nri_fees": [],
#         "important_points": []
#     }
    
#     for item in full_content:
#         if item["type"] == "table":
#             table_text = str(item["data"]).lower()
            
#             # Check for Non-NRI fees
#             if "non-nri" in table_text or "non nri" in table_text:
#                 fee_summary["non_nri_fees"].append(item["data"])
            
#             # Check for NRI fees
#             elif "nri" in table_text and "non-nri" not in table_text:
#                 fee_summary["nri_fees"].append(item["data"])
    
#     # Extract important points
#     for item in full_content:
#         if item["type"] == "list":
#             list_text = " ".join(item["items"]).lower()
#             if any(keyword in list_text for keyword in ["pay", "fee", "deadline", "fine", "refund"]):
#                 fee_summary["important_points"] = item["items"]
    
#     data["fee_summary"] = fee_summary
    
#     # ===================== APPLICATION FEE INFO =====================
#     application_fee_section = None
#     for item in full_content:
#         if item["type"] == "paragraph" and "application fee" in item["text"].lower():
#             application_fee_section = item["text"]
#             break
    
#     if application_fee_section:
#         data["application_fee"] = application_fee_section
    
#     # ===================== POLL SECTION =====================
#     poll_data = {}
#     poll_container = soup.find("div", id="poll-container")
#     if poll_container:
#         poll_question = poll_container.find("div", class_="poll-question")
#         if poll_question:
#             poll_data["question"] = poll_question.get_text(strip=True)
        
#         poll_options = []
#         options_div = poll_container.find("div", class_="poll-options")
#         if options_div:
#             for option in options_div.find_all("div", class_="poll-option"):
#                 label = option.find("label")
#                 if label:
#                     poll_options.append(label.get_text(strip=True))
        
#         poll_data["options"] = poll_options
        
#         poll_info = poll_container.find("div", class_="poll-info")
#         if poll_info:
#             votes = poll_info.find("span", class_="poll-info-text")
#             if votes:
#                 poll_data["total_votes"] = votes.get_text(strip=True)
    
#     if poll_data:
#         data["poll"] = poll_data
    
#     # ===================== VIDEO SECTION =====================
#     videos = []
#     video_container = soup.find("div", class_="openVideoContainer")
#     if video_container:
#         video_items = video_container.find_all("li", class_="d87173")
#         for video in video_items:
#             iframe = video.find("iframe")
#             if iframe:
#                 video_data = {
#                     "src": iframe.get("src"),
#                     "title": iframe.get("title", "")
#                 }
#                 videos.append(video_data)
#             else:
#                 img = video.find("img")
#                 if img:
#                     video_data = {
#                         "thumbnail": img.get("src"),
#                         "alt": img.get("alt", "")
#                     }
#                     videos.append(video_data)
    
#     if videos:
#         data["videos"] = videos
    
#     return data


# def extract_table_data(table):
#     """Helper function to extract table data"""
#     table_data = {
#         "headers": [],
#         "rows": []
#     }
    
#     # Extract headers
#     thead = table.find("thead")
#     if thead:
#         for th in thead.find_all("th"):
#             table_data["headers"].append(th.get_text(" ", strip=True))
#     else:
#         # Check for th in first row
#         first_row = table.find("tr")
#         if first_row:
#             for th in first_row.find_all("th"):
#                 table_data["headers"].append(th.get_text(" ", strip=True))
    
#     # Extract rows
#     tbody = table.find("tbody") or table
#     rows = tbody.find_all("tr")
    
#     for tr in rows:
#         # Skip header row if we already have headers
#         if tr.find("th") and table_data["headers"]:
#             continue
        
#         row_data = []
#         cells = tr.find_all(["td", "th"])
        
#         for cell in cells:
#             cell_text = cell.get_text(" ", strip=True)
            
#             # Check for links in cell
#             links = []
#             for a in cell.find_all("a", href=True):
#                 links.append({
#                     "text": a.get_text(strip=True),
#                     "href": a.get("href")
#                 })
            
#             cell_data = {
#                 "text": cell_text,
#                 "links": links if links else None
#             }
#             row_data.append(cell_data)
        
#         if row_data:
#             table_data["rows"].append(row_data)
    
#     return table_data if table_data["rows"] else None

# def scrape_nift_seat_matrix_data(driver):
#     import re 
#     driver.get(NIFTS_SEAT)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}
#     data["meta"] = {}
    
#     # ---------- Updated Date ----------
#     updated_div = soup.select_one("div.blogdata_user > span")
#     if updated_div and "Updated on" in updated_div.text:
#         data["meta"]["updated_on"] = updated_div.get_text(strip=True)
    
#     # ---------- Author Information ----------
#     author_section = soup.find("div", class_="adp_user")
#     if author_section:
#         author_anchor = author_section.select_one("div.adp_usr_dtls > a")
#         name = None
#         if author_anchor:
#             name = "".join(author_anchor.find_all(string=True, recursive=False)).strip()
        
#         data["meta"]["author"] = {
#             "name": name,
#             "profile": author_anchor["href"] if author_anchor else None,
#             "role": author_section.select_one(".user_expert_level").get_text(strip=True)
#                     if author_section.select_one(".user_expert_level") else None,
#             "verified": bool(author_section.select_one("i.tickIcon"))
#         }
    
#     # ---------- Title ----------
#     h1 = soup.find("h1")
#     data["title"] = h1.get_text(strip=True) if h1 else "NIFT Seat Matrix Information"
    
#     # ---------- Main Image ----------
#     picture = soup.find("picture")
#     if picture:
#         img_tag = picture.find("img")
#         if img_tag:
#             data["meta"]["img"] = img_tag.get("src")
#     else:
#         # Alternative image search
#         img_div = soup.find("div", class_="photo-widget-full")
#         if img_div:
#             img = img_div.find("img")
#             if img:
#                 data["meta"]["img"] = img.get("src")
    
#     # ===================== BLOG SUMMARY =====================
#     blog_summary = soup.find("div", id="blogSummary")
#     if blog_summary:
#         data["blog_summary"] = blog_summary.get_text(strip=True)
    
#     # ===================== INTRODUCTION SECTION =====================
#     intro_section = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#     intro_content = []
    
#     if intro_section:
#         # First paragraph (italic)
#         first_p = intro_section.find("p", style="text-align: justify;")
#         if first_p:
#             intro_content.append(first_p.get_text(" ", strip=True))
        
#         # Second and third paragraphs
#         paragraphs = intro_section.find_all("p", style="text-align: justify;")
#         for p in paragraphs[1:]:  # Skip first paragraph
#             intro_content.append(p.get_text(" ", strip=True))
        
#         # Also check regular paragraphs
#         regular_ps = intro_section.find_all("p")
#         for p in regular_ps:
#             if p not in paragraphs:
#                 text = p.get_text(" ", strip=True)
#                 if text and len(text) > 10:
#                     intro_content.append(text)
    
#     data["intro"] = intro_content
    
#     # ===================== FAQ SECTION =====================
#     faqs = []
#     sectional_faqs = soup.find_all("div", class_="sectional-faqs")
    
#     for faq_section in sectional_faqs:
#         questions = faq_section.find_all("div", class_="html-0")
#         answers = faq_section.find_all("div", class_="f61835")
        
#         for q, a in zip(questions, answers):
#             question = q.get_text(" ", strip=True).replace("Q:", "").strip()
            
#             # Extract answer text
#             answer_div = a.find("div", class_="cmsAContent")
#             if answer_div:
#                 answer_text = answer_div.get_text(" ", strip=True)
                
#                 # Extract tables from answer if present
#                 tables = []
#                 for table in answer_div.find_all("table"):
#                     table_data = extract_table_data(table)
#                     if table_data:
#                         tables.append(table_data)
                
#                 faqs.append({
#                     "question": question,
#                     "answer": answer_text,
#                     "tables": tables if tables else None
#                 })
    
#     data["faqs"] = faqs
    
#     # ===================== TABLE OF CONTENTS =====================
#     toc = []
#     toc_wrapper = soup.find("ul", id="tocWrapper")
#     if toc_wrapper:
#         for li in toc_wrapper.find_all("li"):
#             toc.append(li.get_text(" ", strip=True))
    
#     data["table_of_contents"] = toc
    
#     # ===================== MAIN CONTENT SECTIONS =====================
#     full_content = []
    
#     # Find all content sections
#     content_sections = soup.find_all("div", class_=["wikkiContents", "ab3f81"])
    
#     for section in content_sections:
#         # Skip FAQ sections since we already processed them
#         if "sectional-faqs" in section.get("class", []):
#             continue
        
#         # Process each element in the section
#         for elem in section.children:
#             if not hasattr(elem, "name"):
#                 continue
            
#             # ---------- HEADINGS ----------
#             if elem.name in ["h2", "h3"]:
#                 heading_text = elem.get_text(" ", strip=True)
#                 heading_id = elem.get("id", "")
                
#                 full_content.append({
#                     "type": "heading",
#                     "level": 2 if elem.name == "h2" else 3,
#                     "text": heading_text,
#                     "id": heading_id if heading_id else None
#                 })
            
#             # ---------- PARAGRAPHS ----------
#             elif elem.name == "p":
#                 text = elem.get_text(" ", strip=True)
#                 if text and len(text) > 10:  # Skip very short paragraphs
#                     full_content.append({
#                         "type": "paragraph",
#                         "text": text
#                     })
            
#             # ---------- LISTS ----------
#             elif elem.name == "ul":
#                 items = []
#                 for li in elem.find_all("li"):
#                     item_text = li.get_text(" ", strip=True)
#                     if item_text:
#                         items.append(item_text)
                
#                 if items:
#                     full_content.append({
#                         "type": "list",
#                         "items": items
#                     })
            
#             # ---------- TABLES ----------
#             elif elem.name == "table":
#                 table_data = extract_table_data(elem)
#                 if table_data:
#                     full_content.append({
#                         "type": "table",
#                         "data": table_data
#                     })
            
#             # ---------- DIV WITH TABLE ----------
#             elif elem.name == "div" and elem.find("table"):
#                 table_data = extract_table_data(elem.find("table"))
#                 if table_data:
#                     full_content.append({
#                         "type": "table",
#                         "data": table_data
#                     })
    
#     data["full_content"] = full_content
    
#     # ===================== SEAT MATRIX SUMMARY =====================
#     seat_summary = {
#         "overall_seats": {},
#         "course_wise_seats": [],
#         "institute_wise_seats": [],
#         "category_wise_seats": {},
#         "year_wise_trend": {}
#     }
    
#     # Extract overall seat information from intro
#     for paragraph in intro_content:
#         if "total seats" in paragraph.lower() or "seats available" in paragraph.lower():
#             # Try to extract seat numbers
#             import re
#             seat_numbers = re.findall(r'\d{1,3}(?:,\d{3})*', paragraph)
#             if seat_numbers:
#                 seat_summary["overall_seats"]["total"] = seat_numbers[0]
    
#     # Extract year-wise seat trends
#     seat_trend_section = None
#     for item in full_content:
#         if item["type"] == "heading" and "seat matrix" in item["text"].lower():
#             # Look for list or table after this heading
#             seat_trend_section = item
    
#     if seat_trend_section:
#         # Look for lists with year information
#         for item in full_content:
#             if item["type"] == "list":
#                 list_text = " ".join(item["items"]).lower()
#                 if any(year in list_text for year in ["2022", "2023", "2024", "2025", "2026"]):
#                     for list_item in item["items"]:
#                         # Extract year and seat numbers
#                         year_match = re.search(r'(\d{4})', list_item)
#                         seat_match = re.search(r'(\d{1,3}(?:,\d{3})*)', list_item)
#                         if year_match and seat_match:
#                             year = year_match.group(1)
#                             seats = seat_match.group(1)
#                             seat_summary["year_wise_trend"][year] = seats
    
#     # Extract course-wise seat tables
#     for item in full_content:
#         if item["type"] == "table":
#             table_text = str(item["data"]).lower()
            
#             # Check for course-wise seats
#             if any(course in table_text for course in ["b.des", "b.f.tech", "m.des", "m.f.m", "m.f.tech"]):
#                 seat_summary["course_wise_seats"].append(item["data"])
            
#             # Check for institute-wise seats
#             elif any(institute in table_text for institute in ["bengaluru", "chennai", "delhi", "mumbai", "kolkata"]):
#                 seat_summary["institute_wise_seats"].append(item["data"])
            
#             # Check for category-wise seats (All India, State Domicile, Foreign Nationals)
#             elif any(category in table_text for category in ["all india", "state domicile", "foreign nationals", "nri"]):
#                 seat_summary["category_wise_seats"] = item["data"]
    
#     data["seat_summary"] = seat_summary
    
#     # ===================== KEY STATISTICS =====================
#     key_stats = {}
    
#     # Extract total seats from intro
#     for paragraph in intro_content:
#         if "5,289 seats" in paragraph or "5289 seats" in paragraph:
#             key_stats["total_seats_2026"] = 5289
#         elif "4,837 seats" in paragraph or "4837 seats" in paragraph:
#             key_stats["total_seats_2025"] = 4837
#         elif "19 participating" in paragraph or "19 campuses" in paragraph:
#             key_stats["total_campuses"] = 19
    
#     # Extract from tables
#     for item in full_content:
#         if item["type"] == "table":
#             table_data = item["data"]
#             table_text = str(table_data).lower()
            
#             if "total" in table_text and "seats" in table_text:
#                 # Try to find total seats in table
#                 for row in table_data.get("rows", []):
#                     row_text = str(row).lower()
#                     if "total" in row_text:
#                         # Extract numbers from this row
#                         numbers = re.findall(r'\d{1,3}(?:,\d{3})*', str(row))
#                         if numbers:
#                             key_stats["table_total_seats"] = numbers[-1]
    
#     data["key_statistics"] = key_stats
    
#     # ===================== ADMISSION PROCESS INFO =====================
#     admission_process = []
#     for item in full_content:
#         if item["type"] == "paragraph" and any(keyword in item["text"].lower() for keyword in ["admission", "process", "cat", "gat", "situation test"]):
#             admission_process.append(item["text"])
    
#     if admission_process:
#         data["admission_process"] = admission_process
    
#     # ===================== POLL SECTION =====================
#     poll_data = {}
#     poll_container = soup.find("div", id="poll-container")
#     if poll_container:
#         poll_question = poll_container.find("div", class_="poll-question")
#         if poll_question:
#             poll_data["question"] = poll_question.get_text(strip=True)
        
#         poll_options = []
#         options_div = poll_container.find("div", class_="poll-options")
#         if options_div:
#             for option in options_div.find_all("div", class_="poll-option"):
#                 label = option.find("label")
#                 if label:
#                     poll_options.append(label.get_text(strip=True))
        
#         poll_data["options"] = poll_options
        
#         poll_info = poll_container.find("div", class_="poll-info")
#         if poll_info:
#             votes = poll_info.find("span", class_="poll-info-text")
#             if votes:
#                 poll_data["total_votes"] = votes.get_text(strip=True)
    
#     if poll_data:
#         data["poll"] = poll_data
    
#     # ===================== VIDEO SECTION =====================
#     videos = []
#     video_container = soup.find("div", class_="openVideoContainer")
#     if video_container:
#         video_items = video_container.find_all("li", class_="d87173")
#         for video in video_items:
#             iframe = video.find("iframe")
#             if iframe:
#                 video_data = {
#                     "src": iframe.get("src"),
#                     "title": iframe.get("title", "")
#                 }
#                 videos.append(video_data)
#             else:
#                 img = video.find("img")
#                 if img:
#                     video_data = {
#                         "thumbnail": img.get("src"),
#                         "alt": img.get("alt", "")
#                     }
#                     videos.append(video_data)
    
#     if videos:
#         data["videos"] = videos
    
#     # ===================== RECOMMENDED COLLEGES SECTION =====================
#     recommended_colleges = []
#     reco_section = soup.find("div", class_="rwsBody")
#     if reco_section:
#         college_cards = reco_section.find_all("div", class_="collegCard")
#         for card in college_cards:
#             college_info = {}
            
#             # College name
#             name_elem = card.find("strong", class_="mainH")
#             if name_elem:
#                 college_info["name"] = name_elem.get_text(strip=True)
            
#             # Location
#             location_elem = card.find("div", class_="location")
#             if location_elem:
#                 college_info["location"] = location_elem.get_text(strip=True)
            
#             # Courses offered
#             courses_elem = card.find("div", class_="bluLinkBox")
#             if courses_elem:
#                 college_info["courses"] = courses_elem.get_text(strip=True)
            
#             # Total fees
#             fees_elem = card.find("span", class_="comma")
#             if fees_elem:
#                 college_info["total_fees"] = fees_elem.get_text(strip=True)
            
#             if college_info:
#                 recommended_colleges.append(college_info)
    
#     if recommended_colleges:
#         data["recommended_colleges"] = recommended_colleges
    
#     return data


# def extract_table_data(table):
#     """Helper function to extract table data"""
#     table_data = {
#         "headers": [],
#         "rows": []
#     }
    
#     # Extract headers
#     thead = table.find("thead")
#     if thead:
#         for th in thead.find_all("th"):
#             table_data["headers"].append(th.get_text(" ", strip=True))
#     else:
#         # Check for th in first row
#         first_row = table.find("tr")
#         if first_row:
#             for th in first_row.find_all("th"):
#                 table_data["headers"].append(th.get_text(" ", strip=True))
    
#     # Extract rows
#     tbody = table.find("tbody") or table
#     rows = tbody.find_all("tr")
    
#     for tr in rows:
#         # Skip header row if we already have headers
#         if tr.find("th") and table_data["headers"]:
#             continue
        
#         row_data = []
#         cells = tr.find_all(["td", "th"])
        
#         for cell in cells:
#             cell_text = cell.get_text(" ", strip=True)
            
#             # Check for links in cell
#             links = []
#             for a in cell.find_all("a", href=True):
#                 links.append({
#                     "text": a.get_text(strip=True),
#                     "href": a.get("href")
#                 })
            
#             cell_data = {
#                 "text": cell_text,
#                 "links": links if links else None
#             }
#             row_data.append(cell_data)
        
#         if row_data:
#             table_data["rows"].append(row_data)
    
#     return table_data if table_data["rows"] else None

# def scrape_interview_tips_article(driver):

#     import re
#     driver.get(NIFTS_INTERVIEWS)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}
#     data["meta"] = {}
    
#     try:
#         # ---------- Updated Date ----------
#         updated_div = soup.select_one("div.blogdata_user > span")
#         if updated_div:
#             data["meta"]["updated_on"] = updated_div.get_text(strip=True)
        
#         # ---------- Author Information ----------
#         author_section = soup.find("div", class_="adp_user")
#         if author_section:
#             author_anchor = author_section.select_one("div.adp_usr_dtls > a")
#             name = None
#             if author_anchor:
#                 name = "".join(author_anchor.find_all(string=True, recursive=False)).strip()
            
#             data["meta"]["author"] = {
#                 "name": name,
#                 "profile": author_anchor["href"] if author_anchor else None,
#                 "role": author_section.select_one(".user_expert_level").get_text(strip=True)
#                         if author_section.select_one(".user_expert_level") else None,
#                 "verified": bool(author_section.select_one("i.tickIcon"))
#             }
        
#         # ---------- Main Image ----------
#         # Look for image in the photo-widget-full div
#         img_div = soup.find("div", class_="photo-widget-full")
#         if img_div:
#             img_tag = img_div.find("img")
#             if img_tag:
#                 data["meta"]["img"] = img_tag.get("src")
        
#         # ---------- Blog Title ----------
#         title_h1 = soup.find("h1")
#         if title_h1:
#             data["title"] = title_h1.get_text(strip=True)
#         else:
#             data["title"] = "10 Tips to Crack Interview for Design Courses at NID, NIFT & IIT"
        
#         # ===================== BLOG SUMMARY =====================
#         blog_summary = soup.find("div", id="blogSummary")
#         if blog_summary:
#             data["blog_summary"] = blog_summary.get_text(strip=True)
        
#         # ===================== INTRODUCTION SECTION =====================
#         intro_section = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#         intro_content = []
        
#         if intro_section:
#             # Get the italic text from the figure div
#             figure_div = intro_section.find("div", class_="figure")
#             if figure_div:
#                 em_text = figure_div.find("em")
#                 if em_text:
#                     intro_content.append(em_text.get_text(" ", strip=True))
            
#             # Get the first paragraph after the image
#             paragraphs = intro_section.find_all("p")
#             for p in paragraphs:
#                 text = p.get_text(" ", strip=True)
#                 if text and len(text) > 20:
#                     intro_content.append(text)
#                     break  # Only take the first main paragraph
        
#         data["intro"] = intro_content
        
#         # ===================== TABLE OF CONTENTS =====================
#         # This article doesn't have a TOC in the HTML, but we can extract headings
#         toc = []
        
#         # Extract all h2 headings for TOC
#         all_headings = soup.find_all(["h2", "h3"])
#         for heading in all_headings:
#             heading_text = heading.get_text(" ", strip=True)
#             if heading_text:
#                 toc.append(heading_text)
        
#         data["table_of_contents"] = toc
        
#         # ===================== MAIN CONTENT EXTRACTION =====================
#         full_content = []
        
#         # Get the main content div
#         main_content_div = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
        
#         if main_content_div:
#             # Process all elements in order
#             for element in main_content_div.descendants:
#                 if element.name is None:
#                     continue
                
#                 # Skip certain elements
#                 if element.name in ["script", "style", "svg", "path"]:
#                     continue
                
#                 # Skip advertisement divs
#                 if element.name == "div" and "DFPRecoWrapper" in element.get("class", []):
#                     continue
#                 if element.name == "span" and "onSiteDFPReco_new" in element.get("class", []):
#                     continue
                
#                 # HEADINGS
#                 if element.name in ["h2", "h3"]:
#                     heading_text = element.get_text(" ", strip=True)
#                     heading_id = element.get("id", "")
                    
#                     if heading_text:
#                         full_content.append({
#                             "type": "heading",
#                             "level": int(element.name[1]),
#                             "text": heading_text,
#                             "id": heading_id if heading_id else None
#                         })
                
#                 # PARAGRAPHS
#                 elif element.name == "p":
#                     # Skip if it's just whitespace
#                     text = element.get_text(" ", strip=True)
#                     if text and len(text) > 10:
#                         full_content.append({
#                             "type": "paragraph",
#                             "text": text
#                         })
                
#                 # LISTS
#                 elif element.name in ["ul", "ol"]:
#                     items = []
#                     for li in element.find_all("li"):
#                         item_text = li.get_text(" ", strip=True)
#                         if item_text:
#                             items.append(item_text)
                    
#                     if items:
#                         full_content.append({
#                             "type": "list",
#                             "items": items
#                         })
        
#         data["full_content"] = full_content
        
#         # ===================== TIPS EXTRACTION =====================
#         tips = []
        
#         # Look for numbered tips (like "1.", "2.", etc.)
#         for item in full_content:
#             if item["type"] == "paragraph" and re.match(r'^\d+\.', item["text"]):
#                 # This is a tip
#                 tip_text = item["text"]
#                 tip_number = re.match(r'^(\d+)\.', tip_text).group(1)
                
#                 # Look for the list that follows this tip
#                 tip_details = []
#                 idx = full_content.index(item)
                
#                 # Check next items for lists
#                 for next_item in full_content[idx+1:]:
#                     if next_item["type"] == "list":
#                         tip_details.extend(next_item["items"])
#                         break
                
#                 tips.append({
#                     "tip_number": int(tip_number),
#                     "tip_title": tip_text,
#                     "details": tip_details
#                 })
        
#         data["tips"] = tips
        
#         # ===================== VIDEO SECTION =====================
#         videos = []
#         video_container = soup.find("div", class_="openVideoContainer")
        
#         if video_container:
#             video_items = video_container.find_all("li", class_="d87173")
#             for video in video_items:
#                 video_data = {}
                
#                 # Check for iframe (embedded video)
#                 iframe = video.find("iframe")
#                 if iframe:
#                     video_data["type"] = "embedded"
#                     video_data["src"] = iframe.get("src")
#                     video_data["title"] = iframe.get("title", "")
#                 else:
#                     # Check for thumbnail image
#                     img = video.find("img")
#                     if img:
#                         video_data["type"] = "thumbnail"
#                         video_data["thumbnail"] = img.get("src")
#                         video_data["alt"] = img.get("alt", "")
                    
#                     # Get video title
#                     title_div = video.find("div", class_="ada2b9")
#                     if title_div:
#                         video_data["title"] = title_div.get_text(strip=True)
                
#                 if video_data:
#                     videos.append(video_data)
        
#         data["videos"] = videos
        
#         # ===================== KEY INSTITUTIONS MENTIONED =====================
#         institutions = []
        
#         # Look for institution links in the content
#         for item in full_content:
#             if item["type"] == "paragraph":
#                 text = item["text"]
#                 # Look for institution mentions
#                 institution_keywords = ["NIFT", "NID", "IIT", "CEED", "IISc"]
#                 for keyword in institution_keywords:
#                     if keyword in text:
#                         if keyword not in institutions:
#                             institutions.append(keyword)
        
#         data["institutions_mentioned"] = institutions
        
#         # ===================== SOCIAL SHARING INFO =====================
#         social_links = []
#         share_widget = soup.find("div", class_="shareWidget-btm")
        
#         if share_widget:
#             social_anchors = share_widget.find_all("a", href=True)
#             for a in social_anchors:
#                 platform = "unknown"
#                 if "facebook.com" in a["href"]:
#                     platform = "facebook"
#                 elif "twitter.com" in a["href"]:
#                     platform = "twitter"
#                 elif "linkedin.com" in a["href"]:
#                     platform = "linkedin"
#                 elif "mailto:" in a["href"]:
#                     platform = "email"
                
#                 social_links.append({
#                     "platform": platform,
#                     "url": a["href"]
#                 })
        
#         data["social_sharing"] = social_links
        
#         # ===================== AUTHOR BIO SECTION =====================
#         author_bio = {}
#         author_bio_section = soup.find("div", class_="_container abt-athr-wrap")
        
#         if author_bio_section:
#             # Get author image
#             author_img = author_bio_section.find("img", class_="athr-img")
#             if author_img:
#                 author_bio["image"] = author_img.get("src")
            
#             # Get author name and role
#             author_name_div = author_bio_section.find("div", class_="athr-nm-deg")
#             if author_name_div:
#                 name_link = author_name_div.find("a")
#                 if name_link:
#                     author_bio["name"] = name_link.get_text(strip=True)
#                     author_bio["profile"] = name_link.get("href")
                
#                 role_div = author_name_div.find("div", class_="desigTxt")
#                 if role_div:
#                     author_bio["role"] = role_div.get_text(strip=True)
            
#             # Get author bio text
#             bio_div = author_bio_section.find("div", class_="abtd")
#             if bio_div:
#                 bio_paragraphs = bio_div.find_all("p")
#                 if bio_paragraphs:
#                     author_bio["bio"] = bio_paragraphs[0].get_text(strip=True)
        
#         data["author_bio"] = author_bio
        
#         # ===================== FEEDBACK SECTION =====================
#         feedback = {}
#         feedback_section = soup.find("div", id="feedbackSection")
#         if feedback_section:
#             feedback = {
#                 "has_feedback": True,
#                 "rating_stars": 5
#             }
        
#         data["feedback_section"] = feedback
        
#         # ===================== CONTENT SUMMARY =====================
#         content_summary = {
#             "total_sections": len([item for item in full_content if item["type"] == "heading" and item["level"] == 2]),
#             "total_tips": len(tips),
#             "total_paragraphs": len([item for item in full_content if item["type"] == "paragraph"]),
#             "total_videos": len(videos),
#             "main_topics": [item["text"] for item in full_content if item["type"] == "heading" and item["level"] == 2]
#         }
        
#         data["content_summary"] = content_summary
        
#     except Exception as e:
#         print(f"Error in scrape_interview_tips_article: {e}")
#         # Return minimal structure if error occurs
#         data = {
#             "meta": {},
#             "title": "10 Tips to Crack Interview for Design Courses at NID, NIFT & IIT",
#             "blog_summary": "",
#             "intro": [],
#             "table_of_contents": [],
#             "full_content": [],
#             "tips": [],
#             "videos": [],
#             "institutions_mentioned": [],
#             "social_sharing": [],
#             "author_bio": {},
#             "feedback_section": {},
#             "content_summary": {}
#         }
    
#     return data


# Helper function for extracting table data (if needed)
# def extract_table_data(table):
#     """Helper function to extract table data from HTML table"""
#     try:
#         table_data = {
#             "headers": [],
#             "rows": []
#         }
        
#         # Extract headers
#         headers = []
        
#         # Try thead first
#         thead = table.find("thead")
#         if thead:
#             for th in thead.find_all("th"):
#                 text = th.get_text(" ", strip=True)
#                 if text:
#                     headers.append(text)
        
#         # If no thead, check first row for th
#         if not headers:
#             first_row = table.find("tr")
#             if first_row:
#                 for th in first_row.find_all("th"):
#                     text = th.get_text(" ", strip=True)
#                     if text:
#                         headers.append(th)
        
#         # Extract header text from elements
#         table_data["headers"] = []
#         for header in headers:
#             if hasattr(header, 'get_text'):
#                 text = header.get_text(" ", strip=True)
#             else:
#                 text = str(header)
#             if text:
#                 table_data["headers"].append(text)
        
#         # Extract rows
#         rows = table.find_all("tr")
#         for tr in rows:
#             # Skip if this is a header row we already processed
#             if tr in [h.parent for h in headers if hasattr(h, 'parent')]:
#                 continue
            
#             row_data = []
#             cells = tr.find_all(["td", "th"])
            
#             for cell in cells:
#                 # Skip if this cell was used as header
#                 if cell in headers:
#                     continue
                    
#                 cell_text = cell.get_text(" ", strip=True)
                
#                 # Check for links
#                 links = []
#                 for a in cell.find_all("a", href=True):
#                     links.append({
#                         "text": a.get_text(strip=True),
#                         "href": a["href"]
#                     })
                
#                 row_data.append({
#                     "text": cell_text,
#                     "links": links if links else None
#                 })
            
#             if row_data:
#                 table_data["rows"].append(row_data)
        
#         return table_data if table_data["rows"] or table_data["headers"] else None
        
#     except Exception as e:
#         print(f"Error in extract_table_data: {e}")
#         return None

# def scrape_nift_placement(driver):

#     import re
#     driver.get(NIFTS_PLACEMENT)
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     data = {}
#     data["meta"] = {}
    
#     try:
#         # ---------- Updated Date ----------
#         updated_div = soup.select_one("div.blogdata_user > span")
#         if updated_div:
#             data["meta"]["updated_on"] = updated_div.get_text(strip=True)
        
#         # ---------- Author Information ----------
#         author_section = soup.find("div", class_="adp_user")
#         if author_section:
#             author_anchor = author_section.select_one("div.adp_usr_dtls > a")
#             name = None
#             if author_anchor:
#                 name = "".join(author_anchor.find_all(string=True, recursive=False)).strip()
            
#             data["meta"]["author"] = {
#                 "name": name,
#                 "profile": author_anchor["href"] if author_anchor else None,
#                 "role": author_section.select_one(".user_expert_level").get_text(strip=True)
#                         if author_section.select_one(".user_expert_level") else None,
#                 "verified": bool(author_section.select_one("i.tickIcon"))
#             }
        
#         # ---------- Main Image ----------
#         picture = soup.find("picture")
#         if picture:
#             img_tag = picture.find("img")
#             if img_tag:
#                 data["meta"]["img"] = img_tag.get("src")
        
#         # ---------- Blog Title ----------
#         title_h1 = soup.find("h1")
#         if title_h1:
#             data["title"] = title_h1.get_text(strip=True)
#         else:
#             data["title"] = "NIFT Placements"
        
#         # ===================== BLOG SUMMARY =====================
#         blog_summary = soup.find("div", id="blogSummary")
#         if blog_summary:
#             data["blog_summary"] = blog_summary.get_text(strip=True)
        
#         # ===================== INTRODUCTION SECTION =====================
#         intro_section = soup.find("div", id="wikkiContents_multi_ADP_undefined_ua_0")
#         intro_content = []
        
#         if intro_section:
#             paragraphs = intro_section.find_all("p")
#             for p in paragraphs:
#                 text = p.get_text(" ", strip=True)
#                 if text and len(text) > 20:
#                     intro_content.append(text)
        
#         data["intro"] = intro_content
        
#         # ===================== TABLE OF CONTENTS =====================
#         toc = []
#         toc_wrapper = soup.find("ul", id="tocWrapper")
#         if toc_wrapper:
#             for li in toc_wrapper.find_all("li"):
#                 toc_item = li.get_text(" ", strip=True)
#                 if toc_item:
#                     toc.append(toc_item)
        
#         data["table_of_contents"] = toc
        
#         # ===================== MAIN CONTENT EXTRACTION =====================
#         full_content = []
        
#         # Get all wikkiContents divs
#         content_divs = soup.find_all("div", class_="wikkiContents")
        
#         for div in content_divs:
#             # Skip empty divs
#             if not div.get_text(strip=True):
#                 continue
                
#             # Process elements in order
#             for element in div.children:
#                 if element.name is None:
#                     continue
                
#                 # HEADINGS
#                 if element.name in ["h2", "h3", "h4"]:
#                     heading_text = element.get_text(" ", strip=True)
#                     heading_id = element.get("id", "")
                    
#                     if heading_text:
#                         full_content.append({
                      
#                             "text": heading_text,
                          
#                         })
                
#                 # PARAGRAPHS (skip FAQ ones)
#                 elif element.name == "p":
#                     # Skip FAQ paragraphs
#                     if 'fQ' in element.get('class', []) or 'fA' in element.get('class', []):
#                         continue
#                     if element.parent and 'faqWrapper' in element.parent.get('id', ''):
#                         continue
                    
#                     text = element.get_text(" ", strip=True)
#                     if text and len(text) > 20:
#                         full_content.append({
                            
#                             "text": text
#                         })
                
#                 # LISTS
#                 elif element.name in ["ul", "ol"]:
#                     # Skip FAQ lists
#                     if element.parent and 'faqWrapper' in element.parent.get('id', ''):
#                         continue
                    
#                     items = []
#                     for li in element.find_all("li"):
#                         item_text = li.get_text(" ", strip=True)
#                         if item_text:
#                             items.append(item_text)
                    
#                     if items:
#                         full_content.append({
                         
#                             "items": items
#                         })
                
#                 # TABLES
#                 elif element.name == "table":
#                     # Skip FAQ tables
#                     if element.parent and 'faqWrapper' in element.parent.get('id', ''):
#                         continue
                    
#                     table_data = extract_table_data(element)
#                     if table_data:
#                         full_content.append({
                        
#                             "data": table_data
#                         })
                
#                 # SPECIAL DIVS
#                 elif element.name == "div" and element.get("style"):
#                     style = element.get("style", "")
#                     if "border:" in style and "background:" in style:
#                         text = element.get_text(" ", strip=True)
#                         if text and len(text) > 20:
#                             full_content.append({
                            
#                                 "text": text
#                             })
        
#         data["full_content"] = full_content
        
#         # ===================== FAQ SECTION =====================
#         faqs = []
#         faq_wrapper = soup.find("div", id="faqWrapper_last")
        
#         if faq_wrapper:
#             questions = faq_wrapper.find_all("p", class_="fQ")
#             answers = faq_wrapper.find_all("div", class_="fA")
            
#             for q, a in zip(questions, answers):
#                 question = q.get_text(" ", strip=True)
#                 question = re.sub(r'^Q\.\s*', '', question)
                
#                 answer_text = a.get_text(" ", strip=True)
#                 answer_text = re.sub(r'^A\.\s*', '', answer_text)
                
#                 if question and answer_text:
#                     faqs.append({
#                         "question": question.strip(),
#                         "answer": answer_text.strip()
#                     })
        
#         data["faqs"] = faqs
        
#         # ===================== PLACEMENT DATA EXTRACTION =====================
#         placement_data = {
#             "phases": {},
#             "salary_data": {},
#             "recruiters": {},
#             "skill_sets": {},
#             "company_types": {}
#         }
        
#         # Safely extract placement data
#         for item in full_content:
#             # Check if item has 'type' key
#             if not isinstance(item, dict) or 'type' not in item:
#                 continue
                
#             if item["type"] == "heading" and "Phase" in item["text"]:
#                 # Look for table after this heading
#                 idx = full_content.index(item)
#                 for next_item in full_content[idx+1:]:
#                     if isinstance(next_item, dict) and next_item.get("type") == "table":
#                         placement_data["phases"]["schedule"] = next_item["data"]
#                         break
            
#             elif item["type"] == "table":
#                 table_text = str(item.get("data", "")).lower()
                
#                 if "highest salary" in table_text or "average salary" in table_text:
#                     placement_data["salary_data"] = item["data"]
#                 elif "types of firms" in table_text:
#                     placement_data["company_types"] = item["data"]
#                 elif "skill set" in table_text:
#                     placement_data["skill_sets"] = item["data"]
#                 elif "past recruiters" in table_text:
#                     placement_data["recruiters"] = item["data"]
        
#         data["placement_data"] = placement_data
        
#         # ===================== KEY STATISTICS =====================
#         key_stats = {}
        
#         # Extract salary mentions
#         for paragraph in intro_content:
#             salary_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:lakh|lpa|LPA)', paragraph, re.IGNORECASE)
#             if salary_matches:
#                 key_stats["salary_mentions"] = salary_matches
            
#             if 'phase' in paragraph.lower():
#                 key_stats["placement_phases"] = 2
        
#         # Extract highest salary
#         if placement_data.get("salary_data"):
#             highest_salary = 0
#             for row in placement_data["salary_data"].get("rows", []):
#                 for cell in row:
#                     if isinstance(cell, dict):
#                         cell_text = cell["text"]
#                     else:
#                         cell_text = str(cell)
                    
#                     salary_match = re.search(r'(?:Rs\.|INR)\s*(\d+(?:\.\d+)?)\s*(?:lpa|LPA)', cell_text, re.IGNORECASE)
#                     if salary_match:
#                         try:
#                             salary = float(salary_match.group(1))
#                             if salary > highest_salary:
#                                 highest_salary = salary
#                         except ValueError:
#                             continue
            
#             if highest_salary > 0:
#                 key_stats["highest_salary_lpa"] = highest_salary
        
#         data["key_statistics"] = key_stats
        
#         # ===================== SOCIAL SHARING INFO =====================
#         social_links = []
#         share_widget = soup.find("div", class_="shareWidget-btm")
#         if share_widget:
#             social_anchors = share_widget.find_all("a", href=True)
#             for a in social_anchors:
#                 platform = "unknown"
#                 if "facebook.com" in a["href"]:
#                     platform = "facebook"
#                 elif "twitter.com" in a["href"]:
#                     platform = "twitter"
#                 elif "linkedin.com" in a["href"]:
#                     platform = "linkedin"
#                 elif "mailto:" in a["href"]:
#                     platform = "email"
                
#                 social_links.append({
#                     "platform": platform,
#                     "url": a["href"]
#                 })
        
#         data["social_sharing"] = social_links
        
#         # ===================== DOWNLOAD INFO =====================
#         download_info = {}
#         download_div = soup.find("div", class_="dnld-btn")
#         if download_div:
#             download_text_elem = download_div.find("p")
#             download_link = download_div.find("a", href=True)
            
#             download_info = {
#                 "text": download_text_elem.get_text(strip=True) if download_text_elem else "",
#                 "link": download_link["href"] if download_link else None
#             }
        
#         data["download_info"] = download_info
        
#         # ===================== FEEDBACK SECTION =====================
#         feedback = {}
#         feedback_section = soup.find("div", id="feedbackSection")
#         if feedback_section:
#             feedback = {
#                 "has_feedback": True,
#                 "rating_stars": 5
#             }
        
#         data["feedback_section"] = feedback
        
#         # ===================== CONTENT SUMMARY =====================
#         content_summary = {
#             "total_sections": 0,
#             "total_tables": 0,
#             "total_faqs": len(faqs),
#             "total_paragraphs": 0,
#             "main_topics": []
#         }
        
#         for item in full_content:
#             if isinstance(item, dict):
#                 if item.get("type") == "heading" and item.get("level") == 2:
#                     content_summary["total_sections"] += 1
#                     if item.get("text"):
#                         content_summary["main_topics"].append(item["text"])
#                 elif item.get("type") == "table":
#                     content_summary["total_tables"] += 1
#                 elif item.get("type") == "paragraph":
#                     content_summary["total_paragraphs"] += 1
        
#         data["content_summary"] = content_summary
        
#     except Exception as e:
#         print(f"Error in scrape_nift_placement: {e}")
#         # Return minimal structure if error occurs
#         data = {
#             "meta": {},
#             "title": "NIFT Placements",
#             "blog_summary": "",
#             "intro": [],
#             "table_of_contents": [],
#             "full_content": [],
#             "faqs": [],
#             "placement_data": {},
#             "key_statistics": {},
#             "social_sharing": [],
#             "download_info": {},
#             "feedback_section": {},
#             "content_summary": {}
#         }
    
#     return data


# def extract_table_data(table):
#     """Helper function to extract table data from HTML table"""
#     try:
#         table_data = {
#             "headers": [],
#             "rows": []
#         }
        
#         # Extract headers
#         headers = []
        
#         # Try thead first
#         thead = table.find("thead")
#         if thead:
#             for th in thead.find_all("th"):
#                 text = th.get_text(" ", strip=True)
#                 if text:
#                     headers.append(text)
        
#         # If no thead, check first row for th
#         if not headers:
#             first_row = table.find("tr")
#             if first_row:
#                 for th in first_row.find_all("th"):
#                     text = th.get_text(" ", strip=True)
#                     if text:
#                         headers.append(th)
        
#         # Extract header text from elements
#         table_data["headers"] = []
#         for header in headers:
#             if hasattr(header, 'get_text'):
#                 text = header.get_text(" ", strip=True)
#             else:
#                 text = str(header)
#             if text:
#                 table_data["headers"].append(text)
        
#         # Extract rows
#         rows = table.find_all("tr")
#         for tr in rows:
#             # Skip if this is a header row we already processed
#             if tr in [h.parent for h in headers if hasattr(h, 'parent')]:
#                 continue
            
#             row_data = []
#             cells = tr.find_all(["td", "th"])
            
#             for cell in cells:
#                 # Skip if this cell was used as header
#                 if cell in headers:
#                     continue
                    
#                 cell_text = cell.get_text(" ", strip=True)
                
#                 # Check for links
#                 links = []
#                 for a in cell.find_all("a", href=True):
#                     links.append({
#                         "text": a.get_text(strip=True),
#                         "href": a["href"]
#                     })
                
#                 row_data.append({
#                     "text": cell_text,
#                     "links": links if links else None
#                 })
            
#             if row_data:
#                 table_data["rows"].append(row_data)
        
#         return table_data if table_data["rows"] or table_data["headers"] else None
        
#     except Exception as e:
#         print(f"Error in extract_table_data: {e}")
#         return None


def scrape_p_colleges_data(driver):
    driver.get(P_COLLEGE)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "page_title": None,
        "title": None,
        "description": None,
        "sections": []
    }

    # ===============================
    # MAIN WRAPPER
    wrapper = soup.find("div", id="EdContent_categoryPage")
    if not wrapper:
        return data

    # ===============================
    # PAGE TITLE (H1)
    h1 = wrapper.find("h1")
    if h1:
        data["page_title"] = h1.get_text(strip=True)
        data["title"] = data["page_title"]

    # ===============================
    # DESCRIPTION (FIRST P)
    faq_wrapper = wrapper.find("div", class_="faq__according-wrapper")
    if faq_wrapper:
        first_p = faq_wrapper.find("p")
        if first_p:
            data["description"] = first_p.get_text(" ", strip=True)

    # ===============================
    # SECTIONS (Location / Specialization / Entrance Exams)
    for section_div in faq_wrapper.find_all("div", recursive=False):

        h2 = section_div.find("h2")
        if not h2:
            continue

        section_data = {
            "title": h2.get_text(strip=True),
            "content": "",
            "tables": []
        }

        # -------- Paragraphs
        p_tags = section_div.find_all("p", recursive=False)
        paragraphs = []
        for p in p_tags:
            text = p.get_text(" ", strip=True)
            if text:
                paragraphs.append(text)

        section_data["content"] = " ".join(paragraphs)

        # -------- Tables
        for table in section_div.find_all("table"):
            table_data = extract_table_data_fixed(table)
            if table_data:
                section_data["tables"].append(table_data)

        data["sections"].append(section_data)

    return data
def extract_table_data_fixed(table):
    table_data = []

    for row in table.find_all("tr"):
        row_data = []
        for cell in row.find_all(["th", "td"]):
            text = " ".join(cell.get_text(" ", strip=True).split())
            if text:
                row_data.append(text)

        if row_data:
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
              "Bsc_in_interior_design":{
                   "overviews":extract_course_data(driver),
                   "courses":scrape_courses_overview_section(driver),
                #    "syllabus":extract_syllabus_overview(driver),
                #    "subject":scrape_mbbs_subjects_overview(driver),               
                #    "career":scrape_md_career(driver),
                   "addmission":scrape_addmission_2026_data(driver),
                #    "fees": scrape_mba_fees_overview(driver),
                  "POPULAR COLLEGE":scrape_p_colleges_data(driver),
                #   "career_after_MDes":scrape_mdes_career_data(driver),
                #   "NIFTS FEE STRUCTURE":{
                #     "LIFTS_OF_NIFTS":scrape_nift_admission_data(driver), 
                #     "NIFTS COURSE FEE":scrape_nift_fee_structure_data(driver),
                #     "NIFTS SEATS":scrape_nift_seat_matrix_data(driver),
                #     "NIFTS PLACEMENT":scrape_nift_placement(driver),
                #   },
                #   "NIFT_INTERVIEWS":scrape_interview_tips_article(driver),
                   
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

TEMP_FILE = "bscininteriordesign.tmp.json"
FINAL_FILE = "bscininteriordesign.json"

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

