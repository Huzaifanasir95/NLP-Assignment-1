"""
Website Structure Inspector
Downloads and analyzes the Supreme Court website structure
"""

import requests
import ssl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_website_structure():
    """Download website HTML using requests"""
    print("🌐 Downloading website structure...")
    
    try:
        # Configure requests to handle SSL issues
        session = requests.Session()
        session.verify = False
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            with open("website_structure.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ Website structure downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading website: {e}")
        return False

def analyze_form_elements():
    """Analyze form elements in the downloaded HTML"""
    print("\n📋 Analyzing form elements...")
    
    try:
        with open("website_structure.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all form elements
        forms = soup.find_all('form')
        print(f"   Found {len(forms)} forms")
        
        # Find all select dropdowns
        selects = soup.find_all('select')
        print(f"   Found {len(selects)} select elements:")
        for select in selects:
            select_id = select.get('id', 'No ID')
            select_name = select.get('name', 'No Name')
            options = select.find_all('option')
            print(f"     - ID: {select_id}, Name: {select_name}, Options: {len(options)}")
            
            # Show first few options
            for i, option in enumerate(options[:5]):
                option_text = option.get_text(strip=True)
                option_value = option.get('value', '')
                print(f"       Option {i+1}: '{option_text}' (value: '{option_value}')")
        
        # Find all input elements
        inputs = soup.find_all('input')
        print(f"\n   Found {len(inputs)} input elements:")
        for input_elem in inputs:
            input_id = input_elem.get('id', 'No ID')
            input_name = input_elem.get('name', 'No Name')
            input_type = input_elem.get('type', 'No Type')
            input_value = input_elem.get('value', 'No Value')
            print(f"     - ID: {input_id}, Name: {input_name}, Type: {input_type}, Value: {input_value}")
        
        # Find all buttons
        buttons = soup.find_all(['button', 'input[type="submit"]'])
        print(f"\n   Found {len(buttons)} buttons:")
        for button in buttons:
            button_id = button.get('id', 'No ID')
            button_text = button.get_text(strip=True) or button.get('value', 'No Text')
            print(f"     - ID: {button_id}, Text: '{button_text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing HTML: {e}")
        return False

def inspect_with_selenium():
    """Use Selenium to inspect the live website"""
    print("\n🔍 Inspecting website with Selenium...")
    
    try:
        # Setup Chrome options
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        
        print("   Navigating to website...")
        driver.get("https://scp.gov.pk/OnlineCaseInformation.aspx")
        time.sleep(5)
        
        print("   Analyzing page elements...")
        
        # Get page source and save it
        page_source = driver.page_source
        with open("selenium_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        
        # Find all select elements
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"   Found {len(selects)} select elements:")
        
        for i, select in enumerate(selects):
            try:
                select_id = select.get_attribute("id")
                select_name = select.get_attribute("name")
                options = select.find_elements(By.TAG_NAME, "option")
                print(f"     Select {i+1}: ID='{select_id}', Name='{select_name}', Options={len(options)}")
                
                # Show options
                for j, option in enumerate(options[:5]):
                    option_text = option.text
                    option_value = option.get_attribute("value")
                    print(f"       Option {j+1}: '{option_text}' (value: '{option_value}')")
                    
            except Exception as e:
                print(f"       Error reading select {i+1}: {e}")
        
        # Find all input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n   Found {len(inputs)} input elements:")
        
        for i, input_elem in enumerate(inputs):
            try:
                input_id = input_elem.get_attribute("id")
                input_name = input_elem.get_attribute("name")
                input_type = input_elem.get_attribute("type")
                input_value = input_elem.get_attribute("value")
                print(f"     Input {i+1}: ID='{input_id}', Name='{input_name}', Type='{input_type}', Value='{input_value}'")
            except Exception as e:
                print(f"       Error reading input {i+1}: {e}")
        
        driver.quit()
        print("✅ Selenium inspection completed")
        return True
        
    except Exception as e:
        print(f"❌ Selenium inspection failed: {e}")
        if 'driver' in locals():
            driver.quit()
        return False

def extract_sample_data():
    """Extract a small sample of data to test the extraction"""
    print("\n🧪 Testing sample data extraction...")
    
    try:
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        
        print("   Navigating to website...")
        driver.get("https://scp.gov.pk/OnlineCaseInformation.aspx")
        time.sleep(10)  # Wait longer for page to load
        
        # Try to find any form elements by different methods
        print("   Looking for form elements...")
        
        # Method 1: By tag name
        all_selects = driver.find_elements(By.TAG_NAME, "select")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        
        print(f"   Found: {len(all_selects)} selects, {len(all_inputs)} inputs, {len(all_buttons)} buttons")
        
        # Method 2: By partial text
        case_type_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Case Type') or contains(text(), 'case type')]")
        registry_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Registry') or contains(text(), 'registry')]")
        year_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Year') or contains(text(), 'year')]")
        
        print(f"   Text search: {len(case_type_elements)} case type, {len(registry_elements)} registry, {len(year_elements)} year")
        
        # Method 3: Look for any dropdown that might contain 2025
        all_elements = driver.find_elements(By.XPATH, "//*")
        elements_with_2025 = []
        
        for element in all_elements:
            try:
                if "2025" in element.text:
                    elements_with_2025.append(element)
            except:
                pass
        
        print(f"   Found {len(elements_with_2025)} elements containing '2025'")
        
        # Try to find the results table
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"   Found {len(tables)} tables")
        
        if tables:
            print("   Analyzing first table...")
            first_table = tables[0]
            rows = first_table.find_elements(By.TAG_NAME, "tr")
            print(f"     Table has {len(rows)} rows")
            
            if len(rows) > 1:
                # Check first few rows
                for i, row in enumerate(rows[:3]):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_text = " | ".join([cell.text[:50] for cell in cells])
                        print(f"     Row {i+1}: {row_text}")
        
        # Save page source for manual inspection
        page_source = driver.page_source
        with open("current_page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        
        driver.quit()
        print("✅ Sample extraction test completed")
        return True
        
    except Exception as e:
        print(f"❌ Sample extraction failed: {e}")
        if 'driver' in locals():
            driver.quit()
        return False

def main():
    """Main function to run all inspections"""
    print("🔍 Supreme Court Website Structure Inspector")
    print("=" * 50)
    
    # Step 1: Download static HTML
    if download_website_structure():
        analyze_form_elements()
    
    # Step 2: Inspect with Selenium
    inspect_with_selenium()
    
    # Step 3: Test sample extraction
    extract_sample_data()
    
    print("\n" + "=" * 50)
    print("🎯 Inspection completed!")
    print("Check the following files:")
    print("   - website_structure.html (static HTML)")
    print("   - selenium_source.html (Selenium rendered HTML)")
    print("   - current_page_source.html (Current page state)")

if __name__ == "__main__":
    main()