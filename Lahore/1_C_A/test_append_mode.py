"""
Test script to demonstrate the append mode functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ca_lahore_interactive_extractor import CALahoreInteractiveExtractor

def test_append_mode():
    """Test the append mode functionality"""
    print("🧪 Testing Append Mode with Duplicate Prevention")
    print("=" * 60)
    
    # Create extractor instance
    extractor = CALahoreInteractiveExtractor(max_workers=1)
    
    # Test range
    test_range = "test-2020"
    
    # Step 1: Initialize JSON file (first time)
    print("\n📝 Step 1: Initialize JSON file (first time)")
    result = extractor.initialize_json_file(test_range)
    if result:
        print(f"✅ JSON file initialized: {result}")
    
    # Step 2: Add some test cases
    print("\n📝 Step 2: Add some test cases")
    test_cases = [
        {
            "Case_No": "C.A. 123/2020",
            "Title": "Test Case 1",
            "Date_of_Order": "2020-01-15",
            "Judge": "Test Judge 1",
            "Judgment_PDF": "test1.pdf",
            "Memo_PDF": "N/A"
        },
        {
            "Case_No": "C.A. 124/2020",
            "Title": "Test Case 2",
            "Date_of_Order": "2020-01-16",
            "Judge": "Test Judge 2",
            "Judgment_PDF": "test2.pdf",
            "Memo_PDF": "test2_memo.pdf"
        }
    ]
    
    for case in test_cases:
        success = extractor.write_case_incrementally(case, test_range)
        if success:
            print(f"✅ Added case: {case['Case_No']}")
        else:
            print(f"❌ Failed to add case: {case['Case_No']}")
    
    # Step 3: Finalize the JSON file
    print("\n📝 Step 3: Finalize JSON file")
    extractor.finalize_json_file(test_range)
    
    # Step 4: Re-initialize in append mode (should read existing cases)
    print("\n📝 Step 4: Re-initialize in append mode")
    result = extractor.initialize_json_file(test_range)
    if result:
        print(f"✅ JSON file re-initialized for append: {result}")
    
    # Step 5: Try to add duplicate case (should be skipped)
    print("\n📝 Step 5: Try to add duplicate case (should be skipped)")
    duplicate_case = {
        "Case_No": "C.A. 123/2020",  # This is a duplicate
        "Title": "Duplicate Test Case",
        "Date_of_Order": "2020-01-15",
        "Judge": "Test Judge 1",
        "Judgment_PDF": "duplicate.pdf",
        "Memo_PDF": "N/A"
    }
    
    success = extractor.write_case_incrementally(duplicate_case, test_range)
    if not success:
        print(f"✅ Duplicate correctly rejected: {duplicate_case['Case_No']}")
    else:
        print(f"❌ Duplicate was incorrectly added: {duplicate_case['Case_No']}")
    
    # Step 6: Add new unique case (should be added)
    print("\n📝 Step 6: Add new unique case (should be added)")
    new_case = {
        "Case_No": "C.A. 125/2020",  # This is new
        "Title": "New Test Case 3",
        "Date_of_Order": "2020-01-17",
        "Judge": "Test Judge 3",
        "Judgment_PDF": "test3.pdf",
        "Memo_PDF": "N/A"
    }
    
    success = extractor.write_case_incrementally(new_case, test_range)
    if success:
        print(f"✅ New case correctly added: {new_case['Case_No']}")
    else:
        print(f"❌ New case was incorrectly rejected: {new_case['Case_No']}")
    
    # Step 7: Finalize again
    print("\n📝 Step 7: Finalize JSON file again")
    extractor.finalize_json_file(test_range)
    
    # Step 8: Show final result
    print("\n📝 Step 8: Final JSON file content")
    try:
        json_file = f"{test_range.replace('-', '_')}/CA_Lahore_{test_range.replace('-', '_')}_complete.json"
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📄 Final JSON content ({len(content)} characters):")
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print(f"❌ JSON file not found: {json_file}")
    except Exception as e:
        print(f"❌ Error reading final JSON: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Append mode test completed!")

if __name__ == "__main__":
    test_append_mode()