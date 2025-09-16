"""
Configuration settings for Supreme Court Pakistan Data Extractor
"""

import os
from datetime import datetime

class Config:
    # Base directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    # Data directories - matching the existing structure
    CASE_INFO_DIR = os.path.join(DATA_DIR, "SupremeCourt_CaseInfo")
    JUDGMENTS_DIR = os.path.join(DATA_DIR, "SupremeCourt_Judgements")
    
    # PDF subdirectories
    JUDGMENT_PDF_DIR = os.path.join(CASE_INFO_DIR, "judgementspdf")
    MEMO_PDF_DIR = os.path.join(CASE_INFO_DIR, "memopdf")
    GENERAL_PDF_DIR = os.path.join(CASE_INFO_DIR, "pdfs")
    
    # URLs
    CASE_INFO_URL = "https://scp.gov.pk/OnlineCaseInformation.aspx"
    JUDGMENT_URL = "https://www.supremecourt.gov.pk/judgement-search/"
    
    # File names
    CASE_INFO_JSON = "SupremeCourt_CaseInfo.Json"
    JUDGMENTS_JSON = "SupremeCourt_Judgments.json"
    
    # Target years for extraction (1980-2025)
    START_YEAR = 1980
    END_YEAR = 2025
    TARGET_YEAR = 2025  # For compatibility with existing code
    
    # All years for comprehensive extraction
    ALL_YEARS = list(range(START_YEAR, END_YEAR + 1))
    
    # Extraction settings - comprehensive coverage
    REGISTRIES = [
        'Islamabad', 'Lahore', 'Karachi', 'Peshawar', 'Quetta'
    ]
    
    CASE_TYPES = [
        'Civil Appeals', 'Criminal Appeals', 'Constitution Petitions',
        'Review Petitions', 'Miscellaneous Applications', 'Original Jurisdiction',
        'Suo Moto Cases', 'Contempt Cases', 'Reference Cases'
    ]
    
    # Search strategies for comprehensive extraction
    COMPREHENSIVE_STRATEGIES = []
    
    @classmethod
    def generate_comprehensive_strategies(cls):
        """Generate all combinations of registries, case types, and years"""
        strategies = []
        
        # Priority years (recent years first)
        priority_years = [2025, 2024, 2023, 2022, 2021]
        other_years = [year for year in cls.ALL_YEARS if year not in priority_years]
        
        # Combine priority years with all combinations
        for year in priority_years + other_years:
            for registry in cls.REGISTRIES:
                for case_type in cls.CASE_TYPES:
                    strategies.append({
                        "year": year,
                        "registry": registry,
                        "case_type": case_type
                    })
        
        cls.COMPREHENSIVE_STRATEGIES = strategies
        return strategies
    
    # Selenium settings
    TIMEOUT = 60
    MAX_RETRIES = 3
    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 60
    
    # Pagination settings
    MAX_PAGES_PER_SEARCH = 50  # Maximum pages to scrape per search
    RESULTS_PER_PAGE = 20      # Typical results per page
    
    # Rate limiting
    DELAY_BETWEEN_REQUESTS = 3
    DELAY_BETWEEN_PAGES = 2
    DELAY_BETWEEN_SEARCHES = 5  # Delay between different search strategies
    DELAY_BETWEEN_EXTRACTIONS = 10  # Delay between case info and judgment extraction
    
    # Chrome driver options
    CHROME_OPTIONS = [
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--window-size=1920,1080',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        '--memory-pressure-off'
    ]
    
    @classmethod
    def create_directories(cls):
        """Create all required directories"""
        directories = [
            cls.DATA_DIR,
            cls.CASE_INFO_DIR,
            cls.JUDGMENTS_DIR,
            cls.JUDGMENT_PDF_DIR,
            cls.MEMO_PDF_DIR,
            cls.GENERAL_PDF_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        print(f"✅ Created directories in: {cls.DATA_DIR}")
    
    @classmethod
    def get_output_path(cls, data_type, filename):
        """Get full path for output file"""
        cls.create_directories()
        
        if data_type == "case_info":
            return os.path.join(cls.CASE_INFO_DIR, filename)
        elif data_type == "judgments":
            return os.path.join(cls.JUDGMENTS_DIR, filename)
        elif data_type == "judgment_pdfs":
            return os.path.join(cls.JUDGMENT_PDF_DIR, filename)
        elif data_type == "memo_pdfs":
            return os.path.join(cls.MEMO_PDF_DIR, filename)
        elif data_type == "pdfs":
            return os.path.join(cls.GENERAL_PDF_DIR, filename)
        else:
            return os.path.join(cls.DATA_DIR, filename)
    
    @classmethod
    def get_extraction_summary_config(cls):
        """Get summary of extraction configuration"""
        return {
            "total_years": len(cls.ALL_YEARS),
            "year_range": f"{cls.START_YEAR}-{cls.END_YEAR}",
            "registries": len(cls.REGISTRIES),
            "case_types": len(cls.CASE_TYPES),
            "total_strategies": len(cls.REGISTRIES) * len(cls.CASE_TYPES) * len(cls.ALL_YEARS),
            "output_directories": [
                cls.CASE_INFO_DIR,
                cls.JUDGMENT_PDF_DIR,
                cls.MEMO_PDF_DIR,
                cls.GENERAL_PDF_DIR
            ]
        }