"""
Package initialization for utils module
"""

from .web_utils import *

__all__ = [
    'setup_chrome_driver',
    'safe_find_element', 
    'safe_find_elements',
    'handle_alert',
    'clean_text',
    'extract_case_number',
    'extract_year_from_case_number',
    'is_target_year_case',
    'save_json',
    'load_json',
    'check_pagination',
    'click_next_page',
    'wait_for_page_load',
    'get_page_source_soup',
    'filter_2025_cases',
    'log_extraction_progress'
]