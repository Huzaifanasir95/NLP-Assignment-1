"""
COMPREHENSIVE LAHORE REGISTRY EXTRACTOR
========================================
Extracts ALL cases from Lahore Registry across:
- 35 Case Types (C.A., Crl.A., C.P., H.R.C., etc.)  
- 46 Years (1980-2025)
- All Pages (with pagination handling)
- 1,610 Total Combinations

Uses advanced multi-level parallel processing:
1. Case Type Level: Parallel processing of different case types
2. Year Level: Parallel processing of years within each case type  
3. Page Level: Parallel processing of pages within each year
"""

import time
import re
import json
import os
import requests
import urllib3
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
from datetime import datetime
import logging

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ComprehensiveLahoreExtractor:
    """
    Advanced multi-dimensional extractor for all Lahore cases
    Handles 35 case types × 46 years × multiple pages = massive scale extraction
    """
    
    def __init__(self, max_workers=6, case_types_to_extract=None, years_to_extract=None):
        self.max_workers = max_workers
        self.extracted_cases = []
        self.base_url = "https://scp.gov.pk"
        self.results_lock = threading.Lock()
        
        # Load available options
        try:
            with open('lahore_available_options.json', 'r', encoding='utf-8') as f:
                options_data = json.load(f)
                self.all_case_types = options_data['case_types']
                self.all_years = options_data['years']
        except FileNotFoundError:
            print("❌ lahore_available_options.json not found. Run analyze_available_options.py first.")
            self.all_case_types = []
            self.all_years = []
        
        # Set what to extract (default: all)
        self.case_types_to_extract = case_types_to_extract or self.all_case_types
        self.years_to_extract = years_to_extract or self.all_years
        
        # Results organization
        self.results_dir = "results"
        self.stats = {
            'total_combinations': 0,
            'completed_combinations': 0,
            'total_cases': 0,
            'total_pdfs': 0,
            'start_time': None,
            'errors': []
        }
        
        # Setup logging
        self.setup_logging()
        
        print(f"🚀 COMPREHENSIVE LAHORE EXTRACTOR INITIALIZED")
        print(f"   Case Types: {len(self.case_types_to_extract)}")
        print(f"   Years: {len(self.years_to_extract)}")
        print(f"   Total Combinations: {len(self.case_types_to_extract) * len(self.years_to_extract)}")
        print(f"   Max Workers: {max_workers}")
        print(f"   Results Directory: {self.results_dir}")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('lahore_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_optimized_driver(self, headless=True):
        """Create optimized Chrome WebDriver for speed"""
        try:
            options = Options()
            
            # Performance optimizations
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
            
            # Disable resource loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.media_stream": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(5)
            
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create driver: {e}")
            return None
    
    def navigate_to_page(self, driver, page_number, worker_id):
        """Navigate to a specific page"""
        try:
            if page_number == 1:
                return True
            
            # Find and click the page link
            page_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[text()='{page_number}']"))
            )
            driver.execute_script("arguments[0].click();", page_link)
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Worker {worker_id}: Failed to navigate to page {page_number} - {e}")
            return False
    
    def navigate_and_search(self, driver, case_type_value, year_value, worker_id):
        """Navigate to website and perform search for specific case type and year"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
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
            select.select_by_value(case_type_value)
            time.sleep(1)
            
            # Select registry: Lahore
            registry_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
            )
            select = Select(registry_select)
            select.select_by_value('L')  # Lahore
            time.sleep(1)
            
            # Select year
            year_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlYear'))
            )
            select = Select(year_select)
            select.select_by_value(year_value)
            time.sleep(1)
            
            # Click search button
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'btnSearch'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Search failed for case type {case_type_value}, year {year_value} - {e}")
            return False
    
    def handle_form_resubmission(self, driver):
        """Handle form resubmission error"""
        try:
            page_source = driver.page_source.lower()
            
            if ("confirm form resubmission" in page_source or 
                "err_cache_miss" in page_source or
                "resubmit" in page_source):
                
                driver.refresh()
                time.sleep(2)
                return True
            
            return False
        except Exception as e:
            return False
    
    def download_pdf(self, pdf_url, case_no, pdf_type, worker_id):
        """Store PDF link information without downloading"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            # Make URL absolute if relative
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            return f"PDF Link Available: {pdf_url}"
            
        except Exception as e:
            return f"Link Processing Failed: {str(e)}"
    
    def extract_detailed_case_info(self, driver, case_index, worker_id, case_type_text, year, page_number):
        """Extract detailed case information for a specific case"""
        try:
            # Get View Details links
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                return None
            
            # Click View Details
            link = view_details_links[case_index]
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(2)
            
            # Extract information using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Initialize case structure
            case_data = {
                "Case_Number": "N/A",
                "Case_Title": "N/A", 
                "Status": "N/A",
                "Institution_Date": "N/A",
                "Disposal_Date": "N/A",
                "Case_Type": case_type_text,
                "Year": year,
                "Registry": "Lahore",
                "Page_Number": page_number,
                "Advocates": {
                    "ASC": "N/A",
                    "AOR": "N/A",
                    "Prosecutor": "N/A"
                },
                "Petition_Appeal_Memo": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available"
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available"
                },
                "Extra_PDFs": [],
                "Worker_ID": worker_id,
                "Extraction_Timestamp": datetime.now().isoformat()
            }
            
            # Extract basic information
            case_no_span = soup.find('span', {'id': 'spCaseNo'})
            if case_no_span:
                case_data["Case_Number"] = case_no_span.get_text(strip=True)
            
            case_title_span = soup.find('span', {'id': 'spCaseTitle'})
            if case_title_span:
                case_data["Case_Title"] = case_title_span.get_text(strip=True)
            
            status_span = soup.find('span', {'id': 'spStatus'})
            if status_span:
                case_data["Status"] = status_span.get_text(strip=True)
            
            inst_date_span = soup.find('span', {'id': 'spInstDate'})
            if inst_date_span:
                case_data["Institution_Date"] = inst_date_span.get_text(strip=True)
            
            disp_date_span = soup.find('span', {'id': 'spDispDate'})
            if disp_date_span:
                case_data["Disposal_Date"] = disp_date_span.get_text(strip=True)
            
            # Extract advocates
            aor_span = soup.find('span', {'id': 'spAOR'})
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
                    lines = aor_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if '(AOR)' in line:
                            case_data["Advocates"]["AOR"] = line
                        elif '(ASC)' in line:
                            case_data["Advocates"]["ASC"] = line
                        elif 'prosecutor' in line.lower():
                            case_data["Advocates"]["Prosecutor"] = line
            
            # Enhanced PDF detection
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
                        memo_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
                    elif any(keyword in link_text.lower() for keyword in ['judgment', 'order']):
                        judgment_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
                    else:
                        memo_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
            
            # Handle memo files
            if memo_files:
                for i, memo_file in enumerate(memo_files):
                    link_info = self.download_pdf(
                        memo_file['href'], 
                        case_data["Case_Number"], 
                        f"memo_{i+1}", 
                        worker_id
                    )
                    
                    if i == 0:  # First memo is main
                        case_data["Petition_Appeal_Memo"]["File"] = memo_file['href']
                        case_data["Petition_Appeal_Memo"]["Type"] = "PDF"
                        case_data["Petition_Appeal_Memo"]["Downloaded_Path"] = link_info
                    else:  # Additional memos go to extra
                        case_data["Extra_PDFs"].append({
                            "File": memo_file['href'],
                            "Type": "Memo PDF",
                            "Description": memo_file['text'],
                            "Downloaded_Path": link_info
                        })
            
            # Handle judgment files
            if judgment_files:
                for i, judgment_file in enumerate(judgment_files):
                    link_info = self.download_pdf(
                        judgment_file['href'], 
                        case_data["Case_Number"], 
                        f"judgment_{i+1}", 
                        worker_id
                    )
                    
                    if i == 0:  # First judgment is main
                        case_data["Judgement_Order"]["File"] = judgment_file['href']
                        case_data["Judgement_Order"]["Type"] = "PDF"
                        case_data["Judgement_Order"]["Downloaded_Path"] = link_info
                    else:  # Additional judgments go to extra
                        case_data["Extra_PDFs"].append({
                            "File": judgment_file['href'],
                            "Type": "Judgment PDF",
                            "Description": judgment_file['text'],
                            "Downloaded_Path": link_info
                        })
            
            # Extract history
            history_span = soup.find('span', {'id': 'spnNotFound'})
            if history_span and 'No Fixation History Found' in history_span.get_text():
                case_data["History"] = [{"note": "No Fixation History Found"}]
            else:
                history_div = soup.find('div', {'id': 'divResult'})
                if history_div:
                    history_text = history_div.get_text(strip=True)
                    if history_text and "No Fixation History Found" not in history_text:
                        case_data["History"].append({"note": history_text})
            
            # Navigate back
            driver.back()
            time.sleep(1)
            self.handle_form_resubmission(driver)
            
            return case_data
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Error processing case {case_index + 1} - {e}")
            try:
                driver.back()
                time.sleep(1)
                self.handle_form_resubmission(driver)
            except:
                pass
            return None
    
    def get_total_pages(self, driver):
        """Get total number of pages for current search"""
        try:
            # Check if there are page links
            page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
            if not page_links:
                return 1  # Only one page
            
            # Extract page numbers and find max
            page_numbers = []
            for link in page_links:
                try:
                    page_num = int(link.text.strip())
                    page_numbers.append(page_num)
                except:
                    continue
            
            return max(page_numbers) if page_numbers else 1
            
        except Exception as e:
            return 1
    
    def worker_process_combination(self, case_type, year, worker_id):
        """Worker function to process one case type-year combination"""
        driver = None
        processed_cases = []
        
        case_type_value = case_type['value']
        case_type_text = case_type['text']
        year_value = year['value']
        year_text = year['text']
        
        combination_id = f"{case_type_text}_{year_text}"
        
        try:
            self.logger.info(f"Worker {worker_id}: Starting {combination_id}")
            
            # Create driver
            driver = self.create_optimized_driver(headless=True)
            if not driver:
                return []
            
            # Navigate and search
            if not self.navigate_and_search(driver, case_type_value, year_value, worker_id):
                return []
            
            # Check if any results found
            page_source = driver.page_source.lower()
            if "no record found" in page_source or "no records found" in page_source:
                self.logger.info(f"Worker {worker_id}: No records for {combination_id}")
                return []
            
            # Get total pages
            total_pages = self.get_total_pages(driver)
            self.logger.info(f"Worker {worker_id}: {combination_id} has {total_pages} pages")
            
            # Process all pages
            for page_num in range(1, total_pages + 1):
                # Navigate to page
                if not self.navigate_to_page(driver, page_num, worker_id):
                    continue
                
                # Get cases on this page
                view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                total_cases_on_page = len(view_details_links)
                
                self.logger.info(f"Worker {worker_id}: {combination_id} page {page_num} has {total_cases_on_page} cases")
                
                # Process all cases on this page
                for case_index in range(total_cases_on_page):
                    case_data = self.extract_detailed_case_info(
                        driver, case_index, worker_id, case_type_text, year_text, page_num
                    )
                    if case_data:
                        processed_cases.append(case_data)
                    
                    time.sleep(0.3)  # Small delay
            
            self.logger.info(f"Worker {worker_id}: Completed {combination_id} - {len(processed_cases)} cases")
            
            # Save results for this combination immediately
            self.save_combination_results(case_type_text, year_text, processed_cases)
            
            return processed_cases
            
        except Exception as e:
            self.logger.error(f"Worker {worker_id}: Critical error in {combination_id} - {e}")
            self.stats['errors'].append(f"{combination_id}: {str(e)}")
            return processed_cases
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def save_combination_results(self, case_type, year, cases):
        """Save results for a specific case type-year combination"""
        try:
            if not cases:
                return
            
            filename = f"{self.results_dir}/{case_type}_{year}_lahore.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cases, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(cases)} cases to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save {case_type}_{year}: {e}")
    
    def run_comprehensive_extraction(self):
        """Run the comprehensive extraction across all case types and years"""
        print("\n🚀 STARTING COMPREHENSIVE LAHORE EXTRACTION")
        print("=" * 80)
        
        self.stats['start_time'] = time.time()
        self.stats['total_combinations'] = len(self.case_types_to_extract) * len(self.years_to_extract)
        
        print(f"📊 EXTRACTION SCOPE:")
        print(f"   Case Types: {len(self.case_types_to_extract)}")
        print(f"   Years: {len(self.years_to_extract)}")
        print(f"   Total Combinations: {self.stats['total_combinations']}")
        print(f"   Workers: {self.max_workers}")
        
        # Create all combinations
        combinations = []
        for case_type in self.case_types_to_extract:
            for year in self.years_to_extract:
                combinations.append((case_type, year))
        
        print(f"\n🔄 Processing {len(combinations)} combinations...")
        
        # Process combinations in parallel
        all_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all combination tasks
            future_to_combination = {
                executor.submit(
                    self.worker_process_combination, 
                    case_type, 
                    year, 
                    f"W{i % self.max_workers + 1}"
                ): (case_type, year, i)
                for i, (case_type, year) in enumerate(combinations)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_combination):
                case_type, year, combination_index = future_to_combination[future]
                try:
                    combination_results = future.result()
                    all_results.extend(combination_results)
                    
                    self.stats['completed_combinations'] += 1
                    self.stats['total_cases'] += len(combination_results)
                    
                    progress = (self.stats['completed_combinations'] / self.stats['total_combinations']) * 100
                    elapsed = time.time() - self.stats['start_time']
                    
                    print(f"✅ [{self.stats['completed_combinations']}/{self.stats['total_combinations']}] "
                          f"{case_type['text']}_{year['text']}: {len(combination_results)} cases "
                          f"({progress:.1f}% complete, {elapsed/60:.1f}min elapsed)")
                    
                except Exception as e:
                    self.logger.error(f"Combination {case_type['text']}_{year['text']} failed: {e}")
        
        self.extracted_cases = all_results
        
        # Final statistics
        end_time = time.time()
        duration = end_time - self.stats['start_time']
        
        print(f"\n🎯 COMPREHENSIVE EXTRACTION COMPLETED!")
        print(f"   Combinations Processed: {self.stats['completed_combinations']}/{self.stats['total_combinations']}")
        print(f"   Total Cases Extracted: {self.stats['total_cases']}")
        print(f"   Total Time: {duration/60:.1f} minutes")
        print(f"   Average per Combination: {duration/max(1, self.stats['completed_combinations']):.2f} seconds")
        print(f"   Errors: {len(self.stats['errors'])}")
        
        return True
    
    def save_master_results(self, filename="lahore_comprehensive_results.json"):
        """Save master results file"""
        try:
            # Remove duplicates and sort
            seen_cases = set()
            unique_cases = []
            
            for case in self.extracted_cases:
                case_id = f"{case.get('Case_Number', '')}_{case.get('Year', '')}"
                if case_id not in seen_cases:
                    seen_cases.add(case_id)
                    unique_cases.append(case)
            
            # Sort by case type, year, and case number
            unique_cases.sort(key=lambda x: (
                x.get("Case_Type", ""),
                x.get("Year", ""),
                x.get("Case_Number", "")
            ))
            
            # Save master file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Master results saved: {filename} ({len(unique_cases)} unique cases)")
            
            # Generate comprehensive summary
            self.generate_summary_report(unique_cases)
            
        except Exception as e:
            self.logger.error(f"Failed to save master results: {e}")
    
    def generate_summary_report(self, cases):
        """Generate comprehensive summary report"""
        try:
            summary = {
                "extraction_date": datetime.now().isoformat(),
                "total_cases": len(cases),
                "total_combinations_processed": self.stats['completed_combinations'],
                "extraction_duration_minutes": (time.time() - self.stats['start_time']) / 60,
                "case_types_summary": {},
                "years_summary": {},
                "pdf_statistics": {
                    "cases_with_memo_pdfs": 0,
                    "cases_with_judgment_pdfs": 0,
                    "total_pdf_links": 0
                },
                "errors": self.stats['errors']
            }
            
            # Analyze by case type and year
            for case in cases:
                case_type = case.get('Case_Type', 'Unknown')
                year = case.get('Year', 'Unknown')
                
                # Case type stats
                if case_type not in summary["case_types_summary"]:
                    summary["case_types_summary"][case_type] = 0
                summary["case_types_summary"][case_type] += 1
                
                # Year stats
                if year not in summary["years_summary"]:
                    summary["years_summary"][year] = 0
                summary["years_summary"][year] += 1
                
                # PDF stats
                memo_path = case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', '')
                judgment_path = case.get('Judgement_Order', {}).get('Downloaded_Path', '')
                
                if 'PDF Link Available' in memo_path:
                    summary["pdf_statistics"]["cases_with_memo_pdfs"] += 1
                    summary["pdf_statistics"]["total_pdf_links"] += 1
                    
                if 'PDF Link Available' in judgment_path:
                    summary["pdf_statistics"]["cases_with_judgment_pdfs"] += 1
                    summary["pdf_statistics"]["total_pdf_links"] += 1
                
                # Extra PDFs
                extra_pdfs = case.get('Extra_PDFs', [])
                for extra in extra_pdfs:
                    if 'PDF Link Available' in extra.get('Downloaded_Path', ''):
                        summary["pdf_statistics"]["total_pdf_links"] += 1
            
            # Save summary
            with open('lahore_extraction_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 EXTRACTION SUMMARY:")
            print(f"   Total Cases: {summary['total_cases']:,}")
            print(f"   Case Types Covered: {len(summary['case_types_summary'])}")
            print(f"   Years Covered: {len(summary['years_summary'])}")
            print(f"   PDF Links Captured: {summary['pdf_statistics']['total_pdf_links']:,}")
            print(f"   Duration: {summary['extraction_duration_minutes']:.1f} minutes")
            print(f"   Summary saved: lahore_extraction_summary.json")
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")


def main():
    """Main function with configuration options"""
    print("🚀 COMPREHENSIVE LAHORE REGISTRY EXTRACTOR")
    print("=" * 60)
    
    # Configuration options
    print("\nConfiguration Options:")
    print("1. Extract ALL case types and years (1980-2025)")
    print("2. Extract specific case types only")
    print("3. Extract specific years only")
    print("4. Extract recent years only (2020-2025)")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    case_types_filter = None
    years_filter = None
    
    if choice == "2":
        # Specific case types
        print("\nPopular case types:")
        print("1: C.A. (Civil Appeals)")
        print("2: Crl.A. (Criminal Appeals)")
        print("13: C.P. (Civil Petitions)")
        print("15: H.R.C. (Human Rights Cases)")
        case_type_input = input("Enter case type values (comma-separated): ").strip()
        if case_type_input:
            selected_values = [v.strip() for v in case_type_input.split(',')]
            # Load all case types to filter
            with open('lahore_available_options.json', 'r') as f:
                options = json.load(f)
            case_types_filter = [ct for ct in options['case_types'] if ct['value'] in selected_values]
    
    elif choice == "3":
        # Specific years
        year_input = input("Enter years (comma-separated, e.g., 2023,2024,2025): ").strip()
        if year_input:
            selected_years = [y.strip() for y in year_input.split(',')]
            years_filter = [{'value': y, 'text': y} for y in selected_years]
    
    elif choice == "4":
        # Recent years only
        years_filter = [{'value': str(y), 'text': str(y)} for y in range(2020, 2026)]
    
    # Create extractor
    extractor = ComprehensiveLahoreExtractor(
        max_workers=6,
        case_types_to_extract=case_types_filter,
        years_to_extract=years_filter
    )
    
    # Confirm before starting
    total_combinations = len(extractor.case_types_to_extract) * len(extractor.years_to_extract)
    estimated_time = total_combinations * 30 / 60  # Rough estimate: 30 seconds per combination
    
    print(f"\n⚠️  EXTRACTION PREVIEW:")
    print(f"   Total combinations: {total_combinations}")
    print(f"   Estimated time: {estimated_time:.1f} minutes")
    print(f"   This will create individual files for each case type-year combination")
    
    confirm = input("\nProceed with extraction? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Extraction cancelled.")
        return
    
    # Run extraction
    if extractor.run_comprehensive_extraction():
        extractor.save_master_results()
        print(f"\n🎉 COMPREHENSIVE LAHORE EXTRACTION COMPLETED!")
        print(f"   Individual results: {extractor.results_dir}/")
        print(f"   Master file: lahore_comprehensive_results.json")
        print(f"   Summary: lahore_extraction_summary.json")
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    main()