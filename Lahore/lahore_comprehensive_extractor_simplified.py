"""
Comprehensive Lahore Registry Extractor - Using Proven Technique
================================================================
Based on the successful paginated_multi_browser_ca_lahore_2025_extractor.py
Extracts ALL cases from Lahore Registry across all case types and years
Uses the SAME proven multi-browser technique with single output file
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

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ComprehensiveLahoreExtractor:
    """
    Comprehensive Lahore extractor using the SAME proven technique
    Processes all case types and years with multi-browser parallel processing
    """
    
    def __init__(self, max_workers=6):
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
            return
        
        # Generate all combinations to process
        self.combinations_to_process = []
        for case_type in self.all_case_types:
            for year in self.all_years:
                self.combinations_to_process.append({
                    'case_type_value': case_type['value'],
                    'case_type_text': case_type['text'],
                    'year_value': year['value'],
                    'year_text': year['text']
                })
        
        # Create results directory info (no actual downloads)
        self.downloads_dir = "lahore_comprehensive_pdf_links"
        print(f"📋 PDF links will be captured (no downloads) in: {self.downloads_dir}")
        
        print(f"✅ Comprehensive Lahore Extractor initialized")
        print(f"   Case Types: {len(self.all_case_types)}")
        print(f"   Years: {len(self.all_years)}")
        print(f"   Total Combinations: {len(self.combinations_to_process)}")
        print(f"   Max Workers: {max_workers}")
    
    def create_optimized_driver(self, headless=False):
        """Create optimized Chrome WebDriver for speed - SAME as working extractor"""
        try:
            options = Options()
            
            # Performance optimizations - keep JavaScript enabled for functionality
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            # Keep JavaScript enabled for proper functionality
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
            print(f"❌ Failed to create driver: {e}")
            return None
    
    def navigate_to_page(self, driver, page_number, worker_id):
        """Navigate to a specific page - SAME as working extractor"""
        try:
            if page_number == 1:
                # Already on page 1 after search
                return True
            
            print(f"🔄 Worker {worker_id}: Navigating to page {page_number}")
            
            # Find and click the page link
            page_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[text()='{page_number}']"))
            )
            driver.execute_script("arguments[0].click();", page_link)
            time.sleep(3)
            
            print(f"✅ Worker {worker_id}: Successfully navigated to page {page_number}")
            return True
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Failed to navigate to page {page_number} - {e}")
            return False
    
    def navigate_and_search(self, driver, case_type_value, year_value, worker_id):
        """Navigate to website and perform search - SAME technique, different parameters"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Worker {worker_id}: Navigating to website")
            driver.get(url)
            time.sleep(3)
            
            # Wait for page to load completely
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
            
            # Click search button with better handling
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'btnSearch'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", search_button)
            print(f"🔍 Worker {worker_id}: Search button clicked")
            time.sleep(5)
            
            print(f"✅ Worker {worker_id}: Search completed")
            return True
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Search failed - {e}")
            return False
    
    def handle_form_resubmission(self, driver):
        """Handle form resubmission error - SAME as working extractor"""
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
        """Store PDF link information without downloading - SAME as working extractor"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            # Make URL absolute if relative
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            # Return the link without downloading
            return f"PDF Link Available: {pdf_url}"
            
        except Exception as e:
            return f"Link Processing Failed: {str(e)}"
    
    def extract_detailed_case_info(self, driver, case_index, worker_id, case_type_text, year_text, page_number):
        """Extract detailed case information - SAME technique as working extractor"""
        try:
            print(f"🔍 Worker {worker_id}: Processing {case_type_text} {year_text}, Page {page_number}, Case {case_index + 1}")
            
            # Get View Details links
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Worker {worker_id}: Case index {case_index} out of range")
                return None
            
            # Click View Details
            link = view_details_links[case_index]
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(2)
            
            # Extract information using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Initialize case structure - SAME as working extractor with additions
            case_data = {
                "Case_Number": "N/A",
                "Case_Title": "N/A", 
                "Status": "N/A",
                "Institution_Date": "N/A",
                "Disposal_Date": "N/A",
                "Case_Type": case_type_text,
                "Year": year_text,
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
            
            # Extract Case No from spCaseNo - SAME as working extractor
            case_no_span = soup.find('span', {'id': 'spCaseNo'})
            if case_no_span:
                case_data["Case_Number"] = case_no_span.get_text(strip=True)
            
            # Extract Case Title from spCaseTitle - SAME as working extractor  
            case_title_span = soup.find('span', {'id': 'spCaseTitle'})
            if case_title_span:
                case_data["Case_Title"] = case_title_span.get_text(strip=True)
            
            # Extract Status from spStatus - SAME as working extractor
            status_span = soup.find('span', {'id': 'spStatus'})
            if status_span:
                case_data["Status"] = status_span.get_text(strip=True)
            
            # Extract Institution Date from spInstDate - SAME as working extractor
            inst_date_span = soup.find('span', {'id': 'spInstDate'})
            if inst_date_span:
                case_data["Institution_Date"] = inst_date_span.get_text(strip=True)
            
            # Extract Disposal Date from spDispDate - SAME as working extractor
            disp_date_span = soup.find('span', {'id': 'spDispDate'})
            if disp_date_span:
                case_data["Disposal_Date"] = disp_date_span.get_text(strip=True)
            
            # Extract AOR/ASC from spAOR - SAME as working extractor
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
            
            # Enhanced PDF detection and capture - SAME as working extractor
            pdf_links = soup.find_all('a', href=True)
            
            # Collect all PDF files
            memo_files = []
            judgment_files = []
            
            for link in pdf_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                # Enhanced detection for PDF links
                if (href and 
                    ('.pdf' in href.lower() or 
                     'digital copy' in link_text.lower() or
                     ('file' in link_text.lower() and '.pdf' in href.lower()))):
                    
                    # Classify PDF type based on context and text
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
                        # Default to memo if unclear
                        memo_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
            
            # Handle memo files - SAME technique as working extractor
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
            
            # Handle judgment files - SAME technique as working extractor
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
            
            # Extract history - SAME as working extractor
            history_span = soup.find('span', {'id': 'spnNotFound'})
            if history_span and 'No Fixation History Found' in history_span.get_text():
                case_data["History"] = [{"note": "No Fixation History Found"}]
            else:
                history_div = soup.find('div', {'id': 'divResult'})
                if history_div:
                    history_text = history_div.get_text(strip=True)
                    if history_text and "No Fixation History Found" not in history_text:
                        case_data["History"].append({"note": history_text})
            
            # Navigate back - SAME as working extractor
            driver.back()
            time.sleep(1)
            
            # Handle potential form resubmission
            self.handle_form_resubmission(driver)
            
            print(f"✅ Worker {worker_id}: Processed {case_data['Case_Number']}")
            return case_data
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error processing case {case_index + 1} - {e}")
            try:
                driver.back()
                time.sleep(1)
                self.handle_form_resubmission(driver)
            except:
                pass
            return None
    
    def get_total_pages(self, driver):
        """Get total number of pages - SAME as working extractor"""
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
    
    def worker_process_combination(self, combination, worker_id):
        """Worker function to process one case type-year combination"""
        driver = None
        processed_cases = []
        
        case_type_value = combination['case_type_value']
        case_type_text = combination['case_type_text']
        year_value = combination['year_value']
        year_text = combination['year_text']
        
        combination_id = f"{case_type_text}_{year_text}"
        
        try:
            print(f"🔍 Worker {worker_id}: Starting {combination_id}")
            
            # Create optimized driver for this worker
            driver = self.create_optimized_driver(headless=False)
            if not driver:
                print(f"❌ Worker {worker_id}: Failed to create driver")
                return []
            
            # Navigate and search
            if not self.navigate_and_search(driver, case_type_value, year_value, worker_id):
                print(f"❌ Worker {worker_id}: Failed to navigate and search for {combination_id}")
                return []
            
            # Check if any results found
            page_source = driver.page_source.lower()
            if "no record found" in page_source or "no records found" in page_source:
                print(f"ℹ️ Worker {worker_id}: No records found for {combination_id}")
                return []
            
            # Get total pages for this combination
            total_pages = self.get_total_pages(driver)
            print(f"📚 Worker {worker_id}: {combination_id} has {total_pages} pages")
            
            # Process all pages for this combination
            for page_num in range(1, total_pages + 1):
                # Navigate to the page
                if not self.navigate_to_page(driver, page_num, worker_id):
                    continue
                
                # Get all cases on this page
                view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                total_cases_on_page = len(view_details_links)
                
                print(f"📋 Worker {worker_id}: {combination_id} page {page_num} has {total_cases_on_page} cases")
                
                # Process all cases on this page
                for case_index in range(total_cases_on_page):
                    case_data = self.extract_detailed_case_info(
                        driver, case_index, worker_id, case_type_text, year_text, page_num
                    )
                    if case_data:
                        processed_cases.append(case_data)
                    
                    # Small delay between cases
                    time.sleep(0.3)
            
            print(f"✅ Worker {worker_id}: Completed {combination_id} - {len(processed_cases)} cases")
            return processed_cases
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Critical error processing {combination_id} - {e}")
            return processed_cases
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def run_comprehensive_extraction(self):
        """Run comprehensive extraction across all combinations - SAME parallel approach"""
        print("🚀 COMPREHENSIVE LAHORE EXTRACTOR - USING PROVEN TECHNIQUE")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            total_combinations = len(self.combinations_to_process)
            print(f"\n📊 EXTRACTION SCOPE:")
            print(f"   Total Combinations: {total_combinations}")
            print(f"   Workers: {self.max_workers}")
            print(f"   Output: Single comprehensive file")
            
            print(f"\n🔄 Processing {total_combinations} combinations...")
            
            # Process combinations in parallel - SAME technique as working extractor
            all_results = []
            completed_combinations = 0
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all combination tasks
                future_to_combination = {
                    executor.submit(self.worker_process_combination, combination, f"W{i % self.max_workers + 1}"): (combination, i)
                    for i, combination in enumerate(self.combinations_to_process)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_combination):
                    combination, combination_index = future_to_combination[future]
                    try:
                        combination_results = future.result()
                        all_results.extend(combination_results)
                        
                        completed_combinations += 1
                        progress = (completed_combinations / total_combinations) * 100
                        elapsed = time.time() - start_time
                        
                        print(f"✅ [{completed_combinations}/{total_combinations}] "
                              f"{combination['case_type_text']}_{combination['year_text']}: {len(combination_results)} cases "
                              f"({progress:.1f}% complete, {elapsed/60:.1f}min elapsed)")
                        
                    except Exception as e:
                        print(f"❌ Combination failed: {e}")
            
            self.extracted_cases = all_results
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🎯 COMPREHENSIVE EXTRACTION COMPLETED!")
            print(f"   Combinations Processed: {completed_combinations}/{total_combinations}")
            print(f"   Total Cases Extracted: {len(self.extracted_cases)}")
            print(f"   Total Time: {duration/60:.1f} minutes")
            print(f"   Average per Combination: {duration/max(1, completed_combinations):.2f} seconds")
            
            return True
            
        except Exception as e:
            print(f"❌ Comprehensive extraction failed: {e}")
            return False
    
    def save_results(self, filename="lahore_comprehensive_cases.json"):
        """Save results to single JSON file - SAME technique as working extractor"""
        try:
            # Remove duplicates based on Case_Number and Year
            seen_cases = set()
            unique_cases = []
            
            for case in self.extracted_cases:
                case_id = f"{case.get('Case_Number', '')}-{case.get('Year', '')}"
                if case_id not in seen_cases and case.get('Case_Number', '') != 'N/A':
                    seen_cases.add(case_id)
                    unique_cases.append(case)
            
            # Sort by case type, year, and case number
            unique_cases.sort(key=lambda x: (
                x.get("Case_Type", ""),
                x.get("Year", ""),
                x.get("Case_Number", "")
            ))
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(unique_cases)} unique cases to {filename}")
            
            # Show summary - SAME as working extractor
            if unique_cases:
                print(f"\n📋 COMPREHENSIVE LAHORE EXTRACTION SUMMARY:")
                print(f"   Total Unique Cases: {len(unique_cases)}")
                print(f"   PDF Links Captured: {self.downloads_dir}")
                
                # Count by case type and year
                case_type_counts = {}
                year_counts = {}
                pdf_count = 0
                memo_pdfs = 0
                judgment_pdfs = 0
                
                for case in unique_cases:
                    case_type = case.get('Case_Type', 'Unknown')
                    year = case.get('Year', 'Unknown')
                    
                    case_type_counts[case_type] = case_type_counts.get(case_type, 0) + 1
                    year_counts[year] = year_counts.get(year, 0) + 1
                    
                    memo_path = case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', '')
                    judgment_path = case.get('Judgement_Order', {}).get('Downloaded_Path', '')
                    
                    if memo_path and memo_path != 'No PDF Available' and 'PDF Link Available' in memo_path:
                        memo_pdfs += 1
                    if judgment_path and judgment_path != 'No PDF Available' and 'PDF Link Available' in judgment_path:
                        judgment_pdfs += 1
                    
                    # Count extra PDFs
                    for extra in case.get('Extra_PDFs', []):
                        if 'PDF Link Available' in extra.get('Downloaded_Path', ''):
                            pdf_count += 1
                
                print(f"   Cases with Memo PDFs: {memo_pdfs}")
                print(f"   Cases with Judgment PDFs: {judgment_pdfs}")
                print(f"   Extra PDF Links: {pdf_count}")
                
                print(f"\n📄 Top Case Types:")
                top_case_types = sorted(case_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for case_type, count in top_case_types:
                    print(f"   {case_type}: {count} cases")
                
                print(f"\n📅 Recent Years:")
                recent_years = sorted(year_counts.items(), key=lambda x: x[0], reverse=True)[:10]
                for year, count in recent_years:
                    print(f"   {year}: {count} cases")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False


def main():
    """Main function"""
    print("🚀 COMPREHENSIVE LAHORE REGISTRY EXTRACTOR")
    print("=" * 60)
    print("Using the SAME proven technique as C.A. Lahore 2025 extractor")
    
    # Configuration options
    print("\nConfiguration Options:")
    print("1. Extract ALL case types and years (1980-2025) - FULL EXTRACTION")
    print("2. Extract recent years only (2020-2025)")
    print("3. Extract specific case types only")
    print("4. Test run (2 case types, 2 years)")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    # Create base extractor
    extractor = ComprehensiveLahoreExtractor(max_workers=6)
    
    if choice == "2":
        # Recent years only
        recent_years = [y for y in extractor.all_years if int(y['value']) >= 2020]
        extractor.combinations_to_process = []
        for case_type in extractor.all_case_types:
            for year in recent_years:
                extractor.combinations_to_process.append({
                    'case_type_value': case_type['value'],
                    'case_type_text': case_type['text'],
                    'year_value': year['value'],
                    'year_text': year['text']
                })
        print(f"   Reduced to {len(extractor.combinations_to_process)} combinations (recent years)")
    
    elif choice == "3":
        # Specific case types
        print("\nPopular case types:")
        print("1: C.A. (Civil Appeals)")
        print("2: Crl.A. (Criminal Appeals)")
        print("13: C.P. (Civil Petitions)")
        print("15: H.R.C. (Human Rights Cases)")
        case_type_input = input("Enter case type values (comma-separated): ").strip()
        if case_type_input:
            selected_values = [v.strip() for v in case_type_input.split(',')]
            selected_case_types = [ct for ct in extractor.all_case_types if ct['value'] in selected_values]
            extractor.combinations_to_process = []
            for case_type in selected_case_types:
                for year in extractor.all_years:
                    extractor.combinations_to_process.append({
                        'case_type_value': case_type['value'],
                        'case_type_text': case_type['text'],
                        'year_value': year['value'],
                        'year_text': year['text']
                    })
            print(f"   Reduced to {len(extractor.combinations_to_process)} combinations")
    
    elif choice == "4":
        # Test run
        test_case_types = [
            {'value': '1', 'text': 'C.A.'},
            {'value': '2', 'text': 'Crl.A.'}
        ]
        test_years = [
            {'value': '2025', 'text': '2025'},
            {'value': '2024', 'text': '2024'}
        ]
        extractor.combinations_to_process = []
        for case_type in test_case_types:
            for year in test_years:
                extractor.combinations_to_process.append({
                    'case_type_value': case_type['value'],
                    'case_type_text': case_type['text'],
                    'year_value': year['value'],
                    'year_text': year['text']
                })
        print(f"   Test run: {len(extractor.combinations_to_process)} combinations")
    
    # Show final configuration
    total_combinations = len(extractor.combinations_to_process)
    estimated_time = total_combinations * 15 / 60  # 15 seconds per combination estimate
    
    print(f"\n⚠️  EXTRACTION PREVIEW:")
    print(f"   Total combinations: {total_combinations}")
    print(f"   Estimated time: {estimated_time:.1f} minutes")
    print(f"   Output: Single comprehensive JSON file")
    print(f"   Using PROVEN technique from working C.A. extractor")
    
    confirm = input("\nProceed with extraction? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Extraction cancelled.")
        return
    
    # Run extraction
    if extractor.run_comprehensive_extraction():
        extractor.save_results()
        print(f"\n🎉 COMPREHENSIVE LAHORE EXTRACTION COMPLETED!")
        print(f"   Output file: lahore_comprehensive_cases.json")
        print(f"   Using the SAME proven technique as C.A. Lahore 2025 extractor")
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    main()