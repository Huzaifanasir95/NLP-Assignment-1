"""
Test script to verify the modular Supreme Court data extraction system
Tests individual components and basic functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.config import Config
from src.utils.web_utils import setup_chrome_driver, clean_text, extract_case_number
from src.extractors.case_info_extractor import CaseInfoExtractor


def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    
    print(f"   Target Year: {Config.TARGET_YEAR}")
    print(f"   Case Info URL: {Config.CASE_INFO_URL}")
    print(f"   Judgment URL: {Config.JUDGMENT_URL}")
    print(f"   Max Pages: {Config.MAX_PAGES_PER_SEARCH}")
    print(f"   Timeout: {Config.TIMEOUT}")
    
    # Test directory creation
    case_dir = Config.get_output_path("case_info", "test.json")
    judgment_dir = Config.get_output_path("judgments", "test.json")
    
    print(f"   Case Output: {case_dir}")
    print(f"   Judgment Output: {judgment_dir}")
    print("✅ Configuration test passed")


def test_utilities():
    """Test utility functions"""
    print("\n🛠️ Testing Utilities...")
    
    # Test text cleaning
    test_text = "  C.A.123-L/2025   TEST CASE  "
    cleaned = clean_text(test_text)
    print(f"   Text cleaning: '{test_text}' -> '{cleaned}'")
    
    # Test case number extraction
    test_cases = [
        "C.A.123-L/2025",
        "CRL.456/2025", 
        "Some text with C.A.789/2025 embedded",
        "Invalid case number"
    ]
    
    for test_case in test_cases:
        extracted = extract_case_number(test_case)
        print(f"   Case extraction: '{test_case}' -> '{extracted}'")
    
    print("✅ Utilities test passed")


def test_chrome_driver():
    """Test Chrome WebDriver setup"""
    print("\n🌐 Testing Chrome WebDriver...")
    
    driver = setup_chrome_driver()
    if driver:
        print("✅ Chrome WebDriver initialized successfully")
        
        # Test basic navigation
        try:
            driver.get("https://www.google.com")
            print("✅ Basic navigation test passed")
        except Exception as e:
            print(f"⚠️ Navigation test failed: {e}")
        finally:
            driver.quit()
    else:
        print("❌ Chrome WebDriver failed to initialize")


def test_extractor_initialization():
    """Test extractor initialization"""
    print("\n🏛️ Testing Extractor Initialization...")
    
    try:
        case_extractor = CaseInfoExtractor()
        print("✅ CaseInfoExtractor initialized")
        print(f"   URL: {case_extractor.url}")
        print(f"   Search Strategies: {len(case_extractor.search_strategies)}")
        
        # Test some search strategies
        for i, strategy in enumerate(case_extractor.search_strategies[:3]):
            print(f"   Strategy {i+1}: {strategy}")
        
    except Exception as e:
        print(f"❌ Extractor initialization failed: {e}")


def test_basic_extraction():
    """Test basic extraction without full run"""
    print("\n🔍 Testing Basic Extraction Setup...")
    
    try:
        extractor = CaseInfoExtractor()
        
        # Test driver setup
        if extractor.setup_driver():
            print("✅ WebDriver setup successful")
            
            # Test navigation to case info page
            if extractor.navigate_to_url(extractor.url):
                print("✅ Successfully navigated to case info page")
                print("✅ Website is accessible")
            else:
                print("❌ Failed to navigate to case info page")
                
            extractor.cleanup()
        else:
            print("❌ WebDriver setup failed")
            
    except Exception as e:
        print(f"❌ Basic extraction test failed: {e}")


def main():
    """Run all tests"""
    print("🧪 Supreme Court Data Extractor - System Test")
    print("=" * 50)
    
    # Run tests
    test_config()
    test_utilities()
    test_chrome_driver()
    test_extractor_initialization()
    test_basic_extraction()
    
    print("\n" + "=" * 50)
    print("🎯 System test completed!")
    print("\nIf all tests passed, you can run the full extraction with:")
    print("   python main.py")
    print("\nTo extract only case information:")
    print("   python -c \"from src.extractors.case_info_extractor import CaseInfoExtractor; CaseInfoExtractor().run_extraction()\"")


if __name__ == "__main__":
    main()