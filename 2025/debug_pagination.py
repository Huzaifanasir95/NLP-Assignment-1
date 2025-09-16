"""
Debug script to examine pagination structure for C.A. Lahore 2025
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def create_driver():
    """Create Chrome WebDriver"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    
    return driver


def examine_pagination():
    """Examine pagination structure for C.A. Lahore 2025"""
    driver = create_driver()
    
    try:
        # Navigate to website
        url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Search for C.A. Lahore 2025
        # Select case type: C.A.
        case_type_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ddlCaseType'))
        )
        select = Select(case_type_select)
        select.select_by_value('1')  # C.A.
        time.sleep(1)
        
        # Select registry: Lahore
        registry_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
        )
        select = Select(registry_select)
        select.select_by_value('L')  # Lahore
        time.sleep(1)
        
        # Select year: 2025
        year_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ddlYear'))
        )
        select = Select(year_select)
        select.select_by_value('2025')
        time.sleep(1)
        
        # Click search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'btnSearch'))
        )
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(5)
        
        print("🔍 Search completed, examining pagination...")
        
        # Examine current page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find pagination controls
        print(f"\n📄 PAGINATION ANALYSIS:")
        
        # Look for pagination links
        page_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
        print(f"📋 Found {len(page_links)} page links:")
        
        for i, link in enumerate(page_links):
            try:
                link_text = link.text.strip()
                href = link.get_attribute('href')
                print(f"   {i+1}. Text: '{link_text}' | Href: {href}")
            except:
                print(f"   {i+1}. Link could not be read")
        
        # Look for page numbers specifically
        page_numbers = driver.find_elements(By.XPATH, "//a[text()='2' or text()='3' or text()='4' or text()='5' or text()='6']")
        print(f"\n🔢 Page number links found: {len(page_numbers)}")
        for i, page_num in enumerate(page_numbers):
            try:
                text = page_num.text.strip()
                href = page_num.get_attribute('href')
                print(f"   Page {text}: {href}")
            except:
                print(f"   Page link {i+1} could not be read")
        
        # Count current page cases
        view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
        print(f"\n📊 Current page (Page 1) has {len(view_details_links)} cases")
        
        # Test navigation to page 2
        try:
            print(f"\n🔄 Testing navigation to Page 2...")
            page_2_link = driver.find_element(By.XPATH, "//a[text()='2']")
            driver.execute_script("arguments[0].click();", page_2_link)
            time.sleep(3)
            
            # Count cases on page 2
            view_details_links_p2 = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            print(f"✅ Page 2 has {len(view_details_links_p2)} cases")
            
            # Check if page 2 has different pagination
            page_links_p2 = driver.find_elements(By.XPATH, "//a[contains(@href, 'Page$')]")
            print(f"📋 Page 2 pagination links: {len(page_links_p2)}")
            
        except Exception as e:
            print(f"❌ Could not navigate to page 2: {e}")
        
        # Save page source for analysis
        with open("pagination_analysis.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"\n💾 Page source saved to pagination_analysis.html")
        
        print(f"\n✅ Pagination analysis completed")
        
    except Exception as e:
        print(f"❌ Error during pagination analysis: {e}")
    
    finally:
        driver.quit()


if __name__ == "__main__":
    examine_pagination()