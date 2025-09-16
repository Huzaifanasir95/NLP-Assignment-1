"""
Test Extractor for C.A. Lahore 2025 Cases with PDF Downloads
Simplified version for testing View Details and PDF downloads
"""

import time
import re
import json
import os
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup


class CALahore2025Extractor:
    """Focused extractor for C.A. Lahore 2025 cases with PDF downloads"""
    
    def __init__(self):
        self.driver = None
        self.extracted_cases = []
        self.base_url = "https://scp.gov.pk"
        
        # Create downloads directory
        self.downloads_dir = "ca_lahore_2025_pdfs"
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)
        
        print("✅ C.A. Lahore 2025 Extractor initialized")
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            print("✅ Chrome WebDriver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to setup driver: {e}")
            return False
    
    def navigate_to_website(self):
        """Navigate to website"""
        try:
            url = "https://scp.gov.pk/OnlineCaseInformation.aspx"
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            print("✅ Successfully navigated to website")
            return True
        except Exception as e:
            print(f"❌ Failed to navigate: {e}")
            return False
    
    def handle_form_resubmission(self):
        """Handle form resubmission error"""
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if ("confirm form resubmission" in page_source or 
                "err_cache_miss" in page_source or
                "resubmit" in page_source):
                
                print("🔄 Handling form resubmission error...")
                self.driver.refresh()
                time.sleep(3)
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ Error handling form resubmission: {e}")
            return False
    
    def perform_search(self):
        """Perform search for C.A. Lahore 2025"""
        try:
            print("🔍 Performing search: C.A. Lahore 2025")
            
            # Select case type: C.A.
            case_type_select = self.driver.find_element(By.ID, 'ddlCaseType')
            select = Select(case_type_select)
            select.select_by_value('1')  # C.A.
            print("✅ Selected case type: C.A.")
            time.sleep(1)
            
            # Select registry: Lahore
            registry_select = self.driver.find_element(By.ID, 'ddlRegistry')
            select = Select(registry_select)
            select.select_by_value('L')  # Lahore
            print("✅ Selected registry: Lahore")
            time.sleep(1)
            
            # Select year: 2025
            year_select = self.driver.find_element(By.ID, 'ddlYear')
            select = Select(year_select)
            select.select_by_value('2025')
            print("✅ Selected year: 2025")
            time.sleep(1)
            
            # Click search button
            search_button = self.driver.find_element(By.ID, 'btnSearch')
            search_button.click()
            print("🔍 Search button clicked")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def download_pdf(self, pdf_url, case_no, pdf_type):
        """Download PDF file"""
        try:
            if not pdf_url or pdf_url == "N/A" or "not available" in pdf_url.lower():
                return "No PDF Available"
            
            # Make URL absolute if relative
            if pdf_url.startswith('/'):
                pdf_url = urljoin(self.base_url, pdf_url)
            
            # Create safe filename
            safe_case_no = re.sub(r'[<>:"/\\|?*]', '_', case_no)
            filename = f"{safe_case_no}_{pdf_type}.pdf"
            filepath = os.path.join(self.downloads_dir, filename)
            
            print(f"📄 Downloading {pdf_type} PDF for {case_no}...")
            
            # Download PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download PDF: {e}")
            return f"Download Failed: {str(e)}"
    
    def extract_detailed_case_info(self, case_index):
        """Extract detailed case information with PDF downloads"""
        try:
            print(f"🔍 Processing case {case_index + 1}...")
            
            # Get View Details links
            view_details_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            
            if case_index >= len(view_details_links):
                print(f"⚠️ Case index {case_index} out of range")
                return None
            
            # Click View Details
            link = view_details_links[case_index]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", link)
            time.sleep(4)
            
            # Extract information
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
            # Initialize case structure
            case_data = {
                "Case_No": "N/A",
                "Case_Title": "N/A",
                "Status": "N/A",
                "Institution_Date": "N/A",
                "Disposal_Date": "N/A",
                "Advocates": {
                    "ASC": "N/A",
                    "AOR": "N/A",
                    "Prosecutor": "N/A"
                },
                "Petition_Appeal_Memo": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available"
                },
                "History": [],
                "Judgement_Order": {
                    "File": "N/A",
                    "Type": "N/A",
                    "Downloaded_Path": "No PDF Available"
                }
            }
            
            # Extract information using specific HTML structure
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract Case No from spCaseNo
            case_no_span = soup.find('span', {'id': 'spCaseNo'})
            if case_no_span:
                case_data["Case_No"] = case_no_span.get_text(strip=True)
            
            # Extract Case Title from spCaseTitle  
            case_title_span = soup.find('span', {'id': 'spCaseTitle'})
            if case_title_span:
                case_data["Case_Title"] = case_title_span.get_text(strip=True)
            
            # Extract Status from spStatus
            status_span = soup.find('span', {'id': 'spStatus'})
            if status_span:
                case_data["Status"] = status_span.get_text(strip=True)
            
            # Extract Institution Date from spInstDate
            inst_date_span = soup.find('span', {'id': 'spInstDate'})
            if inst_date_span:
                case_data["Institution_Date"] = inst_date_span.get_text(strip=True)
            
            # Extract Disposal Date from spDispDate
            disp_date_span = soup.find('span', {'id': 'spDispDate'})
            if disp_date_span:
                case_data["Disposal_Date"] = disp_date_span.get_text(strip=True)
            
            # Extract AOR/ASC from spAOR
            aor_span = soup.find('span', {'id': 'spAOR'})
            if aor_span:
                aor_html = str(aor_span)
                
                # Split by <br> tags for better parsing
                if '<br>' in aor_html:
                    parts = aor_html.split('<br>')
                    for part in parts:
                        # Remove HTML tags
                        clean_text = re.sub(r'<[^>]+>', '', part).strip()
                        if '(AOR)' in clean_text:
                            case_data["Advocates"]["AOR"] = clean_text
                        elif '(ASC)' in clean_text:
                            case_data["Advocates"]["ASC"] = clean_text
                        elif 'prosecutor' in clean_text.lower():
                            case_data["Advocates"]["Prosecutor"] = clean_text
                else:
                    # Fallback to text parsing
                    aor_text = aor_span.get_text()
                    lines = aor_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if '(AOR)' in line:
                            case_data["Advocates"]["AOR"] = line
                        elif '(ASC)' in line:
                            case_data["Advocates"]["ASC"] = line
                        elif 'prosecutor' in line.lower():
                            case_data["Advocates"]["Prosecutor"] = line
            
            # Extract Petition/Appeal Memo information
            memo_div = soup.find('div', string=re.compile('Digital Copy Not Available'))
            if memo_div:
                case_data["Petition_Appeal_Memo"]["File"] = "Digital Copy Not Available"
            else:
                # Look for memo links
                memo_links = soup.find_all('a', href=re.compile(r'.*memo.*|.*petition.*', re.I))
                for link in memo_links:
                    href = link.get('href', '')
                    if href:
                        case_data["Petition_Appeal_Memo"]["File"] = href
                        case_data["Petition_Appeal_Memo"]["Type"] = "PDF"
                        # Download memo PDF
                        download_path = self.download_pdf(href, case_data["Case_No"], "memo")
                        case_data["Petition_Appeal_Memo"]["Downloaded_Path"] = download_path
                        break
            
            # Extract History information
            history_span = soup.find('span', {'id': 'spnNotFound'})
            if history_span and 'No Fixation History Found' in history_span.get_text():
                case_data["History"] = [{"note": "No Fixation History Found"}]
            else:
                # Look for history information in divResult
                history_div = soup.find('div', {'id': 'divResult'})
                if history_div:
                    history_text = history_div.get_text(strip=True)
                    if history_text and "No Fixation History Found" not in history_text:
                        case_data["History"].append({"note": history_text})
            
            # Look for judgment/order links
            judgment_links = soup.find_all('a', href=re.compile(r'.*judgment.*|.*order.*', re.I))
            for link in judgment_links:
                href = link.get('href', '')
                link_text = link.get_text().lower()
                if href and ('judgment' in link_text or 'order' in link_text):
                    case_data["Judgement_Order"]["File"] = href
                    case_data["Judgement_Order"]["Type"] = "PDF"
                    # Download judgment PDF
                    download_path = self.download_pdf(href, case_data["Case_No"], "judgment")
                    case_data["Judgement_Order"]["Downloaded_Path"] = download_path
                    break
            
            # Remove the advocate section parsing since we're using HTML-based extraction now
            
            # Find and download PDFs
            pdf_links = soup.find_all('a', href=True)
            
            for link in pdf_links:
                href = link.get('href', '')
                link_text = link.get_text().lower()
                
                if '.pdf' in href.lower() or 'pdf' in link_text:
                    if 'memo' in link_text or 'petition' in link_text or 'appeal' in link_text:
                        case_data["Petition_Appeal_Memo"]["File"] = href
                        case_data["Petition_Appeal_Memo"]["Type"] = "PDF"
                        # Download memo PDF
                        download_path = self.download_pdf(href, case_data["Case_No"], "memo")
                        case_data["Petition_Appeal_Memo"]["Downloaded_Path"] = download_path
                    
                    elif 'judgment' in link_text or 'order' in link_text:
                        case_data["Judgement_Order"]["File"] = href
                        case_data["Judgement_Order"]["Type"] = "PDF"
                        # Download judgment PDF
                        download_path = self.download_pdf(href, case_data["Case_No"], "judgment")
                        case_data["Judgement_Order"]["Downloaded_Path"] = download_path
            
            # Extract history
            history_match = re.search(r'History:?\s*([^\n\r]+)', page_text, re.IGNORECASE)
            if history_match:
                history_text = history_match.group(1).strip()
                if "No Fixation History Found" not in history_text:
                    case_data["History"].append({"note": history_text})
            
            # Navigate back
            self.driver.back()
            time.sleep(3)
            
            # Handle potential form resubmission
            self.handle_form_resubmission()
            
            print(f"✅ Case {case_index + 1} processed: {case_data['Case_No']}")
            return case_data
            
        except Exception as e:
            print(f"❌ Error processing case {case_index + 1}: {e}")
            try:
                self.driver.back()
                time.sleep(2)
                self.handle_form_resubmission()
            except:
                pass
            return None
    
    def get_total_cases_count(self):
        """Get total number of cases on current page"""
        try:
            view_details_links = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")
            return len(view_details_links)
        except:
            return 0
    
    def extract_all_cases(self):
        """Extract all C.A. Lahore 2025 cases with details and PDFs"""
        all_cases = []
        
        try:
            total_cases = self.get_total_cases_count()
            print(f"📋 Found {total_cases} cases to process")
            
            if total_cases == 0:
                print("⚠️ No cases found on page")
                return []
            
            # Process each case
            for i in range(total_cases):
                case_data = self.extract_detailed_case_info(i)
                
                if case_data:
                    all_cases.append(case_data)
                    print(f"✅ Processed case {i+1}/{total_cases}: {case_data.get('Case_No', 'Unknown')}")
                else:
                    print(f"⚠️ Failed to process case {i+1}/{total_cases}")
                
                # Small delay between cases
                time.sleep(2)
            
            return all_cases
            
        except Exception as e:
            print(f"❌ Error in extraction: {e}")
            return all_cases
    
    def run_extraction(self):
        """Run the complete extraction process"""
        print("🚀 C.A. LAHORE 2025 EXTRACTOR WITH PDF DOWNLOADS")
        print("=" * 60)
        
        try:
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Navigate to website
            if not self.navigate_to_website():
                return False
            
            # Perform search
            if not self.perform_search():
                return False
            
            # Extract all cases
            self.extracted_cases = self.extract_all_cases()
            
            print(f"\n🎯 EXTRACTION COMPLETED: {len(self.extracted_cases)} cases processed")
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_results(self, filename="ca_lahore_2025_complete_with_pdfs.json"):
        """Save results to JSON file"""
        try:
            # Remove duplicates
            seen_cases = set()
            unique_cases = []
            
            for case in self.extracted_cases:
                case_no = case.get("Case_No", "")
                if case_no and case_no != "N/A" and case_no not in seen_cases:
                    seen_cases.add(case_no)
                    unique_cases.append(case)
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_cases, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(unique_cases)} unique cases to {filename}")
            
            # Show summary
            if unique_cases:
                print(f"\n📋 EXTRACTION SUMMARY:")
                print(f"   Total Cases: {len(unique_cases)}")
                print(f"   PDF Downloads Directory: {self.downloads_dir}")
                
                pdf_count = 0
                for case in unique_cases:
                    if (case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', '') != 'No PDF Available' or
                        case.get('Judgement_Order', {}).get('Downloaded_Path', '') != 'No PDF Available'):
                        pdf_count += 1
                
                print(f"   Cases with PDFs: {pdf_count}")
                
                # Show first few cases
                print(f"\n📄 Sample Cases:")
                for i, case in enumerate(unique_cases[:3]):
                    print(f"\n   {i+1}. {case.get('Case_No', 'N/A')}")
                    print(f"      Title: {case.get('Case_Title', 'N/A')[:60]}...")
                    print(f"      Status: {case.get('Status', 'N/A')}")
                    print(f"      Memo PDF: {case.get('Petition_Appeal_Memo', {}).get('Downloaded_Path', 'N/A')}")
                    print(f"      Judgment PDF: {case.get('Judgement_Order', {}).get('Downloaded_Path', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False


def main():
    """Main function"""
    extractor = CALahore2025Extractor()
    
    if extractor.run_extraction():
        extractor.save_results()
        print("\n🎉 Extraction completed successfully!")
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    main()