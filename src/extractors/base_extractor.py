"""
Base extractor class for Supreme Court data extraction
"""

import time
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.utils.web_utils import (
    setup_chrome_driver, safe_find_element, safe_find_elements,
    handle_alert, wait_for_page_load, click_next_page, save_json,
    filter_2025_cases, log_extraction_progress, get_current_page_number
)
from src.config import Config


class BaseExtractor(ABC):
    """Base class for all Supreme Court data extractors"""
    
    def __init__(self):
        self.driver = None
        self.extracted_data = []
        self.current_page = 1
        self.total_extracted = 0
    
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        self.driver = setup_chrome_driver()
        return self.driver is not None
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ WebDriver closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing WebDriver: {e}")
    
    @abstractmethod
    def extract_data(self):
        """Abstract method to extract data - must be implemented by subclasses"""
        pass
    
    def navigate_to_url(self, url):
        """Navigate to URL with error handling"""
        try:
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            wait_for_page_load(self.driver)
            return True
        except Exception as e:
            print(f"❌ Failed to navigate to {url}: {e}")
            return False
    
    def fill_form_field(self, field_id, value, field_type="input"):
        """Fill form field with error handling"""
        try:
            if field_type == "select":
                select_element = safe_find_element(self.driver, By.ID, field_id)
                if select_element:
                    select = Select(select_element)
                    select.select_by_visible_text(value)
                    print(f"✅ Selected '{value}' in field {field_id}")
                    return True
            else:
                field = safe_find_element(self.driver, By.ID, field_id)
                if field:
                    field.clear()
                    field.send_keys(value)
                    print(f"✅ Filled field {field_id} with '{value}'")
                    return True
            
            print(f"❌ Field {field_id} not found")
            return False
        except Exception as e:
            print(f"❌ Error filling field {field_id}: {e}")
            return False
    
    def submit_form(self, button_id=None, button_text=None):
        """Submit form with error handling"""
        try:
            if button_id:
                button = safe_find_element(self.driver, By.ID, button_id)
            elif button_text:
                button = safe_find_element(self.driver, By.XPATH, f"//input[@value='{button_text}']")
            else:
                # Try common submit button patterns
                button = safe_find_element(self.driver, By.XPATH, "//input[@type='submit']")
            
            if button:
                print(f"🔍 Submitting form...")
                button.click()
                
                # Handle any alerts
                alert_text = handle_alert(self.driver)
                if alert_text:
                    print(f"⚠️ Alert handled: {alert_text}")
                
                wait_for_page_load(self.driver)
                return True
            else:
                print("❌ Submit button not found")
                return False
                
        except Exception as e:
            print(f"❌ Error submitting form: {e}")
            return False
    
    def extract_with_pagination(self, extraction_function, max_pages=None):
        """Extract data with pagination support"""
        max_pages = max_pages or Config.MAX_PAGES_PER_SEARCH
        page_count = 0
        
        while page_count < max_pages:
            try:
                # Get current page number from pagination
                current_page_num = get_current_page_number(self.driver)
                print(f"\n📄 Processing page {current_page_num} (iteration {self.current_page})")
                
                # Extract data from current page
                page_data = extraction_function()
                
                if page_data:
                    # Filter for 2025 cases only
                    filtered_data = filter_2025_cases(page_data)
                    self.extracted_data.extend(filtered_data)
                    self.total_extracted += len(filtered_data)
                    
                    log_extraction_progress(current_page_num, len(filtered_data))
                else:
                    print("⚠️ No data extracted from current page")
                
                # Try to go to next page
                if not click_next_page(self.driver, current_page_num):
                    print("✅ No more pages available or reached end")
                    break
                
                # Wait for new page to load
                wait_for_page_load(self.driver)
                
                self.current_page += 1
                page_count += 1
                
                # Add delay between pages
                time.sleep(Config.DELAY_BETWEEN_PAGES)
                
            except Exception as e:
                print(f"❌ Error on page {self.current_page}: {e}")
                break
        
        print(f"\n🎯 Total extraction complete: {self.total_extracted} cases from {page_count + 1} pages")
        return self.extracted_data
    
    def save_data(self, filename=None, data_type="case_info"):
        """Save extracted data to JSON file"""
        if not self.extracted_data:
            print("⚠️ No data to save")
            return False
        
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{data_type}_{Config.TARGET_YEAR}_{timestamp}.json"
        
        filepath = Config.get_output_path(data_type, filename)
        return save_json(self.extracted_data, filepath)
    
    def get_extraction_summary(self):
        """Get summary of extraction results"""
        total_cases = len(self.extracted_data)
        year_2025_cases = len([case for case in self.extracted_data 
                              if case.get('Case_No', '').endswith(f"/{Config.TARGET_YEAR}")])
        
        summary = {
            "total_cases_extracted": total_cases,
            "year_2025_cases": year_2025_cases,
            "pages_processed": self.current_page,
            "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary
    
    def run_extraction(self):
        """Main extraction workflow"""
        try:
            print(f"🚀 Starting {self.__class__.__name__} extraction for {Config.TARGET_YEAR}")
            
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Run extraction
            result = self.extract_data()
            
            # Save results
            if self.extracted_data:
                self.save_data()
                
                # Print summary
                summary = self.get_extraction_summary()
                print("\n📊 Extraction Summary:")
                for key, value in summary.items():
                    print(f"   {key}: {value}")
            
            return result
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        finally:
            self.cleanup()