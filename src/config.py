"""
Configuration settings for Supreme Court Pakistan Data Extractor
"""

import os
from datetime import datetime

class Config:
    # Base directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    # Data directories
    CASE_INFO_DIR = os.path.join(DATA_DIR, "case_info")
    JUDGMENTS_DIR = os.path.join(DATA_DIR, "judgments")
    PDF_DIR = os.path.join(DATA_DIR, "pdfs")
    
    # URLs
    CASE_INFO_URL = "https://scp.gov.pk/OnlineCaseInformation.aspx"
    JUDGMENT_URL = "https://www.supremecourt.gov.pk/judgement-search/"
    
    # File names
    CASE_INFO_JSON = "SupremeCourt_CaseInfo_2025.json"
    JUDGMENTS_JSON = "SupremeCourt_Judgments_2025.json"
    
    # Target year for extraction
    TARGET_YEAR = 2025
    
    # Extraction settings
    REGISTRIES = ['Islamabad', 'Lahore', 'Karachi']
    CASE_TYPES = ['C.A.', 'C.M.A.', 'C.P.', 'C.R.P.']
    
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
            cls.PDF_DIR
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
        elif data_type == "pdfs":
            return os.path.join(cls.PDF_DIR, filename)
        else:
            return os.path.join(cls.DATA_DIR, filename)