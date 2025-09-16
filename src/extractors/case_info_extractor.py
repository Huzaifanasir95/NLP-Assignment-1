"""
Case Information Extractor for Supreme Court of Pakistan
Extracts case information with pagination support for 2025 data
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from src.extractors.base_extractor import BaseExtractor
from src.utils.web_utils import (
    safe_find_element, safe_find_elements, clean_text, 
    extract_case_number, get_page_source_soup
)
from src.config import Config


class CaseInfoExtractor(BaseExtractor):
    """Extract case information from Supreme Court website"""
    
    def __init__(self):
        super().__init__()
        self.url = Config.CASE_INFO_URL
        # Generate comprehensive strategies for all years and combinations
        Config.generate_comprehensive_strategies()
        self.search_strategies = Config.COMPREHENSIVE_STRATEGIES
        print(f"🎯 Initialized with {len(self.search_strategies)} search strategies")
    
    def extract_data(self):
        """Extract case information data with multiple search strategies"""
        all_cases = []
        
        for strategy in self.search_strategies:
            print(f"\n🔍 Searching: {strategy}")
            
            if not self.navigate_to_url(self.url):
                continue
            
            if self.perform_search(strategy):
                # Extract cases from current search with pagination
                strategy_cases = self.extract_with_pagination(
                    self.extract_cases_from_page, 
                    Config.MAX_PAGES_PER_SEARCH
                )
                
                if strategy_cases:
                    all_cases.extend(strategy_cases)
                    print(f"✅ Found {len(strategy_cases)} cases for {strategy}")
                else:
                    print(f"⚠️ No cases found for {strategy}")
            
            # Reset for next strategy
            self.extracted_data = []
            self.current_page = 1
            
            # Delay between different searches
            time.sleep(Config.DELAY_BETWEEN_SEARCHES)
        
        self.extracted_data = all_cases
        return len(all_cases) > 0
    
    def perform_search(self, strategy):
        """Perform search with given strategy using correct element IDs"""
        try:
            # Wait for page to load
            time.sleep(3)
            
            # Fill case type using correct ID
            case_type = strategy.get("case_type")
            if case_type:
                case_type_select = safe_find_element(self.driver, By.ID, "ddlCaseType")
                if case_type_select:
                    select = Select(case_type_select)
                    try:
                        select.select_by_visible_text(case_type)
                        print(f"✅ Selected case type: {case_type}")
                        time.sleep(1)
                    except:
                        print(f"⚠️ Case type '{case_type}' not found, trying alternatives...")
                        # Try partial match
                        for option in select.options:
                            if case_type.lower() in option.text.lower():
                                select.select_by_visible_text(option.text)
                                print(f"✅ Selected alternative: {option.text}")
                                break
            
            # Fill registry using correct ID
            registry = strategy.get("registry")
            if registry:
                registry_select = safe_find_element(self.driver, By.ID, "ddlRegistry")
                if registry_select:
                    select = Select(registry_select)
                    try:
                        select.select_by_visible_text(registry)
                        print(f"✅ Selected registry: {registry}")
                        time.sleep(1)
                    except:
                        print(f"⚠️ Registry '{registry}' not found")
            
            # Fill year using correct ID
            year = strategy.get("year", Config.TARGET_YEAR)
            year_select = safe_find_element(self.driver, By.ID, "ddlYear")
            if year_select:
                select = Select(year_select)
                try:
                    select.select_by_visible_text(str(year))
                    print(f"✅ Selected year: {year}")
                    time.sleep(1)
                except:
                    print(f"⚠️ Year {year} not found in dropdown")
                    return False
            
            # Submit search using correct button ID
            search_button = safe_find_element(self.driver, By.ID, "btnSearch")
            if search_button:
                print("🔍 Clicking search button...")
                search_button.click()
                
                # Wait for results
                time.sleep(5)
                
                # Check for alerts or errors
                from src.utils.web_utils import handle_alert
                alert_text = handle_alert(self.driver)
                if alert_text:
                    print(f"⚠️ Search alert: {alert_text}")
                
                return True
            else:
                print("❌ Search button not found")
                return False
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def extract_cases_from_page(self):
        """Extract cases from current page"""
        cases = []
        
        try:
            # Get page source
            soup = get_page_source_soup(self.driver)
            if not soup:
                return cases
            
            # Look for case data in tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:  # Minimum expected columns
                        case_data = self.extract_case_from_row(cells)
                        if case_data and case_data.get('Case_No') != "N/A":
                            # Accept all cases, let the calling code handle year filtering
                            cases.append(case_data)
            
            # Also try alternative extraction methods
            if not cases:
                cases = self.extract_cases_alternative_method(soup)
            
            print(f"📋 Extracted {len(cases)} cases from current page")
            return cases
            
        except Exception as e:
            print(f"❌ Error extracting cases from page: {e}")
            return cases
    
    def extract_case_from_row(self, cells):
        """Extract case information from table row with complete structure"""
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
            
            # Extract based on common patterns
            for i, cell in enumerate(cells):
                cell_text = clean_text(cell.get_text())
                
                # Case number is usually in first few columns
                if i == 0 or (i <= 2 and any(char.isdigit() for char in cell_text)):
                    potential_case_no = extract_case_number(cell_text)
                    if potential_case_no != "N/A":
                        case_data["Case_No"] = potential_case_no
                
                # Case title is usually the longest text
                elif len(cell_text) > 20 and any(keyword in cell_text.lower() for keyword in ['vs', 'v.', 'versus']):
                    case_data["Case_Title"] = cell_text[:200]  # Limit length
                
                # Status keywords
                elif any(keyword in cell_text.lower() for keyword in ['pending', 'decided', 'dismissed', 'allowed', 'disposed']):
                    case_data["Status"] = cell_text
                
                # Date patterns
                elif any(keyword in cell_text.lower() for keyword in ['date', 'view details']):
                    case_data["Institution_Date"] = cell_text
                
                # Check for advocate information in cells
                elif any(keyword in cell_text.lower() for keyword in ['advocate', 'counsel', 'lawyer']):
                    # Try to parse advocate info
                    if 'asc' in cell_text.lower():
                        case_data["Advocates"]["ASC"] = cell_text
                    elif 'aor' in cell_text.lower():
                        case_data["Advocates"]["AOR"] = cell_text
                    elif 'prosecutor' in cell_text.lower():
                        case_data["Advocates"]["Prosecutor"] = cell_text
                
                # Check for file links
                elif 'pdf' in cell_text.lower() or 'file' in cell_text.lower():
                    # Check if it's a judgment or memo
                    if any(keyword in cell_text.lower() for keyword in ['judgment', 'order']):
                        case_data["Judgement_Order"]["File"] = cell_text
                    elif any(keyword in cell_text.lower() for keyword in ['petition', 'memo', 'appeal']):
                        case_data["Petition_Appeal_Memo"]["File"] = cell_text
            
            # Validate that we have meaningful data
            if case_data["Case_No"] != "N/A":
                return case_data
            
        except Exception as e:
            print(f"⚠️ Error extracting case from row: {e}")
        
        return None
    
    def extract_cases_alternative_method(self, soup):
        """Alternative extraction method for different page layouts"""
        cases = []
        
        try:
            # Look for divs with case information
            case_divs = soup.find_all('div', class_=['case-info', 'case-item', 'result-item'])
            
            for div in case_divs:
                case_text = clean_text(div.get_text())
                
                # Extract case number
                case_no = extract_case_number(case_text)
                
                if case_no != "N/A" and str(Config.TARGET_YEAR) in case_no:
                    case_data = {
                        "Case_No": case_no,
                        "Case_Title": case_text[:200] if len(case_text) > 20 else "N/A",
                        "Status": "Pending",  # Default status
                        "Institution_Date": "View Details"
                    }
                    cases.append(case_data)
            
            # Also try looking for specific patterns in the HTML
            if not cases:
                all_text = soup.get_text()
                case_patterns = re.findall(r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/2025)', all_text)
                
                for pattern in case_patterns:
                    case_data = {
                        "Case_No": pattern,
                        "Case_Title": "N/A",
                        "Status": "Pending",
                        "Institution_Date": "View Details"
                    }
                    cases.append(case_data)
        
        except Exception as e:
            print(f"⚠️ Alternative extraction error: {e}")
        
        return cases