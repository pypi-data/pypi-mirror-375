"""
Miniapp Scraping - Core Functionality v1.4.0
Lightweight, pure Python press release scraper
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin
from datetime import datetime


class MiniappScraper:
    """Lightweight press release scraper with email extraction"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.version = "1.4.0"
    
    def scrape(self, url):
        """Main scraping method"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            title = self._extract_title(soup)
            company = self._extract_company(soup)
            date = self._extract_date(response.text)
            content = self._extract_content(soup)
            emails = self._extract_emails(soup)
            
            # Create result
            result = {
                "url": url,
                "title": title,
                "company": company,
                "date": date,
                "content": content,
                "emails": emails,
                "scraped_at": datetime.now().isoformat(),
                "version": self.version
            }
            
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def _extract_title(self, soup):
        """Extract title"""
        title_elem = soup.find('h1')
        return title_elem.get_text(strip=True) if title_elem else ""
    
    def _extract_company(self, soup):
        """Extract company name"""
        company_elem = soup.find('a', href=re.compile(r'/main/html/searchrlp/company_id/'))
        return company_elem.get_text(strip=True) if company_elem else ""
    
    def _extract_date(self, text):
        """Extract date"""
        date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
        date_match = re.search(date_pattern, text)
        return date_match.group() if date_match else ""
    
    def _extract_content(self, soup):
        """Extract main content"""
        # Remove unwanted elements
        for elem in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            elem.decompose()
        
        # Get main content
        content_area = soup.find('main') or soup.find('article') or soup.find('body')
        if content_area:
            return content_area.get_text(strip=True, separator='\\n')
        return ""
    
    def _extract_emails(self, soup):
        """Extract email addresses"""
        text_content = soup.get_text()
        
        # Email patterns (prioritized)
        patterns = [
            r'(?:E-mail|Email|メール|お問い合わせ)[:：]?\\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})'
        ]
        
        emails = []
        for pattern in patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                email = match if isinstance(match, str) else match[0] if match else None
                if email and email not in emails and '@' in email:
                    emails.append(email)
        
        return emails
    
    def save_json(self, data, filename=None):
        """Save data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prtimes_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved to: {filename}")
        return filename
