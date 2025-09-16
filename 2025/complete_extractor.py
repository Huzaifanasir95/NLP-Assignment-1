"""
Complete Case Information Extractor with Pagination
Extracts all 2025 case data with proper pagination handling
"""

import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


class CompleteCaseExtractor:
    """Complete extractor with pagination support"""
    
    def __init__(self):
        self.driver = None
        self.all_extracted_cases = []
        
        # Element IDs from website inspection
        self.element_ids = {
            'case_type': 'ddlCaseType',
            'year': 'ddlYear', 
            'registry': 'ddlRegistry',
            'search_button': 'btnSearch'
        }
        
        # Search strategies for comprehensive coverage
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
        
        # Option mappings from inspection
        self.case_type_options = {
            'C.A.': '1',
            'C.M.A.': '21', 
            'C.P.': '13'
        }
        
        self.registry_options = {
            'Islamabad': 'I',
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
        """Navigate to case information website"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def perform_search(self, strategy):
        """Perform search with given strategy"""
        try:
            case_type = strategy['case_type']
            registry = strategy['registry']
            
            print(f"🔍 Search: {case_type} in {registry} for 2025")
            
            # Select case type
            if case_type in self.case_type_options:
                case_type_select = self.driver.find_element(By.ID, self.element_ids['case_type'])
                select = Select(case_type_select)
                select.select_by_value(self.case_type_options[case_type])
                time.sleep(1)
            
            # Select registry
            if registry in self.registry_options:
                registry_select = self.driver.find_element(By.ID, self.element_ids['registry'])
                select = Select(registry_select)
                select.select_by_value(self.registry_options[registry])
                time.sleep(1)
            
            # Select year 2025
            year_select = self.driver.find_element(By.ID, self.element_ids['year'])
            select = Select(year_select)
            select.select_by_value('2025')
            time.sleep(1)
            
            # Click search
            search_button = self.driver.find_element(By.ID, self.element_ids['search_button'])
            search_button.click()
            time.sleep(8)  # Wait for results
            
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def extract_cases_from_page(self):
        """Extract cases from current page"""
        cases = []
        
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find tables with case data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Extract case information
                        case_no = "N/A"
                        case_title = "N/A"
                        status = "Pending"
                        institution_date = "View Details"
                        
                        for cell_text in cell_texts:
                            # Case number pattern for 2025
                            if re.search(r'[A-Z]\.[A-Z]\..*\d+.*[/-].*2025', cell_text):
                                case_no = cell_text
                            # Case title (longer text with vs)
                            elif len(cell_text) > 20 and ('vs' in cell_text.lower() or 'v.' in cell_text.lower()):
                                case_title = cell_text[:200]
                            # Status
                            elif any(word in cell_text.lower() for word in ['pending', 'decided', 'dismissed']):
                                status = cell_text
                            # Institution date
                            elif 'view details' in cell_text.lower():
                                institution_date = cell_text
                        
                        # Only include valid 2025 cases
                        if case_no != "N/A" and "2025" in case_no:
                            case_data = {
                                "Case_No": case_no,
                                "Case_Title": case_title,
                                "Status": status,
                                "Institution_Date": institution_date
                            }
                            cases.append(case_data)
            
            return cases
            
        except Exception as e:
            print(f"❌ Error extracting cases: {e}")
            return []
    
    def get_pagination_links(self):
        """Get available pagination links"""
        try:
            # Look for numbered pagination links
            pagination_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$') and string-length(text()) <= 3 and text() != '']")
            
            if pagination_links:
                page_numbers = []
                for link in pagination_links:
                    try:
                        page_num = int(link.text)
                        page_numbers.append(page_num)
                    except:
                        continue
                
                return sorted(page_numbers)
            
            return []
            
        except Exception as e:
            print(f"❌ Error getting pagination: {e}")
            return []
    
    def click_page(self, page_number):
        """Click specific page number"""
        try:
            page_link = self.driver.find_element(By.XPATH, f"//a[text()='{page_number}']")
            
            if page_link and page_link.is_enabled():
                print(f"🔄 Clicking page {page_number}")
                page_link.click()
                time.sleep(5)  # Wait for page to load
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error clicking page {page_number}: {e}")
            return False
    
    def extract_with_pagination(self, strategy, max_pages=10):
        """Extract cases with pagination for a specific strategy"""
        strategy_cases = []
        
        try:
            print(f"\n📄 Starting pagination extraction for {strategy}")
            
            # Extract from first page
            page_1_cases = self.extract_cases_from_page()
            if page_1_cases:
                strategy_cases.extend(page_1_cases)
                print(f"   Page 1: {len(page_1_cases)} cases")
            
            # Get pagination info
            available_pages = self.get_pagination_links()
            
            if available_pages:
                print(f"   Available pages: {available_pages}")
                
                # Process additional pages (limit to max_pages)
                pages_to_process = [p for p in available_pages if p > 1 and p <= max_pages]
                
                for page_num in pages_to_process:
                    if self.click_page(page_num):
                        page_cases = self.extract_cases_from_page()
                        if page_cases:
                            strategy_cases.extend(page_cases)
                            print(f"   Page {page_num}: {len(page_cases)} cases")
                        else:
                            print(f"   Page {page_num}: No cases found")
                    else:
                        print(f"   Page {page_num}: Failed to click")
                        break
            else:
                print("   No pagination found")
            
            print(f"✅ Strategy completed: {len(strategy_cases)} total cases")
            return strategy_cases
            
        except Exception as e:
            print(f"❌ Pagination extraction failed: {e}")
            return strategy_cases
    
    def run_complete_extraction(self, max_pages_per_search=5, test_mode=False):
        """Run complete extraction with all strategies"""
        print("🏛️ Supreme Court Case Extractor - Complete Extraction")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            strategies_to_process = self.search_strategies[:2] if test_mode else self.search_strategies
            
            for i, strategy in enumerate(strategies_to_process):
                print(f"\n🔍 Strategy {i+1}/{len(strategies_to_process)}: {strategy}")
                
                # Navigate to fresh page for each search
                if not self.navigate_to_website():
                    continue
                
                # Perform search
                if self.perform_search(strategy):
                    # Extract with pagination
                    strategy_cases = self.extract_with_pagination(strategy, max_pages_per_search)
                    
                    # Add to overall results
                    self.all_extracted_cases.extend(strategy_cases)
                    
                    print(f"✅ Strategy {i+1} completed: {len(strategy_cases)} cases")
                else:
                    print(f"❌ Strategy {i+1} failed")
                
                # Wait between strategies
                time.sleep(3)
            
            # Remove duplicates
            unique_cases = self.remove_duplicates(self.all_extracted_cases)
            self.all_extracted_cases = unique_cases
            
            print(f"\n🎯 Extraction completed!")
            print(f"   Total cases extracted: {len(self.all_extracted_cases)}")
            print(f"   Strategies processed: {len(strategies_to_process)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Complete extraction failed: {e}")
            return False
        finally:
            self.cleanup()
    
    def remove_duplicates(self, cases):
        """Remove duplicate cases based on Case_No"""
        seen = set()
        unique_cases = []
        
        for case in cases:
            case_no = case.get('Case_No', '')
            if case_no not in seen:
                seen.add(case_no)
                unique_cases.append(case)
        
        print(f"🔄 Removed {len(cases) - len(unique_cases)} duplicates")
        return unique_cases
    
    def save_results(self, filename="complete_case_extraction_2025.json"):
        """Save all extracted results"""
        if not self.all_extracted_cases:
            print("⚠️ No cases to save")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_extracted_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.all_extracted_cases)} cases to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save: {e}")
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
    """Main execution function"""
    print("Choose extraction mode:")
    print("1. Test mode (2 strategies, 3 pages each)")
    print("2. Full extraction (all strategies, 5 pages each)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    extractor = CompleteCaseExtractor()
    
    if choice == "1":
        print("\n🧪 Running in TEST MODE")
        success = extractor.run_complete_extraction(max_pages_per_search=3, test_mode=True)
        filename = "test_complete_extraction.json"
    else:
        print("\n🚀 Running FULL EXTRACTION")
        success = extractor.run_complete_extraction(max_pages_per_search=5, test_mode=False)
        filename = "complete_case_extraction_2025.json"
    
    if success:
        extractor.save_results(filename)
        print(f"\n🎯 Extraction completed successfully!")
        print(f"   Results saved to: {filename}")
        print(f"   Total cases: {len(extractor.all_extracted_cases)}")
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    main()