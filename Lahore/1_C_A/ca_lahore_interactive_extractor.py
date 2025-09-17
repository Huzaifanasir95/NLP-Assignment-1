"""
Interactive C.A. (Civil Appeals) Lahore Extractor
Based on proven paginated multi-browser technique
Allows user to select specific year ranges for extraction
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


class CALahoreInteractiveExtractor:
    """Interactive extractor for C.A. Lahore cases with user-selectable year ranges"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.extracted_cases = []
        self.base_url = "https://scp.gov.pk"
        self.results_lock = threading.Lock()
        
        # Configuration for C.A. cases
        self.case_type_value = "1"
        self.case_type_text = "C.A."
        
        # Available year ranges (5-year gaps)
        self.year_ranges = {
            "1": {"name": "1980-1984", "years": [1980, 1981, 1982, 1983, 1984]},
            "2": {"name": "1985-1989", "years": [1985, 1986, 1987, 1988, 1989]},
            "3": {"name": "1990-1994", "years": [1990, 1991, 1992, 1993, 1994]},
            "4": {"name": "1995-1999", "years": [1995, 1996, 1997, 1998, 1999]},
            "5": {"name": "2000-2004", "years": [2000, 2001, 2002, 2003, 2004]},
            "6": {"name": "2005-2009", "years": [2005, 2006, 2007, 2008, 2009]},
            "7": {"name": "2010-2014", "years": [2010, 2011, 2012, 2013, 2014]},
            "8": {"name": "2015-2019", "years": [2015, 2016, 2017, 2018, 2019]},
            "9": {"name": "2020-2024", "years": [2020, 2021, 2022, 2023, 2024]},
            "10": {"name": "2025", "years": [2025]}
        }
        
        print(f"✅ C.A. Lahore Interactive Extractor initialized")
        print(f"   Case Type: {self.case_type_text} (Value: {self.case_type_value})")
        print(f"   Max Workers: {self.max_workers}")
    
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
    
    def navigate_and_search(self, driver, worker_id, year):
        """Navigate and search for specific year (proven technique)"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Worker {worker_id}: Navigating for year {year}")
            driver.get(url)
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlCaseType"))
            )
            
            # Select case type: C.A.
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
            print(f"🔍 Worker {worker_id}: Search completed for year {year}")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Search failed for year {year} - {e}")
            return False
    
    def navigate_to_page(self, driver, page_number, worker_id):
        """Navigate to specific page (proven technique)"""
        try:
            if page_number == 1:
                return True
            
            print(f"🔄 Worker {worker_id}: Navigating to page {page_number}")
            
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
    
    def download_pdf(self, pdf_url, case_no, pdf_type, worker_id, year_range_name):
        """Download PDF files (proven technique)"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            # Create year range specific downloads directory
            downloads_dir = os.path.join(year_range_name, "pdfs")
            os.makedirs(downloads_dir, exist_ok=True)
            
            safe_case_no = re.sub(r'[^\w\-_.]', '_', case_no)
            filename = f"{safe_case_no}_{pdf_type}.pdf"
            local_path = os.path.join(downloads_dir, filename)
            
            if os.path.exists(local_path):
                print(f"📄 Worker {worker_id}: PDF already exists - {filename}")
                return local_path
            
            print(f"⬇️ Worker {worker_id}: Downloading {filename}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(pdf_url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Worker {worker_id}: Downloaded {filename} ({len(response.content)} bytes)")
            return local_path
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Worker {worker_id}: Download failed for {case_no} - {e}")
            return f"Download Failed: {str(e)}"
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error downloading {case_no} - {e}")
            return f"Download Error: {str(e)}"
    
    def extract_detailed_case_info(self, driver, case_index, worker_id, page_number, year, year_range_name):
        """Extract detailed case information (proven technique)"""
        try:
            print(f"🔍 Worker {worker_id}: Processing Year {year}, Page {page_number}, Case {case_index + 1}")
            
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Worker {worker_id}: Case index {case_index} out of range")
                return None
            
            link = view_details_links[case_index]
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
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
                    "Files": []
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []
                },
                "Worker_ID": worker_id,
                "Page_Number": page_number,
                "Year": year,
                "Case_Type": self.case_type_text,
                "Year_Range": year_range_name
            }
            
            # Extract case information using proven selectors
            case_no_span = soup.find('span', {'id': 'spCaseNo'})
            if case_no_span:
                case_data["Case_No"] = case_no_span.get_text(strip=True)
            
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
                case_data["Petition_Appeal_Memo"]["Files"] = []
                for i, memo_file in enumerate(memo_files):
                    file_info = {
                        "File": memo_file['href'],
                        "Type": memo_file['type'], 
                        "Description": memo_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }
                    
                    link_info = self.download_pdf(
                        memo_file['href'], 
                        case_data["Case_No"], 
                        f"memo_{i+1}", 
                        worker_id,
                        year_range_name
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
                    file_info = {
                        "File": judgment_file['href'],
                        "Type": judgment_file['type'],
                        "Description": judgment_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }
                    
                    link_info = self.download_pdf(
                        judgment_file['href'], 
                        case_data["Case_No"], 
                        f"judgment_{i+1}", 
                        worker_id,
                        year_range_name
                    )
                    file_info["Downloaded_Path"] = link_info
                    case_data["Judgement_Order"]["Files"].append(file_info)
                
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
            
            driver.back()
            time.sleep(1)
            
            print(f"✅ Worker {worker_id}: Year {year}, Page {page_number}, Case {case_index + 1} processed - {case_data['Case_No']}")
            return case_data
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error processing Year {year}, Page {page_number}, Case {case_index + 1} - {e}")
            try:
                driver.back()
                time.sleep(1)
            except:
                pass
            return None
    
    def worker_process_year(self, year, worker_id, year_range_name):
        """Process all cases for a specific year"""
        driver = None
        processed_cases = []
        
        try:
            driver = self.create_optimized_driver(headless=False)
            if not driver:
                print(f"❌ Worker {worker_id}: Failed to create driver")
                return []
            
            if not self.navigate_and_search(driver, worker_id, year):
                print(f"❌ Worker {worker_id}: Failed to navigate and search for year {year}")
                return []
            
            # Check if there are any results
            try:
                no_records = driver.find_element(By.XPATH, "//span[contains(text(), 'No Record Found')]")
                print(f"ℹ️ Worker {worker_id}: No records found for year {year}")
                return []
            except:
                # Continue - records found
                pass
            
            # Get total pages
            try:
                page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
                total_pages = len(page_links) + 1 if page_links else 1
                print(f"📋 Worker {worker_id}: Found {total_pages} pages for year {year}")
            except:
                total_pages = 1
            
            # Process all pages for this year
            for page_num in range(1, total_pages + 1):
                if page_num > 1:
                    if not self.navigate_to_page(driver, page_num, worker_id):
                        continue
                
                view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                total_cases_on_page = len(view_details_links)
                
                print(f"📋 Worker {worker_id}: Processing {total_cases_on_page} cases on page {page_num} for year {year}")
                
                for case_index in range(total_cases_on_page):
                    case_data = self.extract_detailed_case_info(driver, case_index, worker_id, page_num, year, year_range_name)
                    if case_data:
                        processed_cases.append(case_data)
                    
                    time.sleep(0.5)
            
            print(f"✅ Worker {worker_id}: Completed year {year} - {len(processed_cases)} cases")
            return processed_cases
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Critical error processing year {year} - {e}")
            return processed_cases
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def display_year_ranges_menu(self):
        """Display available year ranges for selection"""
        print(f"\n📅 AVAILABLE YEAR RANGES FOR C.A. LAHORE EXTRACTION:")
        print("=" * 60)
        
        for key, range_info in self.year_ranges.items():
            years_str = ", ".join(map(str, range_info['years']))
            print(f"   {key}. {range_info['name']} ({len(range_info['years'])} years: {years_str})")
        
        print(f"\n   0. Extract ALL year ranges")
        print(f"   q. Quit")
    
    def get_user_selection(self):
        """Get user selection for year ranges"""
        while True:
            self.display_year_ranges_menu()
            
            choice = input(f"\nSelect year range(s) to extract (e.g., '1' for single range, '1,5,9' for multiple, '0' for all): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice == '0':
                # Return all year ranges
                return list(self.year_ranges.keys())
            
            # Parse selection
            try:
                selected_ranges = []
                choices = [c.strip() for c in choice.split(',')]
                
                for c in choices:
                    if c in self.year_ranges:
                        selected_ranges.append(c)
                    else:
                        print(f"❌ Invalid choice: {c}")
                        break
                else:
                    if selected_ranges:
                        return selected_ranges
                
                print("❌ Please enter valid choices")
                
            except ValueError:
                print("❌ Please enter valid numbers separated by commas")
    
    def run_extraction(self, selected_ranges):
        """Run extraction for selected year ranges"""
        print(f"\n🚀 C.A. LAHORE EXTRACTION STARTING")
        print("=" * 50)
        
        total_start_time = time.time()
        all_results = []
        
        for range_key in selected_ranges:
            range_info = self.year_ranges[range_key]
            years = range_info['years']
            range_name = range_info['name']
            
            print(f"\n📊 PROCESSING YEAR RANGE: {range_name}")
            print(f"   Years: {years}")
            print(f"   Workers: {self.max_workers}")
            
            start_time = time.time()
            
            try:
                range_results = []
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_year = {
                        executor.submit(self.worker_process_year, year, f"Y{year}", range_name): year
                        for year in years
                    }
                    
                    for future in as_completed(future_to_year):
                        year = future_to_year[future]
                        try:
                            year_results = future.result()
                            range_results.extend(year_results)
                            print(f"✅ Year {year} completed: {len(year_results)} cases")
                        except Exception as e:
                            print(f"❌ Year {year} failed: {e}")
                
                all_results.extend(range_results)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"\n🎯 YEAR RANGE {range_name} COMPLETED!")
                print(f"   Years Processed: {len(years)}")
                print(f"   Cases Found: {len(range_results)}")
                print(f"   Duration: {duration:.2f} seconds")
                if range_results:
                    print(f"   Avg Time/Case: {duration/len(range_results):.2f} seconds")
                
                # Save results for this range
                self.save_range_results(range_results, range_name)
                
            except Exception as e:
                print(f"❌ Range {range_name} failed: {e}")
        
        self.extracted_cases = all_results
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        print(f"\n🎉 COMPLETE C.A. EXTRACTION FINISHED!")
        print(f"   Total Year Ranges: {len(selected_ranges)}")
        print(f"   Total Cases: {len(all_results)}")
        print(f"   Total Duration: {total_duration:.2f} seconds")
        if all_results:
            print(f"   Avg Time/Case: {total_duration/len(all_results):.2f} seconds")
        
        return True
    
    def save_range_results(self, cases, range_name):
        """Save results for a specific year range"""
        try:
            # Create range directory
            range_dir = range_name.replace('-', '_')
            os.makedirs(range_dir, exist_ok=True)
            
            filename = os.path.join(range_dir, f"CA_Lahore_{range_name.replace('-', '_')}_complete.json")
            
            # Remove duplicates
            seen_cases = set()
            unique_cases = []
            
            for case in cases:
                case_no = case.get("Case_No", "")
                if case_no and case_no != "N/A" and case_no not in seen_cases:
                    seen_cases.add(case_no)
                    unique_cases.append(case)
            
            unique_cases.sort(key=lambda x: x.get("Case_No", ""))
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(unique_cases)} unique cases to {filename}")
            
            # Save summary
            if unique_cases:
                summary = {
                    "case_type": self.case_type_text,
                    "year_range": range_name,
                    "total_cases": len(unique_cases),
                    "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "pdf_directory": os.path.join(range_dir, "pdfs")
                }
                
                summary_file = os.path.join(range_dir, f"CA_Lahore_{range_name.replace('-', '_')}_summary.json")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                
                print(f"   Summary saved to {summary_file}")
                
                # Count PDFs
                pdf_count = 0
                for case in unique_cases:
                    memo_path = case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', '')
                    judgment_path = case.get('Judgement_Order', {}).get('Downloaded_Path', '')
                    
                    if memo_path and memo_path != 'No PDF Available' and os.path.exists(memo_path):
                        pdf_count += 1
                    if judgment_path and judgment_path != 'No PDF Available' and os.path.exists(judgment_path):
                        pdf_count += 1
                
                print(f"   PDFs Downloaded: {pdf_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save range results: {e}")
            return False


def main():
    """Main function"""
    print("🚀 C.A. (CIVIL APPEALS) LAHORE INTERACTIVE EXTRACTOR")
    print("=" * 60)
    print("Based on proven paginated multi-browser technique")
    print("Supports selective year range extraction with PDF downloads")
    
    extractor = CALahoreInteractiveExtractor(max_workers=3)
    
    # Get user selection
    selected_ranges = extractor.get_user_selection()
    
    if not selected_ranges:
        print("\n👋 Extraction cancelled by user")
        return
    
    # Show selected ranges
    print(f"\n📋 SELECTED YEAR RANGES:")
    for range_key in selected_ranges:
        range_info = extractor.year_ranges[range_key]
        print(f"   {range_info['name']}: {range_info['years']}")
    
    # Confirm extraction
    confirm = input(f"\nProceed with extraction? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n👋 Extraction cancelled")
        return
    
    # Run extraction
    if extractor.run_extraction(selected_ranges):
        print("\n🎉 C.A. Lahore extraction completed successfully!")
    else:
        print("\n❌ C.A. Lahore extraction failed")


if __name__ == "__main__":
    main()