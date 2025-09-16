# Supreme Court Data Extractor - 2025 Focus

## Quick Start Guide

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run Extraction
```bash
# Extract all 2025 data
python main.py
```

### 3. Check Results
- Case Information: `data/case_info/`
- Judgments: `data/judgments/`

## Key Features for 2025 Data

✅ **Automatic Pagination** - Handles all pages automatically  
✅ **2025 Filter** - Only extracts 2025 data  
✅ **Multiple Strategies** - Uses various search combinations  
✅ **Error Handling** - Robust timeout and retry mechanisms  
✅ **JSON Output** - Matches assignment requirements  

## Configuration

Edit `src/config.py` for:
- Target year (default: 2025)
- Maximum pages per search
- Timeout settings
- Output directories

## Troubleshooting

**No data found?**
- Check if 2025 data exists on website
- Increase timeout in config.py
- Ensure Chrome browser is updated

**Timeout errors?**
- Default timeout is 60s (increased from 15s)
- Check internet connection
- Website might be slow

## Output Format

Based on existing JSON structure:
```json
{
  "Case_No": "C.A.76-L/2025",
  "Case_Title": "Case Title Here",
  "Status": "Pending",
  "Institution_Date": "View Details"
}
```