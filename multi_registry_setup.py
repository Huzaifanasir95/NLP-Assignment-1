"""
Multi-Registry Supreme Court Structure Creator and Manager
Creates organized folder structures for all Pakistani Supreme Court registries
"""

import json
import os
from pathlib import Path


class MultiRegistryStructureManager:
    """Manages organized folder structures for all Supreme Court registries"""
    
    def __init__(self, base_dir="d:/SEM7/NLP/NLP-Assignment-1"):
        self.base_dir = Path(base_dir)
        
        # Registry configurations
        self.registries = {
            'Peshawar': {
                'code': 'P',
                'name': 'Peshawar',
                'folder': 'Peshawar'
            },
            'Quetta': {
                'code': 'Q', 
                'name': 'Quetta',
                'folder': 'Quetta'
            },
            'Karachi': {
                'code': 'K',
                'name': 'Karachi', 
                'folder': 'Karachi'
            }
        }
        
        print(f"🏛️ Multi-Registry Supreme Court Structure Manager Initialized")
        print(f"📍 Registries: {', '.join(self.registries.keys())}")
    
    def sanitize_folder_name(self, name):
        """Convert case type names to valid folder names"""
        # Replace dots and special characters
        sanitized = name.replace('.', '_').replace('(', '_').replace(')', '_')
        # Remove trailing underscores
        sanitized = sanitized.rstrip('_')
        return sanitized
    
    def load_analysis_data(self, registry_name):
        """Load analysis data for a specific registry"""
        registry_folder = self.registries[registry_name]['folder']
        analysis_file = self.base_dir / registry_folder / f"{registry_folder.lower()}_structure_analysis.json"
        
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
    
    def create_folder_structure(self, registry_name):
        """Create the complete organized folder structure for a registry"""
        print(f"\\n🏗️ CREATING {registry_name.upper()} ORGANIZED FOLDER STRUCTURE")
        print("=" * 60)
        
        analysis_data = self.load_analysis_data(registry_name)
        case_types = analysis_data['case_types']
        year_ranges = analysis_data['year_ranges']
        
        registry_folder = self.registries[registry_name]['folder']
        registry_dir = self.base_dir / registry_folder
        
        created_folders = 0
        
        for case_type in case_types:
            case_value = case_type['value']
            case_text = case_type['text']
            case_folder_name = f"{case_value}_{self.sanitize_folder_name(case_text)}"
            
            # Create main case type folder
            case_type_dir = registry_dir / case_folder_name
            case_type_dir.mkdir(exist_ok=True)
            
            print(f"📁 Case Type: {case_folder_name}")
            
            # Create year range folders within case type folder
            for year_range in year_ranges:
                range_name = year_range['name']
                year_range_dir = case_type_dir / range_name
                year_range_dir.mkdir(exist_ok=True)
                
                # Also create the underscore version for consistency
                range_name_underscore = range_name.replace('-', '_')
                year_range_dir_underscore = case_type_dir / range_name_underscore
                year_range_dir_underscore.mkdir(exist_ok=True)
                
                created_folders += 2
                print(f"   📂 {range_name} & {range_name_underscore}")
        
        print(f"\\n✅ {registry_name.upper()} FOLDER STRUCTURE CREATED SUCCESSFULLY!")
        print(f"   Total Case Type Folders: {len(case_types)}")
        print(f"   Total Year Range Folders: {created_folders}")
        print(f"   Structure: {len(case_types)} case types × {len(year_ranges)} year ranges")
        
        return True
    
    def create_extraction_script(self, registry_name, case_type, year_range):
        """Create individual extraction script for a case type-year range combination"""
        registry_config = self.registries[registry_name]
        registry_code = registry_config['code']
        registry_folder = registry_config['folder']
        
        case_value = case_type['value']
        case_text = case_type['text']
        case_folder_name = f"{case_value}_{self.sanitize_folder_name(case_text)}"
        
        range_name = year_range['name']
        script_dir = self.base_dir / registry_folder / case_folder_name / range_name
        script_file = script_dir / f"extract_{case_folder_name}_{range_name.replace('-', '_')}.py"
        
        # Generate the extraction script content
        script_content = f'''"""
{registry_name} Supreme Court Case Extractor
Case Type: {case_text} (Value: {case_value})
Year Range: {range_name}
Registry: {registry_name} ({registry_code})
"""

import json
import os
import time
import threading
from datetime import datetime
from multiprocessing import Process, Manager
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


class {registry_name}InteractiveExtractor:
    """Interactive {registry_name} extractor for case type {case_text}"""
    
    def __init__(self):
        self.case_type_value = "{case_value}"  # {case_text}
        self.registry_value = "{registry_code}"  # {registry_name}
        self.year_range = {year_range['years']}
        self.range_name = "{range_name}"
        
        # Paths
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir
        
        # Active JSON file tracking for append mode
        self.active_json_files = {{}}
        self.json_locks = {{}}
        
        print(f"🏛️ {registry_name} Supreme Court Case Extractor Initialized")
        print(f"📋 Case Type: {case_text} (Value: {case_value})")
        print(f"📅 Year Range: {range_name}")
        print(f"🏢 Registry: {registry_name}")
    
    def setup_edge_driver(self):
        """Setup Edge WebDriver with optimized options"""
        try:
            edge_options = Options()
            
            # Performance optimizations
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--disable-gpu-sandbox')
            edge_options.add_argument('--disable-software-rasterizer')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--disable-extensions')
            edge_options.add_argument('--disable-plugins')
            edge_options.add_argument('--disable-images')
            edge_options.add_argument('--disable-javascript')
            edge_options.add_argument('--disable-background-timer-throttling')
            edge_options.add_argument('--disable-backgrounding-occluded-windows')
            edge_options.add_argument('--disable-renderer-backgrounding')
            edge_options.add_argument('--disable-web-security')
            edge_options.add_argument('--allow-running-insecure-content')
            
            # Memory and process management
            edge_options.add_argument('--memory-pressure-off')
            edge_options.add_argument('--max_old_space_size=4096')
            edge_options.add_argument('--single-process')
            
            # Anti-detection and crash prevention
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_argument('--crash-dumps-dir=/tmp')
            edge_options.add_argument('--disable-crash-reporter')
            
            # Create WebDriver
            driver = webdriver.Edge(options=edge_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}})")
            
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            return driver
            
        except Exception as e:
            print(f"❌ Failed to setup Edge driver: {{e}}")
            return None
    
    def navigate_and_search(self, driver, worker_id, year):
        """Navigate and search for specific year with enhanced timeout handling"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Worker {{worker_id}}: Navigating for year {{year}}")
            
            # Use longer timeout for initial page load
            driver.set_page_load_timeout(30)
            driver.get(url)
            time.sleep(5)  # Increased wait time
            
            # Wait for page to load with longer timeout
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "ddlCaseType"))
            )
            print(f"✅ Worker {{worker_id}}: Page loaded successfully for year {{year}}")
            
            # Select case type: {case_text}
            case_type_select = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'ddlCaseType'))
            )
            select = Select(case_type_select)
            select.select_by_value(self.case_type_value)
            time.sleep(2)  # Increased wait time
            print(f"✅ Worker {{worker_id}}: Case type selected for year {{year}}")
            
            # Select registry: {registry_name}
            registry_select = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
            )
            select = Select(registry_select)
            select.select_by_value('{registry_code}')
            time.sleep(2)  # Increased wait time
            print(f"✅ Worker {{worker_id}}: Registry selected for year {{year}}")
            
            # Select year
            year_select = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'ddlYear'))
            )
            select = Select(year_select)
            select.select_by_value(str(year))
            time.sleep(2)  # Increased wait time
            print(f"✅ Worker {{worker_id}}: Year {{year}} selected")
            
            # Click search button with enhanced error handling
            search_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'btnSearch'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(2)
            
            # Use JavaScript click and wait for results
            driver.execute_script("arguments[0].click();", search_button)
            print(f"🔍 Worker {{worker_id}}: Search button clicked for year {{year}}")
            
            # Wait for search results with longer timeout
            print(f"⏳ Worker {{worker_id}}: Waiting for search results for year {{year}}...")
            time.sleep(8)  # Increased wait time for search to complete
            
            # Check if search completed successfully by looking for results or "No Record Found"
            try:
                # Check for "No Record Found" message
                no_record_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'No Record Found')]")
                if no_record_elements:
                    print(f"ℹ️ Worker {{worker_id}}: No records found for year {{year}}")
                    return True  # Valid response, just no data
                
                # Check for results table or pagination
                results_found = (
                    driver.find_elements(By.XPATH, "//table") or
                    driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]") or
                    driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
                )
                
                if results_found:
                    print(f"✅ Worker {{worker_id}}: Search results loaded successfully for year {{year}}")
                    return True
                else:
                    print(f"⚠️ Worker {{worker_id}}: Unclear search state for year {{year}}, proceeding anyway")
                    return True  # Proceed optimistically
                    
            except Exception as check_error:
                print(f"⚠️ Worker {{worker_id}}: Error checking search results for year {{year}}: {{check_error}}")
                return True  # Proceed anyway
            
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Search failed for year {{year}} - {{e}}")
            return False
    
    def extract_detailed_case_info(self, driver, case_index, worker_id, page_num, year, year_range_name):
        """Extract detailed information from a specific case"""
        try:
            # Find all "View Details" links on current page
            view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Worker {{worker_id}}: Case index {{case_index}} out of range on page {{page_num}}")
                return None
            
            # Click on the specific "View Details" link
            target_link = view_details_links[case_index]
            original_window = driver.current_window_handle
            
            driver.execute_script("arguments[0].click();", target_link)
            time.sleep(2)
            
            # Switch to new window/tab
            windows = driver.window_handles
            if len(windows) > 1:
                driver.switch_to.window(windows[-1])
            
            # Extract case information
            case_data = {{}}
            
            try:
                # Extract case details from the details page
                case_data['extraction_date'] = datetime.now().isoformat()
                case_data['year'] = year
                case_data['page_number'] = page_num
                case_data['case_index'] = case_index
                case_data['worker_id'] = worker_id
                case_data['year_range'] = year_range_name
                case_data['case_type'] = "{case_text}"
                case_data['registry'] = "{registry_name}"
                
                # Try to extract case number, parties, etc.
                try:
                    case_data['case_number'] = driver.find_element(By.XPATH, "//span[@id='lblCaseNumber']").text.strip()
                except:
                    case_data['case_number'] = "Not found"
                
                try:
                    case_data['case_title'] = driver.find_element(By.XPATH, "//span[@id='lblCaseTitle']").text.strip()
                except:
                    case_data['case_title'] = "Not found"
                
                try:
                    case_data['date_of_filing'] = driver.find_element(By.XPATH, "//span[@id='lblDateOfFiling']").text.strip()
                except:
                    case_data['date_of_filing'] = "Not found"
                
                try:
                    case_data['date_of_hearing'] = driver.find_element(By.XPATH, "//span[@id='lblDateOfHearing']").text.strip()
                except:
                    case_data['date_of_hearing'] = "Not found"
                
                try:
                    case_data['status'] = driver.find_element(By.XPATH, "//span[@id='lblStatus']").text.strip()
                except:
                    case_data['status'] = "Not found"
                
                print(f"✅ Worker {{worker_id}}: Extracted case {{case_index+1}} from page {{page_num}} (Year {{year}})")
                
            except Exception as extract_error:
                print(f"❌ Worker {{worker_id}}: Error extracting details: {{extract_error}}")
                case_data = None
            
            # Close detail window and return to main window
            if len(windows) > 1:
                driver.close()
                driver.switch_to.window(original_window)
            
            # Save case data immediately (append mode)
            if case_data:
                self.save_case_data_append(case_data, year_range_name)
            
            return case_data
            
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Error processing case {{case_index}} on page {{page_num}}: {{e}}")
            return None
    
    def save_case_data_append(self, case_data, year_range_name):
        """Save case data in append mode to prevent data loss"""
        try:
            # Create filename
            filename = f"{registry_name}Cases_{{case_data['case_type'].replace('.', '')}}_{{year_range_name.replace('-', '_')}}_{{case_data['year']}}.json"
            filepath = self.data_dir / filename
            
            # Initialize JSON file if needed
            self.initialize_json_file(filepath, year_range_name)
            
            # Get or create lock for this file
            if str(filepath) not in self.json_locks:
                self.json_locks[str(filepath)] = threading.Lock()
            
            # Thread-safe append operation
            with self.json_locks[str(filepath)]:
                # Read existing data
                existing_data = []
                if filepath.exists() and filepath.stat().st_size > 0:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except:
                        existing_data = []
                
                # Check for duplicates (by case_number or unique identifier)
                case_id = f"{{case_data.get('case_number', 'unknown')}}_{{case_data.get('year', 'unknown')}}_{{case_data.get('page_number', 'unknown')}}_{{case_data.get('case_index', 'unknown')}}"
                
                # Check if this case already exists
                duplicate_found = False
                for existing_case in existing_data:
                    existing_id = f"{{existing_case.get('case_number', 'unknown')}}_{{existing_case.get('year', 'unknown')}}_{{existing_case.get('page_number', 'unknown')}}_{{existing_case.get('case_index', 'unknown')}}"
                    if existing_id == case_id:
                        duplicate_found = True
                        break
                
                if not duplicate_found:
                    # Append new case
                    existing_data.append(case_data)
                    
                    # Write back to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Saved case data to {{filepath}} (Total: {{len(existing_data)}} cases)")
                else:
                    print(f"⚠️ Duplicate case found, skipping: {{case_id}}")
            
        except Exception as e:
            print(f"❌ Error saving case data: {{e}}")
    
    def initialize_json_file(self, filepath, range_name):
        """Initialize JSON file with empty array if it doesn't exist"""
        try:
            if not filepath.exists():
                # Create directory if needed
                filepath.parent.mkdir(parents=True, exist_ok=True)
                
                # Create empty JSON array
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
                
                print(f"📄 Initialized JSON file: {{filepath}}")
                
                # Track active file
                self.active_json_files[range_name] = {{
                    'filepath': filepath,
                    'initialized': datetime.now().isoformat(),
                    'case_count': 0
                }}
            
        except Exception as e:
            print(f"❌ Error initializing JSON file {{filepath}}: {{e}}")
    
    def run_interactive_extraction(self):
        """Run the interactive extraction process"""
        print("\\n🚀 STARTING {registry_name.upper()} INTERACTIVE EXTRACTION")
        print("=" * 60)
        print(f"📋 Case Type: {case_text}")
        print(f"📅 Year Range: {range_name}")
        print(f"🏢 Registry: {registry_name}")
        print(f"🎯 Years to process: {{self.year_range}}")
        
        try:
            # Setup driver
            driver = self.setup_edge_driver()
            if not driver:
                print("❌ Failed to setup driver")
                return
            
            for year in self.year_range:
                print(f"\\n🔄 Processing year {{year}}...")
                
                # Navigate and search
                if not self.navigate_and_search(driver, "MAIN", year):
                    print(f"❌ Failed to search for year {{year}}")
                    continue
                
                # Process all pages for this year
                self.process_all_pages(driver, "MAIN", year)
            
            print("\\n✅ EXTRACTION COMPLETED!")
            
        except Exception as e:
            print(f"❌ Extraction failed: {{e}}")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def process_all_pages(self, driver, worker_id, year):
        """Process all pages of results for a given year"""
        try:
            page_num = 1
            while True:
                print(f"📄 Worker {{worker_id}}: Processing page {{page_num}} for year {{year}}")
                
                # Process cases on current page
                view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
                total_cases = len(view_details_links)
                
                if total_cases == 0:
                    print(f"ℹ️ Worker {{worker_id}}: No cases found on page {{page_num}}")
                    break
                
                print(f"📋 Worker {{worker_id}}: Found {{total_cases}} cases on page {{page_num}}")
                
                # Process each case on this page
                for case_index in range(total_cases):
                    self.extract_detailed_case_info(driver, case_index, worker_id, page_num, year, self.range_name)
                    time.sleep(1)  # Small delay between cases
                
                # Try to navigate to next page
                try:
                    next_page_link = driver.find_element(By.XPATH, f"//a[text()='{{page_num + 1}}']")
                    driver.execute_script("arguments[0].click();", next_page_link)
                    time.sleep(2)
                    page_num += 1
                except:
                    print(f"✅ Worker {{worker_id}}: No more pages for year {{year}}")
                    break
                    
        except Exception as e:
            print(f"❌ Worker {{worker_id}}: Error processing pages for year {{year}}: {{e}}")


def main():
    """Main function"""
    extractor = {registry_name}InteractiveExtractor()
    extractor.run_interactive_extraction()


if __name__ == "__main__":
    main()
'''
        
        # Write the script
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return True
    
    def create_all_extraction_scripts(self, registry_name):
        """Create extraction scripts for all case type-year range combinations for a registry"""
        print(f"\\n🔧 CREATING ALL {registry_name.upper()} EXTRACTION SCRIPTS")
        print("=" * 60)
        
        analysis_data = self.load_analysis_data(registry_name)
        case_types = analysis_data['case_types']
        year_ranges = analysis_data['year_ranges']
        
        total_scripts = 0
        
        for case_type in case_types:
            for year_range in year_ranges:
                try:
                    if self.create_extraction_script(registry_name, case_type, year_range):
                        total_scripts += 1
                except Exception as e:
                    print(f"❌ Failed to create script for {case_type['text']} - {year_range['name']}: {e}")
        
        print(f"\\n✅ {registry_name.upper()} EXTRACTION SCRIPTS CREATED!")
        print(f"   Total scripts created: {total_scripts}")
        print(f"   Expected scripts: {len(case_types) * len(year_ranges)}")
        
        return total_scripts
    
    def setup_all_registries(self):
        """Set up folder structures and scripts for all registries"""
        print("🚀 MULTI-REGISTRY SUPREME COURT STRUCTURE SETUP")
        print("=" * 60)
        print(f"📍 Setting up: {', '.join(self.registries.keys())}")
        
        total_scripts_created = 0
        
        for registry_name in self.registries.keys():
            try:
                print(f"\\n🔄 Processing {registry_name}...")
                
                # Create folder structure
                if self.create_folder_structure(registry_name):
                    print(f"✅ {registry_name} folder structure created!")
                
                # Create extraction scripts
                scripts_created = self.create_all_extraction_scripts(registry_name)
                total_scripts_created += scripts_created
                print(f"✅ {registry_name} scripts created: {scripts_created}")
                
            except Exception as e:
                print(f"❌ Failed to setup {registry_name}: {e}")
        
        print(f"\\n🎉 ALL REGISTRIES SETUP COMPLETE!")
        print("=" * 60)
        print(f"📁 Structures created for: {', '.join(self.registries.keys())}")
        print(f"📋 35 case types × 10 year ranges × {len(self.registries)} registries")
        print(f"🔧 Total extraction scripts created: {total_scripts_created}")
        print(f"\\n🚀 Ready for systematic case extraction across all registries!")


def main():
    """Main function"""
    manager = MultiRegistryStructureManager()
    manager.setup_all_registries()


if __name__ == "__main__":
    main()