"""
Miniapp Scraping CLI v1.4.0
Command-line interface for easy integration
"""

import sys
import argparse
from .scraper import MiniappScraper


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Miniapp Scraping v1.4.0 - Extract press releases with email addresses'
    )
    parser.add_argument('url', help='Press release URL to scrape')
    parser.add_argument('-o', '--output', help='Output JSON filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Miniapp Scraping v1.4.0")
        print("=" * 40)
    
    # Initialize scraper
    scraper = MiniappScraper()
    
    # Scrape data
    result = scraper.scrape(args.url)
    
    if result:
        if args.verbose:
            print("\\n✅ Success!")
            print(f"Title: {result['title']}")
            print(f"Company: {result['company']}")
            print(f"Emails found: {len(result['emails'])}")
            for email in result['emails']:
                print(f"  - {email}")
        
        # Save data
        filename = scraper.save_json(result, args.output)
        
        if args.verbose:
            print(f"\\nData saved to: {filename}")
        
        return 0
    else:
        print("❌ Failed to scrape data")
        return 1


if __name__ == '__main__':
    sys.exit(main())
