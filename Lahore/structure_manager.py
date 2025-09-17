"""
Lahore Supreme Court Structured Folder Creator and Manager
Creates organized folder structure for systematic extraction
"""

import os
import json
import shutil
from pathlib import Path


class LahoreStructureManager:
    """Manages the organized folder structure for Lahore registry extraction"""
    
    def __init__(self, base_dir="d:/SEM7/NLP/NLP-Assignment-1/Lahore"):
        self.base_dir = Path(base_dir)
        self.analysis_file = self.base_dir / "lahore_structure_analysis.json"
        self.analysis_data = None
        
        # Load analysis data
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
        else:
            raise FileNotFoundError("Analysis file not found. Run analyze_options.py first.")
    
    def sanitize_folder_name(self, name):
        """Convert case type names to valid folder names"""
        # Replace dots and special characters
        sanitized = name.replace('.', '_').replace('(', '_').replace(')', '_')
        # Remove trailing underscores
        sanitized = sanitized.rstrip('_')
        return sanitized
    
    def create_folder_structure(self):
        """Create the complete organized folder structure"""
        print("🏗️ CREATING LAHORE ORGANIZED FOLDER STRUCTURE")
        print("=" * 60)
        
        case_types = self.analysis_data['case_types']
        year_ranges = self.analysis_data['year_ranges']
        
        created_folders = 0
        
        for case_type in case_types:
            case_value = case_type['value']
            case_text = case_type['text']
            case_folder_name = f"{case_value}_{self.sanitize_folder_name(case_text)}"
            
            print(f"\n📁 Creating case type folder: {case_folder_name}")
            
            case_type_dir = self.base_dir / case_folder_name
            case_type_dir.mkdir(exist_ok=True)
            
            for year_range in year_ranges:
                range_name = year_range['name']
                range_folder = case_type_dir / range_name
                range_folder.mkdir(exist_ok=True)
                
                # Create subfolders for organization
                (range_folder / "pdfs").mkdir(exist_ok=True)
                (range_folder / "logs").mkdir(exist_ok=True)
                
                created_folders += 1
                print(f"   📂 {range_name} (Years: {year_range['years']})")
        
        print(f"\n✅ FOLDER STRUCTURE CREATED SUCCESSFULLY!")
        print(f"   Total Case Type Folders: {len(case_types)}")
        print(f"   Total Year Range Folders: {created_folders}")
        print(f"   Structure: {len(case_types)} case types × {len(year_ranges)} year ranges")
        
        return True
    
    def create_extraction_script(self, case_type, year_range):
        """Create individual extraction script for a case type-year range combination"""
        case_value = case_type['value']
        case_text = case_type['text']
        case_folder_name = f"{case_value}_{self.sanitize_folder_name(case_text)}"
        
        range_name = year_range['name']
        script_dir = self.base_dir / case_folder_name / range_name
        script_file = script_dir / f"extract_{case_folder_name}_{range_name.replace('-', '_')}.py"
        
        # Generate the extraction script content using the proven technique
        script_content = f'''"""
Extractor for {case_text} Lahore {range_name}
Based on proven paginated multi-browser technique
"""

import time
import re
import json
import os
import requests
import urllib3
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class {case_folder_name}_{range_name.replace('-', '_')}_Extractor:
    """Extractor for {case_text} Lahore {range_name} using proven technique"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.extracted_cases = []
        self.base_url = "https://scp.gov.pk"
        self.results_lock = threading.Lock()
        
        # Configuration for this specific extraction
        self.case_type_value = "{case_value}"
        self.case_type_text = "{case_text}"
        self.years = {year_range['years']}
        self.year_range_name = "{range_name}"
        
        # Create downloads directory
        self.downloads_dir = "pdfs"
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        print(f"✅ {case_text} Lahore {range_name} Extractor initialized")
        print(f"   Case Type: {case_text} (Value: {case_value})")
        print(f"   Years: {year_range['years']}")
        print(f"   Workers: {{self.max_workers}}")
    
    def create_optimized_driver(self, headless=False):
        """Create optimized Chrome WebDriver (proven technique)"""
        try:
            options = Options()
            
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            options.add_argument('--hide-scrollbars')
            options.add_argument('--mute-audio')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Memory optimizations
            options.add_argument('--memory-pressure-off')
            options.add_argument('--max_old_space_size=4096')
            
            # Network optimizations
            options.add_argument('--aggressive-cache-discard')
            options.add_argument('--disable-background-networking')
            
            # Add prefs to disable images and other resources
            prefs = {{
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.media_stream": 2,
            }}
            options.add_experimental_option("prefs", prefs)
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(5)
            
            return driver
        except Exception as e:
            print(f"❌ Failed to create driver: {{e}}")
            return None
    
    def navigate_and_search(self, driver, worker_id, year):
        """Navigate and search for specific year (proven technique)"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Worker {{worker_id}}: Navigating for year {{year}}")
            driver.get(url)
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlCaseType"))
            )
            
            # Select case type
            case_type_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlCaseType'))
            )
            select = Select(case_type_select)
            select.select_by_value(self.case_type_value)
            time.sleep(1)
            
            # Select registry: Lahore
            registry_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
            )
            select = Select(registry_select)
            select.select_by_value('L')
            time.sleep(1)
            
            # Select year
            year_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlYear'))
            )
            select = Select(year_select)
            select.select_by_value(str(year))
            time.sleep(1)
            
            # Click search button
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'btnSearch'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", search_button)
            print(f"🔍 Worker {{worker_id}}: Search completed for year {{year}}")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Search failed for year {{year}} - {{e}}")
            return False
    
    def navigate_to_page(self, driver, page_number, worker_id):
        """Navigate to specific page (proven technique)"""
        try:
            if page_number == 1:
                return True
            
            print(f"🔄 Worker {{worker_id}}: Navigating to page {{page_number}}")
            
            page_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[text()='{{page_number}}']"))
            )
            driver.execute_script("arguments[0].click();", page_link)
            time.sleep(3)
            
            print(f"✅ Worker {{worker_id}}: Successfully navigated to page {{page_number}}")
            return True
            
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Failed to navigate to page {{page_number}} - {{e}}")
            return False
    
    def download_pdf(self, pdf_url, case_no, pdf_type, worker_id):
        """Download PDF files (proven technique)"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            safe_case_no = re.sub(r'[^\\w\\-_.]', '_', case_no)
            filename = f"{{safe_case_no}}_{{pdf_type}}.pdf"
            local_path = os.path.join(self.downloads_dir, filename)
            
            if os.path.exists(local_path):
                print(f"📄 Worker {{worker_id}}: PDF already exists - {{filename}}")
                return local_path
            
            print(f"⬇️ Worker {{worker_id}}: Downloading {{filename}}")
            
            headers = {{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }}
            
            response = requests.get(pdf_url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Worker {{worker_id}}: Downloaded {{filename}} ({{len(response.content)}} bytes)")
            return local_path
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Worker {{worker_id}}: Download failed for {{case_no}} - {{e}}")
            return f"Download Failed: {{str(e)}}"
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Error downloading {{case_no}} - {{e}}")
            return f"Download Error: {{str(e)}}"
    
    def extract_detailed_case_info(self, driver, case_index, worker_id, page_number, year):
        """Extract detailed case information (proven technique)"""
        try:
            print(f"🔍 Worker {{worker_id}}: Processing Year {{year}}, Page {{page_number}}, Case {{case_index + 1}}")
            
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Worker {{worker_id}}: Case index {{case_index}} out of range")
                return None
            
            link = view_details_links[case_index]
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            case_data = {{
                "Case_No": "N/A",
                "Case_Title": "N/A", 
                "Status": "N/A",
                "Institution_Date": "N/A",
                "Disposal_Date": "N/A",
                "Advocates": {{
                    "ASC": "N/A",
                    "AOR": "N/A",
                    "Prosecutor": "N/A"
                }},
                "Petition_Appeal_Memo": {{
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []
                }},
                "History": [],
                "Judgement_Order": {{
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []
                }},
                "Worker_ID": worker_id,
                "Page_Number": page_number,
                "Year": year,
                "Case_Type": self.case_type_text,
                "Year_Range": self.year_range_name
            }}
            
            # Extract case information using proven selectors
            case_no_span = soup.find('span', {{'id': 'spCaseNo'}})
            if case_no_span:
                case_data["Case_No"] = case_no_span.get_text(strip=True)
            
            case_title_span = soup.find('span', {{'id': 'spCaseTitle'}})
            if case_title_span:
                case_data["Case_Title"] = case_title_span.get_text(strip=True)
            
            status_span = soup.find('span', {{'id': 'spStatus'}})
            if status_span:
                case_data["Status"] = status_span.get_text(strip=True)
            
            inst_date_span = soup.find('span', {{'id': 'spInstDate'}})
            if inst_date_span:
                case_data["Institution_Date"] = inst_date_span.get_text(strip=True)
            
            disp_date_span = soup.find('span', {{'id': 'spDispDate'}})
            if disp_date_span:
                case_data["Disposal_Date"] = disp_date_span.get_text(strip=True)
            
            # Extract advocates
            aor_span = soup.find('span', {{'id': 'spAOR'}})
            if aor_span:
                aor_html = str(aor_span)
                
                if '<br>' in aor_html:
                    parts = aor_html.split('<br>')
                    for part in parts:
                        clean_text = re.sub(r'<[^>]+>', '', part).strip()
                        if '(AOR)' in clean_text:
                            case_data["Advocates"]["AOR"] = clean_text
                        elif '(ASC)' in clean_text:
                            case_data["Advocates"]["ASC"] = clean_text
                        elif 'prosecutor' in clean_text.lower():
                            case_data["Advocates"]["Prosecutor"] = clean_text
                else:
                    aor_text = aor_span.get_text()
                    lines = aor_text.split('\\n')
                    for line in lines:
                        line = line.strip()
                        if '(AOR)' in line:
                            case_data["Advocates"]["AOR"] = line
                        elif '(ASC)' in line:
                            case_data["Advocates"]["ASC"] = line
                        elif 'prosecutor' in line.lower():
                            case_data["Advocates"]["Prosecutor"] = line
            
            # Extract PDF links (proven technique)
            pdf_links = soup.find_all('a', href=True)
            
            memo_files = []
            judgment_files = []
            
            for link in pdf_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                if (href and 
                    ('.pdf' in href.lower() or 
                     'digital copy' in link_text.lower() or
                     ('file' in link_text.lower() and '.pdf' in href.lower()))):
                    
                    if (any(keyword in link_text.lower() for keyword in ['digital copy', 'file', 'memo', 'petition', 'appeal']) and
                        not any(keyword in link_text.lower() for keyword in ['judgment', 'order'])):
                        memo_files.append({{
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        }})
                    elif any(keyword in link_text.lower() for keyword in ['judgment', 'order']):
                        judgment_files.append({{
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        }})
                    else:
                        memo_files.append({{
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        }})
            
            # Handle memo files
            if memo_files:
                case_data["Petition_Appeal_Memo"]["Files"] = []
                for i, memo_file in enumerate(memo_files):
                    file_info = {{
                        "File": memo_file['href'],
                        "Type": memo_file['type'], 
                        "Description": memo_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }}
                    
                    link_info = self.download_pdf(
                        memo_file['href'], 
                        case_data["Case_No"], 
                        f"memo_{{i+1}}", 
                        worker_id
                    )
                    file_info["Downloaded_Path"] = link_info
                    case_data["Petition_Appeal_Memo"]["Files"].append(file_info)
                
                case_data["Petition_Appeal_Memo"]["File"] = memo_files[0]['href']
                case_data["Petition_Appeal_Memo"]["Type"] = "PDF"
                case_data["Petition_Appeal_Memo"]["Downloaded_Path"] = case_data["Petition_Appeal_Memo"]["Files"][0]["Downloaded_Path"]
            
            # Handle judgment files
            if judgment_files:
                case_data["Judgement_Order"]["Files"] = []
                for i, judgment_file in enumerate(judgment_files):
                    file_info = {{
                        "File": judgment_file['href'],
                        "Type": judgment_file['type'],
                        "Description": judgment_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }}
                    
                    link_info = self.download_pdf(
                        judgment_file['href'], 
                        case_data["Case_No"], 
                        f"judgment_{{i+1}}", 
                        worker_id
                    )
                    file_info["Downloaded_Path"] = link_info
                    case_data["Judgement_Order"]["Files"].append(file_info)
                
                case_data["Judgement_Order"]["File"] = judgment_files[0]['href']
                case_data["Judgement_Order"]["Type"] = "PDF"
                case_data["Judgement_Order"]["Downloaded_Path"] = case_data["Judgement_Order"]["Files"][0]["Downloaded_Path"]
            
            # Extract history
            history_span = soup.find('span', {{'id': 'spnNotFound'}})
            if history_span and 'No Fixation History Found' in history_span.get_text():
                case_data["History"] = [{{"note": "No Fixation History Found"}}]
            else:
                history_div = soup.find('div', {{'id': 'divResult'}})
                if history_div:
                    history_text = history_div.get_text(strip=True)
                    if history_text and "No Fixation History Found" not in history_text:
                        case_data["History"].append({{"note": history_text}})
            
            driver.back()
            time.sleep(1)
            
            print(f"✅ Worker {{worker_id}}: Year {{year}}, Page {{page_number}}, Case {{case_index + 1}} processed - {{case_data['Case_No']}}")
            return case_data
            
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Error processing Year {{year}}, Page {{page_number}}, Case {{case_index + 1}} - {{e}}")
            try:
                driver.back()
                time.sleep(1)
            except:
                pass
            return None
    
    def worker_process_year(self, year, worker_id):
        """Process all cases for a specific year"""
        driver = None
        processed_cases = []
        
        try:
            driver = self.create_optimized_driver(headless=False)
            if not driver:
                print(f"❌ Worker {{worker_id}}: Failed to create driver")
                return []
            
            if not self.navigate_and_search(driver, worker_id, year):
                print(f"❌ Worker {{worker_id}}: Failed to navigate and search for year {{year}}")
                return []
            
            # Check if there are any results
            try:
                no_records = driver.find_element(By.XPATH, "//span[contains(text(), 'No Record Found')]")
                print(f"ℹ️ Worker {{worker_id}}: No records found for year {{year}}")
                return []
            except:
                # Continue - records found
                pass
            
            # Get total pages
            try:
                page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
                total_pages = len(page_links) + 1 if page_links else 1
                print(f"📋 Worker {{worker_id}}: Found {{total_pages}} pages for year {{year}}")
            except:
                total_pages = 1
            
            # Process all pages for this year
            for page_num in range(1, total_pages + 1):
                if page_num > 1:
                    if not self.navigate_to_page(driver, page_num, worker_id):
                        continue
                
                view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                total_cases_on_page = len(view_details_links)
                
                print(f"📋 Worker {{worker_id}}: Processing {{total_cases_on_page}} cases on page {{page_num}} for year {{year}}")
                
                for case_index in range(total_cases_on_page):
                    case_data = self.extract_detailed_case_info(driver, case_index, worker_id, page_num, year)
                    if case_data:
                        processed_cases.append(case_data)
                    
                    time.sleep(0.5)
            
            print(f"✅ Worker {{worker_id}}: Completed year {{year}} - {{len(processed_cases)}} cases")
            return processed_cases
            
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Critical error processing year {{year}} - {{e}}")
            return processed_cases
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def run_extraction(self):
        """Run extraction for all years in this range"""
        print(f"🚀 {{self.case_type_text.upper()}} LAHORE {{self.year_range_name}} EXTRACTOR")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            print(f"\\n📚 Processing {{len(self.years)}} years with {{self.max_workers}} workers...")
            print(f"📊 Years to process: {{self.years}}")
            
            all_results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_year = {{
                    executor.submit(self.worker_process_year, year, f"Y{{year}}"): year
                    for year in self.years
                }}
                
                for future in as_completed(future_to_year):
                    year = future_to_year[future]
                    try:
                        year_results = future.result()
                        all_results.extend(year_results)
                        print(f"✅ Year {{year}} completed: {{len(year_results)}} cases")
                    except Exception as e:
                        print(f"❌ Year {{year}} failed: {{e}}")
            
            self.extracted_cases = all_results
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\\n🎯 EXTRACTION COMPLETED!")
            print(f"   Case Type: {{self.case_type_text}}")
            print(f"   Year Range: {{self.year_range_name}}")
            print(f"   Years Processed: {{len(self.years)}}")
            print(f"   Total Cases: {{len(self.extracted_cases)}}")
            print(f"   Duration: {{duration:.2f}} seconds")
            if self.extracted_cases:
                print(f"   Avg Time/Case: {{duration/len(self.extracted_cases):.2f}} seconds")
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {{e}}")
            return False
    
    def save_results(self):
        """Save results to JSON file"""
        try:
            filename = f"{{self.case_type_text.replace('.', '_').replace('(', '_').replace(')', '_')}}_{self.year_range_name.replace('-', '_')}_complete.json"
            
            # Remove duplicates
            seen_cases = set()
            unique_cases = []
            
            for case in self.extracted_cases:
                case_no = case.get("Case_No", "")
                if case_no and case_no != "N/A" and case_no not in seen_cases:
                    seen_cases.add(case_no)
                    unique_cases.append(case)
            
            unique_cases.sort(key=lambda x: x.get("Case_No", ""))
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {{len(unique_cases)}} unique cases to {{filename}}")
            
            # Save summary
            if unique_cases:
                summary = {{
                    "case_type": self.case_type_text,
                    "year_range": self.year_range_name,
                    "years_processed": self.years,
                    "total_cases": len(unique_cases),
                    "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "pdf_directory": self.downloads_dir
                }}
                
                with open(f"{{filename.replace('.json', '_summary.json')}}", 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                
                print(f"   Summary saved to {{filename.replace('.json', '_summary.json')}}")
                
                # Count PDFs
                pdf_count = 0
                for case in unique_cases:
                    memo_path = case.get('Petition_Appeal_Memo', {{}}).get('Downloaded_Path', '')
                    judgment_path = case.get('Judgement_Order', {{}}).get('Downloaded_Path', '')
                    
                    if memo_path and memo_path != 'No PDF Available' and os.path.exists(memo_path):
                        pdf_count += 1
                    if judgment_path and judgment_path != 'No PDF Available' and os.path.exists(judgment_path):
                        pdf_count += 1
                
                print(f"   PDFs Downloaded: {{pdf_count}}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {{e}}")
            return False


def main():
    """Main function"""
    extractor = {case_folder_name}_{range_name.replace('-', '_')}_Extractor(max_workers=3)
    
    if extractor.run_extraction():
        extractor.save_results()
        print("\\n🎉 Extraction completed successfully!")
    else:
        print("\\n❌ Extraction failed")


if __name__ == "__main__":
    main()
'''
        
        # Write the script
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_file
    
    def create_all_extraction_scripts(self):
        """Create extraction scripts for all case type-year range combinations"""
        print("📝 CREATING EXTRACTION SCRIPTS")
        print("=" * 50)
        
        case_types = self.analysis_data['case_types']
        year_ranges = self.analysis_data['year_ranges']
        
        created_scripts = 0
        
        for case_type in case_types:
            case_text = case_type['text']
            print(f"\n📁 Creating scripts for {case_text}...")
            
            for year_range in year_ranges:
                range_name = year_range['name']
                script_file = self.create_extraction_script(case_type, year_range)
                print(f"   ✅ {script_file.name}")
                created_scripts += 1
        
        print(f"\n🎯 SCRIPT CREATION COMPLETED!")
        print(f"   Total Scripts Created: {created_scripts}")
        print(f"   Structure: {len(case_types)} case types × {len(year_ranges)} year ranges")
        
        return True


def main():
    """Main function"""
    print("🚀 LAHORE SUPREME COURT STRUCTURE MANAGER")
    print("=" * 60)
    
    try:
        manager = LahoreStructureManager()
        
        print("\\nOptions:")
        print("1. Create folder structure only")
        print("2. Create folders and extraction scripts")
        print("3. Create extraction scripts only (folders must exist)")
        
        choice = input("\\nSelect option (1-3): ").strip()
        
        if choice == "1":
            manager.create_folder_structure()
        elif choice == "2":
            manager.create_folder_structure()
            manager.create_all_extraction_scripts()
        elif choice == "3":
            manager.create_all_extraction_scripts()
        else:
            print("Invalid choice")
            return
        
        print("\\n🎉 Structure management completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()