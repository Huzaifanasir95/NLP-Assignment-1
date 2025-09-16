"""
Analyzer to discover all available case types and years for Lahore registry
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def create_driver():
    """Create optimized Chrome WebDriver"""
    options = Options()
    # Don't use headless for debugging
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-logging')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    return driver


def analyze_website_options():
    """Analyze available case types and years"""
    driver = None
    try:
        print("🔍 Analyzing Supreme Court website options...")
        driver = create_driver()
        
        # Navigate to the website
        url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        driver.get(url)
        time.sleep(3)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ddlCaseType"))
        )
        
        # Get case types
        print("\n📋 Available Case Types:")
        case_type_select = driver.find_element(By.ID, 'ddlCaseType')
        case_type_options = case_type_select.find_elements(By.TAG_NAME, 'option')
        
        case_types = []
        for option in case_type_options:
            value = option.get_attribute('value')
            text = option.text.strip()
            if value and value != '0':  # Skip default/empty options
                case_types.append({'value': value, 'text': text})
                print(f"   {value}: {text}")
        
        # Select Lahore registry to get years
        registry_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
        )
        select = Select(registry_select)
        select.select_by_value('L')  # Lahore
        time.sleep(1)
        
        # Get available years
        print("\n📅 Available Years:")
        year_select = driver.find_element(By.ID, 'ddlYear')
        year_options = year_select.find_elements(By.TAG_NAME, 'option')
        
        years = []
        for option in year_options:
            value = option.get_attribute('value')
            text = option.text.strip()
            if value and value != '0':  # Skip default/empty options
                years.append({'value': value, 'text': text})
                print(f"   {value}: {text}")
        
        print(f"\n✅ Analysis Complete:")
        print(f"   Total Case Types: {len(case_types)}")
        print(f"   Total Years: {len(years)}")
        print(f"   Estimated Total Combinations: {len(case_types) * len(years)}")
        
        return case_types, years
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return [], []
    
    finally:
        if driver:
            driver.quit()


def main():
    """Main analysis function"""
    print("🚀 SUPREME COURT LAHORE REGISTRY OPTIONS ANALYZER")
    print("=" * 60)
    
    case_types, years = analyze_website_options()
    
    if case_types and years:
        # Save results for reference
        results = {
            'case_types': case_types,
            'years': years,
            'total_combinations': len(case_types) * len(years)
        }
        
        import json
        with open('lahore_available_options.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to lahore_available_options.json")
        
        # Show strategic recommendations
        print(f"\n🎯 EXTRACTION STRATEGY RECOMMENDATIONS:")
        print(f"   • Use batch processing for {len(case_types)} case types")
        print(f"   • Process {len(years)} years with parallel workers")
        print(f"   • Implement pagination for each case type-year combination")
        print(f"   • Estimate total processing time: {len(case_types) * len(years) * 2} minutes")
        print(f"   • Use 4-6 parallel workers for optimal performance")
        
    else:
        print("\n❌ Failed to analyze website options")


if __name__ == "__main__":
    main()