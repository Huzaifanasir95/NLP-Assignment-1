"""
Interactive Crl.A. (Criminal Appeals) Lahore Extractor
Based on proven paginated multi-browser technique
Allows user to select specific year ranges for extraction
"""

import time
import re
import json
import os
import requests
import urllib3
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CrlALahoreInteractiveExtractor:
    """Interactive extractor for Crl.Sha.A. Lahore cases with user-selectable year ranges"""
    
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.extracted_cases = []
        self.base_url = "https://scp.gov.pk"
        self.results_lock = threading.Lock()
        self.active_json_files = {}  # Track open JSON files for incremental writing
        
        # Configuration for Crl.A. cases
        self.case_type_value = "9"
        self.case_type_text = "Crl.Sh.P."
    
        # Available year ranges (5-year gaps)
        self.year_ranges = {
            "1": {"name": "1980-1984", "years": [1980, 1981, 1982, 1983, 1984]},
            "2": {"name": "1985-1989", "years": [1985, 1986, 1987, 1988, 1989]},
            "3": {"name": "1990-1994", "years": [1990, 1991, 1992, 1993, 1994]},
            "4": {"name": "1995-1999", "years": [1995, 1996, 1997, 1998, 1999]},
            "5": {"name": "2000-2004", "years": [2000, 2001, 2002, 2003, 2004]},
            "6": {"name": "2005-2009", "years": [2005, 2006, 2007, 2008, 2009]},
            "7": {"name": "2010-2014", "years": [2010, 2011, 2012, 2013, 2014]},
            "8": {"name": "2015-2019", "years": [2015, 2016, 2017, 2018, 2019]},
            "9": {"name": "2020-2024", "years": [2020, 2021, 2022, 2023, 2024]},
            "10": {"name": "2025", "years": [2025]}
        }
        
        print(f"✅ Crl.Sha.A. Lahore Interactive Extractor initialized")
        print(f"   Case Type: {self.case_type_text} (Value: {self.case_type_value})")
        print(f"   Max Workers: {self.max_workers}")
        print(f"   Browser: Edge WebDriver (Enhanced Stability)")
    
    def create_optimized_driver(self, headless=False, max_retries=3):
        """Create optimized Edge WebDriver with enhanced stability"""
        for attempt in range(max_retries):
            try:
                # Edge options for stability and performance
                options = EdgeOptions()
                
                if headless:
                    options.add_argument('--headless')
                
                # Core stability options for Edge (Chromium-based)
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-plugins')
                options.add_argument('--disable-images')
                options.add_argument('--disable-web-security')
                options.add_argument('--allow-running-insecure-content')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--disable-logging')
                options.add_argument('--disable-default-apps')
                options.add_argument('--disable-sync')
                options.add_argument('--disable-translate')
                options.add_argument('--hide-scrollbars')
                options.add_argument('--mute-audio')
                options.add_argument('--no-first-run')
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-features=TranslateUI')
                options.add_argument('--disable-blink-features=AutomationControlled')
                
                # Enhanced crash prevention for Edge
                options.add_argument('--disable-crash-reporter')
                options.add_argument('--disable-hang-monitor')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                options.add_argument('--disable-background-timer-throttling')
                options.add_argument('--disable-renderer-backgrounding')
                options.add_argument('--disable-backgrounding-occluded-windows')
                options.add_argument('--disable-client-side-phishing-detection')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--disable-prompt-on-repost')
                options.add_argument('--disable-ipc-flooding-protection')
                
                # Memory optimizations
                options.add_argument('--memory-pressure-off')
                options.add_argument('--max_old_space_size=2048')
                options.add_argument('--aggressive-cache-discard')
                options.add_argument('--disable-background-networking')
                
                # Process isolation and resource limits
                options.add_argument('--max-webgl-contexts=1')
                options.add_argument('--disable-webgl')
                options.add_argument('--disable-3d-apis')
                options.add_argument('--disable-accelerated-2d-canvas')
                
                # Page load strategy for faster loading
                options.page_load_strategy = 'eager'
                
                # Edge-specific prefs to disable resources
                prefs = {
                    "profile.managed_default_content_settings.images": 2,
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.default_content_settings.popups": 0,
                    "profile.managed_default_content_settings.media_stream": 2,
                    "profile.default_content_setting_values.plugins": 2,
                    "profile.content_settings.plugin_whitelist.adobe-flash-player": 2,
                    "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 2
                }
                options.add_experimental_option("prefs", prefs)
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Create Edge driver
                driver = webdriver.Edge(options=options)
                
                # Enhanced timeout settings
                driver.set_page_load_timeout(20)
                driver.implicitly_wait(3)
                
                print(f"✅ Edge driver created successfully (attempt {attempt + 1})")
                return driver
                
            except Exception as e:
                print(f"❌ Edge driver creation failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"🔄 Retrying Edge driver creation in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ All Edge driver creation attempts failed")
                    return None
        
        return None

    def initialize_json_file(self, range_name):
        """Initialize JSON file for incremental writing with append mode support"""
        try:
            range_dir = range_name.replace('-', '_')
            os.makedirs(range_dir, exist_ok=True)
            
            filename = os.path.join(range_dir, f"CrlA_Lahore_{range_name.replace('-', '_')}_complete.json")
            
            existing_cases = set()
            case_count = 0
            
            # Check if file exists and read existing cases
            if os.path.exists(filename):
                print(f"📖 Found existing JSON file: {filename}")
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        
                    if content and content != '[]':
                        # Parse existing JSON to get case numbers
                        if content.startswith('[') and content.endswith(']'):
                            # Remove trailing ] to prepare for appending
                            content = content.rstrip(']').rstrip()
                            
                            # Parse the JSON to extract existing case numbers
                            try:
                                existing_data = json.loads(content + ']')
                                for case in existing_data:
                                    if isinstance(case, dict) and case.get("Case_No"):
                                        existing_cases.add(case["Case_No"])
                                        case_count += 1
                                
                                print(f"📊 Found {case_count} existing cases, will append new ones")
                                
                                # Rewrite file without closing bracket for appending
                                with open(filename, 'w', encoding='utf-8') as f:
                                    if case_count > 0:
                                        # Write existing content without closing bracket
                                        f.write(content.rstrip(']').rstrip())
                                    else:
                                        f.write('[\n')
                                        
                            except json.JSONDecodeError as je:
                                print(f"⚠️ JSON parsing error, treating as new file: {je}")
                                # Start fresh if JSON is corrupted
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write('[\n')
                                existing_cases = set()
                                case_count = 0
                        else:
                            # File exists but not proper JSON array, start fresh
                            print(f"⚠️ Existing file not proper JSON array, starting fresh")
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write('[\n')
                            existing_cases = set()
                            case_count = 0
                    else:
                        # Empty file or just empty array, start fresh
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write('[\n')
                        existing_cases = set()
                        case_count = 0
                        
                except Exception as e:
                    print(f"⚠️ Error reading existing file, starting fresh: {e}")
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write('[\n')
                    existing_cases = set()
                    case_count = 0
            else:
                # New file, initialize with empty array
                print(f"📝 Creating new JSON file: {filename}")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('[\n')
            
            # Track the file state
            with self.results_lock:
                self.active_json_files[range_name] = {
                    'filename': filename,
                    'case_count': case_count,
                    'seen_cases': existing_cases
                }
            
            print(f"✅ JSON file ready: {filename} (existing cases: {case_count})")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to initialize JSON file for {range_name}: {e}")
            return None
    
    def write_case_incrementally(self, case_data, range_name):
        """Write a single case to JSON file incrementally with duplicate prevention"""
        try:
            if not case_data or not case_data.get("Case_No") or case_data.get("Case_No") == "N/A":
                return False
            
            case_no = case_data["Case_No"]
            
            with self.results_lock:
                if range_name not in self.active_json_files:
                    print(f"❌ JSON file not initialized for range {range_name}")
                    return False
                
                file_info = self.active_json_files[range_name]
                
                # Check for duplicates
                if case_no in file_info['seen_cases']:
                    print(f"⚠️ Duplicate case skipped: {case_no} (already exists)")
                    return False
                
                file_info['seen_cases'].add(case_no)
                filename = file_info['filename']
                
                # Append case to JSON file
                with open(filename, 'a', encoding='utf-8') as f:
                    if file_info['case_count'] > 0:
                        f.write(',\n')
                    
                    json.dump(case_data, f, indent=2, ensure_ascii=False)
                
                file_info['case_count'] += 1
                
                print(f"💾 NEW case {case_no} written to {filename} (total: {file_info['case_count']})")
                return True
                
        except Exception as e:
            print(f"❌ Failed to write case {case_data.get('Case_No', 'Unknown')}: {e}")
            return False
    
    def finalize_json_file(self, range_name):
        """Finalize JSON file by closing the array and creating summary (append mode aware)"""
        try:
            with self.results_lock:
                if range_name not in self.active_json_files:
                    return False
                
                file_info = self.active_json_files[range_name]
                filename = file_info['filename']
                case_count = file_info['case_count']
                
                # Close the JSON array
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write('\n]')
                
                print(f"✅ Finalized {filename} with {case_count} total cases (including any existing ones)")
                
                # Create/update summary file
                if case_count > 0:
                    range_dir = os.path.dirname(filename)
                    summary = {
                        "case_type": self.case_type_text,
                        "year_range": range_name,
                        "total_cases": case_count,
                        "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "pdf_directory": os.path.join(range_dir, "pdfs"),
                        "mode": "append_mode_with_duplicate_prevention"
                    }
                    
                    summary_file = os.path.join(range_dir, f"CrlA_Lahore_{range_name.replace('-', '_')}_summary.json")
                    with open(summary_file, 'w', encoding='utf-8') as f:
                        json.dump(summary, f, indent=2, ensure_ascii=False)
                    
                    print(f"📊 Summary updated: {summary_file}")
                
                # Clean up tracking
                del self.active_json_files[range_name]
                return True
                
        except Exception as e:
            print(f"❌ Failed to finalize JSON file for {range_name}: {e}")
            return False

    def navigate_and_search(self, driver, worker_id, year):
        """Navigate and search for specific year (proven technique) with enhanced timeout handling"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Worker {worker_id}: Navigating for year {year}")
            
            # Use longer timeout for initial page load
            driver.set_page_load_timeout(30)
            driver.get(url)
            time.sleep(5)  # Increased wait time
            
            # Wait for page to load with longer timeout
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "ddlCaseType"))
            )
            print(f"✅ Worker {worker_id}: Page loaded successfully for year {year}")
            
            # Select case type: C.P.L.A.
            case_type_select = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'ddlCaseType'))
            )
            select = Select(case_type_select)
            select.select_by_value(self.case_type_value)
            time.sleep(2)  # Increased wait time
            print(f"✅ Worker {worker_id}: Case type selected for year {year}")
            
            # Select registry: Lahore
            registry_select = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
            )
            select = Select(registry_select)
            select.select_by_value('L')
            time.sleep(2)  # Increased wait time
            print(f"✅ Worker {worker_id}: Registry selected for year {year}")
            
            # Select year
            year_select = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'ddlYear'))
            )
            select = Select(year_select)
            select.select_by_value(str(year))
            time.sleep(2)  # Increased wait time
            print(f"✅ Worker {worker_id}: Year {year} selected")
            
            # Click search button with enhanced error handling
            search_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'btnSearch'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(2)
            
            # Use JavaScript click and wait for results
            driver.execute_script("arguments[0].click();", search_button)
            print(f"🔍 Worker {worker_id}: Search button clicked for year {year}")
            
            # Wait for search results with longer timeout
            print(f"⏳ Worker {worker_id}: Waiting for search results for year {year}...")
            time.sleep(8)  # Increased wait time for search to complete
            
            # Check if search completed successfully by looking for results or "No Record Found"
            try:
                # Wait for either results table or no records message
                WebDriverWait(driver, 20).until(
                    lambda d: (
                        d.find_elements(By.XPATH, "//table") or 
                        d.find_elements(By.XPATH, "//span[contains(text(), 'No Record Found')]")
                    )
                )
                print(f"✅ Worker {worker_id}: Search completed for year {year}")
                
                # Reset page load timeout back to normal
                driver.set_page_load_timeout(20)
                return True
                
            except Exception as wait_error:
                print(f"⚠️ Worker {worker_id}: Search results timeout for year {year} - {wait_error}")
                # Reset page load timeout back to normal
                driver.set_page_load_timeout(20)
                return False
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Search failed for year {year} - {e}")
            # Reset page load timeout back to normal in case of error
            try:
                driver.set_page_load_timeout(20)
            except:
                pass
            return False
    
    def navigate_to_page(self, driver, page_number, worker_id, max_retries=3):
        """Navigate to specific page with enhanced crash recovery and advanced pagination handling"""
        if page_number == 1:
            return True
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Worker {worker_id}: Navigating to page {page_number} (attempt {attempt + 1})")
                
                # Check if driver is still responsive
                try:
                    driver.current_url
                except Exception as e:
                    print(f"❌ Worker {worker_id}: Driver unresponsive - {e}")
                    return False
                
                # Try multiple navigation strategies
                navigation_success = False
                
                # Strategy 1: Direct page link (works for pages 1-10 typically)
                try:
                    page_link = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f"//a[text()='{page_number}']"))
                    )
                    driver.execute_script("arguments[0].click();", page_link)
                    print(f"✅ Worker {worker_id}: Direct navigation to page {page_number}")
                    navigation_success = True
                    
                except:
                    # Strategy 2: Enhanced ellipsis navigation for pages > 10
                    if page_number > 10:
                        print(f"🔄 Worker {worker_id}: Page {page_number} > 10, using enhanced ellipsis navigation")
                        navigation_success = self._navigate_through_ellipsis(driver, page_number, worker_id)
                        
                        # If ellipsis navigation fails, try direct URL manipulation as last resort
                        if not navigation_success:
                            print(f"🔄 Worker {worker_id}: Ellipsis navigation failed, trying direct URL approach")
                            navigation_success = self._try_direct_url_navigation(driver, page_number, worker_id)
                    else:
                        # Strategy 3: Try alternative selectors for pages <= 10
                        navigation_success = self._try_alternative_navigation(driver, page_number, worker_id)
                
                if not navigation_success:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Worker {worker_id}: Navigation failed, retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    else:
                        print(f"❌ Worker {worker_id}: All navigation strategies failed for page {page_number}")
                        return False
                
                # Wait for page load with timeout
                time.sleep(2)
                
                # Verify navigation succeeded by checking page content
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//table"))
                    )
                    print(f"✅ Worker {worker_id}: Successfully navigated to page {page_number}")
                    return True
                except:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Worker {worker_id}: Page content not loaded, retrying...")
                        time.sleep(1)
                        continue
                    else:
                        print(f"❌ Worker {worker_id}: Page content failed to load")
                        return False
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Worker {worker_id}: Failed to navigate to page {page_number} (attempt {attempt + 1}) - {error_msg}")
                
                # Check for specific crash indicators (Chrome, Firefox, and Edge)
                if any(indicator in error_msg.lower() for indicator in [
                    "chrome not reachable", "session deleted", "firefox not reachable", "edge not reachable", 
                    "connection refused", "browser disconnected", "invalid session id"
                ]):
                    print(f"💥 Worker {worker_id}: Browser crashed, cannot recover")
                    return False
                
                if attempt < max_retries - 1:
                    wait_time = 1 + attempt
                    print(f"🔄 Worker {worker_id}: Retrying navigation in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Worker {worker_id}: All navigation attempts failed")
                    return False
        
        return False
    
    def _navigate_through_ellipsis(self, driver, target_page, worker_id, max_ellipsis_clicks=10):
        """Enhanced ellipsis navigation with multiple click support"""
        try:
            print(f"🔍 Worker {worker_id}: Starting ellipsis navigation to page {target_page}")
            
            for ellipsis_attempt in range(max_ellipsis_clicks):
                # First, check if target page is now visible
                try:
                    target_link = driver.find_element(By.XPATH, f"//a[text()='{target_page}']")
                    if target_link.is_displayed():
                        driver.execute_script("arguments[0].click();", target_link)
                        print(f"✅ Worker {worker_id}: Found and clicked page {target_page} after {ellipsis_attempt} ellipsis clicks")
                        return True
                except:
                    pass
                
                # Look for different types of ellipsis or "Next" links
                ellipsis_found = False
                
                # Try various ellipsis patterns (prioritize forward navigation)
                ellipsis_patterns = [
                    # Forward ellipsis patterns (higher priority)
                    "//a[contains(text(), '...') and not(contains(text(), '...'))]",  # Just ellipsis
                    "//a[contains(text(), '…') and not(contains(text(), '…'))]",     # Unicode ellipsis
                    "//a[contains(text(), 'Next')]",
                    "//a[contains(text(), '>>')]",
                    "//a[contains(text(), '›')]", 
                    "//a[contains(text(), '»')]",
                    # Generic patterns as fallback
                    "//span[contains(@class, 'pagination')]//a[contains(text(), '...')]",
                    "//div[contains(@class, 'pagination')]//a[contains(text(), '...')]"
                ]
                
                for pattern in ellipsis_patterns:
                    try:
                        ellipsis_links = driver.find_elements(By.XPATH, pattern)
                        
                        # Filter for forward ellipsis if multiple found
                        forward_ellipsis = None
                        if len(ellipsis_links) > 1:
                            # Try to identify the rightmost (forward) ellipsis
                            max_x_position = -1
                            for link in ellipsis_links:
                                if link.is_displayed() and link.is_enabled():
                                    try:
                                        x_pos = link.location['x']
                                        if x_pos > max_x_position:
                                            max_x_position = x_pos
                                            forward_ellipsis = link
                                    except:
                                        continue
                        elif len(ellipsis_links) == 1:
                            forward_ellipsis = ellipsis_links[0]
                        
                        if forward_ellipsis and forward_ellipsis.is_displayed() and forward_ellipsis.is_enabled():
                            print(f"🔄 Worker {worker_id}: Clicking FORWARD ellipsis/next (attempt {ellipsis_attempt + 1}) - pattern: {pattern}")
                            driver.execute_script("arguments[0].click();", forward_ellipsis)
                            time.sleep(2)  # Wait for page update
                            ellipsis_found = True
                            break
                    except:
                        continue
                
                if not ellipsis_found:
                    print(f"❌ Worker {worker_id}: No more ellipsis links found after {ellipsis_attempt + 1} attempts")
                    break
                
                # Check if we've gone too far (current visible pages are > target)
                try:
                    visible_pages = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$') and string(number(text())) = text()]")
                    if visible_pages:
                        max_visible = max([int(link.text) for link in visible_pages if link.text.isdigit()])
                        min_visible = min([int(link.text) for link in visible_pages if link.text.isdigit()])
                        print(f"🔍 Worker {worker_id}: Current visible page range: {min_visible}-{max_visible}, target: {target_page}")
                        
                        if min_visible > target_page:
                            print(f"⚠️ Worker {worker_id}: Overshot target page {target_page}, visible range is {min_visible}-{max_visible}")
                            break
                except:
                    pass
            
            # Final attempt to find the target page
            try:
                target_link = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[text()='{target_page}']"))
                )
                driver.execute_script("arguments[0].click();", target_link)
                print(f"✅ Worker {worker_id}: Final attempt successful - clicked page {target_page}")
                return True
            except:
                print(f"❌ Worker {worker_id}: Target page {target_page} not found after ellipsis navigation")
                return False
                
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error during ellipsis navigation: {e}")
            return False
    
    def _try_alternative_navigation(self, driver, page_number, worker_id):
        """Try alternative navigation methods for pages that might not be directly visible"""
        try:
            # Alternative selectors that might work
            alternative_selectors = [
                f"//a[@href and contains(@href, 'Page${page_number}')]",
                f"//a[contains(@href, 'Page') and contains(@href, '{page_number}')]",
                f"//input[@value='{page_number}']/..//a",
                f"//span[text()='{page_number}']/../a",
                f"//td[text()='{page_number}']/..//a"
            ]
            
            for selector in alternative_selectors:
                try:
                    link = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    driver.execute_script("arguments[0].click();", link)
                    print(f"✅ Worker {worker_id}: Alternative navigation successful with selector: {selector}")
                    return True
                except:
                    continue
            
            print(f"❌ Worker {worker_id}: All alternative navigation methods failed for page {page_number}")
            return False
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error in alternative navigation: {e}")
            return False
    
    def _try_direct_url_navigation(self, driver, page_number, worker_id):
        """Try direct URL manipulation as last resort for pagination"""
        try:
            current_url = driver.current_url
            print(f"🔄 Worker {worker_id}: Trying direct URL navigation to page {page_number}")
            print(f"Current URL: {current_url}")
            
            # Common URL patterns for pagination
            url_patterns = [
                f"Page${page_number}",
                f"page={page_number}",
                f"p={page_number}",
                f"pageNum={page_number}"
            ]
            
            for pattern in url_patterns:
                try:
                    # Try to modify the URL directly
                    if "Page$" in current_url:
                        # Replace existing page parameter
                        import re
                        new_url = re.sub(r'Page\$\d+', f'Page${page_number}', current_url)
                        if new_url != current_url:
                            print(f"🔄 Worker {worker_id}: Trying direct URL: {new_url}")
                            driver.get(new_url)
                            time.sleep(3)
                            
                            # Verify the page loaded
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//table"))
                                )
                                print(f"✅ Worker {worker_id}: Direct URL navigation successful")
                                return True
                            except:
                                print(f"⚠️ Worker {worker_id}: Direct URL loaded but no table found")
                                continue
                    
                except Exception as e:
                    print(f"⚠️ Worker {worker_id}: Direct URL pattern {pattern} failed: {e}")
                    continue
            
            print(f"❌ Worker {worker_id}: All direct URL patterns failed")
            return False
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error in direct URL navigation: {e}")
            return False
    
    def debug_pagination_structure(self, driver, worker_id):
        """Debug method to understand pagination structure"""
        try:
            print(f"🔍 Worker {worker_id}: Debugging pagination structure")
            
            # Find all pagination-related elements
            pagination_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page')]")
            print(f"📋 Found {len(pagination_elements)} pagination links:")
            
            for i, elem in enumerate(pagination_elements[:20]):  # Limit to first 20 to avoid spam
                try:
                    text = elem.text.strip()
                    href = elem.get_attribute('href')
                    is_displayed = elem.is_displayed()
                    print(f"   {i+1}. Text: '{text}' | Displayed: {is_displayed} | Href: {href}")
                except:
                    print(f"   {i+1}. Error reading element")
            
            # Look for ellipsis elements
            ellipsis_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '...') or contains(text(), '…')]")
            print(f"📋 Found {len(ellipsis_elements)} ellipsis elements:")
            
            for i, elem in enumerate(ellipsis_elements):
                try:
                    text = elem.text.strip()
                    tag_name = elem.tag_name
                    is_displayed = elem.is_displayed()
                    print(f"   {i+1}. Tag: {tag_name} | Text: '{text}' | Displayed: {is_displayed}")
                except:
                    print(f"   {i+1}. Error reading ellipsis element")
                    
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error debugging pagination: {e}")

    def identify_forward_ellipsis(self, driver, worker_id, current_max_page):
        """Identify which ellipsis is the forward navigation one"""
        try:
            ellipsis_elements = driver.find_elements(By.XPATH, "//a[contains(text(), '...') or contains(text(), '…')]")
            
            if not ellipsis_elements:
                return None
            
            print(f"🔍 Worker {worker_id}: Found {len(ellipsis_elements)} ellipsis elements, analyzing...")
            
            forward_candidates = []
            
            for i, elem in enumerate(ellipsis_elements):
                if not (elem.is_displayed() and elem.is_enabled()):
                    continue
                
                try:
                    # Get position and context
                    location = elem.location
                    x_position = location['x']
                    
                    # Get surrounding text for context
                    parent = elem.find_element(By.XPATH, "./..")
                    surrounding_text = parent.text
                    
                    # Check if it appears after the max page number in the DOM
                    try:
                        preceding_pages = driver.find_elements(By.XPATH, f"//a[text()='{current_max_page}']/preceding::a[contains(text(), '...') or contains(text(), '…')]")
                        following_pages = driver.find_elements(By.XPATH, f"//a[text()='{current_max_page}']/following::a[contains(text(), '...') or contains(text(), '…')]")
                        
                        is_after_max = elem in following_pages
                        is_before_max = elem in preceding_pages
                        
                        candidate_info = {
                            'element': elem,
                            'x_position': x_position,
                            'is_after_max_page': is_after_max,
                            'is_before_max_page': is_before_max,
                            'surrounding_text': surrounding_text[:100]  # Limit text
                        }
                        
                        forward_candidates.append(candidate_info)
                        
                        print(f"   Ellipsis {i+1}: x={x_position}, after_max={is_after_max}, before_max={is_before_max}")
                        
                    except Exception as e:
                        print(f"   Ellipsis {i+1}: Position analysis failed - {e}")
                        
                except Exception as e:
                    print(f"   Ellipsis {i+1}: Error analyzing - {e}")
                    continue
            
            # Choose the best forward candidate
            if forward_candidates:
                # Priority 1: Ellipsis that comes after max page in DOM
                after_max_candidates = [c for c in forward_candidates if c['is_after_max_page']]
                if after_max_candidates:
                    # Choose rightmost if multiple
                    best = max(after_max_candidates, key=lambda x: x['x_position'])
                    print(f"✅ Worker {worker_id}: Selected ellipsis after max page (x={best['x_position']})")
                    return best['element']
                
                # Priority 2: Rightmost ellipsis
                best = max(forward_candidates, key=lambda x: x['x_position'])
                print(f"✅ Worker {worker_id}: Selected rightmost ellipsis (x={best['x_position']})")
                return best['element']
            
            print(f"❌ Worker {worker_id}: No suitable forward ellipsis found")
            return None
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error identifying forward ellipsis: {e}")
            return None

    def download_pdf(self, pdf_url, case_no, pdf_type, worker_id, year_range_name):
        """Download PDF files (proven technique)"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            # Create year range specific downloads directory
            downloads_dir = os.path.join(year_range_name, "pdfs")
            os.makedirs(downloads_dir, exist_ok=True)
            
            safe_case_no = re.sub(r'[^\w\-_.]', '_', case_no)
            filename = f"{safe_case_no}_{pdf_type}.pdf"
            local_path = os.path.join(downloads_dir, filename)
            
            if os.path.exists(local_path):
                print(f"📄 Worker {worker_id}: PDF already exists - {filename}")
                return local_path
            
            print(f"⬇️ Worker {worker_id}: Downloading {filename}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(pdf_url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Worker {worker_id}: Downloaded {filename} ({len(response.content)} bytes)")
            return local_path
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Worker {worker_id}: Download failed for {case_no} - {e}")
            return f"Download Failed: {str(e)}"
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error downloading {case_no} - {e}")
            return f"Download Error: {str(e)}"
    
    def extract_detailed_case_info(self, driver, case_index, worker_id, page_number, year, year_range_name):
        """Extract detailed case information (proven technique)"""
        try:
            print(f"🔍 Worker {worker_id}: Processing Year {year}, Page {page_number}, Case {case_index + 1}")
            
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Worker {worker_id}: Case index {case_index} out of range")
                return None
            
            link = view_details_links[case_index]
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
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
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available",
                    "Files": []
                },
                "Worker_ID": worker_id,
                "Page_Number": page_number,
                "Year": year,
                "Case_Type": self.case_type_text,
                "Year_Range": year_range_name
            }
            
            # Extract case information using proven selectors
            case_no_span = soup.find('span', {'id': 'spCaseNo'})
            if case_no_span:
                case_data["Case_No"] = case_no_span.get_text(strip=True)
            
            case_title_span = soup.find('span', {'id': 'spCaseTitle'})
            if case_title_span:
                case_data["Case_Title"] = case_title_span.get_text(strip=True)
            
            status_span = soup.find('span', {'id': 'spStatus'})
            if status_span:
                case_data["Status"] = status_span.get_text(strip=True)
            
            inst_date_span = soup.find('span', {'id': 'spInstDate'})
            if inst_date_span:
                case_data["Institution_Date"] = inst_date_span.get_text(strip=True)
            
            disp_date_span = soup.find('span', {'id': 'spDispDate'})
            if disp_date_span:
                case_data["Disposal_Date"] = disp_date_span.get_text(strip=True)
            
            # Extract advocates
            aor_span = soup.find('span', {'id': 'spAOR'})
            if aor_span:
                aor_html = str(aor_span)
                
                if '<br>' in aor_html:
                    parts = aor_html.split('<br>')
                    for part in parts:
                        clean_text = re.sub(r'<[^>]+>', '', part).strip()
                        if '(AOR)' in clean_text:
                            case_data["Advocates"]["AOR"] = clean_text
                        elif '(ASC)' in clean_text:
                            case_data["Advocates"]["ASC"] = clean_text
                        elif 'prosecutor' in clean_text.lower():
                            case_data["Advocates"]["Prosecutor"] = clean_text
                else:
                    aor_text = aor_span.get_text()
                    lines = aor_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if '(AOR)' in line:
                            case_data["Advocates"]["AOR"] = line
                        elif '(ASC)' in line:
                            case_data["Advocates"]["ASC"] = line
                        elif 'prosecutor' in line.lower():
                            case_data["Advocates"]["Prosecutor"] = line
            
            # Extract PDF links (proven technique)
            pdf_links = soup.find_all('a', href=True)
            
            memo_files = []
            judgment_files = []
            
            for link in pdf_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True)
                
                if (href and 
                    ('.pdf' in href.lower() or 
                     'digital copy' in link_text.lower() or
                     ('file' in link_text.lower() and '.pdf' in href.lower()))):
                    
                    if (any(keyword in link_text.lower() for keyword in ['digital copy', 'file', 'memo', 'petition', 'appeal']) and
                        not any(keyword in link_text.lower() for keyword in ['judgment', 'order'])):
                        memo_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
                    elif any(keyword in link_text.lower() for keyword in ['judgment', 'order']):
                        judgment_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
                    else:
                        memo_files.append({
                            'text': link_text,
                            'href': href,
                            'type': 'PDF'
                        })
            
            # Handle memo files
            if memo_files:
                case_data["Petition_Appeal_Memo"]["Files"] = []
                for i, memo_file in enumerate(memo_files):
                    file_info = {
                        "File": memo_file['href'],
                        "Type": memo_file['type'], 
                        "Description": memo_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }
                    
                    link_info = self.download_pdf(
                        memo_file['href'], 
                        case_data["Case_No"], 
                        f"memo_{i+1}", 
                        worker_id,
                        year_range_name
                    )
                    file_info["Downloaded_Path"] = link_info
                    case_data["Petition_Appeal_Memo"]["Files"].append(file_info)
                
                case_data["Petition_Appeal_Memo"]["File"] = memo_files[0]['href']
                case_data["Petition_Appeal_Memo"]["Type"] = "PDF"
                case_data["Petition_Appeal_Memo"]["Downloaded_Path"] = case_data["Petition_Appeal_Memo"]["Files"][0]["Downloaded_Path"]
            
            # Handle judgment files
            if judgment_files:
                case_data["Judgement_Order"]["Files"] = []
                for i, judgment_file in enumerate(judgment_files):
                    file_info = {
                        "File": judgment_file['href'],
                        "Type": judgment_file['type'],
                        "Description": judgment_file['text'],
                        "Downloaded_Path": "No PDF Available"
                    }
                    
                    link_info = self.download_pdf(
                        judgment_file['href'], 
                        case_data["Case_No"], 
                        f"judgment_{i+1}", 
                        worker_id,
                        year_range_name
                    )
                    file_info["Downloaded_Path"] = link_info
                    case_data["Judgement_Order"]["Files"].append(file_info)
                
                case_data["Judgement_Order"]["File"] = judgment_files[0]['href']
                case_data["Judgement_Order"]["Type"] = "PDF"
                case_data["Judgement_Order"]["Downloaded_Path"] = case_data["Judgement_Order"]["Files"][0]["Downloaded_Path"]
            
            # Extract history
            history_span = soup.find('span', {'id': 'spnNotFound'})
            if history_span and 'No Fixation History Found' in history_span.get_text():
                case_data["History"] = [{"note": "No Fixation History Found"}]
            else:
                history_div = soup.find('div', {'id': 'divResult'})
                if history_div:
                    history_text = history_div.get_text(strip=True)
                    if history_text and "No Fixation History Found" not in history_text:
                        case_data["History"].append({"note": history_text})
            
            driver.back()
            time.sleep(1)
            
            # Write case incrementally to JSON file
            if case_data and case_data.get("Case_No") != "N/A":
                self.write_case_incrementally(case_data, year_range_name)
            
            print(f"✅ Worker {worker_id}: Year {year}, Page {page_number}, Case {case_index + 1} processed - {case_data['Case_No']}")
            return case_data
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Error processing Year {year}, Page {page_number}, Case {case_index + 1} - {e}")
            try:
                driver.back()
                time.sleep(1)
            except:
                pass
            return None
    
    def check_driver_health(self, driver, worker_id):
        """Check if driver is still healthy and responsive"""
        try:
            # Test basic driver responsiveness
            current_url = driver.current_url
            driver.execute_script("return document.readyState;")
            return True
        except Exception as e:
            print(f"💔 Worker {worker_id}: Driver health check failed - {e}")
            return False
    
    def restart_driver_if_needed(self, driver, worker_id, max_failures=3):
        """Restart driver if it becomes unhealthy"""
        if self.check_driver_health(driver, worker_id):
            return driver
        
        print(f"🔄 Worker {worker_id}: Restarting unhealthy Edge driver...")
        
        try:
            if driver:
                driver.quit()
        except:
            pass
        
        time.sleep(2)
        new_driver = self.create_optimized_driver(headless=False)
        
        if new_driver:
            print(f"✅ Worker {worker_id}: Edge driver restarted successfully")
            return new_driver
        else:
            print(f"❌ Worker {worker_id}: Failed to restart Edge driver")
            return None

    def worker_process_year_sequential(self, year, worker_id, year_range_name, total_workers=1, worker_index=0):
        """Process pages sequentially with chunk-based pagination (Enhanced for Chunk-by-Chunk Processing)"""
        driver = None
        processed_count = 0
        
        try:
            driver = self.create_optimized_driver(headless=False)
            if not driver:
                print(f"❌ Worker {worker_id}: Failed to create driver")
                return 0

            if not self.navigate_and_search(driver, worker_id, year):
                print(f"❌ Worker {worker_id}: Failed to navigate and search for year {year}")
                return 0

            # Check if there are any results
            try:
                no_records = driver.find_element(By.XPATH, "//span[contains(text(), 'No Record Found')]")
                print(f"ℹ️ Worker {worker_id}: No records found for year {year}")
                return 0
            except:
                # Continue - records found
                pass

            # Get initial pagination info with enhanced handling for few pages
            try:
                time.sleep(3)  # Wait for pagination to load
                page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
                initial_visible_pages = len(page_links) + 1 if page_links else 1
                print(f"📋 Worker {worker_id}: Initial visible pages: {initial_visible_pages}")
                
                # Check if this is a single page result (no pagination)
                if initial_visible_pages == 1 and not page_links:
                    print(f"📄 Worker {worker_id}: Single page detected for year {year}")
            except Exception as e:
                print(f"⚠️ Worker {worker_id}: Error reading pagination info: {e}")
                initial_visible_pages = 1

            # Process pages using chunk-based navigation
            current_chunk_start = 1
            chunk_failures = 0
            max_chunk_failures = 3
            
            while True:
                print(f"🔄 Worker {worker_id}: Processing chunk starting from page {current_chunk_start} for year {year}")
                
                # Health check before processing each chunk
                if not self.check_driver_health(driver, worker_id):
                    print(f"💔 Worker {worker_id}: Driver unhealthy before chunk {current_chunk_start}")
                    driver = self.restart_driver_if_needed(driver, worker_id)
                    if not driver:
                        print(f"❌ Worker {worker_id}: Cannot restart driver, stopping")
                        break
                    
                    # Re-navigate to search results after restart
                    if not self.navigate_and_search(driver, worker_id, year):
                        print(f"❌ Worker {worker_id}: Failed to re-navigate after restart")
                        break
                
                # Get currently visible pages in this chunk
                try:
                    time.sleep(2)  # Wait for page load
                    page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$') and string(number(text())) = text()]")
                    visible_pages = sorted([int(link.text) for link in page_links if link.text.isdigit()])
                    
                    if not visible_pages:
                        print(f"⚠️ Worker {worker_id}: No visible page numbers found in current chunk")
                        break
                    
                    chunk_start = min(visible_pages)
                    chunk_end = max(visible_pages)
                    print(f"📋 Worker {worker_id}: Current chunk shows pages {chunk_start}-{chunk_end}")
                    
                except Exception as e:
                    print(f"❌ Worker {worker_id}: Error reading visible pages: {e}")
                    chunk_failures += 1
                    if chunk_failures >= max_chunk_failures:
                        print(f"❌ Worker {worker_id}: Too many chunk failures, stopping")
                        break
                    continue
                
                # Process each page in current visible chunk
                pages_processed_in_chunk = 0
                for page_num in visible_pages:
                    print(f"🔄 Worker {worker_id}: Processing page {page_num}/{chunk_end} in current chunk")
                    
                    # Navigate to specific page within chunk
                    if page_num > 1:
                        try:
                            page_link = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, f"//a[text()='{page_num}']"))
                            )
                            driver.execute_script("arguments[0].click();", page_link)
                            time.sleep(2)
                            print(f"✅ Worker {worker_id}: Navigated to page {page_num}")
                        except Exception as nav_error:
                            print(f"❌ Worker {worker_id}: Failed to navigate to page {page_num}: {nav_error}")
                            continue
                    
                    # Process cases on this page
                    try:
                        view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                        total_cases_on_page = len(view_details_links)
                        
                        print(f"📋 Worker {worker_id}: Found {total_cases_on_page} cases on page {page_num}")
                        
                        if total_cases_on_page == 0:
                            print(f"⚠️ Worker {worker_id}: No cases found on page {page_num}, skipping")
                            continue
                        
                        # Divide cases on this page among workers
                        if total_workers > 1:
                            cases_per_worker = max(1, total_cases_on_page // total_workers)
                            start_case = worker_index * cases_per_worker
                            end_case = min(total_cases_on_page, start_case + cases_per_worker)
                            
                            # Handle remaining cases for the last worker
                            if worker_index == total_workers - 1:
                                end_case = total_cases_on_page
                            
                            assigned_cases = list(range(start_case, end_case))
                            print(f"🔧 Worker {worker_id}: Processing cases {start_case+1}-{end_case} on page {page_num} ({len(assigned_cases)} cases)")
                        else:
                            # Single worker processes all cases
                            assigned_cases = list(range(total_cases_on_page))
                            print(f"🔧 Worker {worker_id}: Processing all {total_cases_on_page} cases on page {page_num}")

                        # Process assigned cases on this page
                        for case_index in assigned_cases:
                            # Health check every 5 cases
                            if case_index % 5 == 0 and case_index > 0:
                                if not self.check_driver_health(driver, worker_id):
                                    print(f"💔 Worker {worker_id}: Driver became unhealthy during case processing")
                                    break
                            
                            case_data = self.extract_detailed_case_info(driver, case_index, worker_id, page_num, year, year_range_name)
                            if case_data:
                                processed_count += 1

                            time.sleep(0.3)  # Reduced sleep time
                        
                        pages_processed_in_chunk += 1
                        print(f"✅ Worker {worker_id}: Completed page {page_num} - processed {len(assigned_cases)} cases")
                            
                    except Exception as page_error:
                        print(f"❌ Worker {worker_id}: Error processing page {page_num} - {page_error}")
                        continue
                
                # Check if there are more pages (look for FORWARD ellipsis to next chunk)
                try:
                    current_max_page = max(visible_pages) if visible_pages else chunk_end
                    forward_ellipsis = self.identify_forward_ellipsis(driver, worker_id, current_max_page)
                    
                    if forward_ellipsis:
                        print(f"🔄 Worker {worker_id}: Clicking FORWARD ellipsis to move to next chunk after page {chunk_end}")
                        driver.execute_script("arguments[0].click();", forward_ellipsis)
                        time.sleep(3)  # Wait for next chunk to load
                        current_chunk_start = chunk_end + 1
                        chunk_failures = 0  # Reset failure counter on successful navigation
                    else:
                        print(f"✅ Worker {worker_id}: No forward ellipsis found, reached end of pages")
                        break
                        
                except Exception as ellipsis_error:
                    print(f"❌ Worker {worker_id}: Error checking for forward ellipsis: {ellipsis_error}")
                    break
                
                print(f"✅ Worker {worker_id}: Completed chunk {chunk_start}-{chunk_end} - {pages_processed_in_chunk} pages processed")

            print(f"✅ Worker {worker_id}: Completed year {year} ALL chunks - {processed_count} cases total")
            return processed_count
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Critical error processing year {year} - {e}")
            return processed_count
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def worker_process_year(self, year, worker_id, year_range_name, total_workers=1, worker_index=0):
        """Process assigned pages for a specific year (work division among workers)"""
        driver = None
        processed_count = 0  # Count instead of storing all cases
        
        try:
            driver = self.create_optimized_driver(headless=False)
            if not driver:
                print(f"❌ Worker {worker_id}: Failed to create driver")
                return 0

            if not self.navigate_and_search(driver, worker_id, year):
                print(f"❌ Worker {worker_id}: Failed to navigate and search for year {year}")
                return 0

            # Check if there are any results
            try:
                no_records = driver.find_element(By.XPATH, "//span[contains(text(), 'No Record Found')]")
                print(f"ℹ️ Worker {worker_id}: No records found for year {year}")
                return 0
            except:
                # Continue - records found
                pass

            # Get total pages
            try:
                page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
                total_pages = len(page_links) + 1 if page_links else 1
                print(f"📋 Worker {worker_id}: Found {total_pages} total pages for year {year}")
            except:
                total_pages = 1

            # Calculate which pages this worker should handle
            if total_workers > 1:
                # Divide pages among workers
                pages_per_worker = max(1, total_pages // total_workers)
                start_page = (worker_index * pages_per_worker) + 1
                end_page = min(total_pages, start_page + pages_per_worker - 1)
                
                # Handle remaining pages for the last worker
                if worker_index == total_workers - 1:
                    end_page = total_pages
                    
                assigned_pages = list(range(start_page, end_page + 1))
                print(f"🔧 Worker {worker_id}: Assigned pages {start_page}-{end_page} ({len(assigned_pages)} pages)")
            else:
                # Single worker processes all pages
                assigned_pages = list(range(1, total_pages + 1))
                print(f"🔧 Worker {worker_id}: Processing all pages 1-{total_pages}")

            # Process assigned pages only
            page_failures = 0
            max_page_failures = 3
            
            for page_num in assigned_pages:
                # Health check before processing each page
                if not self.check_driver_health(driver, worker_id):
                    print(f"💔 Worker {worker_id}: Driver unhealthy before page {page_num}")
                    driver = self.restart_driver_if_needed(driver, worker_id)
                    if not driver:
                        print(f"❌ Worker {worker_id}: Cannot restart driver, stopping")
                        break
                    
                    # Re-navigate to search results after restart
                    if not self.navigate_and_search(driver, worker_id, year):
                        print(f"❌ Worker {worker_id}: Failed to re-navigate after restart")
                        break
                
                # Navigate to page if needed
                if page_num > 1:
                    navigation_success = self.navigate_to_page(driver, page_num, worker_id)
                    if not navigation_success:
                        page_failures += 1
                        print(f"⚠️ Worker {worker_id}: Page navigation failed ({page_failures}/{max_page_failures})")
                        
                        if page_failures >= max_page_failures:
                            print(f"❌ Worker {worker_id}: Too many page failures, stopping")
                            break
                        continue
                
                # Reset failure counter on successful navigation
                page_failures = 0
                
                try:
                    view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                    total_cases_on_page = len(view_details_links)

                    print(f"📋 Worker {worker_id}: Processing {total_cases_on_page} cases on page {page_num} for year {year}")

                    for case_index in range(total_cases_on_page):
                        # Health check every 5 cases
                        if case_index % 5 == 0 and case_index > 0:
                            if not self.check_driver_health(driver, worker_id):
                                print(f"💔 Worker {worker_id}: Driver became unhealthy during case processing")
                                break
                        
                        case_data = self.extract_detailed_case_info(driver, case_index, worker_id, page_num, year, year_range_name)
                        if case_data:
                            processed_count += 1

                        time.sleep(0.3)  # Reduced sleep time
                        
                except Exception as page_error:
                    print(f"❌ Worker {worker_id}: Error processing page {page_num} - {page_error}")
                    continue

            print(f"✅ Worker {worker_id}: Completed year {year} pages {assigned_pages[0]}-{assigned_pages[-1]} - {processed_count} cases")
            return processed_count
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: Critical error processing year {year} - {e}")
            return processed_count
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def display_year_ranges_menu(self):
        """Display available year ranges for selection"""
        print(f"\n📅 AVAILABLE YEAR RANGES FOR CRL.Sha.A. LAHORE EXTRACTION:")
        print("=" * 60)
        
        for key, range_info in self.year_ranges.items():
            years_str = ", ".join(map(str, range_info['years']))
            print(f"   {key}. {range_info['name']} ({len(range_info['years'])} years: {years_str})")
        
        print(f"\n   0. Extract ALL year ranges")
        print(f"   q. Quit")
    
    def get_worker_allocation(self, selected_ranges):
        """Get user input for worker allocation per year within selected ranges"""
        worker_allocation = {}
        
        print(f"\n⚙️ WORKER ALLOCATION CONFIGURATION")
        print("=" * 50)
        print(f"Available total workers: {self.max_workers}")
        print("You can assign workers to specific years for optimized extraction")
        print("Leave blank for automatic distribution")
        print("⚠️  WARNING: Multiple workers per year use more system resources")
        print("💡 TIP: Start with 1-2 workers per year, increase if stable")
        print("🌐 EDGE: Enhanced stability for long-running extractions")
        print("🔧 RESOURCE LIMIT: Max 6 concurrent browsers to prevent crashes")
        
        for range_key in selected_ranges:
            range_info = self.year_ranges[range_key]
            range_name = range_info['name']
            years = range_info['years']
            
            print(f"\n📊 Year Range: {range_name}")
            print(f"Years: {years}")
            
            # Ask user if they want manual allocation for this range
            manual_choice = input(f"Configure worker allocation for {range_name}? (y/n, default: n): ").strip().lower()
            
            if manual_choice == 'y':
                year_workers = {}
                total_assigned = 0
                
                print(f"\nAssign workers to individual years (total available: {self.max_workers}):")
                
                for year in years:
                    while True:
                        try:
                            remaining_workers = self.max_workers - total_assigned
                            if remaining_workers <= 0:
                                print(f"⚠️ All {self.max_workers} workers have been assigned")
                                year_workers[year] = 0
                                break
                            
                            worker_input = input(f"  Workers for year {year} (0-{remaining_workers}, default: auto): ").strip()
                            
                            if not worker_input:
                                # Auto-assign remaining workers equally
                                remaining_years = len(years) - len(year_workers)
                                if remaining_years > 0:
                                    auto_workers = max(1, remaining_workers // remaining_years)
                                    year_workers[year] = min(auto_workers, remaining_workers)
                                    total_assigned += year_workers[year]
                                else:
                                    year_workers[year] = 0
                                break
                            
                            workers = int(worker_input)
                            if workers < 0:
                                print("❌ Workers cannot be negative")
                                continue
                            
                            if workers > remaining_workers:
                                print(f"❌ Only {remaining_workers} workers remaining")
                                continue
                            
                            year_workers[year] = workers
                            total_assigned += workers
                            break
                            
                        except ValueError:
                            print("❌ Please enter a valid number")
                
                # Handle any remaining workers
                if total_assigned < self.max_workers:
                    remaining = self.max_workers - total_assigned
                    print(f"\n⚠️ {remaining} workers remain unassigned. Auto-distributing...")
                    
                    # Distribute remaining workers to years with 0 workers first
                    zero_worker_years = [year for year, workers in year_workers.items() if workers == 0]
                    if zero_worker_years and remaining > 0:
                        per_year = remaining // len(zero_worker_years)
                        extra = remaining % len(zero_worker_years)
                        
                        for i, year in enumerate(zero_worker_years):
                            year_workers[year] = per_year + (1 if i < extra else 0)
                
                worker_allocation[range_key] = year_workers
                
                # Show allocation summary
                print(f"\n✅ Worker allocation for {range_name}:")
                for year, workers in year_workers.items():
                    status = "🔥" if workers > 1 else "⚡" if workers == 1 else "⏸️"
                    print(f"   {year}: {workers} workers {status}")
                
            else:
                # Auto-distribute workers equally across years
                workers_per_year = max(1, self.max_workers // len(years))
                year_workers = {year: workers_per_year for year in years}
                
                # Distribute any remaining workers
                remaining = self.max_workers - (workers_per_year * len(years))
                for i in range(remaining):
                    year_workers[years[i]] += 1
                
                worker_allocation[range_key] = year_workers
                
                print(f"✅ Auto-distributed {self.max_workers} workers across {len(years)} years")
                for year, workers in year_workers.items():
                    print(f"   {year}: {workers} workers")
        
        return worker_allocation
    
    def get_user_selection(self):
        """Get user selection for year ranges"""
        while True:
            self.display_year_ranges_menu()
            
            choice = input(f"\nSelect year range(s) to extract (e.g., '1' for single range, '1,5,9' for multiple, '0' for all): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice == '0':
                # Return all year ranges
                return list(self.year_ranges.keys())
            
            # Parse selection
            try:
                selected_ranges = []
                choices = [c.strip() for c in choice.split(',')]
                
                for c in choices:
                    if c in self.year_ranges:
                        selected_ranges.append(c)
                    else:
                        print(f"❌ Invalid choice: {c}")
                        break
                else:
                    if selected_ranges:
                        return selected_ranges
                
                print("❌ Please enter valid choices")
                
            except ValueError:
                print("❌ Please enter valid numbers separated by commas")
    
    def show_work_division_plan(self, selected_ranges, worker_allocation):
        """Display how work will be divided among workers"""
        print(f"\n📊 WORK DIVISION PLAN")
        print("=" * 60)
        
        for range_key in selected_ranges:
            range_info = self.year_ranges[range_key]
            range_name = range_info['name']
            years = range_info['years']
            year_workers = worker_allocation[range_key]
            
            print(f"\n📋 {range_name}")
            print("-" * 40)
            
            total_workers = sum(year_workers.values())
            active_years = len([y for y, w in year_workers.items() if w > 0])
            
            print(f"   Total Workers: {total_workers}")
            print(f"   Active Years: {active_years}/{len(years)}")
            print(f"   Work Division:")
            
            for year in years:
                workers = year_workers[year]
                if workers > 0:
                    if workers == 1:
                        division_info = "Single worker processes all pages sequentially"
                    else:
                        division_info = f"{workers} workers process pages sequentially, divide cases per page"
                    
                    status = "🔥 High Priority" if workers > 2 else "⚡ Standard"
                    print(f"     {year}: {workers} workers - {division_info} {status}")
                else:
                    print(f"     {year}: ⏸️ Skipped")
        
        print("\n💡 Chunk-Based Sequential Processing Mode:")
        print("   • Process pages in chunks (1-10, then 11-20, then 21-30, etc.)")
        print("   • All workers process each page in current chunk before moving to next chunk")
        print("   • Workers divide the ~15 cases per page among themselves")
        print("   • Click ellipsis (...) to move to next chunk of 10 pages")
        print("   • Enhanced pagination: Handles chunk-based navigation automatically")
        print("   • No duplicate cases: Proper case division per page within each chunk")
        
    def run_extraction(self, selected_ranges, worker_allocation):
        """Run extraction for selected year ranges with custom worker allocation"""
        print(f"\n🚀 CRL.Sha.A. LAHORE EXTRACTION STARTING")
        print("=" * 50)
        
        total_start_time = time.time()
        total_cases_extracted = 0
        
        for range_key in selected_ranges:
            range_info = self.year_ranges[range_key]
            years = range_info['years']
            range_name = range_info['name']
            year_workers = worker_allocation[range_key]
            
            print(f"\n📊 PROCESSING YEAR RANGE: {range_name}")
            print(f"   Years: {years}")
            
            # Initialize JSON file for this range
            if not self.initialize_json_file(range_name):
                print(f"❌ Failed to initialize JSON file for {range_name}, skipping")
                continue
            
            # Display worker allocation
            print(f"   Worker Allocation:")
            for year in years:
                workers = year_workers[year]
                status = "🔥 High Priority" if workers > 2 else "⚡ Standard" if workers > 0 else "⏸️ Skipped"
                print(f"     {year}: {workers} workers - {status}")
            
            start_time = time.time()
            range_case_count = 0
            
            try:
                # Process years with custom worker allocation
                # Group years by worker count for efficient processing
                worker_groups = {}
                for year, workers in year_workers.items():
                    if workers > 0:  # Only process years with assigned workers
                        if workers not in worker_groups:
                            worker_groups[workers] = []
                        worker_groups[workers].append(year)
                
                # Process each worker group with limited concurrency
                for workers_count, group_years in worker_groups.items():
                    if not group_years:
                        continue
                    
                    # Limit concurrent workers to prevent resource exhaustion
                    effective_workers = min(workers_count * len(group_years), 6)  # Max 6 concurrent browsers
                    
                    print(f"\n⚙️ Processing {len(group_years)} years with {workers_count} workers each (CHUNK-BASED MODE)")
                    print(f"   📝 Work Division: Workers process chunks (1-10, 11-20, etc.), dividing cases per page")
                    print(f"   🔄 Navigation: Automatic ellipsis clicking to move between chunks")
                    print(f"   🌐 Browser Management: Limited to {effective_workers} concurrent Edge browsers")
                    
                    # Process years in this group with parallel workers (sequential page processing)
                    with ThreadPoolExecutor(max_workers=effective_workers) as executor:
                        future_to_year = {}
                        
                        # Submit jobs for each year with its allocated workers
                        for year in group_years:
                            total_workers_for_year = workers_count
                            for worker_index in range(workers_count):
                                future = executor.submit(
                                    self.worker_process_year_sequential,  # Use sequential method
                                    year, 
                                    f"Y{year}_W{worker_index+1}", 
                                    range_name,
                                    total_workers_for_year,
                                    worker_index
                                )
                                future_to_year[future] = (year, worker_index+1)
                        
                        # Collect results (now just counts)
                        year_case_counts = {}
                        for future in as_completed(future_to_year):
                            year, worker_id = future_to_year[future]
                            try:
                                case_count = future.result()
                                if year not in year_case_counts:
                                    year_case_counts[year] = 0
                                year_case_counts[year] += case_count
                                print(f"✅ Year {year} Worker {worker_id} completed: {case_count} cases")
                            except Exception as e:
                                print(f"❌ Year {year} Worker {worker_id} failed: {e}")
                        
                        # Sum up total cases for this range
                        for year, case_count in year_case_counts.items():
                            range_case_count += case_count
                            allocated_workers = year_workers[year]
                            print(f"📋 Year {year} Summary: {case_count} cases processed (using {allocated_workers} workers)")
                
                # Finalize JSON file for this range
                self.finalize_json_file(range_name)
                total_cases_extracted += range_case_count
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"\n🎯 YEAR RANGE {range_name} COMPLETED!")
                print(f"   Years Processed: {len([y for y, w in year_workers.items() if w > 0])}")
                print(f"   Years Skipped: {len([y for y, w in year_workers.items() if w == 0])}")
                print(f"   Cases Found: {range_case_count}")
                print(f"   Duration: {duration:.2f} seconds")
                if range_case_count > 0:
                    print(f"   Avg Time/Case: {duration/range_case_count:.2f} seconds")
                
            except Exception as e:
                print(f"❌ Range {range_name} failed: {e}")
                # Still finalize the JSON file even if there was an error
                self.finalize_json_file(range_name)
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        print(f"\n🎉 COMPLETE CRL.Sha.A. EXTRACTION FINISHED!")
        print(f"   Total Year Ranges: {len(selected_ranges)}")
        print(f"   Total Cases: {total_cases_extracted}")
        print(f"   Total Duration: {total_duration:.2f} seconds")
        if total_cases_extracted > 0:
            print(f"   Avg Time/Case: {total_duration/total_cases_extracted:.2f} seconds")
        
        return True
    
    # Note: save_range_results method removed - using incremental writing instead
    # Cases are written immediately as they're extracted via write_case_incrementally()
    # JSON files are finalized via finalize_json_file()


def main():
    """Main function"""
    print("🚀 CRL.Sha.A. (CRIMINAL APPEALS) LAHORE INTERACTIVE EXTRACTOR")
    print("=" * 60)
    print("Enhanced with Edge WebDriver for improved stability")
    print("Supports selective year range extraction with PDF downloads")
    
    extractor = CrlALahoreInteractiveExtractor(max_workers=5)
    
    # Get user selection
    selected_ranges = extractor.get_user_selection()
    
    if not selected_ranges:
        print("\n👋 Extraction cancelled by user")
        return
    
    # Show selected ranges
    print(f"\n📋 SELECTED YEAR RANGES:")
    for range_key in selected_ranges:
        range_info = extractor.year_ranges[range_key]
        print(f"   {range_info['name']}: {range_info['years']}")
    
    # Confirm extraction
    confirm = input(f"\nProceed with extraction? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n👋 Extraction cancelled")
        return
    
    # Get user's worker allocation preferences
    print(f"\n⚙️ WORKER ALLOCATION SETUP")
    print("Now configure how many workers to assign to each year within your selected ranges.")
    worker_allocation = extractor.get_worker_allocation(selected_ranges)
    
    # Show work division plan
    extractor.show_work_division_plan(selected_ranges, worker_allocation)
    
    # Final confirmation
    final_confirm = input(f"\nProceed with this work division plan? (y/n): ").strip().lower()
    if final_confirm != 'y':
        print("\n👋 Extraction cancelled")
        return
    
    # Run extraction with custom allocation
    if extractor.run_extraction(selected_ranges, worker_allocation):
        print("\n🎉 Crl.Sha.A. Lahore extraction completed successfully!")
    else:
        print("\n❌ Crl.Sha.A. Lahore extraction failed")


if __name__ == "__main__":
    main()