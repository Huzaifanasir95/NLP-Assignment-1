"""
Main execution script for Supreme Court data extraction
Extracts 2025 case information and judgments with pagination support
"""

import sys
import time
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from src.extractors.case_info_extractor import CaseInfoExtractor
from src.extractors.judgment_extractor import JudgmentExtractor
from src.config import Config


def main():
    """Main execution function"""
    print("🏛️ Supreme Court of Pakistan Data Extractor")
    print("=" * 50)
    print(f"Target Year: {Config.TARGET_YEAR}")
    print(f"Max Pages per Search: {Config.MAX_PAGES_PER_SEARCH}")
    print("=" * 50)
    
    extraction_summary = {
        "case_info": {"extracted": 0, "success": False},
        "judgments": {"extracted": 0, "success": False}
    }
    
    # Extract Case Information
    print("\n🔍 Starting Case Information Extraction...")
    try:
        case_extractor = CaseInfoExtractor()
        case_success = case_extractor.run_extraction()
        
        extraction_summary["case_info"]["success"] = case_success
        extraction_summary["case_info"]["extracted"] = len(case_extractor.extracted_data)
        
        if case_success:
            print(f"✅ Case extraction completed: {len(case_extractor.extracted_data)} cases")
        else:
            print("❌ Case extraction failed")
            
    except Exception as e:
        print(f"❌ Case extraction error: {e}")
    
    # Wait between extractions
    print(f"\n⏳ Waiting {Config.DELAY_BETWEEN_EXTRACTIONS}s before next extraction...")
    time.sleep(Config.DELAY_BETWEEN_EXTRACTIONS)
    
    # Extract Judgments
    print("\n📋 Starting Judgment Extraction...")
    try:
        judgment_extractor = JudgmentExtractor()
        judgment_success = judgment_extractor.run_extraction()
        
        extraction_summary["judgments"]["success"] = judgment_success
        extraction_summary["judgments"]["extracted"] = len(judgment_extractor.extracted_data)
        
        if judgment_success:
            print(f"✅ Judgment extraction completed: {len(judgment_extractor.extracted_data)} judgments")
        else:
            print("❌ Judgment extraction failed")
            
    except Exception as e:
        print(f"❌ Judgment extraction error: {e}")
    
    # Print final summary
    print("\n" + "=" * 50)
    print("📊 FINAL EXTRACTION SUMMARY")
    print("=" * 50)
    
    total_extracted = 0
    for extraction_type, results in extraction_summary.items():
        status = "✅ SUCCESS" if results["success"] else "❌ FAILED"
        count = results["extracted"]
        total_extracted += count
        print(f"{extraction_type.upper()}: {status} - {count} records")
    
    print(f"\nTOTAL RECORDS EXTRACTED: {total_extracted}")
    print(f"TARGET YEAR: {Config.TARGET_YEAR}")
    print(f"OUTPUT DIRECTORY: {Config.BASE_OUTPUT_DIR}")
    
    if total_extracted > 0:
        print("\n🎯 Extraction completed successfully!")
        print(f"📁 Check the '{Config.BASE_OUTPUT_DIR}' directory for output files")
    else:
        print("\n⚠️ No data was extracted. Please check:")
        print("   - Internet connection")
        print("   - Website availability")
        print("   - Chrome WebDriver installation")
        print("   - Search criteria configuration")
    
    return total_extracted > 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)