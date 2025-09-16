"""
Test View Details Extraction for 2025 Data
Tests whether the 2025 extractors capture detailed information from "View Details" clicks
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


class ViewDetailsExtractor:
    """Test extractor to check View Details functionality"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        options = Options()
        # Remove headless for debugging
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            print("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            return False
    
    def perform_search(self):
        """Perform a simple search to get some 2025 cases"""
        try:
            print("🌐 Navigating to search page...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Fill year dropdown for 2025
            print("📅 Selecting year 2025...")
            year_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlYear"))
            )
            year_select = Select(year_dropdown)
            year_select.select_by_visible_text("2025")
            time.sleep(1)
            
            # Fill registry dropdown
            print("🏛️ Selecting registry Lahore...")
            registry_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlRegistry"))
            )
            registry_select = Select(registry_dropdown)
            registry_select.select_by_visible_text("Lahore")
            time.sleep(1)
            
            # Click search
            print("🔍 Clicking search...")
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
    
    def check_current_extraction(self):
        """Check what the current extraction method captures"""
        print("\n📋 CHECKING CURRENT EXTRACTION METHOD:")
        print("=" * 50)
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for tables
            tables = soup.find_all('table')
            cases_found = []
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        case_data = {
                            "Case_No": "N/A",
                            "Case_Title": "N/A",
                            "Status": "N/A",
                            "Institution_Date": "N/A"
                        }
                        
                        for i, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            
                            if i <= 2 and any(char.isdigit() for char in cell_text):
                                if "2025" in cell_text:
                                    case_data["Case_No"] = cell_text
                            elif len(cell_text) > 20 and any(keyword in cell_text.lower() for keyword in ['vs', 'v.']):
                                case_data["Case_Title"] = cell_text[:100]
                            elif any(keyword in cell_text.lower() for keyword in ['pending', 'disposed']):
                                case_data["Status"] = cell_text
                            elif "view details" in cell_text.lower():
                                case_data["Institution_Date"] = cell_text
                        
                        if case_data["Case_No"] != "N/A" and "2025" in case_data["Case_No"]:
                            cases_found.append(case_data)
            
            print(f"📊 Current method found: {len(cases_found)} cases")
            for i, case in enumerate(cases_found[:3]):
                print(f"   {i+1}. {case['Case_No']} - {case['Institution_Date']}")
            
            return cases_found
            
        except Exception as e:
            print(f"❌ Current extraction failed: {e}")
            return []
    
    def test_view_details_clicking(self):
        """Test clicking on View Details links"""
        print("\n🔍 TESTING VIEW DETAILS CLICKING:")
        print("=" * 50)
        
        detailed_cases = []
        
        try:
            # Look for "View Details" links
            view_details_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            print(f"📋 Found {len(view_details_links)} 'View Details' links")
            
            if view_details_links:
                # Test clicking on the first few links
                for i, link in enumerate(view_details_links[:3]):
                    try:
                        print(f"\n🔍 Testing link {i+1}...")
                        
                        # Scroll to the link and click
                        self.driver.execute_script("arguments[0].scrollIntoView();", link)
                        time.sleep(1)
                        
                        # Click the link
                        self.driver.execute_script("arguments[0].click();", link)
                        time.sleep(3)
                        
                        # Check if detailed information appeared
                        detailed_info = self.extract_detailed_case_info()
                        
                        if detailed_info:
                            detailed_cases.append(detailed_info)
                            print(f"✅ Extracted detailed info for case {i+1}")
                        else:
                            print(f"⚠️ No detailed info found for case {i+1}")
                        
                    except Exception as e:
                        print(f"❌ Error clicking link {i+1}: {e}")
            
            else:
                print("⚠️ No 'View Details' links found")
                
                # Alternative: look for other clickable elements
                print("🔍 Looking for alternative clickable elements...")
                clickable_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript')]")
                print(f"📋 Found {len(clickable_elements)} javascript links")
                
                # Try to find Institution Date or View Details in different formats
                institution_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Institution') or contains(text(), 'Details')]")
                print(f"📋 Found {len(institution_links)} institution/details links")
            
            return detailed_cases
            
        except Exception as e:
            print(f"❌ View Details testing failed: {e}")
            return []
    
    def extract_detailed_case_info(self):
        """Extract detailed case information after clicking View Details"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for the detailed case information structure
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
            
            # Look for case information section
            case_info_section = soup.find('div', string=lambda text: text and 'Case Information' in text)
            
            if case_info_section:
                print("📋 Found 'Case Information' section")
                
                # Extract Case Title
                case_title_element = soup.find('span', string=lambda text: text and 'Case Title:' in text)
                if case_title_element:
                    title_text = case_title_element.find_next_sibling(text=True)
                    if title_text:
                        detailed_info["Case_Title"] = title_text.strip()
                
                # Extract Case No
                case_no_element = soup.find('span', string=lambda text: text and 'Case No:' in text)
                if case_no_element:
                    case_no_text = case_no_element.find_next_sibling(text=True)
                    if case_no_text:
                        detailed_info["Case_No"] = case_no_text.strip()
                
                # Extract Status
                status_element = soup.find('span', string=lambda text: text and 'Status:' in text)
                if status_element:
                    status_text = status_element.find_next_sibling(text=True)
                    if status_text:
                        detailed_info["Status"] = status_text.strip()
                
                # Extract Advocate information
                aor_element = soup.find('span', string=lambda text: text and 'AOR/ASC:' in text)
                if aor_element:
                    aor_text = aor_element.find_next_sibling(text=True)
                    if aor_text:
                        detailed_info["Advocates"]["AOR"] = aor_text.strip()
                
                # Extract Petition/Appeal Memo
                memo_element = soup.find('span', string=lambda text: text and 'Petition/Appeal Memo:' in text)
                if memo_element:
                    memo_text = memo_element.find_next_sibling(text=True)
                    if memo_text:
                        detailed_info["Petition_Appeal_Memo"]["File"] = memo_text.strip()
                
                # Extract History table
                history_table = soup.find('table')
                if history_table:
                    history_rows = history_table.find_all('tr')[1:]  # Skip header
                    for row in history_rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            history_entry = {
                                "Fixation_Date": cells[0].get_text(strip=True) if len(cells) > 0 else "N/A",
                                "Result": cells[1].get_text(strip=True) if len(cells) > 1 else "N/A",
                                "Judgments_Orders": cells[2].get_text(strip=True) if len(cells) > 2 else "N/A"
                            }
                            detailed_info["History"].append(history_entry)
                
                return detailed_info
            
            else:
                print("⚠️ No 'Case Information' section found")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting detailed info: {e}")
            return None
    
    def analyze_page_structure(self):
        """Analyze the page structure to understand how View Details works"""
        print("\n🔍 ANALYZING PAGE STRUCTURE:")
        print("=" * 50)
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Save current page source for analysis
            with open('2025/view_details_page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("✅ Saved page source to 2025/view_details_page_source.html")
            
            # Look for all links
            all_links = soup.find_all('a')
            print(f"📋 Total links found: {len(all_links)}")
            
            # Categorize links
            view_details_links = [link for link in all_links if 'view details' in link.get_text().lower()]
            javascript_links = [link for link in all_links if link.get('href', '').startswith('javascript')]
            
            print(f"📋 'View Details' links: {len(view_details_links)}")
            print(f"📋 JavaScript links: {len(javascript_links)}")
            
            # Show samples
            if view_details_links:
                print("📋 Sample View Details links:")
                for i, link in enumerate(view_details_links[:3]):
                    print(f"   {i+1}. Text: '{link.get_text().strip()}'")
                    print(f"      Href: '{link.get('href', 'N/A')}'")
            
            if javascript_links:
                print("📋 Sample JavaScript links:")
                for i, link in enumerate(javascript_links[:3]):
                    print(f"   {i+1}. Text: '{link.get_text().strip()}'")
                    print(f"      Href: '{link.get('href', 'N/A')}'")
            
            # Look for forms and inputs
            forms = soup.find_all('form')
            inputs = soup.find_all('input')
            
            print(f"📋 Forms found: {len(forms)}")
            print(f"📋 Input elements found: {len(inputs)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Page analysis failed: {e}")
            return False
    
    def run_test(self):
        """Run the complete View Details test"""
        print("🧪 TESTING VIEW DETAILS EXTRACTION FOR 2025 DATA")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            # Perform search
            if not self.perform_search():
                return False
            
            # Check current extraction method
            current_cases = self.check_current_extraction()
            
            # Analyze page structure
            self.analyze_page_structure()
            
            # Test View Details clicking
            detailed_cases = self.test_view_details_clicking()
            
            # Summary
            print(f"\n📊 TEST SUMMARY:")
            print(f"   Current method cases: {len(current_cases)}")
            print(f"   Detailed extraction cases: {len(detailed_cases)}")
            
            if detailed_cases:
                print(f"\n✅ DETAILED CASE SAMPLE:")
                sample_case = detailed_cases[0]
                for key, value in sample_case.items():
                    if isinstance(value, dict):
                        print(f"   {key}:")
                        for sub_key, sub_value in value.items():
                            print(f"      {sub_key}: {sub_value}")
                    elif isinstance(value, list):
                        print(f"   {key}: {len(value)} entries")
                    else:
                        print(f"   {key}: {value}")
            else:
                print(f"⚠️ No detailed extraction achieved")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        
        finally:
            if self.driver:
                input("\nPress Enter to close browser...")
                self.driver.quit()


def main():
    """Main test function"""
    extractor = ViewDetailsExtractor()
    extractor.run_test()


if __name__ == "__main__":
    main()