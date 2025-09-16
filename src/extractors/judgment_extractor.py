"""
Judgment Extractor for Supreme Court of Pakistan
Extracts judgment information with pagination support for 2025 data
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


class JudgmentExtractor(BaseExtractor):
    """Extract judgment information from Supreme Court website"""
    
    def __init__(self):
        super().__init__()
        self.url = Config.JUDGMENT_URL
        self.search_strategies = [
            {"year": Config.TARGET_YEAR, "month": "January"},
            {"year": Config.TARGET_YEAR, "month": "February"},
            {"year": Config.TARGET_YEAR, "month": "March"},
            {"year": Config.TARGET_YEAR, "month": "April"},
            {"year": Config.TARGET_YEAR, "month": "May"},
            {"year": Config.TARGET_YEAR, "month": "June"},
            {"year": Config.TARGET_YEAR, "month": "July"},
            {"year": Config.TARGET_YEAR, "month": "August"},
            {"year": Config.TARGET_YEAR, "month": "September"},
            {"year": Config.TARGET_YEAR, "month": "October"},
            {"year": Config.TARGET_YEAR, "month": "November"},
            {"year": Config.TARGET_YEAR, "month": "December"}
        ]
    
    def extract_data(self):
        """Extract judgment data with multiple search strategies"""
        all_judgments = []
        
        for strategy in self.search_strategies:
            print(f"\n🔍 Searching judgments: {strategy}")
            
            if not self.navigate_to_url(self.url):
                continue
            
            if self.perform_search(strategy):
                # Extract judgments from current search with pagination
                strategy_judgments = self.extract_with_pagination(
                    self.extract_judgments_from_page, 
                    Config.MAX_PAGES_PER_SEARCH
                )
                
                if strategy_judgments:
                    all_judgments.extend(strategy_judgments)
                    print(f"✅ Found {len(strategy_judgments)} judgments for {strategy}")
                else:
                    print(f"⚠️ No judgments found for {strategy}")
            
            # Reset for next strategy
            self.extracted_data = []
            self.current_page = 1
            
            # Delay between different searches
            time.sleep(Config.DELAY_BETWEEN_SEARCHES)
        
        self.extracted_data = all_judgments
        return len(all_judgments) > 0
    
    def perform_search(self, strategy):
        """Perform judgment search with given strategy"""
        try:
            # Wait for page to load
            time.sleep(3)
            
            # Fill year
            year = strategy.get("year", Config.TARGET_YEAR)
            year_select = safe_find_element(self.driver, By.NAME, "year")
            if not year_select:
                year_select = safe_find_element(self.driver, By.ID, "year")
            
            if year_select:
                select = Select(year_select)
                try:
                    select.select_by_visible_text(str(year))
                    print(f"✅ Selected year: {year}")
                    time.sleep(1)
                except:
                    try:
                        select.select_by_value(str(year))
                        print(f"✅ Selected year by value: {year}")
                    except:
                        print(f"⚠️ Year {year} not found in dropdown")
                        return False
            
            # Fill month if available
            month = strategy.get("month")
            if month:
                month_select = safe_find_element(self.driver, By.NAME, "month")
                if not month_select:
                    month_select = safe_find_element(self.driver, By.ID, "month")
                
                if month_select:
                    select = Select(month_select)
                    try:
                        select.select_by_visible_text(month)
                        print(f"✅ Selected month: {month}")
                        time.sleep(1)
                    except:
                        print(f"⚠️ Month '{month}' not found")
            
            # Submit search
            search_button = safe_find_element(self.driver, By.XPATH, "//input[@type='submit']")
            if not search_button:
                search_button = safe_find_element(self.driver, By.XPATH, "//button[contains(text(), 'Search')]")
            
            if search_button:
                print("🔍 Clicking search button...")
                search_button.click()
                
                # Wait for results
                time.sleep(5)
                return True
            else:
                print("❌ Search button not found")
                return False
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def extract_judgments_from_page(self):
        """Extract judgments from current page"""
        judgments = []
        
        try:
            # Get page source
            soup = get_page_source_soup(self.driver)
            if not soup:
                return judgments
            
            # Look for judgment data in tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:  # Minimum expected columns
                        judgment_data = self.extract_judgment_from_row(cells)
                        if judgment_data and judgment_data.get('Case_No') != "N/A":
                            # Only include 2025 judgments
                            if str(Config.TARGET_YEAR) in judgment_data.get('Case_No', ''):
                                judgments.append(judgment_data)
            
            # Also try alternative extraction methods
            if not judgments:
                judgments = self.extract_judgments_alternative_method(soup)
            
            print(f"📋 Extracted {len(judgments)} judgments from current page")
            return judgments
            
        except Exception as e:
            print(f"❌ Error extracting judgments from page: {e}")
            return judgments
    
    def extract_judgment_from_row(self, cells):
        """Extract judgment information from table row"""
        try:
            judgment_data = {
                "Case_No": "N/A",
                "Parties": "N/A",
                "Judgment_Date": "N/A",
                "PDF_Link": "N/A",
                "Judge": "N/A"
            }
            
            # Extract based on common patterns
            for i, cell in enumerate(cells):
                cell_text = clean_text(cell.get_text())
                
                # Case number is usually in first column
                if i == 0 or (i <= 2 and any(char.isdigit() for char in cell_text)):
                    potential_case_no = extract_case_number(cell_text)
                    if potential_case_no != "N/A" and str(Config.TARGET_YEAR) in potential_case_no:
                        judgment_data["Case_No"] = potential_case_no
                
                # Parties (usually contains "vs" or "v/s")
                elif "vs" in cell_text.lower() or "v/s" in cell_text.lower():
                    judgment_data["Parties"] = cell_text[:200]  # Limit length
                
                # Date patterns
                elif re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', cell_text):
                    judgment_data["Judgment_Date"] = cell_text
                
                # PDF link
                elif cell.find('a'):
                    link = cell.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        if href.endswith('.pdf') or 'pdf' in href.lower():
                            judgment_data["PDF_Link"] = href
                
                # Judge name (usually contains "J." or "Justice")
                elif "j." in cell_text.lower() or "justice" in cell_text.lower():
                    judgment_data["Judge"] = cell_text
            
            # Validate that we have meaningful data
            if judgment_data["Case_No"] != "N/A" and str(Config.TARGET_YEAR) in judgment_data["Case_No"]:
                return judgment_data
            
        except Exception as e:
            print(f"⚠️ Error extracting judgment from row: {e}")
        
        return None
    
    def extract_judgments_alternative_method(self, soup):
        """Alternative extraction method for different page layouts"""
        judgments = []
        
        try:
            # Look for divs with judgment information
            judgment_divs = soup.find_all('div', class_=['judgment-info', 'judgment-item', 'result-item'])
            
            for div in judgment_divs:
                judgment_text = clean_text(div.get_text())
                
                # Extract case number
                case_no = extract_case_number(judgment_text)
                
                if case_no != "N/A" and str(Config.TARGET_YEAR) in case_no:
                    # Try to extract parties
                    parties = "N/A"
                    if "vs" in judgment_text.lower():
                        parts = judgment_text.split("vs")
                        if len(parts) >= 2:
                            parties = f"{parts[0].strip()} vs {parts[1].strip()}"[:200]
                    
                    # Extract date
                    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', judgment_text)
                    judgment_date = date_match.group(1) if date_match else "N/A"
                    
                    # Look for PDF link
                    pdf_link = "N/A"
                    link = div.find('a')
                    if link and link.get('href'):
                        href = link.get('href')
                        if href.endswith('.pdf') or 'pdf' in href.lower():
                            pdf_link = href
                    
                    judgment_data = {
                        "Case_No": case_no,
                        "Parties": parties,
                        "Judgment_Date": judgment_date,
                        "PDF_Link": pdf_link,
                        "Judge": "N/A"
                    }
                    judgments.append(judgment_data)
            
            # Also try looking for specific patterns in the HTML
            if not judgments:
                all_text = soup.get_text()
                case_patterns = re.findall(r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/2025)', all_text)
                
                for pattern in case_patterns:
                    judgment_data = {
                        "Case_No": pattern,
                        "Parties": "N/A",
                        "Judgment_Date": "N/A",
                        "PDF_Link": "N/A",
                        "Judge": "N/A"
                    }
                    judgments.append(judgment_data)
        
        except Exception as e:
            print(f"⚠️ Alternative extraction error: {e}")
        
        return judgments