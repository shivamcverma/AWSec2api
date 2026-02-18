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

PCOMBA_O_URL="https://www.shiksha.com/b-tech-bachelor-of-technology-chp"
PCOMBA_C_URL="https://www.shiksha.com/b-tech-bachelor-of-technology-courses-chp"
PCOMBA_MBA_SYLLABUS_URL = "https://www.shiksha.com/b-tech-bachelor-of-technology-syllabus-chp"
PCOMBA_MBA_CAREER_URL = "https://www.shiksha.com/b-tech-bachelor-of-technology-career-chp"
PCOMBA_MBA_ADDMISSION_2026_URL = "https://www.shiksha.com/b-tech-bachelor-of-technology-admission-chp"
PCOMBA_MBA_FEES_URL = "https://www.shiksha.com/b-tech-bachelor-of-technology-fees-chp"
PCOMBA_MBA_PGDM_URL = "https://www.shiksha.com/articles/btech-vs-bsc-which-is-a-better-career-option-after-class-12-blogId-72555"
PCOMBA_JMP_URL = "https://www.shiksha.com/engineering/articles/tips-towards-your-jee-mains-advanced-preparation-blogId-11721"
PCOMBA_QN_URL = "https://www.shiksha.com/tags/b-tech-tdp-413"
PCOMBA_QND_URL = "https://www.shiksha.com/tags/b-tech-tdp-413?type=discussion"


URLS = {
    "overviews":"https://www.shiksha.com/mba/cat-exam",
    "result":"https://www.shiksha.com/mba/cat-exam-results",
    "cut_off":"https://www.shiksha.com/mba/cat-exam-cutoff",
    "ans_key":"https://www.shiksha.com/mba/cat-exam-answer-key",
    "counselling":"https://www.shiksha.com/mba/cat-exam-counselling",
    "analysis":"https://www.shiksha.com/mba/cat-exam-analysis",
    "question_paper":"https://www.shiksha.com/mba/cat-exam-question-papers",
    "admit_card":"https://www.shiksha.com/mba/cat-exam-admit-card",
    "dates":"https://www.shiksha.com/mba/cat-exam-dates",
    "mock_test":"https://www.shiksha.com/mba/cat-exam-mocktest",
    "registration":"https://www.shiksha.com/mba/cat-exam-registration",
    "syllabus":"https://www.shiksha.com/mba/cat-exam-syllabus",
    "pattern":"https://www.shiksha.com/mba/cat-exam-pattern",
    "preparation":"https://www.shiksha.com/mba/cat-exam-preparation",
    "books":"https://www.shiksha.com/mba/cat-exam-books",
    "notification":"https://www.shiksha.com/mba/cat-exam-notification",
    "center":"https://www.shiksha.com/mba/cat-exam-centre",
    "news":"https://www.shiksha.com/mba/cat-exam-news",
    "accepting_college":"https://www.shiksha.com/mba/colleges/mba-colleges-accepting-cat-india?sby=popularity",
    "mba_with_low_fees":"https://www.shiksha.com/mba/articles/mba-colleges-in-india-with-low-fees-blogId-23533",
                   
}


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


def extract_course_data(driver):
    driver.get(PCOMBA_O_URL)
    time.sleep(5)
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
    # OVERVIEW SECTION
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
    # ELIGIBILITY SECTION
    # =====================================================
    eligibility_div = soup.find("section", id="chp_section_eligibility")
    if eligibility_div:
        content = []

        # Grab all relevant elements recursively
        for elem in eligibility_div.find_all(["h1","h2","h3","h4","h5","h6","p","table","div"], recursive=True):
            if elem.name in ["h1","h2","h3","h4","h5","h6"]:
                content.append({
                    "text": elem.get_text(" ", strip=True)
                })

            elif elem.name == "table":
                headers = [th.get_text(" ", strip=True) for th in elem.find_all("th")]
                rows_data = []
                for row in elem.find_all("tr")[1:]:
                    cols = row.find_all(["td", "th"])
                    row_dict = {}
                    for idx, col in enumerate(cols):
                        key = headers[idx] if idx < len(headers) else f"col_{idx}"
                        row_dict[key] = col.get_text(" ", strip=True)
                    rows_data.append(row_dict)
                content.append({
                    "headers": headers,
                    "rows": rows_data
                })

        faq_blocks = eligibility_div.find_all("div", class_="html-0 c5db62 listener")
        for faq in faq_blocks:
            # Extract question
            question_span = faq.find("span", string=lambda x: x and x.strip().startswith("Q:"))
            question_text = None
            if question_span:
                # The actual question text is in the next span after "Q:"
                spans = faq.find_all("span")
                if len(spans) > 1:
                    question_text = spans[1].get_text(" ", strip=True)

            # Extract answer
            answer_div = faq.find_next_sibling("div", class_="_16f53f")
            answer_text = ""
            if answer_div:
                # Get all paragraph texts inside answer div
                paragraphs = answer_div.find_all("p")
                if paragraphs:
                    answer_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
                else:
                    # Fallback: get all text inside answer div
                    answer_text = answer_div.get_text(" ", strip=True)

            if question_text and answer_text:
                content.append({
                    "question": question_text,
                    "answer": answer_text
                })

        data["eligibility_admission"] = content

    # =====================================================
    # POPULAR EXAMS & IIT SEATS
    # =====================================================
    popular_div = soup.find("div", id="wikkiContents_chp_section_popularexams_0")
    if popular_div:
        # 1. Popular Entrance Exams
        exams_table = popular_div.find("table")
        exams = []
        if exams_table:
            rows = exams_table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 3:
                    exams.append({
                        "exam_name": cols[0].get_text(strip=True),
                        "exam_dates": cols[1].get_text(strip=True),
                        "exam_schedule_link": cols[2].find("a")["href"] if cols[2].find("a") else None
                    })
        data["popular_exams"] = exams

        # 2. JEE Main Cutoff
        cutoff_table = popular_div.find("h3", string=lambda x: x and "JEE Main 2025 Cutoff" in x)
        cutoff_data = []
        if cutoff_table:
            table = cutoff_table.find_next("table")
            if table:
                headers = [th.get_text(strip=True) for th in table.find_all("th")]
                for row in table.find_all("tr")[1:]:
                    cols = row.find_all("td")
                    cutoff_data.append({headers[i]: cols[i].get_text(strip=True) for i in range(len(cols))})
        data["jee_main_cutoff_2025"] = cutoff_data

        # 3. IIT Seats (Delhi, Madras, Bombay)
        iit_seats = {}
        for h4 in popular_div.find_all("h4"):
            if "IIT" in h4.text and "BTech Seats" in h4.text:
                iit_name = h4.text.replace("BTech Seats","").strip()
                table = h4.find_next("table")
                seats = []
                if table:
                    headers = [th.get_text(strip=True) for th in table.find_all("th")]
                    for row in table.find_all("tr")[1:]:
                        cols = row.find_all("td")
                        seats.append({headers[i]: cols[i].get_text(strip=True) for i in range(len(cols))})
                iit_seats[iit_name] = seats
        data["iit_btech_seats"] = iit_seats

    # =====================================================
    # POPULAR SPECIALIZATIONS SECTION
    # =====================================================
    popular_specialization_div = soup.find("section", id="chp_section_popularspecialization")
    if popular_specialization_div:
        content = []
        
        # Main heading
        main_heading = popular_specialization_div.find("h2", class_="tbSec2")
        if main_heading:
            content.append({
                "text": main_heading.get_text(" ", strip=True)
            })
        
        # Introductory text
        intro_div = popular_specialization_div.find("div", class_="photo-widget-full")
        if intro_div:
            intro_text = intro_div.get_text(" ", strip=True)
            if intro_text:
                content.append({
                    "text": intro_text
                })
        
        # Specializations table
        specializations_table = popular_specialization_div.find("table")
        if specializations_table:
            # Extract table headers
            headers = [th.get_text(" ", strip=True) for th in specializations_table.find_all("th")]
            
            # Extract table rows
            rows_data = []
            for row in specializations_table.find_all("tr")[1:]:  # Skip header row
                cols = row.find_all(["td", "th"])
                row_dict = {}
                
                for idx, col in enumerate(cols):
                    key = headers[idx] if idx < len(headers) else f"col_{idx}"
                    row_dict[key] = col.get_text(" ", strip=True)
                
                rows_data.append(row_dict)
            
            content.append({
                "title": "BTech Specializations and Jobs",
                "headers": headers,
                "rows": rows_data
            })
        
        # Note text
        note_p = popular_specialization_div.find("p", string=lambda x: x and "Note" in x)
        if note_p:
            content.append({
                "text": note_p.get_text(" ", strip=True)
            })
        
        # Popular specializations list
        specialization_box = popular_specialization_div.find("div", class_="specialization-box")
        if specialization_box:
            specializations_list = []
            for li in specialization_box.find_all("li"):
                link = li.find("a", href=True)
                college_count = li.find("p")
                
                if link:
                    specializations_list.append({
                        "specialization": link.get_text(strip=True),
                        "college_count": college_count.get_text(strip=True) if college_count else None
                    })
            
            if specializations_list:
                content.append({
                    "title": "Popular Specializations by College Count",
                    "specializations": specializations_list
                })
        
        # FAQs
        faq_section = popular_specialization_div.find("div", id="sectional-faqs-0")
        if faq_section:
            faqs = []
            faq_blocks = faq_section.find_all("div", class_="html-0 c5db62 listener")
            
            for faq_block in faq_blocks:
                # Extract question
                question_spans = faq_block.find_all("span")
                question_text = None
                if len(question_spans) >= 2:
                    question_text = question_spans[1].get_text(" ", strip=True)
                
                # Extract answer from next sibling div
                answer_div = faq_block.find_next_sibling("div", class_="_16f53f")
                answer_text = ""
                if answer_div:
                    answer_content = answer_div.find("div", class_="cmsAContent")
                    if answer_content:
                        paragraphs = answer_content.find_all("p")
                        if paragraphs:
                            answer_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
                        else:
                            answer_text = answer_content.get_text(" ", strip=True)
                
                if question_text:
                    faqs.append({
                        "question": question_text,
                        "answer": answer_text if answer_text else None
                    })
            
            if faqs:
                content.append({
                    "questions": faqs
                })
        
        # Add the entire content to data dictionary
        data["popular_specializations"] = content

    # =====================================================
    # BTECH SYLLABUS & SUBJECTS SECTION
    # =====================================================
    syllabus_div = soup.find("section", id="chp_section_coursesyllabus")
    if syllabus_div:
        content = []
        
        # Main heading
        main_heading = syllabus_div.find("h2", class_="tbSec2")
        if main_heading:
            content.append({
                "text": main_heading.get_text(" ", strip=True)
            })
        
        # Introductory text
        intro_p = syllabus_div.find("p", style="text-align: justify;")
        if intro_p:
            content.append({
                "text": intro_p.get_text(" ", strip=True)
            })
        
        # Extract all specialization syllabus sections
        specializations = []
        
        # Find all syllabus sections (CSE, Electrical, Mechanical, AI)
        syllabus_headings = syllabus_div.find_all(["h3", "h2"])
        for heading in syllabus_headings:
            heading_text = heading.get_text(" ", strip=True)
            
            # Check if this is a specialization syllabus heading
            if any(keyword in heading_text for keyword in ["BTech CSE Syllabus", "BTech Electrical Engineering Syllabus", 
                                                          "BTech Mechanical Engineering Syllabus", "BTech in Artificial Intelligence Syllabus",
                                                          "B Tech Specialization-Wise Syllabus"]):
                
                specialization_section = {
                    "title": heading_text,
                    "description": "",
                    "semester_tables": []
                }
                
                # Get description after heading
                desc_p = heading.find_next("p")
                if desc_p:
                    specialization_section["description"] = desc_p.get_text(" ", strip=True)
                
                # Get syllabus table after heading
                table = heading.find_next("table")
                if table:
                    # Extract table data without links
                    table_data = []
                    
                    # Process all rows
                    for row in table.find_all("tr"):
                        row_data = []
                        for cell in row.find_all(["td", "th"]):
                            # Get only text, remove links
                            cell_text = cell.get_text(" ", strip=True)
                            row_data.append(cell_text)
                        
                        if row_data:  # Only add non-empty rows
                            table_data.append(row_data)
                    
                    if table_data:
                        specialization_section["semester_tables"] = table_data
                
                # Add note if present
                note_p = heading.find_next("p", string=lambda x: x and "Note -" in x)
                if note_p:
                    specialization_section["note"] = note_p.get_text(" ", strip=True)
                
                specializations.append(specialization_section)
        
        # Add specialization-wise syllabus links as text only
        links_section = syllabus_div.find("h2", string=lambda x: x and "B Tech Specialization-Wise Syllabus" in x)
        if links_section:
            links_table = links_section.find_next("table")
            if links_table:
                specialization_links = []
                
                # Process all rows
                rows = links_table.find_all("tr")
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 2:
                        # Get left and right column texts
                        left_text = cols[0].get_text(" ", strip=True)
                        right_text = cols[1].get_text(" ", strip=True) if len(cols) > 1 else ""
                        
                        if left_text:
                            specialization_links.append(left_text)
                        if right_text:
                            specialization_links.append(right_text)
                
                if specialization_links:
                    content.append({
                        "title": "Specialization-Wise Syllabus (Text Only)",
                        "syllabus_list": specialization_links
                    })
        
        # Useful links as text only
        useful_links_section = syllabus_div.find("p", string=lambda x: x and "Useful Link for B Tech Courses List" in x)
        if not useful_links_section:
            useful_links_section = syllabus_div.find("span", string=lambda x: x and "Useful Link for B Tech Courses List" in x)
        
        if useful_links_section:
            useful_links = []
            
            # Get the next 2 paragraphs after the heading
            next_elem = useful_links_section.find_next_sibling()
            link_count = 0
            
            while next_elem and link_count < 2:
                if next_elem.name == "p":
                    link_text = next_elem.get_text(" ", strip=True)
                    if link_text:
                        useful_links.append(link_text)
                        link_count += 1
                next_elem = next_elem.find_next_sibling()
            
            if useful_links:
                content.append({
                    "title": "Useful Information",
                    "info_items": useful_links
                })
        
        # FAQs
        faq_section = syllabus_div.find("div", id="sectional-faqs-0")
        if faq_section:
            faqs = []
            faq_blocks = faq_section.find_all("div", class_="html-0 c5db62 listener")
            
            for faq_block in faq_blocks:
                # Extract question
                question_spans = faq_block.find_all("span")
                question_text = None
                if len(question_spans) >= 2:
                    question_text = question_spans[1].get_text(" ", strip=True)
                
                # Extract answer from next sibling div
                answer_div = faq_block.find_next_sibling("div", class_="_16f53f")
                answer_text = ""
                if answer_div:
                    answer_content = answer_div.find("div", class_="cmsAContent")
                    if answer_content:
                        paragraphs = answer_content.find_all("p")
                        if paragraphs:
                            answer_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
                        else:
                            answer_text = answer_content.get_text(" ", strip=True)
                
                if question_text:
                    faqs.append({
                        "question": question_text,
                        "answer": answer_text if answer_text else None
                    })
            
            if faqs:
                content.append({
                    "questions": faqs
                })
        
        # Add specializations to content
        if specializations:
            content.append({
                "title": "BTech Syllabus by Specialization",
                "specializations": specializations
            })
        
        # Add the entire content to data dictionary
        data["btech_syllabus"] = content

    # =====================================================
    # BTECH SALARY & CAREER SCOPE SECTION (NEW SECTION ADDED)
    # =====================================================
    salary_div = soup.find("section", id="chp_section_salary")
    if salary_div:
        content = []
        
        # Main heading
        main_heading = salary_div.find("h2", class_="tbSec2")
        if main_heading:
            content.append({
                "text": main_heading.get_text(" ", strip=True)
            })
        
        # Introductory paragraph
        intro_p = salary_div.find("p", string=lambda x: x and "BTech is one of the most popular courses" in x)
        if intro_p:
            content.append({
                "text": intro_p.get_text(" ", strip=True)
            })
        
        # B Tech Salary and Jobs in India section
        salary_jobs_heading = salary_div.find("h3", string=lambda x: x and "B Tech Salary and Jobs in India" in x)
        if salary_jobs_heading:
            salary_section = {
                "title": salary_jobs_heading.get_text(" ", strip=True),
                "description": "",
                "industry_jobs": []
            }
            
            # Get description after heading
            next_elem = salary_jobs_heading.find_next_sibling()
            description_parts = []
            while next_elem and next_elem.name != "h4":
                if next_elem.name == "p":
                    description_parts.append(next_elem.get_text(" ", strip=True))
                next_elem = next_elem.find_next_sibling()
            
            if description_parts:
                salary_section["description"] = " ".join(description_parts)
            
            content.append(salary_section)
        
        # Extract all industry job tables
        industry_sections = []
        
        # Find all industry job sections (IT & Software, Automotive, Aerospace, etc.)
        industry_headings = salary_div.find_all("h4")
        for heading in industry_headings:
            heading_text = heading.get_text(" ", strip=True)
            
            if any(keyword in heading_text for keyword in ["IT & Software", "Automotive", "Aerospace", 
                                                         "Electrical & Electronics", "Mechanical", "Civil"]):
                industry_section = {
                    "industry": heading_text.replace("B Tech Jobs", "").replace("BTech Jobs", "").strip(),
                    "description": "",
                    "job_profiles": []
                }
                
                # Get description after heading
                desc_p = heading.find_next("p")
                if desc_p:
                    industry_section["description"] = desc_p.get_text(" ", strip=True)
                
                # Get job table after heading
                table = heading.find_next("table")
                if table:
                    # Extract table headers
                    headers = []
                    header_row = table.find("tr")
                    if header_row:
                        for th in header_row.find_all(["th", "td"]):
                            headers.append(th.get_text(" ", strip=True))
                    
                    # Extract job profiles data
                    rows = table.find_all("tr")[1:]  # Skip header row
                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        if len(cols) >= 3:
                            job_profile = {
                                "job_profile": cols[0].get_text(" ", strip=True),
                                "job_description": cols[1].get_text(" ", strip=True),
                                "average_salary": cols[2].get_text(" ", strip=True)
                            }
                            industry_section["job_profiles"].append(job_profile)
                
                # Add note if present
                note_p = heading.find_next("p", string=lambda x: x and "Note -" in x)
                if note_p:
                    industry_section["note"] = note_p.get_text(" ", strip=True)
                
                industry_sections.append(industry_section)
        
        # BTech Courses Top Recruiters section
        recruiters_heading = salary_div.find("h3", string=lambda x: x and "BTech Courses Top Recruiters" in x)
        if recruiters_heading:
            recruiters_section = {
                "title": recruiters_heading.get_text(" ", strip=True),
                "description": "",
                "recruiters_table": []
            }
            
            # Get description after heading
            desc_p = recruiters_heading.find_next("p")
            if desc_p:
                recruiters_section["description"] = desc_p.get_text(" ", strip=True)
            
#             # Get recruiters table
            table = recruiters_heading.find_next("table")
            if table:
                table_data = []
                rows = table.find_all("tr")
                for row in rows:
                    row_data = []
                    for cell in row.find_all(["td", "th"]):
                        row_data.append(cell.get_text(" ", strip=True))
                    if row_data:
                        table_data.append(row_data)
                
                recruiters_section["recruiters_table"] = table_data
            
            # Add note if present
            note_p = recruiters_heading.find_next("p", string=lambda x: x and "Note -" in x)
            if note_p:
                recruiters_section["note"] = note_p.get_text(" ", strip=True)
            
            content.append(recruiters_section)
        
        # BTech Placements in India section
        placements_heading = salary_div.find("h3", string=lambda x: x and "BTech Placements in India" in x)
        if placements_heading:
            placements_section = {
                "title": placements_heading.get_text(" ", strip=True),
                "description": "",
                "placements_table": []
            }
            
            # Get description after heading
            desc_p = placements_heading.find_next("p")
            if desc_p:
                placements_section["description"] = desc_p.get_text(" ", strip=True)
            
            # Get placements table
            table = placements_heading.find_next("table")
            if table:
                table_data = []
                rows = table.find_all("tr")
                for row in rows:
                    row_data = []
                    for cell in row.find_all(["td", "th"]):
                        row_data.append(cell.get_text(" ", strip=True))
                    if row_data:
                        table_data.append(row_data)
                
                placements_section["placements_table"] = table_data
            
            # Add note if present
            note_p = placements_heading.find_next("p", string=lambda x: x and "Note -" in x)
            if note_p:
                placements_section["note"] = note_p.get_text(" ", strip=True)
            
            content.append(placements_section)
        
        # Useful links as text only
        useful_links_heading = salary_div.find("p", string=lambda x: x and "Useful Links for B Tech Scope" in x)
        if not useful_links_heading:
            useful_links_heading = salary_div.find("span", string=lambda x: x and "Useful Links for B Tech Scope" in x)
        
        if useful_links_heading:
            useful_links = []
            
            # Get the next 2 paragraphs after the heading
            next_elem = useful_links_heading.find_next_sibling()
            link_count = 0
            
            while next_elem and link_count < 2:
                if next_elem.name == "p":
                    link_text = next_elem.get_text(" ", strip=True)
                    if link_text:
                        useful_links.append(link_text)
                        link_count += 1
                next_elem = next_elem.find_next_sibling()
            
            if useful_links:
                content.append({
                    "title": "Useful Links for B Tech Scope",
                    "info_items": useful_links
                })
        
        # Helpful links as text only
        helpful_links_heading = salary_div.find("p", string=lambda x: x and "Helpful Links for Jobs for BTech Freshers" in x)
        if not helpful_links_heading:
            helpful_links_heading = salary_div.find("span", string=lambda x: x and "Helpful Links for Jobs for BTech Freshers" in x)
        
        if helpful_links_heading:
            helpful_links = []
            
            # Get the next 2 paragraphs after the heading
            next_elem = helpful_links_heading.find_next_sibling()
            link_count = 0
            
            while next_elem and link_count < 2:
                if next_elem.name == "p":
                    link_text = next_elem.get_text(" ", strip=True)
                    if link_text:
                        helpful_links.append(link_text)
                        link_count += 1
                next_elem = next_elem.find_next_sibling()
            
            if helpful_links:
                content.append({
                    "title": "Helpful Links for BTech Freshers Jobs",
                    "info_items": helpful_links
                })
        
        # YouTube video iframe
        youtube_iframe = salary_div.find("iframe")
        if youtube_iframe and "youtube.com" in youtube_iframe.get("src", ""):
            content.append({
                "title": youtube_iframe.get("title", "Tips to Find Job as a Fresh BTech graduate"),
                "src": youtube_iframe["src"],
                "width": youtube_iframe.get("width", "560"),
                "height": youtube_iframe.get("height", "315")
            })
        
        # FAQs
        faq_section = salary_div.find("div", id="sectional-faqs-0")
        if faq_section:
            faqs = []
            faq_blocks = faq_section.find_all("div", class_="html-0 c5db62 listener")
            
            for faq_block in faq_blocks:
                # Extract question
                question_spans = faq_block.find_all("span")
                question_text = None
                if len(question_spans) >= 2:
                    question_text = question_spans[1].get_text(" ", strip=True)
                
                # Extract answer from next sibling div
                answer_div = faq_block.find_next_sibling("div", class_="_16f53f")
                answer_text = ""
                if answer_div:
                    answer_content = answer_div.find("div", class_="cmsAContent")
                    if answer_content:
                        paragraphs = answer_content.find_all("p")
                        if paragraphs:
                            answer_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
                        else:
                            answer_text = answer_content.get_text(" ", strip=True)
                    
                    # Extract tables from answer if any
                    answer_tables = []
                    for table in answer_div.find_all("table"):
                        table_data = []
                        rows = table.find_all("tr")
                        for row in rows:
                            row_data = []
                            for cell in row.find_all(["td", "th"]):
                                row_data.append(cell.get_text(" ", strip=True))
                            if row_data:
                                table_data.append(row_data)
                        
                        if table_data:
                            answer_tables.append(table_data)
                
                if question_text:
                    faq_item = {
                        "question": question_text,
                        "answer": answer_text if answer_text else None
                    }
                    
                    if answer_tables:
                        faq_item["tables"] = answer_tables
                    
                    faqs.append(faq_item)
            
            if faqs:
                content.append({
                    "questions": faqs
                })
        
        # Add industry sections to content
        if industry_sections:
            content.append({
                "title": "Industry-wise BTech Jobs and Salaries",
                "industries": industry_sections
            })
        
        # Add the entire content to data dictionary
        data["btech_salary_career"] = content

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
            else:
                if link and text.lower().startswith(("also read", "know more")):
                    target["related_links"].append({
                        "text": clean(link),
                        "url": link["href"]
                    })
                else:
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

def scrape_mba_syllabus(driver):
    driver.get(PCOMBA_MBA_SYLLABUS_URL)
    WebDriverWait(driver, 15)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {
        "title": None,
        "updated_on": None,
        "author": None,
        "courses": {
            "intro": {"paragraphs": []},
            "syllabus_faq": [],
            "btech_syllabus": [],  # ✅ NEW
            "btech_core_subjects": {
                "intro": "",
                "specializations": [],
                "specialization_links": [],
                "notes": [],
                
            },
            "faqs": [],
            "specializations":{}

        }
    }

    # ===== TITLE =====
    title_div = soup.find("div", class_="f48b")
    if title_div:
        data["title"] = clean(title_div.find("div"))

    # ===== UPDATED ON =====
    updated_div = soup.find("div", string=lambda x: x and "Updated on" in x)
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===== AUTHOR INFO =====
    author_block = soup.find("div", class_="be8c")
    if author_block:
        a_tag = author_block.find("a")
        data["author"] = {
            "name": clean(a_tag),
            "profile": a_tag["href"] if a_tag else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===== INTRO PARAGRAPHS =====
    intro_container = soup.find("div", id="wikkiContents_chp_syllabus_overview_0")
    if intro_container:
        for p in intro_container.find_all("p"):
            text = p.get_text(" ", strip=True)
            if text:
                data["courses"]["intro"]["paragraphs"].append(text)

    # ======================================================
    # ✅ BTECH SYLLABUS SCRAPING (YOUR HTML SECTION)
    # ======================================================
    syllabus_container = soup.find("div", id="wikkiContents_chp_syllabus_popularcolleges_0")

    if syllabus_container:
        # First intro paragraph inside syllabus
        intro_p = syllabus_container.find("p")
        if intro_p:
            data["courses"]["btech_syllabus"].append({
                "type": "intro",
                "text": intro_p.get_text(" ", strip=True)
            })

        # Each branch section
        for h3 in syllabus_container.find_all("h3"):
            branch_name = h3.get_text(" ", strip=True)

            table = h3.find_next("table")
            branch_data = {
                "branch": branch_name,
                "semesters": {}
            }

            if table:
                current_semester = None

                for row in table.find_all("tr"):
                    th = row.find("th")
                    tds = row.find_all("td")

                    # Semester Heading
                    if th:
                        current_semester = th.get_text(" ", strip=True)
                        branch_data["semesters"][current_semester] = []
                        continue

                    # Subjects Row
                    if current_semester and tds:
                        subjects = [
                            td.get_text(" ", strip=True)
                            for td in tds
                            if td.get_text(strip=True)
                        ]
                        if subjects:
                            branch_data["semesters"][current_semester].extend(subjects)

            data["courses"]["btech_syllabus"].append(branch_data)

    # ===== FAQ =====
    faq_container = soup.find("div", id="sectional-faqs-0")
    if faq_container:
        questions = faq_container.find_all("div", class_="html-0 c5db62 listener")
        answers = faq_container.find_all("div", class_="_16f53f")

        for q_div, a_div in zip(questions, answers):
            question_text = " ".join(q_div.stripped_strings).replace("Q:", "").strip()
            answer_content = [
                p.get_text(" ", strip=True)
                for p in a_div.find_all("p")
                if p.get_text(strip=True)
            ]

            data["courses"]["syllabus_faq"].append({
                "question": question_text,
                "answer": answer_content
            })
    # ======================================================
    # ✅ BTECH CORE SUBJECTS & SPECIALIZATION LINKS
    # ======================================================
    core_container = soup.find("div", id="wikkiContents_chp_syllabus_popularexams_0")

    if core_container:
        core_data = {
            "intro": "",
            "specializations": [],
            "specialization_links": [],
            "notes": []
        }

        # ---- Intro paragraph (first <p>)
        first_p = core_container.find("p")
        if first_p:
            core_data["intro"] = first_p.get_text(" ", strip=True)

        tables = core_container.find_all("table")

        # ================= TABLE 1 =================
        # BTech Specialization vs Core Subjects
        if len(tables) > 0:
            rows = tables[0].find_all("tr")[1:]  # skip header
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link_tag = cols[0].find("a")

                    core_data["specializations"].append({
                        "name": cols[0].get_text(" ", strip=True),
                        "core_subjects": cols[1].get_text(" ", strip=True)
                    })

        # ================= TABLE 2 =================
        # Specialization-wise syllabus links
        if len(tables) > 1:
            for row in tables[1].find_all("tr")[1:]:
                for td in row.find_all("td"):
                    a_tag = td.find("a")
                    if a_tag:
                        core_data["specialization_links"].append({
                            "title": a_tag.get_text(" ", strip=True),
                           
                        })

        # ---- Notes & remaining paragraphs
        for p in core_container.find_all("p"):
            text = p.get_text(" ", strip=True)
            if "Note -" in text or "syllabus is extensive" in text:
                core_data["notes"].append(text)

        data["courses"]["btech_core_subjects"] = core_data
    # ======================================================
    # ✅ FAQ / QnA SECTION SCRAPING
    # ======================================================
    faq_container = soup.find("div", id="sectional-faqs-0")

    if faq_container:
        faq_items = faq_container.find_all("div", class_="html-0")

        for q_div in faq_items:
            # -------- QUESTION --------
            question_text = q_div.get_text(" ", strip=True)
            question_text = question_text.replace("Q:", "").strip()

            # -------- ANSWER BLOCK (next sibling) --------
            answer_wrapper = q_div.find_next_sibling("div", class_="_16f53f")
            if not answer_wrapper:
                continue

            answer_content = answer_wrapper.find("div", class_="cmsAContent")
            if not answer_content:
                continue

            answer_parts = []

            # ---- Paragraphs
            for p in answer_content.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text:
                    answer_parts.append(text)

            # ---- Bullet points (if any)
            for ul in answer_content.find_all("ul"):
                for li in ul.find_all("li"):
                    li_text = li.get_text(" ", strip=True)
                    if li_text:
                        answer_parts.append(li_text)

            data["courses"]["faqs"].append({
                "question": question_text,
                "answer": answer_parts
            })
    spec_container = soup.find(
        "div",
        id="wikkiContents_chp_syllabus_popularspecialization_0"
    )

    if spec_container:
        table = spec_container.find("table")

        if table:
            rows = table.find_all("tr")[1:]  # skip header row

            for row in rows:
                cols = row.find_all("td")
                if len(cols) != 3:
                    continue

                # ---- Specialization name
                specialization = cols[0].get_text(" ", strip=True)

                # ---- Book titles
                book_titles = [
                    p.get_text(" ", strip=True)
                    for p in cols[1].find_all("p")
                    if p.get_text(strip=True)
                ]

                # ---- Author names
                authors = [
                    p.get_text(" ", strip=True)
                    for p in cols[2].find_all("p")
                    if p.get_text(strip=True)
                ]

                books = []
                for i in range(min(len(book_titles), len(authors))):
                    books.append({
                        "book_title": book_titles[i],
                        "author": authors[i]
                    })

                data["courses"]["specializations"][specialization] = books

    return data
def scrape_mba_career(driver):
    driver.get(PCOMBA_MBA_CAREER_URL)
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
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # Career Overview (paragraphs only)
    # Find the overview div
    overview_div = soup.find("div", id="wikkiContents_chp_career_overview_0")

    data["career_overview"] = []

    if overview_div:
        # Sab <p> grab karo recursively
        for p in overview_div.find_all("p"):
            # Agar <p> ke baad <h2> ya <h3> aa gaya, break
            # (BeautifulSoup doesn't directly know "next heading" yet, so we just stop after first few paragraphs)
            text = p.get_text(" ", strip=True)
            if text:
                data["career_overview"].append(text)
        
        # Only take first 5 paragraphs to avoid extra tables/jobs
        data["career_overview"] = data["career_overview"][:5]


    # ===============================
    # Tables scraped by Heading (KEY FIX)
    data["sections"] = {}

    if overview_div:
        for heading in overview_div.find_all(["h2", "h3"]):
            section_title = heading.get_text(strip=True)

            table = heading.find_next_sibling("table")
            if not table:
                continue

            rows_data = []
            rows = table.find_all("tr")[1:]  # skip header

            for row in rows:
                cols = [c.get_text(" ", strip=True) for c in row.find_all("td")]
                if cols:
                    rows_data.append(cols)

            if rows_data:
                data["sections"][section_title] = rows_data

    # ===============================
    # CSE Jobs (Structured Output)
    data["career_profiles"] = []
    for key, rows in data["sections"].items():
        if "CSE" in key or "Computer Science" in key:
            for r in rows:
                if len(r) >= 3:
                    data["career_profiles"].append({
                        "job_profile": r[0],
                        "description": r[1],
                        "average_salary": r[2]
                    })

    # ===============================
    # Mechanical Engineering Jobs
    data["mechanical_jobs"] = []
    for key, rows in data["sections"].items():
        if "Mechanical" in key:
            for r in rows:
                if len(r) >= 3:
                    data["mechanical_jobs"].append({
                        "job_profile": r[0],
                        "description": r[1],
                        "average_salary": r[2]
                    })

    # ===============================
    # Electrical Engineering Jobs
    data["electrical_jobs"] = []
    for key, rows in data["sections"].items():
        if "Electrical" in key:
            for r in rows:
                if len(r) >= 3:
                    data["electrical_jobs"].append({
                        "job_profile": r[0],
                        "description": r[1],
                        "average_salary": r[2]
                    })

    # ===============================
    # Biotechnology Jobs
    data["biotech_jobs"] = []
    for key, rows in data["sections"].items():
        if "Biotech" in key or "Biotechnology" in key:
            for r in rows:
                if len(r) >= 3:
                    data["biotech_jobs"].append({
                        "job_profile": r[0],
                        "description": r[1],
                        "average_salary": r[2]
                    })

    # ===============================
    # Civil Engineering Jobs
    data["civil_jobs"] = []
    for key, rows in data["sections"].items():
        if "Civil" in key:
            for r in rows:
                if len(r) >= 3:
                    data["civil_jobs"].append({
                        "job_profile": r[0],
                        "description": r[1],
                        "average_salary": r[2]
                    })

    # ===============================
    # Top Recruiters
    data["top_recruiters"] = []
    for key, rows in data["sections"].items():
        if "Recruiter" in key or "Top Recruiters" in key:
            for r in rows:
                data["top_recruiters"].extend(r)

    data["top_recruiters"] = list(set(data["top_recruiters"]))  # remove duplicates

    # ===============================
    # Top Colleges & Placements
    data["top_colleges"] = []

    tables = overview_div.find_all("table") if overview_div else []
    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if "Placements" in " ".join(headers) or "Package" in " ".join(headers):
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    link_tag = cols[0].find("a")
                    data["top_colleges"].append({
                        "college": cols[0].get_text(strip=True),
                        "median_salary": cols[1].get_text(strip=True),
                        "link": link_tag["href"] if link_tag else None
                    })

    return data
 
def scrape_addmission_2026_data(driver):
    driver.get(PCOMBA_MBA_ADDMISSION_2026_URL)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    data = {}
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

    # Section 1: Overview
    overview_section = soup.find("div", id="wikkiContents_chp_admission_overview_0")
    if overview_section:
        overview_paragraphs = overview_section.find_all("p")
        data['overview_text'] = " ".join([p.get_text(strip=True) for p in overview_paragraphs])

        # Scrape suggested / useful links in overview
        overview_links = []
        for p in overview_section.find_all("p"):
            a_tag = p.find("a")
            if a_tag and a_tag.get("href"):
                overview_links.append({"text": a_tag.get_text(strip=True), "url": a_tag['href']})
        data['overview_links'] = overview_links

    # ===============================
    # Section 2: Eligibility Criteria (FIXED)
    eligibility_section = soup.find("h2", id="chp_admission_toc_0")

    if eligibility_section:
        eligibility_data = {}

        # Heading
        eligibility_data["heading"] = eligibility_section.get_text(strip=True)

        # Paragraphs under eligibility
        para_list = []
        next_tag = eligibility_section.find_next_sibling()

        while next_tag and next_tag.name != "table":
            if next_tag.name == "p":
                para_list.append(next_tag.get_text(strip=True))
            next_tag = next_tag.find_next_sibling()

        eligibility_data["description"] = para_list

        # Eligibility Table
        table = eligibility_section.find_next("table")
        table_rows = []

        if table:
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    table_rows.append({
                        "course": cols[0].get_text(strip=True),
                        "eligibility": cols[1].get_text(strip=True)
                    })

        eligibility_data["criteria"] = table_rows

        data["eligibility"] = eligibility_data



    # Section 3: Admission Process
    admission_section = soup.find("h2", id="chp_admission_toc_1")
    if admission_section:
        process_list = admission_section.find_next("ul")
        if process_list:
            data['admission_process'] = [li.get_text(strip=True) for li in process_list.find_all("li")]

    # Section 4: Entrance Exams
    exams_section = soup.find("h2", id="chp_admission_toc_2")
    if exams_section:
        exams_table = exams_section.find_next("table")
        if exams_table:
            rows = exams_table.find_all("tr")
            entrance_exams = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    entrance_exams.append({
                        "exam_name": cols[0].get_text(strip=True),
                        "exam_schedule": cols[1].get_text(strip=True)
                    })
            data['entrance_exams'] = entrance_exams

    # Section 5: Exam Syllabus
    syllabus_section = soup.find("h2", id="chp_admission_toc_3")
    if syllabus_section:
        syllabus_table = syllabus_section.find_next("table")
        if syllabus_table:
            rows = syllabus_table.find_all("tr")
            exam_syllabus = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    exam_syllabus.append({
                        "exam_name": cols[0].get_text(strip=True),
                        "syllabus_details": [p.get_text(strip=True) for p in cols[1].find_all("p")]
                    })
            data['exam_syllabus'] = exam_syllabus

    # Section 6: Best Colleges (IIMs & IITs)
    best_colleges_section = soup.find("h2", id="chp_admission_toc_5")
    if best_colleges_section:
        tables = best_colleges_section.find_all_next("table", limit=2)
        best_colleges = {}
        if tables:
            # IIMs
            iim_rows = tables[0].find_all("tr")[1:]
            best_colleges['IIMs'] = [{"college_name": cols[0].get_text(strip=True),
                                      "mba_fees": cols[1].get_text(strip=True)}
                                     for row in iim_rows if (cols := row.find_all("td")) and len(cols) == 2]
            # IITs
            iit_rows = tables[1].find_all("tr")[1:]
            best_colleges['IITs'] = [{"college_name": cols[0].get_text(strip=True),
                                      "mba_fees": cols[1].get_text(strip=True)}
                                     for row in iit_rows if (cols := row.find_all("td")) and len(cols) == 2]
        data['best_colleges'] = best_colleges

    # Section 6a: Top Government Colleges
    gov_colleges_section = soup.find("h3", id="chp_admission_toc_5_2")
    if gov_colleges_section:
        gov_table = gov_colleges_section.find_next("table")
        if gov_table:
            rows = gov_table.find_all("tr")[1:]
            government_colleges = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link = cols[0].find("a")['href'] if cols[0].find("a") else None
                    government_colleges.append({
                        "college_name": cols[0].get_text(strip=True),
                        "admission_url": link,
                        "mba_fees": cols[1].get_text(strip=True)
                    })
            data['government_colleges'] = government_colleges

    # Section 6b: Top Private Colleges
    private_colleges_section = soup.find("h3", id="chp_admission_toc_5_3")
    if private_colleges_section:
        private_table = private_colleges_section.find_next("table")
        if private_table:
            rows = private_table.find_all("tr")[1:]
            private_colleges = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link = cols[0].find("a")['href'] if cols[0].find("a") else None
                    private_colleges.append({
                        "college_name": cols[0].get_text(strip=True),
                        "admission_url": link,
                        "mba_fees": cols[1].get_text(strip=True)
                    })
            data['private_colleges'] = private_colleges

    # Section 7: Important Dates
    dates_section = soup.find("h2", id="chp_admission_toc_4")
    if dates_section:
        dates_table = dates_section.find_next("table")
        if dates_table:
            rows = dates_table.find_all("tr")
            important_dates = []
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    important_dates.append({
                        "event": cols[0].get_text(strip=True),
                        "date": cols[1].get_text(strip=True)
                    })
            data['important_dates'] = important_dates

    # Section 8: Contact Info
    contact_section = soup.find("div", id="contact_info")
    if contact_section:
        contact_paragraphs = contact_section.find_all("p")
        data['contact_info'] = [p.get_text(strip=True) for p in contact_paragraphs]

    # Section 9: Placements
    placement_section = soup.find("h2", id="chp_admission_toc_8")
    if placement_section:
        placement_table = placement_section.find_next("table")
        if placement_table:
            rows = placement_table.find_all("tr")[1:]
            placements = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) == 2:
                    link = cols[0].find("a")['href'] if cols[0].find("a") else None
                    placements.append({
                        "college_name": cols[0].get_text(strip=True),
                        "placement_url": link,
                        "average_package": cols[1].get_text(strip=True)
                    })
            data['placements'] = placements

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
        data["author"] = {
            "name": clean(a),
            "profile": a["href"] if a else None,
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
            "role": clean(author_block.find("span", class_="b0fc")),
            "verified": bool(author_block.find("i", class_="tickIcon"))
        }

    # ===============================
    # FEES OVERVIEW (CLEAN & CORRECT)
    fees_overview_div = soup.find("div", id="wikkiContents_chp_fees_overview_0")

    if fees_overview_div:
        fees_data = {
            "overview_text": [],
            "heading": None,
            "fees_table": [],
            "note": None,
            "helpful_links": []
        }

        # 1️⃣ Heading
        h2 = fees_overview_div.find("h2", id="chp_fees_toc_0")
        if h2:
            fees_data["heading"] = h2.get_text(strip=True)

    # ===============================
    # FIXED OVERVIEW TEXT EXTRACTION

    content_div = fees_overview_div.find("div", recursive=False)

    if content_div:
        for elem in content_div.children:

            if getattr(elem, "name", None) == "h2":
                break   # stop before fees table heading

            if getattr(elem, "name", None) == "p":
                text = elem.get_text(strip=True)

                if (
                    text
                    and "Relevant Links" not in text
                    and "Helpful Links" not in text
                ):
                    fees_data["overview_text"].append(text)


        # 3️⃣ Fees Table
        table = fees_overview_div.find("table")
        if table:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) == 2:
                    a_tag = cols[0].find("a")
                    fees_data["fees_table"].append({
                        "college": cols[0].get_text(strip=True),
                        "fees": cols[1].get_text(strip=True),
                        
                    })

        # 4️⃣ Note
        for p in fees_overview_div.find_all("p"):
            if p.get_text(strip=True).startswith("Note"):
                fees_data["note"] = p.get_text(strip=True)

        # 5️⃣ Helpful Links (AFTER table)
        for a in fees_overview_div.find_all("a"):
            href = a.get("href")
            title = a.get_text(strip=True)

            if href and "shiksha.com" in href:
                fees_data["helpful_links"].append({
                    "title": title,
                    
                })

        data["fees_overview"] = fees_data


    # ===============================
    # MBA Course Fees: Location Wise (UNCHANGED)
    data["location_wise_fees"] = []

    location_section = soup.find("div", id="wikkiContents_chp_fees_locationwisefees_0")
    if location_section:
        current_city = None

        for element in location_section.find_all(["h3", "table", "p"], recursive=True):

            if element.name == "h3":
                current_city = element.get_text(strip=True)
                data["location_wise_fees"].append({
                    "city": current_city,
                    "colleges": [],
                    "read_more": None
                })

            elif element.name == "table" and current_city:
                rows = element.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        college_tag = cols[0].find("a")
                        data["location_wise_fees"][-1]["colleges"].append({
                            "college": cols[0].get_text(strip=True),
                            "fees": cols[1].get_text(strip=True),
                            "link": college_tag.get("href") if college_tag else None
                        })

            elif element.name == "p" and current_city:
                a_tag = element.find("a")
                if a_tag and "Click Here" in a_tag.get_text():
                    data["location_wise_fees"][-1]["read_more"] = a_tag.get("href")

    return data


def scrape_btech_vs_bsc_article(driver):
    driver.get(PCOMBA_MBA_PGDM_URL)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    data = {}
    title = soup.find("div",class_="flx-box mA")
    h1 = title.find("h1").text.strip()
    data["title"] = h1
    author_section = soup.find("div", class_="adp_blog")

    if author_section:
        author = {}

        author_link = author_section.select_one(
            ".adp_user_tag .adp_usr_dtls > a[href*='/author/']"
        )

        if author_link:
            author["name"] = author_link.get_text(strip=True)
            author["profile"] = author_link.get("href")

            # ✅ VERIFIED CHECK (CORRECT)
            author["verified"] = bool(author_link.select_one("i.tickIcon"))

        # Author Image
        img = author_section.select_one(".adp_user_tag img")
        if img:
            author["image"] = img.get("src")

        # Author Role
        role = author_section.select_one(".user_expert_level")
        if role:
            author["role"] = role.get_text(strip=True)

        data["author"] = author

        # Updated Date
        updated_span = author_section.select_one(".blogdata_user span")
        if updated_span:
            data["updated_on"] = updated_span.get_text(strip=True)
    # ===============================
    # Blog Summary
    summary_div = soup.find("div", id="blogSummary")
    if summary_div:
        data["summary"] = summary_div.get_text(strip=True)

    # ===============================
    # Intro Section
    intro_div = soup.find("div", id=lambda x: x and x.startswith("wikkiContents_multi"))
    if intro_div:
        data["introduction"] = {
            "text": [p.get_text(strip=True) for p in intro_div.find_all("p") if p.get_text(strip=True)],
            "image": None
        }

        img = intro_div.find("img")
        if img:
            data["introduction"]["image"] = img.get("src")

    # ===============================
    # Table of Contents
    data["table_of_contents"] = []
    toc = soup.find("ul", id="tocWrapper")
    if toc:
        for li in toc.find_all("li"):
            data["table_of_contents"].append(li.get_text(strip=True))

    # ===============================
    # Content Sections (h2 + paragraphs)
    data["sections"] = []

    for section in soup.find_all("div", class_="wikkiContents"):
        h2 = section.find("h2")
        if not h2:
            continue

        section_data = {
            "heading": h2.get_text(strip=True),
            "content": [],
            "tables": []
        }

        # Paragraphs
        for p in section.find_all("p", recursive=False):
            text = p.get_text(" ", strip=True)
            if text:
                section_data["content"].append(text)

        # Tables
        for table in section.find_all("table"):
            table_data = []
            rows = table.find_all("tr")

            headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])] if rows else []

            for row in rows[1:]:
                cols = row.find_all("td")
                if not cols:
                    continue
                row_data = {}
                for i, col in enumerate(cols):
                    key = headers[i] if i < len(headers) else f"col_{i}"
                    row_data[key] = col.get_text(" ", strip=True)
                table_data.append(row_data)

            section_data["tables"].append(table_data)

        data["sections"].append(section_data)

    # ===============================
    # Video Section
    data["video"] = None
    
    iframe = soup.select_one("div iframe[src*='youtube'], iframe[src*='youtube']")
    if iframe:
        data["video"] = iframe.get("src")
    # ===============================
    # Colleges Offering MBA / PGDM
    # ===============================
    # Colleges Offering MBA / PGDM (FIXED)
    data["colleges"] = []
    
    for h2 in soup.find_all("h2"):
        heading_text = h2.get_text(strip=True).lower()
    
        if "college" in heading_text and ("mba" in heading_text or "pgdm" in heading_text):
            table = h2.find_next("table")
            if not table:
                continue
    
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    a = cols[0].find("a")
                    data["colleges"].append({
                        "college": cols[0].get_text(strip=True),
                        "program": cols[1].get_text(strip=True),
                        "link": a.get("href") if a else None
                    })
    # ===============================
    # SECTION: FAQs (Q&A)
    faq_wrapper = soup.find("div", id="faqWrapper_last")

    if faq_wrapper:
        faqs = []

        questions = faq_wrapper.find_all("p", class_="fQ")

        for q in questions:
            q_text = q.get_text(strip=True).replace("Q.", "").strip()

            answer_div = q.find_next_sibling("div", class_="fA")
            if not answer_div:
                continue

            answer_data = {
                "paragraphs": [],
                "bullets": [],
                "table": None
            }

            # Paragraphs
            for p in answer_div.find_all("p"):
                text = p.get_text(" ", strip=True)
                if text:
                    text = text.replace("A.", "").strip()
                    answer_data["paragraphs"].append(text)

            # Bullet points
            for li in answer_div.find_all("li"):
                text = li.get_text(" ", strip=True)
                if text:
                    answer_data["bullets"].append(text)

            # Table (if exists)
            table = answer_div.find("table")
            if table:
                headers = [th.get_text(strip=True) for th in table.find_all("th")]
                rows_data = []

                for row in table.find_all("tr")[1:]:
                    cols = row.find_all("td")
                    if len(cols) == len(headers):
                        row_obj = {}
                        for i, header in enumerate(headers):
                            row_obj[header] = cols[i].get_text(" ", strip=True)
                        rows_data.append(row_obj)

                answer_data["table"] = {
                    "headers": headers,
                    "rows": rows_data
                }

            faqs.append({
                "question": q_text,
                "answer": answer_data
            })

        data["faqs"] = faqs
    return data

def scrape_jmp_content(driver):
    driver.get(PCOMBA_JMP_URL)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    data = {
        "title":"",
        "updated_on":"",
        "author":{},
        "intro": {
            "emphasis_text": "",
            "paragraphs": [],
            "images": []
        },
        "sections": [],
        "authors": {},
        "also_read": [],
        "videos_you_may_like": []
    }
    # Course Name
    course_name_div = soup.find("div", class_="flx-box mA")
    if course_name_div:
        h1 = course_name_div.find("h1")
        data["title"] = clean(h1)

    # ===============================
    # Updated Date
    updated_div = soup.find("div",class_="blogdata_user")
    if updated_div:
        span = updated_div.find("span")
        data["updated_on"] = clean(span)

    # ===============================
    # Author Info
    author_block = soup.find("div", class_="adp_usr_dtls")
    if author_block:
        a = author_block.find("a")
        data["author"] = {
            "name": clean(a),
            "image": author_block.find("img")["src"] if author_block.find("img") else None,
           
        }

    # ================= INTRO BLOCK =================
    first_block = soup.find("div", class_="wikkiContents")
    if first_block:
        em = first_block.find("em")
        if em:
            data["intro"]["emphasis_text"] = em.get_text(" ", strip=True)

        for p in first_block.find_all("p", recursive=False):
            text = p.get_text(" ", strip=True)
            if text and not p.find("em"):
                data["intro"]["paragraphs"].append(text)

        for img in first_block.find_all("img"):
            data["intro"]["images"].append({
                "src": img.get("src"),
                "alt": img.get("alt"),
                "width": img.get("width"),
                "height": img.get("height")
            })

    # ================= ALL WIKKI CONTENT BLOCKS =================
    blocks = soup.find_all("div", class_="wikkiContents")

    for block in blocks:
        current_section = None

        for tag in block.find_all(["h2", "h3", "p", "table", "ul", "iframe"], recursive=True):

            # ---------- Heading ----------
            if tag.name in ["h2", "h3"]:
                if current_section:
                    data["sections"].append(current_section)

                current_section = {
                    "heading": tag.get_text(strip=True),
                    "content": {
                        "paragraphs": [],
                        "tables": [],
                        "lists": [],
                        "videos": []
                    }
                }

            # ---------- Paragraph ----------
            elif tag.name == "p" and current_section:
                txt = tag.get_text(" ", strip=True)
                if txt:
                    current_section["content"]["paragraphs"].append(txt)

            # ---------- List ----------
            elif tag.name == "ul" and current_section:
                items = []
                for li in tag.find_all("li"):
                    items.append({
                        "text": li.get_text(" ", strip=True),
                        "link": li.find("a").get("href") if li.find("a") else None
                    })
                current_section["content"]["lists"].append(items)

            # ---------- Table ----------
            elif tag.name == "table" and current_section:
                headers = [th.get_text(strip=True) for th in tag.find_all("th")]
                rows = []

                for tr in tag.find_all("tr")[1:]:
                    cols = tr.find_all("td")
                    if cols:
                        row = {}
                        for i, col in enumerate(cols):
                            key = headers[i] if i < len(headers) else f"col_{i}"
                            row[key] = col.get_text(" ", strip=True)
                        rows.append(row)

                current_section["content"]["tables"].append({
                    "headers": headers,
                    "rows": rows
                })

            # ---------- Video ----------
            elif tag.name == "iframe" and current_section:
                current_section["content"]["videos"].append({
                    "src": tag.get("src"),
                    "width": tag.get("width"),
                    "height": tag.get("height")
                })

        if current_section:
            data["sections"].append(current_section)

    # ================= AUTHOR =================
    author_name = soup.find(string=lambda t: "About the Author" in t if t else False)
    if author_name:
        author_p = author_name.find_parent("p").find_next_sibling("p")
        if author_p:
            data["authors"]["name"] = author_p.get_text(strip=True)

    # ================= ALSO READ =================
    also_read_heading = soup.find("strong", string=lambda t: t and "Also read" in t)
    if also_read_heading:
        ul = also_read_heading.find_parent("p").find_next_sibling("ul")
        if ul:
            for li in ul.find_all("li"):
                a = li.find("a")
                data["also_read"].append({
                    "title": a.get_text(strip=True),
                    "url": a.get("href")
                })

    # ---------- Video ----------
    elif tag.name == "iframe" and current_section:
        video_src = (
            tag.get("src")
            or tag.get("data-src")
            or tag.get("data-lazy-src")
        )

        if video_src:
            current_section["content"]["videos"].append({
                "src": video_src,
                "title": tag.get("title"),
                "width": tag.get("width"),
                "height": tag.get("height")
            })

    return data


def scrape_shiksha_qa(driver):
    driver.get(PCOMBA_QN_URL)
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
    driver.get(PCOMBA_QND_URL)
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
              "B Tech":{
                   "overviews":extract_course_data(driver),
                   "courses":scrape_courses_overview_section(driver),
                   "syllabus":scrape_mba_syllabus(driver),
                   "career":scrape_mba_career(driver),
                   "B.tech_addmission":scrape_addmission_2026_data(driver),
                   "fees": scrape_mba_fees_overview(driver),
                   "btech VS bsc":scrape_btech_vs_bsc_article(driver),
                    "JM Prepration":scrape_jmp_content(driver),
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

