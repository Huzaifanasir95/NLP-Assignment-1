"""
Supreme Court Registry Folder Structure Creator
Creates basic folder structures for Islamabad, Peshawar, Quetta, and Karachi
Structure: Registry > Case_Type > Year_Range > Individual_Years > (Logs + PDF)
"""

import json
import os
from pathlib import Path


class RegistryStructureCreator:
    """Creates organized folder structures for each registry"""
    
    def __init__(self, base_dir="d:/SEM7/NLP/NLP-Assignment-1"):
        self.base_dir = Path(base_dir)
        
        # Load the case types and years from Lahore structure
        self.lahore_analysis_file = self.base_dir / "Lahore" / "lahore_structure_analysis.json"
        
        with open(self.lahore_analysis_file, 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
        
        self.registries = ['Islamabad', 'Peshawar', 'Quetta', 'Karachi']
    
    def sanitize_folder_name(self, name):
        """Convert case type names to valid folder names"""
        sanitized = name.replace('.', '_').replace('(', '_').replace(')', '_')
        sanitized = sanitized.rstrip('_')
        return sanitized
    
    def create_registry_structure(self, registry_name):
        """Create the complete folder structure for a registry"""
        print(f"🏗️ CREATING {registry_name.upper()} FOLDER STRUCTURE")
        print("=" * 60)
        
        registry_dir = self.base_dir / registry_name
        registry_dir.mkdir(exist_ok=True)
        
        case_types = self.analysis_data['case_types']
        year_ranges = self.analysis_data['year_ranges']
        
        created_folders = 0
        
        for case_type in case_types:
            case_value = case_type['value']
            case_text = case_type['text']
            case_folder_name = f"{case_value}_{self.sanitize_folder_name(case_text)}"
            
            # Create main case type folder
            case_type_dir = registry_dir / case_folder_name
            case_type_dir.mkdir(exist_ok=True)
            
            print(f"📁 Case Type: {case_folder_name}")
            
            # Create year range folders within case type folder
            for year_range in year_ranges:
                range_name = year_range['name']
                year_range_dir = case_type_dir / range_name
                year_range_dir.mkdir(exist_ok=True)
                
                # Create logs and pdfs folders directly in year range folder
                logs_dir = year_range_dir / "logs"
                pdfs_dir = year_range_dir / "pdfs"
                logs_dir.mkdir(exist_ok=True)
                pdfs_dir.mkdir(exist_ok=True)
                
                created_folders += 1
                
        print(f"\n✅ {registry_name.upper()} FOLDER STRUCTURE CREATED!")
        print(f"   Case Type Folders: {len(case_types)}")
        print(f"   Year Range Folders: {len(case_types) * len(year_ranges)}")
        print(f"   Logs + PDF Folders: {len(case_types) * len(year_ranges) * 2}")
        print(f"   Total Folders Created: {created_folders * 2}")  # *2 for logs + pdfs
        
        return True
    
    def create_all_registries(self):
        """Create folder structures for all registries"""
        print("🚀 CREATING ALL REGISTRY FOLDER STRUCTURES")
        print("=" * 60)
        
        success_count = 0
        
        for registry in self.registries:
            try:
                if self.create_registry_structure(registry):
                    success_count += 1
                print()  # Add spacing between registries
            except Exception as e:
                print(f"❌ Failed to create {registry}: {e}")
        
        print("🎉 ALL REGISTRY STRUCTURES COMPLETE!")
        print("=" * 60)
        print(f"✅ Successfully created: {success_count}/{len(self.registries)} registries")
        print(f"📁 Structure: Case_Type > Year_Range > (logs + pdfs)")
        print(f"📋 {len(self.analysis_data['case_types'])} case types × {len(self.analysis_data['year_ranges'])} year ranges per registry")
        print("🚀 Ready for case extraction development!")


def main():
    """Main function"""
    creator = RegistryStructureCreator()
    creator.create_all_registries()


if __name__ == "__main__":
    main()