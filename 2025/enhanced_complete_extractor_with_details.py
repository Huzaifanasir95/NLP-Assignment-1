"""
Enhanced Complete Case Information Extractor with View Details
Based on the successful complete_extractor.py but enhanced to click View Details and extract detailed information
"""

import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup


class EnhancedCompleteExtractor:
    """Enhanced extractor with View Details functionality based on successful approach"""
    
    def __init__(self):
        self.driver = None
        self.all_extracted_cases = []
        
        # Element IDs from website inspection (same as working extractor)
        self.element_ids = {
            'case_type': 'ddlCaseType',
            'year': 'ddlYear', 
            'registry': 'ddlRegistry',
            'search_button': 'btnSearch'
        }
        
        # Search strategies for comprehensive coverage (same as working)
        self.search_strategies = [
            {'case_type': 'C.A.', 'registry': 'Lahore'},
            {'case_type': 'C.A.', 'registry': 'Karachi'},
            {'case_type': 'C.A.', 'registry': 'Islamabad'},
            {'case_type': 'C.M.A.', 'registry': 'Lahore'},
            {'case_type': 'C.M.A.', 'registry': 'Karachi'},
            {'case_type': 'C.M.A.', 'registry': 'Islamabad'},
            {'case_type': 'C.P.', 'registry': 'Lahore'},
            {'case_type': 'C.P.', 'registry': 'Karachi'},
            {'case_type': 'C.P.', 'registry': 'Islamabad'},
        ]
        
        # Option mappings from inspection (same as working)
        self.case_type_options = {
            'C.A.': '1',
            'C.M.A.': '21', 
            'C.P.': '13'
        }
        
        self.registry_options = {
            'Lahore': '2',
            'Karachi': '3', 
            'Islamabad': '1'
        }
        
        print("✅ Enhanced extractor initialized with working configurations")
    
    def setup_driver(self):
        """Setup Chrome driver with same configuration as working extractor"""
        options = Options()
        # Keep browser visible for debugging (same as working version)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Chrome driver setup successful")
            return True
        except Exception as e:
            print(f"❌ Driver setup failed: {e}")
            return False
    
    def navigate_to_site(self):
        """Navigate to the website (same as working extractor)"""
        url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        try:
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)
            print("✅ Navigation successful")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def perform_search(self, strategy):
        """Perform search with given strategy (same as working extractor)"""
        try:
            print(f"🔍 Performing search: {strategy}")
            
            # Select case type
            case_type_dropdown = self.driver.find_element(By.ID, self.element_ids['case_type'])
            case_type_select = Select(case_type_dropdown)
            case_type_value = self.case_type_options.get(strategy['case_type'], '1')
            case_type_select.select_by_value(case_type_value)
            print(f"✅ Selected case type: {strategy['case_type']}")
            time.sleep(1)
            
            # Select registry
            registry_dropdown = self.driver.find_element(By.ID, self.element_ids['registry'])
            registry_select = Select(registry_dropdown)
            registry_value = self.registry_options.get(strategy['registry'], '1')
            registry_select.select_by_value(registry_value)
            print(f"✅ Selected registry: {strategy['registry']}")
            time.sleep(1)
            
            # Select year (2025)
            year_dropdown = self.driver.find_element(By.ID, self.element_ids['year'])
            year_select = Select(year_dropdown)
            year_select.select_by_value('2025')
            print("✅ Selected year: 2025")
            time.sleep(1)
            
            # Click search button
            search_button = self.driver.find_element(By.ID, self.element_ids['search_button'])
            search_button.click()
            print("🔍 Search button clicked")
            time.sleep(5)  # Wait for results
            
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def get_basic_cases_from_page(self):
        """Get basic case information from current page (similar to working extractor)"""
        cases = []
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find tables containing case data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Skip header row
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        case_data = self.extract_basic_case_info(cells)
                        
                        if case_data and '2025' in case_data.get('Case_No', ''):
                            cases.append(case_data)
            
            print(f"📋 Found {len(cases)} cases on current page")
            return cases
            
        except Exception as e:
            print(f"❌ Error extracting basic cases: {e}")
            return []
    
    def extract_basic_case_info(self, cells):
        """Extract basic case information from table cells"""
        try:
            case_data = {
                "Case_No": "N/A",
                "Case_Title": "N/A",
                "Status": "N/A"
            }
            
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Case number (usually in first few columns)
                if i <= 2 and any(char.isdigit() for char in cell_text):
                    if '2025' in cell_text:
                        case_data["Case_No"] = self.extract_case_number(cell_text)
                
                # Case title (longer text with vs/v.)
                elif len(cell_text) > 20 and any(keyword in cell_text.lower() for keyword in ['vs', 'v.', 'versus']):
                    case_data["Case_Title"] = cell_text
                
                # Status
                elif any(keyword in cell_text.lower() for keyword in ['pending', 'disposed', 'decided']):
                    case_data["Status"] = cell_text
            
            return case_data if case_data["Case_No"] != "N/A" else None
            
        except Exception as e:
            print(f"⚠️ Error extracting basic case info: {e}")
            return None
    
    def extract_case_number(self, text):
        """Extract case number using regex patterns (same as working extractor)"""
        patterns = [
            r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/\d{4})',
            r'([A-Z]\.[A-Z]\.\d+/\d{4})',
            r'([A-Z]+\.\d+/\d{4})',
            r'([A-Z]+\.[A-Z]+\.[A-Z]+\.\d+[-/]\w*/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return text.strip()
    
    def click_view_details_and_extract(self, case_index):
        """Click View Details for a specific case and extract detailed information"""
        try:
            print(f"🔍 Processing case {case_index + 1} for detailed extraction...")
            
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
            detailed_case = self.extract_detailed_information()
            
            # Navigate back to search results
            self.driver.back()
            time.sleep(2)
            
            return detailed_case
            
        except Exception as e:
            print(f"❌ Error in View Details extraction for case {case_index + 1}: {e}")
            return None
    
    def extract_detailed_information(self):
        """Extract detailed case information from View Details page"""
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
            aor_section_match = re.search(r'AOR/ASC:\s*([^\n\r]+(?:\n[^\n\r]+)*?)(?:\n\n|\nPetition)', page_text, re.DOTALL)
            if aor_section_match:
                aor_text = aor_section_match.group(1).strip()
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
            
            print(f"✅ Extracted detailed info for case: {detailed_case['Case_No']}")
            return detailed_case
            
        except Exception as e:
            print(f"❌ Error extracting detailed information: {e}")
            return None
    
    def extract_page_with_details(self):
        """Extract all cases from current page with detailed View Details information"""
        page_cases = []
        
        # First get basic case list to know how many cases we have
        basic_cases = self.get_basic_cases_from_page()
        
        if not basic_cases:
            print("⚠️ No cases found on current page")
            return []
        
        print(f"📋 Processing {len(basic_cases)} cases for detailed extraction...")
        
        # Process each case with View Details
        for i in range(len(basic_cases)):
            try:
                # Extract detailed information for this case
                detailed_case = self.click_view_details_and_extract(i)
                
                if detailed_case:
                    # Merge with basic info if detailed extraction missed anything
                    basic_case = basic_cases[i]
                    if detailed_case["Case_No"] == "N/A":
                        detailed_case["Case_No"] = basic_case.get("Case_No", "N/A")
                    if detailed_case["Case_Title"] == "N/A":
                        detailed_case["Case_Title"] = basic_case.get("Case_Title", "N/A")
                    if detailed_case["Status"] == "N/A":
                        detailed_case["Status"] = basic_case.get("Status", "N/A")
                    
                    page_cases.append(detailed_case)
                    print(f"✅ Case {i+1} processed successfully")
                else:
                    # Fallback to basic case with enhanced structure
                    print(f"⚠️ Using basic info for case {i+1}")
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
                
                # Small delay between cases
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing case {i+1}: {e}")
                continue
        
        print(f"✅ Completed page processing: {len(page_cases)} cases extracted")
        return page_cases
    
    def click_page_number(self, page_num):
        """Click specific page number for pagination (same as working extractor)"""
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
    
    def extract_with_pagination(self, max_pages=5):
        """Extract with pagination support (enhanced version of working extractor)"""
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
    
    def extract_all_strategies(self):
        """Extract using all search strategies (same structure as working extractor)"""
        try:
            all_cases = []
            
            for i, strategy in enumerate(self.search_strategies):
                print(f"\n🎯 Strategy {i+1}/{len(self.search_strategies)}: {strategy}")
                
                # Navigate to site for each strategy
                if not self.navigate_to_site():
                    continue
                
                # Perform search
                if self.perform_search(strategy):
                    # Extract with pagination and View Details
                    strategy_cases = self.extract_with_pagination(max_pages=3)
                    
                    if strategy_cases:
                        all_cases.extend(strategy_cases)
                        print(f"✅ Strategy {i+1} completed: {len(strategy_cases)} cases")
                    else:
                        print(f"⚠️ Strategy {i+1}: No cases found")
                
                # Delay between strategies
                time.sleep(5)
            
            self.all_extracted_cases = all_cases
            print(f"\n🎯 All strategies completed: {len(all_cases)} total cases")
            
            return True
            
        except Exception as e:
            print(f"❌ Strategy execution failed: {e}")
            return False
    
    def remove_duplicates(self):
        """Remove duplicate cases based on Case_No"""
        seen_cases = set()
        unique_cases = []
        
        for case in self.all_extracted_cases:
            case_no = case.get("Case_No", "")
            if case_no and case_no != "N/A" and case_no not in seen_cases:
                seen_cases.add(case_no)
                unique_cases.append(case)
        
        duplicates_removed = len(self.all_extracted_cases) - len(unique_cases)
        self.all_extracted_cases = unique_cases
        
        print(f"🔍 Removed {duplicates_removed} duplicate cases")
        print(f"✅ Unique cases: {len(unique_cases)}")
        
        return unique_cases
    
    def save_results(self, filename="enhanced_complete_extraction_with_details.json"):
        """Save extraction results to JSON file"""
        try:
            # Remove duplicates
            self.remove_duplicates()
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_extracted_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.all_extracted_cases)} cases to {filename}")
            
            # Print sample cases for verification
            if self.all_extracted_cases:
                print(f"\n📋 Sample extracted cases with detailed information:")
                for i, case in enumerate(self.all_extracted_cases[:3]):
                    print(f"\n{i+1}. Case: {case.get('Case_No', 'N/A')}")
                    print(f"   Title: {case.get('Case_Title', 'N/A')[:80]}...")
                    print(f"   Status: {case.get('Status', 'N/A')}")
                    print(f"   Institution Date: {case.get('Institution_Date', 'N/A')}")
                    print(f"   AOR: {case.get('Advocates', {}).get('AOR', 'N/A')}")
                    print(f"   Memo File: {case.get('Petition_Appeal_Memo', {}).get('File', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False
    
    def run_complete_extraction(self):
        """Run the complete extraction process"""
        print("🚀 ENHANCED COMPLETE EXTRACTION WITH VIEW DETAILS")
        print("=" * 60)
        print("Using the successful extractor approach with View Details enhancement")
        print("=" * 60)
        
        try:
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Extract all strategies
            if self.extract_all_strategies():
                # Save results
                self.save_results()
                return True
            else:
                print("❌ Extraction failed")
                return False
            
        except KeyboardInterrupt:
            print("\n⚠️ Extraction interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        finally:
            if self.driver:
                print("🔄 Closing browser...")
                self.driver.quit()


def main():
    """Main function"""
    extractor = EnhancedCompleteExtractor()
    extractor.run_complete_extraction()


if __name__ == "__main__":
    main()