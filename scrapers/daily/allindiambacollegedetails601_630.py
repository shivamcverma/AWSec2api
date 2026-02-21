from requests import options
from selenium import webdriver
import selenium
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
from selenium.common.exceptions import TimeoutException

# ---------------- URLS ----------------
BASE_URL = [
  "https://www.shiksha.com/college/hi-tech-institute-of-engineering-and-technology-ghaziabad-36980",
  "https://www.shiksha.com/university/jntua-jawaharlal-nehru-technological-university-anantapur-51545",
  "https://www.shiksha.com/university/bau-birsa-agricultural-university-ranchi-22263",
  "https://www.shiksha.com/college/r-g-kedia-college-of-commerce-koti-hyderabad-31635",
  "https://www.shiksha.com/college/delhi-institute-of-advanced-studies-rohini-48191",
  "https://www.shiksha.com/college/rajiv-gandhi-institute-of-petroleum-technology-amethi-46857",
  "https://www.shiksha.com/college/durgadevi-saraf-global-business-school-malad-west-mumbai-208971",
  "https://www.shiksha.com/college/bhagwan-mahavir-college-of-management-bhagwan-mahavir-university-surat-68695",
  "https://www.shiksha.com/college/psna-college-of-engineering-and-technology-tamil-nadu-other-20917",
  "https://www.shiksha.com/college/dr-g-r-damodaran-college-of-science-coimbatore-52763",
  "https://www.shiksha.com/university/j-c-bose-university-of-science-and-technology-ymca-faridabad-21570",
  "https://www.shiksha.com/college/college-of-arts-and-commerce-andhra-university-visakhapatnam-142785",
  "https://www.shiksha.com/college/dc-school-of-management-and-technology-idukki-48212",
  "https://www.shiksha.com/college/government-first-grade-college-vijayanagar-vijayanagar-bangalore-102519",
  "https://www.shiksha.com/university/central-university-of-rajasthan-ajmer-32767",
  "https://www.shiksha.com/college/maharaj-vijayaram-gajapathi-raj-college-of-engineering-mvgrce-vizianagaram-25411",
  "https://www.shiksha.com/university/the-northcap-university-gurgaon-26247",
  "https://www.shiksha.com/college/gita-gandhi-institute-for-technological-advancement-bhubaneswar-23303",
  "https://www.shiksha.com/university/sri-ramachandra-institute-of-higher-education-and-research-chennai-24265",
  "https://www.shiksha.com/college/naemd-national-academy-of-event-management-and-development-mumbai-goregaon-west-27228",
  "https://www.shiksha.com/university/dr-rajendra-prasad-central-agricultural-university-bihar-other-25125",
  "https://www.shiksha.com/college/sri-sathya-sai-institute-of-higher-learning-anantapur-21288",
  "https://www.shiksha.com/college/indore-management-institute-and-research-centre-64101",
  "https://www.shiksha.com/college/vns-group-of-institutions-bhopal-21542",
  "https://www.shiksha.com/college/karpagam-academy-of-higher-education-kahe-coimbatore-28632",
  "https://www.shiksha.com/college/indian-institute-of-hotel-management-kolkata-salt-lake-city-28741",
  "https://www.shiksha.com/college/m-v-j-college-of-engineering-whitefield-bangalore-20690",
  "https://www.shiksha.com/university/the-gandhigram-rural-institute-tamil-nadu-other-22347",
  "https://www.shiksha.com/college/indian-institute-of-logistics-chennai-2991",
  "https://www.shiksha.com/college/gcec-global-foundation-jaipur-56229",
]


def build_urls(BASE_URL):
    return {
        "college_info":BASE_URL,
        "courses": BASE_URL + "/courses",
        "fees": BASE_URL + "/fees",
        "reviews": BASE_URL + "/reviews",
        "admission": BASE_URL + "/admission",
        "placement": BASE_URL + "/placement",
        "cutoff": BASE_URL + "/cutoff",
        "ranking": BASE_URL + "/ranking",
        "gallery": BASE_URL + "/gallery",
        "infrastructure": BASE_URL + "/infrastructure",
        "faculty": BASE_URL + "/faculty",
        "compare": BASE_URL + "/compare",
        "scholarships": BASE_URL + "/scholarships",
        # "qna": "https://ask.shiksha.com/which-is-better-for-mba-iim-ahmedabad-or-jbims-qna-5114413"
    }
# ---------------- DRIVER ----------------
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



def scrape_college_info(driver,URLS):
    import re 
    try:
        driver.get(URLS["college_info"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["college_info"])
    
    wait = WebDriverWait(driver, 40)

    data = {
        "college_info": {
            "college_name": None,
            "rating": None,
            "logo":None,
            "cover_image":None,
            "reviews_count": None,
            "qa_count": None,
            "location": None,
            "city": None,
            "institute_type": None,
            "established_year": None,
            "highlights": {
                "summary": None,
                "table": [],
                "faqs": [],
            },
            "intro": None,
            "courses": [],
            "faqs": []
        }
    }
    college_info = data["college_info"]
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")
        except:
            pass 
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
        except:
            pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            pass
        
        # Rest of your existing header extraction code...
        
    except Exception as e:
        pass
    # ================= COLLEGE NAME =================
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    data["college_info"]["college_name"] = driver.find_element(By.TAG_NAME, "h1").text.strip()

    # ================= LOCATION + CITY =================
    loc = driver.find_element(By.CSS_SELECTOR, "span.f90eb6").text
    if "," in loc:
        l, c = loc.split(",", 1)
        data["college_info"]["location"] = l.strip()
        data["college_info"]["city"] = c.strip()

    # ================= RATING =================
    try:
        rating = driver.find_element(By.CSS_SELECTOR, "span.f1b26c").text
        data["college_info"]["rating"] = re.search(r'([\d.]+)', rating).group(1)
    except:
        pass

    # ================= REVIEWS COUNT =================
    try:
        reviews = driver.find_element(By.XPATH, "//a[contains(text(),'Reviews')]").text
        data["college_info"]["reviews_count"] = int(re.search(r'\d+', reviews).group())
    except:
        pass

    # ================= Q&A COUNT =================
    try:
        qa = driver.find_element(By.XPATH, "//a[contains(text(),'Student Q')]").text.lower()
        val = re.search(r'([\d.]+k?)', qa).group(1)
        data["college_info"]["qa_count"] = int(float(val.replace("k", "")) * 1000) if "k" in val else int(val)
    except:
        pass

    # ================= INSTITUTE TYPE + ESTD =================
    for item in driver.find_elements(By.CSS_SELECTOR, "span.b00d1d"):
        txt = item.text
        if "Institute" in txt:
            data["college_info"]["institute_type"] = txt
        if "Estd" in txt:
            data["college_info"]["established_year"] = re.search(r'\d{4}', txt).group()

    # ================= SECTION WAIT =================

    # ================= HIGHLIGHTS SECTION (JS SAFE) =================
    try:
        highlights = wait.until(
            EC.presence_of_element_located((By.ID, "ovp_section_highlights"))
        )

        # 🔹 SUMMARY (improved to get all text content before table)
        summary = driver.execute_script("""
            // Get the main accordion wrapper
            let el = document.querySelector('.faq__according-wrapper');
            if (!el) return null;
            
            // Get all p tags within the wrapper
            let ps = el.querySelectorAll('p');
            let summaryTexts = [];
            
            ps.forEach(p => {
                // Skip paragraphs that are inside the table
                if (p.closest('table')) return;
                
                let t = p.innerText.trim();
                // Collect meaningful paragraphs (not too short)
                if (t.length > 20 && !t.includes('Check out more')) {
                    summaryTexts.push(t);
                }
            });
            
            // Join with proper spacing
            return summaryTexts.join("\\n\\n");
        """)
        data["college_info"]["highlights"]["summary"] = summary if summary else "Summary not available"

        # 🔹 TABLE (IMPROVED with better data extraction)
        table_data = driver.execute_script("""
            // Find all tables within the highlights section
            let tables = document.querySelectorAll('#EdContent__ovp_section_highlights table');
            if (tables.length === 0) return [];
            
            let result = [];
            
            // Process each table
            tables.forEach(table => {
                let rows = table.querySelectorAll('tr');
                
                // Check if this looks like a highlights table (has "Particulars" header)
                let firstRow = rows[0];
                if (firstRow) {
                    let headerText = firstRow.innerText.toLowerCase();
                    if (headerText.includes('particulars') || headerText.includes('highlight')) {
                        
                        // Process rows starting from index 1 (skip header)
                        for (let i = 1; i < rows.length; i++) {
                            let row = rows[i];
                            let cols = row.querySelectorAll('td, th');
                            
                            if (cols.length >= 2) {
                                let key = cols[0].innerText.trim();
                                let value = cols[1].innerText.trim();
                                
                                // Clean up the key (remove trailing colons, etc.)
                                key = key.replace(/[:|]$/, '').trim();
                                
                                // Check if value contains a link
                                let linkElem = cols[1].querySelector('a');
                                let linkData = null;
                                if (linkElem) {
                                    linkData = {
                                        text: linkElem.innerText.trim(),
                                        href: linkElem.getAttribute('href'),
                                        title: linkElem.getAttribute('title') || ''
                                    };
                                }
                                
                                if (key && value) {
                                    result.push({
                                        particular: key,
                                        details: value,
                                        link: linkData
                                    });
                                }
                            }
                        }
                    }
                }
            });
            
            return result;
        """)
        
        # If table_data is empty, try alternative selector
        if not table_data:
            table_data = driver.execute_script("""
                // Alternative: Look for table directly in the accordion wrapper
                let table = document.querySelector('.faq__according-wrapper table');
                if (!table) return [];
                
                let result = [];
                let rows = table.querySelectorAll('tr');
                
                for (let i = 1; i < rows.length; i++) {
                    let row = rows[i];
                    let cells = row.querySelectorAll('td');
                    
                    if (cells.length >= 2) {
                        let key = cells[0].innerText.trim();
                        let value = cells[1].innerText.trim();
                        
                        // Special handling for rankings (multiple lines)
                        if (key.includes('Rankings')) {
                            let pTags = cells[1].querySelectorAll('p');
                            if (pTags.length > 0) {
                                value = Array.from(pTags).map(p => p.innerText.trim()).join(' | ');
                            }
                        }
                        
                        // Check for links
                        let linkElem = cells[1].querySelector('a');
                        let linkData = null;
                        if (linkElem) {
                            linkData = {
                                text: linkElem.innerText.trim(),
                                href: linkElem.getAttribute('href')
                            };
                        }
                        
                        if (key && value) {
                            result.push({
                                particular: key,
                                details: value,
                                link: linkData
                            });
                        }
                    }
                }
                return result;
            """)
        
        # Format the table data better
        formatted_table = []
        for item in table_data:
            # Clean up the details text
            details = item['details']
            # Remove extra whitespace and newlines
            details = ' '.join(details.split())
            
            formatted_item = {
                "particular": item['particular'],
                "details": details
            }
            
            if item.get('link'):
                formatted_item["link"] = item['link']
                
            formatted_table.append(formatted_item)
        
        data["college_info"]["highlights"]["table"] = formatted_table

    except Exception as e:
        data["college_info"]["highlights"]["summary"] = "Summary not available"
        data["college_info"]["highlights"]["table"] = []


    for item in data["college_info"]["highlights"]["table"]:
        print(f"  - {item['particular']}: {item['details'][:50]}...")

    wait.until(
        EC.presence_of_element_located(
            (By.ID, "ovp_section_popular_courses")
        )
    )

    # ================= INTRO / SUMMARY =================
    data["intro"] = driver.execute_script("""
       let el = document.querySelector('#EdContent__ovp_section_popular_courses');
       if (!el) return null;
   
       let ps = el.querySelectorAll('p');
       let out = [];
   
       ps.forEach(p => {
           let t = p.textContent.replace(/\\s+/g, ' ').trim();
           if (t.length > 20) out.push(t);
       });
   
       return out.join("\\n");
       """)

    # ================= COURSES (FIXED) =================
    courses = driver.execute_script("""
        let result = [];

        document.querySelectorAll('div.base_course_tuple > div[id^="tuple_"]').forEach(tuple => {

            let course = {};

            // name + url
            let h3 = tuple.querySelector('h3');
            course.course_name = h3 ? h3.innerText.trim() : null;
            course.course_url = h3 ? h3.closest('a')?.href : null;

            // duration
            let spans = tuple.querySelectorAll('.edfa span');
            course.duration = spans.length > 1 ? spans[1].innerText.trim() : null;

            // rating + reviews
            let ratingBlock = tuple.querySelector('a[href*="reviews"]');
            if (ratingBlock) {
                course.rating = ratingBlock.querySelector('span')?.innerText.trim() || null;
                let r = ratingBlock.querySelector('.e040');
                course.reviews = r ? r.innerText.replace(/[()]/g, '') : null;
            }

            // ranking
            course.ranking =
                tuple.querySelector('.ba04')?.innerText.trim() || null;

            // ===== EXAMS ACCEPTED (SAFE) =====
            course.exams = [];
            tuple.querySelectorAll('label').forEach(label => {
                if (label.innerText.includes('Exams Accepted')) {
                    let ul = label.parentElement.querySelector('ul');
                    if (ul) {
                        ul.querySelectorAll('a').forEach(a => {
                            course.exams.push(a.innerText.trim());
                        });
                    }
                }
            });

            // ===== FEES =====
            course.fees = null;
            tuple.querySelectorAll('label').forEach(label => {
                if (label.innerText.includes('Total Tuition Fees')) {
                    let div = label.parentElement.querySelector('div');
                    if (div) {
                        course.fees = div.innerText.replace('Get Fee Details', '').trim();
                    }
                }
            });

            // ===== SALARY / PLACEMENT =====
            course.median_salary = null;
            tuple.querySelectorAll('label').forEach(label => {
                if (
                    label.innerText.includes('Median Salary') ||
                    label.innerText.includes('Placement Rating')
                ) {
                    let span = label.parentElement.querySelector('span');
                    if (span) {
                        course.median_salary = span.innerText.trim();
                    }
                }
            });

            result.push(course);
        });

        return result;
    """)
    data["courses"] = courses

    # ================= FAQs =================
    # ================= CLEAN FAQS =================
    try:
        faq_section = driver.find_element(By.ID, "sectional-faqs-0")
        driver.execute_script("arguments[0].scrollIntoView(true);", faq_section)
        time.sleep(2)

        questions = faq_section.find_elements(By.CLASS_NAME, "html-0")

        for q in questions:
            driver.execute_script("arguments[0].click();", q)
            time.sleep(0.5)

            question_text = q.text.replace("Q:", "").strip()

            try:
                ans_block = q.find_element(
                    By.XPATH,
                    "./following-sibling::div//div[contains(@class,'facb5f')]"
                )
                answer_text = clean_text(ans_block.text.replace("A:", "").strip())
            except:
                answer_text = ""

            data["college_info"]["highlights"]["faqs"].append({
                "question": question_text,
                "answer": answer_text
            })
    except:
        pass
    # ================= PLACEMENTS SECTION - FIX FOR DYNAMIC CONTENT =================
    try:
        
        
        # Wait for placements section
        placements_section = wait.until(
            EC.presence_of_element_located((By.ID, "ovp_section_placements"))
        )
        
        # Scroll to make sure everything is visible
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", placements_section)
        time.sleep(1)
        
        # Initialize data
        data["placements"] = {
            "overview": "",
            "course_wise_data": [],
            "top_recruiters": [],
            "student_insights": [],
            "faqs": [],
            "key_statistics": {}
        }
        
        # 🔹 1. OVERVIEW TEXT - Try different selectors
        try:
            # Try multiple selector approaches
            overview_selectors = [
                "#ovp_section_placements .wikiContents p",
                "#ovp_section_placements p",
                ".faq__according-wrapper p"
            ]
            
            overview_texts = []
            for selector in overview_selectors:
                try:
                    paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and len(text) > 30:
                            # Skip video descriptions and links
                            if not any(x in text.lower() for x in ['check out', 'video', 'click here', '→']):
                                overview_texts.append(text)
                except:
                    continue
                
                if overview_texts:
                    break
            
            # Take meaningful paragraphs
            meaningful_paras = []
            for text in overview_texts:
                if any(word in text.lower() for word in ['placement', 'package', 'salary', 'offer', 'student']):
                    meaningful_paras.append(text)
            
            if meaningful_paras:
                data["placements"]["overview"] = "\n\n".join(meaningful_paras[:3])
            elif overview_texts:
                data["placements"]["overview"] = "\n\n".join(overview_texts[:3])
            else:
                data["placements"]["overview"] = "Overview not available"
                
        except Exception as e:
            
            data["placements"]["overview"] = "Overview not available"
        
        # 🔹 2. COURSE-WISE SALARIES - Use JavaScript to extract table data
        try:
            course_data = driver.execute_script("""
                // Find the salary table
                const table = document.querySelector('#ovp_section_placements table.table.f866a4.dc8ace');
                if (!table) return [];
                
                const courses = [];
                // Get all rows except header
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const courseName = cells[0].textContent.trim();
                        const salary = cells[1].textContent.trim();
                        
                        if (courseName && salary && courseName !== 'Course') {
                            courses.push({
                                name: courseName,
                                median_salary: salary
                            });
                        }
                    }
                });
                
                return courses;
            """)
            
            data["placements"]["course_wise_data"] = course_data
           
            
        except Exception as e:
        
            data["placements"]["course_wise_data"] = []
        
        # 🔹 3. TOP RECRUITERS - Extract from carousel
        try:
            recruiters = driver.execute_script("""
                // Find recruiters in the carousel
                const recruiters = [];
                
                // Method 1: Look for recruiter buttons
                const recruiterButtons = document.querySelectorAll('#ovp_section_placements .e03a2f.f6be89');
                recruiterButtons.forEach(btn => {
                    const span = btn.querySelector('.cfed48.a183a8');
                    if (span) {
                        const name = span.textContent.trim();
                        if (name && name.length > 2) {
                            recruiters.push(name);
                        }
                    }
                });
                
                // Method 2: Look for all spans with recruiter names
                if (recruiters.length === 0) {
                    const allSpans = document.querySelectorAll('#ovp_section_placements span');
                    allSpans.forEach(span => {
                        const text = span.textContent.trim();
                        // Company names are usually in uppercase or have specific patterns
                        if (text && text.length > 2 && text.length < 50 && 
                            (text === text.toUpperCase() || 
                            text.includes('Group') || 
                            text.includes('Consulting') ||
                            text.includes('Bank'))) {
                            recruiters.push(text);
                        }
                    });
                }
                
                // Remove duplicates
                return [...new Set(recruiters)];
            """)
            
            data["placements"]["top_recruiters"] = recruiters
            
            
        except Exception as e:
          
            data["placements"]["top_recruiters"] = []
        
        # 🔹 4. STUDENT INSIGHTS
        try:
            insights = driver.execute_script("""
                const insights = [];
                
                // Find insights section
                const insightCards = document.querySelectorAll('#ovp_section_placements .cdf9a8');
                
                insightCards.forEach(card => {
                    const titleElem = card.querySelector('h6');
                    const descElem = card.querySelector('p');
                    
                    if (titleElem && descElem) {
                        insights.push({
                            category: titleElem.textContent.trim(),
                            feedback: descElem.textContent.trim()
                        });
                    }
                });
                
                return insights;
            """)
            
            data["placements"]["student_insights"] = insights
           
            
        except Exception as e:
        
            data["placements"]["student_insights"] = []
        
        # 🔹 5. FAQS - Extract from FAQ section
        try:
            faqs = driver.execute_script("""
                const faqs = [];
                
                // Find all questions
                const questionElements = document.querySelectorAll('#ovp_section_placements .ea1844');
                
                questionElements.forEach((qElem, index) => {
                    // Extract question text
                    let question = '';
                    const qSpan = qElem.querySelector('.flx-box span:nth-child(3)');
                    if (qSpan) {
                        question = qSpan.textContent.trim();
                    } else {
                        question = qElem.textContent.replace('Q:', '').trim();
                    }
                    
                    if (question) {
                        // Find corresponding answer
                        const nextSibling = qElem.nextElementSibling;
                        let answer = '';
                        
                        if (nextSibling && nextSibling.classList.contains('f61835')) {
                            const answerDiv = nextSibling.querySelector('.wikkiContents');
                            if (answerDiv) {
                                // Get text content, remove unnecessary parts
                                answer = answerDiv.textContent.trim();
                                // Remove "Not satisfied with answer?" part
                                answer = answer.replace(/Not satisfied with answer.*/i, '').trim();
                            }
                        }
                        
                        if (question && answer) {
                            faqs.push({
                                question: question,
                                answer: answer.substring(0, 500) // Limit answer length
                            });
                        }
                    }
                });
                
                return faqs;
            """)
            
            data["placements"]["faqs"] = faqs
           
            
        except Exception as e:
          
            data["placements"]["faqs"] = []
        
        # 🔹 6. KEY STATISTICS
        try:
            # Get text and extract statistics
            all_text = placements_section.text
            
            stats = {}
            import re
            
            # Extract key numbers
            patterns = [
                (r'(\d+)\s*offers.*?presented', 'offers_made'),
                (r'(\d+)\s*students.*?participated', 'students_participated'),
                (r'highest.*?package.*?(INR\s*[\d.,]+\s*LPA)', 'highest_package'),
                (r'average.*?package.*?(INR\s*[\d.,]+\s*LPA)', 'average_package'),
                (r'(\d+%)\s*placement rate', 'placement_rate'),
                (r'(\d+)\s*companies.*?participated', 'companies_participated')
            ]
            
            for pattern, key in patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    stats[key] = match.group(1)
            
            data["placements"]["key_statistics"] = stats
            
            
        except Exception as e:
       
            data["placements"]["key_statistics"] = {}
        
     
        
    except Exception as e:
        pass


    # ================= FEES & ELIGIBILITY SECTION =================
    try:
        print("Extracting fees and eligibility data...")
        
        # Wait for the section
        fees_section = wait.until(
            EC.presence_of_element_located((By.ID, "ovp_section_fees_and_eligibility"))
        )
        
        # Scroll to section
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", fees_section)
        time.sleep(1)
        
        # Initialize data structure
        data["fees_and_eligibility"] = {
            "overview": "",
            "courses_table": [],
            "faqs": [],
            "key_statistics": {}
        }
        
        # 🔹 1. OVERVIEW TEXT
        try:
            overview_wrapper = fees_section.find_element(By.CSS_SELECTOR, ".faq__according-wrapper")
            paragraphs = overview_wrapper.find_elements(By.TAG_NAME, "p")
            
            overview_texts = []
            for p in paragraphs:
                text = p.text.strip()
                if text and len(text) > 30:
                    overview_texts.append(text)
            
            data["fees_and_eligibility"]["overview"] = "\n\n".join(overview_texts[:3])
            
            
        except Exception as e:
           
            data["fees_and_eligibility"]["overview"] = "Overview not available"
        
        # 🔹 2. COURSES TABLE DATA
        try:
            # Find the main table
            table = fees_section.find_element(By.CSS_SELECTOR, "table.table.a82bdd")
            
            courses_data = []
            # Get all rows from table body
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        # Course name and count
                        course_cell = cells[0]
                        course_name_elem = course_cell.find_element(By.TAG_NAME, "a")
                        course_name = course_name_elem.text.strip()
                        
                        # Course count
                        try:
                            course_count_elem = course_cell.find_element(By.CLASS_NAME, "d94f03")
                            course_count_text = course_count_elem.text.strip()
                            # Extract number from text like "(4 courses)"
                            import re
                            course_count_match = re.search(r'(\d+)', course_count_text)
                            course_count = int(course_count_match.group(1)) if course_count_match else None
                        except:
                            course_count = None
                        
                        # Tuition fees
                        fees_cell = cells[1]
                        fees_text = fees_cell.text.strip()
                        # Remove "Get Fee Details" text
                        fees_clean = fees_text.replace("Get Fee Details", "").strip()
                        
                        # Eligibility
                        eligibility_cell = cells[2]
                        eligibility_text = eligibility_cell.text.strip()
                        
                        # Extract detailed eligibility information
                        eligibility_data = {}
                        
                        # Check for graduation percentage
                        if "Graduation" in eligibility_text:
                            grad_match = re.search(r'Graduation.*?(\d+)\s*%', eligibility_text)
                            if grad_match:
                                eligibility_data["graduation_percentage"] = f"{grad_match.group(1)}%"
                        
                        # Extract exams
                        exams = []
                        exam_links = eligibility_cell.find_elements(By.TAG_NAME, "a")
                        for exam_link in exam_links:
                            exam_name = exam_link.text.strip()
                            if exam_name:
                                exams.append(exam_name)
                        
                        if exams:
                            eligibility_data["exams"] = exams
                        
                        # Prepare course data
                        course_info = {
                            "course_name": course_name,
                            "course_count": course_count,
                            "tuition_fees": fees_clean,
                            "eligibility": eligibility_data if eligibility_data else eligibility_text
                        }
                        
                        # Add link if available
                        try:
                            course_link = course_name_elem.get_attribute("href")
                            course_info["link"] = course_link
                        except:
                            pass
                        
                        courses_data.append(course_info)
                        
                except Exception as e:
                    
                    continue
            
            data["fees_and_eligibility"]["courses_table"] = courses_data
           
            
        except Exception as e:
           
            data["fees_and_eligibility"]["courses_table"] = []
        
        # 🔹 3. FAQS - FIXED VERSION
        try:
            # First, make sure FAQ section is visible by scrolling to it
            try:
                faq_section_element = fees_section.find_element(By.CSS_SELECTOR, ".sectional-faqs")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", faq_section_element)
                time.sleep(1)
            except:
                pass
            
            # Use JavaScript to extract FAQs - more reliable
            faqs_data = driver.execute_script("""
                // Find FAQ section within fees section
                const faqSection = document.querySelector('#ovp_section_fees_and_eligibility .sectional-faqs');
                if (!faqSection) return [];
                
                const faqs = [];
                
                // Get all question elements
                const questionElements = faqSection.querySelectorAll('.ea1844');
                
                questionElements.forEach((qElem, index) => {
                    try {
                        // Extract question text
                        let questionText = '';
                        const qSpan = qElem.querySelector('.flx-box span:nth-child(3)');
                        if (qSpan) {
                            questionText = qSpan.textContent.trim();
                        } else {
                            // Fallback: get all text and remove "Q:"
                            questionText = qElem.textContent.replace('Q:', '').trim();
                        }
                        
                        if (questionText) {
                            // Find corresponding answer
                            let answerText = '';
                            let nextElem = qElem.nextElementSibling;
                            
                            // Look for answer in next sibling elements
                            while (nextElem) {
                                if (nextElem.classList && nextElem.classList.contains('f61835')) {
                                    const answerDiv = nextElem.querySelector('.wikkiContents');
                                    if (answerDiv) {
                                        answerText = answerDiv.textContent.trim();
                                        // Clean up answer text
                                        answerText = answerText.replace(/Not satisfied with answer.*/gi, '')
                                                            .replace(/Ask Shiksha GPT.*/gi, '')
                                                            .trim();
                                    }
                                    break;
                                }
                                nextElem = nextElem.nextElementSibling;
                            }
                            
                            if (questionText && answerText) {
                                faqs.push({
                                    question: questionText,
                                    answer: answerText.substring(0, 1500) // Limit length
                                });
                            }
                        }
                    } catch (e) {
                        console.log('Error parsing FAQ:', e);
                    }
                });
                
                return faqs;
            """)
            
            if faqs_data:
                data["fees_and_eligibility"]["faqs"] = faqs_data
                
            else:
              
                try:
                    faq_section = fees_section.find_element(By.CSS_SELECTOR, ".sectional-faqs")
                    
                    # Get all text and parse manually
                    all_faq_text = faq_section.text
                    lines = all_faq_text.split('\n')
                    
                    faqs_list = []
                    current_q = None
                    current_a = []
                    in_answer = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Check if this is a question
                        if line.startswith('Q:') or ('?' in line and len(line) < 200):
                            # Save previous FAQ
                            if current_q and current_a:
                                faqs_list.append({
                                    "question": current_q,
                                    "answer": ' '.join(current_a)
                                })
                            
                            # Start new FAQ
                            current_q = line.replace('Q:', '').strip()
                            current_a = []
                            in_answer = True
                        elif in_answer and current_q:
                            # This is part of answer (skip FAQ navigation text)
                            if not any(x in line for x in ['Not satisfied', 'Ask Shiksha GPT', 'View other answers']):
                                current_a.append(line)
                    
                    # Add last FAQ
                    if current_q and current_a:
                        faqs_list.append({
                            "question": current_q,
                            "answer": ' '.join(current_a)
                        })
                    
                    data["fees_and_eligibility"]["faqs"] = faqs_list
                   
                    
                except Exception as e:
                   
                    data["fees_and_eligibility"]["faqs"] = []
            
        except Exception as e:
           
            data["fees_and_eligibility"]["faqs"] = []
        # 🔹 4. KEY STATISTICS (from overview)
        try:
            stats = {}
            
            # Extract fee range from overview
            overview_text = data["fees_and_eligibility"]["overview"]
            import re
            
            # Fee range pattern
            fee_range_match = re.search(r'range between\s*(INR[^.]*?)\s*to\s*(INR[^.]*?)\.', overview_text)
            if fee_range_match:
                stats["fee_range"] = f"{fee_range_match.group(1)} to {fee_range_match.group(2)}"
            
            # Duration range
            duration_match = re.search(r'duration.*?ranges from\s*(\d+[^.]*?)\s*to\s*(\d+[^.]*?)\.', overview_text)
            if duration_match:
                stats["duration_range"] = f"{duration_match.group(1)} to {duration_match.group(2)}"
            
            # Minimum graduation percentage
            grad_match = re.search(r'minimum.*?(\d+)\s*%', overview_text, re.IGNORECASE)
            if grad_match:
                stats["minimum_graduation_percentage"] = f"{grad_match.group(1)}%"
            
            # Accepted exams
            exams_match = re.search(r'scores of\s*([^.]*?)for admission', overview_text)
            if exams_match:
                stats["accepted_exams"] = exams_match.group(1).strip()
            
            data["fees_and_eligibility"]["key_statistics"] = stats
           
            
        except Exception as e:
          
            data["fees_and_eligibility"]["key_statistics"] = {}
        
       
        
    except Exception as e:
       
        import traceback
        traceback.print_exc()
        data["fees_and_eligibility"] = {
            "overview": "Data not available",
            "courses_table": [],
            "faqs": [],
            "key_statistics": {}
        }

    # ================= STUDENT REVIEWS SECTION =================
    try:
      
        reviews_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".a2eb03"))
        )
        
        # Scroll to make all reviews visible
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", reviews_container)
        time.sleep(2)
        
        # Initialize data structure
        data["student_reviews"] = {
            "total_reviews_count": 0,
            "average_rating": 0,
            "reviews_list": [],
            "video_reviews": [],
            "review_summary": {}
        }
        
        # 🔹 1. GET ALL REVIEW CARDS
        try:
            # Find all review cards
            review_cards = reviews_container.find_elements(By.CSS_SELECTOR, ".paper-card[id^='review_']")
        
            reviews_data = []
            
            for card in review_cards:
                try:
                    # Skip video reviews section
                    if "review_mini_clips" in card.get_attribute("id"):
                        continue
                    
                    # Extract review ID
                    review_id = card.get_attribute("id").replace("review_", "")
                    
                    # 🔹 BASIC INFO
                    # Student name and batch
                    try:
                        student_name_elem = card.find_element(By.CSS_SELECTOR, ".f1b51a")
                        student_name = student_name_elem.text.strip()
                    except:
                        student_name = "Anonymous"
                    
                    try:
                        batch_info_elem = card.find_element(By.CSS_SELECTOR, ".b7f142")
                        batch_info = batch_info_elem.text.strip()
                    except:
                        batch_info = "Not specified"
                    
                    # Check if verified
                    try:
                        verified_badge = card.find_element(By.CSS_SELECTOR, ".b2e7fe.c3eef6")
                        is_verified = True
                    except:
                        is_verified = False
                    
                    # 🔹 OVERALL RATING
                    try:
                        rating_elem = card.find_element(By.CSS_SELECTOR, ".f05026 span")
                        overall_rating = rating_elem.text.strip()
                    except:
                        overall_rating = "Not rated"
                    
                    # 🔹 CATEGORY RATINGS
                    category_ratings = []
                    try:
                        category_spans = card.find_elements(By.CSS_SELECTOR, ".d757cc")
                        for cat_span in category_spans:
                            cat_text = cat_span.text.strip()
                            if cat_text:
                                # Parse like "5Placements" → {"category": "Placements", "rating": "5"}
                                import re
                                match = re.match(r'(\d+)(.+)', cat_text)
                                if match:
                                    category_ratings.append({
                                        "category": match.group(2).strip(),
                                        "rating": match.group(1).strip()
                                    })
                    except:
                        category_ratings = []
                    
                    # 🔹 REVIEW TITLE
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, ".d7e2f2")
                        review_title = title_elem.text.strip()
                    except:
                        review_title = "Review"
                    
                    # 🔹 REVIEW CONTENT (Detailed sections)
                    review_content = {}
                    try:
                        # Get all review sections
                        content_divs = card.find_elements(By.CSS_SELECTOR, ".dca212 div")
                        
                        for div in content_divs:
                            text = div.text.strip()
                            if text:
                                # Split by ": " to get category and content
                                if ": " in text:
                                    parts = text.split(": ", 1)
                                    if len(parts) == 2:
                                        category = parts[0].replace("strong>", "").replace("<", "").strip()
                                        content = parts[1].strip()
                                        review_content[category] = content
                                else:
                                    # If no category, add as general content
                                    review_content["General"] = text
                    except:
                        review_content = {"General": "Content not available"}
                    
                    # 🔹 REVIEW DATE
                    try:
                        date_elem = card.find_element(By.CSS_SELECTOR, ".f3dfa4")
                        review_date = date_elem.text.replace("Reviewed on", "").strip()
                    except:
                        review_date = "Date not available"
                    
                    # 🔹 HELPFUL COUNT
                    helpful_count = 0
                    try:
                        helpful_text = card.find_element(By.CSS_SELECTOR, ".c34bdf span:last-child").text
                        # Extract number from text like "2 people found this helpful"
                        import re
                        helpful_match = re.search(r'(\d+)', helpful_text)
                        if helpful_match:
                            helpful_count = int(helpful_match.group(1))
                    except:
                        helpful_count = 0
                    
                    # 🔹 CHECK FOR PHOTOS
                    has_photos = False
                    photo_urls = []
                    try:
                        photos_section = card.find_element(By.CSS_SELECTOR, ".d77071")
                        photos = photos_section.find_elements(By.TAG_NAME, "img")
                        if photos:
                            has_photos = True
                            for photo in photos[:3]:  # Limit to first 3 photos
                                photo_url = photo.get_attribute("src")
                                if photo_url:
                                    photo_urls.append(photo_url)
                    except:
                        has_photos = False
                    
                    # Compile review data
                    review_data = {
                        "review_id": review_id,
                        "student_name": student_name,
                        "batch_info": batch_info,
                        "is_verified": is_verified,
                        "overall_rating": overall_rating,
                        "category_ratings": category_ratings,
                        "review_title": review_title,
                        "review_content": review_content,
                        "review_date": review_date,
                        "helpful_count": helpful_count,
                        "has_photos": has_photos,
                        "photo_urls": photo_urls if has_photos else []
                    }
                    
                    reviews_data.append(review_data)
                    
                except Exception as e:
                    print(f"Error parsing review card: ")
                    continue
            
            data["student_reviews"]["reviews_list"] = reviews_data
            data["student_reviews"]["total_reviews_count"] = len(reviews_data)
            
            
        except Exception as e:
            
            data["student_reviews"]["reviews_list"] = []
        
        # 🔹 2. VIDEO REVIEWS (Mini Clips)
        try:
            video_reviews = []
            
            # Find video reviews section
            video_section = reviews_container.find_element(By.ID, "review_mini_clips")
            
            # Get all video items
            video_items = video_section.find_elements(By.CSS_SELECTOR, ".d87173")
            
            for video_item in video_items:
                try:
                    # Video title/category
                    category = video_item.get_attribute("data-corouselkeyname") or "Video Review"
                    
                    # Thumbnail image
                    thumbnail_elem = video_item.find_element(By.CSS_SELECTOR, ".f69743")
                    thumbnail_url = thumbnail_elem.get_attribute("src")
                    
                    # Video description
                    try:
                        desc_elem = video_item.find_element(By.CSS_SELECTOR, ".ada2b9")
                        description = desc_elem.text.strip()
                    except:
                        description = f"{category} video"
                    
                    # Check if it's a YouTube embed
                    try:
                        iframe = video_item.find_element(By.TAG_NAME, "iframe")
                        video_url = iframe.get_attribute("src")
                        is_embedded = True
                    except:
                        video_url = None
                        is_embedded = False
                    
                    video_reviews.append({
                        "category": category,
                        "description": description,
                        "thumbnail_url": thumbnail_url,
                        "video_url": video_url,
                        "is_embedded": is_embedded
                    })
                    
                except Exception as e:
                    
                    continue
            
            data["student_reviews"]["video_reviews"] = video_reviews
            
            
        except Exception as e:
        
            data["student_reviews"]["video_reviews"] = []
        
        # 🔹 3. TOTAL REVIEWS COUNT FROM "VIEW ALL" BUTTON
        try:
            # Look for "View All X Reviews" button
            view_all_btn = reviews_container.find_element(By.CSS_SELECTOR, ".ea87ef")
            btn_text = view_all_btn.text.strip()
            
            # Extract number from text like "View All 111 Reviews"
            import re
            count_match = re.search(r'(\d+)', btn_text)
            if count_match:
                total_reviews = int(count_match.group(1))
                data["student_reviews"]["total_reviews_count"] = total_reviews
          
                
        except Exception as e:
            # Use count from extracted reviews if available
            if data["student_reviews"]["total_reviews_count"] == 0:
                data["student_reviews"]["total_reviews_count"] = len(data["student_reviews"]["reviews_list"])
        
        # 🔹 4. CALCULATE AVERAGE RATING AND SUMMARY
        try:
            if data["student_reviews"]["reviews_list"]:
                total_rating = 0
                rating_count = 0
                category_totals = {}
                category_counts = {}
                
                for review in data["student_reviews"]["reviews_list"]:
                    # Overall rating
                    try:
                        rating = float(review["overall_rating"])
                        total_rating += rating
                        rating_count += 1
                    except:
                        pass
                    
                    # Category ratings
                    for cat_rating in review.get("category_ratings", []):
                        category = cat_rating["category"]
                        rating = cat_rating["rating"]
                        
                        try:
                            rating_val = float(rating)
                            if category not in category_totals:
                                category_totals[category] = 0
                                category_counts[category] = 0
                            
                            category_totals[category] += rating_val
                            category_counts[category] += 1
                        except:
                            pass
                
                # Calculate averages
                if rating_count > 0:
                    data["student_reviews"]["average_rating"] = round(total_rating / rating_count, 1)
                
                # Calculate category averages
                category_averages = {}
                for category in category_totals:
                    if category_counts[category] > 0:
                        category_averages[category] = round(category_totals[category] / category_counts[category], 1)
                
                # Create summary
                data["student_reviews"]["review_summary"] = {
                    "average_overall_rating": data["student_reviews"]["average_rating"],
                    "total_reviews_analyzed": rating_count,
                    "category_averages": category_averages,
                    "verified_reviews_count": sum(1 for r in data["student_reviews"]["reviews_list"] if r["is_verified"]),
                    "reviews_with_photos": sum(1 for r in data["student_reviews"]["reviews_list"] if r["has_photos"])
                }
                
                print(f"✓ Calculated average rating: {data['student_reviews']['average_rating']}")
                
        except Exception as e:
            
            data["student_reviews"]["review_summary"] = {}
        
      
        
    except Exception as e:
        
        import traceback
        traceback.print_exc()
        
        data["student_reviews"] = {
            "total_reviews_count": 0,
            "average_rating": 0,
            "reviews_list": [],
            "video_reviews": [],
            "review_summary": {}
        }


    return data 
def clean_text(text):
    remove_words = [
        "Upvote",
        "Not satisfied with answer?",
        "Ask Shiksha GPT",
        "Get Placement Report",
        "Get Admission Info"
    ]
    for w in remove_words:
        text = text.replace(w, "")
    return re.sub(r'\n+', '\n', text).strip()

def scrape_courses(driver, URLS):
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    try:
        driver.get(URLS["courses"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["courses"])
    
    wait = WebDriverWait(driver, 20)
    
    # Wait for page to load completely
    time.sleep(2)
    
    # ---------- LOGO AND HEADER INFO ----------
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")
           
        except:
            pass
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
            pass
        except:
           pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            pass
        
        # Rest of your existing header extraction code...
        
    except Exception as e:
        print("⚠️ Error in college header section:")
    
    # ---------- COLLEGE NAME ----------
    try:
        name_elem = driver.find_element(By.CSS_SELECTOR, ".cc5e8d")
        college_info["college_name"] = name_elem.text.strip()
    except Exception as e:
        pass
    
    # ---------- LOCATION ----------
    try:
        location_elem = driver.find_element(By.CSS_SELECTOR, ".f90eb6.a73e41")
        location_text = location_elem.text.strip()
        if "," in location_text:
            location_parts = location_text.split(",")
            college_info["location"] = location_parts[0].strip()
            college_info["city"] = location_parts[1].strip() if len(location_parts) > 1 else ""
        else:
            college_info["location"] = location_text
    except Exception as e:
        print("Location error:")
    
    # ---------- RATING AND REVIEWS ----------
    try:
        # Rating
        rating_elem = driver.find_element(By.CSS_SELECTOR, ".f1b26c")
        rating_text = rating_elem.text.strip()
        if "/" in rating_text:
            rating_parts = rating_text.split("/")
            college_info["rating"] = rating_parts[0].strip()
    except Exception as e:
        print("Rating error:")
    
    try:
        # Reviews count
        reviews_elem = driver.find_element(By.CSS_SELECTOR, 'a[href*="reviews"]')
        reviews_text = reviews_elem.text.strip()
        reviews_match = re.search(r'\((\d+)\s*Reviews\)', reviews_text)
        if reviews_match:
            college_info["reviews_count"] = int(reviews_match.group(1))
    except Exception as e:
        print("Reviews error")
    
    # ---------- Q&A COUNT ----------
    try:
        qa_elem = driver.find_element(By.CSS_SELECTOR, 'a[href*="questions"]')
        qa_text = qa_elem.text.strip()
        qa_match = re.search(r'([\d.]+k?)', qa_text)
        if qa_match:
            qa_value = qa_match.group(1)
            if 'k' in qa_value.lower():
                college_info["qa_count"] = int(float(qa_value.lower().replace('k', '')) * 1000)
            else:
                college_info["qa_count"] = int(qa_value)
    except Exception as e:
        print("Q&A error:")
    
    # ---------- INSTITUTE TYPE AND ESTABLISHED YEAR ----------
    try:
        list_items = driver.find_elements(By.CSS_SELECTOR, ".ff9e36 li .f1b26c .b00d1d")
        for item in list_items:
            text = item.text.strip().lower()
            if "institute" in text or "public" in text or "government" in text:
                college_info["institute_type"] = item.text.strip()
            elif "estd" in text or "est." in text:
                year_match = re.search(r'\d{4}', item.text)
                if year_match:
                    college_info["established_year"] = int(year_match.group())
    except Exception as e:
        print("Institute info error")
    
    # ---------- FEE STRUCTURE HEADING AND OVERVIEW ----------
    fee_heading = ""
    fee_overview = ""
    
    try:
        # Try to find fee structure heading
        fee_heading_elems = driver.find_elements(By.CSS_SELECTOR, ".ab2e01 .ae88c4, .c5d378 .ae88c4, .h2 .ae88c4")
        for elem in fee_heading_elems:
            text = elem.text.strip()
            if "Fee Structure" in text or "fee" in text.lower():
                fee_heading = text
                break
        
        # Try to find fee structure overview/description
        overview_elems = driver.find_elements(By.CSS_SELECTOR, ".wikiContents p, .faq__according-wrapper p, .dfbe34 p")
        for elem in overview_elems:
            text = elem.text.strip()
            if text and len(text) > 50:
                # Check if it's related to fees
                if "fee" in text.lower() or "payment" in text.lower() or "tuition" in text.lower():
                    fee_overview = text
                    break
        
     
        
    except Exception as e:
        print("Fee heading/overview error:")
    
    # ---------- FEE STRUCTURE TABLE DATA (IMPROVED WITH CLEANING) ----------
    fee_structure = []
    
    try:
        # Try to find fee structure section using multiple selectors
        fee_sections = driver.find_elements(By.CSS_SELECTOR, "#acp_section_fees, [id*='fee'], .paper-card")
        
        for fee_section in fee_sections:
            try:
                section_text = fee_section.text.lower()
                if "fee" in section_text or "tuition" in section_text:
                  
                    
                    # Extract fee structure table
                    try:
                        fee_tables = fee_section.find_elements(By.TAG_NAME, "table")
                        for table in enumerate(fee_tables):
                            
                            
                            # Get all rows
                            rows = table.find_elements(By.TAG_NAME, "tr")
                            if not rows:
                                continue
                            
                            # Extract table headers
                            headers = []
                            header_cells = rows[0].find_elements(By.TAG_NAME, "th")
                            
                            for cell in header_cells:
                                try:
                                    # Try to get text from font tag first
                                    font_tag = cell.find_element(By.TAG_NAME, "font")
                                    header_text = font_tag.text.strip()
                                except:
                                    header_text = cell.text.strip()
                                
                                if header_text:
                                    headers.append(header_text)
                            
                            # If no headers found in th, try first row as headers
                            if not headers and rows:
                                first_row_cells = rows[0].find_elements(By.TAG_NAME, "td")
                                if first_row_cells:
                                    for cell in first_row_cells:
                                        headers.append(cell.text.strip())
                                    # Skip first row as it's now headers
                                    rows = rows[1:]
                            
                         
                            
                            # Extract table rows
                            for row_idx, row in enumerate(rows):
                                try:
                                    cells = row.find_elements(By.TAG_NAME, "td")
                                    if not cells:
                                        continue
                                    
                                    fee_item = {}
                                    is_empty_row = True
                                    
                                    for idx, cell in enumerate(cells):
                                        if idx >= len(headers):
                                            continue
                                            
                                        cell_text = cell.text.strip()
                                        if cell_text:
                                            is_empty_row = False
                                        
                                        # Get header name (clean it)
                                        header_name = headers[idx].lower().replace(" ", "_").replace("-", "_")
                                        if header_name == "":
                                            header_name = f"column_{idx}"
                                        
                                        # Clean the cell text - remove newlines and extra spaces
                                        cleaned_text = re.sub(r'\s*\n\s*', ' ', cell_text)  # Replace newlines with space
                                        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Remove extra spaces
                                        
                                        # Check if cell contains link
                                        try:
                                            link = cell.find_element(By.TAG_NAME, "a")
                                            link_href = link.get_attribute("href")
                                            link_text = link.text.strip()
                                            cleaned_link_text = re.sub(r'\s*\n\s*', ' ', link_text)
                                            cleaned_link_text = re.sub(r'\s+', ' ', cleaned_link_text).strip()
                                            
                                            # If cell has both text and link
                                            if cleaned_text and cleaned_text != cleaned_link_text:
                                                fee_item[header_name] = {
                                                    "text": cleaned_text,
                                                    "link": link_href if link_href else None
                                                }
                                            else:
                                                # If only link text
                                                fee_item[header_name] = {
                                                    "text": cleaned_link_text,
                                                    "link": link_href if link_href else None
                                                }
                                        except:
                                            # No link found, just store cleaned text
                                            if cleaned_text:
                                                fee_item[header_name] = cleaned_text
                                    
                                    # Skip empty rows
                                    if is_empty_row:
                                        continue
                                    
                                    # Also check for any main course links in the row
                                    try:
                                        main_links = row.find_elements(By.CSS_SELECTOR, "a[href*='courses']")
                                        if main_links:
                                            fee_item["course_link"] = main_links[0].get_attribute("href")
                                    except:
                                        pass
                                    
                                    if fee_item:
                                        # Additional cleaning of the fee item
                                        cleaned_fee_item = {}
                                        for key, value in fee_item.items():
                                            if isinstance(value, dict):
                                                # Clean text in dictionary values
                                                cleaned_value = value.copy()
                                                if "text" in cleaned_value:
                                                    cleaned_value["text"] = re.sub(r'\s*\n\s*', ' ', cleaned_value["text"])
                                                    cleaned_value["text"] = re.sub(r'\s+', ' ', cleaned_value["text"]).strip()
                                                cleaned_fee_item[key] = cleaned_value
                                            elif isinstance(value, str):
                                                # Clean string values
                                                cleaned_text = re.sub(r'\s*\n\s*', ' ', value)
                                                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                                                cleaned_fee_item[key] = cleaned_text
                                            else:
                                                cleaned_fee_item[key] = value
                                        
                                        fee_structure.append(cleaned_fee_item)
                                       
                                    
                                except Exception as e:
                                   
                                    continue
                    
                    except Exception as e:
                        print("Error extracting fee table:")
                    
                    break  # Stop after first valid fee section
                    
            except Exception as e:
                print("Error processing fee section:")
                continue
        
        # Clean empty items from fee_structure
        fee_structure = [item for item in fee_structure if item and not all(value == "" or value == {} for value in item.values())]
        
        # If we have fee structure but headers are generic, rename them
        if fee_structure:
            # Check if we need to rename keys
            first_item = fee_structure[0]
            keys_to_rename = {}
            
            for key in first_item.keys():
                if key.startswith("column_") or key == "":
                    # Try to determine what this column represents
                    if "course" in str(first_item.get(key, "")).lower():
                        keys_to_rename[key] = "course_name"
                    elif "fee" in str(first_item.get(key, "")).lower() or "l" in str(first_item.get(key, "")) or "inr" in str(first_item.get(key, "")).lower():
                        keys_to_rename[key] = "tuition_fee"
                    elif "eligibility" in str(first_item.get(key, "")).lower() or "graduation" in str(first_item.get(key, "")).lower():
                        keys_to_rename[key] = "eligibility"
                    elif "one_time" in str(first_item.get(key, "")).lower():
                        keys_to_rename[key] = "one_time_fee"
                    elif "hostel" in str(first_item.get(key, "")).lower():
                        keys_to_rename[key] = "hostel_fee"
            
            # Rename keys in all items
            if keys_to_rename:
                for item in fee_structure:
                    for old_key, new_key in keys_to_rename.items():
                        if old_key in item:
                            item[new_key] = item.pop(old_key)
        

        
    except Exception as e:
        print("Fee structure error:")
    
    # ---------- COURSES OVERVIEW TEXT ----------
    overview_text = ""
    try:
        # Look for the overview section with heading
        overview_section = driver.find_element(By.ID, "acp_section_fees_and_eligibility")
        
        # Get the heading
        try:
            heading_elem = overview_section.find_element(By.CSS_SELECTOR, ".ae88c4")
            overview_text = heading_elem.text.strip() + "\n\n"
        except:
            pass
        
        # Get the overview paragraph text
        try:
            overview_para = overview_section.find_element(By.CSS_SELECTOR, ".faq__according-wrapper p")
            overview_text += overview_para.text.strip()
        except:
            # Try alternative selector
            try:
                wiki_content = overview_section.find_element(By.CSS_SELECTOR, ".wikiContents")
                overview_text += wiki_content.text.split("Read more")[0].strip()
            except:
                pass
        
        # Clean overview text
        if overview_text:
            overview_text = re.sub(r'\s*\n\s*', ' ', overview_text)
            overview_text = re.sub(r'\s+', ' ', overview_text).strip()
        
        
    except Exception as e:
        print("Courses overview error")
    
    # ---------- COURSES TABLE DATA ----------
    courses = []
    
    try:
        # Wait for courses table
        table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.a82bdd"))
        )
        
        # Get all rows from table body
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    # Course name and count
                    course_cell = cells[0]
                    try:
                        course_link = course_cell.find_element(By.TAG_NAME, "a")
                        course_name = course_link.text.strip()
                    except:
                        course_name = course_cell.text.strip()
                    
                    # Clean course name
                    course_name = re.sub(r'\s*\n\s*', ' ', course_name)
                    course_name = re.sub(r'\s+', ' ', course_name).strip()
                    
                    # Extract course count if available
                    course_count = None
                    try:
                        count_span = course_cell.find_element(By.CLASS_NAME, "d94f03")
                        count_text = count_span.text.strip()
                        count_match = re.search(r'\((\d+)\s*course', count_text)
                        if count_match:
                            course_count = int(count_match.group(1))
                    except:
                        pass
                    
                    # Tuition fees
                    fees_cell = cells[1]
                    fees_text = fees_cell.text.strip()
                    # Remove "Get Fee Details" text and clean
                    fees_clean = fees_text.replace("Get Fee Details", "").strip()
                    fees_clean = re.sub(r'\s*\n\s*', ' ', fees_clean)
                    fees_clean = re.sub(r'\s+', ' ', fees_clean).strip()
                    
                    # Eligibility
                    eligibility_cell = cells[2]
                    eligibility_text = eligibility_cell.text.strip()
                    eligibility_text = re.sub(r'\s*\n\s*', ' ', eligibility_text)
                    eligibility_text = re.sub(r'\s+', ' ', eligibility_text).strip()
                    
                    # Extract detailed eligibility information
                    eligibility_data = {}
                    
                    # Check for graduation percentage
                    if "Graduation" in eligibility_text:
                        grad_match = re.search(r'Graduation.*?(\d+)\s*%', eligibility_text)
                        if grad_match:
                            eligibility_data["graduation_percentage"] = f"{grad_match.group(1)}%"
                    
                    # Extract exams
                    exams = []
                    try:
                        exam_links = eligibility_cell.find_elements(By.TAG_NAME, "a")
                        for exam_link in exam_links:
                            exam_name = exam_link.text.strip()
                            exam_name = re.sub(r'\s*\n\s*', ' ', exam_name)
                            exam_name = re.sub(r'\s+', ' ', exam_name).strip()
                            if exam_name and exam_name not in ["+2 More", "+1 More", "More"]:
                                exams.append(exam_name)
                    except:
                        pass
                    
                    if exams:
                        eligibility_data["exams"] = exams
                    
                    # If no structured data found, store the raw text
                    if not eligibility_data and eligibility_text and eligibility_text != "– / –":
                        eligibility_data = eligibility_text
                    elif eligibility_text == "– / –":
                        eligibility_data = "Not specified"
                    
                    # Create course object
                    course_obj = {
                        "course_name": course_name,
                        "course_count": course_count,
                        "fees": fees_clean,
                        "eligibility": eligibility_data
                    }
                    
                    # Add course link if available
                    try:
                        course_link = course_cell.find_element(By.TAG_NAME, "a")
                        course_obj["link"] = course_link.get_attribute("href")
                    except:
                        pass
                    
                    courses.append(course_obj)
                    
            except Exception as e:
            
                continue
        
 
        
    except Exception as e:
        print("Error extracting courses table:")
        courses = []
    
    # ---------- FAQS DATA - IMPROVED CLEANING ----------
    faqs = []
    
    try:
        # First, check if FAQ section exists and is visible
        faq_section = driver.find_element(By.CSS_SELECTOR, ".sectional-faqs")
        
        # Scroll to FAQ section to ensure it's in view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", faq_section)
        time.sleep(1)
        
        # Use JavaScript to extract FAQs with better cleaning
        faqs_data = driver.execute_script("""
            const faqs = [];
            const faqSection = document.querySelector('.sectional-faqs');
            
            if (faqSection) {
                // Get all question elements
                const questionElements = faqSection.querySelectorAll('.ea1844');
                
                questionElements.forEach((qElem, index) => {
                    try {
                        // Extract question
                        let question = '';
                        
                        // Try multiple ways to get question
                        const qSpans = qElem.querySelectorAll('.flx-box span');
                        if (qSpans.length >= 3) {
                            question = qSpans[2].textContent.trim();
                        } else {
                            // Fallback: get all text and remove Q:
                            question = qElem.textContent.replace(/^Q:?\s*/i, '').trim();
                        }
                        
                        // Clean question text
                        question = question.replace(/\\s*\\n\\s*/g, ' ').replace(/\\s+/g, ' ').trim();
                        
                        if (question) {
                            // Find corresponding answer
                            let answer = '';
                            let nextElem = qElem.nextElementSibling;
                            
                            // Look for answer in next sibling elements
                            while (nextElem) {
                                if (nextElem.classList && nextElem.classList.contains('f61835')) {
                                    const answerDiv = nextElem.querySelector('.wikkiContents');
                                    if (answerDiv) {
                                        answer = answerDiv.textContent.trim();
                                        
                                        // Clean up answer text more aggressively
                                        answer = answer
                                            .replace(/Not satisfied with answer.*/gi, '')
                                            .replace(/Ask Shiksha GPT.*/gi, '')
                                            .replace(/\\s*\\n\\s*/g, ' ')  // Replace newlines with space
                                            .replace(/\\s+/g, ' ')  // Replace multiple spaces with single space
                                            .replace(/^A:\\s*/, '')  // Remove starting "A:"
                                            .replace(/^A&nbsp;\\s*/, '')  // Remove starting "A&nbsp;"
                                            .trim();
                                    }
                                    break;
                                }
                                nextElem = nextElem.nextElementSibling;
                            }
                            
                            if (question && answer) {
                                faqs.push({
                                    question: question,
                                    answer: answer.substring(0, 2000) // Limit length
                                });
                            }
                        }
                    } catch (e) {
                        console.log('Error parsing FAQ:', e);
                    }
                });
            }
            
            return faqs;
        """)
        
        if faqs_data:
            faqs = faqs_data
           
        else:
            # Fallback to Python method

            try:
                # Get all question elements
                question_elements = faq_section.find_elements(By.CSS_SELECTOR, ".ea1844")
                
                for i, q_elem in enumerate(question_elements):
                    try:
                        # Extract question
                        question = ""
                        try:
                            q_spans = q_elem.find_elements(By.CSS_SELECTOR, ".flx-box span")
                            if len(q_spans) >= 3:
                                question = q_spans[2].text.strip()
                            else:
                                question = q_elem.text.replace("Q:", "").replace("Q :", "").strip()
                        except:
                            question = q_elem.text.replace("Q:", "").strip()
                        
                        # Clean question
                        question = re.sub(r'\s*\n\s*', ' ', question)
                        question = re.sub(r'\s+', ' ', question).strip()
                        
                        # Find answer
                        answer = ""
                        try:
                            answer_elem = driver.execute_script("""
                                var elem = arguments[0];
                                var next = elem.nextElementSibling;
                                while (next) {
                                    if (next.classList.contains('f61835')) {
                                        return next;
                                    }
                                    next = next.nextElementSibling;
                                }
                                return null;
                            """, q_elem)
                            
                            if answer_elem:
                                answer_div = answer_elem.find_element(By.CSS_SELECTOR, ".wikkiContents")
                                answer_text = answer_div.text.strip()
                                
                                # Clean answer text
                                answer_text = re.sub(r'Not satisfied with answer.*', '', answer_text, flags=re.IGNORECASE)
                                answer_text = re.sub(r'Ask Shiksha GPT.*', '', answer_text, flags=re.IGNORECASE)
                                answer_text = re.sub(r'^\s*A:?\s*', '', answer_text)  # Remove starting "A:"
                                answer_text = re.sub(r'^\s*A&nbsp;\s*', '', answer_text)  # Remove starting "A&nbsp;"
                                answer_text = re.sub(r'\s*\n\s*', ' ', answer_text)  # Replace newlines with space
                                answer_text = re.sub(r'\s+', ' ', answer_text).strip()  # Normalize whitespace
                                
                                answer = answer_text
                        except:
                            pass
                        
                        if question and answer:
                            faqs.append({
                                "question": question,
                                "answer": answer[:1500] + "..." if len(answer) > 1500 else answer
                            })
                            
                    except Exception as e:
                
                        continue
                
           
                
            except Exception as e:
                print("Python FAQ extraction also failed:")
                faqs = []
        
        # Additional cleaning of FAQ answers
        for faq in faqs:
            faq["question"] = re.sub(r'\s+', ' ', faq["question"]).strip()
            faq["answer"] = re.sub(r'\s+', ' ', faq["answer"]).strip()
        
    except Exception as e:
        print("FAQ section error:")
        faqs = []
    
    # Create final response structure with organized fee structure
    result = {
        "college_info": college_info,
        "overview": overview_text,
        "courses": courses,
        "fee_structure": {
            "heading": fee_heading,
            "overview": fee_overview,
            "data": fee_structure  # Clean data only
        },
        "faqs": faqs
    }

    all_data = scrape_all_programs_and_courses(driver)
    faqs_section_data = scrape_faqs_section(driver)
    result.update(all_data)
    result.update(faqs_section_data)
    return result

def scrape_all_programs_and_courses(driver):

    all_programs_data = []
    all_courses_data = []
    
    # Wait for page to load completely
    time.sleep(2)
    

    
    # ---------- ALL PROGRAMS DATA ----------
    try:
       
        # Find all program tuples
        program_tuples = driver.find_elements(By.CSS_SELECTOR, ".acp_base_course_tuple .d15c8a.fb6321.a25c93")
        
        for program_tuple in program_tuples:
            try:
                program_data = {}
                
                # Extract program name
                try:
                    program_name_elem = program_tuple.find_element(By.CSS_SELECTOR, ".c42a97 .f443c7")
                    program_data["program_name"] = program_name_elem.text.strip()
                except:
                    program_data["program_name"] = "N/A"
                
                # Extract program details
                try:
                    details_elem = program_tuple.find_element(By.CSS_SELECTOR, ".ae8f7e")
                    details_text = details_elem.text.strip()
                    
                    # Parse course count
                    course_count_match = re.search(r'(\d+)\s*Course', details_text)
                    if course_count_match:
                        program_data["course_count"] = int(course_count_match.group(1))
                    
                    # Parse duration
                    duration_match = re.search(r'(\d+\s*(?:months?|years?|\s*-\s*\d+\s*(?:months?|years?)))', details_text)
                    if duration_match:
                        program_data["duration"] = duration_match.group(1).strip()
                    
                    # Parse rating
                    rating_match = re.search(r'(\d+\.\d+)', details_text)
                    if rating_match:
                        program_data["rating"] = float(rating_match.group(1))
                    
                    # Parse reviews count
                    reviews_match = re.search(r'\((\d+)\)', details_text)
                    if reviews_match:
                        program_data["reviews_count"] = int(reviews_match.group(1))
                    
                    # Parse ranking
                    ranking_match = re.search(r'#(\d+)\s+(\w+)', details_text)
                    if ranking_match:
                        program_data["ranking"] = {
                            "rank": ranking_match.group(1),
                            "source": ranking_match.group(2)
                        }
                        
                except Exception as e:
                    print("Error extracting program details:")
                
                # Extract exams accepted
                try:
                    exams_elem = program_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(1) .c8c9ee")
                    exams_text = exams_elem.text.strip()
                    if exams_text and exams_text != "– / –":
                        # Check if there's a list of exams
                        exam_links = exams_elem.find_elements(By.TAG_NAME, "a")
                        if exam_links:
                            program_data["exams_accepted"] = [link.text.strip() for link in exam_links if link.text.strip()]
                        else:
                            program_data["exams_accepted"] = exams_text
                    else:
                        program_data["exams_accepted"] = "Not specified"
                except:
                    program_data["exams_accepted"] = "Not specified"
                
                # Extract median salary
                try:
                    salary_elem = program_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(2) .c8c9ee")
                    salary_text = salary_elem.text.strip()
                    if salary_text and salary_text != "– / –":
                        program_data["median_salary"] = salary_text
                    else:
                        program_data["median_salary"] = "Not available"
                except:
                    program_data["median_salary"] = "Not available"
                
                # Extract total tuition fees
                try:
                    fees_elem = program_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(3) .c8c9ee")
                    fees_text = fees_elem.text.strip()
                    # Clean fees text
                    if fees_text and fees_text != "– / –":
                        fees_clean = re.sub(r'Get Fee Details.*', '', fees_text).strip()
                        program_data["total_tuition_fees"] = fees_clean
                    else:
                        program_data["total_tuition_fees"] = "Not available"
                except:
                    program_data["total_tuition_fees"] = "Not available"
                
                # Extract program link
                try:
                    program_link_elem = program_tuple.find_element(By.CSS_SELECTOR, ".c42a97 a")
                    program_data["program_link"] = program_link_elem.get_attribute("href")
                except:
                    program_data["program_link"] = None
                
                all_programs_data.append(program_data)
                
            except Exception as e:
                
                continue
        
       
        
    except Exception as e:
        print("Error extracting all programs: ")
    
    # ---------- ALL COURSES DATA ----------
    try:
        print("\nExtracting 'All Courses' data...")
        
        # Find all course tuples
        course_tuples = driver.find_elements(By.CSS_SELECTOR, ".acp_course_tuple .d15c8a.fb6321.a25c93")
        
        for course_tuple in course_tuples:
            try:
                course_data = {}
                
                # Extract course name
                try:
                    course_name_elem = course_tuple.find_element(By.CSS_SELECTOR, ".c42a97 .f443c7")
                    course_data["course_name"] = course_name_elem.text.strip()
                except:
                    course_data["course_name"] = "N/A"
                
                # Extract course details
                try:
                    details_elem = course_tuple.find_element(By.CSS_SELECTOR, ".ae8f7e")
                    details_text = details_elem.text.strip()
                    
                    # Parse rating
                    rating_match = re.search(r'(\d+\.\d+)', details_text)
                    if rating_match:
                        course_data["rating"] = float(rating_match.group(1))
                    
                    # Parse duration
                    duration_match = re.search(r'(\d+\s*(?:days?|months?|years?|\s*-\s*\d+\s*(?:days?|months?|years?)))', details_text)
                    if duration_match:
                        course_data["duration"] = duration_match.group(1).strip()
                    
                    # Parse ranking
                    ranking_match = re.search(r'#(\d+)\s+(\w+)', details_text)
                    if ranking_match:
                        course_data["ranking"] = {
                            "rank": ranking_match.group(1),
                            "source": ranking_match.group(2)
                        }
                    
                    # Check for degree type
                    if "Diploma" in details_text:
                        course_data["degree_type"] = "Diploma"
                    elif "Certificate" in details_text:
                        course_data["degree_type"] = "Certificate"
                    elif "Degree" in details_text:
                        course_data["degree_type"] = "Degree"
                        
                except Exception as e:
                    print("Error extracting course details:")
                
                # Extract seats offered
                try:
                    seats_elem = course_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(1) .c8c9ee")
                    seats_text = seats_elem.text.strip()
                    if seats_text and seats_text != "– / –":
                        # Try to parse as number
                        try:
                            course_data["seats_offered"] = int(seats_text)
                        except:
                            course_data["seats_offered"] = seats_text
                    else:
                        course_data["seats_offered"] = "Not specified"
                except:
                    course_data["seats_offered"] = "Not specified"
                
                # Extract exams accepted
                try:
                    exams_elem = course_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(2) .c8c9ee")
                    exams_text = exams_elem.text.strip()
                    if exams_text and exams_text != "– / –":
                        # Check if there's a list of exams
                        exam_links = exams_elem.find_elements(By.TAG_NAME, "a")
                        if exam_links:
                            course_data["exams_accepted"] = [link.text.strip() for link in exam_links if link.text.strip()]
                        else:
                            course_data["exams_accepted"] = exams_text
                    else:
                        course_data["exams_accepted"] = "Not specified"
                except:
                    course_data["exams_accepted"] = "Not specified"
                
                # Extract median salary
                try:
                    salary_elem = course_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(3) .c8c9ee")
                    salary_text = salary_elem.text.strip()
                    if salary_text and salary_text != "– / –":
                        course_data["median_salary"] = salary_text
                    else:
                        course_data["median_salary"] = "Not available"
                except:
                    course_data["median_salary"] = "Not available"
                
                # Extract total tuition fees
                try:
                    fees_elem = course_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(4) .c8c9ee")
                    fees_text = fees_elem.text.strip()
                    # Clean fees text
                    if fees_text and fees_text != "– / –":
                        fees_clean = re.sub(r'Get Fee Details.*', '', fees_text).strip()
                        course_data["total_tuition_fees"] = fees_clean
                    else:
                        course_data["total_tuition_fees"] = "Not available"
                except:
                    course_data["total_tuition_fees"] = "Not available"
                
                # For online/blended courses, check for different structure
                if "e8c4fd" in course_tuple.get_attribute("class"):
                    try:
                        # Try to extract total fees for online courses
                        total_fees_elem = course_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(1) .c8c9ee")
                        total_fees = total_fees_elem.text.strip()
                        if total_fees and total_fees != "– / –":
                            course_data["total_fees"] = total_fees
                    except:
                        pass
                    
                    try:
                        # Try to extract duration
                        duration_elem = course_tuple.find_element(By.CSS_SELECTOR, ".b93ff8:nth-child(2) .c8c9ee")
                        duration = duration_elem.text.strip()
                        if duration and duration != "– / –":
                            course_data["duration"] = duration
                    except:
                        pass
                    
                    try:
                        # Try to extract skills
                        skills_elem = course_tuple.find_elements(By.CSS_SELECTOR, ".d000d4 .a68029 a")
                        if skills_elem:
                            course_data["skills"] = [skill.text.strip() for skill in skills_elem if skill.text.strip()]
                    except:
                        pass
                
                # Extract course link
                try:
                    course_link_elem = course_tuple.find_element(By.CSS_SELECTOR, ".c42a97 a")
                    course_data["course_link"] = course_link_elem.get_attribute("href")
                except:
                    course_data["course_link"] = None
                
                all_courses_data.append(course_data)
                
            except Exception as e:
                print("Error processing course tuple:")
                continue
       
        
    except Exception as e:
        print("Error extracting all courses:")
    
    # Create final result structure
    result = {
        "all_programs": all_programs_data,
        "all_courses": all_courses_data
    }
    
    return result

def scrape_faqs_section(driver):

    faqs_data = []
    
 
    try:
        # Wait for FAQ section to load
        wait = WebDriverWait(driver, 15)
        
        # Wait for FAQ section to be present - try multiple selectors
        faq_section = None
        section_selectors = [
            (By.ID, "acp_section_fAQs"),
            (By.CSS_SELECTOR, "[data-section-id='fAQs']"),
            (By.CSS_SELECTOR, ".faq__according-wrapper"),
            (By.XPATH, "//*[contains(text(), 'FAQs')]")
        ]
        
        for selector_type, selector in section_selectors:
            try:
                faq_section = wait.until(
                    EC.presence_of_element_located((selector_type, selector))
                )
             
                break
            except:
                continue
        
        if not faq_section:
            return {"faq_section": None}
        
        # Extract section heading
        section_heading = ""
        try:
            heading_selectors = [
                ".ae88c4",
                "h2",
                "h3",
                ".section-heading",
                "[class*='heading']"
            ]
            for selector in heading_selectors:
                try:
                    heading_elem = faq_section.find_element(By.CSS_SELECTOR, selector)
                    if heading_elem.text.strip():
                        section_heading = heading_elem.text.strip()
                        break
                except:
                    continue
        except:
            pass
        

        # Extract introduction text
        intro_text = ""
        try:
            intro_selectors = [
                ".faq__according-wrapper p",
                "p",
                ".intro-text",
                "[class*='description']",
                "[class*='intro']"
            ]
            for selector in intro_selectors:
                try:
                    intro_elem = faq_section.find_element(By.CSS_SELECTOR, selector)
                    text = intro_elem.text.strip()
                    if text and len(text) > 10:  # Avoid short/irrelevant text
                        intro_text = text
                        break
                except:
                    continue
        except:
            pass
        
        
        time.sleep(3)  # Wait for JavaScript to load content
        
       
        js_faqs = driver.execute_script("""
            const faqs = [];
            
            // Find FAQ section - try multiple selectors
            let faqSection = document.querySelector('#acp_section_fAQs');
            if (!faqSection) {
                faqSection = document.querySelector('[data-section-id="fAQs"]');
            }
            if (!faqSection) {
                // Look for any element containing FAQs
                const elements = document.querySelectorAll('*');
                for (const elem of elements) {
                    if (elem.textContent.includes('FAQ') && 
                        elem.textContent.includes('Q:')) {
                        faqSection = elem;
                        break;
                    }
                }
            }
            
            if (!faqSection) {
                console.log('FAQ section not found');
                return faqs;
            }
            
            console.log('FAQ section found:', faqSection);
            
            // Find all question elements - multiple class patterns
            const questionSelectors = [
                '.html-0.ea1844.listener',
                '.ea1844',
                '.listener',
                '[class*="faq"] .question',
                '[class*="accordion"] .question',
                '[class*="accordion__item"]',
                '.flx-box'
            ];
            
            let questionElements = [];
            for (const selector of questionSelectors) {
                const elements = faqSection.querySelectorAll(selector);
                if (elements.length > 0) {
                    console.log(`Found ${elements.length} elements with selector: ${selector}`);
                    questionElements = Array.from(elements);
                    break;
                }
            }
            
            // If no elements found, try a broader search
            if (questionElements.length === 0) {
                console.log('No specific question elements found, trying broader search...');
                const allElements = faqSection.querySelectorAll('*');
                questionElements = Array.from(allElements).filter(el => {
                    const text = el.textContent.trim();
                    return text.startsWith('Q:') || 
                           text.startsWith('Q ') ||
                           (el.classList && 
                            (el.classList.contains('html-0') || 
                             el.classList.contains('listener')));
                });
            }
            
            console.log(`Found ${questionElements.length} question elements`);
            
            questionElements.forEach((qElem, index) => {
                try {
                    // Extract question
                    let question = '';
                    const fullText = qElem.textContent.trim();
                    
                    // Clean question extraction
                    if (fullText.startsWith('Q:')) {
                        question = fullText.substring(2).trim();
                    } else if (fullText.startsWith('Q ')) {
                        question = fullText.substring(1).trim();
                    } else {
                        // Try to find question in spans
                        const questionSpans = qElem.querySelectorAll('span');
                        if (questionSpans.length > 0) {
                            // Get the last span (usually contains the question)
                            const lastSpan = questionSpans[questionSpans.length - 1];
                            question = lastSpan.textContent.trim();
                        } else {
                            question = fullText;
                        }
                    }
                    
                    // Clean question text
                    question = question.replace(/\\s*\\n\\s*/g, ' ').replace(/\\s+/g, ' ').trim();
                    
                    if (!question || question.length < 5) {
                        console.log(`Skipping FAQ ${index} - no valid question`);
                        return;
                    }
                    
                    console.log(`Processing FAQ ${index + 1}: ${question.substring(0, 50)}...`);
                    
                    // Find corresponding answer
                    let answer = '';
                    let tables = [];
                    let images = [];
                    let lists = [];
                    
                    // Look for answer - expand the search
                    let currentElement = qElem;
                    let attempts = 0;
                    const maxAttempts = 5;
                    
                    while (currentElement && attempts < maxAttempts) {
                        attempts++;
                        currentElement = currentElement.nextElementSibling;
                        
                        if (!currentElement) break;
                        
                        // Check if this element could contain an answer
                        const elementClass = currentElement.className || '';
                        const elementId = currentElement.id || '';
                        
                        // Multiple indicators of answer content
                        const isAnswerElement = 
                            elementClass.includes('f61835') ||
                            elementClass.includes('answer') ||
                            elementClass.includes('accordion__content') ||
                            elementClass.includes('faq-answer') ||
                            elementClass.includes('wiki') ||
                            elementId.includes('answer');
                        
                        if (isAnswerElement) {
                            // Look for answer content
                            const contentSelectors = [
                                '.wikkiContents',
                                '.answer-content',
                                '.faq-answer',
                                'p',
                                'div'
                            ];
                            
                            for (const selector of contentSelectors) {
                                const contentElement = currentElement.querySelector(selector);
                                if (contentElement && contentElement.textContent.trim()) {
                                    // Clone to avoid modifying original
                                    const answerClone = contentElement.cloneNode(true);
                                    
                                    // Clean the clone
                                    const unwantedSelectors = [
                                        '.a4bbdd', '.cf05b5', '.eee715',
                                        '.ask-gpt', '.feedback',
                                        '.advertisement', '.ads'
                                    ];
                                    
                                    unwantedSelectors.forEach(unwanted => {
                                        const elements = answerClone.querySelectorAll(unwanted);
                                        elements.forEach(el => el.remove());
                                    });
                                    
                                    // Get cleaned text
                                    answer = answerClone.textContent.trim();
                                    
                                    // Clean answer text
                                    answer = answer.replace(/^A:?\\s*/i, '');
                                    answer = answer.replace(/^Ans:?\\s*/i, '');
                                    answer = answer.replace(/Not satisfied with answer.*/gi, '');
                                    answer = answer.replace(/Ask Shiksha GPT.*/gi, '');
                                    answer = answer.replace(/\\s*\\n\\s*/g, ' ');
                                    answer = answer.replace(/\\s+/g, ' ').trim();
                                    
                                    // Extract tables if present
                                    const tableElements = contentElement.querySelectorAll('table');
                                    tableElements.forEach(table => {
                                        try {
                                            const tableData = {
                                                headers: [],
                                                rows: []
                                            };
                                            
                                            // Extract headers
                                            const thElements = table.querySelectorAll('th');
                                            if (thElements.length > 0) {
                                                thElements.forEach(th => {
                                                    tableData.headers.push(th.textContent.trim());
                                                });
                                            }
                                            
                                            // Extract rows
                                            const trElements = table.querySelectorAll('tr');
                                            trElements.forEach(tr => {
                                                // Skip header rows already captured
                                                if (tr.querySelector('th')) return;
                                                
                                                const rowData = [];
                                                const tdElements = tr.querySelectorAll('td');
                                                tdElements.forEach(td => {
                                                    rowData.push(td.textContent.trim());
                                                });
                                                
                                                if (rowData.length > 0) {
                                                    tableData.rows.push(rowData);
                                                }
                                            });
                                            
                                            if (tableData.headers.length > 0 || tableData.rows.length > 0) {
                                                tables.push(tableData);
                                            }
                                        } catch (e) {
                                            console.log('Error extracting table:', e);
                                        }
                                    });
                                    
                                    // Extract images
                                    const imgElements = contentElement.querySelectorAll('img');
                                    imgElements.forEach(img => {
                                        if (img.src) {
                                            images.push({
                                                src: img.src,
                                                alt: img.alt || '',
                                                width: img.width || 0,
                                                height: img.height || 0
                                            });
                                        }
                                    });
                                    
                                    // Extract lists
                                    const listElements = contentElement.querySelectorAll('ul, ol');
                                    listElements.forEach(list => {
                                        const listItems = [];
                                        const items = list.querySelectorAll('li');
                                        items.forEach(item => {
                                            listItems.push(item.textContent.trim());
                                        });
                                        if (listItems.length > 0) {
                                            lists.push(listItems);
                                        }
                                    });
                                    
                                    break;
                                }
                            }
                            
                            if (answer) break;
                        }
                    }
                    
                    if (answer) {
                        faqs.push({
                            faq_number: index + 1,
                            question: question,
                            answer: {
                                text: answer.substring(0, 3000),
                                has_table: tables.length > 0,
                                has_image: images.length > 0,
                                has_list: lists.length > 0
                            },
                            tables: tables.length > 0 ? tables : undefined,
                            images: images.length > 0 ? images : undefined,
                            lists: lists.length > 0 ? lists : undefined
                        });
                        console.log(`✓ Added FAQ ${index + 1}`);
                    } else {
                        console.log(`✗ No answer found for FAQ ${index + 1}`);
                    }
                } catch (e) {
                    console.log(`Error processing FAQ ${index}:`, e);
                }
            });
            
            console.log(`Total FAQs extracted: ${faqs.length}`);
            return faqs;
        """)
        
        if js_faqs and len(js_faqs) > 0:
            faqs_data = js_faqs
           
        else:
         
            
            # Alternative: Try to find FAQ items using various patterns
            try:
                print("Looking for FAQ patterns...")
                
                # Try to find any text containing Q: pattern
                page_text = driver.page_source
                import re
                
                # Look for Q: pattern in the page
                q_patterns = [
                    r'Q:\s*([^<]+?)<',
                    r'<[^>]*>Q[:\s]+([^<]+?)<',
                    r'question[^>]*>([^<]+?)<',
                    r'<div[^>]*class="[^"]*(?:question|faq)[^"]*"[^>]*>([^<]+?)<'
                ]
                
                all_questions = []
                for pattern in q_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        all_questions.extend(matches)
                
                if all_questions:
                    print(f"Found {len(all_questions)} potential questions via regex")
                    
                    for i, question in enumerate(set(all_questions[:10]), 1):  # Limit to 10 unique
                        if len(question.strip()) > 10:  # Valid question
                            faqs_data.append({
                                "faq_number": i,
                                "question": question.strip()[:500],
                                "answer": {
                                    "text": "Answer not found (dynamic content)",
                                    "has_table": False,
                                    "has_image": False,
                                    "has_list": False
                                }
                            })
                
            except Exception as e:
                print("Manual extraction failed:")
        
    except Exception as e:
        print("Error extracting FAQ section: ")
        import traceback
        traceback.print_exc()
    
    # Create final result structure
    result = {
        "faq_section": {
            "heading": section_heading or "FAQs",
            "introduction": intro_text,
            "total_faqs": len(faqs_data),
            "faqs": faqs_data
        }
    }
    
    return result
# ---------------- FEES ----------------
def scrape_fees(driver, URLS):
    try:
        driver.get(URLS["fees"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["fees"])
    
    wait = WebDriverWait(driver, 20)
    
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    
    fees_data = []
    course_details = []
    faqs_data = []
    overview_description = ""

    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")

        except:
            pass
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
            
        except:
           pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            pass
        
        # Rest of your existing header extraction code...
        
    except Exception as e:
        print("⚠️ Error in college header section:")
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Try to find college name from various selectors
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for h1 in h1_elements:
                if h1.text and ("Fees" in h1.text or "IIM" in h1.text):
                    college_info["college_name"] = h1.text.replace(" Fees", "").replace(" - Indian Institute of Management", "").strip()
                    break
        except:
            pass

        # Extract from the provided HTML structure
        try:
            header_section = driver.find_element(By.CSS_SELECTOR, ".a655da.aadf9d")
            
            # College name
            try:
                name_elem = header_section.find_element(By.CSS_SELECTOR, "h1.cc5e8d")
                college_info["college_name"] = name_elem.text.strip()
            except:
                pass
            
            # Location
            try:
                location_div = header_section.find_element(By.CSS_SELECTOR, ".de89cf")
                location_text = location_div.text.strip()
                if "," in location_text:
                    parts = [p.strip() for p in location_text.split(",", 1)]
                    college_info["location"] = parts[0].replace(",", "").strip()
                    college_info["city"] = parts[1] if len(parts) > 1 else ""
            except:
                pass
            
            # Rating and reviews
            try:
                rating_div = header_section.find_element(By.CSS_SELECTOR, ".e6f71f")
                rating_text = rating_div.text.strip()
                rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
                if rating_match:
                    college_info["rating"] = rating_match.group(1)
                
                reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
                if reviews_match:
                    college_info["reviews_count"] = int(reviews_match.group(1))
            except:
                pass
            
            # Q&A count
            try:
                qa_link = header_section.find_element(By.XPATH, ".//a[contains(text(), 'Student Q&A')]")
                qa_text = qa_link.text.strip()
                qa_match = re.search(r"(\d+(?:\.\d+)?)\s*(k|K)?", qa_text)
                if qa_match:
                    count = float(qa_match.group(1))
                    if qa_match.group(2):
                        count = int(count * 1000)
                    college_info["qa_count"] = int(count)
            except:
                pass
            
            # Institute type and established year
            try:
                list_items = header_section.find_elements(By.CSS_SELECTOR, ".ff9e36 li")
                for li in list_items:
                    text = li.text.strip().lower()
                    if "institute" in text:
                        college_info["institute_type"] = li.text.strip()
                    elif "estd" in text:
                        year_match = re.search(r"\b(\d{4})\b", li.text)
                        if year_match:
                            college_info["established_year"] = year_match.group(1)
            except:
                pass
                
        except Exception as e:
            print("⚠️ Error extracting header info:")

    except Exception as e:
        print("⚠️ Error in college header section:")

    # ---------- FEES OVERVIEW TABLE ----------

    
    try:
        # Look for fees overview table
        fees_section = wait.until(
            EC.presence_of_element_located((By.ID, "fees_section_overview"))
        )
        
        # Extract overview table
        try:
            table = fees_section.find_element(By.CSS_SELECTOR, "table.table")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            for row in rows:
                try:
                    # Extract course name
                    course_elem = row.find_element(By.CSS_SELECTOR, "td:first-child a")
                    course_name = course_elem.text.strip()
                    
                    # Extract fees
                    fees_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                    fees_text = fees_elem.text.strip().replace("Get Fee Details", "").strip()
                    
                    # Clean up course name
                    if "Courses" in course_name:
                        course_name = course_name.split("(")[0].strip()
                    
                    fees_data.append({
                        "course": course_name,
                        "total_tuition_fees": fees_text
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print("⚠️ Error extracting overview table: ")

        try:
            overview_desc = fees_section.find_element(By.CSS_SELECTOR, ".wikiContents .faq__according-wrapper p")
            overview_description = clean_text(overview_desc.text)
           
        except Exception as e:
            print("⚠️ Could not extract overview description: ")
            # Fallback: Try with BeautifulSoup
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                fees_section_soup = soup.find('section', {'id': 'fees_section_overview'})
                if fees_section_soup:
                    overview_div = fees_section_soup.find('div', {'class': 'wikiContents'})
                    if overview_div:
                        overview_para = overview_div.find('p')
                        if overview_para:
                            overview_description = clean_text(overview_para.text)
                            print(f"\nOverview (fallback): {overview_description[:200]}...")
            except:
                pass
    except Exception as e:
        print("⚠️ Fees overview section not found:")

    # ---------- DETAILED COURSE FEES ----------

    
    try:
        # Find all course fee sections
        course_sections = driver.find_elements(By.CSS_SELECTOR, "[id^='fees_section_about_baseCourse_']")
        
        print(f"Found {len(course_sections)} detailed course sections")
        
        for section in course_sections:
            try:
                # Extract course name
                course_name = ""
                try:
                    course_name_elem = section.find_element(By.CSS_SELECTOR, ".ae88c4")
                    course_name = course_name_elem.text.strip()
                except:
                    pass
                
                if not course_name:
                    continue
                
                # Extract course description
                course_desc = ""
                try:
                    desc_elem = section.find_element(By.CSS_SELECTOR, ".wikiContents .faq__according-wrapper p")
                    course_desc = desc_elem.text.strip()[:300]
                except:
                    pass
                
                # Extract fee components table
                fee_components = []
                try:
                    fee_table = section.find_element(By.CSS_SELECTOR, "table.table.f866a4")
                    rows = fee_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    
                    for row in rows:
                        try:
                            component_elem = row.find_element(By.CSS_SELECTOR, "td:first-child")
                            amount_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                            
                            component = component_elem.text.strip()
                            amount = amount_elem.text.strip()
                            
                            # Extract detailed description if available
                            component_desc = ""
                            try:
                                desc_div = component_elem.find_element(By.CSS_SELECTOR, ".c3bd41")
                                component_desc = desc_div.text.strip()
                            except:
                                pass
                            
                            fee_components.append({
                                "component": component,
                                "amount": amount,
                                "description": component_desc
                            })
                            
                        except:
                            continue
                except:
                    pass
                
                # Extract comparison data if available
                comparison_data = []
                try:
                    comparison_section = section.find_element(By.ID, "fees_section_fees_comparison")
                    comp_table = comparison_section.find_element(By.CSS_SELECTOR, "table.table.f6a6c1")
                    comp_rows = comp_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    
                    for row in comp_rows[:3]:  # Limit to top 3
                        try:
                            college_elem = row.find_element(By.CSS_SELECTOR, "td:first-child a")
                            tuition_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                            hostel_elem = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)")
                            
                            comparison_data.append({
                                "college": college_elem.text.strip(),
                                "tuition_fees": tuition_elem.text.strip(),
                                "hostel_fees": hostel_elem.text.strip()
                            })
                        except:
                            continue
                except:
                    pass
                
                # Extract course-specific FAQs
                course_faqs = []
                try:
                    faq_section = section.find_element(By.CSS_SELECTOR, ".a5ea4c.sectional-faqs")
                    faq_items = faq_section.find_elements(By.CSS_SELECTOR, ".html-0.ea1844.listener")
                    
                    for i, faq_item in enumerate(faq_items[:5], 1):  # Limit to 5
                        try:
                            question = ""
                            answer = ""
                            
                            # Extract question
                            try:
                                question_spans = faq_item.find_elements(By.CSS_SELECTOR, ".flx-box span")
                                if len(question_spans) >= 3:
                                    question = question_spans[2].text.strip()
                                else:
                                    question = faq_item.text.replace("Q:", "").strip()
                            except:
                                question = faq_item.text.strip()
                            
                            # Try to find answer
                            try:
                                # Find next sibling with answer class
                                answer_div = driver.execute_script("""
                                    var elem = arguments[0];
                                    var next = elem.nextElementSibling;
                                    while (next) {
                                        if (next.classList && next.classList.contains('f61835')) {
                                            var answerContent = next.querySelector('.wikkiContents');
                                            if (answerContent) {
                                                return answerContent.textContent.trim();
                                            }
                                        }
                                        next = next.nextElementSibling;
                                    }
                                    return '';
                                """, faq_item)
                                
                                if answer_div:
                                    answer = answer_div.replace("A:", "").strip()
                                    answer = re.sub(r'Not satisfied with answer.*', '', answer, flags=re.IGNORECASE)
                                    answer = re.sub(r'Ask Shiksha GPT.*', '', answer, flags=re.IGNORECASE)
                                    answer = re.sub(r'\s+', ' ', answer).strip()
                            except:
                                pass
                            
                            if question and answer:
                                course_faqs.append({
                                    "faq_number": i,
                                    "question": question,
                                    "answer": answer[:500]
                                })
                                
                        except:
                            continue
                except:
                    pass
                
                # Add to course details
                course_details.append({
                    "course_name": course_name,
                    "course_description": course_desc,
                    "fee_components": fee_components,
                    "comparison_colleges": comparison_data,
                    "course_faqs": course_faqs
                })
                
            
                
            except Exception as e:
                print("  ⚠️ Error processing course section:")
                continue
        
    except Exception as e:
        print("⚠️ Error extracting detailed course fees:")


    
    try:
        # Look for FAQ section in fees overview
        faq_container = driver.find_element(By.CSS_SELECTOR, ".a5ea4c.sectional-faqs")
        faq_items = faq_container.find_elements(By.CSS_SELECTOR, ".html-0.ea1844.listener")
        
        print("Found {len(faq_items)} FAQ items in overview")
        
        for i, faq_item in enumerate(faq_items, 1):
            try:
                question = ""
                answer = ""
                
                # Extract question
                try:
                    question_spans = faq_item.find_elements(By.CSS_SELECTOR, ".flx-box span")
                    if len(question_spans) >= 3:
                        question = question_spans[2].text.strip()
                    else:
                        question = faq_item.text.replace("Q:", "").strip()
                except:
                    question = faq_item.text.strip()
                
                # Extract answer using JavaScript
                try:
                    answer_div = driver.execute_script("""
                        var elem = arguments[0];
                        var next = elem.nextElementSibling;
                        while (next) {
                            if (next.classList && next.classList.contains('f61835')) {
                                var answerContent = next.querySelector('.wikkiContents');
                                if (answerContent) {
                                    // Clone and clean the content
                                    var clone = answerContent.cloneNode(true);
                                    var unwanted = clone.querySelectorAll('.a4bbdd, .cf05b5, .eee715');
                                    unwanted.forEach(function(el) {
                                        el.remove();
                                    });
                                    return clone.textContent.trim();
                                }
                            }
                            next = next.nextElementSibling;
                        }
                        return '';
                    """, faq_item)
                    
                    if answer_div:
                        answer = answer_div.replace("A:", "").strip()
                        answer = re.sub(r'Not satisfied with answer.*', '', answer, flags=re.IGNORECASE)
                        answer = re.sub(r'Ask Shiksha GPT.*', '', answer, flags=re.IGNORECASE)
                        answer = re.sub(r'\s+', ' ', answer).strip()
                except:
                    pass
                
                if question and answer:
                    # Check if answer has tables
                    has_table = "table" in answer_div.lower() if answer_div else False
                    
                    faqs_data.append({
                        "faq_number": i,
                        "question": question,
                        "answer": answer[:1000],
                        "has_table": has_table,
                        "section": "Fees Overview"
                    })
                    
                  
                    
            except Exception as e:
              
                continue
                
    except Exception as e:
        print("⚠️ FAQ section not found: ")

    # ---------- FINAL RESULT ----------
    result = {
        "college_info": college_info,
        "fees_overview": {
            "description":overview_description,
            "summary_table": fees_data,
            "total_courses": len(fees_data)
            
        },
        "course_details": course_details,
        "faqs": {
            "overview_faqs": faqs_data,
            "total_faqs": len(faqs_data) + sum(len(course.get("course_faqs", [])) for course in course_details)
        }
    }

    return result

def scrape_review_summary(driver, URLS):
    try:
        driver.get(URLS["reviews"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["reviews"])
    wait = WebDriverWait(driver, 20)
    
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
        "review_summary": {},  # Added for review summary data
        "review_videos": [],   # Added for review videos
        "individual_reviews": []  # Added for individual reviews
    }
    


    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")
        except:
           pass
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
    
        except:
            pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            print("⚠️ Videos/Photos count not found")
        
        # Rest of your existing header extraction code...
        
    except Exception as e:
        print("⚠️ Error in college header section:")
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Try to find college name from various selectors
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for h1 in h1_elements:
                if h1.text and ("Fees" in h1.text or "IIM" in h1.text):
                    college_info["college_name"] = h1.text.replace(" Fees", "").replace(" - Indian Institute of Management", "").strip()
                    break
        except:
            pass

        # Extract from the provided HTML structure
        try:
            header_section = driver.find_element(By.CSS_SELECTOR, ".a655da.aadf9d")
            
            # College name
            try:
                name_elem = header_section.find_element(By.CSS_SELECTOR, "h1.cc5e8d")
                college_info["college_name"] = name_elem.text.strip()
            except:
                pass
            
            # Location
            try:
                location_div = header_section.find_element(By.CSS_SELECTOR, ".de89cf")
                location_text = location_div.text.strip()
                if "," in location_text:
                    parts = [p.strip() for p in location_text.split(",", 1)]
                    college_info["location"] = parts[0].replace(",", "").strip()
                    college_info["city"] = parts[1] if len(parts) > 1 else ""
            except:
                pass
            
            # Rating and reviews
            try:
                rating_div = header_section.find_element(By.CSS_SELECTOR, ".e6f71f")
                rating_text = rating_div.text.strip()
                rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
                if rating_match:
                    college_info["rating"] = rating_match.group(1)
                
                reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
                if reviews_match:
                    college_info["reviews_count"] = int(reviews_match.group(1))
            except:
                pass
            
            # Q&A count
            try:
                qa_link = header_section.find_element(By.XPATH, ".//a[contains(text(), 'Student Q&A')]")
                qa_text = qa_link.text.strip()
                qa_match = re.search(r"(\d+(?:\.\d+)?)\s*(k|K)?", qa_text)
                if qa_match:
                    count = float(qa_match.group(1))
                    if qa_match.group(2):
                        count = int(count * 1000)
                    college_info["qa_count"] = int(count)
            except:
                pass
            
            # Institute type and established year
            try:
                list_items = header_section.find_elements(By.CSS_SELECTOR, ".ff9e36 li")
                for li in list_items:
                    text = li.text.strip().lower()
                    if "institute" in text:
                        college_info["institute_type"] = li.text.strip()
                    elif "estd" in text:
                        year_match = re.search(r"\b(\d{4})\b", li.text)
                        if year_match:
                            college_info["established_year"] = year_match.group(1)
            except:
                pass
                
        except Exception as e:
            print("⚠️ Error extracting header info:")

    except Exception as e:
        print("⚠️ Error in college header section:")
    
    # ---------- REVIEW SUMMARY SECTION ----------
    try:
      
        review_summary_section = driver.find_element(By.ID, "review_section_ratings_summary")
        
        # Extract overall rating
        try:
            rating_element = review_summary_section.find_element(By.CSS_SELECTOR, ".fd70d3")
            rating_text = rating_element.text.strip()
            rating_match = re.search(r'(\d+\.\d+)', rating_text)
            if rating_match:
                college_info["review_summary"]["overall_rating"] = rating_match.group(1)

        except Exception as e:
            print("⚠️ Overall rating not found in review summary:")
        
        # Extract verified reviews count
        try:
            verified_element = review_summary_section.find_element(By.CSS_SELECTOR, ".f62eee")
            verified_text = verified_element.text.strip()
            verified_match = re.search(r'(\d+)\s*Verified Reviews', verified_text)
            if verified_match:
                college_info["review_summary"]["verified_reviews_count"] = int(verified_match.group(1))

        except Exception as e:
            print("⚠️ Verified reviews count not found:")
        
        # Extract rating distribution
        try:
            rating_distribution = []
            rating_items = review_summary_section.find_elements(By.CSS_SELECTOR, ".a728a1 li")
            
            for item in rating_items:
                rating_range = item.find_element(By.CSS_SELECTOR, ".f81c43").text.strip()
                rating_count = item.find_element(By.CSS_SELECTOR, ".f65eaf").text.strip()
                
                # Extract percentage from style attribute
                percentage_element = item.find_element(By.CSS_SELECTOR, ".b5c9f3")
                style_attr = percentage_element.get_attribute("style")
                percentage_match = re.search(r'width:\s*(\d+)%', style_attr)
                percentage = percentage_match.group(1) + "%" if percentage_match else "0%"
                
                rating_distribution.append({
                    "range": rating_range,
                    "count": rating_count,
                    "percentage": percentage
                })
            
            college_info["review_summary"]["rating_distribution"] = rating_distribution
            
        except Exception as e:
            print("⚠️ Rating distribution not found:")
        
        # Extract category ratings
        try:
            category_ratings = []
            category_cards = review_summary_section.find_elements(By.CSS_SELECTOR, ".paper-card.boxShadow.d32700")
            
            for card in category_cards:
                category_name = card.find_element(By.CSS_SELECTOR, ".d7f853").text.strip()
                category_rating = card.find_element(By.CSS_SELECTOR, ".bfc017 span").text.strip()
                
                category_ratings.append({
                    "category": category_name,
                    "rating": category_rating
                })
            
            college_info["review_summary"]["category_ratings"] = category_ratings
      
        except Exception as e:
            print("⚠️ Category ratings not found:")
            
    except Exception as e:
        print("⚠️ Error scraping review summary section:")
    
    # ---------- REVIEW VIDEOS SECTION ----------
    try:
        
        # Find review videos section
        review_videos_section = driver.find_element(By.ID, "review_section_mini_clips")
        
        # Extract video title
        try:
            video_title = review_videos_section.find_element(By.CSS_SELECTOR, ".e2ac30").text.strip()
            
        except Exception as e:
            print("⚠️ Video section title not found:")
        
        # Extract video items
        try:
            video_items = review_videos_section.find_elements(By.CSS_SELECTOR, ".d87173.thumbnailListener")
            print(f"✓ Found {len(video_items)} video items")
            
            for video_item in video_items:
                video_data = {}
                
                # Extract video metadata
                try:
                    video_data["keyname"] = video_item.get_attribute("data-corouselkeyname")
                    video_data["keyid"] = video_item.get_attribute("data-corouselkeyid")
                    video_data["index"] = video_item.get_attribute("data-index")
                except:
                    pass
                
                # Extract YouTube video ID
                try:
                    iframe = video_item.find_element(By.TAG_NAME, "iframe")
                    src = iframe.get_attribute("src")
                    youtube_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', src)
                    if youtube_match:
                        video_data["youtube_id"] = youtube_match.group(1)
                        video_data["type"] = "embedded_video"
                    else:
                        # Check for thumbnail image
                        img = video_item.find_element(By.TAG_NAME, "img")
                        src = img.get_attribute("src")
                        youtube_match = re.search(r'youtube\.com/vi/([a-zA-Z0-9_-]+)', src)
                        if youtube_match:
                            video_data["youtube_id"] = youtube_match.group(1)
                            video_data["type"] = "thumbnail"
                            video_data["thumbnail_url"] = src
                except:
                    pass
                
                # Extract video title/description
                try:
                    title_element = video_item.find_element(By.CSS_SELECTOR, ".ada2b9")
                    video_data["title"] = title_element.text.strip()
                except:
                    try:
                        # Alternative selector for title
                        alt_title = video_item.find_element(By.CSS_SELECTOR, ".e6852b")
                        video_data["title"] = alt_title.text.strip()
                    except:
                        pass
                
                if video_data:  # Only add if we have data
                    college_info["review_videos"].append(video_data)
                    
        except Exception as e:
            print("⚠️ Error extracting video items: ")
            
       
        
    except Exception as e:
        print("⚠️ Error scraping review videos section:")
    
    # ---------- INDIVIDUAL REVIEWS ----------
    try:
 
        review_cards = driver.find_elements(By.CSS_SELECTOR, ".paper-card[id^='review_']")
        
        
        for review_card in review_cards[:5]:  # Limit to first 5 reviews for efficiency
            try:
                review_data = {}
                
                # Extract review ID
                review_id = review_card.get_attribute("id")
                if review_id:
                    review_data["review_id"] = review_id.replace("review_", "")
                
                # Extract user information
                try:
                    user_name = review_card.find_element(By.CSS_SELECTOR, ".f1b51a").text.strip()
                    review_data["user_name"] = user_name
                    
                    # Check if verified
                    verified_badge = review_card.find_element(By.CSS_SELECTOR, "img[alt='Verified Icon']")
                    review_data["verified"] = True if verified_badge else False
                except:
                    pass
                
                # Extract user course/batch
                try:
                    course_element = review_card.find_element(By.CSS_SELECTOR, ".b7f142")
                    course_text = course_element.text.strip()
                    review_data["course"] = course_text
                except:
                    pass
                
                # Extract overall rating
                try:
                    overall_rating = review_card.find_element(By.CSS_SELECTOR, ".f05026 span")
                    review_data["overall_rating"] = overall_rating.text.strip()
                except:
                    pass
                
                # Extract category ratings
                try:
                    category_spans = review_card.find_elements(By.CSS_SELECTOR, ".d757cc")
                    category_ratings = {}
                    
                    for span in category_spans:
                        text = span.text.strip()
                        # Extract rating and category name
                        parts = text.split()
                        if len(parts) >= 2:
                            rating = parts[0]
                            category = " ".join(parts[1:])
                            category_ratings[category] = rating
                    
                    review_data["category_ratings"] = category_ratings
                except:
                    pass
                
                # Extract review title
                try:
                    review_title = review_card.find_element(By.CSS_SELECTOR, ".d7e2f2").text.strip()
                    review_data["title"] = review_title
                except:
                    pass
                
                # Extract review content sections
                try:
                    content_divs = review_card.find_elements(By.CSS_SELECTOR, ".dca212 > div")
                    review_content = {}
                    
                    for div in content_divs:
                        text = div.text.strip()
                        if ":" in text:
                            parts = text.split(":", 1)
                            category = parts[0].replace("<strong>", "").replace("</strong>", "").strip()
                            content = parts[1].strip()
                            review_content[category] = content
                    
                    review_data["content"] = review_content
                except:
                    pass
                
                # Extract review date
                try:
                    date_element = review_card.find_element(By.CSS_SELECTOR, ".f3dfa4")
                    date_text = date_element.text.strip()
                    review_data["review_date"] = date_text.replace("Reviewed on", "").strip()
                except:
                    pass
                
                # Only add review if we have some data
                if review_data:
                    college_info["individual_reviews"].append(review_data)
                    
            except Exception as e:
                print("⚠️ Error processing individual review:")
 
    except Exception as e:
        print("⚠️ Error scraping individual reviews:")
    
    return college_info


def scrape_admission_overview(driver, URLS):
    try:
        driver.get(URLS["admission"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["admission"])
    
    wait = WebDriverWait(driver, 30)
    
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
        "admission_overview": {
            "title": "",
            "description": "",
            "key_points": [],
            "faqs": []
        },
        "eligibility_selection": {
            "title": "",
            "description": "",
            "courses_table": [],
            "faqs": []
        }
    }
    
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")
           
        except:
            pass
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
            
        except:
            pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            print("⚠️ Videos/Photos count not found")
        
        # Rest of your existing header extraction code...
        
    except Exception as e:
        print("⚠️ Error in college header section:")
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Try to find college name from various selectors
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for h1 in h1_elements:
                if h1.text and ("Fees" in h1.text or "IIM" in h1.text):
                    college_info["college_name"] = h1.text.replace(" Fees", "").replace(" - Indian Institute of Management", "").strip()
                    break
        except:
            pass

        # Extract from the provided HTML structure
        try:
            header_section = driver.find_element(By.CSS_SELECTOR, ".a655da.aadf9d")
            
            # College name
            try:
                name_elem = header_section.find_element(By.CSS_SELECTOR, "h1.cc5e8d")
                college_info["college_name"] = name_elem.text.strip()
            except:
                pass
            
            # Location
            try:
                location_div = header_section.find_element(By.CSS_SELECTOR, ".de89cf")
                location_text = location_div.text.strip()
                if "," in location_text:
                    parts = [p.strip() for p in location_text.split(",", 1)]
                    college_info["location"] = parts[0].replace(",", "").strip()
                    college_info["city"] = parts[1] if len(parts) > 1 else ""
            except:
                pass
            
            # Rating and reviews
            try:
                rating_div = header_section.find_element(By.CSS_SELECTOR, ".e6f71f")
                rating_text = rating_div.text.strip()
                rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
                if rating_match:
                    college_info["rating"] = rating_match.group(1)
                
                reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
                if reviews_match:
                    college_info["reviews_count"] = int(reviews_match.group(1))
            except:
                pass
            
            # Q&A count
            try:
                qa_link = header_section.find_element(By.XPATH, ".//a[contains(text(), 'Student Q&A')]")
                qa_text = qa_link.text.strip()
                qa_match = re.search(r"(\d+(?:\.\d+)?)\s*(k|K)?", qa_text)
                if qa_match:
                    count = float(qa_match.group(1))
                    if qa_match.group(2):
                        count = int(count * 1000)
                    college_info["qa_count"] = int(count)
            except:
                pass
            
            # Institute type and established year
            try:
                list_items = header_section.find_elements(By.CSS_SELECTOR, ".ff9e36 li")
                for li in list_items:
                    text = li.text.strip().lower()
                    if "institute" in text:
                        college_info["institute_type"] = li.text.strip()
                    elif "estd" in text:
                        year_match = re.search(r"\b(\d{4})\b", li.text)
                        if year_match:
                            college_info["established_year"] = year_match.group(1)
            except:
                pass
                
        except Exception as e:
            print("⚠️ Error extracting header info:")

    except Exception as e:
        print("⚠️ Error in college header section:")
    try:
       
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)
        
        
        for i in range(0, 2000, 300):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.5)
        
     
        
        try:
            overview_section = wait.until(
                EC.presence_of_element_located((By.ID, "admission_section_admission_overview"))
            )
            
            # Extract title
            try:
                title_div = overview_section.find_element(By.CSS_SELECTOR, ".ae88c4")
                college_info["admission_overview"]["title"] = title_div.text.strip()

            except:
                pass
            
            # Extract description
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#EdContent__admission_section_admission_overview")
                ))
                
                content_div = driver.find_element(By.CSS_SELECTOR, "#EdContent__admission_section_admission_overview")
                paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                
                description_text = ""
                for p in paragraphs:
                    try:
                        text = p.text.strip()
                        if text and len(text) > 20:
                            description_text += text + " "
                    except:
                        continue
                
                college_info["admission_overview"]["description"] = description_text.strip()

                
            except Exception as e:
                print("⚠️ Error extracting admission overview description:")
            
            # Extract FAQs from admission overview
            try:
               
                faq_items = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "#admission_section_admission_overview .html-0.ea1844.listener")
                    )
                )
                
                for faq_item in faq_items:
                    try:
                        # Extract question
                        question_elem = faq_item.find_element(By.CSS_SELECTOR, "strong.flx-box")
                        question_text = question_elem.text.strip()
                        
                        # Clean question
                        if "Q:" in question_text:
                            question_text = question_text.split("Q:", 1)[1].strip()
                        elif "Q." in question_text:
                            question_text = question_text.split("Q.", 1)[1].strip()
                        
                        # Get answer
                        answer_text = ""
                        try:
                            # Get next sibling using XPath
                            answer_container = faq_item.find_element(By.XPATH, "following-sibling::div[1]")
                            answer_div = answer_container.find_element(By.CSS_SELECTOR, ".facb5f")
                            answer_text = answer_div.text.strip()
                            
                            # Clean answer
                            if "A:" in answer_text:
                                answer_text = answer_text.split("A:", 1)[1].strip()
                            elif "A." in answer_text:
                                answer_text = answer_text.split("A.", 1)[1].strip()
                            
                            # Remove GPT reference
                            if "Not satisfied with answer?" in answer_text:
                                answer_text = answer_text.split("Not satisfied with answer?")[0].strip()
                                
                        except:
                            continue
                        
                        if question_text and answer_text:
                            college_info["admission_overview"]["faqs"].append({
                                "question": question_text,
                                "answer": answer_text[:500]
                            })
                            
                    except Exception as e:
                        
                        continue
                
         
            except Exception as e:
                print("⚠️ Error extracting admission overview FAQs:")
                
        except Exception as e:
            print("⚠️ Admission overview section not found:")
        
        try:
            # Scroll to eligibility section
            driver.execute_script("window.scrollTo(0, 2000);")
            time.sleep(2)
            
            eligibility_section = wait.until(
                EC.presence_of_element_located((By.ID, "admission_section_eligibility_selection"))
            )
            
            # Extract title
            try:
                title_div = eligibility_section.find_element(By.CSS_SELECTOR, ".ae88c4")
                college_info["eligibility_selection"]["title"] = title_div.text.strip()
             
            except:
                pass
            
            # Extract description
            try:
                content_div = driver.find_element(By.CSS_SELECTOR, "#EdContent__admission_section_eligibility_selection")
                
                # Get description
                try:
                    description_div = content_div.find_element(By.CSS_SELECTOR, ".photo-widget-full")
                    description_text = description_div.text.strip()
                    
                    if "The table below" in description_text:
                        description_text = description_text.split("The table below")[0].strip()
                    
                    college_info["eligibility_selection"]["description"] = description_text
                    
                except:
                    # Fallback
                    paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                    description_text = ""
                    for p in paragraphs[:2]:
                        text = p.text.strip()
                        if text:
                            description_text += text + " "
                    college_info["eligibility_selection"]["description"] = description_text.strip()
                
            except Exception as e:
                print("⚠️ Error extracting eligibility description:")
            
            # SIMPLIFIED TABLE EXTRACTION
            try:
                # Use JavaScript to extract table data
                table_script = """
                function extractCoursesTable() {
                    const allTables = document.querySelectorAll('#admission_section_eligibility_selection table');
                    const courses = [];
                    
                    for (const table of allTables) {
                        const rows = table.querySelectorAll('tr');
                        if (rows.length < 2) continue;
                        
                        // Check first row for headers
                        const firstRow = rows[0];
                        const headerCells = firstRow.querySelectorAll('th, td');
                        const headerText = Array.from(headerCells).map(cell => 
                            cell.textContent.toLowerCase().trim()
                        ).join(' ');
                        
                        // Check if this looks like a courses table
                        if (headerText.includes('course') && headerText.includes('eligibility') && 
                            (headerText.includes('selection') || headerText.includes('criteria'))) {
                            
                            console.log('Found courses table with', rows.length, 'rows');
                            
                            // Process data rows
                            for (let i = 1; i < rows.length; i++) {
                                const row = rows[i];
                                const cells = row.querySelectorAll('td');
                                
                                if (cells.length >= 3) {
                                    const courseCell = cells[0];
                                    const courseLink = courseCell.querySelector('a');
                                    const courseName = courseLink ? 
                                        courseLink.textContent.trim() : 
                                        courseCell.textContent.trim();
                                    
                                    const eligibility = cells[1].textContent.trim();
                                    const selection = cells[2].textContent.trim();
                                    
                                    // Clean the text
                                    const cleanCourse = courseName.replace(/\\s+/g, ' ').trim();
                                    const cleanEligibility = eligibility.replace(/\\s+/g, ' ').trim();
                                    const cleanSelection = selection.replace(/\\s+/g, ' ').trim();
                                    
                                    if (cleanCourse && cleanCourse.length > 2) {
                                        courses.push({
                                            course: cleanCourse,
                                            eligibility: cleanEligibility,
                                            selection_criteria: cleanSelection
                                        });
                                    }
                                }
                            }
                            break; // Stop after finding first valid table
                        }
                    }
                    return courses;
                }
                
                return extractCoursesTable();
                """
                
                courses_data = driver.execute_script(table_script)
                
                if courses_data and len(courses_data) > 0:
                    college_info["eligibility_selection"]["courses_table"] = courses_data
                    
                else:
               
                    try:
                        tables = eligibility_section.find_elements(By.TAG_NAME, "table")
                        print(f"Found {len(tables)} tables total")
                        
                        for table_idx, table in enumerate(tables):
                            try:
                                rows = table.find_elements(By.TAG_NAME, "tr")
                                if len(rows) > 1:
                                    # Check header
                                    header_cells = rows[0].find_elements(By.TAG_NAME, "th, td")
                                    if len(header_cells) >= 3:
                                        header_text = " ".join([cell.text.lower() for cell in header_cells])
                                        if "course" in header_text and "eligibility" in header_text:
                                            print(f"Table {table_idx + 1} looks like courses table")
                                            
                                            for i in range(1, len(rows)):
                                                try:
                                                    cells = rows[i].find_elements(By.TAG_NAME, "td")
                                                    if len(cells) >= 3:
                                                        course_name = cells[0].text.strip()
                                                        eligibility = cells[1].text.strip()
                                                        selection = cells[2].text.strip()
                                                        
                                                        if course_name:
                                                            college_info["eligibility_selection"]["courses_table"].append({
                                                                "course": course_name,
                                                                "eligibility": eligibility,
                                                                "selection_criteria": selection
                                                            })
                                                except:
                                                    continue
                                            break
                            except:
                                continue
                                
                    
                    except Exception as e:
                        print("Manual extraction failed: ")
                        
            except Exception as e:
                print("⚠️ Error extracting courses table: ")
            
      
            
            try:
                # Scroll to FAQ area
                driver.execute_script("window.scrollTo(0, 2500);")
                time.sleep(1)
                
                # Wait for FAQ section
                faq_section = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#admission_section_eligibility_selection .sectional-faqs")
                    )
                )
                
                # Get FAQ items
                faq_items = faq_section.find_elements(By.CSS_SELECTOR, ".html-0.ea1844")
                
                # SIMPLIFIED FAQ EXTRACTION WITHOUT JAVASCRIPT ERRORS
                for faq_item in faq_items:
                    try:
                        # Extract question
                        question_elem = faq_item.find_element(By.CSS_SELECTOR, "strong.flx-box")
                        question_text = question_elem.text.strip()
                        
                        # Clean question
                        question_text = re.sub(r'^Q[:.]\s*', '', question_text).strip()
                        
                        # Get answer using Python/Selenium only (no JavaScript)
                        answer_text = ""
                        try:
                            # Find next sibling div
                            answer_container = faq_item.find_element(By.XPATH, "following-sibling::div[1]")
                            
                            # Try to find answer text
                            try:
                                answer_elem = answer_container.find_element(By.CSS_SELECTOR, ".facb5f")
                                answer_text = answer_elem.text.strip()
                            except:
                                try:
                                    answer_elem = answer_container.find_element(By.CSS_SELECTOR, ".wikkiContents")
                                    answer_text = answer_elem.text.strip()
                                except:
                                    # Last resort: get all text
                                    answer_text = answer_container.text.strip()
                            
                            # Clean answer
                            answer_text = re.sub(r'^A[:.]\s*', '', answer_text).strip()
                            
                            # Remove GPT reference if present
                            if "Not satisfied with answer?" in answer_text:
                                answer_text = answer_text.split("Not satisfied with answer?")[0].strip()
                                
                        except Exception as e:
                           
                            continue
                        
                        if question_text and answer_text and len(question_text) > 10:
                            college_info["eligibility_selection"]["faqs"].append({
                                "question": question_text,
                                "answer": answer_text[:500]
                            })
                           
                    except Exception as e:
                        continue
                
                # If no FAQs found, try JavaScript approach (fixed)
                if len(college_info["eligibility_selection"]["faqs"]) == 0:
                  
                    try:
                        faq_js_script = """
                        var faqs = [];
                        var faqItems = document.querySelectorAll('#admission_section_eligibility_selection .html-0.ea1844');
                        
                        faqItems.forEach(function(item) {
                            try {
                                // Get question
                                var questionElem = item.querySelector('strong.flx-box');
                                if (!questionElem) return;
                                
                                var question = questionElem.textContent.trim();
                                question = question.replace(/^Q[:.]\\s*/, '').trim();
                                
                                // Get answer
                                var answer = '';
                                var nextSibling = item.nextElementSibling;
                                
                                if (nextSibling && nextSibling.classList.contains('f61835')) {
                                    var answerElem = nextSibling.querySelector('.facb5f') || nextSibling.querySelector('.wikkiContents');
                                    if (answerElem) {
                                        answer = answerElem.textContent.trim();
                                        answer = answer.replace(/^A[:.]\\s*/, '').trim();
                                        
                                        // Remove GPT reference
                                        if (answer.includes('Not satisfied with answer?')) {
                                            answer = answer.split('Not satisfied with answer?')[0].trim();
                                        }
                                    }
                                }
                                
                                if (question && answer && question.length > 10) {
                                    faqs.push({
                                        question: question,
                                        answer: answer
                                    });
                                }
                            } catch (e) {
                                console.error('Error processing FAQ:', e);
                            }
                        });
                        
                        return faqs;
                        """
                        
                        js_faqs = driver.execute_script(faq_js_script)
                        if js_faqs:
                            college_info["eligibility_selection"]["faqs"] = js_faqs
                         
                    except Exception as e:
                        print("JavaScript FAQ extraction failed: ")
                        
            except Exception as e:
                print("⚠️ Error extracting eligibility FAQs: ")
                
        except Exception as e:
            print("⚠️ Eligibility section not found: ")
        
    except Exception as e:
        print("⚠️ Main error in scraping: ")
        import traceback
        traceback.print_exc()

    try:
        # Wait for admission process section
        admission_process_section = wait.until(
            EC.presence_of_element_located((By.ID, "admission_section_admission_process"))
        )
        
        # Get the entire HTML of the section
        section_html = admission_process_section.get_attribute('outerHTML')
        
        # Use BeautifulSoup to parse and extract all text
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(section_html, 'html.parser')
        
        # Initialize admission process data structure
        admission_data = {
            "title": "",
            "full_content": {},
            "fees_table": [],
            "seats_table": [],
            "courses_data": [],
            "faqs": [],
            "videos": []
        }
        
        # 1. Extract Title
        title_elem = soup.find('div', class_='ae88c4')
        if title_elem:
            admission_data["title"] = title_elem.get_text(strip=True)
       
        # 2. Extract ALL Content - COMPLETE METHOD
        content_div = soup.find('div', id='EdContent__admission_section_admission_process')
        
        if content_div:
            # Initialize content structure
            admission_data["full_content"] = {
                "paragraphs": [],
                "headings": [],
                "lists": [],
                "tables": [],
                "key_points": []
            }
            
            # Extract all paragraphs
            paragraphs = content_div.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    admission_data["full_content"]["paragraphs"].append(text)
            
            # Extract all headings (h1-h6)
            headings = content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                text = heading.get_text(strip=True)
                if text:
                    admission_data["full_content"]["headings"].append({
                        "tag": heading.name,
                        "text": text
                    })
            
            # Extract all lists
            lists = content_div.find_all(['ul', 'ol'])
            for list_elem in lists:
                list_items = list_elem.find_all('li')
                if list_items:
                    items_text = [li.get_text(strip=True) for li in list_items if li.get_text(strip=True)]
                    admission_data["full_content"]["lists"].append(items_text)
            
            # Extract key points from story-responsive
            story_div = content_div.find('div', class_='story-responsive')
            if story_div:
                figures = story_div.find_all('div', class_='figure')
                for figure in figures:
                    text = figure.get_text(strip=True)
                    if text:
                        admission_data["full_content"]["key_points"].append(text)
        
        # 3. Extract Fees Table - SIMPLIFIED
        fees_table = soup.find('table', style=lambda x: x and '620px' in str(x))
        if fees_table:
            rows = fees_table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 3:
                    admission_data["fees_table"].append({
                        "course": cols[0].get_text(strip=True),
                        "tuition_fee": cols[1].get_text(strip=True),
                        "average_package": cols[2].get_text(strip=True)
                    })
       
        # 4. Extract Seats Table - SIMPLIFIED
        seats_table = soup.find('table', class_='table _1708 d00e d8b0')
        if seats_table:
            rows = seats_table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 2:
                    admission_data["seats_table"].append({
                        "course": cols[0].get_text(strip=True),
                        "seats": cols[1].get_text(strip=True)
                    })
                # 5. Extract ALL Courses Data - COMPLETE METHOD
        course_sections = soup.find_all('div', id=lambda x: x and 'admission_section_admission_process_bac_' in x)
        
        for course_section in course_sections:
            course_info = {}
            
            # Course name and basic info
            header_div = course_section.find('div', class_='b2aeb1')
            if header_div:
                # Course name
                name_div = header_div.find('div', class_='ca2baa')
                if name_div:
                    course_info["name"] = name_div.get_text(strip=True)
                
                # Course stats
                stats_div = header_div.find('div', class_='e32f97')
                if stats_div:
                    stats_text = stats_div.get_text(strip=True)
                    course_info["stats"] = stats_text
            
            # Extract seat intake and fees from e88036
            stats_container = course_section.find('div', class_='e88036')
            if stats_container:
                stats_items = stats_container.find_all('div', class_='b4aebe')
                for item in stats_items:
                    label = item.find('label', class_='a8edfb')
                    value = item.find('span', class_='ee1018')
                    if label and value:
                        label_text = label.get_text(strip=True).lower().replace(' ', '_')
                        course_info[label_text] = value.get_text(strip=True)
            
            # Extract eligibility criteria
            eligibility_section = course_section.find('h3', class_='fa6426')
            if eligibility_section:
                # Get eligibility text
                eligibility_span = eligibility_section.find('span', class_='ded1b4')
                if eligibility_span and "Eligibility" in eligibility_span.get_text():
                    # Find the UL after this h3
                    ul_element = eligibility_section.find_next('ul', class_='de5ef8')
                    if ul_element:
                        items = ul_element.find_all('li')
                        eligibility_items = []
                        for item in items:
                            item_text = item.get_text(strip=True)
                            if item_text:
                                eligibility_items.append(item_text)
                        course_info["eligibility"] = eligibility_items
            
            # Extract cut-off tables if present
            cutoff_section = course_section.find('div', class_='d38e84')
            if cutoff_section:
                cutoff_tables = cutoff_section.find_all('table')
                course_info["cutoff_tables"] = []
                for table in cutoff_tables:
                    table_data = []
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        table_data.append(row_data)
                    course_info["cutoff_tables"].append(table_data)
            
            # Extract course description from c7f019
            desc_div = course_section.find('div', class_='c7f019')
            if desc_div:
                wiki_div = desc_div.find('div', class_='wikiContents')
                if wiki_div:
                    # Get all paragraphs from description
                    desc_paragraphs = wiki_div.find_all('p')
                    description_text = []
                    for p in desc_paragraphs:
                        text = p.get_text(strip=True)
                        if text:
                            description_text.append(text)
                    course_info["description"] = " ".join(description_text)
            
            # Extract FAQs specific to this course
            faq_container = course_section.find('div', class_='ed0bed')
            if faq_container:
                faq_items = faq_container.find_all('div', class_='html-0')
                course_faqs = []
                for faq_item in faq_items:
                    question_elem = faq_item.find('strong', class_='flx-box')
                    if question_elem:
                        question_text = question_elem.get_text(strip=True)
                        # Clean question
                        question_text = re.sub(r'^Q[:.]\s*', '', question_text).strip()
                        
                        # Find answer
                        answer_text = ""
                        answer_div = faq_item.find_next('div', class_='f61835')
                        if answer_div:
                            answer_elem = answer_div.find('div', class_='facb5f')
                            if answer_elem:
                                answer_text = answer_elem.get_text(strip=True)
                                answer_text = re.sub(r'^A[:.]\s*', '', answer_text).strip()
                        
                        if question_text and answer_text:
                            course_faqs.append({
                                "question": question_text,
                                "answer": answer_text[:500]
                            })
                
                if course_faqs:
                    course_info["faqs"] = course_faqs
            
            if course_info:
                admission_data["courses_data"].append(course_info)
        
 
        # 6. Extract FAQs from the main FAQ section - COMPLETE METHOD
        faq_section = soup.find('div', id='sectional-faqs-0')
        if faq_section:
            faq_items = faq_section.find_all('div', class_='html-0')
            for faq_item in faq_items:
                try:
                    # Question
                    question_elem = faq_item.find('strong', class_='flx-box')
                    if question_elem:
                        question_text = question_elem.get_text(strip=True)
                        question_text = re.sub(r'^Q[:.]\s*', '', question_text).strip()
                        
                        # Answer
                        answer_text = ""
                        answer_container = faq_item.find_next('div', class_='f61835')
                        if answer_container:
                            answer_elem = answer_container.find('div', class_='facb5f')
                            if answer_elem:
                                answer_text = answer_elem.get_text(strip=True)
                                answer_text = re.sub(r'^A[:.]\s*', '', answer_text).strip()
                        
                        if question_text and answer_text:
                            admission_data["faqs"].append({
                                "question": question_text,
                                "answer": answer_text[:1000]  # Longer limit for complete answers
                            })
                except Exception as e:
                    continue
            
   
        # 7. Extract Videos
        video_widget = soup.find('div', id='reelsWidget')
        if video_widget:
            video_items = video_widget.find_all('li', class_='d87173')
            for video in video_items:
                try:
                    title_p = video.find('div', class_='ce64f8').find('p')
                    if title_p:
                        title = title_p.get_text(strip=True)
                        
                        # Duration
                        duration_p = title_p.find_next('p')
                        duration = duration_p.get_text(strip=True) if duration_p else ""
                        
                        admission_data["videos"].append({
                            "title": title,
                            "duration": duration
                        })
                except Exception as e:
                    continue
            
     
        # 8. Extract Additional Content - links, notes, etc.
        additional_content = {}
        
        # Extract all links
        links = content_div.find_all('a') if content_div else []
        additional_content["links"] = []
        for link in links[:10]:  # Limit to first 10 links
            link_text = link.get_text(strip=True)
            link_href = link.get('href', '')
            if link_text and link_href:
                additional_content["links"].append({
                    "text": link_text,
                    "url": link_href
                })
        
        # Extract notes and disclaimers
        notes = []
        if content_div:
            em_elements = content_div.find_all('em')
            for em in em_elements:
                text = em.get_text(strip=True)
                if text and ("Disclaimer" in text or "Note" in text):
                    notes.append(text)
        
        additional_content["notes"] = notes
        admission_data["additional_content"] = additional_content
        
        # Add to college_info
        college_info["admission_process"] = admission_data
        
   
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Add empty structure anyway
        college_info["admission_process"] = {
            "title": "",
            "full_content": {},
            "fees_table": [],
            "seats_table": [],
            "courses_data": [],
            "faqs": [],
            "videos": []
        }
    
    return college_info
    

def scrape_placement_report(driver,URLS):
    try:
        driver.get(URLS["placement"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["placement"])
    
    wait = WebDriverWait(driver, 15)
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
        "placement_data": {}
    }
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")
            
        except:
            pass
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
            
        except:
            pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            print("⚠️ Videos/Photos count not found")
        
        # Rest of your existing header extraction code...
        
    except Exception as e:
        print("⚠️ Error in college header section: ")
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Try to find college name from various selectors
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for h1 in h1_elements:
                if h1.text and ("Fees" in h1.text or "IIM" in h1.text):
                    college_info["college_name"] = h1.text.replace(" Fees", "").replace(" - Indian Institute of Management", "").strip()
                    break
        except:
            pass

        # Extract from the provided HTML structure
        try:
            header_section = driver.find_element(By.CSS_SELECTOR, ".a655da.aadf9d")
            
            # College name
            try:
                name_elem = header_section.find_element(By.CSS_SELECTOR, "h1.cc5e8d")
                college_info["college_name"] = name_elem.text.strip()
            except:
                pass
            
            # Location
            try:
                location_div = header_section.find_element(By.CSS_SELECTOR, ".de89cf")
                location_text = location_div.text.strip()
                if "," in location_text:
                    parts = [p.strip() for p in location_text.split(",", 1)]
                    college_info["location"] = parts[0].replace(",", "").strip()
                    college_info["city"] = parts[1] if len(parts) > 1 else ""
            except:
                pass
            
            # Rating and reviews
            try:
                rating_div = header_section.find_element(By.CSS_SELECTOR, ".e6f71f")
                rating_text = rating_div.text.strip()
                rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
                if rating_match:
                    college_info["rating"] = rating_match.group(1)
                
                reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
                if reviews_match:
                    college_info["reviews_count"] = int(reviews_match.group(1))
            except:
                pass
            
            # Q&A count
            try:
                qa_link = header_section.find_element(By.XPATH, ".//a[contains(text(), 'Student Q&A')]")
                qa_text = qa_link.text.strip()
                qa_match = re.search(r"(\d+(?:\.\d+)?)\s*(k|K)?", qa_text)
                if qa_match:
                    count = float(qa_match.group(1))
                    if qa_match.group(2):
                        count = int(count * 1000)
                    college_info["qa_count"] = int(count)
            except:
                pass
            
            # Institute type and established year
            try:
                list_items = header_section.find_elements(By.CSS_SELECTOR, ".ff9e36 li")
                for li in list_items:
                    text = li.text.strip().lower()
                    if "institute" in text:
                        college_info["institute_type"] = li.text.strip()
                    elif "estd" in text:
                        year_match = re.search(r"\b(\d{4})\b", li.text)
                        if year_match:
                            college_info["established_year"] = year_match.group(1)
            except:
                pass
                
        except Exception as e:
            print("⚠️ Error extracting header info: ")

    except Exception as e:
        print("⚠️ Error in college header section: ")
    try:
        # Wait for placement section to load
        wait.until(EC.presence_of_element_located((By.ID, "placement_section_overview")))
        
        # Scroll to placement section
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
      
        try:
            # Look for "Read more" or "Read less" button
            read_more_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Read more') or contains(text(), 'Read less')]")
            
            if read_more_buttons:
            
                # Click the first one that's visible
                for button in read_more_buttons:
                    try:
                        if button.is_displayed():
                          
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                            time.sleep(1)
                            
                            # Use JavaScript click to avoid interception
                            driver.execute_script("arguments[0].click();", button)
                           
                            time.sleep(3)  # Wait for content to expand
                            break
                    except:
                        continue
            else:
                pass
        except Exception as e:
            print("⚠️ Error clicking read more button: ")
        time.sleep(3)
        
        driver.execute_script("window.scrollBy(0, 200);")
        time.sleep(2)
        
        # Now get the COMPLETE updated HTML
        placement_section = driver.find_element(By.ID, "placement_section_overview")
        
        # Get the complete HTML with JavaScript execution
        section_html = driver.execute_script("""
            var section = arguments[0];
            
            // Force all content to render
            var allElements = section.querySelectorAll('*');
            allElements.forEach(function(el) {
                // Force style computation
                var style = window.getComputedStyle(el);
            });
            
            // Return complete HTML
            return section.outerHTML;
        """, placement_section)
        
    
        soup = BeautifulSoup(section_html, 'html.parser')
        
        # Initialize placement data structure
        placement_data = {
            "title": "",
            "paragraphs": [],  # Main paragraphs
            "tables": [],     # All tables (including those in FAQs)
            "faqs": [],       # FAQ questions and answers
            "rating": "",
            "rating_details": "",
            "links": [],
            "user_feedback": "",
            "video_content": False,
            "stats_summary": {},
            "complete_content": ""  # Complete text content
        }
        
        # Extract title
        title_elem = soup.find('div', class_='ae88c4')
        if title_elem:
            placement_data["title"] = title_elem.get_text(strip=True)

        # Get the main content container
        content_div = soup.find('div', id='EdContent__placement_section_overview')
        
        if content_div:
        
            # Get complete text content
            complete_text = content_div.get_text(separator='\n', strip=True)
            placement_data["complete_content"] = complete_text
            paragraphs = []
            
            # First, try to find the main content wrapper
            content_wrapper = content_div.find('div', class_='faq__according-wrapper')
            if not content_wrapper:
                content_wrapper = content_div
            
            # Get all paragraphs
            p_tags = content_wrapper.find_all('p')
            for p in p_tags:
                text = p.get_text(separator=' ', strip=True)
                if text and len(text) > 20:  # Filter out very short text
                    text = ' '.join(text.split())
                    paragraphs.append(text)
            
            placement_data["paragraphs"] = paragraphs
           
            # Extract all tables from the entire section
            all_tables = []
            
            # Get tables from main content
            main_tables = content_div.find_all('table')
        
            for i, table in enumerate(main_tables):
                table_data = []
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    row_data = []
                    
                    for cell in cells:
                        cell_text = cell.get_text(separator=' ', strip=True)
                        cell_text = ' '.join(cell_text.split())
                        row_data.append(cell_text)
                    
                    if row_data:
                        table_data.append(row_data)
                
                if table_data:
                    all_tables.append({
                        "id": f"main_table_{i+1}",
                        "location": "main_content",
                        "data": table_data,
                        "rows": len(table_data),
                        "columns": len(table_data[0]) if table_data else 0
                    })
        
        # Now extract FAQs separately (you already have this working)
        faq_section = soup.find('div', id='sectional-faqs-0')
        if faq_section:
            faqs = []
            
            # Find all FAQ items
            faq_items = faq_section.find_all('div', class_='html-0')
            
            for faq_item in faq_items:
                try:
                    # Get question
                    question_elem = faq_item.find('strong', class_='flx-box')
                    if question_elem:
                        question_text = question_elem.get_text(strip=True)
                        # Clean question
                        import re
                        question_text = re.sub(r'^Q[:.]\s*', '', question_text).strip()
                        question_text = ' '.join(question_text.split())
                        
                        # Get answer
                        answer_container = faq_item.find_next('div', class_='f61835')
                        if answer_container:
                            # Try different selectors for answer
                            answer_div = answer_container.find('div', class_='wikkiContents')
                            if not answer_div:
                                answer_div = answer_container.find('div', class_='facb5f')
                            
                            if answer_div:
                                answer_text = answer_div.get_text(separator=' ', strip=True)
                                answer_text = re.sub(r'^A[:.]\s*', '', answer_text).strip()
                                answer_text = ' '.join(answer_text.split())
                                
                                # Also extract tables from FAQ answers
                                faq_tables = answer_div.find_all('table')
                                if faq_tables:
                                    for j, table in enumerate(faq_tables):
                                        table_data = []
                                        rows = table.find_all('tr')
                                        
                                        for row in rows:
                                            cells = row.find_all(['th', 'td'])
                                            row_data = [cell.get_text(separator=' ', strip=True) for cell in cells]
                                            row_data = [' '.join(cell.split()) for cell in row_data]
                                            if row_data:
                                                table_data.append(row_data)
                                        
                                        if table_data:
                                            all_tables.append({
                                                "id": f"faq_table_{len(all_tables)+1}",
                                                "location": f"faq_{len(faqs)+1}",
                                                "context": question_text[:50],
                                                "data": table_data,
                                                "rows": len(table_data),
                                                "columns": len(table_data[0]) if table_data else 0
                                            })
                                
                                if question_text and answer_text:
                                    faqs.append({
                                        "question": question_text,
                                        "answer": answer_text[:2000]  # Limit length
                                    })
                except Exception as e:
                  
                    continue
            
            placement_data["faqs"] = faqs
           
        
        # Add all tables to placement_data
        placement_data["tables"] = all_tables
        
        # Extract rating
        rating_div = soup.find('div', class_='c5d199')
        if rating_div:
            rating_text = rating_div.get_text(separator=' ', strip=True)
            rating_text = ' '.join(rating_text.split())
            placement_data["rating_details"] = rating_text
            
            import re
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                placement_data["rating"] = rating_match.group(1)
        
        # Extract download links
        download_links = soup.find_all('a', class_='smce-docs')
        for link in download_links:
            link_text = link.get_text(separator=' ', strip=True)
            link_text = ' '.join(link_text.split())
            if link_text:
                placement_data["links"].append(link_text)
        
        # Extract user feedback
        feedback_div = soup.find('div', class_='d79b7a')
        if feedback_div:
            feedback_text = feedback_div.get_text(separator=' ', strip=True)
            feedback_text = ' '.join(feedback_text.split())
            placement_data["user_feedback"] = feedback_text
        
        # Check for video
        video_div = soup.find('div', class_='vcmsEmbed')
        if video_div:
            placement_data["video_content"] = True
        
        # Add to college_info
        college_info["placement_data"] = placement_data
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Minimal fallback
        college_info["placement_data"] = {
            "title": "IIM Ahmedabad Placement Overview 2025",
            "paragraphs": [],
            "tables": [],
            "faqs": [],
            "rating": "",
            "rating_details": "",
            "links": [],
            "user_feedback": "",
            "video_content": False,
            "error": str(e)
        }
    try:
        # Wait for average package section to load
        wait.until(EC.presence_of_element_located((By.ID, "placement_section_average_package")))
        
        # Scroll to the section
        driver.execute_script("window.scrollTo(0, 1500);")
        time.sleep(2)
        

        try:
            read_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Read more') or contains(text(), 'Read less')]")
            for button in read_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                        print("✓ Clicked read more/less button")
                        time.sleep(2)
                        break
                except:
                    continue
        except:
            pass
        
        # Get the section HTML
        avg_package_section = driver.find_element(By.ID, "placement_section_average_package")
        section_html = driver.execute_script("""
            var section = arguments[0];
            return section.outerHTML;
        """, avg_package_section)
    
   
        soup = BeautifulSoup(section_html, 'html.parser')
        
        # Initialize data structure
        avg_package_data = {
            "title": "",
            "main_table": [],
            "top_recruiters": [],
            "insights": [],
            "faqs": [],
            "graph_image": "",
            "source_info": "",
            "complete_content": ""
        }
        
        # Extract title
        title_elem = soup.find('div', class_='ae88c4')
        if title_elem:
            avg_package_data["title"] = title_elem.get_text(strip=True)

        # Get the main content container
        content_div = soup.find('div', id='EdContent__placement_section_average_package')
        
        if content_div:
            # Get complete text content
            complete_text = content_div.get_text(separator='\n', strip=True)
            avg_package_data["complete_content"] = complete_text
            
            # Extract main table
            main_table = content_div.find('table')
            if main_table:
                table_data = []
                rows = main_table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    row_data = []
                    
                    for cell in cells:
                        cell_text = cell.get_text(separator=' ', strip=True)
                        cell_text = ' '.join(cell_text.split())
                        row_data.append(cell_text)
                    
                    if row_data:
                        table_data.append(row_data)
                
                avg_package_data["main_table"] = table_data
          
            # Extract introductory paragraph
            intro_paragraph = content_div.find('p')
            if intro_paragraph:
                intro_text = intro_paragraph.get_text(strip=True)
                intro_text = ' '.join(intro_text.split())
                avg_package_data["intro_text"] = intro_text
      
        # Find the Top Recruiters section
        recruiters_section = soup.find('div', class_='ca08b1')
        if recruiters_section:
            # Get the heading
            recruiters_heading = recruiters_section.find('p')
            if recruiters_heading:
                avg_package_data["recruiters_heading"] = recruiters_heading.get_text(strip=True)
            
            # Extract all recruiter names
            recruiters = []
            recruiter_spans = recruiters_section.find_all('span', class_='c4af72')
            for span in recruiter_spans:
                recruiter_name = span.get_text(strip=True)
                if recruiter_name:
                    recruiters.append(recruiter_name)
            
            avg_package_data["top_recruiters"] = recruiters
   
            # Sample recruiters
            if recruiters:
                print(f"  Sample: {recruiters[:5]}")
        
        # Extract Insights on Placements

        insights_section = soup.find('div', class_='b811f8')
        if insights_section:
            # Get insights heading
            insights_heading = insights_section.find('h4')
            if insights_heading:
                avg_package_data["insights_heading"] = insights_heading.get_text(strip=True)
            
            # Get student responses count
            responses_span = insights_section.find('span', class_='ede34e')
            if responses_span:
                avg_package_data["responses_count"] = responses_span.get_text(strip=True)
        
        # Extract individual insights
        insights = []
        insight_items = soup.find_all('div', class_='cdf9a8')
        
        for item in insight_items:
            try:
                # Get insight title
                title_elem = item.find('h6')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # Get insight description
                    desc_elem = item.find('p')
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                        
                        insights.append({
                            "title": title,
                            "description": description
                        })
            except:
                continue
        
        avg_package_data["insights"] = insights
       
        # Extract graph image
        graph_img = soup.find('img', alt=lambda x: x and 'Average Package graph' in x)
        if graph_img:
            graph_src = graph_img.get('src', '')
            if graph_src:
                avg_package_data["graph_image"] = graph_src
             
        # Extract source information
        source_div = soup.find('div', class_='d4160c')
        if source_div:
            source_text = source_div.get_text(separator=' ', strip=True)
            source_text = ' '.join(source_text.split())
            avg_package_data["source_info"] = source_text
 
        faq_section = soup.find('div', id='sectional-faqs-0')
        if faq_section:
            faqs = []
            
            # Find all FAQ items
            faq_items = faq_section.find_all('div', class_='html-0')
            
            for faq_item in faq_items:
                try:
                    # Get question
                    question_elem = faq_item.find('strong', class_='flx-box')
                    if question_elem:
                        question_text = question_elem.get_text(strip=True)
                        # Clean question
                        import re
                        question_text = re.sub(r'^Q[:.]\s*', '', question_text).strip()
                        question_text = ' '.join(question_text.split())
                        
                        # Get answer
                        answer_container = faq_item.find_next('div', class_='f61835')
                        if answer_container:
                            # Try to find answer in wikkiContents
                            answer_div = answer_container.find('div', class_='wikkiContents')
                            if not answer_div:
                                answer_div = answer_container.find('div', class_='facb5f')
                            
                            if answer_div:
                                answer_text = answer_div.get_text(separator=' ', strip=True)
                                answer_text = re.sub(r'^A[:.]\s*', '', answer_text).strip()
                                answer_text = ' '.join(answer_text.split())
                                
                                # Extract tables from FAQ answers
                                faq_tables = []
                                tables_in_answer = answer_div.find_all('table')
                                
                                for table in tables_in_answer:
                                    table_data = []
                                    rows = table.find_all('tr')
                                    
                                    for row in rows:
                                        cells = row.find_all(['th', 'td'])
                                        row_data = [cell.get_text(separator=' ', strip=True) for cell in cells]
                                        row_data = [' '.join(cell.split()) for cell in row_data]
                                        if row_data:
                                            table_data.append(row_data)
                                    
                                    if table_data:
                                        faq_tables.append(table_data)
                                
                                if question_text and answer_text:
                                    faqs.append({
                                        "question": question_text,
                                        "answer": answer_text[:2000],  # Limit length
                                        "tables": faq_tables
                                    })
                except Exception as e:
                    
                    continue
            
            avg_package_data["faqs"] = faqs
            
        
        # Extract user feedback
        feedback_div = soup.find('div', class_='d79b7a')
        if feedback_div:
            feedback_text = feedback_div.get_text(separator=' ', strip=True)
            feedback_text = ' '.join(feedback_text.split())
            avg_package_data["user_feedback"] = feedback_text
        
        # Add to college_info (as a separate section)
        if "placement_sections" not in college_info:
            college_info["placement_sections"] = {}
        
        college_info["placement_sections"]["average_package"] = avg_package_data
        
        # Also add to main placement_data for backward compatibility
        if "placement_data" not in college_info:
            college_info["placement_data"] = {}
        
        # Add average package table to main placement_data
        if avg_package_data.get("main_table"):
            if "tables" not in college_info["placement_data"]:
                college_info["placement_data"]["tables"] = []
            
            college_info["placement_data"]["tables"].append({
                "title": "Average Package 2023-2025",
                "data": avg_package_data["main_table"]
            })
        
        # Add recruiters to main placement_data
        if avg_package_data.get("top_recruiters"):
            college_info["placement_data"]["top_recruiters"] = avg_package_data["top_recruiters"]
        
        # Add insights to main placement_data
        if avg_package_data.get("insights"):
            college_info["placement_data"]["insights"] = avg_package_data["insights"]
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Add empty section to avoid errors
        if "placement_sections" not in college_info:
            college_info["placement_sections"] = {}
        
        college_info["placement_sections"]["average_package"] = {
            "title": "IIM Ahmedabad Average Package 2025",
            "main_table": [],
            "top_recruiters": [],
            "insights": [],
            "faqs": [],
            "graph_image": "",
            "source_info": "",
            "complete_content": "",
            "error": str(e)
        }
    try:
        # Wait for PGP placements section to load
        wait.until(EC.presence_of_element_located((By.ID, "placement_section_about_baseCourse_101")))
        
        # Scroll to the section
        driver.execute_script("window.scrollTo(0, 2000);")
        time.sleep(2)
        
        # Click "Read more" if exists in this section
        try:
            section_element = driver.find_element(By.ID, "placement_section_about_baseCourse_101")
            read_buttons = section_element.find_elements(By.XPATH, ".//*[contains(text(), 'Read more') or contains(text(), 'Read less')]")
            for button in read_buttons:
                try:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].click();", button)
                        print("✓ Clicked read more/less in PGP section")
                        time.sleep(2)
                        break
                except:
                    continue
        except:
            pass
        
        # Also try to expand the PGP FABM accordion if present
        try:
            fabm_accordion = driver.find_element(By.ID, "placement_section_class_profile")
            fabm_header = fabm_accordion.find_element(By.CLASS_NAME, "ca7e28")
            if fabm_header:
                driver.execute_script("arguments[0].click();", fabm_header)
                
                time.sleep(2)
        except:
            pass
        
        # Get the section HTML
        pgp_section = driver.find_element(By.ID, "placement_section_about_baseCourse_101")
        section_html = driver.execute_script("""
            var section = arguments[0];
            return section.outerHTML;
        """, pgp_section)
        
        soup = BeautifulSoup(section_html, 'html.parser')
        
        # Initialize data structure
        pgp_placements_data = {
            "title": "",
            "intro_text": "",
            "main_table": [],
            "placement_comparison": [],
            "pgp_fabm_data": {},
            "faqs": [],
            "placement_rating": "",
            "source_info": "",
            "complete_content": ""
        }
        
        # Extract title
        title_elem = soup.find('div', class_='ae88c4')
        if title_elem:
            pgp_placements_data["title"] = title_elem.get_text(strip=True)

        content_div = soup.find('div', id='EdContent_')
        if content_div:
            intro_text = content_div.get_text(separator='\n', strip=True)
            pgp_placements_data["complete_content"] = intro_text
            
            # Get paragraphs
            paragraphs = content_div.find_all('p')
            if paragraphs:
                intro_para = paragraphs[0].get_text(strip=True) if len(paragraphs) > 0 else ""
                key_para = paragraphs[1].get_text(strip=True) if len(paragraphs) > 1 else ""
                
                pgp_placements_data["intro_text"] = intro_para
                pgp_placements_data["key_points_text"] = key_para
          
        
        main_table = soup.find('table', class_='table d7ad5f f866a4 dc8ace')
        if main_table:
            table_data = []
            
            # Extract headers
            headers = []
            header_row = main_table.find('thead').find('tr')
            if header_row:
                th_cells = header_row.find_all('th')
                headers = [th.get_text(strip=True) for th in th_cells]
                if headers:
                    table_data.append(headers)
            
            # Extract data rows
            tbody = main_table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    row_data = []
                    
                    for cell in cells:
                        # Get main text
                        cell_text = cell.get_text(separator=' ', strip=True)
                        cell_text = ' '.join(cell_text.split())
                        
                        # Check for info icon (might have additional info)
                        info_div = cell.find('div', class_='f6ee63')
                        if info_div:
                            cell_text = cell_text.replace(info_div.get_text(strip=True), '').strip()
                        
                        row_data.append(cell_text)
                    
                    if row_data:
                        table_data.append(row_data)
            
            pgp_placements_data["main_table"] = table_data
       
            # Show sample
            if len(table_data) > 1:
                print(f"  Sample row: {table_data[1]}")
        
        # Extract source information
        source_div = soup.find('div', class_='d4160c')
        if source_div:
            source_text = source_div.get_text(separator=' ', strip=True)
            source_text = ' '.join(source_text.split())
            pgp_placements_data["source_info"] = source_text
        
        comparison_div = soup.find('div', id='placement_section_placement_comparison')
        if comparison_div:
            comparison_table = comparison_div.find('table', class_='table f6a6c1 f866a4 dc8ace')
            if comparison_table:
                comparison_data = []
                
                # Extract headers
                comp_headers = []
                comp_header_row = comparison_table.find('thead').find('tr')
                if comp_header_row:
                    th_cells = comp_header_row.find_all('th')
                    comp_headers = [th.get_text(strip=True) for th in th_cells]
                    if comp_headers:
                        comparison_data.append(comp_headers)
                
                # Extract data rows
                comp_tbody = comparison_table.find('tbody')
                if comp_tbody:
                    rows = comp_tbody.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        row_data = []
                        
                        for cell in cells:
                            cell_text = cell.get_text(separator=' ', strip=True)
                            cell_text = ' '.join(cell_text.split())
                            row_data.append(cell_text)
                        
                        if row_data:
                            comparison_data.append(row_data)
                
                pgp_placements_data["placement_comparison"] = comparison_data
               
                # Extract source note
                source_note = comparison_div.find('i', class_='da39de')
                if source_note:
                    pgp_placements_data["comparison_note"] = source_note.get_text(strip=True)
        
       
        fabm_section = soup.find('div', id='placement_section_class_profile')
        if fabm_section:
            fabm_data = {
                "title": "",
                "content": "",
                "table": []
            }
            
            # Extract FABM title
            fabm_title = fabm_section.find('div', class_='ae88c4')
            if fabm_title:
                fabm_data["title"] = fabm_title.get_text(strip=True)
            
            # Extract FABM content
            fabm_content = fabm_section.find('div', id='EdContent__placement_section_class_profile')
            if fabm_content:
                fabm_text = fabm_content.get_text(separator='\n', strip=True)
                fabm_data["content"] = fabm_text
                
                # Extract FABM table
                fabm_table = fabm_content.find('table')
                if fabm_table:
                    fabm_table_data = []
                    rows = fabm_table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        row_data = [cell.get_text(separator=' ', strip=True) for cell in cells]
                        row_data = [' '.join(cell.split()) for cell in row_data]
                        if row_data:
                            fabm_table_data.append(row_data)
                    
                    fabm_data["table"] = fabm_table_data
            
            pgp_placements_data["pgp_fabm_data"] = fabm_data
          
        # Extract Placement rating
        rating_div = soup.find('div', class_='bdb2d9')
        if rating_div:
            rating_text = rating_div.get_text(strip=True)
            pgp_placements_data["placement_rating"] = rating_text
            
      
        faq_section = soup.find('div', id='sectional-faqs-0')
        if faq_section:
            faqs = []
            
            # Find all FAQ items
            faq_items = faq_section.find_all('div', class_='html-0')
            
            for faq_item in faq_items:
                try:
                    # Get question
                    question_elem = faq_item.find('strong', class_='flx-box')
                    if question_elem:
                        question_text = question_elem.get_text(strip=True)
                        # Clean question
                        import re
                        question_text = re.sub(r'^Q[:.]\s*', '', question_text).strip()
                        question_text = ' '.join(question_text.split())
                        
                        # Get answer
                        answer_container = faq_item.find_next('div', class_='f61835')
                        if answer_container:
                            # Try to find answer in wikkiContents
                            answer_div = answer_container.find('div', class_='wikkiContents')
                            if not answer_div:
                                answer_div = answer_container.find('div', class_='facb5f')
                            
                            if answer_div:
                                answer_text = answer_div.get_text(separator=' ', strip=True)
                                answer_text = re.sub(r'^A[:.]\s*', '', answer_text).strip()
                                answer_text = ' '.join(answer_text.split())
                                
                                # Extract tables from FAQ answers
                                faq_tables = []
                                tables_in_answer = answer_div.find_all('table')
                                
                                for table in tables_in_answer:
                                    table_data = []
                                    rows = table.find_all('tr')
                                    
                                    for row in rows:
                                        cells = row.find_all(['th', 'td'])
                                        row_data = [cell.get_text(separator=' ', strip=True) for cell in cells]
                                        row_data = [' '.join(cell.split()) for cell in row_data]
                                        if row_data:
                                            table_data.append(row_data)
                                    
                                    if table_data:
                                        faq_tables.append({
                                            "rows": len(table_data),
                                            "columns": len(table_data[0]) if table_data else 0,
                                            "data": table_data
                                        })
                                
                                if question_text and answer_text:
                                    faqs.append({
                                        "question": question_text,
                                        "answer": answer_text[:3000],  # Limit length
                                        "tables": faq_tables,
                                        "table_count": len(faq_tables)
                                    })
                except Exception as e:
                   
                    continue
            
            pgp_placements_data["faqs"] = faqs
         
        # Extract user feedback
        feedback_div = soup.find('div', class_='d79b7a')
        if feedback_div:
            feedback_text = feedback_div.get_text(separator=' ', strip=True)
            pgp_placements_data["user_feedback"] = feedback_text
        
        # Add to college_info
        if "placement_sections" not in college_info:
            college_info["placement_sections"] = {}
        
        college_info["placement_sections"]["pgp_placements"] = pgp_placements_data
        
        # Also add to main placement_data for backward compatibility
        if "placement_data" not in college_info:
            college_info["placement_data"] = {}
        
        # Add PGP table to main placement_data
        if pgp_placements_data.get("main_table"):
            if "tables" not in college_info["placement_data"]:
                college_info["placement_data"]["tables"] = []
            
            college_info["placement_data"]["tables"].append({
                "title": "PGP Placement Statistics 2023-2025",
                "data": pgp_placements_data["main_table"]
            })
        
        # Add FAQs to main placement_data
        if pgp_placements_data.get("faqs"):
            if "faqs" not in college_info["placement_data"]:
                college_info["placement_data"]["faqs"] = []
            
            college_info["placement_data"]["faqs"].extend(pgp_placements_data["faqs"])
    except Exception as e:
        
        import traceback
        traceback.print_exc()
        
        # Add empty section to avoid errors
        if "placement_sections" not in college_info:
            college_info["placement_sections"] = {}
        
        college_info["placement_sections"]["pgp_placements"] = {
            "title": "IIM Ahmedabad PGP Placements 2025",
            "intro_text": "",
            "main_table": [],
            "placement_comparison": [],
            "pgp_fabm_data": {},
            "faqs": [],
            "placement_rating": "",
            "source_info": "",
            "complete_content": "",
            "error": str(e)
        }

    return college_info

    


def scrape_cutoff(driver, URLS):
    try:
        driver.get(URLS["cutoff"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["cutoff"])

    wait = WebDriverWait(driver, 20)
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
        "placement_data": {},
        "cutoff_data": {
            "qualifying_cutoff": {},
            "year_wise_cutoff": {},
            "college_comparison": [],
            "faqs": [],
            "description": []
        }
    }
    
    # ---------- COLLEGE HEADER ----------
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image
        try:
            top_header_section = driver.find_element(By.ID, "topHeaderCard-top-section")
            cover_img = top_header_section.find_element(By.ID, "topHeaderCard-gallery-image")
            college_info["cover_image"] = cover_img.get_attribute("src")
            
        except:
            pass
        
        # Extract logo
        try:
            logo_div = driver.find_element(By.CSS_SELECTOR, ".ca46d2.e014b3")
            logo_img = logo_div.find_element(By.TAG_NAME, "img")
            college_info["logo"] = logo_img.get_attribute("src")
         
        except:
            pass
        
        # Extract videos and photos count
        try:
            badges_div = driver.find_element(By.CSS_SELECTOR, ".e4df0b.ad160e")
            badges = badges_div.find_elements(By.CSS_SELECTOR, ".dcd631")
            
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    videos_match = re.search(r'(\d+)\s*videos?', text)
                    if videos_match:
                        college_info["videos_count"] = int(videos_match.group(1))
                elif "photo" in text:
                    photos_match = re.search(r'(\d+)\s*photos?', text)
                    if photos_match:
                        college_info["photos_count"] = int(photos_match.group(1))
        except:
            print("⚠️ Videos/Photos count not found")
        
        # Try to find college name from various selectors
        try:
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for h1 in h1_elements:
                if h1.text and ("Fees" in h1.text or "IIM" in h1.text):
                    college_info["college_name"] = h1.text.replace(" Fees", "").replace(" - Indian Institute of Management", "").strip()
                    break
        except:
            pass

        # Extract from the provided HTML structure
        try:
            header_section = driver.find_element(By.CSS_SELECTOR, ".a655da.aadf9d")
            
            # College name
            try:
                name_elem = header_section.find_element(By.CSS_SELECTOR, "h1.cc5e8d")
                college_info["college_name"] = name_elem.text.strip()
            except:
                pass
            
            # Location
            try:
                location_div = header_section.find_element(By.CSS_SELECTOR, ".de89cf")
                location_text = location_div.text.strip()
                if "," in location_text:
                    parts = [p.strip() for p in location_text.split(",", 1)]
                    college_info["location"] = parts[0].replace(",", "").strip()
                    college_info["city"] = parts[1] if len(parts) > 1 else ""
            except:
                pass
            
            # Rating and reviews
            try:
                rating_div = header_section.find_element(By.CSS_SELECTOR, ".e6f71f")
                rating_text = rating_div.text.strip()
                rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
                if rating_match:
                    college_info["rating"] = rating_match.group(1)
                
                reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
                if reviews_match:
                    college_info["reviews_count"] = int(reviews_match.group(1))
            except:
                pass
            
            # Q&A count
            try:
                qa_link = header_section.find_element(By.XPATH, ".//a[contains(text(), 'Student Q&A')]")
                qa_text = qa_link.text.strip()
                qa_match = re.search(r"(\d+(?:\.\d+)?)\s*(k|K)?", qa_text)
                if qa_match:
                    count = float(qa_match.group(1))
                    if qa_match.group(2):
                        count = int(count * 1000)
                    college_info["qa_count"] = int(count)
            except:
                pass
            
            # Institute type and established year
            try:
                list_items = header_section.find_elements(By.CSS_SELECTOR, ".ff9e36 li")
                for li in list_items:
                    text = li.text.strip().lower()
                    if "institute" in text:
                        college_info["institute_type"] = li.text.strip()
                    elif "estd" in text:
                        year_match = re.search(r"\b(\d{4})\b", li.text)
                        if year_match:
                            college_info["established_year"] = year_match.group(1)
            except:
                pass
                
        except Exception as e:
            print("⚠️ Error extracting header info: ")

    except Exception as e:
        print("⚠️ Error in college header section: ")
    
    # ---------- CUTOFF DATA SCRAPING ----------
    try:

        try:
            cutoff_section = wait.until(
                EC.presence_of_element_located((By.ID, "icop_section_exams"))
            )
            # Scroll into view to trigger JavaScript loading
            driver.execute_script("arguments[0].scrollIntoView(true);", cutoff_section)
            time.sleep(2)  # Wait for lazy loading
            
        except Exception as e:
            print("⚠️ Could not find cutoff section: ")
            return college_info
        
        
        try:
            # Wait for table to load with dynamic content
            time.sleep(3)
            
            # Try multiple strategies to find the qualifying cutoff table
            qualifying_table = None
            
            # Strategy 1: Look for table with specific class/id
            try:
                qualifying_table = driver.find_element(By.CSS_SELECTOR, "table.iima-table-id-7902")
               
            except:
                # Strategy 2: Look for table containing specific headers
                qualifying_tables = driver.find_elements(By.XPATH, "//table[.//th[contains(text(), 'VARC')] and .//th[contains(text(), 'DILR')] and .//th[contains(text(), 'QA')]]")
                if qualifying_tables:
                    qualifying_table = qualifying_tables[0]
                   
                else:
                    # Strategy 3: Look in the expanded qualifying cutoff section
                    try:
                        qualifying_section = driver.find_element(By.ID, "icop_section_latest_round_cutoff_327")
                        driver.execute_script("arguments[0].scrollIntoView(true);", qualifying_section)
                        time.sleep(2)
                        qualifying_tables = qualifying_section.find_elements(By.TAG_NAME, "table")
                        if qualifying_tables:
                            qualifying_table = qualifying_tables[0]
                           
                    except:
                        pass
            
            if qualifying_table:
                rows = qualifying_table.find_elements(By.TAG_NAME, "tr")
                
                # Skip header row
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 5:
                        category = cells[0].text.strip()
                        if category:  # Only add if category is not empty
                            college_info["cutoff_data"]["qualifying_cutoff"][category] = {
                                "VARC": cells[1].text.strip(),
                                "DILR": cells[2].text.strip(),
                                "QA": cells[3].text.strip(),
                                "Overall": cells[4].text.strip()
                            }
                
    
            else:
                pass
               
        
        except Exception as e:
           
            import traceback
            traceback.print_exc()
        
        # 2. Scrape Year-wise Cutoff Tables
        try:
            # Scroll to trigger loading of year-wise tables
            year_wise_section = driver.find_element(By.ID, "icop_section_previous_year_cutoff_327")
            driver.execute_script("arguments[0].scrollIntoView(true);", year_wise_section)
            time.sleep(2)
            
            # Find all year-wise cutoff tables
            cutoff_tables = driver.find_elements(By.CSS_SELECTOR, ".table.a82bdd.f866a4.dc8ace")
          
            for table_index, table in enumerate(cutoff_tables):
                try:
                    # Get table headers to determine table type
                    thead = table.find_element(By.TAG_NAME, "thead")
                    header_row = thead.find_element(By.TAG_NAME, "tr")
                    headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, "th")]
                    
                    # Check if this is a year-wise cutoff table (has years as headers)
                    is_year_table = any(header.isdigit() and len(header) == 4 for header in headers)
                    
                    if is_year_table:
                        # Try to get the course name from the previous h5 element
                        try:
                            course_header = driver.execute_script("""
                                var table = arguments[0];
                                var prev = table.previousElementSibling;
                                while (prev && prev.tagName !== 'H5') {
                                    prev = prev.previousElementSibling;
                                }
                                return prev ? prev.textContent : '';
                            """, table)
                            course_name = course_header.strip()
                            # Clean up the course name
                            if "IIM Ahmedabad" in course_name:
                                course_name = course_name.split(" - IIM Ahmedabad")[0].strip()
                            if "CAT percentile Cutoff" in course_name:
                                course_name = course_name.split(": CAT percentile Cutoff")[0].strip()
                            if not course_name:
                                course_name = f"Course_{table_index + 1}"
                        except:
                            course_name = f"Course_{table_index + 1}"
                        
                        # Extract table data
                        rows_data = []
                        tbody = table.find_element(By.TAG_NAME, "tbody")
                        data_rows = tbody.find_elements(By.TAG_NAME, "tr")
                        
                        for row in data_rows:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) > 0:
                                row_data = {
                                    "section": cells[0].text.strip(),
                                    "scores": {}
                                }
                                
                                # Map scores to years based on headers
                                for i in range(1, min(len(cells), len(headers))):
                                    year = headers[i]
                                    score = cells[i].text.strip()
                                    row_data["scores"][year] = score
                                
                                rows_data.append(row_data)
                        
                        if rows_data:
                            college_info["cutoff_data"]["year_wise_cutoff"][course_name] = {
                                "headers": headers,
                                "data": rows_data
                            }
                            print(f"  Added year-wise cutoff for: {course_name}")
                
                except Exception as e:
                    
                    continue
            
          
        except Exception as e:
            print("⚠️ Error scraping year-wise cutoff: ")
        
        # 3. Scrape College Comparison Table
        try:
            # Scroll to college comparison section
            comparison_section = driver.find_element(By.ID, "icop_section_college_comparison_327")
            driver.execute_script("arguments[0].scrollIntoView(true);", comparison_section)
            time.sleep(2)
            
            # Find college comparison table by looking for specific headers
            comparison_tables = driver.find_elements(By.XPATH, "//table[.//th[contains(text(), 'Colleges')] and .//th[contains(text(), 'Specialization')]]")
            
            if comparison_tables:
                comparison_table = comparison_tables[0]
                
                # Get table rows
                tbody = comparison_table.find_element(By.TAG_NAME, "tbody")
                data_rows = tbody.find_elements(By.TAG_NAME, "tr")
                
                for row in data_rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        # Extract college name and link
                        college_cell = cells[0]
                        
                        # Find college name (look for link with blackLink class or f0581e class)
                        college_name = ""
                        college_link = ""
                        
                        try:
                            college_link_elem = college_cell.find_element(By.CSS_SELECTOR, "a.f0581e.blackLink")
                            college_name = college_link_elem.text.strip()
                            college_link = college_link_elem.get_attribute("href")
                        except:
                            try:
                                # Try other selectors
                                links = college_cell.find_elements(By.TAG_NAME, "a")
                                for link in links:
                                    if link.text.strip() and "compare" not in link.text.lower():
                                        college_name = link.text.strip()
                                        college_link = link.get_attribute("href")
                                        break
                            except:
                                # If no link, get text from the cell
                                college_name = college_cell.text.strip()
                                # Remove "Compare" text if present
                                if "\n" in college_name:
                                    college_name = college_name.split("\n")[0].strip()
                        
                        # Extract specialization
                        specialization = cells[1].text.strip() if len(cells) > 1 else ""
                        
                        # Extract cutoff (clean up the text)
                        cutoff_text = cells[2].text.strip() if len(cells) > 2 else ""
                        # Extract just the number if possible
                        cutoff_match = re.search(r'(\d+(?:\.\d+)?)', cutoff_text)
                        cutoff = cutoff_match.group(1) if cutoff_match else cutoff_text
                        
                        # Only add if we have college name
                        if college_name and college_name != "Compare":
                            college_info["cutoff_data"]["college_comparison"].append({
                                "college_name": college_name,
                                "college_link": college_link,
                                "specialization": specialization,
                                "cutoff": cutoff
                            })
                
                # Remove duplicates
                unique_comparisons = []
                seen = set()
                for comp in college_info["cutoff_data"]["college_comparison"]:
                    key = (comp["college_name"], comp["specialization"], comp["cutoff"])
                    if key not in seen:
                        seen.add(key)
                        unique_comparisons.append(comp)
                
                college_info["cutoff_data"]["college_comparison"] = unique_comparisons

            else:
                pass
        
        except Exception as e:
            print("⚠️ Error scraping college comparison: ")
        
        # 4. Scrape FAQ Questions
        try:
            # Scroll to FAQ section
            faq_sections = driver.find_elements(By.CLASS_NAME, "sectional-faqs")
            
            for faq_section in faq_sections:
                faq_items = faq_section.find_elements(By.CLASS_NAME, "html-0")
                
                for faq_item in faq_items:
                    try:
                        # Extract question text
                        strong_element = faq_item.find_element(By.TAG_NAME, "strong")
                        question_text = strong_element.text.strip()
                        
                        # Clean up the question text
                        if question_text:
                            # Remove extra whitespace and newlines
                            question_text = ' '.join(question_text.split())
                            # Remove extra "Q:" if present
                            if question_text.startswith("Q:"):
                                question_text = question_text[2:].strip()
                            college_info["cutoff_data"]["faqs"].append(question_text)
                    except:
                        continue
            
            # Remove duplicates
            college_info["cutoff_data"]["faqs"] = list(dict.fromkeys(college_info["cutoff_data"]["faqs"]))
          
        except Exception as e:
            print("⚠️ Error scraping FAQs: ")
        
        # 5. Scrape Description
        try:
            # Get cutoff description from wikiContents sections
            wiki_sections = driver.find_elements(By.CSS_SELECTOR, ".wikiContents.dfbe34, .wikiContents.a566c1")
            
            for wiki_section in wiki_sections:
                try:
                    paragraphs = wiki_section.find_elements(By.TAG_NAME, "p")
                    for p in paragraphs:
                        text = p.text.strip()
                        # Filter: only keep meaningful paragraphs
                        if text and len(text) > 20 and not text.startswith("A:") and not text.startswith("Q:"):
                            # Clean up text
                            text = ' '.join(text.split())
                            if text not in college_info["cutoff_data"]["description"]:
                                college_info["cutoff_data"]["description"].append(text)
                except:
                    continue
            
           
        except Exception as e:
            print("⚠️ Error scraping description: ")
    
    except Exception as e:
        print("⚠️ Error in cutoff data section: ")
        import traceback
        traceback.print_exc()
    
    return college_info

def scrape_ranking(driver, URLS):
    try:
        driver.get(URLS["ranking"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["ranking"])
    

    wait = WebDriverWait(driver, 40)  # Increased wait time
    
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    

    time.sleep(7)  # Increased initial wait
    
    try:
        # Wait for specific elements to ensure page is loaded
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.cc5e8d")))
        
    except:
        pass
    

    try:
        # Extract cover image
        try:
            cover_img = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-gallery-image")))
            college_info["cover_image"] = cover_img.get_attribute("src")
            
        except:
            pass
        
        # Extract logo
        try:
            logo_img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ca46d2.e014b3 img")))
            college_info["logo"] = logo_img.get_attribute("src")
           
        except:
            pass
        
        # Extract college name - FIXED: Get proper college name
        try:
            # Try multiple selectors for college name
            selectors = [
                "h1.b16e25",  # Main title
                "h1.cc5e8d",  # Alternative title
                ".ab2e01 h1",  # Another alternative
                "h1"  # Any h1
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and "IIM" in text and "Ranking" not in text:
                            college_info["college_name"] = text
                            break
                    if college_info["college_name"]:
                        break
                except:
                    continue
            
            if not college_info["college_name"]:
                # Fallback to any h1
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                for h1 in h1_elements:
                    text = h1.text.strip()
                    if text and "IIM" in text:
                        college_info["college_name"] = text.split("Ranking")[0].strip()
                        break
        except:
            pass
        
        # Extract videos and photos count - FIXED
        try:
            # Look for badges with video/photo counts
            badges = driver.find_elements(By.CSS_SELECTOR, ".dcd631")
            for badge in badges:
                text = badge.text.lower()
                if "video" in text:
                    # Extract number from text like "2 Videos"
                    match = re.search(r'(\d+)\s*videos?', text, re.IGNORECASE)
                    if match:
                        college_info["videos_count"] = int(match.group(1))
                elif "photo" in text:
                    match = re.search(r'(\d+)\s*photos?', text, re.IGNORECASE)
                    if match:
                        college_info["photos_count"] = int(match.group(1))
        except:
            pass
        
        # Extract location
        try:
            location_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".de89cf")))
            location_text = location_elem.text.strip()
            if "," in location_text:
                parts = [p.strip() for p in location_text.split(",", 1)]
                college_info["location"] = parts[0].replace(",", "").strip()
                college_info["city"] = parts[1] if len(parts) > 1 else ""
           
        except:
            pass
        
        # Extract rating and reviews
        try:
            rating_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".e6f71f")))
            rating_text = rating_div.text.strip()
            
            rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
            if rating_match:
                college_info["rating"] = rating_match.group(1)
            
            reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
            if reviews_match:
                college_info["reviews_count"] = int(reviews_match.group(1))
            

        except:
            pass
        
        # Extract Q&A count - FIXED
        try:
            # Look for Q&A links in the header
            qa_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'questions') or contains(text(), 'Q&A') or contains(text(), 'Student Q&A')]")
            for link in qa_links:
                text = link.text.strip()
                if "Q&A" in text or "Questions" in text:
                    # Extract number from text like "1.5k" or "1500"
                    match = re.search(r'([\d,\.]+(?:k|K)?)', text)
                    if match:
                        num_text = match.group(1).replace(',', '')
                        if 'k' in num_text.lower():
                            num = float(num_text.lower().replace('k', '')) * 1000
                            college_info["qa_count"] = int(num)
                        else:
                            college_info["qa_count"] = int(float(num_text))
                        break
        except:
            pass
        
        # Extract other details
        try:
            details_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ff9e36 li")))
            for li in details_list:
                text = li.text.strip().lower()
                if "institute" in text:
                    college_info["institute_type"] = li.text.strip()
                elif "estd" in text:
                    year_match = re.search(r"\b(\d{4})\b", li.text)
                    if year_match:
                        college_info["established_year"] = year_match.group(1)
            
  
        except:
            print("⚠️ Institute details not found")
            
    except Exception as e:
        print("⚠️ Error in college header section: ")
        import traceback
        traceback.print_exc()

    ranking_data = {
        "highlights": {"description": "", "rankings": []},
        "international_ranking": {"description": "", "qs_ranking": {}, "financial_times_ranking": {}},
        "nirf": {"description": "", "table_data": [], "comparison": [], "ranking_criteria": {}},
        "outlook": {"description": "", "table_data": [], "comparison": []},
        "business_today": {"table_data": [], "comparison": []},
        "qs_world": {"description": "", "rankings": {}, "comparison": [], "ranking_criteria": {}},
        "table_of_contents": []
    }
    

    try:
        # Use JavaScript to check for specific elements
        js_check = driver.execute_script("""
            return {
                hasToc: document.querySelector('#newTocSection') !== null,
                tocItems: document.querySelectorAll('#newTocSection li').length,
                hasInternationalRanking: document.querySelector('#rp_section_international_ranking') !== null,
                rankingSections: document.querySelectorAll('[id^="rp_section_"]').length
            };
        """)
     
    except Exception as e:
        print("⚠️ JavaScript check failed: ")
    
  
    try:
        # Scroll multiple times to trigger lazy loading
        for i in range(5):
            scroll_position = (i + 1) * 500
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(1)
        
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
    except Exception as e:
        print("⚠️ Error during scrolling: ")
    
    # Helper function to expand all sections
    def expand_all_sections():
       
        try:
            # Find all "Read more" buttons
            read_more_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), 'Read more')]")
            print(f"Found {len(read_more_buttons)} 'Read more' buttons")
            
            for button in read_more_buttons:
                try:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(0.5)
                except:
                    continue
            
            # Also click on accordion headers to expand
            accordions = driver.find_elements(By.CSS_SELECTOR, ".ad25e5")
            for accordion in accordions:
                try:
                    if "expanded" not in accordion.get_attribute("class"):
                        driver.execute_script("arguments[0].scrollIntoView(true);", accordion)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", accordion)
                        time.sleep(0.5)
                except:
                    continue
                    
            return True
        except Exception as e:
            
            return False
    
    # Expand all sections first
    expand_all_sections()
    
    # 1. EXTRACT TABLE OF CONTENTS - COMPLETELY REWRITTEN
    print("\n1. Extracting Table of Contents...")
    try:
        # Use JavaScript to directly extract TOC items
        toc_items_js = driver.execute_script("""
            const tocSection = document.getElementById('newTocSection');
            if (!tocSection) return [];
            
            const items = [];
            const liElements = tocSection.querySelectorAll('li');
            
            liElements.forEach(li => {
                // Try to get text from anchor first, then from li
                const anchor = li.querySelector('a');
                let text = '';
                
                if (anchor) {
                    text = anchor.textContent.trim();
                } else {
                    text = li.textContent.trim();
                }
                
                // Clean up the text
                text = text.replace(/\\n/g, ' ').replace(/\\s+/g, ' ').trim();
                
                if (text && !items.includes(text)) {
                    items.push(text);
                }
            });
            
            return items;
        """)
        
        if toc_items_js:
            ranking_data["table_of_contents"] = toc_items_js
            
        else:
            
            try:
                toc_section = wait.until(EC.presence_of_element_located((By.ID, "newTocSection")))
                toc_items = toc_section.find_elements(By.CSS_SELECTOR, ".c27cda.newTocListV2 li, #newTocSection li")
                
                for item in toc_items:
                    try:
                        # Try to get text from anchor tag
                        try:
                            anchor = item.find_element(By.TAG_NAME, "a")
                            text = anchor.text.strip()
                        except:
                            text = item.text.strip()
                        
                        # Clean the text
                        if text:
                            text = ' '.join(text.split())
                            if text not in ranking_data["table_of_contents"]:
                                ranking_data["table_of_contents"].append(text)
                    except:
                        continue
              
            except Exception as e:
                print("⚠️ TOC extraction failed: ")
                
    except Exception as e:
        print("⚠️ TOC not found: ")
    
 
    try:
        highlights_section = wait.until(EC.presence_of_element_located((By.ID, "rp_section_highlights")))
        driver.execute_script("arguments[0].scrollIntoView(true);", highlights_section)
        time.sleep(2)
        
        # Expand if needed
        expand_all_sections()
        
        # Extract description
        try:
            description_elem = highlights_section.find_element(By.CSS_SELECTOR, ".wikiContents")
            ranking_data["highlights"]["description"] = description_elem.text.strip()
         
        except:
            pass
        
        # Extract ranking cards
        try:
            ranking_cards = highlights_section.find_elements(By.CSS_SELECTOR, ".f35625, .bc4a0d")
        
            
            for card in ranking_cards:
                try:
                    # Extract publisher from image alt text
                    publisher_img = card.find_element(By.TAG_NAME, "img")
                    publisher_alt = publisher_img.get_attribute("alt")
                    
                    # Map alt text to publisher name
                    publisher_map = {
                        "NIRF Icon": "NIRF",
                        "BT Icon": "Business Today",
                        "Outlook Icon": "Outlook",
                        "QS Icon": "QS"
                    }
                    publisher = publisher_map.get(publisher_alt, publisher_alt.replace(" Icon", ""))
                    
                    # Extract category
                    category_elem = card.find_element(By.CLASS_NAME, "f1495c")
                    category = category_elem.text.strip()
                    
                    # Extract year
                    year_elem = card.find_element(By.CLASS_NAME, "d8ca5d")
                    year_text = year_elem.text.strip()
                    
                    # Extract rank
                    rank_elem = card.find_element(By.CLASS_NAME, "a3ae6e")
                    rank = rank_elem.text.strip()
                    
                    # Extract highlight
                    highlight = ""
                    try:
                        highlight_elem = card.find_element(By.CLASS_NAME, "f4f104")
                        highlight = highlight_elem.text.strip().replace("->", "").replace("-&gt;", "").strip()
                    except:
                        pass
                    
                    ranking_data["highlights"]["rankings"].append({
                        "publisher": publisher,
                        "category": category,
                        "year": year_text,
                        "rank": rank,
                        "highlight": highlight
                    })
                    
                except Exception as card_error:
                    continue
                    
        except Exception as e:
            print("⚠️ Error extracting ranking cards: ")
            
    except Exception as e:
        print("⚠️ Error in highlights section: ")
   
    try:
        nirf_section = wait.until(EC.presence_of_element_located((By.ID, "rp_section_publishers_8")))
        driver.execute_script("arguments[0].scrollIntoView(true);", nirf_section)
        time.sleep(2)
        
        # Expand all "Read more" sections
        expand_all_sections()
        
        # Extract description
        try:
            nirf_content = nirf_section.find_element(By.CSS_SELECTOR, ".wikiContents")
            ranking_data["nirf"]["description"] = nirf_content.text.strip()
            print("✓ NIRF description extracted")
        except:
            pass
        
        # Extract table data
        try:
            nirf_table = nirf_section.find_element(By.CSS_SELECTOR, ".table")
            rows = nirf_table.find_elements(By.TAG_NAME, "tr")
            
            if len(rows) > 1:
                headers = []
                th_elements = rows[0].find_elements(By.TAG_NAME, "th")
                for th in th_elements:
                    headers.append(th.text.strip().lower().replace(" ", "_"))
                
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                row_data[headers[i]] = cell.text.strip()
                        ranking_data["nirf"]["table_data"].append(row_data)
                
                print("✓ NIRF table data extracted: {len(ranking_data['nirf']['table_data'])} rows")
        except Exception as e:
            print("⚠️ Error extracting NIRF table: ")
        
        # Extract comparison data
        try:
            # Find all tables in NIRF section
            all_tables = nirf_section.find_elements(By.TAG_NAME, "table")
            
            for table in all_tables:
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:
                        # Check if this is a comparison table (has college names and ranks)
                        first_row_text = rows[1].text.lower()
                        if "iim" in first_row_text or "compare" in first_row_text:
                            for row in rows[1:]:
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if len(cells) >= 2:
                                    college_name = cells[0].text.strip()
                                    # Clean college name
                                    college_name = re.sub(r'\nCompare$', '', college_name)
                                    college_name = re.sub(r'\s+Compare$', '', college_name)
                                    college_name = college_name.split('\n')[0].strip()
                                    rank = cells[1].text.strip()
                                    
                                    ranking_data["nirf"]["comparison"].append({
                                        "college": college_name,
                                        "rank": rank
                                    })

                            break
                except:
                    continue
                    
        except Exception as e:
            print("⚠️ Error extracting NIRF comparison: ")
            
        # Extract ranking criteria using JavaScript
        try:
            criteria_data = driver.execute_script("""
                const criteriaSection = arguments[0];
                const criteria = {};
                
                // Look for tables with ranking criteria
                const tables = criteriaSection.getElementsByTagName('table');
                
                for (let table of tables) {
                    const rows = table.getElementsByTagName('tr');
                    for (let i = 1; i < rows.length; i++) {
                        const cells = rows[i].getElementsByTagName('td');
                        if (cells.length >= 2) {
                            const criteriaName = cells[0].textContent.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
                            const score = cells[1].textContent.trim();
                            if (criteriaName && score) {
                                criteria[criteriaName] = score;
                            }
                        }
                    }
                }
                
                return criteria;
            """, nirf_section)
            
            if criteria_data:
                ranking_data["nirf"]["ranking_criteria"] = criteria_data
           
        except:
            ranking_data["nirf"]["ranking_criteria"] = {}
            
    except Exception as e:
        print("⚠️ Error in NIRF section: ")
    

    try:
        outlook_section = wait.until(EC.presence_of_element_located((By.ID, "rp_section_publishers_3")))
        driver.execute_script("arguments[0].scrollIntoView(true);", outlook_section)
        time.sleep(2)
        
        expand_all_sections()
        
        # Extract description
        try:
            outlook_content = outlook_section.find_element(By.CSS_SELECTOR, ".wikiContents")
            ranking_data["outlook"]["description"] = outlook_content.text.strip()
      
        except:
            pass
        
        # Extract table data
        try:
            outlook_table = outlook_section.find_element(By.CSS_SELECTOR, ".table")
            rows = outlook_table.find_elements(By.TAG_NAME, "tr")
            
            if len(rows) > 1:
                headers = []
                th_elements = rows[0].find_elements(By.TAG_NAME, "th")
                for th in th_elements:
                    headers.append(th.text.strip().lower().replace(" ", "_"))
                
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                row_data[headers[i]] = cell.text.strip()
                        ranking_data["outlook"]["table_data"].append(row_data)

        except Exception as e:
            print("⚠️ Error extracting Outlook table: ")
        
        # Extract comparison data
        try:
            comp_tables = outlook_section.find_elements(By.CSS_SELECTOR, ".table.f6a6c1, table")
            
            for table in comp_tables:
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:
                        for row in rows[1:]:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 2:
                                college_name = cells[0].text.strip()
                                college_name = re.sub(r'\nCompare$', '', college_name)
                                college_name = re.sub(r'\s+Compare$', '', college_name)
                                college_name = college_name.split('\n')[0].strip()
                                rank = cells[1].text.strip()
                                
                                ranking_data["outlook"]["comparison"].append({
                                    "college": college_name,
                                    "rank": rank
                                })

                        break
                except:
                    continue
                    
        except Exception as e:
            print("⚠️ Error extracting Outlook comparison: ")
            
    except Exception as e:
        print("⚠️ Error in Outlook section: ")
    
   
    try:
        bt_section = wait.until(EC.presence_of_element_located((By.ID, "rp_section_publishers_2")))
        driver.execute_script("arguments[0].scrollIntoView(true);", bt_section)
        time.sleep(2)
        
        # Extract table data
        try:
            bt_table = bt_section.find_element(By.CSS_SELECTOR, ".table")
            rows = bt_table.find_elements(By.TAG_NAME, "tr")
            
            if len(rows) > 1:
                headers = []
                th_elements = rows[0].find_elements(By.TAG_NAME, "th")
                for th in th_elements:
                    headers.append(th.text.strip().lower().replace(" ", "_"))
                
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                row_data[headers[i]] = cell.text.strip()
                        ranking_data["business_today"]["table_data"].append(row_data)
        except Exception as e:
            print("⚠️ Error extracting Business Today table: ")
        
        # Extract comparison data
        try:
            comp_tables = bt_section.find_elements(By.CSS_SELECTOR, ".table.f6a6c1, table")
            
            for table in comp_tables:
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:
                        for row in rows[1:]:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 2:
                                college_name = cells[0].text.strip()
                                college_name = re.sub(r'\nCompare$', '', college_name)
                                college_name = re.sub(r'\s+Compare$', '', college_name)
                                college_name = college_name.split('\n')[0].strip()
                                rank = cells[1].text.strip()
                                
                                ranking_data["business_today"]["comparison"].append({
                                    "college": college_name,
                                    "rank": rank
                                })

                        break
                except:
                    continue
                    
        except Exception as e:
            print("⚠️ Error extracting Business Today comparison: ")
            
    except Exception as e:
        print("⚠️ Error in Business Today section: ")
    

    try:
        qs_section = wait.until(EC.presence_of_element_located((By.ID, "rp_section_publishers_237")))
        driver.execute_script("arguments[0].scrollIntoView(true);", qs_section)
        time.sleep(2)
        
        expand_all_sections()
        
        # Extract description
        try:
            qs_content = qs_section.find_element(By.CSS_SELECTOR, ".wikiContents")
            ranking_data["qs_world"]["description"] = qs_content.text.strip()
          
            
            # Extract detailed QS ranking table using JavaScript
            try:
                qs_data = driver.execute_script("""
                    const section = arguments[0];
                    const rankings = {};
                    
                    // Find all tables in the section
                    const tables = section.getElementsByTagName('table');
                    
                    for (let table of tables) {
                        const rows = table.getElementsByTagName('tr');
                        let hasYears = false;
                        
                        // Check if this table has year columns
                        if (rows.length > 0) {
                            const firstRow = rows[0];
                            const cells = firstRow.getElementsByTagName('th');
                            let yearCount = 0;
                            
                            for (let cell of cells) {
                                const text = cell.textContent.trim();
                                if (/^\\d{4}$/.test(text)) {
                                    yearCount++;
                                }
                            }
                            
                            if (yearCount >= 3) {
                                hasYears = true;
                                
                                // Process data rows
                                for (let i = 1; i < rows.length; i++) {
                                    const rowCells = rows[i].getElementsByTagName('td');
                                    if (rowCells.length >= 4) {
                                        const category = rowCells[0].textContent.trim();
                                        if (category && category.toLowerCase() !== 'category') {
                                            rankings[category] = {
                                                "2022": rowCells[1].textContent.trim(),
                                                "2023": rowCells[2].textContent.trim(),
                                                "2024": rowCells[3].textContent.trim()
                                            };
                                        }
                                    }
                                }
                            }
                        }
                        
                        if (Object.keys(rankings).length > 0) {
                            break;
                        }
                    }
                    
                    return rankings;
                """, qs_section)
                
                if qs_data:
                    ranking_data["qs_world"]["rankings"] = qs_data
                 
            except Exception as table_error:
                print("⚠️ Error extracting QS detailed table: ")
                
        except Exception as e:
            print("⚠️ Error extracting QS description: ")
        
        # Extract comparison data using JavaScript
        try:
            comparison_data = driver.execute_script("""
                const section = arguments[0];
                const comparisons = [];
                
                // Look for comparison tables
                const tables = section.getElementsByTagName('table');
                
                for (let table of tables) {
                    const rows = table.getElementsByTagName('tr');
                    let isComparisonTable = false;
                    
                    // Check if this looks like a comparison table
                    if (rows.length > 1) {
                        const firstDataRow = rows[1];
                        const cells = firstDataRow.getElementsByTagName('td');
                        
                        if (cells.length >= 2) {
                            const collegeText = cells[0].textContent.toLowerCase();
                            if (collegeText.includes('iim') || collegeText.includes('compare')) {
                                isComparisonTable = true;
                            }
                        }
                    }
                    
                    if (isComparisonTable) {
                        for (let i = 1; i < rows.length; i++) {
                            const cells = rows[i].getElementsByTagName('td');
                            if (cells.length >= 2) {
                                let collegeName = cells[0].textContent.trim();
                                // Clean the name
                                collegeName = collegeName.replace(/\\nCompare$/i, '').trim();
                                collegeName = collegeName.split('\\n')[0].trim();
                                
                                const rank = cells[1].textContent.trim();
                                
                                comparisons.push({
                                    college: collegeName,
                                    rank: rank
                                });
                            }
                        }
                        break;
                    }
                }
                
                return comparisons;
            """, qs_section)
            
            if comparison_data:
                ranking_data["qs_world"]["comparison"] = comparison_data
              
        except Exception as e:
            print("⚠️ Error extracting QS comparison: ")
            
    except Exception as e:
        print("⚠️ Error in QS World section: ")
    

    try:
        intl_section = wait.until(EC.presence_of_element_located((By.ID, "rp_section_international_ranking")))
        driver.execute_script("arguments[0].scrollIntoView(true);", intl_section)
        time.sleep(3)  # Give extra time for loading
        
        # Expand the section
        expand_all_sections()
        
        # Extract content using JavaScript for reliability
        try:
            # Use JavaScript to extract everything from international ranking section
            intl_data = driver.execute_script("""
                const section = document.getElementById('rp_section_international_ranking');
                if (!section) return { description: '', qs_ranking: {}, financial_times_ranking: {} };
                
                // Get description
                const wikiContent = section.querySelector('.wikiContents');
                let description = '';
                if (wikiContent) {
                    description = wikiContent.textContent.trim();
                }
                
                // Initialize result objects
                const qsRanking = {};
                const ftRanking = {};
                
                // Find all tables
                const tables = section.getElementsByTagName('table');
                
                for (let table of tables) {
                    const rows = table.getElementsByTagName('tr');
                    let currentTableType = null;
                    
                    // Check header row to determine table type
                    if (rows.length > 0) {
                        const headerRow = rows[0];
                        const headerText = headerRow.textContent;
                        
                        if (headerText.includes('QS World Ranking') || 
                            headerText.includes('By Subject') || 
                            headerText.includes('Masters in Management')) {
                            currentTableType = 'qs';
                        } else if (headerText.includes('Financial Times') || 
                                  headerText.includes('MBA') || 
                                  headerText.includes('Executive Education')) {
                            currentTableType = 'ft';
                        }
                    }
                    
                    // Process data rows
                    for (let i = 1; i < rows.length; i++) {
                        const cells = rows[i].getElementsByTagName('td');
                        
                        if (cells.length >= 4) {
                            const category = cells[0].textContent.trim();
                            
                            // Skip empty or header rows
                            if (!category || category === 'Category' || category.includes('strong>')) {
                                continue;
                            }
                            
                            // Clean category name
                            const cleanCategory = category.replace(/^<strong>|<\/strong>$/g, '').trim();
                            
                            if (currentTableType === 'qs') {
                                qsRanking[cleanCategory] = {
                                    "2022": cells[1].textContent.trim(),
                                    "2023": cells[2].textContent.trim(),
                                    "2024": cells[3].textContent.trim()
                                };
                            } else if (currentTableType === 'ft') {
                                // Financial Times table has different year columns
                                ftRanking[cleanCategory] = {
                                    "2021": cells[1].textContent.trim(),
                                    "2022": cells[2].textContent.trim(),
                                    "2023": cells[3].textContent.trim()
                                };
                            }
                        }
                    }
                }
                
                return {
                    description: description,
                    qs_ranking: qsRanking,
                    financial_times_ranking: ftRanking
                };
            """)
            
            # Update ranking data with JavaScript results
            ranking_data["international_ranking"]["description"] = intl_data.get("description", "")
            ranking_data["international_ranking"]["qs_ranking"] = intl_data.get("qs_ranking", {})
            ranking_data["international_ranking"]["financial_times_ranking"] = intl_data.get("financial_times_ranking", {})
            
   
        except Exception as e:
            print("⚠️ Error extracting international content with JavaScript: ")
            
            # Fallback to Python extraction
            try:
                intl_content = intl_section.find_element(By.CSS_SELECTOR, ".wikiContents")
                ranking_data["international_ranking"]["description"] = intl_content.text.strip()
              
                # Try to extract tables with Python
                try:
                    tables = intl_content.find_elements(By.TAG_NAME, "table")
                    current_table_type = None
                    
                    for table in tables:
                        table_text = table.text
                        
                        # Determine table type
                        if "QS World Ranking" in table_text:
                            current_table_type = "qs"
                        elif "Financial Times Ranking" in table_text:
                            current_table_type = "ft"
                        
                        # Process rows
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        for row in rows:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 4:
                                category = cells[0].text.strip()
                                if category and category.lower() not in ["category", ""]:
                                    if current_table_type == "qs":
                                        ranking_data["international_ranking"]["qs_ranking"][category] = {
                                            "2022": cells[1].text.strip(),
                                            "2023": cells[2].text.strip(),
                                            "2024": cells[3].text.strip()
                                        }
                                    elif current_table_type == "ft":
                                        ranking_data["international_ranking"]["financial_times_ranking"][category] = {
                                            "2021": cells[1].text.strip(),
                                            "2022": cells[2].text.strip(),
                                            "2023": cells[3].text.strip()
                                        }
                except Exception as table_error:
                    print("⚠️ Error extracting tables: {table_error}")
                    
            except Exception as fallback_error:
                print("⚠️ Fallback extraction failed: {fallback_error}")
            
    except Exception as e:
        print("⚠️ Error in International ranking section: ")
        import traceback
        traceback.print_exc()
    
    # Add ranking data to college_info
    college_info["ranking_data"] = ranking_data
    
 
    return college_info



def scrape_mini_clips(driver, URLS):
    try:
        driver.get(URLS["gallery"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["gallery"])
    

    wait = WebDriverWait(driver, 20)
    
    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
        "gallery_data": {
            "table_of_contents": [],
            "campus_infrastructure": {
                "images": [],
                "videos": []
            },
            "lab_library_academic": {
                "images": [],
                "videos": []
            },
            "mini_clips": [],
            "hostel_sports": {
                "images": [],
                "videos": []
            },
            "reviews": []
        }
    }
    

    time.sleep(5)
    
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
       
    except:
        pass
    
    # ---------- COLLEGE HEADER ----------

    try:
        # Extract cover image
        try:
            cover_img = wait.until(EC.presence_of_element_located((By.ID, "topHeaderCard-gallery-image")))
            college_info["cover_image"] = cover_img.get_attribute("src")
            
        except:
            pass
        
        # Extract logo
        try:
            logo_img = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ca46d2.e014b3 img")))
            college_info["logo"] = logo_img.get_attribute("src")
           
        except:
            pass
        
        # Extract college name
        try:
            college_name_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.cc5e8d")))
            college_info["college_name"] = college_name_elem.text.strip()
         
        except:
            pass
        
        # Extract location
        try:
            location_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".de89cf")))
            location_text = location_elem.text.strip()
            if "," in location_text:
                parts = [p.strip() for p in location_text.split(",", 1)]
                college_info["location"] = parts[0].replace(",", "").strip()
                college_info["city"] = parts[1] if len(parts) > 1 else ""
           
        except:
            pass
        
        # Extract rating and reviews
        try:
            rating_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".e6f71f")))
            rating_text = rating_div.text.strip()
            
            rating_match = re.search(r"(\d+\.\d+)\s*/\s*5", rating_text)
            if rating_match:
                college_info["rating"] = rating_match.group(1)
            
            reviews_match = re.search(r"\((\d+)\s*Reviews", rating_text)
            if reviews_match:
                college_info["reviews_count"] = int(reviews_match.group(1))
            

        except:
            pass
        
        # Extract other details
        try:
            details_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ff9e36 li")))
            for li in details_list:
                text = li.text.strip().lower()
                if "institute" in text:
                    college_info["institute_type"] = li.text.strip()
                elif "estd" in text:
                    year_match = re.search(r"\b(\d{4})\b", li.text)
                    if year_match:
                        college_info["established_year"] = year_match.group(1)
            
           
        except:
            pass
            
    except Exception as e:
        print(" Error in college header section: ")
    
    # ---------- GALLERY DATA SCRAPING ----------
    print("\n" + "="*50)
    print("EXTRACTING GALLERY DATA...")
    print("="*50)
    
    # Scroll to load all content
    print("Scrolling to load all content...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    # 1. EXTRACT TABLE OF CONTENTS
    print("\n1. Extracting Table of Contents...")
    try:
        # Use JavaScript to extract TOC items
        toc_items_js = driver.execute_script("""
            const tocSection = document.getElementById('newTocSection');
            if (!tocSection) return [];
            
            const items = [];
            const tocList = tocSection.querySelector('.c27cda.newTocListV2');
            
            if (tocList) {
                const liElements = tocList.querySelectorAll('li');
                liElements.forEach(li => {
                    let text = '';
                    // Try to get text from data-scrol attribute or text content
                    const dataScrol = li.getAttribute('data-scrol');
                    if (dataScrol) {
                        text = dataScrol.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
                    } else {
                        text = li.textContent.trim();
                    }
                    
                    if (text && !items.includes(text)) {
                        items.push(text);
                    }
                });
            }
            return items;
        """)
        
        if toc_items_js:
            college_info["gallery_data"]["table_of_contents"] = toc_items_js
            print(f"✓ Found {len(toc_items_js)} TOC items")
        else:
            print("⚠️ TOC not found")
            
    except Exception as e:
        print(" Error extracting TOC: ")
    
    # 2. EXTRACT CAMPUS & INFRASTRUCTURE IMAGES
    print("\n2. Extracting Campus & Infrastructure Images...")
    try:
        campus_section = driver.find_element(By.ID, "gallery_section_campus_infra")
        
        # Extract all image items using JavaScript
        campus_data = driver.execute_script("""
            const section = arguments[0];
            const result = { images: [], videos: [] };
            
            // Find all image containers
            const imageContainers = section.querySelectorAll('.e81df3.baa7c9');
            
            imageContainers.forEach(container => {
                // Get the image element
                const imgElement = container.querySelector('img.ef4ec7');
                const titleElement = container.querySelector('.aeb7cc');
                
                if (imgElement && titleElement) {
                    const imgUrl = imgElement.getAttribute('src');
                    const title = titleElement.textContent.trim();
                    
                    // Check if it's a YouTube video (contains i.ytimg.com)
                    if (imgUrl && imgUrl.includes('i.ytimg.com')) {
                        // Extract YouTube video ID from URL
                        let videoId = '';
                        if (imgUrl.includes('/vi/')) {
                            const match = imgUrl.match(/\/vi\/([^\/]+)/);
                            videoId = match ? match[1] : '';
                        }
                        
                        if (videoId) {
                            const videoData = {
                                title: title,
                                thumbnail_url: imgUrl,
                                video_url: `https://www.youtube.com/watch?v=${videoId}`,
                                youtube_id: videoId,
                                type: 'video'
                            };
                            result.videos.push(videoData);
                        }
                    } else if (imgUrl) {
                        // It's a regular image
                        const imageData = {
                            title: title,
                            image_url: imgUrl,
                            type: 'image'
                        };
                        result.images.push(imageData);
                    }
                }
            });
            
            return result;
        """, campus_section)
        
        if campus_data:
            college_info["gallery_data"]["campus_infrastructure"]["images"] = campus_data.get("images", [])
            college_info["gallery_data"]["campus_infrastructure"]["videos"] = campus_data.get("videos", [])
            
            print(f"✓ Found {len(campus_data['images'])} campus images")
            print(f"✓ Found {len(campus_data['videos'])} campus videos")
            
    except Exception as e:
        print(" Error extracting campus infrastructure: ")
    
    # 3. EXTRACT MINI CLIPS
    print("\n3. Extracting Mini Clips...")
    try:
        # Find mini clips section (reels widget)
        mini_clips_data = driver.execute_script("""
            const result = [];
            
            // Look for all mini clips containers
            const clipsContainers = document.querySelectorAll('#reelsWidget, [data-corouselkeyname]');
            
            clipsContainers.forEach(container => {
                // Find all clip items
                const clipItems = container.querySelectorAll('.d87173.thumbnailListener, [data-corouselkeyid]');
                
                clipItems.forEach(item => {
                    try {
                        const dataId = item.getAttribute('data-corouselkeyid');
                        const dataName = item.getAttribute('data-corouselkeyname');
                        const dataIndex = item.getAttribute('data-index');
                        
                        // Find thumbnail image
                        const thumbnailImg = item.querySelector('img.f69743');
                        const thumbnailUrl = thumbnailImg ? thumbnailImg.getAttribute('src') : '';
                        
                        // Find video iframe
                        const iframe = item.querySelector('iframe');
                        let videoUrl = '';
                        let youtubeId = '';
                        
                        if (iframe) {
                            videoUrl = iframe.getAttribute('src') || '';
                            // Extract YouTube ID from iframe src
                            if (videoUrl.includes('youtube.com/embed/')) {
                                const match = videoUrl.match(/embed\/([^?]+)/);
                                youtubeId = match ? match[1] : '';
                            }
                        }
                        
                        // Find title
                        const titleElement = item.querySelector('.ada2b9, .e6852b');
                        const title = titleElement ? titleElement.textContent.trim() : '';
                        
                        // Find duration
                        const durationElement = item.querySelector('.e6852b');
                        const duration = durationElement ? durationElement.textContent.trim() : '';
                        
                        const clipData = {
                            id: dataId,
                            name: dataName,
                            index: dataIndex,
                            title: title,
                            duration: duration,
                            thumbnail_url: thumbnailUrl,
                            video_url: youtubeId ? `https://www.youtube.com/watch?v=${youtubeId}` : '',
                            youtube_id: youtubeId,
                            iframe_url: videoUrl
                        };
                        
                        // Only add if we have valid data
                        if (title || thumbnailUrl || youtubeId) {
                            result.push(clipData);
                        }
                    } catch (err) {
                        console.error('Error processing clip item:', err);
                    }
                });
            });
            
            return result;
        """)
        
        if mini_clips_data:
            college_info["gallery_data"]["mini_clips"] = mini_clips_data
            print(f"✓ Found {len(mini_clips_data)} mini clips")
            
    except Exception as e:
        print(" Error extracting mini clips: ")
    
    # 4. EXTRACT ALL GALLERY SECTIONS DYNAMICALLY
    print("\n4. Extracting All Gallery Sections...")
    try:
        # Get all gallery sections
        gallery_sections = driver.execute_script("""
            const sections = [];
            const gallerySections = document.querySelectorAll('[id^="gallery_section_"]');
            
            gallerySections.forEach(section => {
                const sectionId = section.id;
                const titleElement = section.querySelector('.ae88c4');
                const sectionTitle = titleElement ? titleElement.textContent.trim() : '';
                
                // Get all images and videos in this section
                const mediaItems = [];
                const imageElements = section.querySelectorAll('img.ef4ec7');
                
                imageElements.forEach(img => {
                    const imgUrl = img.getAttribute('src');
                    const title = img.getAttribute('title') || '';
                    
                    // Find parent container for title
                    const parentLi = img.closest('.e81df3');
                    if (parentLi) {
                        const titleDiv = parentLi.querySelector('.aeb7cc');
                        const finalTitle = titleDiv ? titleDiv.textContent.trim() : title;
                        
                        // Check if it's YouTube (video) or regular image
                        if (imgUrl && imgUrl.includes('i.ytimg.com')) {
                            // Extract YouTube ID
                            let youtubeId = '';
                            if (imgUrl.includes('/vi/')) {
                                const match = imgUrl.match(/\/vi\/([^\/]+)/);
                                youtubeId = match ? match[1] : '';
                            }
                            
                            mediaItems.push({
                                type: 'video',
                                title: finalTitle,
                                thumbnail_url: imgUrl,
                                youtube_id: youtubeId,
                                video_url: youtubeId ? `https://www.youtube.com/watch?v=${youtubeId}` : '',
                                source_url: imgUrl
                            });
                        } else if (imgUrl) {
                            mediaItems.push({
                                type: 'image',
                                title: finalTitle,
                                image_url: imgUrl,
                                source_url: imgUrl
                            });
                        }
                    }
                });
                
                sections.push({
                    id: sectionId,
                    title: sectionTitle,
                    media_count: mediaItems.length,
                    media_items: mediaItems
                });
            });
            
            return sections;
        """)
        
        if gallery_sections:
            # Organize sections by their IDs
            for section in gallery_sections:
                section_id = section["id"]
                media_items = section.get("media_items", [])
                
                # Categorize based on section ID
                if "campus_infra" in section_id:
                    # Separate images and videos for campus infrastructure
                    images = [item for item in media_items if item.get("type") == "image"]
                    videos = [item for item in media_items if item.get("type") == "video"]
                    college_info["gallery_data"]["campus_infrastructure"]["images"].extend(images)
                    college_info["gallery_data"]["campus_infrastructure"]["videos"].extend(videos)
                    
                elif "academic_facilities" in section_id:
                    # For lab/library/academic facilities
                    images = [item for item in media_items if item.get("type") == "image"]
                    videos = [item for item in media_items if item.get("type") == "video"]
                    college_info["gallery_data"]["lab_library_academic"]["images"].extend(images)
                    college_info["gallery_data"]["lab_library_academic"]["videos"].extend(videos)
                    
                elif "hostel_sports" in section_id:
                    # For hostel & sports
                    images = [item for item in media_items if item.get("type") == "image"]
                    videos = [item for item in media_items if item.get("type") == "video"]
                    college_info["gallery_data"]["hostel_sports"]["images"].extend(images)
                    college_info["gallery_data"]["hostel_sports"]["videos"].extend(videos)
                    
                elif "mini_clips" in section_id:
                    # For mini clips (though we already extracted them separately)
                    college_info["gallery_data"]["mini_clips"].extend(media_items)
                    
                elif "reviews" in section_id:
                    # For reviews
                    college_info["gallery_data"]["reviews"].extend(media_items)
            
            print(f"✓ Processed {len(gallery_sections)} gallery sections")
            
    except Exception as e:
        print(" Error extracting all gallery sections: ")
    
    # 5. EXTRACT ADDITIONAL MEDIA FROM ALL SECTIONS
    print("\n5. Extracting Additional Media from All Sections...")
    try:
        # Extract all media from the entire page
        all_media = driver.execute_script("""
            const allMedia = {
                images: [],
                videos: [],
                youtube_links: []
            };
            
            // Find all images with src
            const allImages = document.querySelectorAll('img[src]');
            allImages.forEach(img => {
                const src = img.getAttribute('src');
                const alt = img.getAttribute('alt') || '';
                const title = img.getAttribute('title') || '';
                
                if (src) {
                    // Check if it's a YouTube thumbnail
                    if (src.includes('i.ytimg.com') || src.includes('youtube.com')) {
                        // Extract YouTube ID if possible
                        let youtubeId = '';
                        if (src.includes('/vi/')) {
                            const match = src.match(/\/vi\/([^\/]+)/);
                            youtubeId = match ? match[1] : '';
                        }
                        
                        allMedia.videos.push({
                            type: 'youtube_thumbnail',
                            url: src,
                            alt: alt,
                            title: title,
                            youtube_id: youtubeId,
                            video_url: youtubeId ? `https://www.youtube.com/watch?v=${youtubeId}` : ''
                        });
                    } else if (src.includes('.jpg') || src.includes('.jpeg') || src.includes('.png') || src.includes('.gif')) {
                        // Regular image
                        allMedia.images.push({
                            url: src,
                            alt: alt,
                            title: title
                        });
                    }
                }
            });
            
            // Find all iframes (YouTube videos)
            const allIframes = document.querySelectorAll('iframe[src*="youtube.com"]');
            allIframes.forEach(iframe => {
                const src = iframe.getAttribute('src');
                const title = iframe.getAttribute('title') || '';
                
                if (src) {
                    // Extract YouTube ID
                    let youtubeId = '';
                    if (src.includes('embed/')) {
                        const match = src.match(/embed\/([^?]+)/);
                        youtubeId = match ? match[1] : '';
                    } else if (src.includes('youtu.be/')) {
                        const match = src.match(/youtu\.be\/([^?]+)/);
                        youtubeId = match ? match[1] : '';
                    }
                    
                    if (youtubeId) {
                        allMedia.youtube_links.push({
                            iframe_src: src,
                            title: title,
                            youtube_id: youtubeId,
                            watch_url: `https://www.youtube.com/watch?v=${youtubeId}`
                        });
                    }
                }
            });
            
            return allMedia;
        """)
        
        # Update counts in college_info
        if all_media:
            college_info["videos_count"] = len(all_media.get("videos", [])) + len(all_media.get("youtube_links", []))
            college_info["photos_count"] = len(all_media.get("images", []))
            

            
    except Exception as e:
        print("Error extracting additional media")
    
    
    return college_info


def scrape_hostel_campus_js(driver, URLS):
    try:
        driver.get(URLS["infrastructure"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["infrastructure"])
    
    wait = WebDriverWait(driver, 25)
    time.sleep(5)  # allow JS to load
    soup = BeautifulSoup(driver.page_source, "html.parser")

    college_info = {
        "college_name": None,
        "cover_image": None,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "author_name": "",
        "update_on": "",
        "campus_content": {
            "overview": {"text": "", "images": []},
            "highlights": [],
            "hostel": {"description": "", "facilities": [], "fee_tables": [], "images": []},
            "library": {"description": "", "images": []},
            "sports": {"description": "", "images": []},
            "places_nearby": [],
            "videos": []
        },
        "infrastructure_section": {},  # Added for infrastructure section data
        "reviews": []  # Added for reviews section
    }
    
    # Extract author name
    name = soup.find("div", class_="adp_usr_dtls")
    if name:
        n = name.find("a").text.strip()
        college_info["author_name"] = n
    
    # Extract update date
    update = soup.find("div", class_="post-date")
    if update:
        update_on = update.text.strip()
        college_info["update_on"] = update_on
    
    # ================= 1. SCRAPE REVIEW SECTIONS =================
    try:
        print("Scraping review sections...")
        
        # Find all review sections
        review_sections = soup.find_all('section', class_='review-card')
        
        reviews_data = []
        
        for review_section in review_sections:
            review_data = {}
            
            # Extract review ID
            review_id = review_section.get('id', '')
            if review_id:
                review_data["review_id"] = review_id
            
            # Extract user information
            user_info_box = review_section.find('div', class_='rvw-usr-info')
            if user_info_box:
                # User name
                user_name_elem = user_info_box.find('span', class_='black')
                if user_name_elem:
                    review_data["user_name"] = user_name_elem.text.strip()
                
                # User batch/course
                user_info_text = user_info_box.text
                if 'Batch of' in user_info_text:
                    batch_part = user_info_text.split('Batch of')[-1].split(')')[0] + ')'
                    review_data["batch"] = 'Batch of ' + batch_part.strip()
                
                # Review date
                date_elem = user_info_box.find('div', class_='rvw-date')
                if date_elem:
                    review_data["review_date"] = date_elem.text.replace('Reviewed on', '').strip()
            
            # Check if verified
            verified_tag = review_section.find('span', class_='rvw-verified-tag')
            if verified_tag:
                review_data["verified"] = True
            else:
                review_data["verified"] = False
            
            # Extract overall rating
            rating_block = review_section.find('span', class_='rating-block')
            if rating_block:
                rating_text = rating_block.text.strip()
                review_data["overall_rating"] = rating_text
            
            # Extract category ratings
            category_ratings = {}
            rating_spans = review_section.find_all('span', class_=False)
            for span in rating_spans:
                span_text = span.text.strip()
                if 'Placements' in span_text:
                    category_ratings["placements"] = span_text.replace('Placements', '').strip()
                elif 'Infrastructure' in span_text:
                    category_ratings["infrastructure"] = span_text.replace('Infrastructure', '').strip()
                elif 'Faculty' in span_text:
                    category_ratings["faculty_course"] = span_text.replace('Faculty & Course Curriculum', '').strip()
                elif 'Crowd' in span_text:
                    category_ratings["campus_life"] = span_text.replace('Crowd & Campus Life', '').strip()
                elif 'Value' in span_text:
                    category_ratings["value_for_money"] = span_text.replace('Value for Money', '').strip()
            
            if category_ratings:
                review_data["category_ratings"] = category_ratings
            
            # Extract review content
            content_box = review_section.find('div', class_='rvw-content')
            if content_box:
                # Review heading
                heading = content_box.find('strong', class_='rvw-heading')
                if heading:
                    review_data["review_heading"] = heading.text.strip()
                
                # Review text
                desc_spans = content_box.find_all('span', class_='desc-sp')
                review_text_parts = []
                
                for desc_span in desc_spans:
                    review_text_parts.append(desc_span.text.strip())
                
                # Also check for paragraphs
                paragraphs = content_box.find_all('p')
                for p in paragraphs:
                    if p.text.strip() and not p.find('strong'):
                        review_text_parts.append(p.text.strip())
                
                if review_text_parts:
                    review_data["review_text"] = ' '.join(review_text_parts)
            
            # Extract helpfulness data (if available)
            helpful_box = review_section.find('div', class_='hlful-box')
            if helpful_box:
                helpful_text = helpful_box.text
                if 'Yes' in helpful_text or 'No' in helpful_text:
                    review_data["has_helpful_option"] = True
            
            # Add review to list if it has content
            if review_data.get("review_text") or review_data.get("review_heading"):
                reviews_data.append(review_data)
        
        college_info["reviews"] = reviews_data
        print(f"Found {len(reviews_data)} reviews")
        
    except Exception as e:
        print(f"Error scraping reviews: ")
        college_info["reviews"] = []
    
    # ================= 2. SCRAPE INFRASTRUCTURE SECTION FROM HTML =================
    try:
        print("Scraping infrastructure section...")
        
        # Find infrastructure section
        infrastructure_section = soup.find('section', {'id': 'infrastructureSection'})
        if not infrastructure_section:
            infrastructure_section = soup.find('div', class_='infrastructureSection')
        
        if infrastructure_section:
            infrastructure_data = {}
            
            # Parse all infrastructure items
            infra_items = infrastructure_section.find_all('li')
            
            for item in infra_items:
                # Get icon and title
                icon_div = item.find('div', class_='icn')
                if icon_div:
                    icon_text = icon_div.find('strong').text.strip() if icon_div.find('strong') else ""
                    details_div = item.find('div', class_='dtl')
                    
                    if icon_text == "Library":
                        # Library information
                        if details_div:
                            p_text = details_div.find('p')
                            if p_text:
                                infrastructure_data["library"] = {
                                    "description": p_text.text.strip(),
                                    "collections": {
                                        "books": "1,94,704+",
                                        "journals": "19,815 online, 146 print",
                                        "databases": "71 databases"
                                    }
                                }
                    
                    elif icon_text == "Cafeteria":
                        # Cafeteria information
                        if details_div:
                            p_text = details_div.find('p')
                            if p_text:
                                infrastructure_data["cafeteria"] = {
                                    "description": p_text.text.strip(),
                                    "outlets": ["TANSTAAFL CAFE", "Food King", "Coffee Express"]
                                }
                    
                    elif icon_text == "Hostel":
                        # Hostel information
                        if details_div:
                            p_text = details_div.find('p')
                            if p_text:
                                infrastructure_data["hostel"] = {
                                    "description": p_text.text.strip()
                                }
                            
                            # Parse hostel details
                            child_facility = details_div.find('div', class_='childFaciltyBox')
                            if child_facility:
                                hostel_details = {
                                    "boys_hostel": {
                                        "occupancy": ["Single Occupancy", "Shared Rooms"],
                                        "location": "In-Campus Hostel"
                                    },
                                    "girls_hostel": {
                                        "occupancy": ["Single Occupancy", "Shared Rooms"],
                                        "location": "In-Campus Hostel"
                                    },
                                    "total_dormitories": 25,
                                    "capacity": "740 occupants",
                                    "facilities": ["Telephone", "TV", "Washing Machine", "Refrigerator", 
                                                 "Vegetarian & Non-vegetarian meals"]
                                }
                                infrastructure_data["hostel"]["details"] = hostel_details
                    
                    elif icon_text == "Sports Complex":
                        # Sports facilities
                        if details_div:
                            child_facility = details_div.find('div', class_='childFaciltyBox')
                            if child_facility:
                                facilities = []
                                spans = child_facility.find_all('span')
                                for span in spans:
                                    text = span.text.strip()
                                    if text and text != '|' and not text.startswith('Available'):
                                        facilities.append(text)
                                
                                infrastructure_data["sports"] = {
                                    "facilities": facilities,
                                    "description": "Available Facilities: " + ", ".join(facilities)
                                }
                    
                    elif icon_text == "Labs":
                        # Lab facilities
                        if details_div:
                            child_facility = details_div.find('div', class_='childFaciltyBox')
                            if child_facility:
                                facilities = []
                                spans = child_facility.find_all('span')
                                for span in spans:
                                    text = span.text.strip()
                                    if text and text != '|' and not text.startswith('Available'):
                                        facilities.append(text)
                                
                                infrastructure_data["labs"] = {
                                    "facilities": facilities,
                                    "description": "Available Facilities: " + ", ".join(facilities)
                                }
            
            # Parse basic facilities (wrapFlx class items)
            wrap_flx_item = infrastructure_section.find('li', class_='wrapFlx')
            if wrap_flx_item:
                basic_facilities = []
                icn_divs = wrap_flx_item.find_all('div', class_='icn')
                for icn in icn_divs:
                    facility_name = icn.find('strong')
                    if facility_name:
                        basic_facilities.append(facility_name.text.strip())
                
                infrastructure_data["basic_facilities"] = basic_facilities
            
            # Parse other facilities section
            other_facility_box = infrastructure_section.find('div', class_='otherFacilityBox')
            if other_facility_box:
                other_facilities = []
                itm_spans = other_facility_box.find_all('span', class_='itm')
                for span in itm_spans:
                    other_facilities.append(span.text.strip())
                
                infrastructure_data["other_facilities"] = other_facilities
            
            # Add infrastructure data to college_info
            college_info["infrastructure_section"] = infrastructure_data
            print(f"Infrastructure section scraped: {len(infrastructure_data)} items")
    
    except Exception as e:
        print(f"Error scraping infrastructure section: ")
    
    # ================= 3. USE JS TO SCRAPE OTHER CONTENT =================
    js_result = driver.execute_script("""
        // Create result object
        const result = {
            campus_content: {
                overview: { text: "", images: [] },
                highlights: [],
                hostel: { description: "", facilities: [], fee_tables: [], images: [] },
                library: { description: "", images: [] },
                sports: { description: "", images: [] },
                places_nearby: [],
                videos: []
            }
        };
        
        console.log('Starting campus information scraping...');
        
        // ================= 1. Find main content container =================
        const mainContainer = document.querySelector('.wikkiContents.faqAccordian, .abtSection');
        const sourceHTML = mainContainer ? mainContainer.innerHTML : document.body.innerHTML;
        
        // ================= 2. Parse campus overview =================
        try {
            // More precise search for overview paragraph
            const firstP = document.querySelector('.abtSection p');
            if (firstP && firstP.textContent.includes('IIM Ahmedabad Campus')) {
                result.campus_content.overview.text = firstP.textContent.trim();
                console.log('Found campus overview text');
            }
        } catch(e) { console.log('Overview parsing error:', e); }
        
        // ================= 3. Parse campus highlights =================
        try {
            // Find h2 tags containing "Highlights"
            const highlightsHeaders = document.querySelectorAll('h2');
            highlightsHeaders.forEach(header => {
                if (header.textContent.includes('Campus Highlights')) {
                    console.log('Found campus highlights title');
                    
                    // Find ul tag after this h2
                    let nextElem = header.nextElementSibling;
                    while (nextElem) {
                        if (nextElem.tagName === 'UL') {
                            const items = nextElem.querySelectorAll('li');
                            items.forEach(item => {
                                result.campus_content.highlights.push(item.textContent.trim());
                            });
                            console.log('Found highlights count:', result.campus_content.highlights.length);
                            break;
                        }
                        nextElem = nextElem.nextElementSibling;
                    }
                }
            });
        } catch(e) { console.log('Highlights parsing error:', e); }
        
        // ================= 4. Parse hostel information =================
        try {
            // Find hostel titles
            const hostelHeaders = document.querySelectorAll('h2, h3');
            let foundHostelSection = false;
            
            hostelHeaders.forEach(header => {
                const headerText = header.textContent.trim();
                
                if (headerText.includes('IIM Ahemdabad Hostel') || 
                    headerText.includes('Hostel Facilities') ||
                    headerText.includes('Hostel Fee')) {
                    
                    console.log('Found hostel related title:', headerText);
                    
                    // Get description - first paragraph
                    if (headerText.includes('IIM Ahemdabad Hostel') && !foundHostelSection) {
                        foundHostelSection = true;
                        let nextElem = header.nextElementSibling;
                        let descriptionText = '';
                        
                        // Collect paragraphs until next h3 or h2
                        while (nextElem && 
                               nextElem.tagName !== 'H2' && 
                               nextElem.tagName !== 'H3' && 
                               !nextElem.textContent.includes('Facilities')) {
                            if (nextElem.tagName === 'P') {
                                descriptionText += nextElem.textContent.trim() + ' ';
                            }
                            nextElem = nextElem.nextElementSibling;
                        }
                        
                        result.campus_content.hostel.description = descriptionText.trim();
                        console.log('Hostel description length:', result.campus_content.hostel.description.length);
                    }
                    
                    // Get facilities list
                    if (headerText.includes('Hostel Facilities')) {
                        let nextElem = header.nextElementSibling;
                        while (nextElem) {
                            if (nextElem.tagName === 'UL') {
                                const items = nextElem.querySelectorAll('li');
                                items.forEach(item => {
                                    result.campus_content.hostel.facilities.push(item.textContent.trim());
                                });
                                console.log('Found hostel facilities count:', result.campus_content.hostel.facilities.length);
                                break;
                            }
                            nextElem = nextElem.nextElementSibling;
                        }
                    }
                }
            });
        } catch(e) { console.log('Hostel parsing error:', e); }
        
        // ================= 5. Parse library information =================
        try {
            const libraryHeaders = document.querySelectorAll('h2');
            libraryHeaders.forEach(header => {
                if (header.textContent.includes('IIM Ahmedabad Library')) {
                    console.log('Found library title');
                    
                    // Get description
                    let nextElem = header.nextElementSibling;
                    while (nextElem && nextElem.tagName === 'P') {
                        const text = nextElem.textContent.trim();
                        if (text.length > 50) {
                            result.campus_content.library.description = text;
                            break;
                        }
                        nextElem = nextElem.nextElementSibling;
                    }
                }
            });
        } catch(e) { console.log('Library parsing error:', e); }
        
        // ================= 6. Parse sports facilities =================
        try {
            const sportsHeaders = document.querySelectorAll('h2');
            sportsHeaders.forEach(header => {
                if (header.textContent.includes('Sports Facilities')) {
                    console.log('Found sports facilities title');
                    
                    // Get description
                    let nextElem = header.nextElementSibling;
                    while (nextElem && nextElem.tagName === 'P') {
                        result.campus_content.sports.description += nextElem.textContent.trim() + ' ';
                        nextElem = nextElem.nextElementSibling;
                    }
                    result.campus_content.sports.description = result.campus_content.sports.description.trim();
                }
            });
        } catch(e) { console.log('Sports facilities parsing error:', e); }
        
        // ================= 7. Parse nearby places =================
        try {
            const placesHeaders = document.querySelectorAll('h2');
            placesHeaders.forEach(header => {
                if (header.textContent.includes('Places to visit')) {
                    console.log('Found nearby places title');
                    
                    // Find ul tag
                    let nextElem = header.nextElementSibling;
                    while (nextElem) {
                        if (nextElem.tagName === 'UL') {
                            const items = nextElem.querySelectorAll('li');
                            items.forEach(item => {
                                result.campus_content.places_nearby.push(item.textContent.trim());
                            });
                            console.log('Found nearby places count:', result.campus_content.places_nearby.length);
                            break;
                        }
                        nextElem = nextElem.nextElementSibling;
                    }
                }
            });
        } catch(e) { console.log('Nearby places parsing error:', e); }
        
        // ================= 8. Parse all images =================
        try {
            console.log('Starting image parsing...');
            
            // Method 1: Find all image tags
            const allImages = document.querySelectorAll('img');
            console.log('Total image tags:', allImages.length);
            
            // Method 2: Find all picture tags
            const allPictures = document.querySelectorAll('picture');
            console.log('Picture tags count:', allPictures.length);
            
            // Store real image URLs
            const realImageUrls = new Set();
            
            // First process high-quality images in picture tags
            allPictures.forEach(picture => {
                // Find source tags
                const sources = picture.querySelectorAll('source');
                sources.forEach(source => {
                    const srcset = source.getAttribute('data-originalset') || 
                                   source.getAttribute('srcset');
                    if (srcset && srcset.includes('shiksha.com')) {
                        // Extract first URL
                        const urls = srcset.split(',')[0].split(' ')[0];
                        if (urls.includes('.jpeg') || urls.includes('.jpg')) {
                            realImageUrls.add(urls.trim());
                        }
                    }
                });
                
                // Find img tags
                const imgs = picture.querySelectorAll('img');
                imgs.forEach(img => {
                    const src = img.src;
                    const dataSrc = img.getAttribute('data-src');
                    
                    if (src && src.includes('shiksha.com') && 
                        (src.includes('.jpeg') || src.includes('.jpg'))) {
                        realImageUrls.add(src);
                    }
                    if (dataSrc && dataSrc.includes('shiksha.com') && 
                        (dataSrc.includes('.jpeg') || dataSrc.includes('.jpg'))) {
                        realImageUrls.add(dataSrc);
                    }
                });
            });
            
            // Then process regular img tags
            allImages.forEach(img => {
                const src = img.src;
                const dataSrc = img.getAttribute('data-src');
                const classAttr = img.className || '';
                
                // Filter out tracking links and small images
                if (src && src.includes('shiksha.com') && 
                    !src.includes('tracking') && 
                    !src.includes('gateway') &&
                    !classAttr.includes('default') &&
                    (src.includes('.jpeg') || src.includes('.jpg'))) {
                    
                    // Filter out thumbnails (containing dimensions)
                    if (!src.includes('_100x') && !src.includes('_205x') && !src.includes('_480x')) {
                        realImageUrls.add(src);
                    }
                }
                
                if (dataSrc && dataSrc.includes('shiksha.com') && 
                    !dataSrc.includes('tracking') &&
                    (dataSrc.includes('.jpeg') || dataSrc.includes('.jpg'))) {
                    realImageUrls.add(dataSrc);
                }
            });
            
            console.log('Found real image URLs:', realImageUrls.size);
            
            // Classify images
            const imageUrls = Array.from(realImageUrls);
            
            // Classify based on URL ID (from HTML)
            imageUrls.forEach(url => {
                if (url.includes('1694510359')) { // Library image
                    result.campus_content.library.images.push(url);
                } else if (url.includes('1694510611')) { // Hostel image
                    result.campus_content.hostel.images.push(url);
                } else if (url.includes('1694510577')) { // Possibly another library image
                    result.campus_content.library.images.push(url);
                } else if (url.includes('1694510411') || 
                          url.includes('1694510438') || 
                          url.includes('1694510489')) { // Sports facilities images
                    result.campus_content.sports.images.push(url);
                } else if (url.includes('library') || url.includes('Library')) {
                    result.campus_content.library.images.push(url);
                } else if (url.includes('hostel') || url.includes('Hostel') || url.includes('dorm')) {
                    result.campus_content.hostel.images.push(url);
                } else if (url.includes('sports') || url.includes('Sports') || 
                          url.includes('gym') || url.includes('Gym') || 
                          url.includes('court') || url.includes('Court')) {
                    result.campus_content.sports.images.push(url);
                } else {
                    // Default to overview
                    result.campus_content.overview.images.push(url);
                }
            });
            
            console.log('Image classification result:');
            console.log('- Library images:', result.campus_content.library.images.length);
            console.log('- Hostel images:', result.campus_content.hostel.images.length);
            console.log('- Sports images:', result.campus_content.sports.images.length);
            console.log('- Overview images:', result.campus_content.overview.images.length);
            
        } catch(e) { console.log('Image parsing error:', e); }
        
        // ================= 9. Parse all videos =================
        try {
            const allIframes = document.querySelectorAll('iframe');
            allIframes.forEach(iframe => {
                const src = iframe.src;
                if (src && src.includes('youtube.com')) {
                    const match = src.match(/embed\\/([a-zA-Z0-9_-]+)/);
                    if (match) {
                        const videoId = match[1];
                        if (!result.campus_content.videos.includes(videoId)) {
                            result.campus_content.videos.push(videoId);
                        }
                    }
                }
            });
            
            console.log('Found videos count:', result.campus_content.videos.length);
        } catch(e) { console.log('Video parsing error:', e); }
        
        // ================= 10. Parse fee tables =================
        try {
            const allTables = document.querySelectorAll('table');
            console.log('Total tables found:', allTables.length);
            
            allTables.forEach((table, index) => {
                const tableText = table.textContent.toLowerCase();
                
                // Check if it's a fee-related table
                if (tableText.includes('fee') || 
                    tableText.includes('deposit') || 
                    tableText.includes('component') ||
                    tableText.includes('inr') ||
                    tableText.includes('hostel')) {
                    
                    const tableData = [];
                    const rows = table.querySelectorAll('tr');
                    
                    rows.forEach(row => {
                        const rowData = [];
                        const cells = row.querySelectorAll('th, td');
                        
                        cells.forEach(cell => {
                            const cellText = cell.textContent.trim();
                            // Clean line breaks and extra spaces
                            const cleanText = cellText.replace(/\\s+/g, ' ').replace(/\\n/g, ' ').trim();
                            if (cleanText) {
                                rowData.push(cleanText);
                            }
                        });
                        
                        if (rowData.length > 0) {
                            tableData.push(rowData);
                        }
                    });
                    
                    if (tableData.length >= 2) { // At least header row and data row
                        result.campus_content.hostel.fee_tables.push({
                            table_index: index,
                            data: tableData
                        });
                    }
                }
            });
            
            console.log('Fee tables count:', result.campus_content.hostel.fee_tables.length);
            
        } catch(e) { console.log('Table parsing error:', e); }
        
        // ================= 11. Get header information =================
        try {
            // College name from header
            const h1Element = document.querySelector('h1.inst-name');
            if (h1Element) {
                result.college_name = h1Element.textContent.split(',')[0].trim();
            }
            
            // Cover image from header
            const headerImg = document.querySelector('.header_img.desktop img');
            if (headerImg) {
                result.cover_image = headerImg.src;
            }
            
            // Rating
            const ratingElement = document.querySelector('.rating-block');
            if (ratingElement) {
                result.rating = ratingElement.textContent.trim();
            }
            
            // Reviews count
            const reviewsElement = document.querySelector('.view_rvws');
            if (reviewsElement) {
                const match = reviewsElement.textContent.match(/(\\d+)/);
                if (match) {
                    result.reviews_count = parseInt(match[1]);
                }
            }
            
            // Location
            const locationElement = document.querySelector('.ilp-loc span');
            if (locationElement) {
                const parts = locationElement.textContent.split(',').map(p => p.trim());
                result.location = parts[0];
                if (parts.length > 1) result.city = parts[1];
            }
            
        } catch(e) { console.log('Header information parsing error:', e); }
        
        console.log('Scraping completed!');
        console.log('=== Scraping Result Summary ===');
        console.log('Facilities count:', result.campus_content.highlights.length);
        console.log('Hostel facilities count:', result.campus_content.hostel.facilities.length);
        console.log('Library images count:', result.campus_content.library.images.length);
        console.log('Sports images count:', result.campus_content.sports.images.length);
        
        return result;
    """)
    
    # ================= 4. MERGE JS SCRAPING RESULTS =================
    if js_result:
        # Update header information
        if js_result.get('college_name'):
            college_info['college_name'] = js_result['college_name']
        if js_result.get('cover_image'):
            college_info['cover_image'] = js_result['cover_image']
        if js_result.get('rating'):
            college_info['rating'] = js_result['rating']
        if js_result.get('reviews_count'):
            college_info['reviews_count'] = js_result['reviews_count']
        if js_result.get('location'):
            college_info['location'] = js_result['location']
        if js_result.get('city'):
            college_info['city'] = js_result['city']
        
        # Update campus content
        if js_result.get('campus_content'):
            campus_data = js_result['campus_content']
            
            # Overview
            if campus_data['overview']['text']:
                college_info['campus_content']['overview']['text'] = campus_data['overview']['text']
            if campus_data['overview']['images']:
                college_info['campus_content']['overview']['images'] = campus_data['overview']['images']
            
            # Highlights
            if campus_data['highlights']:
                college_info['campus_content']['highlights'] = campus_data['highlights']
            
            # Hostel
            if campus_data['hostel']['description']:
                college_info['campus_content']['hostel']['description'] = campus_data['hostel']['description']
            if campus_data['hostel']['facilities']:
                college_info['campus_content']['hostel']['facilities'] = campus_data['hostel']['facilities']
            if campus_data['hostel']['fee_tables']:
                college_info['campus_content']['hostel']['fee_tables'] = campus_data['hostel']['fee_tables']
            if campus_data['hostel']['images']:
                college_info['campus_content']['hostel']['images'] = campus_data['hostel']['images']
            
            # Library
            if campus_data['library']['description']:
                college_info['campus_content']['library']['description'] = campus_data['library']['description']
            if campus_data['library']['images']:
                college_info['campus_content']['library']['images'] = campus_data['library']['images']
            
            # Sports
            if campus_data['sports']['description']:
                college_info['campus_content']['sports']['description'] = campus_data['sports']['description']
            if campus_data['sports']['images']:
                college_info['campus_content']['sports']['images'] = campus_data['sports']['images']
            
            # Places nearby
            if campus_data['places_nearby']:
                college_info['campus_content']['places_nearby'] = campus_data['places_nearby']
            
            # Videos
            if campus_data['videos']:
                college_info['campus_content']['videos'] = campus_data['videos']
    
    # ================= 5. FALLBACK: DIRECT HTML PARSING =================
    if not college_info['campus_content']['hostel']['facilities']:
        print("JS scraping didn't get hostel facilities, using fallback parsing...")
        try:
            page_html = driver.page_source
            
            # Directly parse hostel facilities from HTML
            import re
            
            # Find ul after "Hostel Facilities"
            facilities_pattern = r'Hostel Facilities.*?<ul>(.*?)</ul>'
            facilities_match = re.search(facilities_pattern, page_html, re.DOTALL | re.IGNORECASE)
            
            if facilities_match:
                ul_content = facilities_match.group(1)
                facilities_items = re.findall(r'<li>(.*?)</li>', ul_content)
                college_info['campus_content']['hostel']['facilities'] = [item.strip() for item in facilities_items]
                print(f"Fallback parsing found hostel facilities: {len(facilities_items)} items")
            
            # Find real image URLs
            picture_patterns = [
                r'data-originalset="(https://images\\.shiksha\\.com/mediadata/images/articles/.*?\\.jpeg)"',
                r'src="(https://images\\.shiksha\\.com/mediadata/images/articles/.*?\\.jpeg)"'
            ]
            
            all_image_urls = []
            for pattern in picture_patterns:
                matches = re.findall(pattern, page_html)
                all_image_urls.extend(matches)
            
            # Remove duplicates
            all_image_urls = list(set(all_image_urls))
            
            # Classify images
            for img_url in all_image_urls:
                if '1694510359' in img_url:  # Library image
                    college_info['campus_content']['library']['images'].append(img_url)
                elif '1694510611' in img_url:  # Hostel image
                    college_info['campus_content']['hostel']['images'].append(img_url)
                elif '1694510411' in img_url or '1694510438' in img_url or '1694510489' in img_url:  # Sports images
                    college_info['campus_content']['sports']['images'].append(img_url)
            
        except Exception as e:
            print(f"Fallback parsing error: ")
    
    # ================= 6. ENHANCE WITH INFRASTRUCTURE SECTION DATA =================
    # If infrastructure section has better data, use it to enhance existing data
    if college_info.get("infrastructure_section"):
        infra_data = college_info["infrastructure_section"]
        
        # Enhance hostel information
        if infra_data.get("hostel") and infra_data["hostel"].get("description"):
            if not college_info["campus_content"]["hostel"]["description"] or \
               len(infra_data["hostel"]["description"]) > len(college_info["campus_content"]["hostel"]["description"]):
                college_info["campus_content"]["hostel"]["description"] = infra_data["hostel"]["description"]
        
        # Enhance library information
        if infra_data.get("library") and infra_data["library"].get("description"):
            college_info["campus_content"]["library"]["description"] = infra_data["library"]["description"]
        
        # Enhance sports information
        if infra_data.get("sports") and infra_data["sports"].get("description"):
            college_info["campus_content"]["sports"]["description"] = infra_data["sports"]["description"]
    
    return college_info


def parse_faculty_full_html(driver,URLS):
    try:
        driver.get(URLS["faculty"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)

    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image from pwa-headerwrapper
        try:
            header_wrapper = driver.find_element(By.CLASS_NAME, "pwa-headerwrapper")
            cover_img = header_wrapper.find_element(By.CSS_SELECTOR, ".header_img.desktop img")
            college_info["cover_image"] = cover_img.get_attribute("src")
            print(f"✓ Cover image found: {college_info['cover_image']}")
        except Exception as e:
            print(" Cover image not found: ")
        
        # Extract college name
        try:
            h1_element = driver.find_element(By.CSS_SELECTOR, "h1.inst-name.h2")
            full_text = h1_element.text.strip()
            # Clean the college name - remove "Faculty Details & Reviews" and location
            college_name = full_text.split("Faculty Details & Reviews")[0].strip()
            college_info["college_name"] = college_name
            print(f"✓ College name found: {college_info['college_name']}")
        except Exception as e:
            print(" College name not found: ")
        
        # Extract location and city
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, ".ilp-loc.white-space-nowrap")
            location_text = location_element.text.strip()
            
            # Extract Vastrapur and Ahmedabad
            parts = location_text.split(", ")
            if len(parts) >= 1:
                # First part is Vastrapur
                college_info["location"] = parts[0].strip()
            
            if len(parts) >= 2:
                # Second part contains Ahmedabad (might be inside a link)
                city_part = parts[1]
                # Remove any HTML tags or links
                city_part = re.sub(r'<[^>]+>', '', city_part)
                college_info["city"] = city_part.strip()
            
            print(f"✓ Location found: {college_info['location']}, {college_info['city']}")
        except Exception as e:
            print(" Location not found: ")
        
        # Extract rating
        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, ".rating-block.rvw-lyr")
            rating_text = rating_element.text.strip()
            # Extract just the numeric rating (e.g., "4.6" from "4.6" with stars)
            rating_match = re.search(r'(\d+\.\d+)', rating_text)
            if rating_match:
                college_info["rating"] = rating_match.group(1)
                print(f"✓ Rating found: {college_info['rating']}")
        except Exception as e:
            print(" Rating not found: ")
        
        # Extract reviews count
        try:
            reviews_link = driver.find_element(By.CSS_SELECTOR, "a.view_rvws.ripple.dark")
            reviews_text = reviews_link.text.strip()
            # Extract number from text like "(136 Reviews)"
            reviews_match = re.search(r'\((\d+)\s*Reviews', reviews_text)
            if reviews_match:
                college_info["reviews_count"] = int(reviews_match.group(1))
                print(f"✓ Reviews count found: {college_info['reviews_count']}")
        except Exception as e:
            print(" Reviews count not found: ")
        
        # Extract Q&A count
        try:
            qa_element = driver.find_element(By.CSS_SELECTOR, ".qna_student a")
            qa_text = qa_element.text.strip()
            # Extract number from text like "1.5k Student Q&A"
            qa_match = re.search(r'(\d+(?:\.\d+)?)\s*(k|K)?', qa_text)
            if qa_match:
                count = float(qa_match.group(1))
                if qa_match.group(2):  # If has 'k' suffix
                    count *= 1000
                college_info["qa_count"] = int(count)
                print(f"✓ Q&A count found: {college_info['qa_count']}")
        except Exception as e:
            print(" Q&A count not found: ")
        
        # Extract institute type (if available)
        try:
            # Look for institute type in other parts of the page
            institute_type_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Institute Type') or contains(text(), 'Type:')]")
            for elem in institute_type_elements:
                text = elem.text.strip()
                if "Institute Type" in text or "Type:" in text:
                    college_info["institute_type"] = text.split(":")[-1].strip() if ":" in text else text
                    print(f"✓ Institute type found: {college_info['institute_type']}")
                    break
        except Exception as e:
            print(" Institute type not found: ")
        
        # Extract established year (if available)
        try:
            # Look for established year in other parts of the page
            estd_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Established') or contains(text(), 'Estd') or contains(text(), 'Founded')]")
            for elem in estd_elements:
                text = elem.text.strip()
                # Look for year pattern
                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                if year_match:
                    college_info["established_year"] = year_match.group()
                    print(f"✓ Established year found: {college_info['established_year']}")
                    break
        except Exception as e:
            print(" Established year not found: ")
        
        # Extract videos and photos count (from different parts of page)
        try:
            # Look for videos count
            video_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'video') or contains(text(), 'Video')]")
            for elem in video_elements:
                text = elem.text.lower()
                if "video" in text:
                    video_match = re.search(r'(\d+)\s*videos?', text)
                    if video_match:
                        college_info["videos_count"] = int(video_match.group(1))
                        print(f"✓ Videos count found: {college_info['videos_count']}")
                        break
        except Exception as e:
            print(" Videos count not found: ")
        
        try:
            # Look for photos count
            photo_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'photo') or contains(text(), 'Photo') or contains(text(), 'image') or contains(text(), 'Image')]")
            for elem in photo_elements:
                text = elem.text.lower()
                if "photo" in text or "image" in text:
                    photo_match = re.search(r'(\d+)\s*(photos?|images?)', text)
                    if photo_match:
                        college_info["photos_count"] = int(photo_match.group(1))
                        print(f"✓ Photos count found: {college_info['photos_count']}")
                        break
        except Exception as e:
            print(" Photos count not found: ")
        
        # Extract logo (if available)
        try:
            # Look for logo in different parts
            logo_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in logo_elements:
                src = img.get_attribute("src") or ""
                alt = img.get_attribute("alt") or ""
                if ("logo" in src.lower() or "logo" in alt.lower()) and "shiksha.com" in src:
                    college_info["logo"] = src
                    print(f"✓ Logo found: {college_info['logo']}")
                    break
        except Exception as e:
            print(" Logo not found: ")

    except Exception as e:
        print(" Error in college header section: ")
    driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)

    # section = wait.until(
    #     EC.presence_of_element_located(
    #         (By.CSS_SELECTOR, "div.wikkiContents.faqAccordian")
    #     )
    # )
    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,"div.wikkiContents.faqAccordian")
            )
        )
    except:
        print("⚠️ parse_faculty_full_html not available, skipping")
        return None

    # 🔥 Scroll for lazy content
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(2)

    html = driver.execute_script(
        "return arguments[0].innerHTML;", section
    )

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "author": {
            "name": "",
            "profile_url": "",
            "verified": False
        },
        "last_updated": "",
        "description": "",
        "faculty": []
    }

    # ✅ Author details
    author_tag = soup.select_one(".adp_usr_dtls a")
    if author_tag:
        data["author"]["name"] = author_tag.get_text(strip=True)
        data["author"]["profile_url"] = author_tag.get("href", "")
        data["author"]["verified"] = bool(author_tag.select_one(".tickIcon"))

    # ✅ Updated date
    date_tag = soup.select_one(".post-date")
    if date_tag:
        data["last_updated"] = (
            date_tag.get_text(strip=True)
            .replace("Updated on", "")
            .strip()
        )

    # ✅ Full description (first <p>)
    desc_p = soup.select_one(".abtSection p")
    if desc_p:
        data["description"] = desc_p.get_text(" ", strip=True)

    # ✅ Faculty table (FULL SAFE PARSE)
    table = soup.select_one(".abtSection table")
    if table:
        rows = table.find_all("tr")

        for row in rows[1:]:  # skip header
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            faculty_name = cols[0].get_text(" ", strip=True)

            qualifications = []
            for item in cols[1].select("p"):
                text = item.get_text(" ", strip=True)
                if text:
                    qualifications.append(text)

            data["faculty"].append({
                "faculty_name": faculty_name,
                "qualifications": qualifications
            })

    return {"college_info":college_info,"data":data}

def parse_faculty_reviews(driver,URLS):
    try:
        driver.get(URLS["faculty"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["faculty"])
    wait = WebDriverWait(driver, 15)

    section = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//h2[contains(text(),'Faculty Reviews')]/ancestor::section")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(0.5)

    html = driver.execute_script(
        "return arguments[0].innerHTML;", section
    )

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "overall_rating": "",
        "rating_out_of": "5",
        "based_on_reviews": "",
        "rating_distribution": [],
        "verified_reviews_info": ""
    }

    # ✅ Overall rating
    rating_tag = soup.select_one(".rvwScore h3")
    if rating_tag:
        data["overall_rating"] = rating_tag.get_text(strip=True)

    # ✅ Based on reviews count
    based_tag = soup.select_one(".refrnceTxt span")
    if based_tag:
        data["based_on_reviews"] = based_tag.get_text(strip=True)

    # ✅ Rating distribution (4-5, 3-4, etc.)
    for bar in soup.select(".starBar"):
        label_tag = bar.select_one(".starC a")
        percent_tag = bar.select_one(".starPrgrs")
        fill_tag = bar.select_one(".fillBar")

        data["rating_distribution"].append({
            "rating_range": label_tag.get_text(strip=True) if label_tag else "",
            "percentage_text": percent_tag.get_text(strip=True) if percent_tag else "",
            "percentage_width": fill_tag["style"].replace("width:", "").replace(";", "").strip()
            if fill_tag and fill_tag.has_attr("style") else ""
        })

    # ✅ Verified reviews description text
    verified_info = soup.select_one(".getAllrvws")
    if verified_info:
        data["verified_reviews_info"] = verified_info.get_text(" ", strip=True)

    return data

def parse_review_summarisation_all_tabs(driver,URLS):
    try:
        driver.get(URLS["faculty"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["faculty"])
    
    wait = WebDriverWait(driver, 15)


    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.ID, "ReviewSummarisationReviewSummary")
            )
        )
    except:
        print("⚠️ parse_review_summarisation_all_tabs not available, skipping")
        return None

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(2)

    final_data = {
        "heading": "",
        "tabs_data": {}
    }

    # Heading
    heading = section.find_element(By.CLASS_NAME, "rvwSmSecHeading")
    final_data["heading"] = heading.text.strip()

    # All tabs
    tabs = section.find_elements(By.CLASS_NAME, "rvwSmTabItem")

    for idx, tab in enumerate(tabs):
        tab_name = tab.find_element(By.CLASS_NAME, "rvwSmTabName").text.strip()

        # Click tab
        driver.execute_script("arguments[0].click();", tab)
        time.sleep(1.5)

        # Fresh HTML after tab change
        html = driver.execute_script(
            "return arguments[0].innerHTML;", section
        )
        soup = BeautifulSoup(html, "html.parser")

        tab_data = {
            "likes": [],
            "info_text": ""
        }

        # Likes
        for li in soup.select(".likeSec ul.bulletList li"):
            gray = li.select_one(".grayItem")
            tab_data["likes"].append({
                "text": li.get_text(" ", strip=True).replace(
                    gray.get_text(strip=True), ""
                ).strip() if gray else li.get_text(strip=True),
                "review_count": gray.get_text(strip=True) if gray else ""
            })

        # Info text
        info = soup.select_one(".rvwSmInfoTxt")
        if info:
            tab_data["info_text"] = info.get_text(strip=True)

        final_data["tabs_data"][tab_name] = tab_data

    return final_data

def parse_articles_section(driver,URLS):
    try:
        driver.get(URLS["compare"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["compare"])
    
    wait = WebDriverWait(driver, 15)

    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image from pwa-headerwrapper
        try:
            header_wrapper = driver.find_element(By.CLASS_NAME, "pwa-headerwrapper")
            cover_img = header_wrapper.find_element(By.CSS_SELECTOR, ".header_img.desktop img")
            college_info["cover_image"] = cover_img.get_attribute("src")
            print(f"✓ Cover image found: {college_info['cover_image']}")
        except Exception as e:
            print(" Cover image not found: ")
        
        # Extract college name
        try:
            h1_element = driver.find_element(By.CSS_SELECTOR, "h1.inst-name.h2")
            full_text = h1_element.text.strip()
            # Clean the college name - remove "Faculty Details & Reviews" and location
            college_name = full_text.split("Faculty Details & Reviews")[0].strip()
            college_info["college_name"] = college_name
            print(f"✓ College name found: {college_info['college_name']}")
        except Exception as e:
            print(" College name not found: ")
        
        # Extract location and city
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, ".ilp-loc.white-space-nowrap")
            location_text = location_element.text.strip()
            
            # Extract Vastrapur and Ahmedabad
            parts = location_text.split(", ")
            if len(parts) >= 1:
                # First part is Vastrapur
                college_info["location"] = parts[0].strip()
            
            if len(parts) >= 2:
                # Second part contains Ahmedabad (might be inside a link)
                city_part = parts[1]
                # Remove any HTML tags or links
                city_part = re.sub(r'<[^>]+>', '', city_part)
                college_info["city"] = city_part.strip()
            
            print(f"✓ Location found: {college_info['location']}, {college_info['city']}")
        except Exception as e:
            print(" Location not found: ")
        
        # Extract rating
        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, ".rating-block.rvw-lyr")
            rating_text = rating_element.text.strip()
            # Extract just the numeric rating (e.g., "4.6" from "4.6" with stars)
            rating_match = re.search(r'(\d+\.\d+)', rating_text)
            if rating_match:
                college_info["rating"] = rating_match.group(1)
                print(f"✓ Rating found: {college_info['rating']}")
        except Exception as e:
            print(" Rating not found: ")
        
        # Extract reviews count
        try:
            reviews_link = driver.find_element(By.CSS_SELECTOR, "a.view_rvws.ripple.dark")
            reviews_text = reviews_link.text.strip()
            # Extract number from text like "(136 Reviews)"
            reviews_match = re.search(r'\((\d+)\s*Reviews', reviews_text)
            if reviews_match:
                college_info["reviews_count"] = int(reviews_match.group(1))
                print(f"✓ Reviews count found: {college_info['reviews_count']}")
        except Exception as e:
            print(" Reviews count not found: ")
        
        # Extract Q&A count
        try:
            qa_element = driver.find_element(By.CSS_SELECTOR, ".qna_student a")
            qa_text = qa_element.text.strip()
            # Extract number from text like "1.5k Student Q&A"
            qa_match = re.search(r'(\d+(?:\.\d+)?)\s*(k|K)?', qa_text)
            if qa_match:
                count = float(qa_match.group(1))
                if qa_match.group(2):  # If has 'k' suffix
                    count *= 1000
                college_info["qa_count"] = int(count)
                print(f"✓ Q&A count found: {college_info['qa_count']}")
        except Exception as e:
            print(" Q&A count not found: ")
        
        # Extract institute type (if available)
        try:
            # Look for institute type in other parts of the page
            institute_type_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Institute Type') or contains(text(), 'Type:')]")
            for elem in institute_type_elements:
                text = elem.text.strip()
                if "Institute Type" in text or "Type:" in text:
                    college_info["institute_type"] = text.split(":")[-1].strip() if ":" in text else text
                    print(f"✓ Institute type found: {college_info['institute_type']}")
                    break
        except Exception as e:
            print(" Institute type not found: ")
        
        # Extract established year (if available)
        try:
            # Look for established year in other parts of the page
            estd_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Established') or contains(text(), 'Estd') or contains(text(), 'Founded')]")
            for elem in estd_elements:
                text = elem.text.strip()
                # Look for year pattern
                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                if year_match:
                    college_info["established_year"] = year_match.group()
                    print(f"✓ Established year found: {college_info['established_year']}")
                    break
        except Exception as e:
            print(" Established year not found: ")
        
        # Extract videos and photos count (from different parts of page)
        try:
            # Look for videos count
            video_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'video') or contains(text(), 'Video')]")
            for elem in video_elements:
                text = elem.text.lower()
                if "video" in text:
                    video_match = re.search(r'(\d+)\s*videos?', text)
                    if video_match:
                        college_info["videos_count"] = int(video_match.group(1))
                        print(f"✓ Videos count found: {college_info['videos_count']}")
                        break
        except Exception as e:
            print(" Videos count not found: ")
        
        try:
            # Look for photos count
            photo_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'photo') or contains(text(), 'Photo') or contains(text(), 'image') or contains(text(), 'Image')]")
            for elem in photo_elements:
                text = elem.text.lower()
                if "photo" in text or "image" in text:
                    photo_match = re.search(r'(\d+)\s*(photos?|images?)', text)
                    if photo_match:
                        college_info["photos_count"] = int(photo_match.group(1))
                        print(f"✓ Photos count found: {college_info['photos_count']}")
                        break
        except Exception as e:
            print(" Photos count not found: ")
        
        # Extract logo (if available)
        try:
            # Look for logo in different parts
            logo_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in logo_elements:
                src = img.get_attribute("src") or ""
                alt = img.get_attribute("alt") or ""
                if ("logo" in src.lower() or "logo" in alt.lower()) and "shiksha.com" in src:
                    college_info["logo"] = src
                    print(f"✓ Logo found: {college_info['logo']}")
                    break
        except Exception as e:
            print(" Logo not found: ")

    except Exception as e:
        print(" Error in college header section: ")
    driver.get(URLS["compare"])
    wait = WebDriverWait(driver, 15)

    try:
        section = wait.until(
            EC.presence_of_element_located((By.ID, "Articles"))
        )
    except TimeoutException:
        print("⚠️ Articles section not found, skipping...")
        return []
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", section
    )
    time.sleep(2)

    html = driver.execute_script("return arguments[0].innerHTML;", section)
    soup = BeautifulSoup(html, "html.parser")

    articles_data = []

    for card in soup.select(".articleCard_Wrapper"):
        title_tag = card.select_one("h3.articleTitle a")
        author_tag = card.select_one(".authorInfo a")
        date_tag = card.select_one(".articelUpdatedDate")
        image_tag = card.select_one(".imageBox img")
        views_tag = card.select_one(".viewsData label")
        comment_tag = card.select_one(".commentData label")

        # Image fallback: background-image if img not present
        if not image_tag:
            bg = card.select_one(".img-blurdiv")
            image_url = ""
            if bg:
                style = bg.get("style", "")
                match = re.search(r'url\("&quot;(.*?)&quot;\)', style)
                if match:
                    image_url = match.group(1)
        else:
            image_url = image_tag.get("src", "")

        articles_data.append({
            "title": title_tag.text.strip() if title_tag else "",
            "link": "https://www.shiksha.com" + title_tag.get("href") if title_tag else "",
            "author_name": author_tag.text.strip() if author_tag else "",
            "author_link": author_tag.get("href") if author_tag else "",
            "date": date_tag.text.strip() if date_tag else "",
            "image": image_url,
            "views": views_tag.text.strip() if views_tag else "",
            "comments": comment_tag.text.strip() if comment_tag else ""
        })

    return {"college_info":college_info,"articles":articles_data}


def parse_faq_scholarships_section(driver, URLS):
    try:
        driver.get(URLS["scholarships"])
    except selenium.common.exceptions.InvalidSessionIdException:
        driver = webdriver.Chrome(options=options)
        driver.get(URLS["scholarships"]) 
    wait = WebDriverWait(driver, 15)

    college_info = {
        "college_name": None,
        "logo": None,
        "cover_image": None,
        "videos_count": 0,
        "photos_count": 0,
        "rating": None,
        "reviews_count": None,
        "qa_count": None,
        "location": None,
        "city": None,
        "institute_type": None,
        "established_year": None,
    }
    try:
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Extract cover image from pwa-headerwrapper
        try:
            header_wrapper = driver.find_element(By.CLASS_NAME, "pwa-headerwrapper")
            cover_img = header_wrapper.find_element(By.CSS_SELECTOR, ".header_img.desktop img")
            college_info["cover_image"] = cover_img.get_attribute("src")
            print(f"✓ Cover image found: {college_info['cover_image']}")
        except Exception as e:
            print(" Cover image not found: ")
        
        # Extract college name
        try:
            h1_element = driver.find_element(By.CSS_SELECTOR, "h1.inst-name.h2")
            full_text = h1_element.text.strip()
            # Clean the college name - remove "Faculty Details & Reviews" and location
            college_name = full_text.split("Faculty Details & Reviews")[0].strip()
            college_info["college_name"] = college_name
            print(f"✓ College name found: {college_info['college_name']}")
        except Exception as e:
            print(" College name not found: ")
        
        # Extract location and city
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, ".ilp-loc.white-space-nowrap")
            location_text = location_element.text.strip()
            
            # Extract Vastrapur and Ahmedabad
            parts = location_text.split(", ")
            if len(parts) >= 1:
                # First part is Vastrapur
                college_info["location"] = parts[0].strip()
            
            if len(parts) >= 2:
                # Second part contains Ahmedabad (might be inside a link)
                city_part = parts[1]
                # Remove any HTML tags or links
                city_part = re.sub(r'<[^>]+>', '', city_part)
                college_info["city"] = city_part.strip()
            
            print(f"✓ Location found: {college_info['location']}, {college_info['city']}")
        except Exception as e:
            print(" Location not found: ")
        
        # Extract rating
        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, ".rating-block.rvw-lyr")
            rating_text = rating_element.text.strip()
            # Extract just the numeric rating (e.g., "4.6" from "4.6" with stars)
            rating_match = re.search(r'(\d+\.\d+)', rating_text)
            if rating_match:
                college_info["rating"] = rating_match.group(1)
                print(f"✓ Rating found: {college_info['rating']}")
        except Exception as e:
            print(" Rating not found: ")
        
        # Extract reviews count
        try:
            reviews_link = driver.find_element(By.CSS_SELECTOR, "a.view_rvws.ripple.dark")
            reviews_text = reviews_link.text.strip()
            # Extract number from text like "(136 Reviews)"
            reviews_match = re.search(r'\((\d+)\s*Reviews', reviews_text)
            if reviews_match:
                college_info["reviews_count"] = int(reviews_match.group(1))
                print(f"✓ Reviews count found: {college_info['reviews_count']}")
        except Exception as e:
            print(" Reviews count not found: ")
        
        # Extract Q&A count
        try:
            qa_element = driver.find_element(By.CSS_SELECTOR, ".qna_student a")
            qa_text = qa_element.text.strip()
            # Extract number from text like "1.5k Student Q&A"
            qa_match = re.search(r'(\d+(?:\.\d+)?)\s*(k|K)?', qa_text)
            if qa_match:
                count = float(qa_match.group(1))
                if qa_match.group(2):  # If has 'k' suffix
                    count *= 1000
                college_info["qa_count"] = int(count)
                print(f"✓ Q&A count found: {college_info['qa_count']}")
        except Exception as e:
            print(" Q&A count not found: ")
        
        # Extract institute type (if available)
        try:
            # Look for institute type in other parts of the page
            institute_type_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Institute Type') or contains(text(), 'Type:')]")
            for elem in institute_type_elements:
                text = elem.text.strip()
                if "Institute Type" in text or "Type:" in text:
                    college_info["institute_type"] = text.split(":")[-1].strip() if ":" in text else text
                    print(f"✓ Institute type found: {college_info['institute_type']}")
                    break
        except Exception as e:
            print(" Institute type not found: ")
        
        # Extract established year (if available)
        try:
            # Look for established year in other parts of the page
            estd_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Established') or contains(text(), 'Estd') or contains(text(), 'Founded')]")
            for elem in estd_elements:
                text = elem.text.strip()
                # Look for year pattern
                year_match = re.search(r'\b(19|20)\d{2}\b', text)
                if year_match:
                    college_info["established_year"] = year_match.group()
                    print(f"✓ Established year found: {college_info['established_year']}")
                    break
        except Exception as e:
            print(" Established year not found: ")
        
        # Extract videos and photos count (from different parts of page)
        try:
            # Look for videos count
            video_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'video') or contains(text(), 'Video')]")
            for elem in video_elements:
                text = elem.text.lower()
                if "video" in text:
                    video_match = re.search(r'(\d+)\s*videos?', text)
                    if video_match:
                        college_info["videos_count"] = int(video_match.group(1))
                        print(f"✓ Videos count found: {college_info['videos_count']}")
                        break
        except Exception as e:
            print(" Videos count not found: ")
        
        try:
            # Look for photos count
            photo_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'photo') or contains(text(), 'Photo') or contains(text(), 'image') or contains(text(), 'Image')]")
            for elem in photo_elements:
                text = elem.text.lower()
                if "photo" in text or "image" in text:
                    photo_match = re.search(r'(\d+)\s*(photos?|images?)', text)
                    if photo_match:
                        college_info["photos_count"] = int(photo_match.group(1))
                        print(f"✓ Photos count found: {college_info['photos_count']}")
                        break
        except Exception as e:
            print(" Photos count not found: ")
        
        # Extract logo (if available)
        try:
            # Look for logo in different parts
            logo_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in logo_elements:
                src = img.get_attribute("src") or ""
                alt = img.get_attribute("alt") or ""
                if ("logo" in src.lower() or "logo" in alt.lower()) and "shiksha.com" in src:
                    college_info["logo"] = src
                    print(f"✓ Logo found: {college_info['logo']}")
                    break
        except Exception as e:
            print(" Logo not found: ")

    except Exception as e:
        print(" Error in college header section: ")
    driver.get(URLS["scholarships"])
    wait = WebDriverWait(driver, 15)
    # section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wikkiContents.faqAccordian")))
    try:
        section = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,".wikkiContents.faqAccordian")
            )
        )
    except:
        
        return None
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", section)
    time.sleep(0.5)

    html = driver.execute_script("return arguments[0].innerHTML;", section)
    soup = BeautifulSoup(html, "html.parser")

    # Author
    author_tag = soup.select_one(".adp_usr_dtls a")
    author_name = author_tag.text.strip() if author_tag else ""
    author_link = author_tag.get("href") if author_tag else ""
    
    # Date
    date_tag = soup.select_one(".post-date")
    updated_on = date_tag.text.replace("Updated on", "").strip() if date_tag else ""

    # Paragraphs
    paragraphs = [p.text.strip() for p in soup.select(".abtSection p")]

    # Tables
    tables = []
    for table in soup.select(".abtSection table"):
        table_data = []
        for row in table.find_all("tr"):
            cols = [td.text.strip() for td in row.find_all(["td","th"])]
            table_data.append(cols)
        tables.append(table_data)

    # PDF links
    pdf_links = [a.get("data-link") for a in soup.select("a.smce-cta-link")]

    # Videos
    iframe_elements = driver.find_elements(By.CSS_SELECTOR, ".vcmsEmbed iframe")
    videos = []
    
    for iframe in iframe_elements:
        driver.execute_script("arguments[0].scrollIntoView(true);", iframe)
        time.sleep(0.5)  # wait for lazy loading
        src = iframe.get_attribute("src") or iframe.get_attribute("data-src")
        if src:
            videos.append(src)

    result = {}
    
    result["author_name"] = author_name
    result["author_link"] = author_link
    result["updated_on"] = updated_on
    result["paragraphs"] = paragraphs
    result["tables"] = tables
    result["pdf_links"] = pdf_links
    result["videos"] = videos


    return {"college_info":college_info,"result":result}

# def extract_shiksha_qna(driver,URLS):
#     driver.get(URLS["qna"])

#     # Thoda wait karo page load ke liye
#     import time
#     time.sleep(2)

#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     result = {}

#     # ===== Question Details =====
#     question_data = {}
#     title_tag = soup.select_one("#quesTitle_5114413 .wikkiContents")
#     question_data['title'] = title_tag.get_text(strip=True) if title_tag else None

#     asker_tag = soup.select_one(".new-column .right-cl a")
#     question_data['asked_by'] = asker_tag.get_text(strip=True) if asker_tag else None
#     question_data['asker_profile'] = asker_tag['href'] if asker_tag else None

#     follower_tag = soup.select_one(".followersCountTextArea")
#     question_data['followers'] = int(follower_tag.get_text(strip=True).split()[0]) if follower_tag else 0

#     # Views
#     viewers_tag = soup.select_one(".viewers-span")
#     if viewers_tag:
#         views_text = viewers_tag.get_text(strip=True).replace("Views","").strip()
#         if "k" in views_text:
#             views_text = views_text.replace("k", "")
#             question_data['views'] = int(float(views_text) * 1000)
#         else:
#             question_data['views'] = int(views_text)
#     else:
#         question_data['views'] = 0


#     time_tag = soup.select_one("span.time span:last-child")
#     question_data['posted'] = time_tag.get_text(strip=True) if time_tag else None

#     result['question'] = question_data

#     # ===== Answers =====
#     answers = []
#     for li in soup.find_all("li", class_="module"):
#         answer = {}

#         author_tag = li.select_one(".avatar-name")
#         answer['author_name'] = author_tag.get_text(strip=True) if author_tag else None
#         answer['author_profile'] = author_tag['href'] if author_tag else None

#         level_tag = li.select_one(".lvl-name")
#         answer['contributor_level'] = level_tag.get_text(strip=True) if level_tag else None

#         time_tag = li.select_one(".time")
#         answer['time'] = time_tag.get_text(strip=True) if time_tag else None

#         content_tag = li.select_one("p[id^='answerMsgTxt_']")
#         if content_tag:
#             text = content_tag.get_text(strip=True)
#             text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
#             answer['content'] = text
#         else:
#             answer['content'] = None

#         upvote_tag = li.select_one("input[id^='userCountUpvote_']")
#         downvote_tag = li.select_one("input[id^='userCountDownvote_']")
#         answer['upvotes'] = int(upvote_tag['value']) if upvote_tag else 0
#         answer['downvotes'] = int(downvote_tag['value']) if downvote_tag else 0

#         share_tag = li.select_one("a.qSLayer")
#         answer['share_url'] = share_tag['data-shareurl'] if share_tag else None

#         report_tag = li.select_one("a.raLayerClk")
#         answer['report_url'] = report_tag['href'] if report_tag else None

#         answers.append(answer)

#     result['answers'] = answers

#     return result


def scrape_mba_colleges():
    driver = create_driver()
    all_data = []
    c_count =601

    try:
        for base_url in BASE_URL:
            print("🔄 Scraping:", base_url)

            URLS = build_urls(base_url)
           

            college_data = {       
                "college_details":{
                "id":f"college_{c_count:03d}",
                "college_info":{
                 "college_info":scrape_college_info(driver,URLS),
                },
                "courses": scrape_courses(driver,URLS),
                "fees":scrape_fees(driver,URLS),
                "reviews":{
                    "review_summary":scrape_review_summary(driver,URLS),
                 },
                 "admission":{
                    "admission_overview":scrape_admission_overview(driver,URLS),
                 },
                "placement":{
                    "placement_report":scrape_placement_report(driver,URLS),
                 
                },               
                "cut_off":{
                "cut_off":scrape_cutoff(driver,URLS),
                },
                "ranking":{
                "ranking":scrape_ranking(driver,URLS),
              
                },
                "gallery":{
                "gallery_page":scrape_mini_clips(driver,URLS),
                },
                "hotel_campus":{
                 "hostel_campus":scrape_hostel_campus_js(driver,URLS),
        
                },
                "faculty":{
                   "faculty":parse_faculty_full_html(driver,URLS),
                    "faculty_reviews":parse_faculty_reviews(driver,URLS),
                    "review_summarisation":parse_review_summarisation_all_tabs(driver,URLS),                   
                },
                "compare":{
                    "articles":parse_articles_section(driver,URLS),
                },
                
                "scholarships":parse_faq_scholarships_section(driver,URLS),
                    }
               
                }
            all_data.append(college_data)
            c_count += 1
    finally:
        driver.quit()

    return all_data



import time
import os

TEMP_FILE = "allindiambacollegedetails601_630.tmp.json"
FINAL_FILE = "allindiambacollegedetails601_630.json"

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
        
