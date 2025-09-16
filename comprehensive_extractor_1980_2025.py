"""
Comprehensive Supreme Court Pakistan Data Extractor (1980-2025)
Extracts case information from all years, registries, and case types
Based on the successful test extractors with proper element IDs and pagination
"""

import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


class ComprehensiveSupremeCourtExtractor:
    """Comprehensive extractor for Supreme Court Pakistan data (1980-2025)"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        self.extracted_cases = []
        self.total_extracted = 0
        self.failed_searches = []
        
        # Comprehensive extraction parameters
        self.start_year = 1980
        self.end_year = 2025
        
        self.registries = [
            'Islamabad', 'Lahore', 'Karachi', 'Peshawar', 'Quetta'
        ]
        
        self.case_types = [
            'Civil Appeals', 'Criminal Appeals', 'Constitution Petitions',
            'Review Petitions', 'Miscellaneous Applications', 'Original Jurisdiction'
        ]
        
        # Output directory structure
        self.output_dir = "SupremeCourt_CaseInfo"
        self.setup_directories()
        
        print(f"🎯 Comprehensive Extractor Initialized")
        print(f"   📅 Years: {self.start_year}-{self.end_year} ({self.end_year - self.start_year + 1} years)")
        print(f"   🏛️ Registries: {len(self.registries)}")
        print(f"   📝 Case Types: {len(self.case_types)}")
        print(f"   🔍 Total strategies: {len(self.registries) * len(self.case_types) * (self.end_year - self.start_year + 1)}")
    
    def setup_directories(self):
        """Create output directory structure"""
        directories = [
            self.output_dir,
            os.path.join(self.output_dir, "judgementspdf"),
            os.path.join(self.output_dir, "memopdf"),
            os.path.join(self.output_dir, "pdfs")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        print(f"✅ Created directory structure in: {self.output_dir}")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with optimal settings"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            print("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            return False
    
    def navigate_to_search_page(self):
        """Navigate to the search page"""
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Failed to navigate to search page: {e}")
            return False
    
    def perform_search(self, year, registry, case_type):
        """Perform search with given parameters"""
        try:
            print(f"🔍 Searching: {year} | {registry} | {case_type}")
            
            # Fill year dropdown
            year_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlYear"))
            )
            year_select = Select(year_dropdown)
            try:
                year_select.select_by_visible_text(str(year))
                print(f"✅ Selected year: {year}")
            except:
                print(f"⚠️ Year {year} not available")
                return False
            
            time.sleep(1)
            
            # Fill registry dropdown  
            registry_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlRegistry"))
            )
            registry_select = Select(registry_dropdown)
            try:
                registry_select.select_by_visible_text(registry)
                print(f"✅ Selected registry: {registry}")
            except:
                print(f"⚠️ Registry {registry} not available")
                # Try partial match
                for option in registry_select.options:
                    if registry.lower() in option.text.lower():
                        registry_select.select_by_visible_text(option.text)
                        print(f"✅ Selected alternative registry: {option.text}")
                        break
            
            time.sleep(1)
            
            # Fill case type dropdown
            case_type_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlCaseType"))
            )
            case_type_select = Select(case_type_dropdown)
            try:
                case_type_select.select_by_visible_text(case_type)
                print(f"✅ Selected case type: {case_type}")
            except:
                print(f"⚠️ Case type {case_type} not available")
                # Try partial match
                for option in case_type_select.options:
                    if case_type.lower() in option.text.lower():
                        case_type_select.select_by_visible_text(option.text)
                        print(f"✅ Selected alternative case type: {option.text}")
                        break
            
            time.sleep(1)
            
            # Click search button
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnSearch"))
            )
            search_button.click()
            print("🔍 Search submitted")
            
            # Wait for results
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            self.failed_searches.append({
                "year": year,
                "registry": registry, 
                "case_type": case_type,
                "error": str(e)
            })
            return False
    
    def extract_cases_from_page(self):
        """Extract cases from current page"""
        cases = []
        
        try:
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for tables containing case data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Skip header row
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        case_data = self.extract_case_from_row(cells)
                        if case_data:
                            cases.append(case_data)
            
            # Alternative extraction method if no tables found
            if not cases:
                cases = self.extract_cases_alternative_method(soup)
            
            print(f"📋 Extracted {len(cases)} cases from current page")
            return cases
            
        except Exception as e:
            print(f"❌ Error extracting cases: {e}")
            return []
    
    def extract_case_from_row(self, cells):
        """Extract case information from table row"""
        try:
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
                    "Type": "N/A"
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A"
                }
            }
            
            # Extract information from cells
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Case number patterns
                if i <= 2 and any(char.isdigit() for char in cell_text):
                    case_no = self.extract_case_number(cell_text)
                    if case_no != "N/A":
                        case_data["Case_No"] = case_no
                
                # Case title
                elif len(cell_text) > 20 and any(keyword in cell_text.lower() for keyword in ['vs', 'v.', 'versus']):
                    case_data["Case_Title"] = cell_text[:200]
                
                # Status
                elif any(keyword in cell_text.lower() for keyword in ['pending', 'decided', 'dismissed', 'allowed', 'disposed']):
                    case_data["Status"] = cell_text
                
                # Date information
                elif any(keyword in cell_text.lower() for keyword in ['date', 'view details']):
                    case_data["Institution_Date"] = cell_text
                
                # Advocate information
                elif any(keyword in cell_text.lower() for keyword in ['advocate', 'counsel']):
                    if 'asc' in cell_text.lower():
                        case_data["Advocates"]["ASC"] = cell_text
                    elif 'aor' in cell_text.lower():
                        case_data["Advocates"]["AOR"] = cell_text
            
            # Validate case data
            if case_data["Case_No"] != "N/A":
                return case_data
            
        except Exception as e:
            print(f"⚠️ Error extracting case from row: {e}")
        
        return None
    
    def extract_case_number(self, text):
        """Extract case number from text"""
        import re
        
        patterns = [
            r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/\d{4})',
            r'([A-Z]\.[A-Z]\.\d+/\d{4})',
            r'([A-Z]+\.\d+/\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "N/A"
    
    def extract_cases_alternative_method(self, soup):
        """Alternative method to extract cases"""
        cases = []
        
        try:
            # Look for case patterns in the entire page text
            import re
            page_text = soup.get_text()
            
            case_patterns = re.findall(r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/\d{4})', page_text)
            
            for case_no in case_patterns:
                case_data = {
                    "Case_No": case_no,
                    "Case_Title": "N/A",
                    "Status": "Pending",
                    "Institution_Date": "View Details",
                    "Disposal_Date": "N/A",
                    "Advocates": {"ASC": "N/A", "AOR": "N/A", "Prosecutor": "N/A"},
                    "Petition_Appeal_Memo": {"File": "N/A", "Type": "N/A"},
                    "History": [],
                    "Judgement_Order": {"File": "N/A", "Type": "N/A"}
                }
                cases.append(case_data)
        
        except Exception as e:
            print(f"⚠️ Alternative extraction error: {e}")
        
        return cases
    
    def extract_with_pagination(self, max_pages=5):
        """Extract data with pagination support"""
        all_cases = []
        current_page = 1
        
        while current_page <= max_pages:
            print(f"📄 Processing page {current_page}")
            
            # Extract cases from current page
            page_cases = self.extract_cases_from_page()
            
            if page_cases:
                all_cases.extend(page_cases)
                print(f"✅ Found {len(page_cases)} cases on page {current_page}")
            
            # Try to go to next page
            if not self.click_next_page(current_page + 1):
                print("📄 No more pages available")
                break
            
            current_page += 1
            time.sleep(2)
        
        return all_cases
    
    def click_next_page(self, page_num):
        """Click specific page number"""
        try:
            page_selectors = [
                f"//a[text()='{page_num}']",
                f"//a[normalize-space(text())='{page_num}']",
                f"//input[@value='{page_num}']"
            ]
            
            for selector in page_selectors:
                try:
                    page_link = self.driver.find_element(By.XPATH, selector)
                    if page_link and page_link.is_enabled() and page_link.is_displayed():
                        self.driver.execute_script("arguments[0].click();", page_link)
                        time.sleep(3)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error clicking page {page_num}: {e}")
            return False
    
    def run_comprehensive_extraction(self, max_strategies=None, max_pages_per_search=3):
        """Run comprehensive extraction for all years, registries, and case types"""
        
        if not self.setup_driver():
            return False
        
        try:
            strategy_count = 0
            total_strategies = len(self.registries) * len(self.case_types) * (self.end_year - self.start_year + 1)
            
            if max_strategies:
                total_strategies = min(total_strategies, max_strategies)
            
            print(f"\n🚀 Starting comprehensive extraction")
            print(f"📊 Total strategies to process: {total_strategies}")
            print("=" * 60)
            
            # Prioritize recent years first
            years = list(range(self.end_year, self.start_year - 1, -1))
            
            for year in years:
                for registry in self.registries:
                    for case_type in self.case_types:
                        
                        if max_strategies and strategy_count >= max_strategies:
                            print(f"⚠️ Reached maximum strategies limit: {max_strategies}")
                            break
                        
                        strategy_count += 1
                        print(f"\n📈 Strategy {strategy_count}/{total_strategies}")
                        
                        # Navigate to search page
                        if not self.navigate_to_search_page():
                            continue
                        
                        # Perform search
                        if self.perform_search(year, registry, case_type):
                            # Extract cases with pagination
                            strategy_cases = self.extract_with_pagination(max_pages_per_search)
                            
                            if strategy_cases:
                                self.extracted_cases.extend(strategy_cases)
                                self.total_extracted += len(strategy_cases)
                                print(f"✅ Strategy completed: {len(strategy_cases)} cases")
                            else:
                                print("⚠️ No cases found for this strategy")
                        
                        # Progress report
                        if strategy_count % 10 == 0:
                            self.print_progress_report(strategy_count, total_strategies)
                        
                        # Delay between strategies
                        time.sleep(3)
                        
                        if max_strategies and strategy_count >= max_strategies:
                            break
                    
                    if max_strategies and strategy_count >= max_strategies:
                        break
                
                if max_strategies and strategy_count >= max_strategies:
                    break
            
            print(f"\n🎯 Extraction completed!")
            print(f"📊 Total cases extracted: {self.total_extracted}")
            print(f"📈 Strategies processed: {strategy_count}")
            print(f"❌ Failed searches: {len(self.failed_searches)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Comprehensive extraction failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def print_progress_report(self, current, total):
        """Print progress report"""
        percentage = (current / total) * 100
        print(f"\n📊 PROGRESS REPORT")
        print(f"   Completed: {current}/{total} ({percentage:.1f}%)")
        print(f"   Cases extracted: {self.total_extracted}")
        print(f"   Failed searches: {len(self.failed_searches)}")
        print(f"   Average cases per strategy: {self.total_extracted/current if current > 0 else 0:.1f}")
    
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
        print(f"✅ Unique cases: {len(unique_cases)}")
    
    def save_results(self):
        """Save extraction results to JSON file"""
        try:
            # Remove duplicates
            self.remove_duplicates()
            
            # Save main JSON file
            output_file = os.path.join(self.output_dir, "SupremeCourt_CaseInfo.Json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.extracted_cases)} cases to {output_file}")
            
            # Save failed searches log
            if self.failed_searches:
                failed_file = os.path.join(self.output_dir, "failed_searches.json")
                with open(failed_file, 'w', encoding='utf-8') as f:
                    json.dump(self.failed_searches, f, indent=2, ensure_ascii=False)
                print(f"⚠️ Saved {len(self.failed_searches)} failed searches to {failed_file}")
            
            # Save extraction summary
            summary = {
                "extraction_date": datetime.now().isoformat(),
                "total_cases": len(self.extracted_cases),
                "total_strategies_attempted": len(self.registries) * len(self.case_types) * (self.end_year - self.start_year + 1),
                "failed_searches": len(self.failed_searches),
                "year_range": f"{self.start_year}-{self.end_year}",
                "registries": self.registries,
                "case_types": self.case_types
            }
            
            summary_file = os.path.join(self.output_dir, "extraction_summary.json")
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Saved extraction summary to {summary_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False
    
    def get_year_distribution(self):
        """Get distribution of cases by year"""
        year_counts = {}
        
        for case in self.extracted_cases:
            case_no = case.get("Case_No", "")
            if "/" in case_no:
                year = case_no.split("/")[-1]
                if year.isdigit():
                    year_counts[year] = year_counts.get(year, 0) + 1
        
        return dict(sorted(year_counts.items()))
    
    def print_final_summary(self):
        """Print final extraction summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"📊 Total cases extracted: {len(self.extracted_cases)}")
        print(f"📅 Year range: {self.start_year}-{self.end_year}")
        print(f"🏛️ Registries covered: {len(self.registries)}")
        print(f"📝 Case types covered: {len(self.case_types)}")
        print(f"❌ Failed searches: {len(self.failed_searches)}")
        
        # Year distribution
        year_dist = self.get_year_distribution()
        if year_dist:
            print(f"\n📈 Cases by year:")
            for year, count in year_dist.items():
                print(f"   {year}: {count} cases")
        
        print(f"\n📁 Output directory: {self.output_dir}")
        print("=" * 60)


def main():
    """Main function to run comprehensive extraction"""
    extractor = ComprehensiveSupremeCourtExtractor()
    
    # Run extraction with limits for testing
    # Remove max_strategies limit for full extraction
    success = extractor.run_comprehensive_extraction(
        max_strategies=50,  # Limit for testing - remove for full extraction
        max_pages_per_search=3
    )
    
    if success:
        extractor.save_results()
        extractor.print_final_summary()
    else:
        print("❌ Extraction failed")


if __name__ == "__main__":
    main()