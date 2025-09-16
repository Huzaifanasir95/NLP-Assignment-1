"""
Fixed Case Information Extractor
Uses correct element IDs discovered from website inspection
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


class FixedCaseExtractor:
    """Fixed extractor with correct element IDs"""
    
    def __init__(self):
        self.driver = None
        self.extracted_cases = []
        
        # Correct element IDs from website inspection
        self.element_ids = {
            'case_type': 'ddlCaseType',
            'year': 'ddlYear', 
            'registry': 'ddlRegistry',
            'judge': 'ddlJudge',
            'case_no': 'txtCaseNo',
            'case_title': 'txtCaseTitle',
            'search_button': 'btnSearch'
        }
        
        # Available options from inspection
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
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
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
        """Navigate to the case information website"""
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
        """Perform search with given parameters"""
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
            print("🔍 Clicking search button...")
            search_button.click()
            
            # Wait for results to load
            time.sleep(8)
            print("✅ Search completed, waiting for results...")
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def extract_cases_from_current_page(self):
        """Extract cases from the current results page"""
        cases = []
        
        try:
            print("📋 Extracting cases from current page...")
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for tables containing case data
            tables = soup.find_all('table')
            print(f"   Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"   Table {table_idx + 1}: {len(rows)} rows")
                
                for row_idx, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:  # Minimum expected columns for case data
                        # Extract text from each cell
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Look for case numbers in first few cells
                        case_no = "N/A"
                        case_title = "N/A"
                        status = "N/A"
                        institution_date = "N/A"
                        
                        for i, cell_text in enumerate(cell_texts):
                            # Check for case number patterns
                            if re.search(r'[A-Z]\.[A-Z]\..*\d+.*[/-].*2025', cell_text):
                                case_no = cell_text
                            # Check for case titles (usually longer text with 'vs')
                            elif len(cell_text) > 20 and ('vs' in cell_text.lower() or 'v.' in cell_text.lower()):
                                case_title = cell_text[:200]  # Limit length
                            # Check for status
                            elif any(status_word in cell_text.lower() for status_word in ['pending', 'decided', 'dismissed', 'allowed']):
                                status = cell_text
                            # Check for dates or "View Details"
                            elif 'view details' in cell_text.lower() or re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', cell_text):
                                institution_date = cell_text
                        
                        # Only include if we found a valid case number for 2025
                        if case_no != "N/A" and "2025" in case_no:
                            case_data = {
                                "Case_No": case_no,
                                "Case_Title": case_title,
                                "Status": status,
                                "Institution_Date": institution_date
                            }
                            cases.append(case_data)
                            print(f"   ✅ Found case: {case_no}")
            
            # Alternative method: Look for direct text patterns
            if not cases:
                print("   🔍 Trying alternative extraction method...")
                all_text = soup.get_text()
                
                # Find all case number patterns
                case_patterns = re.findall(r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/2025)', all_text)
                
                for pattern in case_patterns:
                    case_data = {
                        "Case_No": pattern,
                        "Case_Title": "N/A",
                        "Status": "Pending",
                        "Institution_Date": "View Details"
                    }
                    cases.append(case_data)
                    print(f"   ✅ Found case pattern: {pattern}")
            
            print(f"📊 Extracted {len(cases)} cases from current page")
            return cases
            
        except Exception as e:
            print(f"❌ Error extracting cases: {e}")
            return []
    
    def check_pagination(self):
        """Check for pagination links"""
        try:
            # Look for numbered pagination
            pagination_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$') and string-length(text()) <= 3]")
            
            if pagination_links:
                print(f"📄 Found {len(pagination_links)} pagination links")
                for link in pagination_links[:5]:  # Show first 5
                    print(f"   Page link: {link.text}")
                return pagination_links
            else:
                print("⚠️ No pagination found")
                return []
                
        except Exception as e:
            print(f"❌ Error checking pagination: {e}")
            return []
    
    def click_next_page(self, current_page=1):
        """Click next page in pagination"""
        try:
            next_page = current_page + 1
            
            # Look for next page link
            next_link = self.driver.find_element(By.XPATH, f"//a[text()='{next_page}']")
            
            if next_link and next_link.is_enabled():
                print(f"🔄 Clicking page {next_page}")
                next_link.click()
                time.sleep(5)
                return True
            else:
                print(f"⚠️ Page {next_page} not found or not clickable")
                return False
                
        except Exception as e:
            print(f"❌ Error clicking next page: {e}")
            return False
    
    def test_small_extraction(self):
        """Test extraction with small data set"""
        print("🧪 Testing small extraction...")
        
        if not self.setup_driver():
            return False
        
        try:
            if not self.navigate_to_website():
                return False
            
            # Test with Civil Appeals in Lahore for 2025
            if self.perform_search(case_type="C.A.", registry="Lahore", year=2025):
                # Extract from first page only
                cases = self.extract_cases_from_current_page()
                
                if cases:
                    self.extracted_cases.extend(cases)
                    print(f"✅ Test extraction successful: {len(cases)} cases")
                    
                    # Show first few cases
                    for i, case in enumerate(cases[:3]):
                        print(f"   Case {i+1}: {case['Case_No']} - {case['Case_Title'][:50]}")
                    
                    # Check for pagination
                    pagination = self.check_pagination()
                    if pagination:
                        print(f"✅ Pagination available: {len(pagination)} pages")
                    
                    return True
                else:
                    print("⚠️ No cases found in test extraction")
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"❌ Test extraction failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def save_results(self, filename="test_extraction_results.json"):
        """Save extracted results to JSON file"""
        if not self.extracted_cases:
            print("⚠️ No cases to save")
            return False
        
        try:
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.extracted_cases)} cases to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ WebDriver closed")
            except:
                pass


def main():
    """Main test function"""
    print("🏛️ Fixed Case Extractor Test")
    print("=" * 40)
    
    extractor = FixedCaseExtractor()
    
    if extractor.test_small_extraction():
        extractor.save_results("test_extraction_small.json")
        print("\n🎯 Test completed successfully!")
        print("   Check test_extraction_small.json for results")
    else:
        print("\n❌ Test failed")


if __name__ == "__main__":
    main()