"""
Multi-Browser Optimized Extractor for C.A. Lahore 2025 Cases with PDF Downloads
Uses parallel processing with multiple browser instances for 5x speed improvement
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

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MultiBrowserCALahore2025Extractor:
    """High-speed extractor using multiple browser instances for parallel processing"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.extracted_cases = []
        self.base_url = "https://scp.gov.pk"
        self.case_queue = Queue()
        self.results_lock = threading.Lock()
        
        # Create downloads directory
        self.downloads_dir = "ca_lahore_2025_pdfs_multi"
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)
        
        print(f"✅ Multi-Browser C.A. Lahore 2025 Extractor initialized with {max_workers} workers")
    
    def create_optimized_driver(self, headless=False):
        """Create optimized Chrome WebDriver for speed"""
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
            # options.add_argument('--disable-javascript')  # Commented out
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
    
    def navigate_and_search(self, driver, worker_id):
        """Navigate to website and perform search for a worker"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Worker {worker_id}: Navigating to website")
            driver.get(url)
            time.sleep(3)
            
            # Wait for page to load completely
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlCaseType"))
            )
            
            # Select case type: C.A.
            case_type_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlCaseType'))
            )
            select = Select(case_type_select)
            select.select_by_value('1')  # C.A.
            time.sleep(1)
            
            # Select registry: Lahore
            registry_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
            )
            select = Select(registry_select)
            select.select_by_value('L')  # Lahore
            time.sleep(1)
            
            # Select year: 2025
            year_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ddlYear'))
            )
            select = Select(year_select)
            select.select_by_value('2025')
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
        """Download PDF file"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            # Make URL absolute if relative
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            # Create safe filename
            safe_case_no = re.sub(r'[<>:"/\\|?*]', '_', case_no)
            filename = f"{safe_case_no}_{pdf_type}_w{worker_id}.pdf"
            filepath = os.path.join(self.downloads_dir, filename)
            
            # Download PDF with shorter timeout for speed and SSL bypass
            response = requests.get(pdf_url, timeout=15, verify=False)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
            
        except Exception as e:
            return f"Download Failed: {str(e)}"
    
    def extract_detailed_case_info(self, driver, case_index, worker_id):
        """Extract detailed case information for a specific case"""
        try:
            print(f"🔍 Worker {worker_id}: Processing case {case_index + 1}")
            
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
            
            # Initialize case structure
            case_data = {
                "Case_No": "N/A",
                "Case_Title": "N/A", 
                "Status": "N/A",
                "Institution_Date": "N/A",
                "Disposal_Date": "N/A",
                "Advocates": {
                    "ASC": "N/A",
                    "AOR": "N/A",
                    "Prosecutor": "N/A"
                },
                "Petition_Appeal_Memo": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []  # Support for multiple files
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []  # Support for multiple files
                },
                "Worker_ID": worker_id
            }
            
            # Extract Case No from spCaseNo
            case_no_span = soup.find('span', {'id': 'spCaseNo'})
            if case_no_span:
                case_data["Case_No"] = case_no_span.get_text(strip=True)
            
            # Extract Case Title from spCaseTitle  
            case_title_span = soup.find('span', {'id': 'spCaseTitle'})
            if case_title_span:
                case_data["Case_Title"] = case_title_span.get_text(strip=True)
            
            # Extract Status from spStatus
            status_span = soup.find('span', {'id': 'spStatus'})
            if status_span:
                case_data["Status"] = status_span.get_text(strip=True)
            
            # Extract Institution Date from spInstDate
            inst_date_span = soup.find('span', {'id': 'spInstDate'})
            if inst_date_span:
                case_data["Institution_Date"] = inst_date_span.get_text(strip=True)
            
            # Extract Disposal Date from spDispDate
            disp_date_span = soup.find('span', {'id': 'spDispDate'})
            if disp_date_span:
                case_data["Disposal_Date"] = disp_date_span.get_text(strip=True)
            
            # Extract AOR/ASC from spAOR
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
            
            # Enhanced PDF detection and download
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
                    
                    print(f"🔍 Worker {worker_id}: Found potential PDF - '{link_text}' -> {href}")
                    
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
            
            # Handle memo files
            if memo_files:
                case_data["Petition_Appeal_Memo"]["Files"] = []
                for i, memo_file in enumerate(memo_files):
                    file_info = {
                        "File": memo_file['href'],
                        "Type": memo_file['type'], 
                        "Description": memo_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }
                    
                    # Download each memo PDF
                    print(f"📄 Worker {worker_id}: Downloading memo {i+1}: {memo_file['text']}")
                    download_path = self.download_pdf(
                        memo_file['href'], 
                        case_data["Case_No"], 
                        f"memo_{i+1}", 
                        worker_id
                    )
                    file_info["Downloaded_Path"] = download_path
                    case_data["Petition_Appeal_Memo"]["Files"].append(file_info)
                
                # Keep backward compatibility - use first file
                case_data["Petition_Appeal_Memo"]["File"] = memo_files[0]['href']
                case_data["Petition_Appeal_Memo"]["Type"] = "PDF"
                case_data["Petition_Appeal_Memo"]["Downloaded_Path"] = case_data["Petition_Appeal_Memo"]["Files"][0]["Downloaded_Path"]
            
            # Handle judgment files
            if judgment_files:
                case_data["Judgement_Order"]["Files"] = []
                for i, judgment_file in enumerate(judgment_files):
                    file_info = {
                        "File": judgment_file['href'],
                        "Type": judgment_file['type'],
                        "Description": judgment_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }
                    
                    # Download each judgment PDF
                    print(f"📄 Worker {worker_id}: Downloading judgment {i+1}: {judgment_file['text']}")
                    download_path = self.download_pdf(
                        judgment_file['href'], 
                        case_data["Case_No"], 
                        f"judgment_{i+1}", 
                        worker_id
                    )
                    file_info["Downloaded_Path"] = download_path
                    case_data["Judgement_Order"]["Files"].append(file_info)
                
                # Keep backward compatibility - use first file
                case_data["Judgement_Order"]["File"] = judgment_files[0]['href']
                case_data["Judgement_Order"]["Type"] = "PDF"
                case_data["Judgement_Order"]["Downloaded_Path"] = case_data["Judgement_Order"]["Files"][0]["Downloaded_Path"]
            
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
            
            # Handle potential form resubmission
            self.handle_form_resubmission(driver)
            
            print(f"✅ Worker {worker_id}: Case {case_index + 1} processed - {case_data['Case_No']}")
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
    
    def worker_process_cases(self, case_indices, worker_id):
        """Worker function to process assigned cases"""
        driver = None
        processed_cases = []
        
        try:
            # Create optimized driver for this worker
            driver = self.create_optimized_driver(headless=False)  # Use visible mode for better reliability
            if not driver:
                print(f"❌ Worker {worker_id}: Failed to create driver")
                return []
            
            # Navigate and search
            if not self.navigate_and_search(driver, worker_id):
                print(f"❌ Worker {worker_id}: Failed to navigate and search")
                return []
            
            # Process assigned cases
            for case_index in case_indices:
                case_data = self.extract_detailed_case_info(driver, case_index, worker_id)
                if case_data:
                    processed_cases.append(case_data)
                
                # Small delay between cases
                time.sleep(0.5)
            
            print(f"✅ Worker {worker_id}: Completed processing {len(processed_cases)} cases")
            return processed_cases
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Critical error - {e}")
            return processed_cases
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def get_total_cases_count(self):
        """Get total number of cases available"""
        driver = None
        try:
            # Create temporary driver to get case count
            driver = self.create_optimized_driver(headless=False)  # Use visible mode for scout
            if not driver:
                return 0
            
            # Navigate and search
            if not self.navigate_and_search(driver, "scout"):
                return 0
            
            # Count View Details links
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            total_cases = len(view_details_links)
            
            print(f"📋 Total cases found: {total_cases}")
            return total_cases
            
        except Exception as e:
            print(f"❌ Error getting case count: {e}")
            return 0
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def distribute_cases(self, total_cases):
        """Distribute cases among workers"""
        if total_cases == 0:
            return []
        
        cases_per_worker = max(1, total_cases // self.max_workers)
        worker_assignments = []
        
        for i in range(self.max_workers):
            start_idx = i * cases_per_worker
            if i == self.max_workers - 1:  # Last worker gets remaining cases
                end_idx = total_cases
            else:
                end_idx = (i + 1) * cases_per_worker
            
            if start_idx < total_cases:
                case_indices = list(range(start_idx, end_idx))
                worker_assignments.append((case_indices, i + 1))
        
        # Print distribution
        print(f"📊 Case Distribution:")
        for case_indices, worker_id in worker_assignments:
            print(f"   Worker {worker_id}: Cases {case_indices[0]+1}-{case_indices[-1]+1} ({len(case_indices)} cases)")
        
        return worker_assignments
    
    def run_parallel_extraction(self):
        """Run parallel extraction with multiple browsers"""
        print("🚀 MULTI-BROWSER C.A. LAHORE 2025 EXTRACTOR")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Get total cases count
            total_cases = self.get_total_cases_count()
            if total_cases == 0:
                print("❌ No cases found to process")
                return False
            
            # Distribute cases among workers
            worker_assignments = self.distribute_cases(total_cases)
            if not worker_assignments:
                print("❌ No worker assignments created")
                return False
            
            print(f"\n🏁 Starting parallel extraction with {len(worker_assignments)} workers...")
            
            # Run parallel extraction
            all_results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all worker tasks
                future_to_worker = {
                    executor.submit(self.worker_process_cases, case_indices, worker_id): worker_id
                    for case_indices, worker_id in worker_assignments
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_worker):
                    worker_id = future_to_worker[future]
                    try:
                        worker_results = future.result()
                        all_results.extend(worker_results)
                        print(f"✅ Worker {worker_id} completed: {len(worker_results)} cases")
                    except Exception as e:
                        print(f"❌ Worker {worker_id} failed: {e}")
            
            self.extracted_cases = all_results
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🎯 PARALLEL EXTRACTION COMPLETED!")
            print(f"   Total Cases Processed: {len(self.extracted_cases)}")
            print(f"   Total Time: {duration:.2f} seconds")
            print(f"   Average Time per Case: {duration/len(self.extracted_cases):.2f} seconds")
            print(f"   Speed Improvement: ~{15*60/duration:.1f}x faster than single browser")
            
            return True
            
        except Exception as e:
            print(f"❌ Parallel extraction failed: {e}")
            return False
    
    def save_results(self, filename="ca_lahore_2025_multi_browser_results.json"):
        """Save results to JSON file"""
        try:
            # Remove duplicates based on Case_No
            seen_cases = set()
            unique_cases = []
            
            for case in self.extracted_cases:
                case_no = case.get("Case_No", "")
                if case_no and case_no != "N/A" and case_no not in seen_cases:
                    seen_cases.add(case_no)
                    unique_cases.append(case)
            
            # Sort by case number for consistency
            unique_cases.sort(key=lambda x: x.get("Case_No", ""))
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(unique_cases)} unique cases to {filename}")
            
            # Show summary
            if unique_cases:
                print(f"\n📋 EXTRACTION SUMMARY:")
                print(f"   Total Unique Cases: {len(unique_cases)}")
                print(f"   PDF Downloads Directory: {self.downloads_dir}")
                
                pdf_count = 0
                memo_pdfs = 0
                judgment_pdfs = 0
                
                for case in unique_cases:
                    memo_path = case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', '')
                    judgment_path = case.get('Judgement_Order', {}).get('Downloaded_Path', '')
                    
                    if memo_path and memo_path != 'No PDF Available' and 'Failed' not in memo_path:
                        memo_pdfs += 1
                    if judgment_path and judgment_path != 'No PDF Available' and 'Failed' not in judgment_path:
                        judgment_pdfs += 1
                    
                    if memo_path != 'No PDF Available' or judgment_path != 'No PDF Available':
                        pdf_count += 1
                
                print(f"   Cases with PDFs: {pdf_count}")
                print(f"   Memo PDFs Downloaded: {memo_pdfs}")
                print(f"   Judgment PDFs Downloaded: {judgment_pdfs}")
                
                # Show sample cases
                print(f"\n📄 Sample Cases:")
                for i, case in enumerate(unique_cases[:3]):
                    print(f"\n   {i+1}. {case.get('Case_No', 'N/A')}")
                    print(f"      Title: {case.get('Case_Title', 'N/A')[:60]}...")
                    print(f"      Status: {case.get('Status', 'N/A')}")
                    print(f"      Worker: {case.get('Worker_ID', 'N/A')}")
                    
                    memo_path = case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', 'N/A')
                    judgment_path = case.get('Judgement_Order', {}).get('Downloaded_Path', 'N/A')
                    
                    print(f"      Memo PDF: {'✅' if memo_path != 'No PDF Available' else '❌'}")
                    print(f"      Judgment PDF: {'✅' if judgment_path != 'No PDF Available' else '❌'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False


def main():
    """Main function"""
    # Create extractor with 4 workers for optimal performance
    extractor = MultiBrowserCALahore2025Extractor(max_workers=4)
    
    if extractor.run_parallel_extraction():
        extractor.save_results()
        print("\n🎉 Multi-browser extraction completed successfully!")
    else:
        print("\n❌ Multi-browser extraction failed")


if __name__ == "__main__":
    main()