"""
JSON Structure Analysis for Supreme Court Data
Analyzes the complete structure and creates templates for extraction
"""

import json
from collections import defaultdict, Counter


def analyze_json_structure():
    """Analyze the complete JSON structure"""
    print("📊 ANALYZING SUPREME COURT JSON STRUCTURE")
    print("=" * 60)
    
    # Load the existing JSON file
    with open("SupremeCourt_CaseInfo/SupremeCourt_CaseInfo.Json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"📋 Total cases in file: {len(data)}")
    
    # Analyze the structure
    all_fields = set()
    field_types = defaultdict(set)
    sample_values = defaultdict(list)
    
    for case in data:
        if isinstance(case, dict):
            for key, value in case.items():
                all_fields.add(key)
                field_types[key].add(type(value).__name__)
                
                # Store sample values
                if len(sample_values[key]) < 3:
                    if isinstance(value, dict):
                        sample_values[key].append(f"Dict with keys: {list(value.keys())}")
                    elif isinstance(value, list):
                        sample_values[key].append(f"List with {len(value)} items")
                    else:
                        sample_values[key].append(str(value)[:50])
    
    print("\n📋 COMPLETE FIELD STRUCTURE:")
    print("-" * 40)
    
    for field in sorted(all_fields):
        types = ", ".join(field_types[field])
        samples = " | ".join(sample_values[field])
        print(f"   {field}:")
        print(f"      Type(s): {types}")
        print(f"      Samples: {samples}")
        print()
    
    # Analyze Advocates structure
    advocates_keys = set()
    for case in data:
        if isinstance(case, dict) and "Advocates" in case and isinstance(case["Advocates"], dict):
            advocates_keys.update(case["Advocates"].keys())
    
    print("👨‍💼 ADVOCATES STRUCTURE:")
    print(f"   Keys: {sorted(advocates_keys)}")
    
    # Analyze Petition_Appeal_Memo structure  
    memo_keys = set()
    for case in data:
        if isinstance(case, dict) and "Petition_Appeal_Memo" in case and isinstance(case["Petition_Appeal_Memo"], dict):
            memo_keys.update(case["Petition_Appeal_Memo"].keys())
    
    print("\n📝 PETITION_APPEAL_MEMO STRUCTURE:")
    print(f"   Keys: {sorted(memo_keys)}")
    
    # Analyze Judgement_Order structure
    judgment_keys = set()
    for case in data:
        if isinstance(case, dict) and "Judgement_Order" in case and isinstance(case["Judgement_Order"], dict):
            judgment_keys.update(case["Judgement_Order"].keys())
    
    print("\n⚖️ JUDGEMENT_ORDER STRUCTURE:")
    print(f"   Keys: {sorted(judgment_keys)}")
    
    # Analyze year distribution
    years = Counter()
    case_types = Counter()
    registries = Counter()
    statuses = Counter()
    
    for case in data:
        if isinstance(case, dict):
            case_no = case.get("Case_No", "")
            
            # Extract year
            if "/" in case_no:
                year = case_no.split("/")[-1]
                if year.isdigit():
                    years[year] += 1
            
            # Extract case type
            if "." in case_no:
                case_type = case_no.split(".")[0] + "." + case_no.split(".")[1]
                case_types[case_type] += 1
            
            # Extract registry
            if "-" in case_no and "/" in case_no:
                registry_part = case_no.split("-")[-1].split("/")[0]
                registries[registry_part] += 1
            
            # Status
            status = case.get("Status", "N/A")
            statuses[status] += 1
    
    print("\n📊 DATA DISTRIBUTION:")
    print(f"   Years: {dict(years.most_common())}")
    print(f"   Case Types: {dict(case_types.most_common())}")
    print(f"   Registries: {dict(registries.most_common())}")
    print(f"   Statuses: {dict(statuses.most_common())}")
    
    return {
        "total_cases": len(data),
        "fields": sorted(all_fields),
        "advocates_keys": sorted(advocates_keys),
        "memo_keys": sorted(memo_keys),
        "judgment_keys": sorted(judgment_keys),
        "years": dict(years),
        "case_types": dict(case_types),
        "registries": dict(registries),
        "statuses": dict(statuses)
    }


def analyze_folder_structure():
    """Analyze the folder structure for file organization"""
    print("\n📁 FOLDER STRUCTURE ANALYSIS:")
    print("=" * 60)
    
    import os
    
    base_path = "SupremeCourt_CaseInfo"
    
    for root, dirs, files in os.walk(base_path):
        level = root.replace(base_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({size} bytes)")
            except:
                print(f"{subindent}{file}")
    
    print("\n📋 FOLDER PURPOSE:")
    print("   judgementspdf/  - PDF files of judgments")
    print("   memopdf/        - PDF files of petition/appeal memos") 
    print("   pdfs/           - General PDF files")
    print("   SupremeCourt_CaseInfo.Json - Main case data")


def create_complete_template():
    """Create template for complete case data structure"""
    template = {
        "Case_No": "C.A.123-L/2025",
        "Case_Title": "Petitioner Name v. Respondent Name, etc",
        "Status": "Pending",  # Pending, Disposed, etc
        "Institution_Date": "View Details",
        "Disposal_Date": "N/A",
        "Advocates": {
            "ASC": "N/A",  # Advocate Supreme Court
            "AOR": "N/A",  # Advocate on Record
            "Prosecutor": "N/A"
        },
        "Petition_Appeal_Memo": {
            "File": "N/A",  # PDF file path
            "Type": "N/A"   # Document type
        },
        "History": [],  # Case history/proceedings
        "Judgement_Order": {
            "File": "N/A",  # PDF file path
            "Type": "N/A"   # Document type
        }
    }
    
    print("\n📋 COMPLETE CASE DATA TEMPLATE:")
    print("=" * 60)
    print(json.dumps(template, indent=2))
    
    return template


def main():
    """Main analysis function"""
    structure_info = analyze_json_structure()
    analyze_folder_structure()
    template = create_complete_template()
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS COMPLETE!")
    print(f"   Total fields identified: {len(structure_info['fields'])}")
    print(f"   Years covered: {len(structure_info['years'])}")
    print(f"   Case types: {len(structure_info['case_types'])}")
    print(f"   Registries: {len(structure_info['registries'])}")
    print("=" * 60)
    
    return structure_info, template


if __name__ == "__main__":
    main()