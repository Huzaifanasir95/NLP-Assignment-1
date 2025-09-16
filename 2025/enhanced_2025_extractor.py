"""
Enhanced 2025 Extractor with Proper View Details Handling
Clicks each View Details link, extracts detailed information, then continues
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup


class Enhanced2025Extractor:
    """Enhanced extractor that properly handles View Details clicking"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        self.extracted_cases = []
        self.total_extracted = 0
        
        # Search strategies for 2025
        self.search_strategies = [
            {"registry": "Lahore", "case_type": "Civil Appeals"},
            {"registry": "Karachi", "case_type": "Civil Appeals"}, 
            {"registry": "Islamabad", "case_type": "Constitution Petitions"},
            {"registry": "Lahore", "case_type": "Criminal Appeals"},
            {"registry": "Karachi", "case_type": "Criminal Appeals"},
            {"registry": "Lahore", "case_type": "Review Petitions"},
            {"registry": "Karachi", "case_type": "Miscellaneous Applications"}
        ]
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            print("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            return False
    
    def perform_search(self, strategy):
        """Perform search with given strategy"""
        try:
            print(f"🔍 Searching: {strategy}")
            
            # Navigate to search page
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Fill year dropdown for 2025
            year_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlYear"))
            )
            year_select = Select(year_dropdown)
            year_select.select_by_visible_text("2025")
            time.sleep(1)
            
            # Fill registry dropdown
            registry = strategy.get("registry")
            if registry:
                registry_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ddlRegistry"))
                )
                registry_select = Select(registry_dropdown)
                try:
                    registry_select.select_by_visible_text(registry)
                    print(f"✅ Selected registry: {registry}")
                except:
                    # Try partial match
                    for option in registry_select.options:
                        if registry.lower() in option.text.lower():
                            registry_select.select_by_visible_text(option.text)
                            print(f"✅ Selected alternative registry: {option.text}")
                            break
                time.sleep(1)
            
            # Fill case type dropdown
            case_type = strategy.get("case_type")
            if case_type:
                case_type_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ddlCaseType"))
                )
                case_type_select = Select(case_type_dropdown)
                try:
                    case_type_select.select_by_visible_text(case_type)
                    print(f"✅ Selected case type: {case_type}")
                except:
                    # Try partial match
                    for option in case_type_select.options:
                        if case_type.lower() in option.text.lower():
                            case_type_select.select_by_visible_text(option.text)
                            print(f"✅ Selected alternative case type: {option.text}")
                            break
                time.sleep(1)
            
            # Click search
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnSearch"))
            )
            search_button.click()
            time.sleep(5)
            
            print("✅ Search completed")
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def get_case_list_from_page(self):
        """Get list of cases with their case numbers from current page"""
        cases = []
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for tables containing case data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        case_no = "N/A"
                        case_title = "N/A"
                        status = "N/A"
                        
                        for i, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            
                            # Case number
                            if i <= 2 and any(char.isdigit() for char in cell_text):
                                if "2025" in cell_text:
                                    case_no = self.extract_case_number(cell_text)
                            
                            # Case title
                            elif len(cell_text) > 20 and any(keyword in cell_text.lower() for keyword in ['vs', 'v.', 'versus']):
                                case_title = cell_text[:200]
                            
                            # Status
                            elif any(keyword in cell_text.lower() for keyword in ['pending', 'disposed']):
                                status = cell_text
                        
                        if case_no != "N/A" and "2025" in case_no:
                            cases.append({
                                "case_no": case_no,
                                "case_title": case_title,
                                "status": status
                            })
            
            print(f"📋 Found {len(cases)} cases on current page")
            return cases
            
        except Exception as e:
            print(f"❌ Error getting case list: {e}")
            return []
    
    def extract_case_number(self, text):
        """Extract case number from text"""
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
        
        return text.strip() if text.strip() else "N/A"
    
    def click_view_details_for_case(self, case_index):
        """Click View Details for a specific case by index"""
        try:
            # Get fresh View Details links
            view_details_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index < len(view_details_links):
                link = view_details_links[case_index]
                
                # Scroll to the link
                self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                time.sleep(1)
                
                # Click the link
                self.driver.execute_script("arguments[0].click();", link)
                time.sleep(3)
                
                print(f"✅ Clicked View Details for case {case_index + 1}")
                return True
            else:
                print(f"⚠️ Case index {case_index} out of range")
                return False
                
        except Exception as e:
            print(f"❌ Error clicking View Details for case {case_index + 1}: {e}")
            return False
    
    def extract_detailed_case_info(self):
        """Extract detailed case information from View Details page"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            detailed_info = {
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
            
            # Extract Case Information section
            page_text = soup.get_text()
            
            # Extract Case Title
            title_match = re.search(r'Case Title:\s*([^\n\r]+)', page_text)
            if title_match:
                detailed_info["Case_Title"] = title_match.group(1).strip()
            
            # Extract Case No
            case_no_match = re.search(r'Case No:\s*([^\n\r]+)', page_text)
            if case_no_match:
                detailed_info["Case_No"] = case_no_match.group(1).strip()
            
            # Extract Status
            status_match = re.search(r'Status:\s*([^\n\r]+)', page_text)
            if status_match:
                detailed_info["Status"] = status_match.group(1).strip()
            
            # Extract Institution Date
            inst_date_match = re.search(r'Institution Date:\s*([^\n\r]+)', page_text)
            if inst_date_match:
                detailed_info["Institution_Date"] = inst_date_match.group(1).strip()
            
            # Extract Disposal Date
            disp_date_match = re.search(r'Disposal Date:\s*([^\n\r]+)', page_text)
            if disp_date_match:
                detailed_info["Disposal_Date"] = disp_date_match.group(1).strip()
            
            # Extract AOR/ASC information
            aor_asc_match = re.search(r'AOR/ASC:\s*([^\n\r]+(?:\n[^\n\r]+)*)', page_text)
            if aor_asc_match:
                aor_text = aor_asc_match.group(1).strip()
                lines = aor_text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if '(ASC)' in line:
                        detailed_info["Advocates"]["ASC"] = line
                    elif '(AOR)' in line:
                        detailed_info["Advocates"]["AOR"] = line
                    elif 'Prosecutor' in line:
                        detailed_info["Advocates"]["Prosecutor"] = line
            
            # Extract Petition/Appeal Memo
            memo_match = re.search(r'Petition/Appeal Memo:\s*([^\n\r]+)', page_text)
            if memo_match:
                detailed_info["Petition_Appeal_Memo"]["File"] = memo_match.group(1).strip()
            
            # Extract History information
            history_match = re.search(r'History:\s*([^\n\r]+)', page_text)
            if history_match:
                history_text = history_match.group(1).strip()
                if "No Fixation History Found" not in history_text:
                    detailed_info["History"].append({"note": history_text})
            
            # Look for any judgment/order links
            judgment_links = soup.find_all('a', string=lambda text: text and 'judgment' in text.lower())
            if judgment_links:
                detailed_info["Judgement_Order"]["File"] = judgment_links[0].get('href', 'Available')
                detailed_info["Judgement_Order"]["Type"] = "PDF"
            
            return detailed_info
            
        except Exception as e:
            print(f"❌ Error extracting detailed info: {e}")
            return None
    
    def navigate_back_to_search_results(self):
        """Navigate back to search results"""
        try:
            # Try browser back button
            self.driver.back()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"⚠️ Back navigation failed: {e}")
            return False
    
    def extract_cases_from_page_with_details(self):
        """Extract all cases from current page with detailed information"""
        page_cases = []
        
        # Get list of cases on current page
        case_list = self.get_case_list_from_page()
        
        if not case_list:
            print("⚠️ No cases found on current page")
            return []
        
        print(f"📋 Processing {len(case_list)} cases for detailed extraction...")
        
        for i, basic_case in enumerate(case_list):
            try:
                print(f"\n🔍 Processing case {i+1}/{len(case_list)}: {basic_case['case_no']}")
                
                # Click View Details for this case
                if self.click_view_details_for_case(i):
                    # Extract detailed information
                    detailed_case = self.extract_detailed_case_info()
                    
                    if detailed_case:
                        # Merge basic info with detailed info
                        if detailed_case["Case_No"] == "N/A":
                            detailed_case["Case_No"] = basic_case["case_no"]
                        if detailed_case["Case_Title"] == "N/A":
                            detailed_case["Case_Title"] = basic_case["case_title"]
                        if detailed_case["Status"] == "N/A":
                            detailed_case["Status"] = basic_case["status"]
                        
                        page_cases.append(detailed_case)
                        print(f"✅ Extracted detailed info for {detailed_case['Case_No']}")
                    else:
                        print(f"⚠️ Failed to extract details, using basic info")
                        # Fallback to basic info with enhanced structure
                        fallback_case = {
                            "Case_No": basic_case["case_no"],
                            "Case_Title": basic_case["case_title"],
                            "Status": basic_case["status"],
                            "Institution_Date": "View Details",
                            "Disposal_Date": "N/A",
                            "Advocates": {"ASC": "N/A", "AOR": "N/A", "Prosecutor": "N/A"},
                            "Petition_Appeal_Memo": {"File": "N/A", "Type": "N/A"},
                            "History": [],
                            "Judgement_Order": {"File": "N/A", "Type": "N/A"}
                        }
                        page_cases.append(fallback_case)
                    
                    # Navigate back to search results
                    if not self.navigate_back_to_search_results():
                        # If back navigation fails, re-perform the search
                        print("⚠️ Re-performing search to continue...")
                        time.sleep(2)
                        break  # Exit the loop and return what we have
                    
                    # Wait before processing next case
                    time.sleep(2)
                
                else:
                    print(f"⚠️ Failed to click View Details for case {i+1}")
                    
            except Exception as e:
                print(f"❌ Error processing case {i+1}: {e}")
                continue
        
        print(f"✅ Completed processing page: {len(page_cases)} cases extracted")
        return page_cases
    
    def click_next_page(self, page_num):
        """Click specific page number for pagination"""
        try:
            print(f"🔄 Looking for page {page_num}")
            
            page_selectors = [
                f"//a[text()='{page_num}']",
                f"//a[normalize-space(text())='{page_num}']",
                f"//input[@value='{page_num}']"
            ]
            
            for selector in page_selectors:
                try:
                    page_link = self.driver.find_element(By.XPATH, selector)
                    if page_link and page_link.is_enabled() and page_link.is_displayed():
                        print(f"🔄 Clicking page {page_num}")
                        self.driver.execute_script("arguments[0].click();", page_link)
                        time.sleep(3)
                        return True
                except:
                    continue
            
            print(f"⚠️ Page {page_num} not found or not clickable")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking page {page_num}: {e}")
            return False
    
    def extract_with_pagination(self, max_pages=5):
        """Extract data with pagination support"""
        all_cases = []
        current_page = 1
        
        while current_page <= max_pages:
            print(f"\n📄 Processing page {current_page}")
            
            # Extract cases from current page with detailed information
            page_cases = self.extract_cases_from_page_with_details()
            
            if page_cases:
                all_cases.extend(page_cases)
                print(f"✅ Page {current_page}: {len(page_cases)} cases extracted")
            else:
                print(f"⚠️ Page {current_page}: No cases extracted")
            
            # Try to go to next page
            if not self.click_next_page(current_page + 1):
                print("📄 No more pages available")
                break
            
            current_page += 1
            time.sleep(3)
        
        return all_cases
    
    def run_complete_extraction(self):
        """Run complete extraction for all strategies"""
        if not self.setup_driver():
            return False
        
        try:
            all_extracted_cases = []
            
            for i, strategy in enumerate(self.search_strategies):
                print(f"\n🎯 Strategy {i+1}/{len(self.search_strategies)}: {strategy}")
                
                if self.perform_search(strategy):
                    # Extract with pagination
                    strategy_cases = self.extract_with_pagination(max_pages=3)
                    
                    if strategy_cases:
                        all_extracted_cases.extend(strategy_cases)
                        print(f"✅ Strategy {i+1} completed: {len(strategy_cases)} cases")
                    else:
                        print(f"⚠️ Strategy {i+1}: No cases found")
                
                # Delay between strategies
                time.sleep(5)
            
            self.extracted_cases = all_extracted_cases
            self.total_extracted = len(all_extracted_cases)
            
            print(f"\n🎯 EXTRACTION COMPLETED!")
            print(f"📊 Total cases extracted: {self.total_extracted}")
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def remove_duplicates(self):
        """Remove duplicate cases based on Case_No"""
        seen_cases = set()
        unique_cases = []
        
        for case in self.extracted_cases:
            case_no = case.get("Case_No", "")
            if case_no and case_no != "N/A" and case_no not in seen_cases:
                seen_cases.add(case_no)
                unique_cases.append(case)
        
        removed_count = len(self.extracted_cases) - len(unique_cases)
        self.extracted_cases = unique_cases
        
        print(f"🔍 Removed {removed_count} duplicate cases")
        return unique_cases
    
    def save_results(self, filename="enhanced_2025_extraction.json"):
        """Save extraction results"""
        try:
            # Remove duplicates
            self.remove_duplicates()
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.extracted_cases)} cases to {filename}")
            
            # Print sample cases
            if self.extracted_cases:
                print(f"\n📋 Sample extracted cases:")
                for i, case in enumerate(self.extracted_cases[:3]):
                    print(f"   {i+1}. {case.get('Case_No', 'N/A')}")
                    print(f"      Title: {case.get('Case_Title', 'N/A')[:80]}...")
                    print(f"      Status: {case.get('Status', 'N/A')}")
                    print(f"      Institution: {case.get('Institution_Date', 'N/A')}")
                    print(f"      AOR: {case.get('Advocates', {}).get('AOR', 'N/A')}")
                    print()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False


def main():
    """Main function to run enhanced extraction"""
    print("🚀 ENHANCED 2025 EXTRACTION WITH VIEW DETAILS")
    print("=" * 60)
    
    extractor = Enhanced2025Extractor()
    
    if extractor.run_complete_extraction():
        extractor.save_results("enhanced_2025_with_details.json")
    else:
        print("❌ Extraction failed")


if __name__ == "__main__":
    main()