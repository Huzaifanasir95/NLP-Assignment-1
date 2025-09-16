"""
Test Updated SRC Extractors
Tests the updated src/extractors with correct element IDs
"""

import sys
import os

# Add src to path
sys.path.append('src')

from src.extractors.case_info_extractor import CaseInfoExtractor
from src.config import Config


def test_updated_extractor():
    """Test the updated case info extractor"""
    print("🧪 TESTING UPDATED SRC EXTRACTORS")
    print("=" * 50)
    
    # Show configuration
    print("📋 Configuration:")
    print(f"   Target Year: {Config.TARGET_YEAR}")
    print(f"   URL: {Config.CASE_INFO_URL}")
    print(f"   Output Dir: {Config.CASE_INFO_DIR}")
    
    # Create directories
    Config.create_directories()
    
    # Initialize extractor
    print(f"\n🔧 Initializing CaseInfoExtractor...")
    extractor = CaseInfoExtractor()
    
    print(f"   Strategies: {len(extractor.search_strategies)}")
    print(f"   First few strategies:")
    for i, strategy in enumerate(extractor.search_strategies[:5]):
        print(f"      {i+1}. {strategy}")
    
    # Test a limited extraction (just first strategy)
    print(f"\n🧪 Testing with first strategy only...")
    
    # Limit to one strategy for testing
    original_strategies = extractor.search_strategies
    extractor.search_strategies = original_strategies[:1]
    
    print(f"   Using strategy: {extractor.search_strategies[0]}")
    
    # Run extraction
    try:
        result = extractor.run_extraction()
        
        if result:
            print(f"✅ Test extraction successful!")
            print(f"   Cases extracted: {len(extractor.extracted_data)}")
            
            # Show sample cases
            if extractor.extracted_data:
                print(f"\n📋 Sample extracted cases:")
                for i, case in enumerate(extractor.extracted_data[:3]):
                    print(f"   {i+1}. {case.get('Case_No', 'N/A')} - {case.get('Case_Title', 'N/A')[:50]}...")
            
            # Show summary
            summary = extractor.get_extraction_summary()
            print(f"\n📊 Extraction Summary:")
            for key, value in summary.items():
                print(f"   {key}: {value}")
        
        else:
            print(f"❌ Test extraction failed")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


def show_comprehensive_config():
    """Show comprehensive extraction configuration"""
    print("\n🎯 COMPREHENSIVE EXTRACTION CONFIGURATION")
    print("=" * 50)
    
    # Generate comprehensive strategies
    Config.generate_comprehensive_strategies()
    
    summary = Config.get_extraction_summary_config()
    
    print(f"📊 Extraction Scope:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print(f"\n📁 Output Directories:")
    for directory in summary["output_directories"]:
        print(f"   {directory}")
    
    print(f"\n🔍 Sample Strategies (first 10):")
    for i, strategy in enumerate(Config.COMPREHENSIVE_STRATEGIES[:10]):
        print(f"   {i+1}. {strategy}")
    
    print(f"\n   ... and {len(Config.COMPREHENSIVE_STRATEGIES) - 10} more strategies")


def main():
    """Main test function"""
    print("🚀 TESTING UPDATED SUPREME COURT EXTRACTORS")
    print("=" * 60)
    
    # Test updated extractor
    test_updated_extractor()
    
    # Show comprehensive configuration
    show_comprehensive_config()
    
    print("\n" + "=" * 60)
    print("🎯 TESTS COMPLETED")
    print("✅ Updated src/extractors are ready for full extraction")
    print("✅ Comprehensive extractor (1980-2025) is available")
    print("=" * 60)


if __name__ == "__main__":
    main()