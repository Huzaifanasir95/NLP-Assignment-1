"""
Test script for Comprehensive Lahore Extractor
Tests with a small sample to validate the system before full extraction
"""

import json
import sys
import os

# Import our main extractor
from lahore_comprehensive_extractor import ComprehensiveLahoreExtractor


def test_small_sample():
    """Test with a small sample of case types and years"""
    print("🧪 TESTING COMPREHENSIVE LAHORE EXTRACTOR")
    print("=" * 60)
    
    # Load available options
    try:
        with open('lahore_available_options.json', 'r', encoding='utf-8') as f:
            options_data = json.load(f)
    except FileNotFoundError:
        print("❌ Please run analyze_available_options.py first")
        return False
    
    # Select test sample
    test_case_types = [
        {'value': '1', 'text': 'C.A.'},      # Civil Appeals  
        {'value': '2', 'text': 'Crl.A.'}     # Criminal Appeals
    ]
    
    test_years = [
        {'value': '2025', 'text': '2025'},
        {'value': '2024', 'text': '2024'}
    ]
    
    print(f"\n📋 TEST SAMPLE:")
    print(f"   Case Types: {[ct['text'] for ct in test_case_types]}")
    print(f"   Years: {[y['text'] for y in test_years]}")
    print(f"   Total Combinations: {len(test_case_types) * len(test_years)}")
    
    # Create test extractor
    extractor = ComprehensiveLahoreExtractor(
        max_workers=2,  # Reduced workers for testing
        case_types_to_extract=test_case_types,
        years_to_extract=test_years
    )
    
    # Run test extraction
    print(f"\n🚀 Starting test extraction...")
    
    if extractor.run_comprehensive_extraction():
        # Save test results
        extractor.save_master_results("lahore_test_results.json")
        
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY!")
        print(f"   Total cases extracted: {len(extractor.extracted_cases)}")
        print(f"   Test results: lahore_test_results.json")
        print(f"   Individual files: results/")
        
        # Show sample results
        if extractor.extracted_cases:
            print(f"\n📄 SAMPLE CASES:")
            for i, case in enumerate(extractor.extracted_cases[:3]):
                print(f"   {i+1}. {case.get('Case_Number', 'N/A')} - {case.get('Case_Type', 'N/A')} {case.get('Year', 'N/A')}")
                print(f"      Title: {case.get('Case_Title', 'N/A')[:60]}...")
                memo_pdf = case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', 'N/A')
                judgment_pdf = case.get('Judgement_Order', {}).get('Downloaded_Path', 'N/A')
                print(f"      Memo PDF: {'✅' if 'PDF Link Available' in memo_pdf else '❌'}")
                print(f"      Judgment PDF: {'✅' if 'PDF Link Available' in judgment_pdf else '❌'}")
                print()
        
        return True
    else:
        print(f"\n❌ TEST FAILED")
        return False


def main():
    """Main test function"""
    success = test_small_sample()
    
    if success:
        print(f"\n🎯 TEST VALIDATION COMPLETE!")
        print(f"   ✅ System is working correctly")
        print(f"   ✅ Ready for full-scale extraction")
        print(f"\n💡 To run full extraction:")
        print(f"   python lahore_comprehensive_extractor.py")
    else:
        print(f"\n❌ SYSTEM NEEDS DEBUGGING")
        print(f"   Check logs and fix issues before full extraction")


if __name__ == "__main__":
    main()