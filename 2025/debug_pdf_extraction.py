"""
Debug script to examine PDF link structure for C.A.66-L/2025
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


def debug_case_66():
    """Debug C.A.66-L/2025 case specifically"""
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
        
        print("🔍 Search completed, looking for C.A.66-L/2025...")
        
        # Find all View Details links
        view_details_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
        print(f"📋 Found {len(view_details_links)} cases")
        
        # Look for C.A.66-L/2025 specifically
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the case row
        case_found = False
        for i, link in enumerate(view_details_links):
            # Get the row containing this link to check case number
            row = link.find_element(By.XPATH, "./ancestor::tr")
            row_text = row.text
            
            if "C.A.66-L/2025" in row_text:
                print(f"🎯 Found C.A.66-L/2025 at index {i}")
                print(f"Row text preview: {row_text[:200]}...")
                
                # Click View Details for this case
                driver.execute_script("arguments[0].scrollIntoView(true);", link)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", link)
                time.sleep(3)
                
                case_found = True
                break
        
        if not case_found:
            print("❌ C.A.66-L/2025 not found in current results")
            return
        
        # Now examine the detailed page for PDF links
        print("🔍 Examining detailed page for PDF links...")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        print(f"\n📄 ALL LINKS FOUND ({len(all_links)}):")
        for i, link in enumerate(all_links):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            print(f"  {i+1}. Text: '{text}' | Href: '{href}'")
            
            # Check for PDF indicators
            if any(keyword in text.lower() for keyword in ['digital', 'copy', 'file', 'pdf', 'memo', 'petition', 'appeal']):
                print(f"      ⭐ POTENTIAL PDF LINK!")
        
        # Look for specific sections
        print(f"\n📋 PETITION/APPEAL MEMO SECTION:")
        petition_text = soup.get_text()
        if "Petition/Appeal Memo:" in petition_text:
            # Find the section after "Petition/Appeal Memo:"
            lines = petition_text.split('\n')
            memo_section = False
            for line in lines:
                if "Petition/Appeal Memo:" in line:
                    memo_section = True
                    continue
                if memo_section:
                    if line.strip() and not line.startswith('History'):
                        print(f"  {line.strip()}")
                        if 'Digital Copy' in line:
                            print(f"      ⭐ FOUND DIGITAL COPY REFERENCE!")
                    else:
                        break
        
        # Save page source for detailed analysis
        with open("debug_case_66_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"\n💾 Page source saved to debug_case_66_page_source.html")
        
        print(f"\n✅ Debug completed for C.A.66-L/2025")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
    
    finally:
        driver.quit()


if __name__ == "__main__":
    debug_case_66()