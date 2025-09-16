# Supreme Court of Pakistan Data Extractor

A comprehensive Python-based data extraction system for Supreme Court of Pakistan case information and judgments, specifically designed for 2025 data with pagination support.

## Features

- **2025 Data Focus**: Extracts only 2025 case data as specified
- **Pagination Support**: Handles website pagination automatically using Selenium
- **Dual Extraction**: Extracts both case information and judgment data
- **Robust Error Handling**: Comprehensive error handling and retry mechanisms
- **Configurable**: Easy configuration through centralized config file
- **Multiple Search Strategies**: Uses various search combinations to maximize data coverage

## Project Structure

```
NLP-Assignment-1/
├── src/
│   ├── config.py                 # Central configuration
│   ├── extractors/
│   │   ├── base_extractor.py     # Base extraction class
│   │   ├── case_info_extractor.py # Case information extractor
│   │   └── judgment_extractor.py  # Judgment extractor
│   └── utils/
│       └── web_utils.py          # Web scraping utilities
├── data/
│   ├── case_info/               # Case information output
│   ├── judgments/               # Judgment data output
│   └── pdfs/                    # PDF files (if downloaded)
├── main.py                      # Main execution script
└── requirements.txt             # Python dependencies
```

## Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)

## Installation

1. Clone or download this project
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `src/config.py` to customize:

- `TARGET_YEAR`: Year to extract (default: 2025)
- `MAX_PAGES_PER_SEARCH`: Maximum pages per search strategy
- `TIMEOUT`: WebDriver timeout settings
- Output directories and file naming

## Usage

### Basic Extraction

Run the main extraction script:

```bash
python main.py
```

### Individual Extractors

Extract only case information:
```python
from src.extractors.case_info_extractor import CaseInfoExtractor

extractor = CaseInfoExtractor()
extractor.run_extraction()
```

Extract only judgments:
```python
from src.extractors.judgment_extractor import JudgmentExtractor

extractor = JudgmentExtractor()
extractor.run_extraction()
```

## Output Format

### Case Information
```json
{
  "Case_No": "C.A.76-L/2025",
  "Case_Title": "Petitioner vs Respondent",
  "Status": "Pending",
  "Institution_Date": "View Details"
}
```

### Judgment Data
```json
{
  "Case_No": "C.A.123/2025",
  "Parties": "Appellant vs Respondent",
  "Judgment_Date": "15/01/2025",
  "PDF_Link": "https://example.com/judgment.pdf",
  "Judge": "Hon'ble Justice Name"
}
```

## Search Strategies

The extractor uses multiple search strategies to maximize data coverage:

### Case Information
- Different case types (Civil Appeals, Criminal Appeals, etc.)
- Multiple registries (Lahore, Karachi, Islamabad)
- Automated pagination handling

### Judgments
- Month-by-month search for 2025
- Automated pagination for each month
- PDF link extraction

## Pagination Handling

The system automatically:
- Detects pagination elements
- Clicks "Next" buttons
- Handles page load timeouts
- Stops when no more pages are available

## Error Handling

- **Timeout Management**: 60-second timeouts with retry mechanisms
- **Alert Handling**: Automatically handles JavaScript alerts
- **Form Validation**: Manages "Please provide at least 2 search criteria" errors
- **Network Issues**: Robust handling of connection problems

## Troubleshooting

### Common Issues

1. **"Timed out receiving message from renderer"**
   - Increase timeout in `config.py`
   - Check internet connection
   - Ensure Chrome browser is updated

2. **"Please provide at least 2 search criteria" alerts**
   - Handled automatically by using multiple search criteria
   - System continues extraction despite alerts

3. **No data extracted**
   - Check if 2025 data is available on the website
   - Verify website structure hasn't changed
   - Check Chrome WebDriver compatibility

### Debug Mode

Enable verbose logging by modifying the print statements in the extraction classes.

## Development

### Adding New Extractors

1. Inherit from `BaseExtractor`
2. Implement `extract_data()` method
3. Use utilities from `web_utils.py`
4. Follow existing patterns for pagination

### Customizing Search Strategies

Modify the `search_strategies` list in extractor classes to add new search combinations.

## Dependencies

- `selenium`: Web automation and pagination
- `beautifulsoup4`: HTML parsing
- `pandas`: Data manipulation (optional)
- `requests`: HTTP requests (optional)

## License

This project is for educational purposes as part of NLP Assignment Group G4.

## Assignment Context

- **Course**: Natural Language Processing (NLP)
- **Assignment**: NLP-Assignment-1
- **Group**: G4
- **Target**: Extract Supreme Court of Pakistan data (1980-2025)
- **Focus**: 2025 data with comprehensive pagination support
- **Output**: JSON format matching assignment requirements