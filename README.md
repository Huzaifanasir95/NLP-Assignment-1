# 🏛️ Pakistan Supreme Court Case Extraction System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-green.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](#)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](#)

A comprehensive automated web scraping system designed to extract case information from the **Supreme Court of Pakistan's** online case database. This system provides multi-registry support, concurrent processing, and robust error handling for systematic legal data collection.

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [🏗️ System Architecture](#️-system-architecture)
- [📊 Data Coverage](#-data-coverage)
- [🚀 Features](#-features)
- [📁 Project Structure](#-project-structure)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🔧 Configuration](#-configuration)
- [📖 Usage Guide](#-usage-guide)
- [🗂️ Case Types & Registries](#️-case-types--registries)
- [📈 Performance & Optimization](#-performance--optimization)
- [🛠️ Technical Details](#️-technical-details)
- [📊 Data Output Format](#-data-output-format)
- [🔍 Troubleshooting](#-troubleshooting)
- [📚 References & Resources](#-references--resources)
- [🤝 Contributing](#-contributing)
- [📄 Legal Notice](#-legal-notice)

## 🎯 Project Overview

### Purpose
This system automates the extraction of legal case information from the **Supreme Court of Pakistan's** public online database, enabling researchers, legal professionals, and data analysts to systematically collect and analyze judicial data for academic and professional purposes.

### Target Website
- **Primary Source**: [Supreme Court of Pakistan - Online Case Information](https://scp.gov.pk/OnlineCaseInformation.aspx)
- **Official Portal**: [Supreme Court of Pakistan](https://scp.gov.pk)
- **Case Search Interface**: Public access portal for case records

### Scope
- **Temporal Coverage**: 1980-2025 (45+ years of judicial records)
- **Geographic Coverage**: All major Pakistani registries (Lahore, Islamabad, Karachi, Peshawar, Quetta)
- **Case Types**: 35+ different case categories including Civil Appeals, Criminal Appeals, Constitutional Petitions
- **Data Points**: 15+ fields per case including case details, advocates, judgments, and PDF documents

## 🏗️ System Architecture

### Design Principles
- **Modular Architecture**: Separate extractors for each registry and case type
- **Concurrent Processing**: Multi-threaded workers for parallel data extraction
- **Fault Tolerance**: Robust error handling and automatic recovery mechanisms
- **Incremental Processing**: Real-time JSON writing with duplicate prevention
- **Resource Management**: Optimized browser instances with memory controls

### Technology Stack
- **Backend**: Python 3.8+
- **Web Automation**: Selenium WebDriver (Microsoft Edge)
- **HTML Parsing**: BeautifulSoup4
- **HTTP Requests**: Requests library with SSL handling
- **Concurrency**: ThreadPoolExecutor for worker management
- **Data Format**: JSON for structured data storage
- **File Management**: PDF download and organization

## 📊 Data Coverage

### Registries Supported
| Registry | Code | Status | Description |
|----------|------|--------|-------------|
| **Lahore** | L | ✅ Complete | Principal Seat - Original implementation |
| **Islamabad** | I | ✅ Complete | Federal Capital registry |
| **Karachi** | K | ✅ Complete | Sindh province registry |
| **Peshawar** | P | ✅ Complete | Khyber Pakhtunkhwa registry |
| **Quetta** | Q | ✅ Complete | Balochistan province registry |

### Year Range Coverage
- **Historical Data**: 1980-1999 (20 years)
- **Modern Era**: 2000-2019 (20 years)
- **Recent Cases**: 2020-2025 (Current to future)
- **Flexible Ranges**: User-selectable 5-year periods for targeted extraction

## 🚀 Features

### Core Functionality
- ✅ **Multi-Registry Support**: Extract from all 5 major Supreme Court registries
- ✅ **Selective Year Processing**: Choose specific year ranges (1980-2025)
- ✅ **Concurrent Extraction**: Multiple workers per year for faster processing
- ✅ **Real-time JSON Writing**: Incremental case storage with duplicate prevention
- ✅ **PDF Document Download**: Automatic retrieval of judgments and petitions
- ✅ **Comprehensive Case Data**: 15+ fields including advocates, dates, status
- ✅ **Robust Error Handling**: Automatic retry mechanisms and crash recovery
- ✅ **Progress Tracking**: Detailed logging and completion statistics

### Advanced Features
- 🔄 **Chunk-based Pagination**: Intelligent navigation through large result sets
- 🌐 **Edge WebDriver Integration**: Enhanced stability and performance
- 📊 **Dynamic Worker Allocation**: User-configurable workers per year
- 🔍 **Duplicate Detection**: Prevents redundant case extraction
- 📁 **Organized File Structure**: Systematic folder hierarchy for data management
- ⚡ **Memory Optimization**: Resource-efficient browser configurations
- 🛡️ **SSL/Certificate Handling**: Secure connections with certificate bypassing

### User Experience
- 🎯 **Interactive CLI Interface**: User-friendly command-line interaction
- 📋 **Flexible Configuration**: Customizable extraction parameters
- 📈 **Real-time Progress**: Live updates during extraction process
- 🎨 **Color-coded Logging**: Enhanced readability with status indicators
- ⚙️ **Resource Control**: Adjustable worker limits and memory settings

## 📁 Project Structure

```
NLP-Assignment-1/
├── 📁 Lahore/                    # Lahore Registry (Original Implementation)
│   ├── 📁 1_C_A/                 # Civil Appeals
│   │   ├── 📄 main.py            # CA extraction script
│   │   ├── 📁 1980_1984/         # Year range folders
│   │   ├── 📁 1985_1989/
│   │   └── ... (46 year ranges)
│   ├── 📁 2_Crl_A/               # Criminal Appeals  
│   ├── 📁 3_Crl_Sh_A/            # Criminal Sharia Appeals
│   ├── 📁 4_C_Sh_A/              # Civil Sharia Appeals
│   ├── 📁 5_C_P_L_A/             # Civil PLAs
│   ├── 📁 6_Crl_P_L_A/           # Criminal PLAs
│   └── ... (35 case types)
│
├── 📁 Islamabad/                 # Islamabad Registry
│   ├── 📁 1_C_A/
│   │   ├── 📄 main.py            # Islamabad CA extractor
│   │   └── 📁 [year_ranges]/
│   └── ... (35 case types)
│
├── 📁 Karachi/                   # Karachi Registry
│   ├── 📁 1_C_A/
│   │   ├── 📄 main.py            # Karachi CA extractor
│   │   └── 📁 [year_ranges]/
│   └── ... (35 case types)
│
├── 📁 Peshawar/                  # Peshawar Registry
│   ├── 📁 1_C_A/
│   │   ├── 📄 main.py            # Peshawar CA extractor
│   │   └── 📁 [year_ranges]/
│   └── ... (35 case types)
│
├── 📁 Quetta/                    # Quetta Registry
│   ├── 📁 1_C_A/
│   │   ├── 📄 main.py            # Quetta CA extractor
│   │   └── 📁 [year_ranges]/
│   └── ... (35 case types)
│
├── 📁 SupremeCourt_CaseInfo/     # Original reference data
│   ├── 📄 SupremeCourt_CaseInfo.Json
│   ├── 📁 judgementspdf/
│   └── 📁 memopdf/
│
├── 📁 SupremeCourt_Judgements/   # Judgment reference data
│   ├── 📄 SupremeCourt_Judgments.json
│   └── 📁 judgmentspdfs/
│
├── 📄 create_registry_folders.py # Folder structure generator
├── 📄 README.md                  # This documentation
├── 📄 .gitignore                 # Git ignore rules
└── 📄 Assignment-1 NLP - Final version.pdf
```

### Folder Organization Logic
- **Registry Level**: Top-level folders for each Supreme Court registry
- **Case Type Level**: 35 case types per registry (C.A., Crl.A., etc.)
- **Year Range Level**: 5-year periods (1980-1984, 1985-1989, etc.)
- **Data Organization**: JSON files and PDF downloads within year ranges

## ⚙️ Installation & Setup

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Microsoft Edge browser (latest version)
# Download from: https://www.microsoft.com/edge
```

### Required Python Packages
```bash
pip install selenium beautifulsoup4 requests urllib3 lxml
```

### WebDriver Setup
```bash
# Microsoft Edge WebDriver (Automatic)
# Selenium 4.0+ automatically manages Edge WebDriver
# No manual download required
```

### Environment Verification
```python
# Test script to verify setup
from selenium import webdriver
from selenium.webdriver.edge.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Edge(options=options)
print("✅ WebDriver setup successful")
driver.quit()
```

## 🔧 Configuration

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for high concurrency)
- **Storage**: 10GB+ free space for PDF downloads
- **Network**: Stable internet connection (SCP website access)
- **OS**: Windows 10/11, macOS, or Linux

### Performance Tuning
```python
# Worker Configuration (in main.py)
max_workers = 5  # Adjust based on system capacity
headless = False  # Set True for server environments

# Memory Optimization
options.add_argument('--max_old_space_size=2048')
options.add_argument('--aggressive-cache-discard')
```

### Browser Configuration
The system uses optimized Edge WebDriver settings:
- **Disabled Features**: Images, plugins, extensions, notifications
- **Enhanced Stability**: Crash prevention and automatic recovery
- **Memory Management**: Aggressive caching and resource limits
- **SSL Handling**: Certificate error bypassing for SCP website

## 📖 Usage Guide

### Basic Extraction Process

#### 1. Navigate to Registry Folder
```bash
cd NLP-Assignment-1/Islamabad/1_C_A
```

#### 2. Run Extraction Script
```bash
python main.py
```

#### 3. Interactive Menu Navigation
```
📅 AVAILABLE YEAR RANGES FOR C.A. ISLAMABAD EXTRACTION:
============================================================
   1. 1980-1984 (5 years: 1980, 1981, 1982, 1983, 1984)
   2. 1985-1989 (5 years: 1985, 1986, 1987, 1988, 1989)
   3. 1990-1994 (5 years: 1990, 1991, 1992, 1993, 1994)
   ...
   0. Extract ALL year ranges
   q. Quit

Select year range(s): 1,5,9  # Multiple ranges
```

#### 4. Worker Allocation
```
⚙️ WORKER ALLOCATION CONFIGURATION
==================================================
Available total workers: 5
Configure worker allocation for 1980-1984? (y/n): y

Assign workers to individual years:
1980: 2 workers
1981: 1 worker
...
```

#### 5. Extraction Progress
```
🚀 C.A. ISLAMABAD EXTRACTION STARTING
==================================================
📊 PROCESSING YEAR RANGE: 1980-1984
   Years: [1980, 1981, 1982, 1983, 1984]
   Worker Allocation:
     1980: 2 workers - 🔥 High Priority
     1981: 1 worker - ⚡ Standard

✅ Worker 1: Page loaded successfully for year 1980
🔍 Worker 1: Search button clicked for year 1980
💾 NEW case C.A.123/1980 written to 1980_1984/CA_Islamabad_1980_1984_complete.json
```

### Advanced Usage Patterns

#### Multi-Registry Extraction
```bash
# Extract from all registries simultaneously
cd Islamabad/1_C_A && python main.py &
cd Karachi/1_C_A && python main.py &
cd Peshawar/1_C_A && python main.py &
cd Quetta/1_C_A && python main.py &
```

#### Targeted Year Extraction
```bash
# Focus on recent years (2020-2024)
# Select range 9 when prompted
python main.py
# Input: 9
```

#### High-Performance Configuration
```python
# Modify main.py for server environments
extractor = CAIslamabadInteractiveExtractor(max_workers=10)
headless = True  # Enable headless mode
```

## 🗂️ Case Types & Registries

### Complete Case Type Mapping
| ID | Code | Full Name | Description |
|----|------|-----------|-------------|
| 1 | C.A. | Civil Appeals | Civil matters appealed to Supreme Court |
| 2 | Crl.A. | Criminal Appeals | Criminal cases on appeal |
| 3 | Crl.Sh.A. | Criminal Sharia Appeals | Sharia-based criminal appeals |
| 4 | C.Sh.A. | Civil Sharia Appeals | Sharia-based civil appeals |
| 5 | C.P.L.A. | Civil PLAs | Civil Petitions for Leave to Appeal |
| 6 | Crl.P.L.A. | Criminal PLAs | Criminal Petitions for Leave to Appeal |
| 7+ | ... | Extended Types | 29 additional case categories |

### Registry Geographic Coverage
- **Lahore**: Punjab province (largest case volume)
- **Islamabad**: Federal capital and ICT
- **Karachi**: Sindh province (commercial hub)
- **Peshawar**: Khyber Pakhtunkhwa (northwestern region)
- **Quetta**: Balochistan province (southwestern region)

## 📈 Performance & Optimization

### Benchmarks
- **Extraction Speed**: ~50-100 cases per minute per worker
- **Memory Usage**: 200-500MB per browser instance
- **Storage**: ~1-5MB per 100 cases (JSON + PDFs)
- **Concurrent Workers**: 5-10 recommended (system-dependent)

### Optimization Strategies
1. **Worker Allocation**: Distribute workers across years, not pages
2. **Chunk Processing**: Handle 10-page chunks for large result sets
3. **Incremental Writing**: Stream JSON data to prevent memory overflow
4. **Resource Cleanup**: Automatic browser instance management
5. **Duplicate Prevention**: Hash-based case deduplication

### Monitoring & Debugging
```bash
# Enable verbose logging
python main.py --verbose

# Monitor system resources
Task Manager (Windows) / Activity Monitor (macOS) / htop (Linux)

# Check extraction progress
tail -f logs/extraction.log  # If logging implemented
```

## 🛠️ Technical Details

### Web Scraping Strategy
- **Navigation**: Selenium WebDriver automation
- **Page Loading**: Explicit waits with timeout handling
- **Data Extraction**: BeautifulSoup HTML parsing
- **Pagination**: Advanced ellipsis navigation algorithm
- **Error Recovery**: Automatic retry with exponential backoff

### Data Processing Pipeline
1. **Page Navigation**: Load case search form
2. **Form Submission**: Select registry, case type, year
3. **Result Parsing**: Extract case list from search results
4. **Detail Extraction**: Navigate to individual case pages
5. **PDF Download**: Retrieve associated documents
6. **Data Storage**: Write structured JSON incrementally

### Error Handling Mechanisms
- **Browser Crashes**: Automatic driver restart
- **Network Timeouts**: Configurable retry attempts
- **Page Loading Failures**: Alternative navigation strategies
- **Duplicate Detection**: Case number-based filtering
- **Resource Exhaustion**: Memory cleanup and optimization

### Security & Legal Compliance
- **Respectful Scraping**: Reasonable request intervals
- **Public Data**: Only accessing publicly available information
- **No Authentication**: Using open-access case database
- **SSL Handling**: Secure connection management

## 📊 Data Output Format

### JSON Structure
```json
{
  "Case_No": "C.A.123/1980",
  "Case_Title": "Example vs. State",
  "Status": "Decided",
  "Institution_Date": "01-01-1980",
  "Disposal_Date": "15-06-1980",
  "Advocates": {
    "ASC": "Advocate Name",
    "AOR": "Attorney Name",
    "Prosecutor": "Prosecutor Name"
  },
  "Petition_Appeal_Memo": {
    "File": "/path/to/memo.pdf",
    "Type": "PDF",
    "Downloaded_Path": "pdfs/case123_memo.pdf",
    "Files": [...]
  },
  "Judgement_Order": {
    "File": "/path/to/judgment.pdf",
    "Type": "PDF", 
    "Downloaded_Path": "pdfs/case123_judgment.pdf",
    "Files": [...]
  },
  "History": [
    {"date": "01-02-1980", "event": "Case filed"},
    {"date": "15-06-1980", "event": "Judgment pronounced"}
  ],
  "Worker_ID": "worker_1",
  "Page_Number": 1,
  "Year": 1980,
  "Case_Type": "C.A.",
  "Year_Range": "1980-1984"
}
```

### File Organization
```
1980_1984/
├── 📄 CA_Islamabad_1980_1984_complete.json    # Main data file
├── 📄 extraction_summary.txt                   # Extraction statistics
├── 📁 pdfs/                                    # Downloaded documents
│   ├── 📄 CA_123_1980_memo.pdf
│   ├── 📄 CA_123_1980_judgment.pdf
│   └── ...
└── 📁 logs/                                    # Processing logs
    ├── 📄 1980_extraction.log
    └── 📄 errors.log
```

## 🔍 Troubleshooting

### Common Issues & Solutions

#### 1. WebDriver Failures
```
Error: EdgeDriver not found
Solution: Update Edge browser to latest version
Command: Check Edge version in Settings > About
```

#### 2. Memory Issues
```
Error: Out of memory
Solution: Reduce max_workers or enable headless mode
Config: max_workers = 3, headless = True
```

#### 3. Network Timeouts
```
Error: Page load timeout
Solution: Increase timeout values
Config: driver.set_page_load_timeout(30)
```

#### 4. Pagination Problems
```
Error: Cannot navigate to page X
Solution: Verify site structure hasn't changed
Debug: Enable debug_pagination_structure()
```

#### 5. PDF Download Failures
```
Error: PDF download failed
Solution: Check network connection and file permissions
Path: Verify pdfs/ folder exists and is writable
```

### Debug Mode
```python
# Enable comprehensive debugging
extractor = CAIslamabadInteractiveExtractor(max_workers=1)
# Single worker for easier debugging

# Add debug prints in worker methods
print(f"DEBUG: Processing page {page_num}")
```

### Log Analysis
```bash
# Check for common error patterns
grep "ERROR" logs/*.log
grep "TIMEOUT" logs/*.log
grep "FAILED" logs/*.log

# Monitor real-time progress
tail -f 1980_1984/CA_Islamabad_1980_1984_complete.json
```

## 📚 References & Resources

### Official Sources
- [Supreme Court of Pakistan](https://scp.gov.pk/) - Official website
- [Case Information System](https://scp.gov.pk/OnlineCaseInformation.aspx) - Public case database
- [Court Rules & Procedures](https://scp.gov.pk/rules.php) - Legal framework
- [Pakistani Legal System](https://en.wikipedia.org/wiki/Judiciary_of_Pakistan) - Background information

### Technical Documentation
- [Selenium WebDriver](https://selenium-python.readthedocs.io/) - Web automation framework
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing library
- [Python Requests](https://requests.readthedocs.io/) - HTTP library
- [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) - Browser automation

### Legal & Research Context
- [Pakistan Legal Database](https://pakistanlegaldb.com/) - Comprehensive legal resource
- [Supreme Court Cases](https://www.supremecourt.gov.pk/) - Case law repository
- [Legal Research Methods](https://libraryguides.law.pace.edu/legalresearch) - Academic guidance
- [Judicial Data Analysis](https://www.jstor.org/topic/judicial-behavior/) - Research applications

### Development Tools
- [Python Official](https://python.org/) - Programming language
- [Visual Studio Code](https://code.visualstudio.com/) - Development environment
- [Git Documentation](https://git-scm.com/doc) - Version control
- [JSON Validator](https://jsonlint.com/) - Data validation tool

## 🤝 Contributing

### Contribution Guidelines
1. **Fork Repository**: Create personal fork for development
2. **Feature Branches**: Use descriptive branch names
3. **Code Standards**: Follow PEP 8 Python style guide
4. **Documentation**: Update README for new features
5. **Testing**: Verify functionality before submission

### Development Setup
```bash
# Clone repository
git clone https://github.com/username/NLP-Assignment-1.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Contribution Areas
- **New Case Types**: Implement additional case category extractors
- **Registry Expansion**: Add support for specialized courts
- **Performance Optimization**: Improve extraction speed and reliability
- **Data Analysis**: Create analysis tools for extracted data
- **Documentation**: Enhance user guides and technical documentation

### Code Review Process
1. Submit pull request with detailed description
2. Ensure all tests pass and documentation is updated
3. Address review feedback promptly
4. Maintain backward compatibility

## 📄 Legal Notice

### Educational Use
This project is developed for **educational and research purposes** only. It is designed to facilitate academic study of judicial data and legal system analysis.

### Data Usage Policy
- **Public Information**: Only extracts publicly available case information
- **Respectful Access**: Implements reasonable request intervals
- **No Commercial Use**: Intended for academic research only
- **Data Attribution**: Acknowledge Supreme Court of Pakistan as data source

### Compliance Guidelines
- **Terms of Service**: Comply with SCP website terms of use
- **Ethical Scraping**: Follow responsible web scraping practices
- **Research Ethics**: Use data in accordance with academic standards
- **Privacy Protection**: Handle personal information appropriately

### Disclaimer
This software is provided "as is" without warranty. Users are responsible for ensuring their use complies with applicable laws and regulations. The developers assume no liability for misuse or legal consequences.

---

## 📞 Support & Contact

For technical support, feature requests, or academic collaboration:

- **Issues**: [GitHub Issues](https://github.com/username/NLP-Assignment-1/issues)
- **Documentation**: This README and inline code comments
- **Academic Use**: Contact institution for research collaboration

**Last Updated**: September 2025  
**Version**: 1.0.0  
**Compatibility**: Python 3.8+, Selenium 4.0+, Edge 90+
