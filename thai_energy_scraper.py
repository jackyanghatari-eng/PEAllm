#!/usr/bin/env python3
"""
Complete Thai Energy Sector Website Scraper
Scrapes EGAT, MEA, PEA, Ministry of Energy, ERC for LLM training data
Handles Thai language, removes duplicates, organizes for Google Drive upload
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from datetime import datetime
import json
from urllib.parse import urljoin, urlparse
import hashlib

class ThaiEnergyWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.all_documents = []
        self.seen_urls = set()
        self.processed_content = set()
        
        # Target websites configuration
        self.websites = {
            'EGAT': {
                'base_url': 'https://www.egat.co.th',
                'thai_url': 'https://www.egat.co.th/th/',
                'target_keywords': ['กฎระเบียบ', 'มาตรฐาน', 'เทคนิค', 'ระบบไฟฟ้า', 'โครงข่าย'],
                'folder': 'State_Enterprises/EGAT/'
            },
            'PEA': {
                'base_url': 'https://www.pea.co.th',
                'thai_url': 'https://www.pea.co.th/th/',
                'target_keywords': ['บริการ', 'มาตรฐาน', 'ระเบียบ', 'จำหน่าย', 'ไฟฟ้า'],
                'folder': 'State_Enterprises/PEA/'
            },
            'MEA': {
                'base_url': 'https://www.mea.or.th',
                'thai_url': 'https://www.mea.or.th/th/',
                'target_keywords': ['กฎหมาย', 'ระเบียบ', 'กรุงเทพ', 'มหานคร', 'ไฟฟ้า'],
                'folder': 'State_Enterprises/MEA/'
            },
            'Ministry_of_Energy': {
                'base_url': 'https://www.energy.go.th',
                'thai_url': 'https://www.energy.go.th/th/',
                'target_keywords': ['นโยบาย', 'แผน', 'ยุทธศาสตร์', 'พลังงาน', 'กระทรวง'],
                'folder': 'Government_Agencies/Ministry_of_Energy/'
            },
            'ERC': {
                'base_url': 'https://www.erc.or.th',
                'thai_url': 'https://www.erc.or.th/th/',
                'target_keywords': ['กฎระเบียบ', 'ใบอนุญาต', 'พลังงาน', 'กำกับ', 'คณะกรรมการ'],
                'folder': 'Government_Agencies/ERC_Energy_Regulatory_Commission/'
            },
            'EPPO': {
                'base_url': 'https://www.eppo.go.th',
                'thai_url': 'https://www.eppo.go.th/index.php/th/',
                'target_keywords': ['นโยบาย', 'แผน', 'พลังงาน', 'สถิติ', 'รายงาน'],
                'folder': 'Government_Agencies/NEPC_National_Energy_Policy_Council/'
            }
        }

    def clean_thai_text(self, text):
        """Clean and normalize Thai text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep Thai and basic punctuation
        text = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s\.,\-\(\)\[\]\/]', '', text)
        
        return text

    def is_relevant_content(self, text, keywords):
        """Check if content contains relevant keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def extract_documents_from_page(self, url, source_config):
        """Extract document links and content from a page"""
        try:
            print(f"🔍 Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            documents_found = 0
            
            for link in links:
                href = link.get('href', '')
                text = self.clean_thai_text(link.get_text())
                
                if not text or len(text) < 5:
                    continue
                
                # Check if it's a relevant document
                if self.is_relevant_content(text, source_config['target_keywords']):
                    # Create absolute URL
                    if href.startswith('/'):
                        full_url = source_config['base_url'] + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(url, href)
                    
                    # Check for duplicates
                    url_hash = hashlib.md5(full_url.encode()).hexdigest()
                    content_hash = hashlib.md5(text.encode()).hexdigest()
                    
                    if url_hash not in self.seen_urls and content_hash not in self.processed_content:
                        self.seen_urls.add(url_hash)
                        self.processed_content.add(content_hash)
                        
                        # Determine document type
                        doc_type = self.classify_document_type(text)
                        priority = self.get_priority(text, doc_type)
                        
                        document = {
                            'Document_Title_Thai': text,
                            'Document_URL': full_url,
                            'Source': source_config['folder'].split('/')[1] if '/' in source_config['folder'] else url.split('//')[1].split('.')[1].upper(),
                            'Collection_Date': datetime.now().strftime('%Y-%m-%d'),
                            'Language': 'Thai',
                            'Document_Type': doc_type,
                            'Priority': priority,
                            'Status': 'Collected',
                            'Folder_Path': source_config['folder'],
                            'Content_Hash': content_hash
                        }
                        
                        self.all_documents.append(document)
                        documents_found += 1
            
            print(f"✅ Found {documents_found} relevant documents from {url}")
            return documents_found
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            return 0

    def classify_document_type(self, title):
        """Classify document type based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['นโยบาย', 'policy']):
            return 'Policy'
        elif any(word in title_lower for word in ['แผน', 'plan', 'ยุทธศาสตร์']):
            return 'Plan'
        elif any(word in title_lower for word in ['กฎ', 'ระเบียบ', 'กฎหมาย', 'regulation']):
            return 'Regulation'
        elif any(word in title_lower for word in ['มาตรฐาน', 'standard', 'เทคนิค']):
            return 'Standard'
        elif any(word in title_lower for word in ['รายงาน', 'report']):
            return 'Report'
        elif any(word in title_lower for word in ['สถิติ', 'statistic']):
            return 'Statistics'
        else:
            return 'Document'

    def get_priority(self, title, doc_type):
        """Assign priority based on content importance"""
        title_lower = title.lower()
        
        # High priority keywords
        high_priority = ['แผนแม่บท', 'นโยบายหลัก', 'ยุทธศาสตร์หลัก', 'มาตรฐานหลัก']
        medium_priority = ['รายงานประจำปี', 'แผนปฏิบัติ', 'ระเบียบปฏิบัติ']
        
        if any(keyword in title_lower for keyword in high_priority):
            return 'High'
        elif any(keyword in title_lower for keyword in medium_priority):
            return 'Medium'
        elif doc_type in ['Policy', 'Plan', 'Regulation']:
            return 'High'
        elif doc_type in ['Standard', 'Report']:
            return 'Medium'
        else:
            return 'Low'

    def scrape_website_deep(self, website_name, config):
        """Deep scrape a website including subpages"""
        print(f"\n🏢 Starting deep scrape of {website_name}")
        
        # Start with main Thai page
        main_docs = self.extract_documents_from_page(config['thai_url'], config)
        
        # Try to find and scrape relevant subpages
        try:
            response = self.session.get(config['thai_url'], timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for navigation menus and important sections
            nav_links = []
            
            # Common navigation selectors
            nav_selectors = [
                'nav a', '.menu a', '.navigation a', 
                '.main-menu a', '.primary-menu a',
                'header a', '.header a'
            ]
            
            for selector in nav_selectors:
                found_links = soup.select(selector)
                for link in found_links:
                    href = link.get('href', '')
                    text = self.clean_thai_text(link.get_text())
                    
                    if (href and text and 
                        self.is_relevant_content(text, config['target_keywords']) and
                        len(text) > 3):
                        
                        if href.startswith('/'):
                            full_url = config['base_url'] + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(config['thai_url'], href)
                            
                        nav_links.append(full_url)
            
            # Remove duplicates and limit to prevent infinite crawling
            nav_links = list(set(nav_links))[:10]  # Limit to 10 subpages per site
            
            print(f"🔍 Found {len(nav_links)} relevant subpages to scrape")
            
            # Scrape each subpage
            for subpage_url in nav_links:
                time.sleep(1)  # Be respectful to servers
                self.extract_documents_from_page(subpage_url, config)
                
        except Exception as e:
            print(f"⚠️ Error in deep scraping {website_name}: {str(e)}")

    def scrape_all_websites(self):
        """Scrape all configured websites"""
        print("🚀 Starting comprehensive Thai energy sector web scraping...")
        print("=" * 70)
        
        total_docs = 0
        
        for website_name, config in self.websites.items():
            try:
                print(f"\n📡 Processing {website_name}...")
                initial_count = len(self.all_documents)
                
                self.scrape_website_deep(website_name, config)
                
                final_count = len(self.all_documents)
                site_docs = final_count - initial_count
                total_docs += site_docs
                
                print(f"✅ {website_name}: Collected {site_docs} documents")
                
                # Brief pause between websites
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Failed to process {website_name}: {str(e)}")
        
        print(f"\n🎉 SCRAPING COMPLETE!")
        print(f"📊 Total documents collected: {total_docs}")
        print(f"🔍 Unique URLs processed: {len(self.seen_urls)}")
        
        return total_docs

    def save_to_files(self):
        """Save collected data to organized files"""
        if not self.all_documents:
            print("❌ No documents to save!")
            return
        
        # Create timestamp for file naming
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        
        # Create main DataFrame
        df_all = pd.DataFrame(self.all_documents)
        
        # Save complete dataset
        filename_all = f"Thai_Energy_Complete_Dataset_{timestamp}.csv"
        df_all.to_csv(filename_all, index=False, encoding='utf-8-sig')
        print(f"💾 Saved complete dataset: {filename_all}")
        
        # Save by source organization
        for org in df_all['Source'].unique():
            df_org = df_all[df_all['Source'] == org]
            filename_org = f"Thai_Energy_{org}_Dataset_{timestamp}.csv"
            df_org.to_csv(filename_org, index=False, encoding='utf-8-sig')
            print(f"📁 Saved {org} dataset: {filename_org} ({len(df_org)} documents)")
        
        # Save high priority documents only
        df_high = df_all[df_all['Priority'] == 'High']
        if not df_high.empty:
            filename_high = f"Thai_Energy_High_Priority_{timestamp}.csv"
            df_high.to_csv(filename_high, index=False, encoding='utf-8-sig')
            print(f"⭐ Saved high priority dataset: {filename_high} ({len(df_high)} documents)")
        
        # Create summary report
        self.create_summary_report(df_all, timestamp)
        
        return filename_all

    def create_summary_report(self, df, timestamp):
        """Create a summary report of the scraping results"""
        summary = {
            'scraping_date': datetime.now().isoformat(),
            'total_documents': len(df),
            'sources': df['Source'].value_counts().to_dict(),
            'document_types': df['Document_Type'].value_counts().to_dict(),
            'priority_breakdown': df['Priority'].value_counts().to_dict(),
            'top_documents': df[df['Priority'] == 'High']['Document_Title_Thai'].head(10).tolist()
        }
        
        # Save JSON summary
        summary_file = f"Thai_Energy_Scraping_Summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Saved summary report: {summary_file}")
        
        # Print summary to console
        print(f"\n📊 SCRAPING SUMMARY:")
        print("=" * 50)
        print(f"📄 Total Documents: {summary['total_documents']}")
        print(f"🏢 Sources: {len(summary['sources'])}")
        for source, count in summary['sources'].items():
            print(f"   • {source}: {count} documents")
        print(f"📋 Document Types: {len(summary['document_types'])}")
        for doc_type, count in summary['document_types'].items():
            print(f"   • {doc_type}: {count} documents")

def main():
    """Main execution function"""
    print("🇹🇭 THAI ENERGY SECTOR COMPREHENSIVE WEB SCRAPER")
    print("=" * 60)
    print("Targets: EGAT, PEA, MEA, Ministry of Energy, ERC, EPPO")
    print("Purpose: LLM Training Data Collection")
    print("Output: CSV files ready for Google Drive upload")
    print("=" * 60)
    
    scraper = ThaiEnergyWebScraper()
    
    try:
        # Perform comprehensive scraping
        total_docs = scraper.scrape_all_websites()
        
        if total_docs > 0:
            # Save all data to files
            main_file = scraper.save_to_files()
            
            print(f"\n🎉 SUCCESS! SCRAPING COMPLETED")
            print("=" * 50)
            print(f"✅ Total documents collected: {total_docs}")
            print(f"📄 Main dataset file: {main_file}")
            print(f"📁 Files saved to current directory")
            print(f"📤 Ready for Google Drive upload!")
            
            print(f"\n📋 NEXT STEPS:")
            print("1. Upload CSV files to your Google Drive folder structure")
            print("2. Use high priority dataset for immediate LLM training")
            print("3. Upload to Hugging Face for fine-tuning")
            print("4. Ready for tomorrow's PEA ambassador demo!")
            
        else:
            print("❌ No documents collected. Check internet connection and website availability.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
        if scraper.all_documents:
            print("💾 Saving collected data before exit...")
            scraper.save_to_files()
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        if scraper.all_documents:
            print("💾 Saving collected data before exit...")
            scraper.save_to_files()

if __name__ == "__main__":
    main()