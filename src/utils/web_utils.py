"""
Utility functions for web scraping and data processing
"""

import re
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from src.config import Config


def setup_chrome_driver():
    """Setup Chrome WebDriver with optimal settings"""
    options = Options()
    
    # Add all Chrome options from config
    for option in Config.CHROME_OPTIONS:
        options.add_argument(option)
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        print("✅ Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize Chrome WebDriver: {e}")
        return None


def safe_find_element(driver, by, value, timeout=None):
    """Safely find element with timeout"""
    timeout = timeout or Config.TIMEOUT
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"⚠️ Element not found: {by}={value}")
        return None


def safe_find_elements(driver, by, value, timeout=None):
    """Safely find multiple elements with timeout"""
    timeout = timeout or Config.TIMEOUT
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except TimeoutException:
        print(f"⚠️ Elements not found: {by}={value}")
        return []


def handle_alert(driver, timeout=5):
    """Handle JavaScript alerts"""
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = Alert(driver)
        alert_text = alert.text
        alert.accept()
        return alert_text
    except TimeoutException:
        return None


def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return "N/A"
    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', str(text).strip())
    return cleaned if cleaned else "N/A"


def extract_case_number(text):
    """Extract case number from text using regex patterns"""
    if not text:
        return "N/A"
    
    # Patterns for different case number formats
    patterns = [
        r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+[-/]\w*/\d{4})',  # C.A.123-L/2025
        r'([A-Z]\.[A-Z]\.(?:[A-Z]\.)?\d+/\d{4})',        # C.A.123/2025
        r'([A-Z]+\.\d+/\d{4})',                          # CRL.123/2025
        r'([A-Z]+\.[A-Z]+\.\d+/\d{4})'                   # C.M.A.123/2025
    ]
    
    for pattern in patterns:
        match = re.search(pattern, str(text))
        if match:
            return match.group(1)
    
    return clean_text(text)


def extract_year_from_case_number(case_no):
    """Extract year from case number"""
    if not case_no or case_no == "N/A":
        return None
    
    year_match = re.search(r'/(\d{4})', case_no)
    if year_match:
        return int(year_match.group(1))
    return None


def is_target_year_case(case_no, target_year=None):
    """Check if case belongs to target year"""
    target_year = target_year or Config.TARGET_YEAR
    extracted_year = extract_year_from_case_number(case_no)
    return extracted_year == target_year


def save_json(data, filepath, indent=2):
    """Save data to JSON file with proper formatting"""
    try:
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        print(f"✅ Saved {len(data) if isinstance(data, list) else 'data'} to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to save {filepath}: {e}")
        return False


def load_json(filepath):
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded data from {filepath}")
        return data
    except Exception as e:
        print(f"❌ Failed to load {filepath}: {e}")
        return None


def check_pagination(driver):
    """Check if pagination exists on current page"""
    pagination_selectors = [
        # Numbered pagination links
        "//a[contains(@href, 'Page$') and text()!='' and string-length(text()) <= 3]",
        "//a[contains(text(), '2')]",
        "//a[contains(text(), '3')]",
        "//a[contains(text(), '4')]",
        "//a[contains(text(), '5')]",
        # Traditional next buttons
        "//a[contains(text(), 'Next')]",
        "//a[contains(text(), '>>')]", 
        "//a[contains(text(), 'next')]",
        "//input[@value='Next']",
        "//button[contains(text(), 'Next')]",
        # CSS selectors for pagination
        ".pagination a",
        ".pager a",
        # Numbered links pattern
        "a[href*='Page']"
    ]
    
    for selector in pagination_selectors:
        try:
            if selector.startswith("//"):
                elements = driver.find_elements(By.XPATH, selector)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            if elements:
                print(f"✅ Found pagination elements: {len(elements)} ({selector})")
                return elements
        except:
            continue
    
    print("⚠️ No pagination found")
    return []


def get_current_page_number(driver):
    """Get current page number from pagination"""
    try:
        # Look for active/current page indicators
        current_selectors = [
            "//span[contains(@class, 'current')]",
            "//a[contains(@class, 'current')]",
            "//span[contains(@class, 'active')]",
            "//a[contains(@class, 'active')]",
            "//span[contains(@style, 'font-weight:bold')]"
        ]
        
        for selector in current_selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element and element.text.isdigit():
                    return int(element.text)
            except:
                continue
        
        # Default to page 1 if not found
        return 1
    except:
        return 1


def click_next_page(driver, current_page=None):
    """Click next page button or numbered pagination"""
    try:
        # Try numbered pagination first
        if current_page is None:
            current_page = get_current_page_number(driver)
        
        next_page = current_page + 1
        
        print(f"🔄 Looking for page {next_page} (current: {current_page})")
        
        # Try to find numbered pagination for next page
        numbered_selectors = [
            f"//a[text()='{next_page}']",
            f"//a[normalize-space(text())='{next_page}']",
            f"//a[contains(@href, 'Page${next_page}')]",
            f"//input[@value='{next_page}']"
        ]
        
        for selector in numbered_selectors:
            try:
                next_page_link = driver.find_element(By.XPATH, selector)
                if next_page_link and next_page_link.is_enabled() and next_page_link.is_displayed():
                    print(f"🔄 Clicking page {next_page}")
                    driver.execute_script("arguments[0].click();", next_page_link)
                    time.sleep(Config.DELAY_BETWEEN_PAGES)
                    return True
            except Exception as e:
                continue
        
        # Fallback to traditional "Next" buttons
        next_button_selectors = [
            "//a[contains(text(), 'Next')]",
            "//a[contains(text(), '>>')]", 
            "//a[contains(text(), 'next')]",
            "//input[@value='Next']",
            "//button[contains(text(), 'Next')]"
        ]
        
        for selector in next_button_selectors:
            try:
                next_button = driver.find_element(By.XPATH, selector)
                if next_button and next_button.is_enabled() and next_button.is_displayed():
                    print(f"🔄 Clicking next page button: {next_button.text}")
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(Config.DELAY_BETWEEN_PAGES)
                    return True
            except Exception as e:
                continue
        
        print("⚠️ No clickable next page button found")
        return False
        
    except Exception as e:
        print(f"❌ Error in pagination: {e}")
        return False


def wait_for_page_load(driver, timeout=None):
    """Wait for page to load completely"""
    timeout = timeout or Config.TIMEOUT
    
    try:
        # Wait for page to be in ready state
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)  # Additional wait for dynamic content
        return True
    except TimeoutException:
        print("⚠️ Page load timeout")
        return False


def get_page_source_soup(driver):
    """Get BeautifulSoup object from current page"""
    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except Exception as e:
        print(f"❌ Failed to parse page source: {e}")
        return None


def filter_2025_cases(cases):
    """Filter cases to only include 2025 cases"""
    filtered_cases = []
    
    for case in cases:
        case_no = case.get('Case_No', '')
        if is_target_year_case(case_no, Config.TARGET_YEAR):
            filtered_cases.append(case)
        else:
            print(f"⚠️ Filtering out non-2025 case: {case_no}")
    
    print(f"✅ Filtered {len(filtered_cases)} cases from {len(cases)} total cases")
    return filtered_cases


def log_extraction_progress(current_page, total_cases, case_type=None, registry=None):
    """Log extraction progress"""
    message = f"📊 Page {current_page}: {total_cases} cases extracted"
    if case_type:
        message += f" | Type: {case_type}"
    if registry:
        message += f" | Registry: {registry}"
    print(message)