"""
Simple script to analyze available case types and years for Lahore registry
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import json


def create_driver():
    """Create optimized Chrome WebDriver"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    return driver


def get_available_options():
    """Get available case types and years"""
    driver = None
    try:
        print("🔍 Analyzing Supreme Court website options...")
        driver = create_driver()
        
        url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
        driver.get(url)
        time.sleep(3)
        
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
            if value and value != '0':
                case_types.append({'value': value, 'text': text})
                print(f"   {value}: {text}")
        
        # Select Lahore registry
        registry_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ddlRegistry'))
        )
        select = Select(registry_select)
        select.select_by_value('L')
        time.sleep(1)
        
        # Get available years
        print("\n📅 Available Years:")
        year_select = driver.find_element(By.ID, 'ddlYear')
        year_options = year_select.find_elements(By.TAG_NAME, 'option')
        
        years = []
        for option in year_options:
            value = option.get_attribute('value')
            text = option.text.strip()
            if value and value != '0':
                years.append({'value': value, 'text': text})
                print(f"   {value}: {text}")
        
        print(f"\n✅ Analysis Complete:")
        print(f"   Total Case Types: {len(case_types)}")
        print(f"   Total Years: {len(years)}")
        print(f"   Total Combinations: {len(case_types) * len(years)}")
        
        return case_types, years
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return [], []
    
    finally:
        if driver:
            driver.quit()


def create_year_ranges(years, gap=5):
    """Create year ranges with specified gap"""
    if not years:
        return []
    
    # Sort years numerically
    year_values = sorted([int(year['value']) for year in years])
    
    ranges = []
    start_year = year_values[0]
    
    for i in range(0, len(year_values), gap):
        end_idx = min(i + gap - 1, len(year_values) - 1)
        end_year = year_values[end_idx]
        
        range_name = f"{start_year}-{end_year}" if start_year != end_year else str(start_year)
        range_years = year_values[i:end_idx + 1]
        
        ranges.append({
            'name': range_name,
            'start_year': start_year,
            'end_year': end_year,
            'years': range_years
        })
        
        if end_idx < len(year_values) - 1:
            start_year = year_values[end_idx + 1]
    
    return ranges


def main():
    """Main function"""
    print("🚀 LAHORE REGISTRY OPTIONS ANALYZER")
    print("=" * 50)
    
    case_types, years = get_available_options()
    
    if case_types and years:
        # Create year ranges (5-year gaps)
        year_ranges = create_year_ranges(years, gap=5)
        
        print(f"\n📊 PROPOSED FOLDER STRUCTURE:")
        print(f"   Year Ranges (5-year gaps): {len(year_ranges)}")
        
        for range_info in year_ranges:
            print(f"   📁 {range_info['name']}: {len(range_info['years'])} years")
        
        # Save analysis results
        analysis = {
            'case_types': case_types,
            'years': years,
            'year_ranges': year_ranges,
            'total_combinations': len(case_types) * len(year_ranges),
            'structure_plan': {
                'case_type_folders': len(case_types),
                'year_range_folders_per_case_type': len(year_ranges),
                'total_extraction_folders': len(case_types) * len(year_ranges)
            }
        }
        
        with open('lahore_structure_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 EXTRACTION STRATEGY:")
        print(f"   • {len(case_types)} case type folders")
        print(f"   • {len(year_ranges)} year range folders per case type")
        print(f"   • {len(case_types) * len(year_ranges)} total extraction folders")
        print(f"   • Each folder will have its own extraction script")
        print(f"   • Organized JSON and PDF storage per folder")
        
        print(f"\n💾 Analysis saved to lahore_structure_analysis.json")
        
    else:
        print("\n❌ Failed to analyze website options")


if __name__ == "__main__":
    main()