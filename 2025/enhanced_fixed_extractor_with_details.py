"""
Enhanced Fixed Extractor with View Details
Based on the successful test_fixed_extractor.py with View Details functionality added
"""

import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup


class EnhancedFixedExtractor:
    """Enhanced version of the successful fixed extractor with View Details"""
    
    def __init__(self):
        self.driver = None
        self.extracted_cases = []
        
        # EXACT same element IDs from successful test_fixed_extractor.py
        self.element_ids = {
            'case_type': 'ddlCaseType',
            'year': 'ddlYear', 
            'registry': 'ddlRegistry',
            'judge': 'ddlJudge',
            'case_no': 'txtCaseNo',
            'case_title': 'txtCaseTitle',
            'search_button': 'btnSearch'
        }
        
        # EXACT same options from successful test_fixed_extractor.py
        self.case_type_options = {
            'C.A.': '1',
            'C.M.A.': '21', 
            'C.M.Appeal.': '20',
            'C.P.': '13'
        }
        
        self.registry_options = {
            'Islamabad': 'I',
            'Peshawar': 'P', 
            'Lahore': 'L',
            'Karachi': 'K'
        }
        
        # Search strategies that work
        self.search_strategies = [
            {'case_type': 'C.A.', 'registry': 'Lahore'},
            {'case_type': 'C.A.', 'registry': 'Karachi'},
            {'case_type': 'C.M.A.', 'registry': 'Lahore'},
            {'case_type': 'C.M.A.', 'registry': 'Karachi'},
            {'case_type': 'C.P.', 'registry': 'Islamabad'},
        ]
        
        print("✅ Enhanced Fixed Extractor initialized with SUCCESSFUL configurations")
    
    def setup_driver(self):
        """Setup Chrome WebDriver - EXACT same as successful version"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            print("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to setup driver: {e}")
            return False
    
    def navigate_to_website(self):
        """Navigate to website - EXACT same as successful version"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load
            print("✅ Successfully navigated to website")
            return True
        except Exception as e:
            print(f"❌ Failed to navigate: {e}")
            return False
    
    def perform_search(self, case_type=None, registry=None, year=2025):
        """Perform search - EXACT same as successful version"""
        try:
            print(f"🔍 Performing search: Type={case_type}, Registry={registry}, Year={year}")
            
            # Fill case type if provided
            if case_type and case_type in self.case_type_options:
                case_type_select = self.driver.find_element(By.ID, self.element_ids['case_type'])
                select = Select(case_type_select)
                select.select_by_value(self.case_type_options[case_type])
                print(f"✅ Selected case type: {case_type}")
                time.sleep(1)
            
            # Fill registry if provided
            if registry and registry in self.registry_options:
                registry_select = self.driver.find_element(By.ID, self.element_ids['registry'])
                select = Select(registry_select)
                select.select_by_value(self.registry_options[registry])
                print(f"✅ Selected registry: {registry}")
                time.sleep(1)
            
            # Fill year
            year_select = self.driver.find_element(By.ID, self.element_ids['year'])
            select = Select(year_select)
            select.select_by_value(str(year))
            print(f"✅ Selected year: {year}")
            time.sleep(1)
            
            # Click search button
            search_button = self.driver.find_element(By.ID, self.element_ids['search_button'])
            search_button.click()
            print("🔍 Search button clicked")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def get_basic_cases_from_page(self):
        """Get basic case list from page - same as successful version"""
        cases = []
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find tables containing case data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Process each row (skip header)
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        case_data = self.extract_basic_case_data(cells)
                        
                        if case_data and '2025' in case_data.get('Case_No', ''):
                            cases.append(case_data)
            
            print(f"📋 Found {len(cases)} cases on current page")
            return cases
            
        except Exception as e:
            print(f"❌ Error extracting basic cases: {e}")
            return []
    
    def extract_basic_case_data(self, cells):
        """Extract basic case data from cells - same logic as successful version"""
        try:
            case_data = {
                "Case_No": "N/A",
                "Case_Title": "N/A",
                "Status": "N/A"
            }
            
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Case number (first few columns, contains digits and 2025)
                if i <= 2 and any(char.isdigit() for char in cell_text) and '2025' in cell_text:
                    case_data["Case_No"] = self.extract_case_number(cell_text)
                
                # Case title (longer text with vs/v.)
                elif len(cell_text) > 20 and any(keyword in cell_text.lower() for keyword in ['vs', 'v.', 'versus']):
                    case_data["Case_Title"] = cell_text
                
                # Status
                elif any(keyword in cell_text.lower() for keyword in ['pending', 'disposed', 'decided']):
                    case_data["Status"] = cell_text
            
            return case_data if case_data["Case_No"] != "N/A" else None
            
        except Exception as e:
            print(f"⚠️ Error extracting case data: {e}")
            return None
    
    def extract_case_number(self, text):
        """Extract case number - same regex as successful version"""
        patterns = [
            r'([A-Z]+\.[A-Z]+\.(?:[A-Z]+\.)?\d+[-/]\w*/\d{4})',
            r'([A-Z]+\.\d+[-/]\w*/\d{4})',
            r'([A-Z]+\.[A-Z]+\.\d+/\d{4})',
            r'([A-Z]+\.\d+/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return text.strip()
    
    def click_view_details_for_case(self, case_index):
        """NEW: Click View Details for specific case and extract detailed info"""
        try:
            print(f"🔍 Clicking View Details for case {case_index + 1}...")
            
            # Get fresh View Details links
            view_details_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Case index {case_index} out of range")
                return None
            
            # Scroll to and click the View Details link
            link = view_details_links[case_index]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", link)
            time.sleep(3)
            
            # Extract detailed information
            detailed_case = self.extract_detailed_case_info()
            
            # Navigate back and handle form resubmission
            self.driver.back()
            time.sleep(2)
            
            # Check if we got the "Confirm Form Resubmission" page
            if self.handle_form_resubmission():
                print("✅ Handled form resubmission")
            
            return detailed_case
            
        except Exception as e:
            print(f"❌ Error in View Details for case {case_index + 1}: {e}")
            return None
    
    def handle_form_resubmission(self):
        """Handle the 'Confirm Form Resubmission' page by refreshing"""
        try:
            page_source = self.driver.page_source.lower()
            
            # Check if we're on the form resubmission error page
            if any(keyword in page_source for keyword in [
                'confirm form resubmission', 
                'err_cache_miss',
                'reload button to resubmit',
                'webpage requires data that you entered earlier'
            ]):
                print("🔄 Form resubmission page detected - refreshing...")
                self.driver.refresh()
                time.sleep(3)
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking form resubmission: {e}")
            return False
    
    def extract_detailed_case_info(self):
        """NEW: Extract detailed case information from View Details page"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
            # Initialize detailed case structure
            detailed_case = {
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
                    "Type": "N/A"
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A"
                }
            }
            
            # Extract Case Title
            title_match = re.search(r'Case Title:\s*([^\n\r]+)', page_text)
            if title_match:
                detailed_case["Case_Title"] = title_match.group(1).strip()
            
            # Extract Case No
            case_no_match = re.search(r'Case No:\s*([^\n\r]+)', page_text)
            if case_no_match:
                detailed_case["Case_No"] = case_no_match.group(1).strip()
            
            # Extract Status
            status_match = re.search(r'Status:\s*([^\n\r]+)', page_text)
            if status_match:
                detailed_case["Status"] = status_match.group(1).strip()
            
            # Extract Institution Date
            inst_date_match = re.search(r'Institution Date:\s*([^\n\r]+)', page_text)
            if inst_date_match:
                detailed_case["Institution_Date"] = inst_date_match.group(1).strip()
            
            # Extract Disposal Date
            disp_date_match = re.search(r'Disposal Date:\s*([^\n\r]+)', page_text)
            if disp_date_match:
                detailed_case["Disposal_Date"] = disp_date_match.group(1).strip()
            
            # Extract AOR/ASC information
            aor_match = re.search(r'AOR/ASC:\s*([^\n\r]+(?:\n[^\n\r]+)*?)(?:\n\n|\nPetition)', page_text, re.DOTALL)
            if aor_match:
                aor_text = aor_match.group(1).strip()
                lines = aor_text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if '(ASC)' in line:
                        detailed_case["Advocates"]["ASC"] = line
                    elif '(AOR)' in line:
                        detailed_case["Advocates"]["AOR"] = line
                    elif 'Prosecutor' in line or 'Additional Prosecutor' in line:
                        detailed_case["Advocates"]["Prosecutor"] = line
            
            # Extract Petition/Appeal Memo
            memo_match = re.search(r'Petition/Appeal Memo:\s*([^\n\r]+)', page_text)
            if memo_match:
                memo_text = memo_match.group(1).strip()
                detailed_case["Petition_Appeal_Memo"]["File"] = memo_text
                if "Not Available" not in memo_text:
                    detailed_case["Petition_Appeal_Memo"]["Type"] = "PDF"
            
            # Extract History
            history_match = re.search(r'History:\s*([^\n\r]+)', page_text)
            if history_match:
                history_text = history_match.group(1).strip()
                if "No Fixation History Found" not in history_text:
                    detailed_case["History"].append({"note": history_text})
            
            # Look for judgment/order links
            judgment_links = soup.find_all('a', href=True)
            for link in judgment_links:
                link_text = link.get_text().lower()
                if 'judgment' in link_text or 'order' in link_text:
                    detailed_case["Judgement_Order"]["File"] = link.get('href', 'Available')
                    detailed_case["Judgement_Order"]["Type"] = "PDF"
                    break
            
            return detailed_case
            
        except Exception as e:
            print(f"❌ Error extracting detailed info: {e}")
            return None
    
    def extract_page_with_details(self):
        """ENHANCED: Extract page with View Details functionality"""
        page_cases = []
        
        # Get basic case list
        basic_cases = self.get_basic_cases_from_page()
        
        if not basic_cases:
            print("⚠️ No cases found on current page")
            return []
        
        print(f"📋 Processing {len(basic_cases)} cases for detailed extraction...")
        
        # Process each case with View Details
        for i in range(len(basic_cases)):
            try:
                print(f"\n--- Processing Case {i+1}/{len(basic_cases)} ---")
                
                # Extract detailed information
                detailed_case = self.click_view_details_for_case(i)
                
                if detailed_case:
                    # Merge with basic info if needed
                    basic_case = basic_cases[i]
                    if detailed_case["Case_No"] == "N/A":
                        detailed_case["Case_No"] = basic_case.get("Case_No", "N/A")
                    if detailed_case["Case_Title"] == "N/A":
                        detailed_case["Case_Title"] = basic_case.get("Case_Title", "N/A")
                    if detailed_case["Status"] == "N/A":
                        detailed_case["Status"] = basic_case.get("Status", "N/A")
                    
                    page_cases.append(detailed_case)
                    print(f"✅ Case {i+1} processed: {detailed_case['Case_No']}")
                else:
                    # Fallback to enhanced basic case
                    enhanced_basic = {
                        "Case_No": basic_cases[i].get("Case_No", "N/A"),
                        "Case_Title": basic_cases[i].get("Case_Title", "N/A"),
                        "Status": basic_cases[i].get("Status", "N/A"),
                        "Institution_Date": "View Details",
                        "Disposal_Date": "N/A",
                        "Advocates": {"ASC": "N/A", "AOR": "N/A", "Prosecutor": "N/A"},
                        "Petition_Appeal_Memo": {"File": "N/A", "Type": "N/A"},
                        "History": [],
                        "Judgement_Order": {"File": "N/A", "Type": "N/A"}
                    }
                    page_cases.append(enhanced_basic)
                    print(f"⚠️ Case {i+1} used basic info: {enhanced_basic['Case_No']}")
                
                # Ensure we're back on the main search results page
                self.ensure_on_search_results_page()
                
                # Delay between cases
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Error processing case {i+1}: {e}")
                # Try to get back to search results
                self.ensure_on_search_results_page()
                continue
        
        return page_cases
    
    def ensure_on_search_results_page(self):
        """Ensure we're back on the search results page and not on error/resubmission page"""
        try:
            max_attempts = 3
            attempts = 0
            
            while attempts < max_attempts:
                page_source = self.driver.page_source.lower()
                
                # Check if we're on an error page or form resubmission page
                if any(keyword in page_source for keyword in [
                    'confirm form resubmission', 
                    'err_cache_miss',
                    'reload button to resubmit',
                    'webpage requires data that you entered earlier'
                ]):
                    print(f"🔄 Error page detected (attempt {attempts + 1}) - refreshing...")
                    self.driver.refresh()
                    time.sleep(3)
                    attempts += 1
                else:
                    # Check if we have search results (View Details links)
                    view_details_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                    if view_details_links:
                        print("✅ Back on search results page")
                        return True
                    else:
                        print(f"⚠️ No View Details links found (attempt {attempts + 1})")
                        self.driver.refresh()
                        time.sleep(3)
                        attempts += 1
            
            print("⚠️ Could not ensure search results page after max attempts")
            return False
            
        except Exception as e:
            print(f"❌ Error ensuring search results page: {e}")
            return False
    
    def click_page_number(self, page_num):
        """Click page number - same as successful version"""
        try:
            print(f"🔄 Looking for page {page_num}")
            
            # Try numbered pagination
            page_selectors = [
                f"//a[text()='{page_num}']",
                f"//a[normalize-space(text())='{page_num}']"
            ]
            
            for selector in page_selectors:
                try:
                    page_element = self.driver.find_element(By.XPATH, selector)
                    if page_element.is_displayed() and page_element.is_enabled():
                        self.driver.execute_script("arguments[0].click();", page_element)
                        print(f"✅ Clicked page {page_num}")
                        time.sleep(3)
                        return True
                except:
                    continue
            
            print(f"⚠️ Page {page_num} not found")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking page {page_num}: {e}")
            return False
    
    def extract_with_pagination(self, max_pages=3):
        """Extract with pagination - enhanced version"""
        all_cases = []
        current_page = 1
        
        while current_page <= max_pages:
            print(f"\n📄 Processing page {current_page}")
            
            # Extract cases from current page with detailed information
            page_cases = self.extract_page_with_details()
            
            if page_cases:
                all_cases.extend(page_cases)
                print(f"✅ Page {current_page}: {len(page_cases)} cases extracted")
            else:
                print(f"⚠️ Page {current_page}: No cases found")
            
            # Try to go to next page
            if not self.click_page_number(current_page + 1):
                print("📄 No more pages available")
                break
            
            current_page += 1
        
        return all_cases
    
    def run_enhanced_extraction(self):
        """Run enhanced extraction with View Details"""
        print("🚀 ENHANCED FIXED EXTRACTOR WITH VIEW DETAILS")
        print("=" * 60)
        print("Using SUCCESSFUL test_fixed_extractor.py approach + View Details")
        print("=" * 60)
        
        try:
            # Setup driver
            if not self.setup_driver():
                return False
            
            all_cases = []
            
            # Run each search strategy
            for i, strategy in enumerate(self.search_strategies):
                print(f"\n🎯 Strategy {i+1}/{len(self.search_strategies)}: {strategy}")
                
                # Navigate to website
                if not self.navigate_to_website():
                    continue
                
                # Perform search
                if self.perform_search(strategy['case_type'], strategy['registry'], 2025):
                    # Extract with pagination and View Details
                    strategy_cases = self.extract_with_pagination(max_pages=3)
                    
                    if strategy_cases:
                        all_cases.extend(strategy_cases)
                        print(f"✅ Strategy {i+1} completed: {len(strategy_cases)} cases")
                    else:
                        print(f"⚠️ Strategy {i+1}: No cases found")
                
                # Delay between strategies
                time.sleep(5)
            
            self.extracted_cases = all_cases
            print(f"\n🎯 EXTRACTION COMPLETED: {len(all_cases)} total cases")
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_results(self, filename="enhanced_fixed_extraction_with_details.json"):
        """Save results with duplicate removal"""
        try:
            # Remove duplicates
            seen_cases = set()
            unique_cases = []
            
            for case in self.extracted_cases:
                case_no = case.get("Case_No", "")
                if case_no and case_no != "N/A" and case_no not in seen_cases:
                    seen_cases.add(case_no)
                    unique_cases.append(case)
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(unique_cases)} unique cases to {filename}")
            
            # Show sample results
            if unique_cases:
                print(f"\n📋 Sample detailed cases extracted:")
                for i, case in enumerate(unique_cases[:3]):
                    print(f"\n{i+1}. Case: {case.get('Case_No', 'N/A')}")
                    print(f"   Title: {case.get('Case_Title', 'N/A')[:80]}...")
                    print(f"   Status: {case.get('Status', 'N/A')}")
                    print(f"   Institution Date: {case.get('Institution_Date', 'N/A')}")
                    print(f"   AOR: {case.get('Advocates', {}).get('AOR', 'N/A')}")
                    print(f"   ASC: {case.get('Advocates', {}).get('ASC', 'N/A')}")
                    print(f"   Memo: {case.get('Petition_Appeal_Memo', {}).get('File', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False


def main():
    """Main function"""
    extractor = EnhancedFixedExtractor()
    
    if extractor.run_enhanced_extraction():
        extractor.save_results()
    else:
        print("❌ Extraction failed")


if __name__ == "__main__":
    main()